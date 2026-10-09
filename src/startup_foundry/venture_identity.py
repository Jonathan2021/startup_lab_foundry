"""Venture aliases and one selector resolution rule for read commands (ADR-0020).

A selector may be a venture ID, a venture alias, a workspace ID, a workspace key
or an idea ID. Resolution is read-only and deterministic; ambiguity is an error.
"""

from __future__ import annotations

from argparse import Namespace
from typing import Annotated, Any, Literal

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import select
from sqlalchemy.orm import Session

from startup_foundry.domain import Idea, Venture, Workspace
from startup_foundry.errors import ConflictError, ReferenceError
from startup_foundry.repository import SessionFactory
from startup_foundry.snapshots import audit, snapshot, transaction

JSON = dict[str, Any]
ALIAS_PATTERN = r"^v-[a-z0-9-]{2,60}$"


class AliasInput(BaseModel):
    model_config = ConfigDict(extra="forbid", str_strip_whitespace=True)
    alias: Annotated[str, Field(pattern=ALIAS_PATTERN, max_length=64)]
    actor: Annotated[str, Field(min_length=1, max_length=200)]
    rationale: Annotated[str, Field(min_length=1, max_length=10000)]
    expected_version: int = Field(ge=1)


def venture_by_identity(session: Session, identity: str) -> Venture | None:
    """A venture by its ID or, failing that, by its alias."""
    return session.get(Venture, identity) or session.scalar(
        select(Venture).where(Venture.alias == identity)
    )


def resolve_selector(
    session: Session, value: str, *, prefer: Literal["venture", "workspace"]
) -> JSON:
    """Resolve a selector to its venture/idea and workspace."""
    venture = venture_by_identity(session, value)
    workspace = session.get(Workspace, value)
    if prefer == "workspace" and workspace is not None:
        venture = None
    if venture is None and workspace is None:
        keyed = list(
            session.scalars(select(Workspace).where(Workspace.key == value).limit(2))
        )
        if len(keyed) > 1:
            raise ConflictError("Workspace key " + value + " is ambiguous; use an ID")
        workspace = keyed[0] if keyed else None
    if venture is None and workspace is None:
        idea = session.get(Idea, value)
        workspace = session.get(Workspace, idea.workspace_id) if idea else None
    if venture is not None:
        return {
            "venture_id": venture.id,
            "workspace_id": venture.workspace_id,
            "idea_id": None,
        }
    if workspace is None:
        raise ReferenceError(
            "No venture, alias, workspace, workspace key or idea matches " + value
        )
    owner = session.scalar(select(Venture).where(Venture.workspace_id == workspace.id))
    idea = session.scalar(select(Idea).where(Idea.workspace_id == workspace.id))
    return {
        "venture_id": owner.id if owner else None,
        "workspace_id": workspace.id,
        "idea_id": idea.id if idea else None,
    }


class VentureAliasService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    def set_alias(self, identity: str, payload: AliasInput) -> JSON:
        """Version-checked alias assignment, retained as an artifact and audit."""
        with transaction(self.factory) as session:
            venture = venture_by_identity(session, identity)
            if venture is None:
                raise ReferenceError("Venture does not exist")
            if venture.alias == payload.alias:
                return {"id": venture.id, "alias": venture.alias, "changed": False}
            if venture.version_id != payload.expected_version:
                raise ConflictError("Venture changed; refresh its version first")
            other = venture_by_identity(session, payload.alias)
            if other is not None and other.id != venture.id:
                raise ConflictError("Alias already identifies another venture")
            keyed = session.scalar(
                select(Workspace).where(
                    Workspace.key == payload.alias,
                    Workspace.id != venture.workspace_id,
                )
            )
            if keyed is not None:
                raise ConflictError("Alias is another workspace's key")
            previous = venture.alias
            venture.alias = payload.alias
            session.flush()
            change = {
                "venture_id": venture.id,
                "previous_alias": previous,
                "alias": payload.alias,
                "actor": payload.actor,
                "rationale": payload.rationale,
            }
            snapshot(session, venture.workspace_id, "venture-alias/v1", change)
            audit(
                session,
                venture.workspace_id,
                venture.id,
                "venture_alias_set",
                payload.actor,
                change,
            )
            return {
                "id": venture.id,
                "alias": venture.alias,
                "previous_alias": previous,
                "version_id": venture.version_id,
                "changed": True,
            }


WORKSPACE_FLAGS = ["workspace_id", "venture_id", "id"]
VENTURE_FLAGS = ["venture_id", "id"]
# (resource, action) -> (kind, flags read, attribute the command consumes)
READ_SELECTORS: dict[tuple[str, str], tuple[str, list[str], str]] = {
    ("agent", "resume"): ("workspace", WORKSPACE_FLAGS, "workspace_id"),
    ("decision-map", "show"): ("workspace", WORKSPACE_FLAGS, "workspace_id"),
    ("decision-map", "draft"): ("workspace", WORKSPACE_FLAGS, "workspace_id"),
    ("result", "list"): ("workspace", WORKSPACE_FLAGS, "workspace_id"),
    ("review", "show"): ("workspace", WORKSPACE_FLAGS, "workspace_id"),
    ("input", "list"): ("workspace", WORKSPACE_FLAGS, "workspace_id"),
    ("existing-project", "show"): ("venture", VENTURE_FLAGS, "venture_id"),
    ("outreach", "list"): ("venture", VENTURE_FLAGS, "venture_id"),
    ("venture", "show"): ("venture", ["id"], "id"),
    ("venture-score", "show"): ("venture", ["id"], "id"),
    ("workspace", "show"): ("venture", ["id"], "id"),
    ("intake", "handoff"): ("venture", ["id"], "id"),
    **{
        (resource, "list"): ("venture", VENTURE_FLAGS, "venture_id")
        for resource in [
            "evidence",
            "assumption",
            "decision",
            "work-item",
            "artifact",
            "experiment",
        ]
    },
}


def normalize_read_selectors(factory: SessionFactory, args: Namespace) -> None:
    """Rewrite a read command's selector flags to the canonical identity."""
    spec = READ_SELECTORS.get((args.resource, args.action))
    if spec is None or (
        args.resource == "intake" and getattr(args, "subject", None) != "venture"
    ):
        return
    kind, flags, target = spec
    value = next(
        (getattr(args, flag) for flag in flags if getattr(args, flag, None)), None
    )
    if value is None:
        return
    prefer: Literal["venture", "workspace"] = (
        "workspace" if kind == "workspace" else "venture"
    )
    with factory() as session:
        resolved = resolve_selector(session, value, prefer=prefer)
    identity = resolved[kind + "_id"]
    if identity is None:
        raise ReferenceError(value + " does not identify a venture")
    for flag in flags:
        if hasattr(args, flag):
            setattr(args, flag, None)
    setattr(args, target, identity)
