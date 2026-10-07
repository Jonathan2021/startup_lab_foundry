"""Campaign regression: planned comparison criteria survive venture reconstruction."""
from __future__ import annotations

from pathlib import Path

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import AssumptionKind, VentureStage, WorkItemKind
from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory


def test_venture_reconstructs_experiment_protocol_without_cross_venture_leak(
    tmp_path: Path,
) -> None:
    url = f"sqlite:///{tmp_path / 'campaign.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    app = FoundryApplication(create_session_factory(engine))
    try:
        for key in ("monitor", "mlflow"):
            app.create_venture(
                venture_id=key,
                name=key,
                objective="Compare the incumbent before implementing a substitute.",
                stage=VentureStage.DISCOVERY,
            )
            app.add_assumption(
                assumption_id=f"a-{key}",
                venture_id=key,
                statement="The incumbent may already support the workflow.",
                kind=AssumptionKind.FEASIBILITY,
                importance=5,
                uncertainty=4,
            )
            app.add_work_item(
                work_item_id=f"w-{key}",
                venture_id=key,
                title=f"Trial {key}",
                kind=WorkItemKind.EXPERIMENT,
                decision_id=None,
                acceptance_criteria="Save observed failures as well as passes.",
                method=f"Run the pinned {key} baseline on frozen local inputs.",
                success_criteria=f"{key} preserves the expected evidence.",
                failure_criteria=f"{key} cannot reproduce the needed behavior.",
                assumption_ids=[f"a-{key}"],
            )
        app.add_work_item(
            work_item_id="ordinary-work",
            venture_id="monitor",
            title="Review source documentation",
            kind=WorkItemKind.INVESTIGATION,
            decision_id=None,
            acceptance_criteria=None,
            method=None,
            success_criteria=None,
            failure_criteria=None,
            assumption_ids=[],
        )
        first = app.show_venture("monitor")
        assert first == app.show_venture("monitor")
        experiments = first["experiments"]
        assert isinstance(experiments, list)
        assert len(experiments) == 1
        protocol = experiments[0]
        assert protocol["work_item_id"] == "w-monitor"
        assert protocol["status"] == "planned"
        assert protocol["method"] == (
            "Run the pinned monitor baseline on frozen local inputs."
        )
        assert protocol["success_criteria"] == (
            "monitor preserves the expected evidence."
        )
        assert protocol["failure_criteria"] == (
            "monitor cannot reproduce the needed behavior."
        )
        assert protocol["assumption_ids"] == ["a-monitor"]
        assert protocol["result_summary"] is None
        assert len(first["work_items"]) == 2
        other = app.show_venture("mlflow")["experiments"]
        assert other[0]["work_item_id"] == "w-mlflow"
    finally:
        engine.dispose()
