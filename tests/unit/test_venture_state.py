"""Truthful derived venture state and attention (ADR-0020, package F07)."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.application import FoundryApplication
from startup_foundry.decision_contracts import (
    ContextInput,
    MapInput,
    ResolveResultInput,
    ResultInput,
    WorkCloseInput,
)
from startup_foundry.decision_maps import DecisionMapService
from startup_foundry.domain import (
    AuditEvent,
    Decision,
    DecisionKind,
    DecisionStatus,
    Venture,
    VentureStage,
    WorkItem,
    WorkItemStatus,
)
from startup_foundry.errors import ConflictError
from startup_foundry.manual_intake import ManualIntakeService
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.proposals import FusionInput, ProposalService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import FACTORS
from startup_foundry.venture_scoring import (
    VentureAssessmentInput,
    VentureScoringService,
)
from startup_foundry.views import PortfolioQuery, PortfolioViewService
from startup_foundry.web import create_app
from startup_foundry.workspace_history import relative_time

NEXT_ACTION = "Run the five-lunch falsification test " + "x" * 260
SUPERSEDED = "Superseded as an executable priority by decision D1; history retained"


def node(identity: str, work_id: str, title: str) -> dict[str, object]:
    return {
        "id": identity,
        "kind": "record",
        "title": title,
        "ref": {"kind": "work", "id": work_id},
    }


@pytest.fixture
def world(tmp_path):
    url = f"sqlite:///{tmp_path / 'state.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    portfolio = PortfolioService(factory)
    FoundryApplication(factory).create_venture(
        venture_id="v-foundry",
        name="Foundry",
        objective="Coordination",
        stage=VentureStage.DISCOVERY,
    )
    portfolio.create_idea(
        IdeaDraft(title="Crous queue", description="Lunch queue estimates"),
        idea_id="P1",
    )
    venture = portfolio.promote_idea("P1", venture_id="v-queue")
    ws = venture["workspace_id"]
    intake = ManualIntakeService(factory).handoff("venture", "v-queue")
    assert intake is not None
    with factory.begin() as session:
        session.get(WorkItem, intake["work_id"]).status = WorkItemStatus.CANCELLED
        legacy = WorkItem(
            workspace_id=ws,
            title="Legacy pilot recruitment",
            kind="investigation",
            status="ready",
            owner="agent",
        )
        gate = WorkItem(
            workspace_id=ws,
            title="Operator approves hosting",
            kind="investigation",
            status="blocked",
            blocked_reason="human_input",
            owner="human",
        )
        current = WorkItem(
            workspace_id=ws,
            title="Harden the MVP",
            kind="execution",
            status="ready",
            owner="agent",
        )
        session.add_all([legacy, gate, current])
        session.flush()
        ids = {"legacy": legacy.id, "gate": gate.id, "current": current.id}
    maps = DecisionMapService(factory)
    draft = {
        "nodes": [
            {"id": "goal", "kind": "goal", "title": "Useful queue estimates"},
            {"id": "question", "kind": "question", "title": "Do students report?"},
            node("legacy", ids["legacy"], "Legacy pilot"),
            node("gate", ids["gate"], "Hosting gate"),
            node("current", ids["current"], "Harden"),
        ],
        "edges": [
            {"source": "legacy", "target": "goal", "kind": "contributes_to"},
            {"source": "gate", "target": "goal", "kind": "contributes_to"},
            {"source": "current", "target": "goal", "kind": "contributes_to"},
        ],
        "focus": ["current"],
    }
    first = maps.revise(
        ws,
        MapInput.model_validate(
            {
                "expected_head": None,
                "request_key": "m1",
                "actor": "operator",
                "rationale": "Initial map",
                "map": draft,
            }
        ),
    )
    with factory() as session:
        legacy_version = session.get(WorkItem, ids["legacy"]).version_id
    head = maps.revise(
        ws,
        MapInput.model_validate(
            {
                "expected_head": first["id"],
                "request_key": "m2",
                "actor": "operator",
                "rationale": "Retire legacy pilot",
                "map": draft,
                "work_treatments": [
                    {
                        "work_id": ids["legacy"],
                        "expected_version": legacy_version,
                        "action": "pause",
                        "rationale": SUPERSEDED,
                    }
                ],
            }
        ),
    )
    ReviewService(factory).append(
        ReviewInput(
            workspace_id=ws,
            expected_revision=0,
            investigation_stage="solution_validation",
            product_maturity="mvp",
            disposition="pursue",
            next_action=NEXT_ACTION,
            next_work_item_id=ids["current"],
            reason="CI-verified MVP",
            author="reviewer",
        )
    )
    client = TestClient(
        create_app(factory, tmp_path / "requests"), base_url="http://127.0.0.1"
    )
    yield factory, ws, ids, head, client, draft
    engine.dispose()


def test_one_derived_state_drives_header_list_today_and_resume(world):
    factory, ws, ids, _, client, _ = world
    resume = AgentHandoffService(factory).resume(ws)
    state = resume["venture_state"]
    assert state["headline"] == "Pursue · Solution validation · Mvp"
    assert state["lifecycle"] == {
        "stored": "discovery",
        "implied": "build",
        "differs": True,
    }
    assert state["next_action"]["work_id"] == ids["current"]
    assert [g["id"] for g in state["open_gates"]] == [ids["gate"]]
    assert "State: Pursue · Solution validation · Mvp" in resume["markdown"]
    listed = PortfolioViewService(factory).list("venture", PortfolioQuery())
    card = next(i for i in listed["items"] if i["id"] == "v-queue")
    assert card["state"] == state
    page = client.get("/ventures/v-queue").text
    assert "Pursue · Solution validation · Mvp" in page
    assert "Lifecycle (recorded): Discovery" in page
    assert page.count(NEXT_ACTION) == 1, "next action rendered once in the header"
    assert "Operator approves hosting" in page and "Open gates (1)" in page
    today = client.get("/").text
    assert "Pursue · Solution validation · Mvp" in today
    assert "Lifecycle (recorded): Discovery" in client.get("/ventures").text


def test_lifecycle_note_is_hidden_when_the_review_agrees(world):
    factory, ws, _, _, client, _ = world
    with factory.begin() as session:
        session.get(Venture, "v-queue").stage = VentureStage.BUILD
    state = AgentHandoffService(factory).resume(ws)["venture_state"]
    assert state["lifecycle"]["differs"] is False
    assert "Lifecycle (recorded)" not in client.get("/ventures/v-queue").text


def test_stale_score_offers_reassessment(world):
    factory, ws, _, _, client, _ = world
    VentureScoringService(factory).assess(
        VentureAssessmentInput(
            venture_id="v-queue",
            expected_sequence=0,
            request_key="score-1",
            scores={key: 6 for key, _, _, _ in FACTORS},
            rationale="Before narrowing",
            author="reviewer",
        )
    )
    assert "Reassess" not in client.get("/ventures/v-queue").text
    with factory.begin() as session:
        session.get(Venture, "v-queue").objective = "Narrowed falsification test"
    state = AgentHandoffService(factory).resume(ws)["venture_state"]
    assert state["score"]["status"] == "predates_scope"
    page = client.get("/ventures/v-queue").text
    assert "Assessment predates current scope" in page
    assert 'tab=scores#reassess">Reassess</a>' in page
    scores = client.get("/ventures/v-queue?tab=scores").text
    assert 'id="reassess" open' in scores


def test_cancelled_initial_review_is_never_offered_as_startable(world):
    _, _, _, _, client, _ = world
    work = client.get("/ventures/v-queue?tab=work").text
    assert "Manual review cancelled" in work
    assert "Copy manual review handoff" not in work
    assert "Start an agent session" not in work


def test_superseded_legacy_work_is_listed_apart_and_closed_with_audit(world):
    factory, ws, ids, _, client, _ = world
    handoffs = AgentHandoffService(factory)
    resume = handoffs.resume(ws)
    assert ids["legacy"] not in resume["needs_review"]
    assert [s["id"] for s in resume["superseded"]] == [ids["legacy"]]
    assert "## Superseded (close or revise)" in resume["markdown"]
    assert "venture-work close" in resume["markdown"]
    page = client.get("/ventures/v-queue").text
    assert "Some decisions need review" not in page
    assert "Close as superseded" in page
    version = resume["superseded"][0]["version_id"]
    payload = WorkCloseInput(
        work_id=ids["legacy"],
        expected_version=version,
        actor="operator",
        rationale="Superseded by decision D1",
    )
    closed = handoffs.close_work(ws, payload)
    assert closed["status"] == "cancelled" and closed["map_revision_id"]
    assert handoffs.close_work(ws, payload) == closed, "retry returns the receipt"
    with factory() as session:
        assert session.get(WorkItem, ids["legacy"]).status == WorkItemStatus.CANCELLED
        event = session.scalar(
            select(AuditEvent).where(
                AuditEvent.entity_id == ids["legacy"],
                AuditEvent.event_type == "work_closed",
            )
        )
        assert event is not None and event.actor == "operator"
        assert event.payload["previous"]["superseded_reason"] == SUPERSEDED
    after = handoffs.resume(ws)
    assert after["superseded"] == [] and ids["legacy"] not in after["needs_review"]
    with pytest.raises(ConflictError):
        handoffs.close_work(
            ws,
            payload.model_copy(update={"rationale": "A different request"}),
        )


def test_claimed_work_cannot_be_closed_by_another_session(world):
    factory, ws, ids, _, _, _ = world
    with factory.begin() as session:
        work = session.get(WorkItem, ids["current"])
        work.status, work.owner = WorkItemStatus.IN_PROGRESS, "agent-a"
    with factory() as session:
        version = session.get(WorkItem, ids["current"]).version_id
    with pytest.raises(ConflictError, match="released"):
        AgentHandoffService(factory).close_work(
            ws,
            WorkCloseInput(
                work_id=ids["current"],
                expected_version=version,
                actor="agent-b",
                rationale="Not mine",
            ),
        )


def test_close_command_is_public(world, tmp_path, capsys):
    import json

    from startup_foundry.cli import main

    factory, ws, ids, _, _, _ = world
    store = str(factory.kw["bind"].url.database)
    assert main(["--store", store, "agent", "schema", "--name", "close"]) == 0
    assert set(json.loads(capsys.readouterr().out)["required"]) == {
        "work_id",
        "expected_version",
        "actor",
        "rationale",
    }
    with factory() as session:
        version = session.get(WorkItem, ids["legacy"]).version_id
    payload = tmp_path / "close.json"
    payload.write_text(
        json.dumps(
            {
                "work_id": ids["legacy"],
                "expected_version": version,
                "actor": "operator",
                "rationale": "Superseded",
            }
        )
    )
    code = main(
        [
            "--store",
            store,
            "venture-work",
            "close",
            "--workspace-id",
            ws,
            "--input",
            str(payload),
        ]
    )
    assert code == 0
    assert json.loads(capsys.readouterr().out)["status"] == "cancelled"


def test_stale_fusion_proposal_is_not_the_current_focus(world):
    factory, ws, _, _, client, _ = world
    portfolio = PortfolioService(factory)
    portfolio.create_idea(IdeaDraft(title="Other", description="x"), idea_id="P2")
    portfolio.promote_idea("P2", venture_id="v-other")
    proposals = ProposalService(factory)
    proposal = proposals.create(
        FusionInput(
            name="Merged queues",
            description="Combine",
            source_idea_ids=["P1", "P2"],
            source_venture_ids=["v-queue", "v-other"],
            result_venture_id="v-merged",
            request_key="fusion",
            rationale="Shared users",
            scope=[
                {
                    "capability": "Queue",
                    "treatment": "combined",
                    "reason": "Same",
                    "provenance": "R1",
                }
            ],
            alternatives=["Keep separate"],
        )
    )
    assert proposals.show(proposal["id"])["stale_reason"] is None
    assert "Review fusion proposal" in client.get("/ventures/v-queue").text
    with factory.begin() as session:
        session.add(
            Decision(
                workspace_id=ws,
                kind=DecisionKind.NARROW,
                status=DecisionStatus.ACCEPTED,
                summary="Narrow to one restaurant",
                rationale="Fusion "
                + proposal["id"][:8]
                + " is historical lineage, superseded by this narrowing",
                decided_by="operator",
                decided_at=datetime.now(UTC) + timedelta(seconds=1),
            )
        )
    shown = proposals.show(proposal["id"])
    assert shown["state"] == "proposed", "history is never rewritten"
    assert shown["display_state"] == "stale_needs_resolution"
    page = client.get("/ventures/v-queue").text
    assert "Stale — needs resolution" in page
    assert '<a class="button" href="/proposals/' not in page
    state = AgentHandoffService(factory).resume(ws)["venture_state"]
    assert any(g["kind"] == "stale_proposal" for g in state["open_gates"])
    assert "Stale — needs resolution" in client.get("/proposals").text


def test_history_rows_show_summaries_and_relative_dates(world):
    _, _, _, _, client, _ = world
    page = client.get("/ventures/v-queue?tab=history").text
    assert "Retire legacy pilot" in page or "Initial map" in page
    assert "Run the five-lunch falsification test" in page
    assert " ago" in page or "just now" in page
    now = datetime(2026, 10, 9, tzinfo=UTC)
    assert relative_time(now - timedelta(days=3), now) == "3 days ago"
    assert relative_time(now - timedelta(seconds=5), now) == "just now"


def test_new_edge_from_unchanged_work_does_not_flag_it(world):
    factory, ws, ids, head, _, draft = world
    changed = {
        **draft,
        "edges": [
            *draft["edges"],
            {"source": "gate", "target": "question", "kind": "tests"},
        ],
    }
    revised = DecisionMapService(factory).revise(
        ws,
        MapInput.model_validate(
            {
                "expected_head": head["id"],
                "request_key": "m3",
                "actor": "operator",
                "rationale": "Explain what the gate tests",
                "map": changed,
            }
        ),
    )
    assert ids["gate"] not in revised["needs_review"]
    dependency = {
        **changed,
        "edges": [
            *changed["edges"],
            {"source": "current", "target": "gate", "kind": "depends_on"},
        ],
    }
    revised = DecisionMapService(factory).revise(
        ws,
        MapInput.model_validate(
            {
                "expected_head": revised["id"],
                "request_key": "m4",
                "actor": "operator",
                "rationale": "Hardening now waits for hosting",
                "map": dependency,
            }
        ),
    )
    assert ids["current"] in revised["needs_review"]


def test_work_scoped_result_keeps_hold_next_action_and_preview_lists_changes(world):
    factory, ws, ids, _, _, _ = world
    ReviewService(factory).append(
        ReviewInput(
            workspace_id=ws,
            expected_revision=1,
            investigation_stage="solution_validation",
            product_maturity="mvp",
            disposition="hold",
            next_action="HOLD until the operator answers R011",
            next_work_item_id=ids["current"],
            reason="Venture on hold",
            author="reviewer",
        )
    )
    handoffs = AgentHandoffService(factory)
    head = DecisionMapService(factory).show(ws)["id"]
    with factory() as session:
        version = session.get(WorkItem, ids["current"]).version_id
    context = handoffs.prepare(
        ws,
        ContextInput(
            work_id=ids["current"],
            expected_work_version=version,
            expected_head=head,
            request_key="ctx",
            actor="agent",
        ),
    )
    result = handoffs.submit(
        ws,
        ResultInput(
            context_id=context["id"],
            request_key="r1",
            actor="agent",
            summary="Hardening package delivered",
            rationale="Checks pass",
            limits="Local only",
            outcome="continue",
            next_action="Start the next code package",
            findings=[
                {
                    "summary": "Delivery: main=abc1234 ci=1",
                    "epistemic_status": "inference",
                }
            ],
        ),
    )
    choice = ResolveResultInput(
        expected_result_digest=result["digest"],
        expected_head=context["map_revision_id"],
        expected_work_version=context["work"]["version_id"],
        expected_review_revision=context["review_revision"],
        resolution="accept",
        actor="agent",
        rationale="Routine",
        coverage_action="accept_limitation",
        coverage_rationale="Fixture",
    )
    preview = handoffs.preview(result["id"], choice)["effects"]
    assert preview["next_action_retained"] is True
    fields = {c["field"]: c for c in preview["review_changes"]}
    assert "next_action" not in fields
    assert fields["next_work_item_id"]["before"] == ids["current"]
    receipt = handoffs.resolve(result["id"], choice)
    assert receipt["effects"]["next_action_retained"] is True
    review = ReviewService(factory).show(ws)["current"]
    assert review["next_action"] == "HOLD until the operator answers R011"
    assert review["disposition"] == "hold"


def test_evidence_cited_by_an_accepted_result_leaves_the_attention_list(world):
    from startup_foundry.decision_contracts import CaptureInput

    factory, ws, ids, _, client, _ = world
    handoffs = AgentHandoffService(factory)
    head = DecisionMapService(factory).show(ws)["id"]
    with factory() as session:
        version = session.get(WorkItem, ids["current"]).version_id
    captured = handoffs.capture(
        ws,
        CaptureInput(
            request_key="ci-run",
            actor="agent",
            summary="CI run 42 passed on main=abc1234",
            sources=["observation: CI"],
        ),
    )
    other = handoffs.capture(
        ws,
        CaptureInput(
            request_key="unrelated",
            actor="agent",
            summary="Unrelated supplier note",
            sources=["observation: note"],
        ),
    )
    before = {c["id"] for c in handoffs.resume(ws)["unreviewed_changes"]}
    assert {captured["evidence_id"], other["evidence_id"]} <= before
    head = DecisionMapService(factory).show(ws)["id"]
    context = handoffs.prepare(
        ws,
        ContextInput(
            work_id=ids["current"],
            expected_work_version=version,
            expected_head=head,
            request_key="ctx-after-capture",
            actor="agent",
        ),
    )
    result = handoffs.submit(
        ws,
        ResultInput(
            context_id=context["id"],
            request_key="cites-ci",
            actor="agent",
            summary="Package delivered",
            rationale="CI evidence cited",
            limits="Local",
            outcome="continue",
            next_action="Next package",
            findings=[
                {
                    "summary": "Verified on CI",
                    "refs": [{"kind": "evidence", "id": captured["evidence_id"]}],
                }
            ],
        ),
    )
    handoffs.resolve(
        result["id"],
        ResolveResultInput(
            expected_result_digest=result["digest"],
            expected_head=context["map_revision_id"],
            expected_work_version=context["work"]["version_id"],
            expected_review_revision=context["review_revision"],
            resolution="accept",
            actor="agent",
            rationale="Routine",
            coverage_action="accept_limitation",
            coverage_rationale="Unrelated note left for the operator",
        ),
    )
    after = {c["id"] for c in handoffs.resume(ws)["unreviewed_changes"]}
    assert captured["evidence_id"] not in after
    assert other["evidence_id"] in after
    page = client.get("/ventures/v-queue").text
    assert "Unrelated supplier note" in page and "CI run 42 passed" not in page
