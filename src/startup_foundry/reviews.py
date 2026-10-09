"""Reviewed coordination, with history and explicit unresolved work."""

from __future__ import annotations

import hashlib
from typing import Any

from pydantic import BaseModel, ConfigDict, Field
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    Artifact,
    Decision,
    Disposition,
    InvestigationStage,
    ProductMaturity,
    WorkItem,
    WorkItemKind,
    WorkItemStatus,
    Workspace,
    WorkspaceReview,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.repository import SessionFactory, UnitOfWork

JSON = dict[str, Any]


class ReviewInput(BaseModel):
    model_config = ConfigDict(extra="forbid")
    workspace_id: str = Field(min_length=1, max_length=36)
    expected_revision: int = Field(ge=0)
    investigation_stage: InvestigationStage
    product_maturity: ProductMaturity
    disposition: Disposition
    next_action: str = Field(min_length=1, max_length=10000)
    next_work_item_id: str | None = None
    reason: str = Field(min_length=1, max_length=20000)
    author: str = Field(min_length=1, max_length=200)
    source_artifact_id: str | None = None
    decision_id: str | None = None


def legacy_disposition(value: str) -> tuple[Disposition, str | None]:
    value = value.upper()
    if value in {"INTERNAL_TRIAL", "INTERNAL_ONLY"}:
        return Disposition.INTERNAL_ONLY, None
    if value.startswith(("STOP", "REJECT")):
        return Disposition.DROPPED, None
    if value.startswith(("HOLD", "INPUT_HOLD", "ACCESS_HOLD")):
        return (
            Disposition.HOLD,
            "human_input" if value == "INPUT_HOLD" else "external_access",
        )
    if value.startswith("ADOPT"):
        return Disposition.USE_EXISTING, None
    if value in {"SHORTLIST_DISCOVERY", "REFRAME_LEARNING", "INVESTIGATE", "CONTINUE"}:
        return Disposition.PURSUE, None
    return Disposition.HOLD, "other"


class ReviewService:
    def __init__(self, factory: SessionFactory) -> None:
        self.factory = factory

    @staticmethod
    def _json(session: Session, review: WorkspaceReview) -> JSON:
        work = (
            session.get(WorkItem, review.next_work_item_id)
            if review.next_work_item_id
            else None
        )
        blocker = None
        if work and work.status == WorkItemStatus.BLOCKED:
            blocker = (
                work.blocked_reason
                if work.blocked_reason in {"human_input", "external_access", "setup"}
                else "other"
            )
        return {
            "id": review.id,
            "workspace_id": review.workspace_id,
            "revision": review.revision,
            "investigation_stage": review.investigation_stage.value,
            "product_maturity": review.product_maturity.value,
            "disposition": Disposition(review.disposition).value,
            "next_action": review.next_action,
            "next_work_item_id": review.next_work_item_id,
            "reason": review.reason,
            "author": review.author,
            "reviewed_at": review.reviewed_at.isoformat(),
            "source_artifact_id": review.source_artifact_id,
            "decision_id": review.decision_id,
            "work_state": work.status.value if work else "not_scheduled",
            "blocker": blocker,
            "owner": work.owner if work else None,
        }

    @staticmethod
    def _append(session: Session, payload: ReviewInput) -> WorkspaceReview:
        if session.get(Workspace, payload.workspace_id) is None:
            raise ReferenceError("Workspace does not exist")
        current = (
            session.scalar(
                select(func.max(WorkspaceReview.revision)).where(
                    WorkspaceReview.workspace_id == payload.workspace_id
                )
            )
            or 0
        )
        if current != payload.expected_revision:
            raise ConflictError(
                f"Review changed: expected {payload.expected_revision}, "
                f"current {current}. Reload before editing."
            )
        for model, identity in [
            (WorkItem, payload.next_work_item_id),
            (Artifact, payload.source_artifact_id),
            (Decision, payload.decision_id),
        ]:
            if identity is not None:
                referenced = session.get(model, identity)
                if (
                    referenced is None
                    or getattr(referenced, "workspace_id", None) != payload.workspace_id
                ):
                    raise ReferenceError(
                        "Review references must belong to the same workspace"
                    )
        if not all(
            t.strip() for t in [payload.reason, payload.next_action, payload.author]
        ):
            raise ValidationError("Reason, next action and author must be nonblank")
        review = WorkspaceReview(
            **payload.model_dump(exclude={"expected_revision"}), revision=current + 1
        )
        session.add(review)
        session.flush()
        return review

    def append(self, payload: ReviewInput) -> JSON:
        try:
            with UnitOfWork(self.factory) as unit:
                session = unit.session
                assert session is not None
                return self._json(session, self._append(session, payload))
        except IntegrityError as exc:
            raise ConflictError(
                "Review changed concurrently; reload before editing"
            ) from exc

    def show(self, workspace_id: str) -> JSON:
        with self.factory() as session:
            if session.get(Workspace, workspace_id) is None:
                raise ReferenceError("Workspace does not exist")
            history = [
                self._json(session, r)
                for r in session.scalars(
                    select(WorkspaceReview)
                    .where(WorkspaceReview.workspace_id == workspace_id)
                    .order_by(WorkspaceReview.revision.desc())
                )
            ]
            return {"current": history[0] if history else None, "history": history}

    def inbox_status(self, content: str) -> list[JSON]:
        """Inspect only the four explicitly supported inbox sections, read-only."""
        with self.factory() as session:
            artifacts = session.scalars(
                select(Artifact)
                .where(
                    Artifact.name.in_(
                        [
                            key + " answer receipt"
                            for key in ["R001", "R002", "R003", "R004"]
                        ]
                    )
                )
                .order_by(Artifact.created_at.desc(), Artifact.id)
            ).all()
            result = []
            seen = set()
            for artifact in artifacts:
                metadata = artifact.metadata_json
                key = metadata.get("request_id")
                if key in seen or key not in {"R001", "R002", "R003", "R004"}:
                    continue
                seen.add(key)
                marker = "## " + key + " — "
                section = (
                    content.split(marker, 1)[1].split("\n## ", 1)[0]
                    if marker in content
                    else ""
                )
                current = hashlib.sha256(section.encode()).hexdigest()
                result.append(
                    {
                        "request_id": key,
                        "artifact_id": artifact.id,
                        "state": "Reviewed"
                        if current == metadata.get("section_sha256")
                        else "New answer awaiting review",
                        "reviewed_digest": metadata.get("section_sha256"),
                        "current_digest": current,
                        "limits": (
                            "An answer does not automatically close "
                            "the narrower follow-up."
                        ),
                    }
                )
            return result

    def import_legacy(self) -> JSON:
        imported = 0
        mapping: dict[str, JSON] = {}
        with UnitOfWork(self.factory) as unit:
            session = unit.session
            assert session is not None
            artifacts = session.scalars(
                select(Artifact)
                .where(
                    Artifact.name.in_(
                        ["Campaign disposition", "Investigation disposition"]
                    )
                )
                .order_by(Artifact.created_at.desc(), Artifact.id)
            ).all()
            seen = set()
            for artifact in artifacts:
                value = str(artifact.metadata_json.get("disposition", "unknown"))
                disposition, blocker = legacy_disposition(value)
                mapping[value] = {"disposition": disposition.value, "blocker": blocker}
                if artifact.workspace_id in seen:
                    continue
                seen.add(artifact.workspace_id)
                if session.scalar(
                    select(WorkspaceReview.id).where(
                        WorkspaceReview.workspace_id == artifact.workspace_id
                    )
                ):
                    continue
                reason = (
                    artifact.metadata_json.get("rationale")
                    or "Legacy state with incomplete rationale; source retained."
                )
                action = (
                    artifact.metadata_json.get("next_action")
                    or artifact.metadata_json.get("next_test")
                    or "Review the retained finding and specify the next bounded test."
                )
                work = None
                if blocker:
                    work = WorkItem(
                        workspace_id=artifact.workspace_id,
                        title=str(action)[:300],
                        description=str(reason),
                        question=str(action),
                        kind=WorkItemKind.INVESTIGATION,
                        status=WorkItemStatus.BLOCKED,
                        owner="human" if blocker == "human_input" else "agent",
                        blocked_reason=blocker,
                        acceptance_criteria=str(action),
                    )
                    session.add(work)
                    session.flush()
                review = self._append(
                    session,
                    ReviewInput(
                        workspace_id=artifact.workspace_id,
                        expected_revision=0,
                        investigation_stage=InvestigationStage.COMPARISON,
                        product_maturity=ProductMaturity.CONCEPT,
                        disposition=disposition,
                        next_action=str(action),
                        next_work_item_id=work.id if work else None,
                        reason=str(reason),
                        author="legacy-campaign-import-v1",
                        source_artifact_id=artifact.id,
                    ),
                )
                review.reviewed_at = artifact.created_at
                imported += 1
        return {
            "imported": imported,
            "mapping": mapping,
            "unknown_bucket": "hold / other",
        }
