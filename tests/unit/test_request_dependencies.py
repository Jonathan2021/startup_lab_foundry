"""Request ownership and outcome invariants, including shared causes."""

import pytest
from sqlalchemy import func, select

from startup_foundry.domain import (
    Artifact,
    HumanRequestDependency,
    HumanRequestTarget,
    WorkItem,
    WorkspaceReview,
)
from startup_foundry.errors import ReferenceError, ValidationError
from startup_foundry.human_inputs import (
    ClaimInput,
    DependencyInput,
    HumanInputService,
    RequestInput,
    ResponseInput,
    ReviewResult,
    TargetChange,
)
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory


@pytest.fixture
def scenario(tmp_path):
    url = f"sqlite:///{tmp_path / 'requests.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    idea = p.create_idea(IdeaDraft(title="Sport", description="Fixture"))
    ws = idea["workspace_id"]
    s = HumanInputService(f, tmp_path)
    for r in ["R006", "R007"]:
        s.register(
            RequestInput(
                id=r, workspace_id=ws, target_workspace_ids=[ws], title=r, question=r
            )
        )
    with f.begin() as db:
        work = WorkItem(
            workspace_id=ws,
            title="Input dependency",
            kind="investigation",
            status="blocked",
            blocked_reason="human_input",
        )
        db.add(work)
        db.flush()
        wid = work.id
    return s, f, ws, wid


def link(s, r, ws, wid, **kw):
    s.link_dependency(
        r,
        DependencyInput(
            expected_version=s.show(r)["version"],
            workspace_id=ws,
            work_id=wid,
            actor="operator",
            reason="Explicit required input",
            **kw,
        ),
    )


def finish(s, r, ws, wid, outcome="sufficient", changes=True, close_ids=None):
    saved = s.submit(
        r,
        ResponseInput(
            expected_version=s.show(r)["version"],
            text="Answer",
            author="operator",
            submission_key=r,
        ),
    )
    claim = s.claim(r, ClaimInput(expected_version=saved["version"], actor="agent"))
    with s.factory() as db:
        revision = (
            db.scalar(
                select(func.max(WorkspaceReview.revision)).where(
                    WorkspaceReview.workspace_id == ws
                )
            )
            or 0
        )
    return s.complete(
        r,
        ReviewResult(
            work_id=claim["work_id"],
            response_id=claim["response_id"],
            actor="agent",
            interpretation="Bounded input",
            outcome=outcome,
            rationale="Test",
            changes=[
                TargetChange(
                    workspace_id=ws,
                    expected_revision=revision,
                    next_action="Next",
                    close_input_work_ids=close_ids if close_ids is not None else [wid],
                )
            ]
            if changes
            else [],
        ),
    )


def test_cross_request_dependency_and_mixed_effects_are_atomic(scenario):
    s, f, ws, wid = scenario
    # Legacy target linkage also remains authoritative during transition.
    with f.begin() as db:
        t = db.scalar(
            select(HumanRequestTarget).where(HumanRequestTarget.request_id == "R007")
        )
        t.work_item_id = wid
    with pytest.raises(ReferenceError):
        finish(s, "R006", ws, wid)
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "blocked"
        assert (
            db.scalar(
                select(func.count())
                .select_from(Artifact)
                .where(Artifact.name == "human-response-review/v1")
            )
            == 0
        )
    assert s.show("R007")["status"] == "waiting_for_answer"
    assert s.show("R006")["status"] == "reviewing"


def test_only_exact_satisfied_dependency_closes(scenario):
    s, f, ws, wid = scenario
    link(s, "R006", ws, wid)
    finish(s, "R006", ws, wid)
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "done"


def test_shared_input_closes_only_after_both_sufficient_reviews(scenario):
    s, f, ws, wid = scenario
    link(s, "R006", ws, wid)
    link(s, "R007", ws, wid)
    finish(s, "R006", ws, wid)
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "blocked"
    finish(s, "R007", ws, wid)
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "done"


def test_mixed_valid_and_invalid_closure_rolls_back_satisfaction(scenario):
    s, f, ws, wid = scenario
    link(s, "R006", ws, wid)
    with f.begin() as db:
        other = WorkItem(
            workspace_id=ws,
            title="Unrelated",
            kind="investigation",
            status="blocked",
            blocked_reason="human_input",
        )
        db.add(other)
        db.flush()
        foreign_id = other.id
    link(s, "R007", ws, foreign_id)
    with pytest.raises(ReferenceError):
        finish(s, "R006", ws, wid, close_ids=[wid, foreign_id])
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "blocked"
        assert not db.scalar(
            select(HumanRequestDependency.satisfied_response_id).where(
                HumanRequestDependency.work_item_id == wid
            )
        )
        assert db.scalar(select(func.count()).select_from(WorkspaceReview)) == 0


def test_shared_and_non_input_causes_stay_blocked(scenario):
    s, f, ws, wid = scenario
    link(s, "R006", ws, wid)
    link(s, "R007", ws, wid, other_causes=["runtime verification"])
    finish(s, "R006", ws, wid)
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "blocked"
    finish(s, "R007", ws, wid, changes=False, outcome="no_change")
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "blocked"


@pytest.mark.parametrize("outcome", ["no_change", "partial", "deferred"])
def test_non_sufficient_outcomes_cannot_close_dependencies(scenario, outcome):
    s, f, ws, wid = scenario
    link(s, "R006", ws, wid)
    with pytest.raises(ValidationError):
        finish(s, "R006", ws, wid, outcome=outcome)
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "blocked"
        assert (
            db.scalar(
                select(func.count())
                .select_from(Artifact)
                .where(Artifact.name == "human-response-review/v1")
            )
            == 0
        )


def test_no_change_records_only_review(scenario):
    s, f, ws, wid = scenario
    result = finish(s, "R006", ws, wid, outcome="no_change", changes=False)
    assert result["effects"] == []
    with f() as db:
        assert db.get(WorkItem, wid).status.value == "blocked"
