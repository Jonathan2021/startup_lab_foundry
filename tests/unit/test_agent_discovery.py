"""Contracts derived from OfferCheck, Coach and interrupted Coopain handoffs."""

import json
import runpy
import subprocess
from pathlib import Path

import pytest
from pydantic import ValidationError

from startup_foundry import cli
from startup_foundry.decision_contracts import MapEdge, ResultInput

KIT = Path(__file__).resolve().parents[2] / "scripts/agent-kit/foundry_agent.py"


@pytest.mark.parametrize("action", [["guide"], ["schema", "--name", "result"]])
def test_static_discovery_never_initializes_storage(
    tmp_path, monkeypatch, capsys, action
):
    def forbidden(*args, **kwargs):
        raise AssertionError("Static discovery touched database configuration")

    monkeypatch.setattr(cli, "get_settings", forbidden)
    store = tmp_path / "missing.db"
    assert cli.main(["--store", str(store), "agent", *action]) == 0
    assert not store.exists()
    output = capsys.readouterr().out
    if action[0] == "schema":
        assert json.loads(output)["x-foundry-agent-contract"] == "2026-10-11.1"
    else:
        assert "final resolve receipt" in output


def test_public_branch_schema_exposes_runtime_condition():
    schema = ResultInput.model_json_schema()["$defs"]["MapEdge"]
    branch = schema["allOf"][0]
    assert branch["if"]["properties"]["kind"]["const"] == "may_lead_to"
    assert set(branch["then"]["required"]) == {"condition", "outcome"}
    assert branch["then"]["properties"]["condition"]["pattern"] == r"\S"
    assert branch["then"]["properties"]["outcome"]["type"] == "string"
    for fields in [
        {},
        {"condition": "   ", "outcome": "supported"},
        {"condition": "yes"},
    ]:
        with pytest.raises(ValidationError):
            MapEdge(source="a", target="b", kind="may_lead_to", **fields)
    MapEdge(source="a", target="b", kind="contributes_to")
    MapEdge(
        source="a", target="b", kind="may_lead_to", condition="yes", outcome="supported"
    )


def test_same_owner_recovery_prepares_without_claim_or_release(monkeypatch):
    start = runpy.run_path(str(KIT))["start_work"]
    work = {"id": "w", "version_id": 4, "owner": "same", "status": "in_progress"}
    state = {
        "work": [work],
        "current_review": {"next_work_item_id": "w"},
        "map_revision_id": "m",
    }
    monkeypatch.setitem(start.__globals__, "invoke", lambda *args: state)
    calls = []

    def prepare(config, payload, *args):
        calls.append((payload, args))
        assert args[:2] == ("handoff", "prepare")
        raise RuntimeError("Context exceeds budget")

    monkeypatch.setitem(start.__globals__, "submit", prepare)
    with pytest.raises(RuntimeError, match="budget"):
        start({"workspace_id": "s"}, "same", None, 24000, resume_owned=True)
    assert len(calls) == 1
    assert calls[0][0]["expected_work_version"] == 4
    with pytest.raises(ValueError, match="owner"):
        start({"workspace_id": "s"}, "other", None, 24000, resume_owned=True)
    assert len(calls) == 1


def test_bridge_timeout_is_bounded_and_does_not_retry_mutations(monkeypatch):
    invoke = runpy.run_path(str(KIT))["invoke"]
    monkeypatch.setitem(
        invoke.__globals__, "cli_argv", lambda *args, **kwargs: ["foundry"]
    )
    calls = []

    def timeout(argv, **kwargs):
        calls.append(kwargs["timeout"])
        raise subprocess.TimeoutExpired(argv, kwargs["timeout"])

    monkeypatch.setattr(subprocess, "run", timeout)
    with pytest.raises(RuntimeError, match="outcome may be unknown"):
        invoke({"timeout_seconds": 90}, "result", "resolve")
    assert calls == [90]
    with pytest.raises(ValueError, match="timeout"):
        invoke({"timeout_seconds": 0}, "agent", "resume")
    assert calls == [90]


@pytest.mark.parametrize(
    ("name", "required"),
    [
        ("source", {"kind", "title", "locator"}),
        ("market_actor_link", {"relation", "note", "checked_on"}),
        ("idea_revision", {"change_reason", "authored_by"}),
        ("idea_relation", {"source_idea_id", "target_idea_id", "kind", "rationale"}),
        ("idea_create", {"title", "description"}),
    ],
)
def test_discovery_inputs_are_published_in_the_agent_schema_registry(
    tmp_path, capsys, name, required
):
    store = tmp_path / "missing.db"
    assert cli.main(["--store", str(store), "agent", "schema", "--name", name]) == 0
    schema = json.loads(capsys.readouterr().out)
    assert schema["x-foundry-agent-contract"] == "2026-10-11.1"
    assert set(schema["required"]) == required
    assert schema["additionalProperties"] is False
    assert not store.exists()
    assert cli.main(["agent", "guide"]) == 0
    assert "`" + name + "`" in capsys.readouterr().out


def test_start_budget_retry_preserves_claim_and_never_retries_other_errors(monkeypatch):
    start = runpy.run_path(str(KIT))["start_work"]
    state = {
        "work": [{"id": "w", "version_id": 1, "status": "ready", "owner": "agent"}],
        "current_review": {"next_work_item_id": "w"},
        "map_revision_id": "m",
    }
    monkeypatch.setitem(start.__globals__, "invoke", lambda *args: state)
    calls = []

    def submit(config, payload, *args):
        calls.append((dict(payload), args))
        if args[1] == "claim":
            return {"version_id": 2}
        if args[1] == "release":
            return {}
        if payload["budget_bytes"] == 24000:
            raise RuntimeError(
                "Required context is 51222 bytes; budget is 24000. "
                "Nothing was silently dropped."
            )
        return {"id": "ctx"}

    monkeypatch.setitem(start.__globals__, "submit", submit)
    result = start({"workspace_id": "s"}, "same", None, 24000)
    assert [a[1] for _, a in calls] == ["claim", "prepare", "prepare"]
    assert calls[1][0]["request_key"] == calls[2][0]["request_key"]
    assert calls[2][0]["expected_work_version"] == 2
    assert result["budget_retry"] == {"requested_bytes": 24000, "used_bytes": 51222}
    calls.clear()

    def fail(config, payload, *args):
        calls.append(args[1])
        if args[1] == "claim":
            return {"version_id": 2}
        if args[1] == "release":
            return {}
        raise RuntimeError("Unknown mutation outcome; timeout")

    monkeypatch.setitem(start.__globals__, "submit", fail)
    with pytest.raises(RuntimeError, match="timeout"):
        start({"workspace_id": "s"}, "same", None, 24000)
    assert calls == ["claim", "prepare", "release"]

    calls.clear()

    def too_large(config, payload, *args):
        calls.append(args[1])
        if args[1] == "claim":
            return {"version_id": 2}
        if args[1] == "release":
            return {}
        raise RuntimeError("Required context is 100001 bytes; budget is 24000.")

    monkeypatch.setitem(start.__globals__, "submit", too_large)
    with pytest.raises(RuntimeError, match="100001"):
        start({"workspace_id": "s"}, "same", None, 24000)
    assert calls == ["claim", "prepare", "release"]


def test_doctor_detects_git_ignored_feedback_with_real_git(tmp_path):
    status = runpy.run_path(str(KIT))["feedback_outbox_status"]
    subprocess.run(["git", "init", str(tmp_path)], capture_output=True, check=True)
    (tmp_path / ".gitignore").write_text("feedback/\n")
    assert status(tmp_path)["git_ignored"] is True
    assert "Git-ignored" in status(tmp_path)["warning"]
    (tmp_path / ".gitignore").write_text("")
    assert status(tmp_path)["git_ignored"] is False


def test_change_schema_explains_sources_and_revision_schema_has_numeric_bound():
    from startup_foundry.decision_contracts import CaptureInput
    from startup_foundry.discovery_records import IdeaRevisionInput

    schema = CaptureInput.model_json_schema()
    assert "observation:" in schema["properties"]["sources"]["description"]
    assert "inference or unknown" in schema["properties"]["sources"]["description"]
    bounds = IdeaRevisionInput.model_json_schema()["properties"]["estimated_mvp_weeks"][
        "anyOf"
    ][0]
    assert bounds["exclusiveMinimum"] == 0 and bounds["maximum"] == 520
    with pytest.raises(ValidationError):
        IdeaRevisionInput(
            change_reason="Already built", authored_by="agent", estimated_mvp_weeks=0
        )
