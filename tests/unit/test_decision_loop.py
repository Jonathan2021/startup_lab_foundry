"""Behavior contracts for durable, scoped lifecycle decisions and agent results."""

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.application import FoundryApplication
from startup_foundry.decision_console import portfolio_attention
from startup_foundry.decision_contracts import (
    ContextInput,
    MapInput,
    ResolveResultInput,
    ResultInput,
)
from startup_foundry.decision_maps import DecisionMapService
from startup_foundry.domain import (
    Artifact,
    Decision,
    Evidence,
    Venture,
    WorkItem,
    WorkItemStatus,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.web import create_app


@pytest.fixture
def loop(tmp_path):
    url = f"sqlite:///{tmp_path / 'loop.db'}"
    upgrade_database(url)
    factory = create_session_factory(create_db_engine(url))
    p = PortfolioService(factory)
    idea = p.create_idea(
        IdeaDraft(title="Release service", description="Reliable billing")
    )
    venture = p.promote_idea(idea["id"])
    ws = venture["workspace_id"]
    with factory.begin() as session:
        work = session.scalar(select(WorkItem).where(WorkItem.workspace_id == ws))
        work.title = "Check release safety"
        evidence = Evidence(
            workspace_id=ws,
            summary="r18 staging crosses accounts",
            details="Synthetic staging test; production unknown",
            kind="experiment_result",
            confidence="high",
        )
        sibling = WorkItem(
            workspace_id=ws,
            title="Improve help pages",
            kind="execution",
            status="ready",
            owner="agent",
        )
        session.add_all([evidence, sibling])
        session.flush()
        wid, eid, sibling_id = work.id, evidence.id, sibling.id
    maps, handoffs = DecisionMapService(factory), AgentHandoffService(factory)
    data = MapInput.model_validate(
        {
            "expected_head": None,
            "request_key": "initial",
            "actor": "operator",
            "rationale": "Make the release gate explicit",
            "map": {
                "nodes": [
                    {"id": "goal", "kind": "goal", "title": "Operate reliable billing"},
                    {
                        "id": "gate",
                        "kind": "question",
                        "title": "Does r18 isolate accounts?",
                    },
                    {
                        "id": "work",
                        "kind": "record",
                        "title": "Release check",
                        "ref": {"kind": "work", "id": wid},
                    },
                    {
                        "id": "source",
                        "kind": "record",
                        "title": "Staging finding",
                        "ref": {"kind": "evidence", "id": eid},
                    },
                    {"id": "hold", "kind": "alternative", "title": "Hold release"},
                ],
                "edges": [
                    {"source": "work", "target": "gate", "kind": "tests"},
                    {"source": "gate", "target": "goal", "kind": "contributes_to"},
                    {"source": "source", "target": "gate", "kind": "informs"},
                    {
                        "source": "gate",
                        "target": "hold",
                        "kind": "may_lead_to",
                        "condition": "Boundary check fails",
                        "outcome": "blocked",
                    },
                ],
                "focus": ["work"],
            },
        }
    )
    head = maps.revise(ws, data)
    return factory, venture, wid, eid, sibling_id, maps, handoffs, data, head


def context(loop, key="ctx"):
    f, venture, wid, _, _, _, h, _, head = loop
    with f() as s:
        version = s.get(WorkItem, wid).version_id
    return h.prepare(
        venture["workspace_id"],
        ContextInput(
            work_id=wid,
            expected_work_version=version,
            expected_head=head["id"],
            request_key=key,
            actor="agent",
        ),
    )


def result_payload(ctx, **changes):
    return ResultInput.model_validate(
        {
            "context_id": ctx["id"],
            "request_key": "result",
            "actor": "agent",
            "summary": "Hold the affected release",
            "rationale": "Boundary test failed",
            "limits": "Production impact unknown",
            "outcome": "hold",
            "revisit_trigger": "Passing independent boundary check",
            "next_action": "Keep the affected release on hold",
            "findings": [
                {
                    "summary": "Failure reproduced in staging",
                    "sources": ["observation:synthetic local reproduction"],
                    "kind": "experiment_result",
                    "confidence": "high",
                }
            ],
            **changes,
        }
    )


def resolution(result, ctx, **changes):
    return ResolveResultInput.model_validate(
        {
            "expected_result_digest": result["digest"],
            "expected_head": ctx["map_revision_id"],
            "expected_work_version": ctx["work"]["version_id"],
            "expected_review_revision": ctx["review_revision"],
            "resolution": "accept",
            "actor": "operator",
            "rationale": "Reviewed sources",
            **changes,
        }
    )


def test_map_history_retry_and_current_scope(loop):
    f, venture, _, _, _, maps, _, data, old = loop
    assert maps.revise(venture["workspace_id"], data)["id"] == old["id"]
    changed = data.model_dump(mode="json")
    changed.update(expected_head=old["id"], request_key="rev2")
    changed["map"]["nodes"][0]["title"] = "A revised goal"
    new = maps.revise(venture["workspace_id"], MapInput.model_validate(changed))
    assert new["id"] != old["id"]
    assert (
        maps.show(venture["workspace_id"], revision=old["id"])["map"]["nodes"][0][
            "title"
        ]
        == "Operate reliable billing"
    )
    with pytest.raises(ConflictError):
        maps.revise(
            venture["workspace_id"],
            data.model_copy(update={"rationale": "Changed retry"}),
        )
    with f.begin() as s:
        s.get(Venture, venture["id"]).objective = "New audience"
    assert maps.show(venture["workspace_id"])["stale_references"]


def test_context_counterevidence_new_arrivals_and_budget(loop):
    f, venture, _, eid, _, _, handoffs, _, _ = loop
    first = context(loop)
    coverage = first["map_coverage"]
    assert coverage["selected_nodes"] == len(first["map"]["nodes"])
    assert coverage["total_nodes"] >= coverage["selected_nodes"]
    assert first["map_revision_id"] in coverage["full_map_command"]
    assert "selected for this work" in first["markdown"]
    assert (
        eid in first["markdown"] and "r18 staging crosses accounts" in first["markdown"]
    )
    assert first["context_complete"]
    with f.begin() as s:
        surprise = Evidence(
            workspace_id=venture["workspace_id"],
            summary="Correction: fixture was wrong",
            kind="document",
            confidence="medium",
        )
        s.add(surprise)
        s.flush()
        sid = surprise.id
    second = context(loop, "new-evidence")
    assert not second["context_complete"]
    assert sid in [r["id"] for r in second["unclassified"]]
    assert handoffs.fetch(second["id"], "evidence", sid)["record"][
        "summary"
    ].startswith("Correction")
    with pytest.raises(ValidationError, match="budget|narrow"):
        handoffs.prepare(
            venture["workspace_id"],
            ContextInput(
                work_id=loop[2],
                expected_work_version=first["work"]["version_id"],
                expected_head=first["map_revision_id"],
                request_key="tiny",
                actor="agent",
                budget_bytes=512,
            ),
        )


def test_accept_atomic_repeat_preserves_unrelated_work_and_scope(loop):
    f, venture, wid, _, sibling, maps, handoffs, _, _ = loop
    ctx = context(loop)
    result = handoffs.submit(venture["workspace_id"], result_payload(ctx))
    before = maps.show(venture["workspace_id"])
    assert before["id"] == ctx["map_revision_id"]
    choice = resolution(result, ctx)
    receipt = handoffs.resolve(result["id"], choice)
    assert handoffs.resolve(result["id"], choice) == receipt
    with f() as s:
        assert s.get(WorkItem, wid).status == WorkItemStatus.DONE
        assert s.get(WorkItem, sibling).status == WorkItemStatus.READY
        assert s.get(Venture, venture["id"]).objective == "Reliable billing"
        assert s.scalar(select(func.count()).select_from(Decision)) == 1
        assert s.scalar(select(func.count()).select_from(Evidence)) == 2


def test_stale_result_retained_without_effects(loop):
    f, venture, wid, _, _, maps, handoffs, data, head = loop
    ctx = context(loop)
    updated = data.model_dump(mode="json")
    updated.update(expected_head=head["id"], request_key="change")
    updated["map"]["nodes"][1]["title"] = "Check r19 instead"
    maps.revise(venture["workspace_id"], MapInput.model_validate(updated))
    result = handoffs.submit(venture["workspace_id"], result_payload(ctx))
    assert result["state"] == "needs_reconciliation"
    with pytest.raises(ConflictError):
        handoffs.resolve(result["id"], resolution(result, ctx))
    with f() as s:
        assert s.get(Artifact, result["id"])
        assert s.scalar(select(func.count()).select_from(Decision)) == 0
        assert s.get(WorkItem, wid).status == WorkItemStatus.READY


def test_changed_condition_blocks_only_dependent_starts(loop):
    f, venture, wid, _, sibling, maps, _, data, head = loop
    updated = data.model_dump(mode="json")
    updated.update(expected_head=head["id"], request_key="changed-condition")
    updated["map"]["edges"][-1]["condition"] = "Test release candidate r19"
    changed = maps.revise(venture["workspace_id"], MapInput.model_validate(updated))
    assert wid in changed["needs_review"]
    app = FoundryApplication(f)
    with pytest.raises(ConflictError, match="review"):
        app.set_work_item_status(wid, WorkItemStatus.IN_PROGRESS)
    app.set_work_item_status(sibling, WorkItemStatus.IN_PROGRESS)


def test_new_unlinked_evidence_after_submission_blocks_acceptance(loop):
    f, venture, _, _, _, _, handoffs, _, _ = loop
    ctx = context(loop)
    result = handoffs.submit(venture["workspace_id"], result_payload(ctx))
    with f.begin() as s:
        s.add(
            Evidence(
                workspace_id=venture["workspace_id"],
                kind="document",
                confidence="high",
                summary="Critical new counterevidence",
            )
        )
    with pytest.raises(ConflictError, match="evidence|coverage"):
        handoffs.resolve(result["id"], resolution(result, ctx))


def test_foreign_reference_and_execution_cycle_are_rejected(loop):
    f, venture, _, _, _, maps, _, data, head = loop
    other = PortfolioService(f).create_idea(
        IdeaDraft(title="Other", description="Private")
    )
    changed = data.model_dump(mode="json")
    changed.update(expected_head=head["id"], request_key="foreign")
    with f.begin() as s:
        e = Evidence(
            workspace_id=other["workspace_id"],
            kind="document",
            confidence="low",
            summary="Private",
        )
        s.add(e)
        s.flush()
        changed["map"]["nodes"][3]["ref"]["id"] = e.id
    with pytest.raises(ReferenceError):
        maps.revise(venture["workspace_id"], MapInput.model_validate(changed))
    changed = data.model_dump(mode="json")
    changed.update(expected_head=head["id"], request_key="cycle")
    changed["map"]["edges"] += [
        {"source": "work", "target": "gate", "kind": "depends_on"},
        {"source": "gate", "target": "work", "kind": "depends_on"},
    ]
    with pytest.raises(ValueError, match="cycle"):
        MapInput.model_validate(changed)


def test_preview_and_failed_accept_leave_no_partial_effects(loop, monkeypatch):
    from startup_foundry.reviews import ReviewService

    f, venture, wid, _, _, maps, handoffs, _, head = loop
    ctx = context(loop)
    result = handoffs.submit(venture["workspace_id"], result_payload(ctx))
    choice = resolution(result, ctx)
    preview = handoffs.preview(result["id"], choice)
    assert preview["preview_only"]
    assert preview["effects"]["completed_work_id"] == wid
    assert maps.show(venture["workspace_id"])["id"] == head["id"]
    with f() as s:
        assert s.scalar(select(func.count()).select_from(Decision)) == 0
        assert s.scalar(select(func.count()).select_from(Evidence)) == 1
        assert s.get(WorkItem, wid).status == WorkItemStatus.READY

    def fail(*args, **kwargs):
        raise RuntimeError("Injected storage fault after evidence and decision")

    monkeypatch.setattr(ReviewService, "_append", fail)
    with pytest.raises(RuntimeError, match="Injected"):
        handoffs.resolve(result["id"], choice)
    with f() as s:
        assert s.scalar(select(func.count()).select_from(Decision)) == 0
        assert s.scalar(select(func.count()).select_from(Evidence)) == 1
        assert s.get(WorkItem, wid).status == WorkItemStatus.READY
    assert maps.show(venture["workspace_id"])["id"] == head["id"]


def test_competing_result_cannot_apply_and_review_clears_attention(loop):
    f, venture, _, eid, _, maps, handoffs, _, _ = loop
    ctx = context(loop)
    one = handoffs.submit(venture["workspace_id"], result_payload(ctx))
    two = handoffs.submit(
        venture["workspace_id"], result_payload(ctx, request_key="competing")
    )
    handoffs.resolve(one["id"], resolution(one, ctx))
    with pytest.raises(ConflictError, match="reconciliation"):
        handoffs.resolve(two["id"], resolution(two, ctx))
    assert handoffs.resume(venture["workspace_id"])["unreviewed_change_count"] == 0
    assert not maps.show(venture["workspace_id"])["map"]["focus"]
    from startup_foundry.domain import DecisionEvidence

    with f() as s:
        assert s.scalar(
            select(DecisionEvidence.id).where(DecisionEvidence.evidence_id == eid)
        )


def test_proposed_reference_changes_are_pinned_and_submission_retry_survives(loop):
    f, venture, _, _, sibling, _, handoffs, _, _ = loop
    ctx = context(loop)
    proposal = result_payload(
        ctx,
        findings=[
            {
                "summary": "Another task may provide relevant information",
                "refs": [{"kind": "work", "id": sibling}],
                "epistemic_status": "inference",
            }
        ],
    )
    result = handoffs.submit(venture["workspace_id"], proposal)
    with f.begin() as s:
        s.get(WorkItem, sibling).description = "Different question"
    repeated = handoffs.submit(venture["workspace_id"], proposal)
    assert repeated["id"] == result["id"]
    assert repeated["state"] == "needs_reconciliation"
    with pytest.raises(ConflictError, match="proposed reference"):
        handoffs.resolve(result["id"], resolution(result, ctx))


def test_later_review_preserves_operating_maturity(loop):
    from startup_foundry.domain import WorkspaceReview
    from startup_foundry.reviews import ReviewInput, ReviewService

    f, venture, _, _, _, _, handoffs, _, _ = loop
    ReviewService(f).append(
        ReviewInput(
            workspace_id=venture["workspace_id"],
            expected_revision=0,
            investigation_stage="solution_validation",
            product_maturity="operating",
            disposition="pursue",
            next_action="Maintain account boundaries",
            reason="Synthetic existing business",
            author="operator",
        )
    )
    ctx = context(loop)
    result = handoffs.submit(venture["workspace_id"], result_payload(ctx))
    handoffs.resolve(result["id"], resolution(result, ctx))
    with f() as s:
        review = s.scalar(
            select(WorkspaceReview).order_by(WorkspaceReview.revision.desc())
        )
        assert review.product_maturity.value == "operating"
        assert review.investigation_stage.value == "solution_validation"


def test_simultaneous_acceptance_has_one_winner(loop):
    from concurrent.futures import ThreadPoolExecutor
    from threading import Barrier

    f, venture, _, _, _, _, handoffs, _, _ = loop
    ctx = context(loop)
    results = [
        handoffs.submit(venture["workspace_id"], result_payload(ctx, request_key=k))
        for k in ["race-a", "race-b"]
    ]
    barrier = Barrier(2)

    def apply(result):
        barrier.wait(timeout=10)
        try:
            handoffs.resolve(result["id"], resolution(result, ctx))
            return "accepted"
        except ConflictError:
            return "conflict"

    with ThreadPoolExecutor(max_workers=2) as pool:
        assert sorted(pool.map(apply, results)) == ["accepted", "conflict"]
    with f() as s:
        assert s.scalar(select(func.count()).select_from(Decision)) == 1
        assert s.scalar(select(func.count()).select_from(Evidence)) == 2


def test_deferral_is_visible_after_restart_and_remains_reviewable(loop):
    f, venture, _, _, _, maps, handoffs, _, head = loop
    ctx = context(loop)
    result = handoffs.submit(venture["workspace_id"], result_payload(ctx))
    handoffs.resolve(
        result["id"],
        resolution(result, ctx, resolution="defer", rationale="Review next session"),
    )
    restarted = AgentHandoffService(f)
    assert restarted.show_result(result["id"])["state"] == "deferred"
    assert (
        restarted.show_result(result["id"])["deferral"]["rationale"]
        == "Review next session"
    )
    assert maps.show(venture["workspace_id"])["id"] == head["id"]
    restarted.resolve(result["id"], resolution(result, ctx))
    assert restarted.show_result(result["id"])["state"] == "accept"


@pytest.mark.parametrize("replacement_resolution", [None, "reject", "defer", "accept"])
def test_superseded_history_requires_accepted_replacement(
    loop, replacement_resolution, tmp_path
):
    factory, venture, *_ = loop
    service = loop[6]
    ws = venture["workspace_id"]
    ctx = context(loop)
    old = service.submit(ws, result_payload(ctx, request_key="original"))
    middle = service.submit(
        ws,
        result_payload(
            ctx,
            request_key="middle",
            supersedes_result_id=old["id"],
            reconciliation_rationale="Correct the original finding",
        ),
    )
    replacement = service.submit(
        ws,
        result_payload(
            ctx,
            request_key="replacement",
            supersedes_result_id=middle["id"],
            reconciliation_rationale="Finish reconciling the finding",
        ),
    )
    if replacement_resolution:
        service.resolve(
            replacement["id"],
            resolution(replacement, ctx, resolution=replacement_resolution),
        )
    resumed = AgentHandoffService(factory).resume(ws)
    original = service.show_result(old["id"])
    assert original["digest"] == old["digest"]
    assert original["proposal"] == old["proposal"]
    assert original["receipt"] is None
    if replacement_resolution == "accept":
        assert original["state"] == "superseded"
        assert original["superseded_by"] == replacement["id"]
        assert service.show_result(middle["id"])["superseded_by"] == replacement["id"]
        assert original["stale_reasons"]  # Retain why the historical context changed.
        assert f"Result {old['id']}: needs_reconciliation" not in resumed["markdown"]
        assert replacement["id"] in resumed["markdown"]
        # Pagination must not determine whether an accepted successor exists.
        assert service.list_results(ws, limit=1)[0]["state"] == "accept"
        assert service.show_result(replacement["id"])["state"] == "accept"
        pending = [
            r["id"]
            for item in portfolio_attention(factory)["items"]
            for r in item["results"]
        ]
        assert old["id"] not in pending and middle["id"] not in pending
        with TestClient(
            create_app(factory, tmp_path), base_url="http://127.0.0.1"
        ) as client:
            page = client.get("/decision-results/" + old["id"])
            assert page.status_code == 200
            assert "Historical result superseded by" in page.text
            assert f"/decision-results/{replacement['id']}" in page.text
            assert "Reconciliation required" not in page.text
            assert 'data-lifecycle="resolve"' not in page.text
    else:
        assert original["state"] != "superseded"
        assert original["superseded_by"] is None
