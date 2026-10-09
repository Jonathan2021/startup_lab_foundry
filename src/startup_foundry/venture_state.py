"""One derived venture state for the header, lists, Today and agent resume.

ADR-0020. The state is a read projection over the append-only review, the
selected score, work, human requests and proposals. It never writes. The stored
``Venture.stage`` is creation-time lifecycle data: it is reported only when it
differs from what the current review implies, and is never silently rewritten.
"""

from __future__ import annotations

from typing import Any

from sqlalchemy import select
from sqlalchemy.orm import Session

from startup_foundry.domain import (
    Disposition,
    HumanRequest,
    HumanRequestTarget,
    InvestigationStage,
    ProductMaturity,
    Venture,
    VentureAssessment,
    VentureStage,
    WorkItem,
    WorkItemStatus,
    WorkspaceReview,
)
from startup_foundry.scoring import ORIGINAL, REVIEWED

JSON = dict[str, Any]
OPEN_REQUEST_STATUSES = ("waiting_for_answer", "needs_clarification")
GATE_BLOCKERS = {"human_input", "external_access", "setup"}
VALIDATION_STAGES = {
    InvestigationStage.PROBLEM_VALIDATION,
    InvestigationStage.SOLUTION_VALIDATION,
    InvestigationStage.BUSINESS_VALIDATION,
}


def pretty(value: str) -> str:
    return value.replace("_", " ").capitalize()


def current_review(session: Session, workspace: str) -> WorkspaceReview | None:
    return session.scalar(
        select(WorkspaceReview)
        .where(WorkspaceReview.workspace_id == workspace)
        .order_by(WorkspaceReview.revision.desc())
        .limit(1)
    )


def implied_lifecycle(review: WorkspaceReview | None) -> VentureStage | None:
    """The lifecycle a review implies; None when nothing has been reviewed."""
    if review is None:
        return None
    disposition = Disposition(review.disposition)
    if disposition == Disposition.DROPPED:
        return VentureStage.ARCHIVED
    if disposition == Disposition.HOLD:
        return VentureStage.PAUSED
    maturity = ProductMaturity(review.product_maturity)
    if maturity == ProductMaturity.OPERATING:
        return VentureStage.OPERATING
    if maturity == ProductMaturity.PILOT:
        return VentureStage.PILOT
    if maturity in {ProductMaturity.MVP, ProductMaturity.PROTOTYPE}:
        return VentureStage.BUILD
    if InvestigationStage(review.investigation_stage) in VALIDATION_STAGES:
        return VentureStage.VALIDATION
    return VentureStage.DISCOVERY


def score_status(session: Session, venture: Venture) -> JSON:
    """The header's selected score and whether it predates the current scope.

    Selection matches the venture score view: the latest reviewed judgment on the
    reviewed card, else the latest on that card, else the original baseline.
    """
    rows = list(
        session.scalars(
            select(VentureAssessment)
            .where(
                VentureAssessment.venture_id == venture.id,
                VentureAssessment.scorecard_id.in_([REVIEWED, ORIGINAL]),
            )
            .order_by(
                VentureAssessment.created_at.desc(),
                VentureAssessment.sequence.desc(),
            )
        )
    )
    selected = (
        next(
            (a for a in rows if a.scorecard_id == REVIEWED and a.kind == "reviewed"),
            None,
        )
        or next((a for a in rows if a.scorecard_id == REVIEWED), None)
        or next((a for a in rows if a.scorecard_id == ORIGINAL), None)
    )
    if selected is None:
        return {"status": "not_scored", "assessment_id": None, "total": None}
    scope = {
        "objective": venture.objective,
        "source_idea_revision_id": venture.source_idea_revision_id,
    }
    recorded = {key: selected.context_json.get(key) for key in scope}
    return {
        "status": "predates_scope" if recorded != scope else "current",
        "assessment_id": selected.id,
        "total": selected.overall_score,
        "scorecard_id": selected.scorecard_id,
        "kind": selected.kind,
    }


def request_file_state(request: HumanRequest) -> str | None:
    sync = (request.source_diagnostics or {}).get("file_sync")
    return sync.get("state") if isinstance(sync, dict) else None


def open_requests(session: Session, workspace: str) -> list[JSON]:
    """Human requests targeting this workspace that still wait for the human."""
    rows = session.scalars(
        select(HumanRequest)
        .join(HumanRequestTarget, HumanRequestTarget.request_id == HumanRequest.id)
        .where(
            HumanRequestTarget.workspace_id == workspace,
            HumanRequest.status.in_(OPEN_REQUEST_STATUSES),
        )
        .order_by(HumanRequest.id)
    )
    items = []
    for request in rows:
        sync = (request.source_diagnostics or {}).get("file_sync")
        items.append(
            {
                "id": request.id,
                "title": request.title,
                "status": request.status,
                "file_state": request_file_state(request),
                "file": sync.get("file") if isinstance(sync, dict) else None,
                "url": "/requests/" + request.id,
            }
        )
    return items


def venture_state(
    session: Session, venture: Venture, *, superseded: set[str] | None = None
) -> JSON:
    """Disposition, investigation, maturity, score, next action and open gates."""
    from startup_foundry.decision_maps import superseded_work
    from startup_foundry.proposals import stale_proposals_for_venture

    review = current_review(session, venture.workspace_id)
    implied = implied_lifecycle(review)
    disposition = Disposition(review.disposition).value if review else "not_reviewed"
    stage = InvestigationStage(review.investigation_stage).value if review else "intake"
    maturity = ProductMaturity(review.product_maturity).value if review else "unknown"
    work = (
        session.get(WorkItem, review.next_work_item_id)
        if review and review.next_work_item_id
        else None
    )
    superseded = (
        superseded
        if superseded is not None
        else set(superseded_work(session, venture.workspace_id))
    )
    gates: list[JSON] = []
    for request in open_requests(session, venture.workspace_id):
        gates.append({"kind": "human_request", **request})
    for blocked in session.scalars(
        select(WorkItem)
        .where(
            WorkItem.workspace_id == venture.workspace_id,
            WorkItem.status == WorkItemStatus.BLOCKED,
            WorkItem.blocked_reason.in_(sorted(GATE_BLOCKERS)),
        )
        .order_by(WorkItem.created_at, WorkItem.id)
    ):
        if blocked.id not in superseded:
            gates.append(
                {
                    "kind": "blocked_work",
                    "id": blocked.id,
                    "title": blocked.title,
                    "reason": blocked.blocked_reason,
                }
            )
    for proposal in stale_proposals_for_venture(session, venture.id):
        gates.append({"kind": "stale_proposal", **proposal})
    stored = venture.stage.value
    return {
        "venture_id": venture.id,
        "alias": venture.alias,
        "workspace_id": venture.workspace_id,
        "disposition": disposition,
        "investigation_stage": stage,
        "product_maturity": maturity,
        "headline": " · ".join(pretty(v) for v in [disposition, stage, maturity]),
        "review_revision": review.revision if review else 0,
        "lifecycle": {
            "stored": stored,
            "implied": implied.value if implied else None,
            "differs": implied is not None and implied.value != stored,
        },
        "score": score_status(session, venture),
        "next_action": {
            "text": review.next_action if review else "Specify the next bounded task",
            "work_id": work.id if work else None,
            "work_title": work.title if work else None,
            "work_status": work.status.value if work else "not_scheduled",
            "owner": work.owner if work else None,
        },
        "open_gates": gates,
        "open_gate_count": len(gates),
        "superseded_work_count": len(superseded),
    }


def state_for_workspace(session: Session, workspace: str) -> JSON | None:
    venture = session.scalar(select(Venture).where(Venture.workspace_id == workspace))
    return venture_state(session, venture) if venture else None
