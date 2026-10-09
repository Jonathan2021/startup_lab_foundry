"""Console views for sources, competition, revisions, relations and cohorts."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from startup_foundry.discovery_records import (
    ActorLinkInput,
    DiscoveryService,
    IdeaRelationInput,
    IdeaRevisionInput,
    MarketActorInput,
    SourceInput,
)
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.scoring import FACTORS, AssessmentInput, ScoringService
from startup_foundry.web import create_app

HOSTILE = "<script>alert(1)</script>"


@pytest.fixture
def console(tmp_path):
    url = f"sqlite:///{tmp_path / 'console.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    portfolio = PortfolioService(factory)
    discovery = DiscoveryService(factory)
    for identity in ["A", "B", "C"]:
        portfolio.create_idea(
            IdeaDraft(title="Idea " + identity, description="Problem " + identity),
            idea_id=identity,
        )
    ScoringService(factory).assess(
        AssessmentInput(
            idea_id="A",
            scores={key: 7 for key, _, _, _ in FACTORS},
            rationale="Cohort review",
            criterion_rationales={"moat": "Rationale " + HOSTILE},
            author="t",
        )
    )
    source = discovery.register_source(
        SourceInput(
            kind="document",
            title="Transcript",
            locator="https://ex.com/transcript",
            idea_ids=["A", "B"],
            link_note="Segment " + HOSTILE,
        )
    )
    discovery.link_actor(
        "A",
        ActorLinkInput(
            actor=MarketActorInput(name="Rival", website="https://rival.example"),
            relation="competitor",
            is_primary=True,
            note="Gap " + HOSTILE,
            checked_on="2026-10-09",
        ),
    )
    discovery.relate(
        IdeaRelationInput(
            source_idea_id="B",
            target_idea_id="A",
            kind="combined_with",
            rationale="Shared buyer",
        )
    )
    discovery.revise(
        "A",
        IdeaRevisionInput(
            title="Idea A narrowed", change_reason="Narrow scope", authored_by="agent"
        ),
    )
    with TestClient(
        create_app(factory, tmp_path / "requests"), base_url="http://127.0.0.1"
    ) as client:
        yield client, source
    engine.dispose()


def test_compare_page_and_json(console):
    client, _ = console
    page = client.get("/ideas/compare?ids=A&ids=B&ids=C")
    assert page.status_code == 200
    text = page.text
    assert "Idea A narrowed" in text and "Idea B" in text and "Idea C" in text
    assert "Scored earlier revision 1" in text
    assert "Not assessed on this scorecard" in text and "Unknown" in text
    assert "Primary: Rival" in text and "Combined with" in text
    assert HOSTILE not in text and "&lt;script&gt;" in text
    data = client.get("/api/ideas/compare?ids=A,B").json()
    assert [i["id"] for i in data["items"]] == ["A", "B"]
    assert data["items"][0]["stale_revision"] is True
    assert data["items"][1]["total"] is None
    assert client.get("/api/ideas/compare").status_code == 400
    assert client.get("/api/ideas/compare?ids=A&ids=missing").status_code == 404
    assert client.get("/ideas/compare?ids=A&scorecard_id=nope").status_code == 404


def test_source_cohort_list_and_source_links(console):
    client, source = console
    page = client.get("/ideas?source_id=" + source["id"])
    assert page.status_code == 200
    assert "Idea B" in page.text and "Idea C" not in page.text
    assert "Compare these 2 ideas" in page.text
    assert 'name="source_id" value="' + source["id"] in page.text
    assert client.get("/ideas?source_id=missing").status_code == 404
    api = client.get("/api/ideas?source_id=" + source["id"]).json()
    assert api["total"] == 2
    sources = client.get("/sources").text
    assert "/ideas?source_id=" + source["id"] in sources
    assert "2 linked ideas" in sources


def test_idea_page_shows_competition_revisions_and_relations(console):
    client, _ = console
    text = client.get("/ideas/A").text
    assert 'id="competition"' in text and "Rival" in text
    assert 'href="https://rival.example"' in text and "Primary" in text
    assert "2026-10-09" in text
    assert "Revisions (2)" in text and "Narrow scope" in text
    assert "Current" in text and "Scored" in text
    assert 'id="related"' in text and "Idea B" in text and "Shared buyer" in text
    assert "/ideas/compare?ids=A&amp;ids=B" in text
    assert "Inspiration" in text and "revision 1 (earlier)" in text
    assert HOSTILE not in text
    assert client.get("/ideas/B").status_code == 200
