"""Fresh idea/promotion/manual intake is persistent and never an unattended run."""

import re

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from startup_foundry.domain import WorkItem
from startup_foundry.errors import ConflictError
from startup_foundry.human_inputs import ClaimInput, HumanInputService
from startup_foundry.manual_intake import IntakeCompletion, ManualIntakeService
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.scoring import AssessmentInput, ScoringService
from startup_foundry.venture_scoring import VentureScoringService
from startup_foundry.web import create_app


def test_fresh_ui_promote_handoff_complete_and_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'intake.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    with TestClient(create_app(f, tmp_path), base_url="http://127.0.0.1") as c:
        token = re.search(r'name="foundry-token" content="([^"]+)"', c.get("/").text)[1]
        headers = {"X-Foundry-Token": token}
        idea = c.post(
            "/api/ideas",
            json={"title": "Fresh idea", "description": "Known hypothesis"},
            headers=headers,
        ).json()
        idea_path = "/ideas/" + idea["id"]
        assert "Request initial review" in c.get(idea_path).text
        initial = c.post(
            "/api/ideas/" + idea["id"] + "/intake",
            headers=headers,
            json={"expected_revision_id": idea["revision_id"], "actor": "operator"},
        ).json()
        assert initial["status"] == "ready"
        assert "Queued for manual agent review" in c.get(idea_path).text
        venture = c.post(
            "/api/ideas/" + idea["id"] + "/promote", headers=headers, json={}
        ).json()
        assert (
            c.post(
                "/api/ideas/" + idea["id"] + "/promote", headers=headers, json={}
            ).json()["id"]
            == venture["id"]
        )
        path = "/ventures/" + venture["id"]
        row = c.get("/api/ventures").json()["items"][0]
        assert row["work_state"] == "ready" and row["next_owner"] == "agent"
        assert "Not yet scored" in c.get(path).text
        handoff = c.get(path + "/intake-handoff").json()
        assert handoff["idea_revision_id"] == idea["revision_id"]
        assert handoff["venture_id"] == venture["id"] and not handoff["worker_running"]
        claim = c.post(
            "/api/ventures/" + venture["id"] + "/intake/claim",
            headers=headers,
            json={
                "expected_version": handoff["work"]["version"],
                "actor": "agent:reviewer",
            },
        ).json()
        result = c.post(
            "/api/ventures/" + venture["id"] + "/intake/complete",
            headers=headers,
            json={
                "work_id": handoff["work"]["id"],
                "expected_version": claim["version"],
                "actor": "agent:reviewer",
                "request_key": "completion",
                "research_summary": "Attributed fixture observation",
                "research_source": "local fixture",
                "research_limits": "Synthetic; demand and access remain untested",
                "scores": {"problem": 7},
                "score_rationale": "Only problem supported",
                "unknown_reason": "Remaining factors need access and payer research",
                "expected_sequence": 0,
                "expected_review_revision": 0,
                "next_action": "Compare one actual workaround",
                "next_work_title": "Bounded comparison",
                "next_owner": "agent",
            },
        )
        assert result.status_code == 200, result.text
        assert result.json()["assessment"]["total"] is None
    with TestClient(create_app(f, tmp_path), base_url="http://127.0.0.1") as c:
        html = c.get(path).text
        assert "1/12 factors" in html and "Bounded comparison" in html
        assert "Only problem supported" in c.get(path + "?tab=scores").text
        assert not VentureScoringService(f).show(venture["id"])["current"][
            "reassessment_suggested"
        ]


def test_scored_source_atomic_targeted_copy_and_distinct_ventures(tmp_path):
    url = f"sqlite:///{tmp_path / 'scores.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    idea = p.create_idea(IdeaDraft(title="Scored", description="Fixture"))
    source = ScoringService(f).assess(
        AssessmentInput(
            idea_id=idea["id"],
            scores={"problem": 6},
            rationale="Source",
            author="operator",
        )
    )
    first = p.promote_idea(idea["id"], venture_id="v-first")
    p.promote_idea(idea["id"], venture_id="v-first")
    p.promote_idea(idea["id"], venture_id="v-second")
    assert p.promote_idea(idea["id"])["id"] == first["id"]
    for v in ["v-first", "v-second"]:
        baseline = VentureScoringService(f).show(v)["current"]
        assert (
            baseline["kind"] == "source_baseline"
            and baseline["source_assessment_id"] == source["id"]
        )
    with f() as db:
        assert db.scalar(select(func.count()).select_from(WorkItem)) == 2


def test_human_next_input_repeat_and_completion_rollback(tmp_path):
    url = f"sqlite:///{tmp_path / 'human.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    idea = p.create_idea(IdeaDraft(title="Unknown access", description="Fixture"))
    venture = p.promote_idea(idea["id"], venture_id="v-human")
    service = ManualIntakeService(f)
    handoff = service.handoff("venture", venture["id"])
    claim = service.claim(
        "venture",
        venture["id"],
        ClaimInput(expected_version=handoff["work"]["version"], actor="reviewer"),
    )
    completion = IntakeCompletion(
        work_id=claim["id"],
        expected_version=claim["version"],
        actor="reviewer",
        request_key="once",
        research_summary="Fixture",
        research_source="Local",
        research_limits="No field observation",
        scores={"problem": 6},
        score_rationale="One factor",
        unknown_reason="Access and other factors unknown",
        expected_sequence=0,
        expected_review_revision=99,
        next_action="Clarify access",
        next_work_title="Access input",
        next_owner="you",
        question_id="R090",
        question="Can you access the queue?",
    )
    with pytest.raises(ConflictError):
        service.complete("venture", venture["id"], completion)
    assert HumanInputService(f, tmp_path).list()["total"] == 0
    assert VentureScoringService(f).show(venture["id"])["current"] is None
    completion = completion.model_copy(update={"expected_review_revision": 0})
    result = service.complete("venture", venture["id"], completion)
    assert service.complete("venture", venture["id"], completion) == result
    assert HumanInputService(f, tmp_path).show("R090")["status"] == "waiting_for_answer"
    with f() as db:
        assert db.get(WorkItem, result["next_work_id"]).status.value == "blocked"
