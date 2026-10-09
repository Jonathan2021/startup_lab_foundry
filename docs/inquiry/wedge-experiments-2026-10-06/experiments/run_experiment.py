"""Test-only synthetic experiment. Never imports or modifies Foundry runtime/state."""
from __future__ import annotations
import copy
import hashlib
import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parent

def encode(value: object) -> str:
    return json.dumps(value, ensure_ascii=False, indent=2) + "\n"

def closure(case: dict) -> list[dict]:
    """Follow explicit relationships both ways, within explicit allowed scopes."""
    rows = {r["id"]: r for r in case["records"] if r["scope"] in case["allowed_scopes"]}
    wanted = set(case["current_question_refs"])
    while True:
        expanded = set(wanted)
        for key, row in rows.items():
            targets = {edge["target"] for edge in row["links"]} & rows.keys()
            if key in wanted or targets & wanted:
                expanded.add(key)
                expanded.update(targets)
        if expanded == wanted:
            break
        wanted = expanded
    return [rows[k] for k in sorted(wanted) if k in rows]

def heading(case: dict) -> str:
    branches = "\n".join(f"- {name}: {criterion}" for name, criterion in case["branch_criteria"].items())
    return (f"# {case['case_id']}: {case['title']}\n\nEXPLICITLY SYNTHETIC.\n\n"
            f"Scope: {case['scope']}\nScope revision: {case['scope_revision']}; question revision: {case['question_revision']}.\n"
            f"Goal: {case['goal']}\nQuestion: {case['current_question']}\n\nBranch criteria:\n{branches}\n\n")

def markdown_record(row: dict, full: bool = False) -> str:
    links = "; ".join(f"{edge['relation']} {edge['target']}" for edge in row["links"]) or "none"
    if full:
        return f"## {row['id']} (scope {row['scope']}, revision {row['revision']})\n\n{row['text']}\n\nRelationships: {links}.\n\n"
    return f"- {row['id']} [{row['scope']}; r{row['revision']}; links: {links}]: {row['text']}\n"

def counts(text: str) -> dict:
    return {"utf8_bytes": len(text.encode("utf-8")), "words": len(re.findall(r"\S+", text))}

def state() -> dict:
    return {"scope_revision": 3, "question_revision": 2, "scope": "venture-A", "current": "open",
            "sibling": "active", "successor": None, "results": {}, "history": [], "effects": 0,
            "evidence": {"E-current": "venture-A", "E-private": "venture-B"}}

def submit(s: dict, request: dict) -> str:
    # No LLM judge: synthetic branch eligibility is intentionally a bounded toy rule.
    payload = {k: request[k] for k in ("scope_revision", "question_revision", "branch", "evidence")}
    old = s["results"].get(request["result_id"])
    if old is not None:
        return "duplicate" if old == payload else "reject_key_conflict"
    if request["scope_revision"] != s["scope_revision"] or request["question_revision"] != s["question_revision"]:
        return "reject_stale"
    if any(s["evidence"].get(e) != s["scope"] for e in request["evidence"]):
        return "reject_scope"
    if request["branch"] == "continue" and "E-current" not in request["evidence"]:
        return "reject_insufficient"
    s["results"][request["result_id"]] = payload
    s["history"].append(copy.deepcopy(payload))
    s["effects"] += 1
    if request["branch"] == "unknown":
        s["current"] = "held"
        return "held_no_successor"
    if request["branch"] == "stop":
        s["current"] = "stopped"
        return "stopped_no_successor"
    s["current"] = "completed"
    s["successor"] = "ready"
    return "continued"

def simulate(request: dict) -> dict:
    s = state()
    actual = submit(s, request)
    action = request["action"]
    if action == "duplicate":
        again = submit(s, request)
        actual = "one_effect" if again == "duplicate" and s["effects"] == 1 else "duplicate_effect_bug"
    elif action == "changed_duplicate":
        changed = dict(request, branch="stop")
        actual = submit(s, changed)
    elif action == "contradict":
        # Preserve accepted history; do not silently flip to a new branch.
        s["history"].append({"event": "contradictory_evidence", "id": "E-later", "contradicts": "E-current"})
        s["current"] = "review_required"
        s["successor"] = "blocked_review"
        actual = "review_required_successor_blocked" if len(s["history"]) == 2 else "history_erased"
    elif action == "revise_scope":
        s["scope_revision"] += 1
        s["current"] = "unresolved_new_scope"
        s["successor"] = "blocked_scope_change"
        actual = "old_result_historical_new_scope_unresolved" if s["history"][0]["scope_revision"] == 3 else "history_erased"
    if request["name"] == "unrelated_active_sibling":
        actual = "sibling_active" if s["sibling"] == "active" else "sibling_closed"
    return {"name": request["name"], "expected": request["expected"], "actual": actual,
            "passed": actual == request["expected"], "final_state": s}

QUESTIONS = """For each of the four cases below, answer in at most 170 words per case:
1. What is the present decision or branch, and what important facts support it? Cite source IDs.
2. What is one concrete next step, and what finding would change the decision?
3. What must stay unchanged or await permission? Identify obsolete evidence, scope limitations and missing facts.
Use only the supplied material. Do not browse or inspect other files. These are invented scenarios, not observations of real ventures. Do not assume completing research implies continuing the venture.\n\n"""

if __name__ == "__main__":
    manifest = json.loads((ROOT / "frozen_inputs.sha256.json").read_text())
    for name, sha in manifest.items():
        if hashlib.sha256((ROOT / name).read_bytes()).hexdigest() != sha:
            raise SystemExit(f"Frozen input hash mismatch: {name}")
    cases = json.loads((ROOT / "fixtures.json").read_text())["cases"]
    results = []
    file_evaluator = QUESTIONS
    packet_evaluator = QUESTIONS
    eval_cases = {"C01", "C02", "C04", "C08"}
    hashes = {}
    for case in cases:
        out = ROOT / "cases" / case["case_id"]
        out.mkdir(parents=True, exist_ok=True)
        relevant = closure(case)
        expected = set(case["oracle"]["required_evidence_ids"])
        curated = [r for r in case["records"] if r["id"] in expected]
        dossier = heading(case) + "## Organized record dossier\n\n" + "".join(markdown_record(r, True) for r in case["records"])
        brief = heading(case) + "## Curated source brief\n\n" + "".join(markdown_record(r) for r in curated)
        packet = {"format": "synthetic-context-packet-v1", "case_id": case["case_id"], "synthetic": True,
                  "scope": case["scope"], "scope_revision": case["scope_revision"], "question_revision": case["question_revision"],
                  "goal": case["goal"], "current_question": case["current_question"],
                  "branch_criteria": case["branch_criteria"], "allowed_scopes": case["allowed_scopes"],
                  "selection": {"method": "explicit_bidirectional_relationship_closure", "seed_ids": case["current_question_refs"],
                                "source_record_count": len(case["records"]), "selected_record_count": len(relevant),
                                "limitation": "Unlinked relevant facts may be omitted. Selection is not semantic retrieval."},
                  "records": relevant}
        packet_text = encode(packet)
        texts = {"full_dossier.md": dossier, "concise_brief.md": brief, "dependency_packet.json": packet_text}
        for name, text in texts.items():
            (out / name).write_text(text, encoding="utf-8")
            hashes[str((out / name).relative_to(ROOT))] = hashlib.sha256(text.encode("utf-8")).hexdigest()
        selected = {r["id"] for r in relevant}
        source_payload = "\n".join(r["text"] for r in relevant)
        row = {"case_id": case["case_id"], "required_ids": sorted(expected), "selected_ids": sorted(selected),
               "missing_required_ids": sorted(expected - selected), "unexpected_selected_ids": sorted(selected - expected),
               "required_evidence_recall": len(expected & selected) / len(expected),
               "sizes": {name: counts(value) for name, value in texts.items()},
               "selected_source_text_only": counts(source_payload),
               "packet_bytes_minus_selected_source_text_bytes": len(packet_text.encode()) - len(source_payload.encode())}
        results.append(row)
        if case["case_id"] in eval_cases:
            file_evaluator += brief + "\n---\n\n"
            packet_evaluator += "```json\n" + packet_text + "```\n\n---\n\n"
    for name, text in {"files_condition.md": file_evaluator, "packet_condition.md": packet_evaluator}.items():
        (ROOT / name).write_text(text, encoding="utf-8")
        hashes[name] = hashlib.sha256(text.encode()).hexdigest()
    transitions = [simulate(item) for item in json.loads((ROOT / "transition_inputs.json").read_text())]
    report = {"measurement": "UTF-8 bytes and whitespace-delimited words; no token/cost/latency measurement", "cases": results,
              "totals": {kind: {metric: sum(r["sizes"][kind][metric] for r in results) for metric in ("utf8_bytes", "words")}
                         for kind in ("full_dossier.md", "concise_brief.md", "dependency_packet.json")},
              "transitions": transitions, "evaluator_input_sizes": {"files": counts(file_evaluator), "packet": counts(packet_evaluator)}}
    (ROOT / "results.json").write_text(encode(report), encoding="utf-8")
    hashes["run_experiment.py"] = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    hashes["results.json"] = hashlib.sha256((ROOT / "results.json").read_bytes()).hexdigest()
    (ROOT / "output_hashes.sha256.json").write_text(encode(hashes), encoding="utf-8")
    print(encode({"totals": report["totals"], "evaluator_inputs_ready": True,
                  "missing_facts": {r["case_id"]: r["missing_required_ids"] for r in results if r["missing_required_ids"]},
                  "transition_pass_count": sum(t["passed"] for t in transitions), "transition_count": len(transitions)}))
