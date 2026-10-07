"""Real CLI dogfood bridge against an isolated store, including retry failure."""

from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path
from uuid import uuid4

from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.decision_contracts import WorkClaimInput
from startup_foundry.demo import create_demo
from startup_foundry.errors import ConflictError
from startup_foundry.repository import create_db_engine, create_session_factory

KIT = Path(__file__).resolve().parents[2] / "scripts/agent-kit/foundry_agent.py"


def test_independent_agent_feedback_retry_and_claim_conflict(tmp_path):
    store = tmp_path / "store.db"
    manifest = create_demo(store)
    source, target = manifest["ventures"][:2]
    project = tmp_path / "venture"
    (project / ".foundry").mkdir(parents=True)
    config_path = project / ".foundry/project.json"
    config = {
        "cli": [sys.executable, "-m", "startup_foundry", "--store", str(store)],
        "venture_id": source["venture_id"],
        "workspace_id": source["workspace_id"],
        "feedback_workspace_id": target["workspace_id"],
    }
    config_path.write_text(json.dumps(config))

    def run(*args):
        return subprocess.run(
            [sys.executable, str(KIT), *args],
            cwd=project,
            capture_output=True,
            text=True,
            timeout=30,
        )

    resumed = run("resume")
    assert resumed.returncode == 0, resumed.stderr
    assert json.loads(resumed.stdout)["workspace_id"] == source["workspace_id"]
    report = json.loads(run("feedback-template").stdout)
    report.update(actor="test-agent", summary="Context discovery takes extra commands")
    payload = project / "input.json"
    payload.write_text(json.dumps(report))
    # Offline attempt is retained, then exactly the same report is retried.
    config_path.write_text(json.dumps({**config, "cli": ["/nonexistent/foundry"]}))
    failed = run("feedback", "--input", str(payload))
    assert failed.returncode == 1
    saved = project / "feedback" / (report["id"] + ".json")
    assert json.loads(saved.read_text()) == report
    assert not saved.with_suffix(".receipt.json").exists()
    config_path.write_text(json.dumps(config))
    first = run("feedback", "--input", str(payload))
    second = run("feedback", "--input", str(payload))
    assert first.returncode == second.returncode == 0, first.stderr + second.stderr
    assert json.loads(first.stdout)["receipt"] == json.loads(second.stdout)["receipt"]
    # Changed payload under the same identity cannot overwrite history.
    payload.write_text(json.dumps({**report, "actual": "changed later"}))
    assert run("feedback", "--input", str(payload)).returncode == 1
    assert json.loads(saved.read_text()) == report
    # Source-scoped report cannot be attributed to a different venture.
    payload.write_text(
        json.dumps({**report, "id": str(uuid4()), "venture_id": "other"})
    )
    assert run("feedback", "--input", str(payload)).returncode == 1

    engine = create_db_engine("sqlite:///" + str(store))
    factory = create_session_factory(engine)
    service = AgentHandoffService(factory)
    work = service.resume(source["workspace_id"])["work"][0]
    failed_start = run(
        "start",
        "--actor",
        "one",
        "--work-id",
        work["id"],
        "--budget-bytes",
        "512",
    )
    assert failed_start.returncode == 1
    released = service.resume(source["workspace_id"])["work"][0]
    assert released["status"] == "ready" and released["owner"] == "agent"
    started = run("start", "--actor", "one", "--work-id", work["id"])
    assert started.returncode == 0, started.stderr
    context = json.loads(started.stdout)
    assert Path(context["saved_context"]).is_file()
    assert context["work"]["owner"] == "one"
    try:
        service.claim(
            source["workspace_id"],
            work["id"],
            WorkClaimInput(actor="two", expected_version=work["version_id"]),
        )
    except ConflictError:
        pass
    else:
        raise AssertionError("A second agent claimed the same work")
    from startup_foundry.workspace_modules import RenameInput, WorkspaceModuleService

    modules = WorkspaceModuleService(factory)
    version = modules.show(source["venture_id"])["workspace_version"]
    modules.rename(
        source["venture_id"],
        RenameInput(
            expected_version=version,
            title="Clarified name",
            actor="operator",
            rationale="User corrected the scope label",
        ),
    )
    retained = service.show_context(context["id"])
    assert "Venture scope changed" in retained["stale_reasons"]
    assert retained["scope"]["title"] == context["scope"]["title"]
    engine.dispose()
