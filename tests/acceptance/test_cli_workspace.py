"""End-to-end acceptance checks for the Foundry CLI workspace."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

import pytest


def run_foundry(database: Path, *arguments: str) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONUTF8"] = "1"
    return subprocess.run(
        [
            sys.executable,
            "-m",
            "startup_foundry",
            "--store",
            str(database),
            *arguments,
        ],
        check=False,
        capture_output=True,
        text=True,
        env=environment,
    )


def require_success(result: subprocess.CompletedProcess[str]) -> dict[str, Any]:
    assert result.returncode == 0, (
        f"command failed with {result.returncode}\nstdout:\n{result.stdout}\n"
        f"stderr:\n{result.stderr}"
    )
    return json.loads(result.stdout)


def create_venture(
    database: Path, venture_id: str = "venture-agentevalops"
) -> dict[str, Any]:
    return require_success(
        run_foundry(
            database,
            "venture",
            "create",
            "--id",
            venture_id,
            "--name",
            "Agent EvalOps",
            "--objective",
            "Turn agent failures and human corrections into release evidence.",
            "--stage",
            "discovery",
        )
    )


def add_assumption(
    database: Path, venture_id: str = "venture-agentevalops"
) -> dict[str, Any]:
    return require_success(
        run_foundry(
            database,
            "assumption",
            "add",
            "--id",
            f"assumption-{venture_id}",
            "--venture-id",
            venture_id,
            "--statement",
            "Teams repeat corrected failures because corrections are not "
            "regression cases.",
            "--kind",
            "desirability",
            "--importance",
            "5",
            "--uncertainty",
            "4",
        )
    )


def assert_utc_timestamp(value: str) -> None:
    assert value.endswith("Z") or value.endswith("+00:00")


def test_help_exposes_the_stage_zero_workflow(tmp_path: Path) -> None:
    result = run_foundry(tmp_path / "workspace.local.db", "--help")
    assert result.returncode == 0
    for command in (
        "venture",
        "assumption",
        "evidence",
        "decision",
        "work-item",
        "artifact",
    ):
        assert command in result.stdout


def test_create_and_reload_a_venture_in_separate_processes(tmp_path: Path) -> None:
    database = tmp_path / "workspace.local.db"
    created = create_venture(database)
    assert created["id"] == "venture-agentevalops"
    assert created["name"] == "Agent EvalOps"
    assert created["stage"] == "discovery"
    assert_utc_timestamp(created["created_at"])

    shown = require_success(
        run_foundry(database, "venture", "show", "--id", "venture-agentevalops")
    )
    assert shown["venture"] == created
    for collection in (
        "assumptions",
        "evidence",
        "assumption_assessments",
        "decisions",
        "work_items",
        "artifacts",
    ):
        assert shown[collection] == []


def test_build_an_evidence_backed_venture_workspace(tmp_path: Path) -> None:
    database = tmp_path / "workspace.local.db"
    create_venture(database)
    assumption = add_assumption(database)

    experiment_work = require_success(
        run_foundry(
            database,
            "work-item",
            "add",
            "--id",
            "work-experiment-001",
            "--venture-id",
            "venture-agentevalops",
            "--title",
            "Inspect design-partner correction workflows",
            "--kind",
            "experiment",
            "--method",
            "Inspect anonymized correction histories from two teams.",
            "--success-criteria",
            "Each team has at least one corrected failure that later recurred.",
            "--failure-criteria",
            "Teams already retain durable cases or corrected failures never recur.",
            "--assumption-id",
            assumption["id"],
        )
    )
    evidence = require_success(
        run_foundry(
            database,
            "evidence",
            "add",
            "--id",
            "evidence-001",
            "--venture-id",
            "venture-agentevalops",
            "--origin-work-item-id",
            experiment_work["id"],
            "--kind",
            "experiment_result",
            "--confidence",
            "high",
            "--summary",
            "Both teams found a previously corrected failure that recurred.",
        )
    )
    assessment = require_success(
        run_foundry(
            database,
            "assumption",
            "assess",
            "--id",
            "assessment-001",
            "--assumption-id",
            assumption["id"],
            "--evidence-id",
            evidence["id"],
            "--outcome",
            "supported",
            "--confidence",
            "medium",
            "--rationale",
            "The pain is observed, but two teams are not enough to generalize.",
        )
    )
    decision = require_success(
        run_foundry(
            database,
            "decision",
            "add",
            "--id",
            "decision-001",
            "--venture-id",
            "venture-agentevalops",
            "--kind",
            "narrow",
            "--summary",
            "Own the failure-to-evaluation-case loop.",
            "--rationale",
            "Reviewed corrections are not retained as release tests.",
            "--assessment-id",
            assessment["id"],
        )
    )
    execution_work = require_success(
        run_foundry(
            database,
            "work-item",
            "add",
            "--id",
            "work-execution-001",
            "--venture-id",
            "venture-agentevalops",
            "--decision-id",
            decision["id"],
            "--title",
            "Define the first trace contract",
            "--kind",
            "execution",
            "--acceptance-criteria",
            "One reviewed failure can become a version-addressed evaluation case.",
        )
    )
    artifact = require_success(
        run_foundry(
            database,
            "artifact",
            "add",
            "--id",
            "artifact-001",
            "--venture-id",
            "venture-agentevalops",
            "--work-item-id",
            execution_work["id"],
            "--kind",
            "document",
            "--name",
            "Agent EvalOps product brief",
            "--location",
            "agentevalops/docs/agent_evalops_project.md",
        )
    )

    assert assumption["status"] == "open"
    assert experiment_work["kind"] == "experiment"
    assert evidence["origin_work_item_id"] == experiment_work["id"]
    assert assessment["evidence_ids"] == [evidence["id"]]
    assert decision["assessment_ids"] == [assessment["id"]]
    assert execution_work["decision_id"] == decision["id"]
    assert artifact["work_item_id"] == execution_work["id"]

    workspace = require_success(
        run_foundry(database, "venture", "show", "--id", "venture-agentevalops")
    )
    expected_ids = {
        "assumptions": [assumption["id"]],
        "evidence": [evidence["id"]],
        "assumption_assessments": [assessment["id"]],
        "decisions": [decision["id"]],
        "work_items": [experiment_work["id"], execution_work["id"]],
        "artifacts": [artifact["id"]],
    }
    for collection, identifiers in expected_ids.items():
        assert [item["id"] for item in workspace[collection]] == identifiers


def test_work_item_status_transitions_are_persisted_and_validated(
    tmp_path: Path,
) -> None:
    database = tmp_path / "workspace.local.db"
    create_venture(database)
    require_success(
        run_foundry(
            database,
            "work-item",
            "add",
            "--id",
            "work-001",
            "--venture-id",
            "venture-agentevalops",
            "--title",
            "Define the first trace contract",
            "--kind",
            "execution",
            "--acceptance-criteria",
            "A version-addressed trace contract exists.",
        )
    )
    updated = require_success(
        run_foundry(
            database,
            "work-item",
            "set-status",
            "--id",
            "work-001",
            "--status",
            "in_progress",
        )
    )
    assert updated["status"] == "in_progress"

    rejected = run_foundry(
        database,
        "work-item",
        "set-status",
        "--id",
        "work-001",
        "--status",
        "almost_done",
    )
    assert rejected.returncode != 0
    workspace = require_success(
        run_foundry(database, "venture", "show", "--id", "venture-agentevalops")
    )
    assert workspace["work_items"][0]["status"] == "in_progress"


@pytest.mark.parametrize(
    "arguments",
    [
        (
            "assumption",
            "add",
            "--id",
            "assumption-orphan",
            "--venture-id",
            "missing-venture",
            "--statement",
            "This must not be stored.",
            "--kind",
            "viability",
            "--importance",
            "3",
            "--uncertainty",
            "3",
        ),
        (
            "artifact",
            "add",
            "--id",
            "artifact-orphan",
            "--venture-id",
            "missing-venture",
            "--kind",
            "document",
            "--name",
            "Orphan",
            "--location",
            "nowhere",
        ),
    ],
)
def test_orphan_records_are_rejected_without_partial_writes(
    tmp_path: Path, arguments: tuple[str, ...]
) -> None:
    database = tmp_path / "workspace.local.db"
    rejected = run_foundry(database, *arguments)
    assert rejected.returncode != 0

    create_venture(database)
    workspace = require_success(
        run_foundry(database, "venture", "show", "--id", "venture-agentevalops")
    )
    assert workspace["assumptions"] == []
    assert workspace["artifacts"] == []


def test_missing_and_cross_venture_references_are_rejected(tmp_path: Path) -> None:
    database = tmp_path / "workspace.local.db"
    create_venture(database)
    first_assumption = add_assumption(database)
    create_venture(database, "venture-other")

    other_evidence = require_success(
        run_foundry(
            database,
            "evidence",
            "add",
            "--id",
            "evidence-other",
            "--venture-id",
            "venture-other",
            "--kind",
            "observation",
            "--confidence",
            "low",
            "--summary",
            "An observation in a different venture.",
        )
    )
    cross_venture = run_foundry(
        database,
        "assumption",
        "assess",
        "--id",
        "assessment-invalid",
        "--assumption-id",
        first_assumption["id"],
        "--evidence-id",
        other_evidence["id"],
        "--outcome",
        "inconclusive",
        "--confidence",
        "low",
        "--rationale",
        "Cross-venture evidence cannot be attached accidentally.",
    )
    assert cross_venture.returncode != 0

    missing_assessment = run_foundry(
        database,
        "decision",
        "add",
        "--id",
        "decision-invalid",
        "--venture-id",
        "venture-agentevalops",
        "--kind",
        "continue",
        "--summary",
        "Invalid decision",
        "--rationale",
        "It references an absent assessment.",
        "--assessment-id",
        "missing-assessment",
    )
    assert missing_assessment.returncode != 0

    workspace = require_success(
        run_foundry(database, "venture", "show", "--id", "venture-agentevalops")
    )
    assert workspace["assumption_assessments"] == []
    assert workspace["decisions"] == []


def test_duplicate_ids_do_not_overwrite_existing_records(tmp_path: Path) -> None:
    database = tmp_path / "workspace.local.db"
    original = create_venture(database)
    duplicate = run_foundry(
        database,
        "venture",
        "create",
        "--id",
        "venture-agentevalops",
        "--name",
        "Replacement",
        "--objective",
        "This must not overwrite the original.",
        "--stage",
        "operating",
    )
    assert duplicate.returncode != 0

    shown = require_success(
        run_foundry(database, "venture", "show", "--id", "venture-agentevalops")
    )
    assert shown["venture"] == original


def test_blank_required_text_is_rejected_without_creating_a_database(
    tmp_path: Path,
) -> None:
    database = tmp_path / "workspace.local.db"
    rejected = run_foundry(
        database,
        "venture",
        "create",
        "--id",
        "venture-agentevalops",
        "--name",
        "   ",
        "--objective",
        "A valid objective cannot rescue a blank name.",
        "--stage",
        "discovery",
    )
    assert rejected.returncode != 0
    assert "name" in rejected.stderr.lower()
    assert "blank" in rejected.stderr.lower() or "required" in rejected.stderr.lower()
    assert not database.exists()
