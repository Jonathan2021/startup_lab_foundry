"""Intake is an investigation, not an unconditional commitment to continue."""

import pytest
from sqlalchemy import select

from startup_foundry.domain import (
    Disposition,
    InvestigationStage,
    ProductMaturity,
    WorkItem,
    WorkItemStatus,
)
from startup_foundry.human_inputs import ClaimInput
from startup_foundry.manual_intake import (
    IntakeCompletion,
    IntakeRequest,
    ManualIntakeService,
)
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.reviews import ReviewInput, ReviewService


@pytest.fixture
def intake(tmp_path):
    url = f"sqlite:///{tmp_path / 'outcomes.db'}"
    upgrade_database(url)
    factory = create_session_factory(create_db_engine(url))
    portfolio = PortfolioService(factory)
    idea = portfolio.create_idea(
        IdeaDraft(title="Operating service", description="Scope")
    )
    service = ManualIntakeService(factory)
    service.request(
        "idea",
        idea["id"],
        IntakeRequest(expected_revision_id=idea["revision_id"], actor="operator"),
    )
    return factory, portfolio, idea, service


def completion(work, **changes):
    return IntakeCompletion(
        **{
            "work_id": work["id"],
            "expected_version": work["version"],
            "actor": "reviewer",
            "request_key": "complete",
            "research_summary": "No gap",
            "research_source": "Synthetic observation",
            "research_limits": "One test",
            "scores": {},
            "score_rationale": "No scored factors",
            "unknown_reason": "Commercial evidence absent",
            "expected_sequence": 0,
            "expected_review_revision": 0,
            "outcome": "stop",
            "next_action": "Reopen only if a distinct gap is observed",
            **changes,
        }
    )


@pytest.mark.parametrize("outcome,disposition", [("stop", "dropped"), ("hold", "hold")])
def test_stop_hold_without_work_preserves_operating_maturity(
    intake, outcome, disposition
):
    factory, _, idea, service = intake
    h = service.handoff("idea", idea["id"])
    work = service.claim(
        "idea",
        idea["id"],
        ClaimInput(expected_version=h["work"]["version"], actor="reviewer"),
    )
    ReviewService(factory).append(
        ReviewInput(
            workspace_id=idea["workspace_id"],
            expected_revision=0,
            investigation_stage=InvestigationStage.BUSINESS_VALIDATION,
            product_maturity=ProductMaturity.OPERATING,
            disposition=Disposition.PURSUE,
            next_action="Investigate the new issue",
            reason="Established business",
            author="operator",
        )
    )
    data = completion(
        work,
        outcome=outcome,
        expected_review_revision=1,
        revisit_trigger="New evidence of unmet need" if outcome == "hold" else None,
    )
    result = service.complete("idea", idea["id"], data)
    assert result["next_work_id"] is None
    assert service.complete("idea", idea["id"], data) == result
    review = ReviewService(factory).show(idea["workspace_id"])["current"]
    assert review["disposition"] == disposition
    assert review["product_maturity"] == "operating"
    assert review["investigation_stage"] == "business_validation"
    with factory() as session:
        assert list(session.scalars(select(WorkItem.status))) == [WorkItemStatus.DONE]


def test_unstarted_promotion_supersedes_idea_intake(intake):
    factory, portfolio, idea, service = intake
    source = service.handoff("idea", idea["id"])
    venture = portfolio.promote_idea(idea["id"])
    handoff = service.handoff("venture", venture["id"])
    assert handoff["work"]["status"] == "ready"
    with factory() as session:
        assert (
            session.get(WorkItem, source["work_id"]).status == WorkItemStatus.CANCELLED
        )
        active = list(
            session.scalars(
                select(WorkItem).where(
                    WorkItem.status.in_(
                        [WorkItemStatus.READY, WorkItemStatus.IN_PROGRESS]
                    )
                )
            )
        )
        assert len(active) == 1
    assert (
        service.handoff("idea", idea["id"])["promotion"]["venture_id"] == venture["id"]
    )


@pytest.mark.parametrize("finished", [False, True])
def test_promotion_reuses_claimed_or_completed_research(intake, finished):
    factory, portfolio, idea, service = intake
    h = service.handoff("idea", idea["id"])
    work = service.claim(
        "idea",
        idea["id"],
        ClaimInput(expected_version=h["work"]["version"], actor="reviewer"),
    )
    if finished:
        service.complete("idea", idea["id"], completion(work))
    venture = portfolio.promote_idea(idea["id"])
    handoff = service.handoff("venture", venture["id"])
    assert handoff["linked_intake"]["idea_id"] == idea["id"]
    assert handoff["work_id"] == work["id"]
    with factory() as session:
        assert len(list(session.scalars(select(WorkItem)))) == 1


def test_operating_venture_without_a_previous_review_is_not_reset(intake):
    from startup_foundry.application import FoundryApplication
    from startup_foundry.domain import VentureStage

    factory, _, _, service = intake
    venture = FoundryApplication(factory).create_venture(
        venture_id="existing-operation",
        name="Operating business",
        objective="Maintain service",
        stage=VentureStage.OPERATING,
    )
    service.request(
        "venture",
        venture["id"],
        IntakeRequest(expected_revision_id=None, actor="operator"),
    )
    handoff = service.handoff("venture", venture["id"])
    claim = service.claim(
        "venture",
        venture["id"],
        ClaimInput(expected_version=handoff["work"]["version"], actor="reviewer"),
    )
    service.complete(
        "venture",
        venture["id"],
        completion(claim, outcome="hold", revisit_trigger="New evidence"),
    )
    assert (
        ReviewService(factory).show(venture["workspace_id"])["current"][
            "product_maturity"
        ]
        == "operating"
    )
