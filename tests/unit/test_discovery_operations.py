"""Product behavior for persistent intake, lineage and bounded steps."""

from pathlib import Path

import pytest

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import VentureStage
from startup_foundry.errors import ConflictError, ReferenceError, ValidationError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.steps import StepService
from startup_foundry.storage import backup_sqlite


@pytest.fixture
def services(tmp_path):
    url = f"sqlite:///{tmp_path / 'foundry.local.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    yield (
        FoundryApplication(factory),
        PortfolioService(factory),
        StepService(factory, tmp_path / "requests"),
        url,
    )
    engine.dispose()


def test_idea_lineage_promotion_and_restart(services):
    app, portfolio, _, url = services
    parent = portfolio.create_idea(
        IdeaDraft(
            title="Ride repair",
            description="Shorten a route within a time budget.",
            customer="Touring riders",
            validation_test="Compare a specified ride.",
        ),
        idea_id="N008",
    )
    child = portfolio.create_idea(
        IdeaDraft(
            title="Transfer preflight",
            description="Compare the transferred path.",
            parent_ids=["N008"],
            derivation_reason="Separate geometry from ETA.",
        ),
        idea_id="derived-1",
    )
    assert child["parents"][0]["id"] == parent["id"]
    promoted = portfolio.promote_idea("derived-1", venture_id="preflight")
    assert promoted["stage"] == "discovery"
    assert portfolio.promote_idea("derived-1", venture_id="preflight") == promoted
    assert portfolio.promote_idea("derived-1") == promoted
    with pytest.raises(ConflictError):
        portfolio.promote_idea("N008", venture_id="preflight")
    engine = create_db_engine(url)
    try:
        recovered = PortfolioService(create_session_factory(engine))
        assert recovered.show_idea("derived-1")["parents"] == child["parents"]
        assert recovered.list_ideas(query="preflight")["total"] == 1
        assert app.list_ventures()["total"] == 1
    finally:
        engine.dispose()


def test_invalid_parent_and_blank_creation_are_atomic(services):
    _, portfolio, _, _ = services
    with pytest.raises(ReferenceError):
        portfolio.create_idea(
            IdeaDraft(
                title="Bad lineage",
                description="No parent exists",
                parent_ids=["absent"],
                derivation_reason="A reason",
            )
        )
    with pytest.raises(ValidationError):
        portfolio.create_idea(IdeaDraft(title=" ", description="Incomplete"))
    assert portfolio.list_ideas()["total"] == 0


def test_step_idempotency_isolation_and_missing_agent_handoff(services):
    app, portfolio, steps, _ = services
    app.create_venture(
        venture_id="route",
        name="Route",
        objective="A real task",
        stage=VentureStage.DISCOVERY,
    )
    app.create_venture(
        venture_id="other",
        name="Other",
        objective="Other task",
        stage=VentureStage.DISCOVERY,
    )
    first = steps.start("venture", "route", "readiness", request_key="check-1")
    assert first["status"] == "succeeded"
    assert first["output"]["commercial_build_qualified"] is False
    assert steps.start("venture", "route", "readiness", request_key="check-1") == first
    with pytest.raises(ConflictError):
        steps.start("venture", "other", "readiness", request_key="check-1")
    assert steps.list_runs("venture", "other")["total"] == 0
    blocked = steps.start("venture", "route", "agent_research", request_key="agent-1")
    assert blocked["status"] == "blocked"
    request_file = Path(blocked["output"]["request_file"])
    assert request_file.is_file()
    assert "Response" in request_file.read_text()
    assert (
        steps.start("venture", "route", "agent_research", request_key="agent-1")
        == blocked
    )
    assert len(list(request_file.parent.glob("*.md"))) == 1


def test_failed_runner_and_adapter_result_are_persisted(services):
    app, _, steps, _ = services
    app.create_venture(
        venture_id="r", name="R", objective="A task", stage=VentureStage.DISCOVERY
    )

    class Runner:
        name = "test-runner"
        version = "fixture-v1"

        def run(self, context):
            raise RuntimeError("private details must not appear in error summaries")

    steps.agent_runner = Runner()
    failed = steps.start("venture", "r", "agent_research", request_key="failure")
    assert failed["status"] == "failed"
    assert "private details" not in str(failed)
    assert steps.show_run(failed["id"]) == failed


def test_runner_success_and_interrupted_recovery_are_distinct(services):
    from startup_foundry.domain import StepRun, StepStatus, WorkItem, WorkItemStatus
    from startup_foundry.repository import UnitOfWork

    app, _, steps, _ = services
    app.create_venture(
        venture_id="r", name="R", objective="A task", stage=VentureStage.DISCOVERY
    )

    class Runner:
        name = "fixture"
        version = "1"

        def run(self, context):
            return {"subject": context["subject_id"], "finding": "Unvalidated draft"}

    steps.agent_runner = Runner()
    done = steps.start("venture", "r", "agent_research", request_key="success")
    assert done["output"]["draft"]["subject"] == "r"
    assert done["output"]["review_required"] is True
    assert steps.recover_interrupted(done["id"], "Must not replace result") == done

    class InterruptedRunner(Runner):
        def run(self, context):
            raise KeyboardInterrupt

    steps.agent_runner = InterruptedRunner()
    with pytest.raises(KeyboardInterrupt):
        steps.start("venture", "r", "agent_research", request_key="interrupted")
    interrupted = steps.list_runs()["items"][0]
    assert interrupted["status"] == "running"
    recovered = steps.recover_interrupted(interrupted["id"], "Process stopped")
    assert recovered["status"] == "failed"
    with UnitOfWork(steps.factory) as unit:
        run = unit.session.get(StepRun, interrupted["id"])
        assert run.status == StepStatus.FAILED
        assert (
            unit.session.get(WorkItem, run.work_item_id).status
            == WorkItemStatus.BLOCKED
        )


def test_source_reuse_keeps_claim_revisions_and_validates_links(services):
    _, portfolio, _, _ = services
    portfolio.create_idea(IdeaDraft(title="Parent", description="A task"), idea_id="p")
    payload = {
        "title": "Comparator",
        "url": "https://example.org/tool",
        "claim": "Documented capability",
        "limits": "No runtime trial",
        "checked_on": "2026-10-02",
    }
    first = portfolio.record_source(payload, idea_ids=["p"])
    assert portfolio.record_source(payload, idea_ids=["p"])["id"] == first["id"]
    second = portfolio.record_source(
        {**payload, "claim": "Revised claim"}, idea_ids=["p"]
    )
    assert second["id"] != first["id"]
    assert len(portfolio.show_idea("p")["sources"]) == 2
    with pytest.raises(ReferenceError):
        portfolio.record_source({**payload, "claim": "Third"}, idea_ids=["absent"])
    assert portfolio.list_sources()["total"] == 2


def test_backup_preserves_state_and_refuses_overwrite(services, tmp_path):
    app, _, _, url = services
    app.create_venture(
        venture_id="saved",
        name="Saved",
        objective="Persist",
        stage=VentureStage.DISCOVERY,
    )
    output = tmp_path / "backup.local.db"
    backup_sqlite(url, output)
    engine = create_db_engine(f"sqlite:///{output}")
    try:
        assert (
            FoundryApplication(create_session_factory(engine)).list_ventures()["total"]
            == 1
        )
    finally:
        engine.dispose()
    with pytest.raises(ConflictError):
        backup_sqlite(url, output)


def test_csv_import_reconciles_views_and_retries_atomically(services, tmp_path):
    import csv
    import json

    from startup_foundry.portfolio import CSV_NAMES

    _, portfolio, _, _ = services
    inputs = tmp_path / "exports"
    campaign = tmp_path / "campaign"
    inputs.mkdir()
    campaign.mkdir()
    for name in CSV_NAMES:
        with (inputs / (name + ".csv")).open("w", newline="") as stream:
            writer = csv.writer(stream)
            writer.writerow(["Idea ID", "Title", "Cleaned description"])
            writer.writerow(["P001", "One idea", "One task"])
    (campaign / "ideas.json").write_text(
        json.dumps(
            [
                {
                    "id": "P001",
                    "title": "One idea",
                    "original": "Original task",
                    "group": "test",
                    "next_test": "Test the incumbent",
                    "source_ids": ["source"],
                    "disposition": "HOLD",
                    "rationale": "Demand unknown",
                }
            ]
        )
    )
    (campaign / "sources.json").write_text(
        json.dumps(
            [
                {
                    "id": "source",
                    "title": "Comparator",
                    "url": "https://example.org",
                    "claim": "Source claim only",
                }
            ]
        )
    )
    result = portfolio.import_campaign(inputs, campaign)
    assert result["created"] == 1
    assert portfolio.list_ideas()["total"] == 1

    assert portfolio.import_campaign(inputs, campaign)["already_imported"] is True
    assert portfolio.list_sources()["total"] == 8
    assert portfolio.show_idea("P001")["assessment"]["rationale"] == "Demand unknown"
    # Same ID with changed material must not silently overwrite the old intake.
    (inputs / "startup_dashboard.csv").write_text("changed,input\n1,2\n")
    with pytest.raises(ConflictError):
        portfolio.import_campaign(inputs, campaign)
    assert portfolio.list_sources()["total"] == 8
    assert portfolio.list_ideas()["total"] == 1

    (inputs / "startup_ideas.csv").write_text(
        "Idea ID,Title,Cleaned description\nP001,short\n"
    )
    with pytest.raises(ValidationError, match="row width"):
        portfolio.import_campaign(inputs, campaign)
    assert portfolio.list_sources()["total"] == 8


def test_default_path_does_not_follow_working_directory(tmp_path, monkeypatch):
    from startup_foundry.config import load_settings

    first = tmp_path / "first"
    second = tmp_path / "second"
    first.mkdir()
    second.mkdir()
    env = {"XDG_DATA_HOME": str(tmp_path / "persistent")}
    monkeypatch.chdir(first)
    before = load_settings(env).database_url
    monkeypatch.chdir(second)
    assert load_settings(env).database_url == before
    assert str(tmp_path / "persistent/startup-foundry/foundry.local.db") in before
    from startup_foundry.errors import ConfigurationError

    with pytest.raises(ConfigurationError, match="absolute"):
        load_settings({"XDG_DATA_HOME": "relative"})
    assert (
        load_settings(
            {"XDG_DATA_HOME": "relative", "FOUNDRY_DATABASE_URL": "sqlite:///:memory:"}
        ).database_url
        == "sqlite:///:memory:"
    )
