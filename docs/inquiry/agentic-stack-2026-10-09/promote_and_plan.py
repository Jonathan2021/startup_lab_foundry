#!/usr/bin/env python3
"""Rank the cohort, promote the merged wedge and create its MVP packages."""
from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CLI = json.loads((REPO / ".foundry" / "project.json").read_text())["cli"]
RECORDS = HERE / "records.json"
VENTURE = "v-fleet-controller"


def cli(*args: str, input_path: Path | None = None) -> dict:
    command = [*CLI, *args] + (["--input", str(input_path)] if input_path else [])
    done = subprocess.run(command, capture_output=True, text=True, check=False)
    if done.returncode != 0:
        raise SystemExit(f"CLI failed: {' '.join(args)}\n{done.stderr[-1500:]}")
    return json.loads(done.stdout)


records = json.loads(RECORDS.read_text())
records.setdefault("plan", {})
if "rank" not in records["plan"]:
    rank = cli("score", "rank", "--scorecard-id", "portfolio-reviewed-v1", "--label", "agentic-stack-2026-10-09")
    records["plan"]["rank"] = {k: rank[k] for k in rank if k != "entries"}
    records["plan"]["rank"]["cohort"] = [e for e in rank.get("entries", []) if str(e.get("idea_id", "")).startswith("AS")]
    print("rank snapshot", rank.get("id") or rank.get("snapshot_id"), "entries", len(rank.get("entries", [])))
    RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False, sort_keys=True))
if "venture" not in records["plan"]:
    venture = cli("idea", "promote", "--id", "AS10", "--venture-id", VENTURE)
    records["plan"]["venture"] = venture
    print("venture", venture.get("id"), "workspace", venture.get("workspace_id"), "stage", venture.get("stage"))
    RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False, sort_keys=True))
workspace = records["plan"]["venture"]["workspace_id"]
records["plan"].setdefault("packages", {})
for key in ["C01", "C02", "C03", "C04", "C05"]:
    if key in records["plan"]["packages"]:
        continue
    payload = json.loads((HERE / "inputs" / f"work-{key}.json").read_text())
    try:
        head = cli("decision-map", "show", "--workspace-id", workspace).get("id")
    except SystemExit:
        head = None
    payload["expected_head"] = head
    path = HERE / "inputs" / f"work-{key}.resolved.json"
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    result = cli("venture-work", "create", "--workspace-id", workspace, input_path=path)
    records["plan"]["packages"][key] = {"work_id": result["id"], "version": result["work"]["version_id"], "status": result["work"]["status"], "head_before": head}
    print(key, result["id"], result["work"]["status"])
    RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False, sort_keys=True))
head = cli("decision-map", "show", "--workspace-id", workspace)
records["plan"]["map_head_after_packages"] = head.get("id")
RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False, sort_keys=True))
print("map head", head.get("id"), "nodes", len(head["map"]["nodes"]), "edges", len(head["map"]["edges"]))
