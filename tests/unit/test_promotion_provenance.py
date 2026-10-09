"""A promoted venture shows and may cite its source idea's provenance (ADR-0020)."""

from __future__ import annotations

import pytest
from fastapi.testclient import TestClient

from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.decision_contracts import ContextInput, MapInput
from startup_foundry.decision_maps import DecisionMapService
from startup_foundry.discovery_records import (
    ActorLinkInput,
    DiscoveryService,
    MarketActorInput,
    SourceInput,
)
from startup_foundry.domain import Evidence, WorkItem
from startup_foundry.errors import ReferenceError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.web import create_app


@pytest.fixture
def promoted(tmp_path):
    url = f"sqlite:///{tmp_path / 'lineage.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    portfolio = PortfolioService(factory)
    discovery = DiscoveryService(factory)
    for identity in ["AS01", "OTHER"]:
        portfolio.create_idea(
            IdeaDraft(title="Idea " + identity, description="Problem " + identity),
            idea_id=identity,
        )
    discovery.register_source(
        SourceInput(
            kind="document",
            title="Agentic transcript",
            locator="https://example.com/transcript",
            idea_ids=["AS01"],
            role="market_reference",
            link_note="Segment 3",
        )
    )
    discovery.link_actor(
        "AS01",
        ActorLinkInput(
            actor=MarketActorInput(name="Rival", website="https://rival.example"),
            relation="competitor",
            note="Hosted evals; no local replay",
            checked_on="2026-10-09",
        ),
    )
    idea_ws = portfolio.show_idea("AS01")["workspace_id"]
    other_ws = portfolio.show_idea("OTHER")["workspace_id"]
    with factory.begin() as session:
        own = Evidence(
            workspace_id=idea_ws,
            summary="Idea-stage desk research",
            kind="document",
            confidence="low",
        )
        foreign = Evidence(
            workspace_id=other_ws,
            summary="Unrelated idea evidence",
            kind="document",
            confidence="low",
        )
        session.add_all([own, foreign])
        session.flush()
        own_id, foreign_id = own.id, foreign.id
    venture = portfolio.promote_idea("AS01")
    yield factory, venture, own_id, foreign_id, tmp_path
    engine.dispose()


def map_input(work_id: str, evidence_id: str, key: str) -> MapInput:
    return MapInput.model_validate(
        {
            "expected_head": None,
            "request_key": key,
            "actor": "agent",
            "rationale": "Carry discovery evidence into the venture",
            "map": {
                "nodes": [
                    {"id": "goal", "kind": "goal", "title": "Validate wedge"},
                    {
                        "id": "work",
                        "kind": "record",
                        "title": "Initial review",
                        "ref": {"kind": "work", "id": work_id},
                    },
                    {
                        "id": "research",
                        "kind": "record",
                        "title": "Discovery research",
                        "ref": {"kind": "evidence", "id": evidence_id},
                    },
                ],
                "edges": [
                    {"source": "work", "target": "goal", "kind": "contributes_to"},
                    {"source": "research", "target": "goal", "kind": "informs"},
                ],
                "focus": ["work"],
            },
        }
    )


def test_map_cites_source_idea_evidence_but_rejects_foreign_workspace(promoted):
    factory, venture, own_id, foreign_id, _ = promoted
    ws = venture["workspace_id"]
    with factory() as session:
        work = session.query(WorkItem).filter_by(workspace_id=ws).one()
        work_id, version = work.id, work.version_id
    maps = DecisionMapService(factory)
    with pytest.raises(ReferenceError, match="another workspace"):
        maps.revise(ws, map_input(work_id, foreign_id, "foreign"))
    head = maps.revise(ws, map_input(work_id, own_id, "lineage"))
    assert head["stale_references"] == []
    context = AgentHandoffService(factory).prepare(
        ws,
        ContextInput(
            work_id=work_id,
            expected_work_version=version,
            expected_head=head["id"],
            request_key="ctx",
            actor="agent",
        ),
    )
    assert "evidence:" + own_id in context["records"]
    assert "Idea-stage desk research" in context["markdown"]


def test_venture_overview_shows_source_idea_provenance(promoted):
    factory, venture, own_id, _, tmp_path = promoted
    client = TestClient(
        create_app(factory, tmp_path / "requests"), base_url="http://127.0.0.1"
    )
    page = client.get("/ventures/" + venture["id"]).text
    assert "From the source idea" in page
    assert "Agentic transcript" in page and "Segment 3" in page
    assert "Market reference" in page
    assert "Rival" in page and "Hosted evals; no local replay" in page
    assert "Idea evidence · 1" in page and own_id in page
    assert 'href="/ideas/AS01' in page
