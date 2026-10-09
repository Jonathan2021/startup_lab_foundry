"""Atomic exact-revision portfolio changes, explicit authority and reversal."""

import pytest
from sqlalchemy import func, select

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import (
    ConfidenceLevel,
    Evidence,
    EvidenceKind,
    Idea,
    IdeaRevision,
    Venture,
    VentureStage,
)
from startup_foundry.errors import ConflictError, ValidationError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.proposals import (
    DelegationInput,
    FusionInput,
    ProposalService,
    ResolveInput,
    ReviseInput,
    SupersedeInput,
)
from startup_foundry.repository import create_db_engine, create_session_factory


def test_equivalent_sources_reuse_pending_proposal_and_changed_scope_conflicts(
    proposal,
):
    s, p, seed, f, portfolio = proposal
    reordered = seed.model_copy(
        update={
            "request_key": "different-key",
            "result_venture_id": "v-another",
            "source_idea_ids": list(reversed(seed.source_idea_ids)),
            "source_venture_ids": list(reversed(seed.source_venture_ids)),
        }
    )
    assert s.create(reordered)["id"] == p["id"]
    assert len(s.list(state="proposed")["items"]) == 1
    with pytest.raises(ConflictError):
        s.create(reordered.model_copy(update={"description": "Different scope"}))


def test_explicit_supersession_and_concurrent_semantic_duplicates(proposal):
    from concurrent.futures import ThreadPoolExecutor

    s, p, seed, f, portfolio = proposal
    replacement = s.supersede(
        p["id"],
        SupersedeInput(
            expected_version=p["version"],
            replacement=seed.model_copy(
                update={
                    "request_key": "superseded",
                    "description": "Narrower scope",
                    "rationale": "Replace the earlier draft explicitly",
                }
            ),
        ),
    )
    assert s.show(p["id"])["state"] == "superseded"
    assert replacement["state"] == "proposed"
    s.resolve(
        replacement["id"],
        ResolveInput(
            expected_version=replacement["version"],
            revision_id=replacement["revision_id"],
            action="reject",
            rationale="Fixture",
            actor="operator",
            actor_kind="user",
            request_key="reject-replacement",
        ),
    )
    with ThreadPoolExecutor(max_workers=2) as pool:
        results = list(
            pool.map(
                lambda key: s.create(seed.model_copy(update={"request_key": key})),
                ["racing-a", "racing-b"],
            )
        )
    assert len({r["id"] for r in results}) == 1
    assert len(s.list(state="proposed")["items"]) == 1


@pytest.mark.parametrize("change", ["objective", "idea", "score", "request"])
def test_result_context_changes_require_explicit_reversal_treatment(proposal, change):
    from pathlib import Path

    from startup_foundry.human_inputs import HumanInputService, RequestInput
    from startup_foundry.venture_scoring import (
        VentureAssessmentInput,
        VentureScoringService,
    )

    s, p, seed, f, portfolio = proposal
    accepted = s.resolve(p["id"], decision(p))
    before = s.show(p["id"])["activity_digest"]
    if change == "objective":
        with f.begin() as db:
            db.get(Venture, "v-volley").objective = "Changed objective"
    elif change == "idea":
        with f.begin() as db:
            idea = db.get(Idea, accepted["result"]["idea_id"])
            rev = IdeaRevision(
                idea_id=idea.id,
                revision_number=2,
                title="New scope",
                cleaned_description="Changed",
                original_text="Changed",
                change_reason="Narrow",
                authored_by="operator",
            )
            db.add(rev)
            db.flush()
            idea.current_revision_id = rev.id
    elif change == "score":
        VentureScoringService(f).assess(
            VentureAssessmentInput(
                venture_id="v-volley",
                expected_sequence=0,
                request_key="result-score",
                scores={"problem": 7},
                rationale="Partial",
                author="operator",
            )
        )
    else:
        HumanInputService(f, Path("/tmp")).register(
            RequestInput(
                id="R099",
                workspace_id=accepted["result"]["workspace_id"],
                target_workspace_ids=[accepted["result"]["workspace_id"]],
                title="New question",
                question="Scope?",
            )
        )
    after = s.show(p["id"])
    assert after["activity_digest"] != before
    assert after["activity_changes"]
    reverse = ResolveInput(
        expected_version=accepted["version"],
        revision_id=p["revision_id"],
        action="reverse",
        rationale="Reconsider",
        actor="operator",
        actor_kind="user",
        request_key="context-reverse",
    )
    with pytest.raises(ConflictError):
        s.resolve(p["id"], reverse)
    assert (
        s.resolve(
            p["id"],
            reverse.model_copy(
                update={
                    "activity_digest": after["activity_digest"],
                    "downstream_treatment": "Retain all activity; hold composite",
                }
            ),
        )["state"]
        == "reversed"
    )


@pytest.fixture
def proposal(tmp_path):
    url = f"sqlite:///{tmp_path / 'fusion.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    FoundryApplication(f).create_venture(
        venture_id="v-foundry",
        name="Foundry",
        objective="Fixture",
        stage=VentureStage.DISCOVERY,
    )
    for i in ["P023", "P103"]:
        p.create_idea(IdeaDraft(title=i, description="Fixture"), idea_id=i)
        p.promote_idea(i, venture_id="v-" + i)
    service = ProposalService(f)
    seed = FusionInput(
        name="Volleyball",
        description="Two bounded jobs",
        source_idea_ids=["P023", "P103"],
        source_venture_ids=["v-P023", "v-P103"],
        result_venture_id="v-volley",
        request_key="sports",
        rationale="Shared participants",
        scope=[
            {
                "capability": "Fair teams",
                "treatment": "combined",
                "reason": "Same group",
                "provenance": "R006",
            }
        ],
        alternatives=["Keep separate"],
    )
    result = service.create(seed)
    return service, result, seed, f, p


def decision(p, **kw):
    return ResolveInput(
        expected_version=p["version"],
        revision_id=p["revision_id"],
        action="accept",
        rationale="Use one investigation",
        actor="operator",
        actor_kind=kw.pop("actor_kind", "user"),
        request_key="accept",
        **kw,
    )


def test_repeat_accept_lineage_and_reversal(proposal):
    s, p, seed, f, portfolio = proposal
    assert s.create(seed)["id"] == p["id"]
    with f() as session:
        assert session.get(Venture, "v-volley") is None
    result = s.resolve(p["id"], decision(p))
    assert s.resolve(p["id"], decision(p))["result"] == result["result"]
    assert portfolio.show_idea("P103")["title"] == "P103"
    assert len(portfolio.show_idea(result["result"]["idea_id"])["parents"]) == 2
    s.resolve(
        p["id"],
        ResolveInput(
            expected_version=result["version"],
            revision_id=p["revision_id"],
            action="reverse",
            rationale="Reconsider",
            actor="operator",
            actor_kind="user",
            request_key="reverse",
        ),
    )
    historical = s.resolve(p["id"], decision(p))
    assert historical["state"] == "reversed"
    with f() as session:
        assert session.get(Venture, "v-volley") is not None


def test_stale_reject_edit_unauthorized_and_rollback(proposal, monkeypatch):
    s, p, seed, f, portfolio = proposal
    with pytest.raises(ValidationError):
        s.resolve(p["id"], decision(p, actor_kind="agent"))
    edited = s.revise(
        p["id"],
        ReviseInput(
            expected_version=p["version"],
            name="Focused volley",
            description="Narrowed scope",
            rationale="Reduce scope",
            actor="agent",
        ),
    )
    with pytest.raises(ConflictError):
        s.resolve(p["id"], decision(p))
    # A new work item or answer changes the effects digest too.
    from startup_foundry.domain import WorkItem, WorkItemKind, WorkItemStatus

    ws = portfolio.show_idea("P103")["workspace_id"]
    with f.begin() as session:
        session.add(
            WorkItem(
                workspace_id=ws,
                title="New finding",
                kind=WorkItemKind.INVESTIGATION,
                status=WorkItemStatus.READY,
            )
        )
    with pytest.raises(ConflictError):
        s.resolve(p["id"], decision(edited))
    fresh = s.revise(
        p["id"],
        ReviseInput(
            expected_version=edited["version"],
            name="Focused volley",
            description="Narrowed scope",
            rationale="Refresh effects",
            actor="agent",
        ),
    )

    def fail(*args):
        raise RuntimeError("Injected failure")

    monkeypatch.setattr(s, "_after_create", fail)
    with pytest.raises(RuntimeError):
        s.resolve(p["id"], decision(fresh))
    with f() as session:
        assert session.get(Venture, "v-volley") is None
    assert s.show(p["id"])["state"] == "proposed"
    rejected = s.resolve(
        p["id"],
        ResolveInput(
            expected_version=fresh["version"],
            revision_id=fresh["revision_id"],
            action="reject",
            rationale="Keep separate",
            actor="operator",
            actor_kind="user",
            request_key="reject",
        ),
    )
    assert rejected["state"] == "rejected"
    with f() as session:
        assert session.get(Venture, "v-volley") is None


@pytest.mark.parametrize("action", ["accept", "reject"])
def test_agent_needs_exact_human_delegation(proposal, action):
    s, p, *_ = proposal
    receipt = s.delegate(
        p["id"],
        DelegationInput(
            revision_id=p["revision_id"],
            delegate="agent",
            action=action,
            reason="Explicit disposable-fixture authorization",
            human_actor="operator",
        ),
    )
    result = s.resolve(
        p["id"],
        ResolveInput(
            expected_version=p["version"],
            revision_id=p["revision_id"],
            action=action,
            rationale="Delegated fixture decision",
            actor="agent",
            actor_kind="agent",
            delegation_id=receipt["id"],
            request_key="delegated",
        ),
    )
    assert result["state"] == ("applied" if action == "accept" else "rejected")


def test_reversal_after_activity_requires_explicit_treatment(proposal):
    s, p, seed, f, portfolio = proposal
    r = s.resolve(p["id"], decision(p))
    with f.begin() as session:
        ws = session.get(Venture, "v-volley").workspace_id
        session.add(
            Evidence(
                workspace_id=ws,
                kind=EvidenceKind.OBSERVATION,
                confidence=ConfidenceLevel.LOW,
                summary="Later observation",
                captured_by="tester",
            )
        )
    reversal = ResolveInput(
        expected_version=r["version"],
        revision_id=p["revision_id"],
        action="reverse",
        rationale="Preserve new observation",
        actor="operator",
        actor_kind="user",
        request_key="reverse",
    )
    with pytest.raises(ConflictError):
        s.resolve(p["id"], reversal)
    s.resolve(
        p["id"],
        reversal.model_copy(
            update={
                "activity_digest": s.show(p["id"])["activity_digest"],
                "downstream_treatment": (
                    "Retain target evidence; reopen sources and hold target for review"
                ),
            }
        ),
    )
    with f() as session:
        assert session.scalar(select(func.count()).select_from(Evidence)) == 1
