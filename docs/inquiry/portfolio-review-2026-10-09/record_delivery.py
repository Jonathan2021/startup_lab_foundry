#!/usr/bin/env python3
"""Record a repository delivery as evidence in a venture (ADR-0020 convention).

Usage: python3 record_delivery.py <slug> <main sha> <ci run id> [--note TEXT]
Writes `Delivery: main=<sha> ci=<run>` so `doctor`/`resume` drift checks resolve.
Receipts go to deliveries.json under the venture's "delivery_evidence" key.
"""
from __future__ import annotations

import json
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CLI = json.loads((REPO / ".foundry" / "project.json").read_text())["cli"]
ACTOR = "fable-portfolio-20261009"
WORKSPACES = {
    "coopain": "9197a72d-23a6-424d-9b00-03e5d4a366f6",
    "crous-queue": "81ee3117-de70-411e-9856-07420859ffad",
    "ride-options": "6972ac19-0263-41c7-9f09-97b64fd99f80",
    "volley-match": "417476af-0674-4aba-9022-843957dc3ca2",
    "offer-check": "546ed36a-a8be-4639-b88c-1b3bcf96c7d8",
    "volley-coach": "9d0ed0f5-960b-4cd0-a52f-4176218a40e5",
    "foundry": "68afabed-a744-47df-94c1-7402f5c7b3b0",
}


def main() -> None:
    args = [a for a in sys.argv[1:] if not a.startswith("--")]
    slug, sha, run = args[0], args[1], args[2]
    note = sys.argv[sys.argv.index("--note") + 1] if "--note" in sys.argv else ""
    ws = WORKSPACES[slug]
    deliveries = HERE / "deliveries.json"
    data = json.loads(deliveries.read_text()) if deliveries.exists() else {}
    entry = data.setdefault(slug, {})
    prior = entry.get("ci", [])
    payload = {
        "request_key": f"delivery-{slug}-{sha[:7]}",
        "actor": ACTOR,
        "summary": f"Delivery: main={sha} ci={run} ({date.today().isoformat()}). {note}".strip()[:10000],
        "details": json.dumps(
            {"main": sha, "ci_run": run, "earlier_runs_this_review": prior,
             "record": f"docs/inquiry/portfolio-review-2026-10-09/{slug}/DELIVERY.md" if slug != "foundry" else "docs/inquiry/portfolio-review-2026-10-09/REPORT.md"},
            ensure_ascii=False)[:10000],
        "kind": "artifact_review",
        "epistemic_status": "observation",
        "confidence": "high",
        "sources": [f"document: docs/inquiry/portfolio-review-2026-10-09/{'REPORT.md' if slug == 'foundry' else slug + '/DELIVERY.md'}"],
        "refs": [],
    }
    path = HERE / "inputs" / f"delivery-{slug}-{sha[:7]}.json"
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n")
    out = subprocess.run([*CLI, "change", "record", "--workspace-id", ws, "--input", str(path)],
                         capture_output=True, text=True, check=True).stdout
    result = json.loads(out)
    evidence_id = result.get("evidence_id") or result.get("id")
    entry.setdefault("delivery_evidence", []).append({"main": sha, "ci": run, "evidence_id": evidence_id})
    deliveries.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n")
    print(slug, sha[:7], run, "evidence", evidence_id)


if __name__ == "__main__":
    main()
