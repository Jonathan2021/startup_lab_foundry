"""Paginated chronological references; original records remain authoritative."""

from __future__ import annotations

from datetime import UTC, datetime
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

SUMMARY_CHARS = 120


def relative_time(value: datetime | None, now: datetime | None = None) -> str:
    """A short human label such as "3 days ago"; stored times are UTC."""
    if value is None:
        return "unknown time"
    moment = value if value.tzinfo else value.replace(tzinfo=UTC)
    seconds = int(((now or datetime.now(UTC)) - moment).total_seconds())
    if seconds < 0:
        return "in the future"
    for size, unit in [
        (86400 * 365, "year"),
        (86400 * 30, "month"),
        (86400, "day"),
        (3600, "hour"),
        (60, "minute"),
    ]:
        if seconds >= size:
            count = seconds // size
            return f"{count} {unit}{'s' if count != 1 else ''} ago"
    return "just now"


def summary_text(value: str | None) -> str:
    text = " ".join((value or "").split())
    return text if len(text) <= SUMMARY_CHARS else text[: SUMMARY_CHARS - 1] + "…"


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
    artifact_summary = func.coalesce(
        Artifact.metadata_json["summary"].as_string(),
        Artifact.metadata_json["rationale"].as_string(),
        Artifact.name,
    )
    audit_summary = func.coalesce(
        AuditEvent.payload["rationale"].as_string(),
        AuditEvent.payload["summary"].as_string(),
        AuditEvent.event_type,
    )
    event_sources: list[tuple[Any, Any, Any, str, Any, Any]] = [
        (
            Decision.id,
            Decision.decided_at,
            Decision.decided_by,
            "decision",
            Decision.workspace_id == workspace,
            Decision.summary,
        ),
        (
            Evidence.id,
            Evidence.captured_at,
            Evidence.captured_by,
            "evidence",
            Evidence.workspace_id == workspace,
            Evidence.summary,
        ),
        (
            StepRun.id,
            StepRun.created_at,
            StepRun.runner,
            "run",
            StepRun.workspace_id == workspace,
            StepRun.kind,
        ),
        (
            WorkspaceReview.id,
            WorkspaceReview.reviewed_at,
            WorkspaceReview.author,
            "state",
            WorkspaceReview.workspace_id == workspace,
            WorkspaceReview.next_action,
        ),
        (
            Artifact.id,
            Artifact.created_at,
            cast(Artifact.metadata_json["actor"], String),
            "artifact",
            Artifact.workspace_id == workspace,
            artifact_summary,
        ),
        (
            AuditEvent.id,
            AuditEvent.occurred_at,
            AuditEvent.actor,
            "audit",
            AuditEvent.workspace_id == workspace,
            audit_summary,
        ),
        (
            VentureAssessment.id,
            VentureAssessment.created_at,
            VentureAssessment.author,
            "score",
            VentureAssessment.venture_id == venture,
            VentureAssessment.rationale,
        ),
    ]
    for identity, time, actor, kind, predicate, summary in event_sources:
        queries.append(
            select(
                identity.label("id"),
                time.label("time"),
                actor.label("actor"),
                literal(kind).label("type"),
                cast(summary, String).label("summary"),
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
                    "summary": summary_text(r["summary"]),
                    "relative_time": relative_time(r["time"]),
                    "url": "/ventures/" + venture + "/events/" + r["id"],
                }
                for r in rows
            ],
            "total": total,
            "offset": offset,
            "limit": limit,
        }
