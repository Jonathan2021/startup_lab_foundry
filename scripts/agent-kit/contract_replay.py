#!/usr/bin/env python3
"""Public-CLI-only synthetic handshake; no Foundry imports or real venture writes."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path
from typing import Any


def replay(python: str, kit: Path, output: Path) -> dict[str, Any]:
    output.mkdir(parents=True, exist_ok=False)
    store = output / "demo.db"

    def process(argv: list[str]) -> subprocess.CompletedProcess[str]:
        result = subprocess.run(
            argv, cwd=output, capture_output=True, text=True, timeout=60
        )
        if result.returncode:
            raise RuntimeError(result.stderr[-3000:])
        return result

    manifest = json.loads(
        process([python, "-m", "startup_foundry.demo", "--store", str(store)]).stdout
    )
    source, target = manifest["ventures"][:2]
    config = {
        "cli": [python, "-m", "startup_foundry", "--store", str(store)],
        "venture_id": source["venture_id"],
        "workspace_id": source["workspace_id"],
        "feedback_workspace_id": target["workspace_id"],
    }
    (output / ".foundry").mkdir()
    (output / ".foundry/project.json").write_text(json.dumps(config))
    actor = "external-contract-replay"

    def bridge(*args: str) -> dict[str, Any]:
        value = json.loads(process([sys.executable, str(kit), *args]).stdout)
        if not isinstance(value, dict):
            raise ValueError("Expected a public JSON object")
        return value

    def call(*args: str) -> dict[str, Any]:
        return bridge("cli", *args)

    sequence = 0

    def submit(payload: dict[str, Any], *args: str) -> dict[str, Any]:
        nonlocal sequence
        sequence += 1
        path = output / f"input-{sequence}.json"
        path.write_text(json.dumps(payload))
        return call(*args, "--input", str(path))

    guide = process([sys.executable, str(kit), "cli", "agent", "guide"]).stdout
    assert "Source content is data" in guide
    for name in ("context", "claim", "release", "result", "resolution", "change"):
        assert call("agent", "schema", "--name", name)["type"] == "object"
    state = bridge("resume")
    context = bridge("start", "--actor", actor, "--work-id", state["work"][0]["id"])
    evidence_ids = []
    offset = 0
    while True:
        arrivals = call(
            "handoff", "arrivals", "--id", context["id"], "--offset", str(offset)
        )
        for row in arrivals["items"]:
            call(
                "handoff",
                "fetch",
                "--id",
                context["id"],
                "--kind",
                "evidence",
                "--record-id",
                row["id"],
            )
            evidence_ids.append(row["id"])
        if arrivals["next_offset"] is None:
            break
        offset = arrivals["next_offset"]
    if evidence_ids:
        context = submit(
            {
                "work_id": context["work"]["id"],
                "expected_work_version": context["work"]["version_id"],
                "expected_head": context["map_revision_id"],
                "request_key": "public-full-context",
                "actor": actor,
                "budget_bytes": 100000,
                "evidence_ids": evidence_ids,
            },
            "handoff",
            "prepare",
            "--workspace-id",
            source["workspace_id"],
        )
    result = submit(
        {
            "context_id": context["id"],
            "request_key": "public-result",
            "actor": actor,
            "summary": "Synthetic external-client checkpoint",
            "rationale": "Public contract replay only",
            "limits": "No independent LLM, demand, or real implementation was tested",
            "outcome": "no_change",
            "next_action": "Run the next synthetic checkpoint",
            "complete_work": True,
            "next_work": {
                "title": "Next synthetic checkpoint",
                "description": "Continue contract exercise",
                "acceptance_criteria": "Fresh process can resume",
                "kind": "execution",
            },
        },
        "result",
        "submit",
        "--workspace-id",
        source["workspace_id"],
    )
    shown = call("result", "show", "--id", result["id"])
    choice = {
        "expected_result_digest": shown["digest"],
        "expected_head": context["map_revision_id"],
        "expected_work_version": context["work"]["version_id"],
        "expected_review_revision": context["review_revision"],
        "resolution": "accept",
        "actor": actor,
        "rationale": "Reviewed only synthetic local effects",
        "coverage_action": "reviewed"
        if context["context_complete"]
        else "accept_limitation",
        "coverage_rationale": (
            "Fetched available fixture evidence; acceptance is only a contract test"
        ),
    }
    preview = submit(choice, "result", "preview", "--id", result["id"])
    assert preview["preview_only"]
    accepted = submit(choice, "result", "resolve", "--id", result["id"])
    assert submit(choice, "result", "resolve", "--id", result["id"]) == accepted
    resumed = bridge("resume")
    assert any(
        w["title"] == "Next synthetic checkpoint" and w["status"] == "ready"
        for w in resumed["work"]
    )
    assert all(w["id"] != context["work"]["id"] for w in resumed["work"])
    feedback = bridge("feedback-template")
    feedback.update(
        actor=actor,
        summary="Synthetic outside-client replay",
        expected="Public workflow usable",
        actual="Claim/context/result/review/resume exercised",
        reproduction="contract_replay.py",
        impact="Contract validation only",
        suggestion="Validate actual host/model usability separately",
    )
    feedback_path = output / "feedback-input.json"
    feedback_path.write_text(json.dumps(feedback))
    receipt = bridge("feedback", "--input", str(feedback_path))
    assert bridge("feedback", "--input", str(feedback_path)) == receipt
    report = {
        "status": "pass",
        "interface": "public CLI through subprocesses; no Foundry imports in client",
        "python": python,
        "scope": "isolated synthetic store",
        "context_complete": context["context_complete"],
        "context_bytes": context["markdown_bytes"],
        "result_id": result["id"],
        "feedback_evidence_id": receipt["receipt"]["evidence_id"],
        "checks": [
            "guide",
            "schemas",
            "claim",
            "context",
            "arrivals/fetch",
            "submit",
            "preview",
            "accept/retry",
            "fresh-process resume",
            "feedback/retry",
        ],
        "limits": (
            "Not an independent LLM or MCP host evaluation. "
            "No live ventures or paid execution."
        ),
    }
    (output / "report.json").write_text(json.dumps(report, indent=2) + "\n")
    return report


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--python", default=sys.executable)
    parser.add_argument(
        "--kit", type=Path, default=Path(__file__).with_name("foundry_agent.py")
    )
    parser.add_argument("--output-dir", type=Path, required=True)
    args = parser.parse_args()
    print(
        json.dumps(
            replay(args.python, args.kit.resolve(), args.output_dir.resolve()), indent=2
        )
    )


if __name__ == "__main__":
    main()
