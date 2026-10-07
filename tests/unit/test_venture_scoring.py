"""Independent judgments and frozen baselines; unknown never becomes zero."""

import pytest

from startup_foundry.errors import ConflictError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.scoring import FACTORS, AssessmentInput, ScoringService
from startup_foundry.venture_scoring import (
    VentureAssessmentInput,
    VentureScoringService,
)
from startup_foundry.views import PortfolioQuery, PortfolioViewService


def test_independence_frozen_baseline_partial_idempotence_and_sort(tmp_path):
    url = f"sqlite:///{tmp_path / 'scores.db'}"
    upgrade_database(url)
    f = create_session_factory(create_db_engine(url))
    p = PortfolioService(f)
    ideas = ScoringService(f)
    s = VentureScoringService(f)
    p.create_idea(IdeaDraft(title="Sports", description="Fixture"), idea_id="P103")
    scores = {k: 5 for k, *_ in FACTORS}
    original = ideas.assess(
        AssessmentInput(
            idea_id="P103", scores=scores, rationale="Fixture", author="test"
        )
    )
    for v in ["one", "two"]:
        p.promote_idea("P103", venture_id=v)
    # Promotion now copies these two pinned baselines atomically.
    assert all(
        s.show(v)["current"]["source_assessment_id"] == original["id"]
        for v in ["one", "two"]
    )
    assert s.bootstrap()["imported"] == 0

    def payload(v, key, n=1, values=scores):
        return VentureAssessmentInput(
            venture_id=v,
            expected_sequence=n,
            request_key=key,
            scores=values,
            rationale="Fixture",
            author="test",
        )

    a = s.assess(payload("one", "one"))
    assert s.assess(payload("one", "one"))["id"] == a["id"]
    with pytest.raises(ConflictError):
        s.assess(payload("one", "one", values={"problem": 1}))
    with pytest.raises(ConflictError):
        s.assess(payload("one", "stale"))
    partial = s.assess(payload("one", "partial", 2, {"problem": 3}))
    assert partial["total"] is None and s.show("one")["current"]["id"] == partial["id"]
    ideas.assess(
        AssessmentInput(
            idea_id="P103",
            scores={k: 9 for k in scores},
            rationale="New idea score",
            author="test",
        )
    )
    assert s.bootstrap()["imported"] == 0
    assert s.show("two")["current"]["source_assessment_id"] == original["id"]
    for direction in ["asc", "desc"]:
        rows = PortfolioViewService(f).list(
            "venture", PortfolioQuery(direction=direction)
        )["items"]
        assert rows[-1]["id"] == "one" and rows[0]["score_label"].startswith(
            "Starting estimate"
        )
    assert ideas.show("P103")["history"][0]["total"] != a["total"]
