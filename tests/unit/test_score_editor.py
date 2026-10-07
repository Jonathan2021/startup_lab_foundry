"""Display scorecards and edit sequence are separate, including custom factors."""

import re

from fastapi.testclient import TestClient

from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.scoring import AssessmentInput, ScorecardInput, ScoringService
from startup_foundry.venture_scoring import VentureScoringService
from startup_foundry.web import create_app


def form(html):
    text = re.search(r'<form data-api="/api/venture-scores".*?</form>', html, re.S)[0]
    return dict(re.findall(r'<input[^>]*name="([^"]+)"[^>]*value="([^"]*)"', text))


def test_original_display_edits_actual_reviewed_sequence_and_stale_conflicts(tmp_path):
    url = f"sqlite:///{tmp_path / 'editor.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    idea = p.create_idea(IdeaDraft(title="Scored", description="Fixture"))
    ScoringService(f).assess(
        AssessmentInput(
            idea_id=idea["id"],
            scores={"problem": 5},
            rationale="Source",
            author="operator",
        )
    )
    p.promote_idea(idea["id"], venture_id="v")
    with TestClient(create_app(f, tmp_path), base_url="http://127.0.0.1") as c:
        html = c.get("/ventures/v?tab=scores&score_view=original").text
        fields = form(html)
        assert fields["scorecard_id"] == "portfolio-reviewed-v1"
        assert fields["expected_sequence"] == "1"
        token = re.search(r'name="foundry-token" content="([^"]+)"', html)[1]
        payload = {
            **fields,
            "expected_sequence": 1,
            "scores": {"problem": 7},
            "rationale": "Native",
            "author": "operator",
        }
        assert (
            c.post(
                "/api/venture-scores", headers={"X-Foundry-Token": token}, json=payload
            ).status_code
            == 200
        )
        payload["request_key"] = "stale-tab"
        assert (
            c.post(
                "/api/venture-scores", headers={"X-Foundry-Token": token}, json=payload
            ).status_code
            == 409
        )
        assert (
            form(c.get("/ventures/v?tab=scores&score_view=original").text)[
                "expected_sequence"
            ]
            == "2"
        )
        assert "Higher = more risk" in html and "weight" in html


def test_custom_card_factors_and_honest_unknown_label(tmp_path):
    url = f"sqlite:///{tmp_path / 'custom.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    idea = p.create_idea(IdeaDraft(title="Fresh", description="Fixture"))
    p.promote_idea(idea["id"], venture_id="v")
    ScoringService(f).import_scorecard(
        ScorecardInput(
            id="access-v1",
            name="Access",
            version=1,
            rationale="Different criterion",
            criteria=[
                {
                    "key": "local_access",
                    "name": "Local access",
                    "direction": "positive",
                    "weight": "1",
                }
            ],
        )
    )
    with TestClient(create_app(f, tmp_path), base_url="http://127.0.0.1") as c:
        html = c.get("/ventures/v?tab=scores&score_view=access-v1").text
        assert (
            'name="score:local_access"' in html and 'name="score:problem"' not in html
        )
        assert form(html)["scorecard_id"] == "access-v1"
        assert (
            c.get(
                "/api/ventures?score_view=access-v1&criterion=local_access"
            ).status_code
            == 200
        )
        assert (
            c.get("/api/ventures?score_view=access-v1&criterion=problem").status_code
            == 400
        )
        rows = c.get("/api/ventures").json()["items"]
        assert rows[0]["score_label"] == "Not yet scored"
    assert VentureScoringService(f).show("v")["current"] is None
