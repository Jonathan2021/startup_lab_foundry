#!/usr/bin/env python3
"""Record the agentic-stack discovery loop into Foundry through the public CLI.

Phases (each idempotent through request keys / stable identities):
  evidence  -> one market_research evidence per idea from research/R*.md JSON blocks
  sources   -> register the transcript and each research file as sources (needs
               `source register`, added by package F02)
  actors    -> market-actor registration and idea links (needs `market-actor` and
               `idea link-actor`, added by package F02)
  scores    -> `score assess` per idea from scores.json with evidence IDs attached

Usage: python3 record_discovery.py <phase> [--dry-run]
Reads/writes records.json next to this file to retain every returned identifier.
No model, network or external action is involved; the CLI is the configured one
from .foundry/project.json.
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
PROJECT = json.loads((REPO / ".foundry" / "project.json").read_text())
CLI = PROJECT["cli"]
ACTOR = "fable-agentic-stack-20261009"
TODAY = date.today().isoformat()
RECORDS = HERE / "records.json"
IDEAS = [f"AS0{i}" for i in range(1, 10)]
MERGED = "AS10"
MERGED_PARENTS = ["AS01", "AS08", "AS03", "AS05"]
ALL_IDEAS = IDEAS + [MERGED]
TRANSCRIPT = REPO / "idea_queue" / "agentic_stack_ideas.md"


def cli(*args: str, input_path: Path | None = None) -> dict:
    command = [*CLI, *args]
    if input_path is not None:
        command += ["--input", str(input_path)]
    completed = subprocess.run(command, capture_output=True, text=True, check=False)
    if completed.returncode != 0:
        raise SystemExit(
            f"CLI failed ({completed.returncode}): {' '.join(args)}\n{completed.stderr[-2000:]}"
        )
    return json.loads(completed.stdout)


def load_records() -> dict:
    return json.loads(RECORDS.read_text()) if RECORDS.exists() else {}


def save_records(records: dict) -> None:
    RECORDS.write_text(json.dumps(records, indent=2, ensure_ascii=False, sort_keys=True))


def research_actors() -> list[dict]:
    """Parse the trailing ```json block of each research/R*.md file."""
    actors: list[dict] = []
    for path in sorted((HERE / "research").glob("R*.md")):
        text = path.read_text()
        blocks = re.findall(r"```json\s*(.*?)```", text, flags=re.S)
        if not blocks:
            print(f"warning: no JSON block in {path.name}", file=sys.stderr)
            continue
        try:
            data = json.loads(blocks[-1])
        except json.JSONDecodeError as exc:
            print(f"warning: invalid JSON in {path.name}: {exc}", file=sys.stderr)
            continue
        items = data if isinstance(data, list) else data.get("actors", [])
        for item in items:
            item.setdefault("checked_on", TODAY)
            item["research_file"] = path.name
            actors.append(item)
    return actors


def actors_for(idea: str, actors: list[dict]) -> list[tuple[dict, dict]]:
    """Actors related to an idea; the merged wedge inherits its parents' actors."""
    wanted = set(MERGED_PARENTS) if idea == MERGED else {idea}
    pairs: dict[tuple[str, str], tuple[dict, dict]] = {}
    for actor in actors:
        for rel in actor.get("relations", []):
            if rel.get("idea") in wanted:
                key = (actor["name"], rel["relation"])
                if key in pairs:
                    continue
                note = rel.get("note", "")
                if idea == MERGED:
                    note = f"[inherited from {rel['idea']}] {note}"
                pairs[key] = (actor, {**rel, "note": note})
    return list(pairs.values())


def write_json(name: str, payload: dict) -> Path:
    path = HERE / "inputs" / name
    path.parent.mkdir(exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False))
    return path


def idea_workspace(idea: str) -> str:
    return cli("idea", "show", "--id", idea)["workspace_id"]


def idea_exists(idea: str) -> bool:
    completed = subprocess.run([*CLI, "idea", "show", "--id", idea], capture_output=True, text=True, check=False)
    return completed.returncode == 0


def phase_merge(dry: bool) -> None:
    """Create the merged wedge AS10, link sources, record relations, narrow AS04."""
    records = load_records()
    records.setdefault("merge", {})
    inputs = HERE / "inputs"
    source_ids = [v["source_id"] for v in records.get("sources", {}).values() if v.get("source_id")]
    if dry:
        print("would create AS10 with", len(source_ids), "sources; 6 relations; revise AS04")
        return
    if not idea_exists(MERGED):
        payload = json.loads((inputs / "idea-AS10.json").read_text())
        payload["source_ids"] = source_ids
        payload["source_role"] = "inspiration"
        payload["source_note"] = "Merged after competition passes R1–R5; see REPORT.md"
        path = write_json("idea-AS10.resolved.json", payload)
        records["merge"]["AS10"] = cli("idea", "create", input_path=path)
        print("created AS10")
    for path in sorted(inputs.glob("relation-*.json")):
        if path.name.endswith(".resolved.json"):
            continue
        result = cli("idea", "relate", input_path=path)
        records["merge"][path.stem] = result
        print("relation", path.stem, "created" if result.get("created") else "existing")
    current = cli("idea", "show", "--id", "AS04")
    if current.get("revision", 1) == 1:
        payload = json.loads((inputs / "revise-AS04.json").read_text())
        payload["expected_revision_id"] = current["revision_id"]
        path = write_json("revise-AS04.resolved.json", payload)
        records["merge"]["AS04-revision"] = cli("idea", "revise", "--id", "AS04", input_path=path)["receipt"]
        print("revised AS04 ->", records["merge"]["AS04-revision"]["revision_number"])
    save_records(records)


def phase_reviews(dry: bool) -> None:
    """Record disposition reviews (pursue/hold/dropped/use_existing/internal_only)."""
    records = load_records()
    records.setdefault("reviews", {})
    scores = json.loads((HERE / "scores.json").read_text())
    stage = {"AS10": "comparison", "AS02": "comparison", "AS04": "comparison"}
    dispo = {"AS10": "pursue", "AS02": "hold", "AS04": "internal_only", "AS07": "use_existing",
             "AS01": "dropped", "AS03": "dropped", "AS05": "dropped", "AS06": "dropped", "AS08": "dropped", "AS09": "dropped"}
    for idea in ALL_IDEAS:
        if idea == MERGED and not idea_exists(idea):
            continue
        shown = cli("idea", "show", "--id", idea)
        review = shown.get("review") or {}
        current = review.get("current") or {}
        payload = {
            "workspace_id": shown["workspace_id"],
            "expected_revision": current.get("revision", 0) if current else 0,
            "investigation_stage": stage.get(idea, "triage"),
            "product_maturity": "concept",
            "disposition": dispo[idea],
            "next_action": scores[idea]["recommendation"],
            "reason": scores[idea]["rationale"][:20000],
            "author": f"agent:{ACTOR}",
        }
        path = write_json(f"review-{idea}.json", payload)
        if dry:
            print(idea, "would review ->", dispo[idea])
            continue
        records["reviews"][idea] = cli("review", "append", input_path=path)
        print(idea, "reviewed ->", dispo[idea])
        save_records(records)


def phase_evidence(dry: bool) -> None:
    records = load_records()
    actors = research_actors()
    records.setdefault("evidence", {})
    for idea in ALL_IDEAS:
        if idea == MERGED and not idea_exists(idea):
            print(f"{idea}: not created yet; skipping evidence")
            continue
        pairs = actors_for(idea, actors)
        if not pairs:
            print(f"{idea}: no actors mapped; skipping evidence")
            continue
        lines = []
        sources: list[str] = []
        for actor, rel in pairs:
            lines.append(
                f"- {actor['name']} [{rel['relation']}]: {actor.get('description','').strip()[:300]}"
                f" Gap/note: {rel.get('note','').strip()[:400]}"
                f" Traction: {actor.get('traction','n/a')[:160]} ({actor.get('traction_source','')})."
                f" Licence: {actor.get('license','n/a')[:80]}. Checked {actor.get('checked_on')}."
            )
            for url in (actor.get("website"), actor.get("traction_source")):
                if url and url.startswith("http") and url not in sources and len(sources) < 20:
                    sources.append(url)
        files = sorted({a["research_file"] for a, _ in pairs})
        summary = (
            f"Competition check {TODAY} for {idea}: {len(pairs)} market actors recorded "
            f"({sum(1 for _, r in pairs if r['relation']=='competitor')} competitors, "
            f"{sum(1 for _, r in pairs if r['relation']=='alternative')} alternatives); "
            f"details list what each does, its traction signal, licence and the gap versus the candidate. "
            f"Source files: {', '.join(files)} under docs/inquiry/agentic-stack-2026-10-09/research/."
        )
        payload = {
            "request_key": f"agentic-stack-{idea}-competition-{TODAY}",
            "actor": ACTOR,
            "summary": summary[:10000],
            "details": "\n".join(lines)[:10000],
            "kind": "market_research",
            "epistemic_status": "observation",
            "confidence": "medium",
            "sources": sources,
            "refs": [],
        }
        path = write_json(f"evidence-{idea}.json", payload)
        if dry:
            print(f"{idea}: would record evidence from {len(pairs)} actors ({path.name})")
            continue
        result = cli("change", "record", "--workspace-id", idea_workspace(idea), input_path=path)
        evidence_id = result.get("evidence_id") or result.get("id") or result.get("evidence", {}).get("id")
        records["evidence"][idea] = {"evidence_id": evidence_id, "raw": result}
        print(f"{idea}: evidence {evidence_id}")
        save_records(records)


def phase_sources(dry: bool) -> None:
    records = load_records()
    records.setdefault("sources", {})
    specs = [
        (
            "transcript",
            {
                "kind": "document",
                "title": "Agentic stack ideas — user conversation transcript (idea_queue/agentic_stack_ideas.md)",
                "locator": str(TRANSCRIPT),
                "publisher": "user-supplied conversation with another agent",
                "notes": "Source material and hypotheses; facts inside are unverified claims until checked. Four prompt/response pairs about adaptive multi-provider orchestration, specialist factories, portability, research OS and an adaptive AI OS.",
                "idea_ids": IDEAS,
                "role": "inspiration",
            },
        )
    ]
    for path in sorted((HERE / "research").glob("R*.md")):
        actors = [a for a in research_actors() if a["research_file"] == path.name]
        ideas = sorted({r["idea"] for a in actors for r in a.get("relations", [])})
        specs.append(
            (
                path.stem,
                {
                    "kind": "report",
                    "title": f"Competition research {path.stem} ({TODAY})",
                    "locator": str(path),
                    "publisher": "Opus research agent, session fable-agentic-stack-20261009",
                    "notes": "Dated, URL-attributed competition pass; vendor claims labelled; nothing installed or run.",
                    "idea_ids": ideas,
                    "role": "market_reference",
                },
            )
        )
    for key, payload in specs:
        path = write_json(f"source-{key}.json", payload)
        if dry:
            print(f"source {key}: would register -> {len(payload['idea_ids'])} ideas")
            continue
        result = cli("source", "register", input_path=path)
        records["sources"][key] = {"source_id": result.get("id"), "raw": result}
        print(f"source {key}: {result.get('id')}")
        save_records(records)


def phase_actors(dry: bool) -> None:
    records = load_records()
    records.setdefault("actors", {})
    actors = research_actors()
    targets = IDEAS + ([MERGED] if idea_exists(MERGED) else [])
    for idea in targets:
        for actor, rel in actors_for(idea, actors):
            research_source = records.get("sources", {}).get(Path(actor["research_file"]).stem, {}).get("source_id")
            payload = {
                "actor": {
                    "name": actor["name"],
                    "website": actor.get("website") or None,
                    "description": (actor.get("description") or "")[:2000] or None,
                },
                "relation": rel["relation"],
                "is_primary": bool(rel.get("primary", False)),
                "note": (
                    f"{rel.get('note','').strip()} Traction: {actor.get('traction','n/a')} "
                    f"({actor.get('traction_source','')}). Licence: {actor.get('license','n/a')}."
                )[:10000],
                "checked_on": actor.get("checked_on", TODAY),
                "source_ids": [s for s in [research_source] if s],
                "recorded_by": ACTOR,
            }
            key = f"{idea}:{actor['name']}:{rel['relation']}"
            if key in records["actors"] and not dry:
                continue
            path = write_json(f"actor-{idea}-{re.sub(r'[^a-z0-9]+','-',actor['name'].lower())[:40]}-{rel['relation']}.json", payload)
            if dry:
                print(f"would link {key}")
                continue
            try:
                result = cli("idea", "link-actor", "--id", idea, input_path=path)
            except SystemExit as exc:
                print(f"FAILED {key}: {exc}")
                records.setdefault("actor_failures", {})[key] = str(exc)[-500:]
                save_records(records)
                continue
            records["actors"][key] = result
            print(f"linked {key}")
            save_records(records)
    save_records(records)


def phase_scores(dry: bool) -> None:
    records = load_records()
    records.setdefault("assessments", {})
    scores = json.loads((HERE / "scores.json").read_text())
    for idea, spec in scores.items():
        if idea == MERGED and not idea_exists(idea):
            print("AS10 not created; skipping score")
            continue
        evidence_id = records.get("evidence", {}).get(idea, {}).get("evidence_id")
        payload = {
            "idea_id": idea,
            "scorecard_id": "portfolio-reviewed-v1",
            "scores": spec["scores"],
            "rationale": spec["rationale"],
            "author": f"agent:{ACTOR}",
            "confidence": spec.get("confidence", "low"),
            "criterion_rationales": spec.get("criterion_rationales", {}),
            "evidence_ids": {k: [evidence_id] for k in ("competition", "moat") if evidence_id},
            "recommendation": spec.get("recommendation"),
        }
        path = write_json(f"assessment-{idea}.json", payload)
        if dry:
            print(f"{idea}: would assess ({path.name})")
            continue
        result = cli("score", "assess", input_path=path)
        records["assessments"][idea] = result
        print(f"{idea}: assessment {result.get('id')} total {result.get('overall_score') or result.get('total')}")
        save_records(records)


if __name__ == "__main__":
    phases = {"evidence": phase_evidence, "sources": phase_sources, "actors": phase_actors,
              "merge": phase_merge, "scores": phase_scores, "reviews": phase_reviews}
    if len(sys.argv) < 2 or sys.argv[1] not in phases:
        raise SystemExit(__doc__)
    phases[sys.argv[1]]("--dry-run" in sys.argv)
