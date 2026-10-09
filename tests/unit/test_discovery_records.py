"""Discovery records: sources, competition, revisions, relations and cohorts."""

from __future__ import annotations

import csv
import hashlib
from pathlib import Path
from typing import TypeVar

import pytest
from pydantic import BaseModel
from pydantic import ValidationError as ContractError
from sqlalchemy import func, select

from startup_foundry.discovery_records import (
    ActorLinkInput,
    DiscoveryService,
    IdeaCreateInput,
    IdeaRelationInput,
    IdeaRevisionInput,
    MarketActorInput,
    SourceInput,
)
from startup_foundry.domain import (
    AuditEvent,
    IdeaRevision,
    IdeaSourceRole,
    ReferenceSource,
    Workspace,
)
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.scoring import FACTORS, AssessmentInput, ScoringService
from startup_foundry.views import PortfolioQuery, PortfolioViewService

ModelT = TypeVar("ModelT", bound=BaseModel)
SOURCES = Path(__file__).resolve().parents[2] / "docs/sources"


@pytest.fixture
def records(tmp_path):
    url = f"sqlite:///{tmp_path / 'discovery.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    yield DiscoveryService(factory), PortfolioService(factory), factory
    engine.dispose()


def idea(portfolio: PortfolioService, identity: str, title: str = "") -> None:
    portfolio.create_idea(
        IdeaDraft(
            title=title or "Idea " + identity,
            description="Testable problem " + identity,
            customer="Operators",
        ),
        idea_id=identity,
    )


def variant(model: ModelT, changes: dict[str, object]) -> ModelT:
    """A validated copy; model_copy(update=...) would skip validation."""
    return type(model).model_validate({**model.model_dump(), **changes})


def full_scores(value: int) -> dict[str, int]:
    return {key: value for key, _, _, _ in FACTORS}


def test_local_file_source_is_content_addressed_and_idempotent(records, tmp_path):
    service, portfolio, factory = records
    idea(portfolio, "AS01")
    idea(portfolio, "AS02")
    document = tmp_path / "transcript.md"
    document.write_text("Agentic stack ideas\n", encoding="utf-8")
    payload = SourceInput(
        kind="document",
        title="Agentic stack transcript",
        locator=str(document),
        publisher="User",
        idea_ids=["AS01", "AS02", "AS01"],
        link_note="Transcript segment 1",
    )
    first = service.register_source(payload)
    digest = hashlib.sha256(document.read_bytes()).hexdigest()
    assert first["created"] is True and first["digest"] == digest
    assert first["locator"] == document.resolve().as_uri() + "#sha256=" + digest
    assert first["retrieved_at"] and first["publisher"] == "User"
    assert [link["idea_id"] for link in first["links"]] == ["AS01", "AS02"]
    again = service.register_source(payload)
    assert again["id"] == first["id"] and again["created"] is False
    assert all(link["created"] is False for link in again["links"])

    document.write_text("Agentic stack ideas, revised\n", encoding="utf-8")
    changed = service.register_source(variant(payload, {"idea_ids": []}))
    assert changed["id"] != first["id"] and changed["created"] is True
    listing = portfolio.list_sources()
    assert listing["total"] == 2
    counts = {item["id"]: item["linked_ideas"] for item in listing["items"]}
    assert counts == {first["id"]: 2, changed["id"]: 0}
    shown = service.show_source(first["id"])
    assert shown["linked_ideas"] == 2
    assert {x["role"] for x in shown["links"]} == {"inspiration"}

    sources = portfolio.show_idea("AS01")["sources"]
    assert sources[0]["role"] == "inspiration"
    assert sources[0]["link_note"] == "Transcript segment 1"


def test_url_sources_and_rejected_locators(records, tmp_path):
    service, portfolio, factory = records
    idea(portfolio, "AS01")
    url = SourceInput(kind="webpage", title="Vendor docs", locator="https://ex.com/a")
    first = service.register_source(url)
    assert first["digest"] is None and first["locator"] == "https://ex.com/a"
    assert service.register_source(url)["id"] == first["id"]
    pinned = service.register_source(variant(url, {"content_digest": "a" * 64}))
    assert pinned["id"] != first["id"]
    assert pinned["locator"] == "https://ex.com/a#sha256=" + "a" * 64
    with pytest.raises(ConflictError):
        service.register_source(variant(url, {"kind": "report"}))
    for locator in ["ftp://ex.com/a", str(tmp_path / "absent.md"), str(tmp_path)]:
        with pytest.raises(ValidationError):
            service.register_source(variant(url, {"locator": locator}))
    document = tmp_path / "notes.md"
    document.write_text("x", encoding="utf-8")
    with pytest.raises(ValidationError):
        service.register_source(
            variant(url, {"locator": str(document), "content_digest": "b" * 64})
        )
    with pytest.raises(ReferenceError):
        service.register_source(
            variant(url, {"locator": str(document), "idea_ids": ["absent"]})
        )
    with factory() as session:
        # The failed link rolled back the whole registration.
        assert session.scalar(select(func.count()).select_from(ReferenceSource)) == 2
    with pytest.raises(ContractError):
        SourceInput(kind="webpage", title="x", locator="https://e.com", extra=1)


def test_link_source_is_idempotent_per_role(records):
    service, portfolio, _ = records
    idea(portfolio, "AS01")
    source = service.register_source(
        SourceInput(kind="report", title="Market scan", locator="https://ex.com/m")
    )
    role = IdeaSourceRole.MARKET_REFERENCE
    first = service.link_source("AS01", source["id"], role, "Pricing table")
    assert first["created"] is True and first["role"] == "market_reference"
    assert service.link_source("AS01", source["id"], role, None)["created"] is False
    validation = service.link_source(
        "AS01", source["id"], IdeaSourceRole.VALIDATION, None
    )
    assert validation["created"] is True
    assert len(portfolio.show_idea("AS01")["sources"]) == 2
    with pytest.raises(ReferenceError):
        service.link_source("AS01", "absent", role, None)
    with pytest.raises(ReferenceError):
        service.link_source("absent", source["id"], role, None)


def test_market_actor_identity_and_conflicts(records):
    service, _, _ = records
    first = service.register_actor(
        MarketActorInput(
            name="  Cursor  Inc ", website="HTTPS://Cursor.com/", description="IDE"
        )
    )
    assert first["created"] is True and first["name"] == "Cursor Inc"
    assert first["website"] == "https://cursor.com"
    same = service.register_actor(
        MarketActorInput(name="Cursor Inc", website="https://cursor.com")
    )
    assert same["id"] == first["id"] and same["created"] is False
    assert (
        service.register_actor(MarketActorInput(name="cursor inc"))["id"]
        == (first["id"])
    )
    with pytest.raises(ConflictError):
        service.register_actor(
            MarketActorInput(name="Cursor Inc", website="https://other.example")
        )
    with pytest.raises(ContractError):
        MarketActorInput(name="Bad", website="javascript:alert(1)")
    service.register_actor(MarketActorInput(name="Windsurf", description="Agent IDE"))
    assert service.list_actors(query="agent")["total"] == 1
    assert service.list_actors()["total"] == 2
    assert service.show_actor(first["id"])["links"] == []
    with pytest.raises(ReferenceError):
        service.show_actor("absent")


def test_actor_links_are_revision_scoped_idempotent_and_audited(records):
    service, portfolio, factory = records
    idea(portfolio, "AS03")
    source = service.register_source(
        SourceInput(kind="webpage", title="Pricing", locator="https://ex.com/p")
    )
    payload = ActorLinkInput(
        actor=MarketActorInput(name="Devin", website="https://devin.ai"),
        relation="competitor",
        is_primary=True,
        note="Autonomous agent; gap: no local evidence history",
        checked_on="2026-10-09",
        source_ids=[source["id"], source["id"]],
        recorded_by="discovery-agent",
    )
    first = service.link_actor("AS03", payload)
    assert first["created"] is True and first["updated"] is False
    assert first["source_ids"] == [source["id"]] and first["revision_number"] == 1
    repeat = service.link_actor("AS03", payload)
    assert repeat["created"] is False and repeat["updated"] is False
    rechecked = service.link_actor(
        "AS03",
        ActorLinkInput(
            actor_id=first["actor_id"],
            relation="competitor",
            is_primary=True,
            note="Now ships a local mode",
            checked_on="2026-10-10",
        ),
    )
    assert rechecked["updated"] is True and rechecked["link_id"] == first["link_id"]
    service.link_actor(
        "AS03",
        ActorLinkInput(
            actor=MarketActorInput(name="Spreadsheet"),
            relation="alternative",
            note="Manual tracking",
            checked_on="2026-10-09",
        ),
    )
    competition = portfolio.show_idea("AS03")["competition"]
    assert [c["name"] for c in competition] == ["Devin", "Spreadsheet"]
    assert competition[0]["checked_on"] == "2026-10-10"
    assert competition[0]["note"] == "Now ships a local mode"
    with factory() as session:
        events = session.scalars(
            select(AuditEvent).where(AuditEvent.event_type.like("idea_market_actor_%"))
        ).all()
        assert sorted(e.event_type for e in events) == [
            "idea_market_actor_linked",
            "idea_market_actor_linked",
            "idea_market_actor_updated",
        ]
        updated = next(e for e in events if e.event_type.endswith("updated"))
        assert updated.payload["previous"]["checked_on"] == "2026-10-09"
        assert updated.actor == "local-operator"
    shown = service.show_actor(first["actor_id"])
    assert shown["links"][0]["idea_id"] == "AS03"
    assert shown["links"][0]["current_revision"] is True
    with pytest.raises(ReferenceError):
        service.link_actor("AS03", variant(payload, {"source_ids": ["absent"]}))
    with pytest.raises(ReferenceError):
        service.link_actor(
            "AS03", variant(payload, {"actor": None, "actor_id": "absent"})
        )
    with pytest.raises(ReferenceError):
        service.link_actor("absent", payload)
    with pytest.raises(ContractError):
        ActorLinkInput(
            actor_id="x",
            actor={"name": "Both"},
            relation="competitor",
            note="n",
            checked_on="2026-10-09",
        )
    with pytest.raises(ContractError):
        ActorLinkInput(relation="competitor", note="n", checked_on="2026-10-09")


def test_revision_carries_fields_competition_and_keeps_assessments(records):
    service, portfolio, factory = records
    idea(portfolio, "AS04", "Broad agent platform")
    scores = ScoringService(factory)
    scores.assess(
        AssessmentInput(
            idea_id="AS04", scores=full_scores(6), rationale="r1", author="t"
        )
    )
    service.link_actor(
        "AS04",
        ActorLinkInput(
            actor=MarketActorInput(name="LangSmith"),
            relation="competitor",
            note="Tracing",
            checked_on="2026-10-09",
        ),
    )
    first_revision = portfolio.show_idea("AS04")["revision_id"]
    result = service.revise(
        "AS04",
        IdeaRevisionInput(
            title="Narrow eval harness",
            narrowing_or_pivot="Only regression evals for coding agents",
            focused_mvp_scope="CLI that replays ten traces",
            estimated_mvp_weeks=3,
            change_reason="Competition covers tracing; narrow to replay",
            authored_by="discovery-agent",
            expected_revision_id=first_revision,
        ),
    )
    receipt, shown = result["receipt"], result["idea"]
    assert receipt["revision_number"] == 2 and receipt["carried_competition"] == 1
    assert set(receipt["changed_fields"]) == {
        "title",
        "narrowing_or_pivot",
        "focused_mvp_scope",
        "estimated_mvp_weeks",
    }
    assert shown["title"] == "Narrow eval harness" and shown["revision"] == 2
    assert shown["customer"] == "Operators"  # unspecified fields carry over
    assert shown["description"] == "Testable problem AS04"
    assert shown["estimated_mvp_weeks"] == 3
    assert [c["name"] for c in shown["competition"]] == ["LangSmith"]
    assert shown["competition_history"][0]["revision_number"] == 1
    assert [r["revision_number"] for r in shown["revisions"]] == [2, 1]
    assert shown["revisions"][0]["current"] and not shown["revisions"][0]["assessed"]
    assert shown["revisions"][1]["assessed"]
    history = shown["scores"]["history"]
    assert history[0]["revision_number"] == 1
    assert history[0]["current_revision"] is False
    with factory() as session:
        workspace = session.get(Workspace, shown["workspace_id"])
        assert workspace.title == "Narrow eval harness"
        event = session.scalar(
            select(AuditEvent).where(AuditEvent.event_type == "idea_revised")
        )
        assert event.actor == "discovery-agent"
        assert event.payload["previous_revision_id"] == first_revision

    with pytest.raises(ConflictError):
        service.revise(
            "AS04",
            IdeaRevisionInput(
                title="Stale",
                change_reason="Stale writer",
                authored_by="other",
                expected_revision_id=first_revision,
            ),
        )
    with pytest.raises(ValidationError):
        service.revise(
            "AS04",
            IdeaRevisionInput(
                title="Narrow eval harness", change_reason="No-op", authored_by="a"
            ),
        )
    dropped = service.revise(
        "AS04",
        IdeaRevisionInput(
            target_customer="",
            change_reason="Customer unknown again; competitors to recheck",
            authored_by="a",
            carry_competition=False,
        ),
    )["idea"]
    assert dropped["customer"] is None and dropped["competition"] == []
    assert [h["revision_number"] for h in dropped["competition_history"]] == [2, 1]
    with pytest.raises(ReferenceError):
        service.revise(
            "absent", IdeaRevisionInput(title="x", change_reason="r", authored_by="a")
        )
    with factory() as session:
        assert (
            session.scalar(
                select(func.count())
                .select_from(IdeaRevision)
                .where(IdeaRevision.idea_id == "AS04")
            )
            == 3
        )


def test_promotion_reuses_venture_after_revision(records):
    service, portfolio, _ = records
    idea(portfolio, "AS05")
    venture = portfolio.promote_idea("AS05")
    service.revise(
        "AS05",
        IdeaRevisionInput(title="Narrowed", change_reason="Scope", authored_by="a"),
    )
    assert portfolio.promote_idea("AS05")["id"] == venture["id"]
    assert (
        portfolio.promote_idea("AS05", venture_id=venture["id"])["id"]
        == (venture["id"])
    )
    assert portfolio.show_idea("AS05")["ventures"] == [venture["id"]]


def test_relations_are_explicit_idempotent_and_bidirectional(records):
    service, portfolio, _ = records
    for identity in ["AS06", "AS07", "AS08"]:
        idea(portfolio, identity)
    payload = IdeaRelationInput(
        source_idea_id="AS07",
        target_idea_id="AS06",
        kind="combined_with",
        rationale="Same buyer; merge the evaluation and memory angles",
    )
    first = service.relate(payload)
    assert first["created"] is True
    assert service.relate(payload)["id"] == first["id"]
    with pytest.raises(ConflictError):
        service.relate(variant(payload, {"rationale": "Different"}))
    with pytest.raises(ValidationError):
        service.relate(variant(payload, {"target_idea_id": "AS07"}))
    with pytest.raises(ReferenceError):
        service.relate(variant(payload, {"target_idea_id": "absent"}))
    service.relate(
        IdeaRelationInput(
            source_idea_id="AS08",
            target_idea_id="AS06",
            kind="duplicates",
            rationale="Same proposal in other words",
        )
    )
    relations = portfolio.show_idea("AS06")["relations"]
    assert {(r["direction"], r["kind"], r["other_id"]) for r in relations} == {
        ("incoming", "combined_with", "AS07"),
        ("incoming", "duplicates", "AS08"),
    }
    outgoing = portfolio.show_idea("AS07")
    assert outgoing["relations"][0]["direction"] == "outgoing"
    assert outgoing["relations"][0]["other_title"] == "Idea AS06"
    # Compatibility: `parents` still lists outgoing relations.
    assert outgoing["parents"][0]["id"] == "AS06"


def test_create_from_input_sets_origin_fields_and_sources(records):
    service, portfolio, factory = records
    source = service.register_source(
        SourceInput(kind="document", title="Transcript", locator="https://ex.com/t")
    )
    created = service.create_idea(
        IdeaCreateInput(
            id="AS09",
            title="Agent memory audit",
            description="Inspect what an agent remembered and why",
            original_text="Transcript excerpt",
            target_customer="Platform teams",
            business_model="Per-seat SaaS",
            narrowing_or_pivot="Start with coding agents",
            focused_mvp_scope="Read-only viewer",
            estimated_mvp_weeks=2.5,
            key_validation_test="Five teams inspect a real trace",
            category="devtools",
            venture_type="software",
            cluster="agent-ops",
            origin="generated_new",
            source_ids=[source["id"]],
            source_role="inspiration",
            source_note="Minute 12",
            authored_by="discovery-agent",
        )
    )
    assert created["origin"] == "generated_new"
    assert created["business_model"] == "Per-seat SaaS"
    assert created["cluster"] == "agent-ops" and created["estimated_mvp_weeks"] == 2.5
    assert created["sources"][0]["link_note"] == "Minute 12"
    assert created["revisions"][0]["authored_by"] == "discovery-agent"
    derived = service.create_idea(
        IdeaCreateInput(
            id="AS09b",
            title="Derived",
            description="Narrower",
            parent_ids=["AS09"],
            derivation_reason="Split viewer from audit",
        )
    )
    assert derived["origin"] == "generated_derived"
    with pytest.raises(ValidationError):
        service.create_idea(
            IdeaCreateInput(
                title="x", description="y", parent_ids=["AS09"], origin="generated_new"
            )
        )
    with pytest.raises(ReferenceError):
        service.create_idea(
            IdeaCreateInput(id="AS10", title="x", description="y", source_ids=["no"])
        )
    with pytest.raises(ConflictError):
        service.create_idea(IdeaCreateInput(id="AS09", title="x", description="y"))
    assert portfolio.list_ideas()["total"] == 2


def test_cohort_comparison_reports_missing_and_stale_scores(records):
    service, portfolio, factory = records
    for identity in ["A", "B", "C"]:
        idea(portfolio, identity)
    scores = ScoringService(factory)
    for identity, value in [("A", 8), ("B", 5)]:
        scores.assess(
            AssessmentInput(
                idea_id=identity,
                scores=full_scores(value),
                rationale="cohort " + identity,
                criterion_rationales={"moat": "Workflow lock-in"},
                author="t",
            )
        )
    service.revise(
        "B", IdeaRevisionInput(title="B narrowed", change_reason="n", authored_by="a")
    )
    service.link_actor(
        "A",
        ActorLinkInput(
            actor=MarketActorInput(name="Incumbent"),
            relation="competitor",
            is_primary=True,
            note="Leader",
            checked_on="2026-10-09",
        ),
    )
    service.relate(
        IdeaRelationInput(
            source_idea_id="C", target_idea_id="A", kind="pivots_from", rationale="p"
        )
    )
    result = service.compare(["C", "A", "B", "A"])
    assert [i["id"] for i in result["items"]] == ["C", "A", "B"]
    assert len(result["criteria"]) == 12
    c, a, b = result["items"]
    assert c["total"] is None and c["assessment_id"] is None and c["scores"] == {}
    assert c["relations_in_set"][0]["other_id"] == "A"
    assert a["total"] is not None and a["stale_revision"] is False
    assert a["scores"]["moat"]["rationale"] == "Workflow lock-in"
    assert a["scores"]["moat"]["raw"] == 8 and a["scores"]["moat"]["weighted"]
    assert a["competition_count"] == 1 and a["primary_competitors"] == ["Incumbent"]
    assert a["relations_in_set"][0]["direction"] == "incoming"
    assert b["stale_revision"] is True and b["revision_number"] == 2
    assert b["assessment_revision_number"] == 1 and b["total"] is not None
    assert b["disposition"] is None
    with pytest.raises(ValidationError):
        service.compare([str(i) for i in range(21)])
    with pytest.raises(ValidationError):
        service.compare([" "])
    with pytest.raises(ReferenceError):
        service.compare(["A", "absent"])
    with pytest.raises(ReferenceError):
        service.compare(["A"], "unknown-card")


def test_idea_views_filter_by_source(records):
    service, portfolio, factory = records
    for identity in ["A", "B", "C"]:
        idea(portfolio, identity)
    source = service.register_source(
        SourceInput(
            kind="document",
            title="Cohort",
            locator="https://ex.com/c",
            idea_ids=["A", "C"],
        )
    )
    views = PortfolioViewService(factory)
    page = views.list("idea", PortfolioQuery(source_id=source["id"]))
    assert sorted(i["id"] for i in page["items"]) == ["A", "C"]
    assert views.list("idea", PortfolioQuery())["total"] == 3
    with pytest.raises(ValidationError):
        views.list("venture", PortfolioQuery(source_id=source["id"]))


def test_original_import_is_not_repeated_after_a_revision(records):
    service, portfolio, factory = records
    with (SOURCES / "startup_ideas.csv").open(encoding="utf-8-sig", newline="") as f:
        rows = list(csv.DictReader(f))
    for row in rows:
        portfolio.create_idea(
            IdeaDraft(title=row["Title"], description=row["Cleaned description"]),
            idea_id=row["Idea ID"],
        )
    scores = ScoringService(factory)
    assert scores.import_original(SOURCES)["imported"] == len(rows)
    service.revise(
        "P023", IdeaRevisionInput(title="Narrowed", change_reason="n", authored_by="a")
    )
    assert scores.import_original(SOURCES)["imported"] == 0
    history = scores.show("P023")["history"]
    assert len(history) == 1 and history[0]["revision_number"] == 1
