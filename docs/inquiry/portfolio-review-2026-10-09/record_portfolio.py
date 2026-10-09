#!/usr/bin/env python3
"""Record portfolio-review outcomes into Foundry through the public CLI.

Usage: python3 record_portfolio.py <phase> <slug>... [--dry-run]
Phases: evidence | scores | reviews | packages
Each venture's REVIEW.md ends with a JSON block produced by its review agent.
Receipts accumulate in records.json next to this file. Idempotent request keys.
"""
from __future__ import annotations

import json
import re
import subprocess
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
REPO = HERE.parents[2]
CLI = json.loads((REPO / ".foundry" / "project.json").read_text())["cli"]
ACTOR = "fable-portfolio-20261009"
TODAY = date.today().isoformat()
RECORDS = HERE / "records.json"
VENTURES = {
    "coopain": ("v-coopain", "9197a72d-23a6-424d-9b00-03e5d4a366f6"),
    "crous-queue": ("f0b5abfe-0274-42f7-9c9a-72dcbe68c116", "81ee3117-de70-411e-9856-07420859ffad"),
    "ride-options": ("v-route-repair", "6972ac19-0263-41c7-9f09-97b64fd99f80"),
    "volley-match": ("v-sports-session", "417476af-0674-4aba-9022-843957dc3ca2"),
    "offer-check": ("v-offer-check", "546ed36a-a8be-4639-b88c-1b3bcf96c7d8"),
    "volley-coach": ("v-volley-coach", "9d0ed0f5-960b-4cd0-a52f-4176218a40e5"),
}
DISPOSITION = {"GO": "pursue", "NARROW": "pursue", "HOLD": "hold", "STOP": "dropped"}


def cli(*args: str, input_path: Path | None = None) -> dict:
    cmd = [*CLI, *args] + (["--input", str(input_path)] if input_path else [])
    done = subprocess.run(cmd, capture_output=True, text=True, check=False)
    if done.returncode:
        raise SystemExit(f"CLI failed: {' '.join(args)}\n{done.stderr[-1500:]}")
    return json.loads(done.stdout)


def load() -> dict:
    return json.loads(RECORDS.read_text()) if RECORDS.exists() else {}


def save(records: dict) -> None:
    RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False, sort_keys=True))


def review_block(slug: str) -> dict:
    """Reviewer JSON block merged with the coordinator's decisions.json overrides."""
    text = (HERE / slug / "REVIEW.md").read_text()
    blocks = re.findall(r"```json\s*(.*?)```", text, flags=re.S)
    if not blocks:
        raise SystemExit(f"{slug}: REVIEW.md has no JSON block")
    block = json.loads(blocks[-1])
    decisions = json.loads((HERE / "decisions.json").read_text()) if (HERE / "decisions.json").exists() else {}
    block.update(decisions.get(slug, {}))
    return block


def write_input(name: str, payload: dict) -> Path:
    path = HERE / "inputs" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return path


def phase_evidence(slug: str, dry: bool) -> None:
    venture, ws = VENTURES[slug]
    block = review_block(slug)
    records = load(); records.setdefault("evidence", {})
    findings = block.get("code_findings") or []
    summary = (
        f"Portfolio review {TODAY}: recommendation {block['recommendation']} "
        f"(confidence {block.get('confidence')}); score change {block.get('score_change')}; "
        f"{len(block.get('packages', []))} proposed packages; blockers: {', '.join(block.get('blockers') or []) or 'none'}. "
        f"Full review: docs/inquiry/portfolio-review-2026-10-09/{slug}/REVIEW.md"
    )
    payload = {
        "request_key": f"portfolio-review-{slug}-{TODAY}",
        "actor": ACTOR,
        "summary": summary[:10000],
        "details": json.dumps({k: block.get(k) for k in ("recommendation", "confidence", "score_change", "blockers", "packages", "feedback_ids")}, ensure_ascii=False)[:10000],
        "kind": "artifact_review",
        "epistemic_status": "observation",
        "confidence": block.get("confidence", "low") if block.get("confidence") in ("low", "medium", "high") else "low",
        "sources": [f"document: docs/inquiry/portfolio-review-2026-10-09/{slug}/REVIEW.md"],
        "refs": [],
    }
    path = write_input(f"evidence-{slug}.json", payload)
    if dry:
        print(slug, "would record evidence"); return
    result = cli("change", "record", "--workspace-id", ws, input_path=path)
    records["evidence"][slug] = {"evidence_id": result.get("evidence_id") or result.get("id"), "raw": result}
    save(records); print(slug, "evidence", records["evidence"][slug]["evidence_id"])


def phase_scores(slug: str, dry: bool) -> None:
    venture, ws = VENTURES[slug]
    block = review_block(slug)
    records = load(); records.setdefault("assessments", {})
    shown = cli("venture-score", "show", "--id", venture)
    evidence_id = records.get("evidence", {}).get(slug, {}).get("evidence_id")
    payload = {
        "venture_id": venture,
        "scorecard_id": "portfolio-reviewed-v1",
        "expected_sequence": shown.get("expected_sequence") or 0,
        "request_key": f"portfolio-review-score-{slug}-{TODAY}",
        "scores": block["scores"],
        "rationale": (block.get("score_rationale") or f"Portfolio review {TODAY}; see docs/inquiry/portfolio-review-2026-10-09/{slug}/REVIEW.md section 4.")[:20000],
        "author": f"agent:{ACTOR}",
        "confidence": block.get("confidence", "low") if block.get("confidence") in ("low", "medium", "high") else "low",
        "criterion_rationales": block.get("criterion_rationales") or {},
        "evidence_ids": {k: [evidence_id] for k in ("competition", "moat") if evidence_id},
    }
    path = write_input(f"score-{slug}.json", payload)
    if dry:
        print(slug, "would assess; expected_sequence", payload["expected_sequence"], "current total", (shown.get("current") or {}).get("total")); return
    result = cli("venture-score", "assess", input_path=path)
    records["assessments"][slug] = result
    save(records); print(slug, "assessment total", result.get("total") or (result.get("current") or {}).get("total"), "| previous", (shown.get("current") or {}).get("total"))


def phase_reviews(slug: str, dry: bool) -> None:
    venture, ws = VENTURES[slug]
    block = review_block(slug)
    records = load(); records.setdefault("reviews", {})
    current = cli("review", "show", "--workspace-id", ws).get("current") or {}
    payload = {
        "workspace_id": ws,
        "expected_revision": current.get("revision", 0),
        "investigation_stage": block.get("investigation_stage") or current.get("investigation_stage") or "solution_validation",
        "product_maturity": block.get("product_maturity") or current.get("product_maturity") or "concept",
        "disposition": DISPOSITION[block["recommendation"]],
        "next_action": block.get("next_action") or f"See portfolio review {TODAY}.",
        "reason": (block.get("reason") or f"Portfolio review {TODAY}: {block['recommendation']}. docs/inquiry/portfolio-review-2026-10-09/{slug}/REVIEW.md")[:20000],
        "author": f"agent:{ACTOR}",
    }
    path = write_input(f"review-{slug}.json", payload)
    if dry:
        print(slug, "would review ->", payload["disposition"], "| expected_revision", payload["expected_revision"]); return
    result = cli("review", "append", input_path=path)
    records["reviews"][slug] = result
    save(records); print(slug, "review ->", payload["disposition"], "revision", result.get("revision") or (result.get("current") or {}).get("revision"))


def phase_packages(slug: str, dry: bool) -> None:
    venture, ws = VENTURES[slug]
    block = review_block(slug)
    records = load(); records.setdefault("packages", {}).setdefault(slug, {})
    selection = block.get("packages_selection") or {}
    if isinstance(block.get("packages"), dict):  # decisions.json override: {id: status}
        selection, block["packages"] = block["packages"], json.loads(re.findall(r"```json\s*(.*?)```", (HERE / slug / "REVIEW.md").read_text(), flags=re.S)[-1]).get("packages", [])
    for i, pkg in enumerate(block.get("packages") or []):
        key = pkg["id"]
        if selection and key not in selection:
            continue
        if key in records["packages"][slug]:
            continue
        chosen = selection.get(key, "ready" if i == 0 else "todo")
        status, _, blocked_reason = chosen.partition(":")
        try:
            head = cli("decision-map", "show", "--workspace-id", ws).get("id")
        except SystemExit:
            head = None
        payload = {
            "request_key": f"portfolio-{slug}-{key}-{TODAY}",
            "actor": ACTOR,
            "rationale": f"Portfolio review {TODAY} package {key}; see docs/inquiry/portfolio-review-2026-10-09/{slug}/REVIEW.md section 6.",
            "expected_head": head,
            "work": {
                "title": f"{key} — {pkg['title']}"[:300],
                "description": (pkg.get("description") or pkg["title"])[:10000],
                "acceptance_criteria": (pkg.get("acceptance") or "See REVIEW.md")[:10000],
                "kind": "execution",
                "owner": "agent",
                "status": status,
                "blocked_reason": blocked_reason or None,
            },
        }
        path = write_input(f"work-{slug}-{key}.json", payload)
        if dry:
            print(slug, key, "would create", payload["work"]["status"]); continue
        result = cli("venture-work", "create", "--workspace-id", ws, input_path=path)
        records["packages"][slug][key] = {"work_id": result["id"], "status": result["work"]["status"], "size": pkg.get("size"), "effort": pkg.get("effort"), "depends_on": pkg.get("depends_on", [])}
        save(records); print(slug, key, result["id"], result["work"]["status"])


if __name__ == "__main__":
    phases = {"evidence": phase_evidence, "scores": phase_scores, "reviews": phase_reviews, "packages": phase_packages}
    args = [a for a in sys.argv[1:] if a != "--dry-run"]
    if len(args) < 2 or args[0] not in phases:
        raise SystemExit(__doc__)
    for slug in args[1:]:
        phases[args[0]](slug, "--dry-run" in sys.argv)
