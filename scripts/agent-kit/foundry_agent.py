#!/usr/bin/env python3
"""Standalone repository-side CLI bridge. No Foundry Python imports or model calls."""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
import tempfile
from pathlib import Path
from typing import Any
from uuid import uuid4


def write_new(path: Path, value: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("x", encoding="utf-8") as out:
        json.dump(value, out, ensure_ascii=False, indent=2)
        out.write("\n")


def invoke(config: dict[str, Any], *args: str) -> dict[str, Any]:
    argv = config["cli"]
    if (
        not isinstance(argv, list)
        or not argv
        or not all(isinstance(x, str) for x in argv)
    ):
        raise ValueError("project.json cli must be a nonempty argv array")
    completed = subprocess.run(
        [*argv, *args], capture_output=True, text=True, timeout=60
    )
    if completed.returncode:
        raise RuntimeError(completed.stderr.strip()[-2000:] or "Foundry command failed")
    value = json.loads(completed.stdout)
    if not isinstance(value, dict):
        raise ValueError("Foundry returned an unexpected response")
    return value


def submit(
    config: dict[str, Any], payload: dict[str, Any], *args: str
) -> dict[str, Any]:
    with tempfile.TemporaryDirectory(prefix="foundry-input-") as folder:
        path = Path(folder) / "input.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return invoke(config, *args, "--input", str(path))


def start_work(
    config: dict[str, Any], actor: str, work_id: str | None, budget: int
) -> dict[str, Any]:
    workspace = config["workspace_id"]
    state = invoke(
        config, "agent", "resume", "--workspace-id", workspace, "--format", "json"
    )
    review = state.get("current_review") or {}
    selected = work_id or review.get("next_work_item_id")
    work = next((w for w in state["work"] if w["id"] == selected), None)
    if work is None:
        raise ValueError("No current next work; review Foundry and choose --work-id")
    if not state["map_revision_id"]:
        raise ValueError("Create and review a decision map before starting work")
    claimed = submit(
        config,
        {"expected_version": work["version_id"], "actor": actor},
        "handoff",
        "claim",
        "--workspace-id",
        workspace,
        "--work-id",
        work["id"],
    )
    try:
        return submit(
            config,
            {
                "work_id": work["id"],
                "expected_work_version": claimed["version_id"],
                "expected_head": state["map_revision_id"],
                "request_key": "start:" + str(uuid4()),
                "actor": actor,
                "budget_bytes": budget,
            },
            "handoff",
            "prepare",
            "--workspace-id",
            workspace,
        )
    except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired):
        # Preparation has no work effects. Release only our exact, unchanged claim.
        submit(
            config,
            {
                "expected_version": claimed["version_id"],
                "actor": actor,
                "rationale": "Context preparation failed; release this exact claim",
            },
            "handoff",
            "release",
            "--workspace-id",
            workspace,
            "--work-id",
            work["id"],
        )
        raise


def send_feedback(config: dict[str, Any], report: dict[str, Any]) -> dict[str, Any]:
    required = {
        "id",
        "venture_id",
        "workspace_id",
        "actor",
        "kind",
        "summary",
        "expected",
        "actual",
        "reproduction",
        "impact",
        "suggestion",
        "sources",
    }
    if not required <= report.keys():
        raise ValueError(
            "Feedback is missing: " + ", ".join(sorted(required - report.keys()))
        )
    if (
        report["venture_id"] != config["venture_id"]
        or report["workspace_id"] != config["workspace_id"]
    ):
        raise ValueError("Feedback belongs to another project; use its configuration")
    if report["kind"] not in {"bug", "friction", "idea", "positive"}:
        raise ValueError("Feedback kind must be bug, friction, idea or positive")
    if not all(
        isinstance(report[k], str) and report[k].strip() for k in required - {"sources"}
    ):
        raise ValueError("Feedback text fields must be nonempty strings")
    if not isinstance(report["sources"], list) or not all(
        isinstance(s, str) for s in report["sources"]
    ):
        raise ValueError("sources must be a list of source locators")
    payload = {
        "request_key": "dogfood:" + report["id"],
        "actor": report["actor"],
        "summary": "[Dogfood/" + report["kind"] + "] " + report["summary"],
        "details": json.dumps(report, ensure_ascii=False, sort_keys=True),
        "epistemic_status": "inference" if report["kind"] == "idea" else "observation",
        "sources": ["document: feedback/" + report["id"] + ".json"],
        "confidence": "low",
    }
    with tempfile.TemporaryDirectory(prefix="foundry-feedback-") as folder:
        path = Path(folder) / "input.json"
        path.write_text(json.dumps(payload), encoding="utf-8")
        return invoke(
            config,
            "change",
            "record",
            "--workspace-id",
            config["feedback_workspace_id"],
            "--input",
            str(path),
        )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", default=".foundry/project.json")
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("resume")
    start = commands.add_parser("start", help="Claim current work and prepare context")
    start.add_argument("--actor", required=True)
    start.add_argument("--work-id")
    start.add_argument("--budget-bytes", type=int, default=24000)
    commands.add_parser("feedback-template")
    feedback = commands.add_parser(
        "feedback", help="Retain and send one sanitized feedback report"
    )
    feedback.add_argument("--input", required=True)
    args = parser.parse_args()
    try:
        config_path = Path(args.config).resolve()
        config = json.loads(config_path.read_text())
        if args.command == "resume":
            result = invoke(
                config,
                "agent",
                "resume",
                "--workspace-id",
                config["workspace_id"],
                "--format",
                "json",
            )
        elif args.command == "start":
            result = start_work(config, args.actor, args.work_id, args.budget_bytes)
            path = config_path.parent / "runs" / (result["id"] + ".json")
            write_new(path, result)
            result = {"saved_context": str(path), **result}
        elif args.command == "feedback-template":
            result = {
                key: "Describe " + key
                for key in [
                    "actor",
                    "summary",
                    "expected",
                    "actual",
                    "reproduction",
                    "impact",
                    "suggestion",
                ]
            }
            result.update(
                id=str(uuid4()),
                venture_id=config["venture_id"],
                workspace_id=config["workspace_id"],
                kind="friction",
                sources=[],
            )
        else:
            report = json.loads(Path(args.input).read_text())
            # Durable outbox first; sync retry uses the same request key and bytes.
            identity = report.get("id", "")
            from uuid import UUID

            UUID(identity)
            destination = config_path.parent.parent / "feedback" / (identity + ".json")
            if destination.exists():
                if json.loads(destination.read_text()) != report:
                    raise ValueError(
                        "An existing feedback ID has different content; issue a new ID"
                    )
            else:
                write_new(destination, report)
            result = send_feedback(config, report)
            receipt = destination.with_suffix(".receipt.json")
            if not receipt.exists():
                write_new(receipt, result)
            result = {"feedback_file": str(destination), "receipt": result}
        print(json.dumps(result, ensure_ascii=False, indent=2))
        return 0
    except (
        OSError,
        ValueError,
        KeyError,
        RuntimeError,
        subprocess.TimeoutExpired,
    ) as exc:
        print(
            "Foundry bridge: "
            + str(exc)
            + "\nRetained feedback without a receipt can be retried "
            "with the same --input. Do not bypass claims or edit the database.",
            file=sys.stderr,
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
