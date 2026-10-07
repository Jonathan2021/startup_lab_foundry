"""Reconcile named retained states and superseded holds without erasing history."""

from __future__ import annotations

import hashlib
import json
from pathlib import Path

from sqlalchemy import select

from startup_foundry.config import load_settings
from startup_foundry.domain import (
    Artifact,
    ArtifactKind,
    AuditEvent,
    Venture,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
    WorkspaceReview,
)
from startup_foundry.portfolio import stable_id
from startup_foundry.repository import (
    SessionFactory,
    UnitOfWork,
    create_db_engine,
    create_session_factory,
)
from startup_foundry.reviews import ReviewInput, ReviewService

RETAINED = [
    (
        "v-evalops",
        "art-evalops",
        "comparison",
        "unknown",
        "hold",
        "Reopen only for a repeated observed workflow incumbents fail.",
        "Standalone product deferred by the October 2 documentary decision; "
        "runtime remains independently retained and was not inspected in this handoff.",
    ),
    (
        "v-g002",
        "art-g002",
        "comparison",
        "concept",
        "internal_only",
        "Review measured source-recovery friction before adding any memory adapter.",
        "Retained internal comparison; Hindsight is uninstalled/unvalidated. "
        "The older learner protocol is historical; learning remains paused.",
    ),
    (
        "portfolio-campaign",
        "register-plan-md",
        "triage",
        "prototype",
        "internal_only",
        "Review a changed claim or new venture input and retain its scoped evidence.",
        "Campaign intake and initial allocation are complete. Operating records "
        "and local trial support exist; commercial qualification remains open.",
    ),
]


def finalize(factory: SessionFactory, project: Path) -> dict[str, object]:
    reviewed = []
    canceled = []
    with UnitOfWork(factory) as unit:
        session = unit.session
        assert session is not None
        for (
            venture_id,
            source_id,
            stage,
            maturity,
            disposition,
            action,
            reason,
        ) in RETAINED:
            venture = session.get(Venture, venture_id)
            assert venture is not None
            latest = session.scalar(
                select(WorkspaceReview)
                .where(WorkspaceReview.workspace_id == venture.workspace_id)
                .order_by(WorkspaceReview.revision.desc())
            )
            if latest is not None:
                continue  # Never overwrite a later human/agent review on repeat.
            task = WorkItem(
                id=stable_id("handoff-retained-next:" + venture_id),
                workspace_id=venture.workspace_id,
                title=action,
                question=action,
                kind=WorkItemKind.INVESTIGATION,
                status=WorkItemStatus.READY,
                owner="agent",
                acceptance_criteria=action,
            )
            session.add(task)
            session.flush()
            review = ReviewService._append(
                session,
                ReviewInput.model_validate(
                    {
                        "workspace_id": venture.workspace_id,
                        "expected_revision": 0,
                        "investigation_stage": stage,
                        "product_maturity": maturity,
                        "disposition": disposition,
                        "next_action": action,
                        "next_work_item_id": task.id,
                        "reason": reason,
                        "author": "agent:handoff-retained-state-v1",
                        "source_artifact_id": source_id,
                    }
                ),
            )
            reviewed.append(review.id)

        # Only old import-owned next work replaced by a named handoff result.
        workspaces = set(
            session.scalars(
                select(WorkspaceReview.workspace_id).where(
                    WorkspaceReview.author == "agent:handoff-20261004"
                )
            )
        )
        for workspace in workspaces:
            history = session.scalars(
                select(WorkspaceReview)
                .where(WorkspaceReview.workspace_id == workspace)
                .order_by(WorkspaceReview.revision.desc())
            ).all()
            latest = history[0]
            if (
                latest.author != "agent:handoff-20261004"
                or not latest.next_work_item_id
            ):
                continue
            candidates = {
                review.next_work_item_id
                for review in history[1:]
                if review.author == "legacy-campaign-import-v1"
                and review.next_work_item_id
            }
            for request in ["R001", "R002", "R003"]:
                candidates.add(stable_id("inbox-followup:" + request + ":" + workspace))
            for identity in candidates:
                task = session.get(WorkItem, identity)
                audit_id = stable_id("handoff-superseded:" + identity)
                if (
                    task is None
                    or task.workspace_id != workspace
                    or task.status != WorkItemStatus.BLOCKED
                    or session.get(AuditEvent, audit_id) is not None
                ):
                    continue
                session.add(
                    AuditEvent(
                        id=audit_id,
                        workspace_id=workspace,
                        entity_type="work_item",
                        entity_id=task.id,
                        event_type="superseded_by_reviewed_next_action",
                        actor="agent:handoff-20261004",
                        payload={
                            "previous_status": task.status.value,
                            "previous_blocker": task.blocked_reason,
                            "superseded_by": latest.next_work_item_id,
                            "review_id": latest.id,
                            "reason": (
                                "Narrower current gate; no human response inferred."
                            ),
                        },
                    )
                )
                task.status = WorkItemStatus.CANCELLED
                task.blocked_reason = None
                canceled.append(task.id)

        report = project / "docs/inquiry/handoff-2026-10-04/REPORT.md"
        if report.is_file():
            digest = hashlib.sha256(report.read_bytes()).hexdigest()
            identity = "handoff-final-report-r1"
            existing = session.get(Artifact, identity)
            if existing is not None and existing.content_digest != digest:
                raise ValueError("Final report changed; register a new revision.")
            if existing is None:
                venture = session.get(Venture, "v-foundry")
                assert venture is not None
                session.add(
                    Artifact(
                        id=identity,
                        workspace_id=venture.workspace_id,
                        kind=ArtifactKind.REPORT,
                        name="October 4 handoff execution and verification",
                        location=str(report.resolve()),
                        content_digest=digest,
                        semantic_version="r1",
                        metadata_json={
                            "record_id": "FOUNDRY-HANDOFF-20261004-001:r1",
                            "browser_visual_qa": "Unavailable",
                            "outreach": "Draft only; no sends",
                            "commercial_validation": "Not established",
                        },
                    )
                )
    return {"retained_reviews": reviewed, "superseded_work": canceled}


if __name__ == "__main__":
    engine = create_db_engine(load_settings().database_url)
    try:
        print(
            json.dumps(
                finalize(
                    create_session_factory(engine), Path(__file__).resolve().parents[1]
                ),
                indent=2,
            )
        )
    finally:
        engine.dispose()
