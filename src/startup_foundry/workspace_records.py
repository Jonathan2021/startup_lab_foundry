"""Scoped readable work/state references shared by review and module views."""

from typing import Any
from urllib.parse import quote

from sqlalchemy import select
from sqlalchemy.orm import Session

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import Idea, Venture, WorkItem, WorkspaceReview
from startup_foundry.errors import ReferenceError
from startup_foundry.reviews import ReviewService

JSON = dict[str, Any]


def workspace_path(session: Session, workspace: str) -> str:
    idea = session.scalar(select(Idea).where(Idea.workspace_id == workspace))
    if idea:
        return "/ideas/" + quote(idea.id, safe="")
    venture = session.scalar(select(Venture).where(Venture.workspace_id == workspace))
    if venture:
        return "/ventures/" + quote(venture.id, safe="")
    raise ReferenceError("Workspace has no idea or venture identity")


def work_reference(
    session: Session, workspace: str, identity: str | None
) -> JSON | None:
    if identity is None:
        return None
    work = session.get(WorkItem, identity)
    if not work or work.workspace_id != workspace:
        raise ReferenceError("Work does not belong to the selected workspace")
    return {
        **FoundryApplication._work_item_json(work),
        "owner": work.owner,
        "description": work.description,
        "blocked_reason": work.blocked_reason,
        "version": work.version_id,
        "url": workspace_path(session, workspace) + "/work/" + work.id,
    }


def state_reference(session: Session, workspace: str, identity: str) -> JSON:
    review = session.get(WorkspaceReview, identity)
    if not review or review.workspace_id != workspace:
        raise ReferenceError("Review does not belong to the selected workspace")
    return {
        **ReviewService._json(session, review),
        "url": workspace_path(session, workspace) + "/reviews/" + review.id,
    }
