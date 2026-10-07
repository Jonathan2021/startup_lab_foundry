"""Paginated chronological references; original records remain authoritative."""

from __future__ import annotations

from typing import Any

from sqlalchemy import String, cast, func, literal, select, union_all

from startup_foundry.domain import (
    Artifact,
    AuditEvent,
    Decision,
    Evidence,
    StepRun,
    VentureAssessment,
    WorkspaceReview,
)
from startup_foundry.errors import ValidationError
from startup_foundry.repository import SessionFactory


def history(
    factory: SessionFactory,
    workspace: str,
    venture: str,
    *,
    offset: int = 0,
    limit: int = 30,
) -> dict[str, Any]:
    if offset < 0 or not 1 <= limit <= 100:
        raise ValidationError("Invalid history pagination")
    queries: list[Any] = []
    event_sources: list[tuple[Any, Any, Any, str, Any]] = [
        (
            Decision.id,
            Decision.decided_at,
            Decision.decided_by,
            "decision",
            Decision.workspace_id == workspace,
        ),
        (
            Evidence.id,
            Evidence.captured_at,
            Evidence.captured_by,
            "evidence",
            Evidence.workspace_id == workspace,
        ),
        (
            StepRun.id,
            StepRun.created_at,
            StepRun.runner,
            "run",
            StepRun.workspace_id == workspace,
        ),
        (
            WorkspaceReview.id,
            WorkspaceReview.reviewed_at,
            WorkspaceReview.author,
            "state",
            WorkspaceReview.workspace_id == workspace,
        ),
        (
            Artifact.id,
            Artifact.created_at,
            cast(Artifact.metadata_json["actor"], String),
            "artifact",
            Artifact.workspace_id == workspace,
        ),
        (
            AuditEvent.id,
            AuditEvent.occurred_at,
            AuditEvent.actor,
            "audit",
            AuditEvent.workspace_id == workspace,
        ),
        (
            VentureAssessment.id,
            VentureAssessment.created_at,
            VentureAssessment.author,
            "score",
            VentureAssessment.venture_id == venture,
        ),
    ]
    for identity, time, actor, kind, predicate in event_sources:
        queries.append(
            select(
                identity.label("id"),
                time.label("time"),
                actor.label("actor"),
                literal(kind).label("type"),
            ).where(predicate)
        )
    events = union_all(*queries).subquery()
    with factory() as session:
        total = session.scalar(select(func.count()).select_from(events)) or 0
        rows = session.execute(
            select(events)
            .order_by(events.c.time.desc(), events.c.id)
            .limit(limit)
            .offset(offset)
        ).mappings()
        return {
            "items": [
                {
                    **dict(r),
                    "url": "/ventures/" + venture + "/events/" + r["id"],
                }
                for r in rows
            ],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
