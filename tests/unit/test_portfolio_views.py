"""SQL query contract: combined filters, stable pages and unknown scores."""

import pytest

from startup_foundry.domain import WorkItem, WorkItemKind, WorkItemStatus
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.reviews import ReviewInput, ReviewService
from startup_foundry.scoring import FACTORS, AssessmentInput, ScoringService
from startup_foundry.views import PortfolioQuery, PortfolioViewService


@pytest.fixture
def view(tmp_path):
    url = f"sqlite:///{tmp_path / 'views.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    p = PortfolioService(factory)
    scores = ScoringService(factory)
    reviews = ReviewService(factory)
    for identity, value, disposition, maturity, blocked in [
        ("a", 8, "dropped", "concept", False),
        ("b", 2, "pursue", "concept", False),
        ("c", 5, "hold", "concept", True),
        ("d", 5, "hold", "prototype", True),
        ("e", 5, "pursue", "concept", False),
        ("f", None, "pursue", "unknown", False),
    ]:
        idea = p.create_idea(
            IdeaDraft(title="Same title", description="Literal %_ match"),
            idea_id=identity,
        )
        if value is not None:
            scores.assess(
                AssessmentInput(
                    idea_id=identity,
                    scores={k: value for k, _, _, _ in FACTORS},
                    rationale="Fixture",
                    author="test",
                )
            )
        work_id = None
        if blocked:
            work_id = "work-" + identity
            with factory.begin() as s:
                s.add(
                    WorkItem(
                        id=work_id,
                        workspace_id=idea["workspace_id"],
                        title="Need review",
                        kind=WorkItemKind.INVESTIGATION,
                        status=WorkItemStatus.BLOCKED,
                        blocked_reason="human_input",
                        owner="human",
                    )
                )
        reviews.append(
            ReviewInput(
                workspace_id=idea["workspace_id"],
                expected_revision=0,
                investigation_stage="business_validation"
                if maturity == "prototype"
                else "comparison",
                product_maturity=maturity,
                disposition=disposition,
                reason="Fixture state",
                author="test",
                next_action="Review fixture",
                next_work_item_id=work_id,
            )
        )
    yield PortfolioViewService(factory), p, scores, reviews, factory
    engine.dispose()


def test_stable_numeric_null_last_and_combined_filters(view):
    v, *_ = view
    for direction, first in [("desc", "a"), ("asc", "b")]:
        items = v.list(
            "idea", PortfolioQuery(score_view="reviewed", direction=direction)
        )["items"]
        assert items[0]["id"] == first and items[-1]["id"] == "f"
        tied = [i["id"] for i in items if i["id"] in ["c", "d", "e"]]
        assert tied == ["c", "d", "e"]
        pages = [
            i["id"]
            for offset in range(0, 6, 2)
            for i in v.list(
                "idea",
                PortfolioQuery(
                    score_view="reviewed", direction=direction, limit=2, offset=offset
                ),
            )["items"]
        ]
        assert pages == [i["id"] for i in items]
    selected = v.list(
        "idea",
        PortfolioQuery(
            score_view="reviewed",
            disposition="hold",
            product_maturity="prototype",
            blocker="human_input",
        ),
    )
    assert selected["total"] == 1 and selected["items"][0]["id"] == "d"
    assert v.list("idea", PortfolioQuery(q="%_"))["total"] == 6
    assert v.list("idea", PortfolioQuery(q="absent"))["total"] == 0
    assert (
        v.list("idea", PortfolioQuery(score_view="original"))["unscored"] == 6
    )  # no mixing reviewed into original


def test_linked_ventures_are_not_arbitrarily_collapsed(view):
    v, p, _, _, _ = view
    p.promote_idea("a", venture_id="one")
    p.promote_idea("a", venture_id="two")
    idea = v.list("idea", PortfolioQuery(q="a"))["items"][0]
    assert {r["id"] for r in idea["ventures"]} == {"one", "two"}
    assert v.list("venture", PortfolioQuery(score_view="reviewed"))["total"] == 2


@pytest.mark.parametrize(
    "input",
    [
        {"offset": -1},
        {"limit": 0},
        {"limit": 501},
        {"criterion": "invalid"},
        {"criterion": "founder_fit", "min_score": 11},
        {"min_score": float("nan")},
        {"sort": "sql injection"},
        {"blocker": "invalid"},
    ],
)
def test_query_bounds_are_explicit(input):
    with pytest.raises(ValueError):
        PortfolioQuery(**input)
