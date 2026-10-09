"""Small immutable JSON snapshots and audited transactional coordination."""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager
from typing import Any

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy.orm.exc import StaleDataError

from startup_foundry.domain import Artifact, ArtifactKind, AuditEvent
from startup_foundry.errors import ConflictError, ReferenceError
from startup_foundry.portfolio import stable_id
from startup_foundry.repository import SessionFactory, UnitOfWork
from startup_foundry.scoring import digest

JSON = dict[str, Any]


@contextmanager
def transaction(factory: SessionFactory) -> Iterator[Session]:
    try:
        with UnitOfWork(factory) as unit:
            assert unit.session is not None
            if unit.session.get_bind().dialect.name == "sqlite":
                # Pin the check-and-write boundary, including against legacy
                # writers. SQLite's default deferred SELECT is not a snapshot.
                unit.session.connection().exec_driver_sql("BEGIN IMMEDIATE")
            yield unit.session
    except (IntegrityError, StaleDataError) as exc:
        raise ConflictError(
            "Concurrent change or duplicate identity; refresh and retry"
        ) from exc


def snapshot(
    session: Session,
    workspace: str,
    schema: str,
    payload: JSON,
    *,
    key: str | None = None,
    work_id: str | None = None,
) -> Artifact:
    identity = stable_id(schema + ":" + workspace + ":" + key) if key else None
    if identity:
        prior = session.get(Artifact, identity)
        if prior:
            if prior.content_digest != digest(payload):
                raise ConflictError(
                    "Submission key already used with different content"
                )
            return prior
    artifact = Artifact(
        id=identity,
        workspace_id=workspace,
        kind=ArtifactKind.DOCUMENT,
        name=schema,
        location="database:inline",
        media_type="application/json",
        semantic_version=schema,
        metadata_json=payload,
        content_digest=digest(payload),
        work_item_id=work_id,
    )
    session.add(artifact)
    session.flush()
    return artifact


def read_snapshot(session: Session, identity: str, workspace: str, schema: str) -> JSON:
    artifact = session.get(Artifact, identity)
    if (
        artifact is None
        or artifact.workspace_id != workspace
        or artifact.semantic_version != schema
        or artifact.content_digest != digest(artifact.metadata_json)
    ):
        raise ReferenceError("Invalid snapshot owner, schema or digest")
    return artifact.metadata_json


def audit(
    session: Session,
    workspace: str,
    identity: str,
    event: str,
    actor: str,
    payload: JSON,
) -> None:
    session.add(
        AuditEvent(
            workspace_id=workspace,
            entity_type="workspace_coordination",
            entity_id=identity,
            event_type=event,
            actor=actor,
            payload=payload,
        )
    )
