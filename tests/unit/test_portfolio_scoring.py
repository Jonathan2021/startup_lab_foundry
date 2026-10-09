"""Workbook parity, immutable imports and explicit assessment gaps."""

import csv
from decimal import Decimal
from pathlib import Path

import pytest
from sqlalchemy import func, select

from startup_foundry.domain import Artifact, CriterionScore, IdeaAssessment
from startup_foundry.errors import ConflictError, ValidationError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.scoring import FACTORS, AssessmentInput, ScoringService, calculate

SOURCES = Path(__file__).resolve().parents[2] / "docs/sources"


@pytest.fixture
def scoring(tmp_path):
    url = f"sqlite:///{tmp_path / 'scores.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    yield ScoringService(factory), PortfolioService(factory), factory
    engine.dispose()


def rows():
    with (SOURCES / "startup_ideas.csv").open(encoding="utf-8-sig", newline="") as f:
        return list(csv.DictReader(f))


def test_all_workbook_rows_reproduce_exact_totals_and_grades():
    anchors = {"P023": 49, "P046": 47, "P103": 45, "G002": 79}
    for row in rows():
        values = {key: Decimal(row[header]) for key, header, _, _ in FACTORS}
        assert calculate(values) == int(row["Priority score"])
        if row["Idea ID"] in anchors:
            assert calculate(values) == anchors[row["Idea ID"]]
    perfect = {
        key: 10 if direction == "positive" else 1 for key, _, direction, _ in FACTORS
    }
    assert calculate(perfect) == 100
    assert (
        calculate(
            {
                key: 1 if direction == "positive" else 10
                for key, _, direction, _ in FACTORS
            }
        )
        == 0
    )
    assert calculate({key: None for key, _, _, _ in FACTORS}) is None
    half = {key: 1 for key, _, _, _ in FACTORS}
    half["retention"] = 2
    assert calculate(half) == 11  # 10.5, Excel half away from zero


@pytest.mark.parametrize("value", [0, 11, -1, "", "NaN", "Infinity", True])
def test_invalid_values_are_not_silently_imputed(value):
    with pytest.raises(ValidationError):
        calculate({key: value for key, _, _, _ in FACTORS})


def test_atomic_import_repeat_relocation_and_review_history(scoring, tmp_path):
    service, portfolio, factory = scoring
    for row in rows():
        portfolio.create_idea(
            IdeaDraft(title=row["Title"], description=row["Cleaned description"]),
            idea_id=row["Idea ID"],
        )
    portfolio.create_idea(
        IdeaDraft(title="New", description="Unscored"), idea_id="N001"
    )
    result = service.import_original(SOURCES)
    assert result["imported"] == 238
    assert service.import_original(SOURCES)["imported"] == 0
    moved = tmp_path / "moved"
    moved.mkdir()
    (moved / "startup_ideas.csv").write_bytes(
        (SOURCES / "startup_ideas.csv").read_bytes()
    )
    assert service.import_original(moved)["imported"] == 0
    with factory() as s:
        assert s.scalar(select(func.count()).select_from(IdeaAssessment)) == 238
        assert s.scalar(select(func.count()).select_from(CriterionScore)) == 2856
        assert (
            s.scalar(
                select(func.count())
                .select_from(Artifact)
                .where(Artifact.name == "Original workbook scoring provenance")
            )
            == 238
        )
    assert service.show("N001")["history"] == []
    before = service.show("P023")["history"][0]
    assert before["total"] == 49 and before["source"]["monthly_revenue_high"]
    reviewed = service.assess(
        AssessmentInput(
            idea_id="P023",
            scores={"founder_fit": 9},
            rationale="Only first-party interest reviewed; other factors unknown.",
            author="reviewer",
        )
    )
    assert reviewed["total"] is None and reviewed["coverage"] == 1
    history = service.show("P023")["history"]
    assert len(history) == 2 and history[-1]["total"] == 49
    assert service.import_original(SOURCES)["imported"] == 0
    text = (moved / "startup_ideas.csv").read_text()
    (moved / "startup_ideas.csv").write_text(
        text.replace("Strong technical founder fit", "Changed judgment", 1)
    )
    with pytest.raises(ConflictError):
        service.import_original(moved)
    assert len(service.show("P023")["history"]) == 2


def test_scorecard_versions_sensitivity_ranking_and_partial_exclusion(scoring):
    from startup_foundry.scoring import ScorecardInput, default_criteria

    service, portfolio, factory = scoring
    for identity in ["a", "b"]:
        portfolio.create_idea(
            IdeaDraft(title=identity, description="Versioned judgment"),
            idea_id=identity,
        )
    card = ScorecardInput(
        id="profile-v2",
        name="Alternative weights",
        version=2,
        rationale="Explicit sensitivity profile",
        criteria=default_criteria(),
    )
    service.import_scorecard(card)
    assert service.import_scorecard(card)["id"] == "profile-v2"
    with pytest.raises(ConflictError):
        service.import_scorecard(
            card.model_copy(update={"rationale": "Rewrite existing method"})
        )
    with pytest.raises(ValidationError):
        service.import_scorecard(
            card.model_copy(
                update={
                    "id": "duplicate-keys",
                    "criteria": card.criteria + [card.criteria[0]],
                }
            )
        )
    values = {k: 1 if d == "positive" else 10 for k, _, d, _ in FACTORS}
    full = service.assess(
        AssessmentInput(
            idea_id="a",
            scorecard_id="profile-v2",
            scores=values,
            rationale="Zero total is a score",
            author="test",
        )
    )
    assert full["total"] == 0
    service.assess(
        AssessmentInput(
            idea_id="b",
            scorecard_id="profile-v2",
            scores={"founder_fit": 9},
            rationale="Unknown factors",
            author="test",
        )
    )
    rank = service.rank("profile-v2", "test comparison")
    assert rank["ranked"] == 1 and rank["excluded"] == 1
    changes = service.sensitivity("a", "profile-v2")
    assert changes["assessment_id"] == full["id"] and changes["base"] == 0
    assert changes["changes"]
    service.assess(
        AssessmentInput(
            idea_id="a",
            scorecard_id="profile-v2",
            scores={},
            rationale="Withdraw unsupported factors explicitly",
            author="test",
        )
    )
    assert service.rank("profile-v2", "updated comparison")["ranked"] == 0


def test_duplicate_csv_ids_and_invalid_parity_fail_before_writes(scoring, tmp_path):
    service, portfolio, factory = scoring
    data = rows()
    data.append(data[0])
    path = tmp_path / "startup_ideas.csv"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
    with pytest.raises(ValidationError):
        service.import_original(tmp_path)
    data = data[:1]
    data[0]["Priority score"] = "-1"
    with path.open("w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=list(data[0]))
        writer.writeheader()
        writer.writerows(data)
    with pytest.raises(ValidationError):
        service.import_original(tmp_path)
    assert service.list_scorecards()["items"] == []
