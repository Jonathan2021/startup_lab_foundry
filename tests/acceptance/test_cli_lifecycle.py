"""Restart-per-command lifecycle replay against isolated synthetic ventures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest
from test_cli_workspace import require_success, run_foundry

from startup_foundry.demo import create_demo
from startup_foundry.errors import ConflictError


def test_lifecycle_cli_replays_and_refuses_demo_overwrite(tmp_path: Path):
    store = tmp_path / "synthetic.db"
    manifest = create_demo(store)
    with pytest.raises(ConflictError, match="NEW store"):
        create_demo(store)

    def run(*args):
        return require_success(run_foundry(store, *args))

    def submit(resource, action, payload, *, workspace=None, identity=None):
        path = tmp_path / "input.json"
        path.write_text(json.dumps(payload))
        owner = ("--workspace-id", workspace) if workspace else ("--id", identity)
        return run(resource, action, *owner, "--input", str(path))

    for entry in manifest["ventures"]:
        ws = entry["workspace_id"]
        state = run(
            "agent", "resume", "--venture-id", entry["venture_id"], "--format", "json"
        )
        original_maturity = state["current_review"]["product_maturity"]
        original_scope = state["scope"]
        old = run("result", "show", "--id", entry["result_id"])
        old_ctx = run("handoff", "show", "--id", entry["context_id"])
        if entry["venture_id"] == "demo-supplier":
            assert old["state"] == "needs_reconciliation"
            old_choice = {
                "expected_result_digest": old["digest"],
                "expected_head": old_ctx["map_revision_id"],
                "expected_work_version": old_ctx["work"]["version_id"],
                "expected_review_revision": old_ctx["review_revision"],
                "resolution": "accept",
                "actor": "operator",
                "rationale": "Try stale context",
            }
            path = tmp_path / "stale.json"
            path.write_text(json.dumps(old_choice))
            failure = run_foundry(
                store, "result", "resolve", "--id", old["id"], "--input", str(path)
            )
            assert failure.returncode != 0 and "reconciliation" in failure.stderr
        for sequence in range(2):
            state = run("agent", "resume", "--workspace-id", ws, "--format", "json")
            work = state["work"][0]
            first = run(
                "handoff",
                "prepare",
                "--workspace-id",
                ws,
                "--work-id",
                work["id"],
                "--actor",
                "replay agent",
            )
            arrivals = run("handoff", "arrivals", "--id", first["id"])
            ctx = submit(
                "handoff",
                "prepare",
                {
                    "work_id": work["id"],
                    "expected_work_version": work["version_id"],
                    "expected_head": state["map_revision_id"],
                    "request_key": "full-context-" + str(sequence),
                    "actor": "replay agent",
                    "budget_bytes": 100000,
                    "evidence_ids": [item["id"] for item in arrivals["items"]],
                },
                workspace=ws,
            )
            assert ctx["context_complete"]
            proposal = {
                "context_id": ctx["id"],
                "request_key": "replay-" + str(sequence),
                "actor": "replay agent",
                "summary": "Retain the bounded uncertainty",
                "rationale": "Review all available synthetic facts",
                "limits": "No real evidence; coordination test only",
                "outcome": "hold",
                "next_action": "Revisit after independent observations",
                "revisit_trigger": "New reliable evidence",
            }
            if entry["venture_id"] == "demo-supplier" and sequence == 0:
                proposal.update(
                    supersedes_result_id=old["id"],
                    reconciliation_rationale="Correction changes the conclusion",
                )
            result = submit("result", "submit", proposal, workspace=ws)
            choice = {
                "expected_result_digest": result["digest"],
                "expected_head": ctx["map_revision_id"],
                "expected_work_version": ctx["work"]["version_id"],
                "expected_review_revision": ctx["review_revision"],
                "resolution": "accept",
                "actor": "operator",
                "rationale": "Reviewed the synthetic evidence and limits",
            }
            preview = submit("result", "preview", choice, identity=result["id"])
            assert preview["preview_only"]
            accepted = submit("result", "resolve", choice, identity=result["id"])
            assert (
                submit("result", "resolve", choice, identity=result["id"]) == accepted
            )
            resumed = run("agent", "resume", "--workspace-id", ws, "--format", "json")
            assert resumed["current_review"]["product_maturity"] == original_maturity
            assert resumed["scope"] == original_scope
            assert resumed["unreviewed_change_count"] == 0
            if sequence == 0:
                submit(
                    "venture-work",
                    "create",
                    {
                        "expected_head": resumed["map_revision_id"],
                        "request_key": "follow-up",
                        "actor": "operator",
                        "rationale": "A later operating event requires a new decision",
                        "work": {
                            "title": "Review the later change",
                            "description": "Compare the new fact with prior reasoning",
                            "acceptance_criteria": "Record changes and unknowns",
                            "owner": "agent",
                        },
                    },
                    workspace=ws,
                )
                submit(
                    "change",
                    "record",
                    {
                        "request_key": "later-change",
                        "actor": "fixture",
                        "summary": "Synthetic correction contradicts the fixture",
                        "sources": ["observation: synthetic replay event"],
                    },
                    workspace=ws,
                )


def test_storage_info_does_not_create_or_migrate_a_store(tmp_path):
    store = tmp_path / "not-created.db"
    require_success(run_foundry(store, "storage", "info"))
    assert not store.exists()
