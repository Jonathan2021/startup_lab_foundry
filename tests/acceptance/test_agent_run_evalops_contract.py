"""Foundry-side behavior contract for the first Agent EvalOps integration."""

from __future__ import annotations

import json
import os
import subprocess
import sys
from pathlib import Path
from typing import Any

FIXTURE = Path(__file__).resolve().parents[1] / "fixtures" / "agent_run_v1.json"


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


def create_evalops_venture(database: Path) -> None:
    require_success(
        run_foundry(
            database,
            "venture",
            "create",
            "--id",
            "venture-agentevalops",
            "--name",
            "Agent EvalOps",
            "--objective",
            "Turn agent failures and human corrections into release evidence.",
            "--stage",
            "discovery",
        )
    )


def record_run(database: Path, fixture: Path = FIXTURE) -> dict[str, Any]:
    return require_success(
        run_foundry(database, "agent-run", "record", "--input", str(fixture))
    )


def test_recorded_run_reconstructs_the_versioned_trace_contract(tmp_path: Path) -> None:
    database = tmp_path / "foundry.local.db"
    create_evalops_venture(database)
    recorded = record_run(database)

    assert recorded["run"] == {
        "id": "run-competitor-research-001",
        "venture_id": "venture-agentevalops",
        "agent_version_id": "agent-competitor-research-v1",
        "status": "succeeded",
        "evalops_trace_id": None,
    }
    assert recorded["trace"] == json.loads(FIXTURE.read_text())
    assert require_success(
        run_foundry(
            database,
            "agent-run",
            "show",
            "--id",
            "run-competitor-research-001",
        )
    ) == recorded


def test_evalops_trace_link_is_retry_safe_and_cannot_be_rebound(tmp_path: Path) -> None:
    database = tmp_path / "foundry.local.db"
    create_evalops_venture(database)
    record_run(database)

    for _ in range(2):
        linked = require_success(
            run_foundry(
                database,
                "agent-run",
                "link-evalops",
                "--id",
                "run-competitor-research-001",
                "--trace-id",
                "trace-evalops-001",
            )
        )
        assert linked["run"]["evalops_trace_id"] == "trace-evalops-001"

    conflict = run_foundry(
        database,
        "agent-run",
        "link-evalops",
        "--id",
        "run-competitor-research-001",
        "--trace-id",
        "trace-evalops-conflict",
    )
    assert conflict.returncode == 2
    assert "trace" in conflict.stderr.lower()
    shown = require_success(
        run_foundry(
            database,
            "agent-run",
            "show",
            "--id",
            "run-competitor-research-001",
        )
    )
    assert shown["run"]["evalops_trace_id"] == "trace-evalops-001"


def test_invalid_event_sequence_rolls_back_all_run_records(tmp_path: Path) -> None:
    database = tmp_path / "foundry.local.db"
    create_evalops_venture(database)
    payload = json.loads(FIXTURE.read_text())
    payload["events"][2]["sequence"] = 2
    invalid = tmp_path / "invalid-run.json"
    invalid.write_text(json.dumps(payload))

    result = run_foundry(
        database, "agent-run", "record", "--input", str(invalid)
    )
    assert result.returncode == 2
    assert "sequence" in result.stderr.lower() or "event" in result.stderr.lower()

    recorded = record_run(database)
    assert recorded["run"]["id"] == "run-competitor-research-001"


def test_secret_bearing_run_is_rejected_without_persisting_it(tmp_path: Path) -> None:
    database = tmp_path / "foundry.local.db"
    create_evalops_venture(database)
    payload = json.loads(FIXTURE.read_text())
    payload["events"][1]["payload"]["authorization"] = "Bearer must-not-leak"
    invalid = tmp_path / "secret-bearing-run.json"
    invalid.write_text(json.dumps(payload))

    result = run_foundry(
        database, "agent-run", "record", "--input", str(invalid)
    )
    assert result.returncode == 2
    assert "secret" in result.stderr.lower() or "credential" in result.stderr.lower()
    assert "must-not-leak" not in result.stderr

    missing = run_foundry(
        database,
        "agent-run",
        "show",
        "--id",
        "run-competitor-research-001",
    )
    assert missing.returncode == 2


def test_unknown_venture_does_not_create_agent_or_run_history(tmp_path: Path) -> None:
    database = tmp_path / "foundry.local.db"
    result = run_foundry(
        database, "agent-run", "record", "--input", str(FIXTURE)
    )
    assert result.returncode == 2
    assert "venture" in result.stderr.lower()

    create_evalops_venture(database)
    recorded = record_run(database)
    assert recorded["run"]["venture_id"] == "venture-agentevalops"
