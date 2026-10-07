"""One-time, public-CLI-only OfferCheck handoff; rehearse on a backup first.

No SQL writes or application imports. Every command/input/output is retained.
Refuses an existing output directory; inspect the journal before retrying a
partially applied run. This is a dated operator procedure, not a product worker.
"""

# ruff: noqa: E501 -- retain exact dated evidence/rationale and user quotation strings

from __future__ import annotations

import argparse
import json
import subprocess
from datetime import UTC, datetime
from pathlib import Path

ROOT = Path("/home/jonathan/startup_lab")
ACTOR = "Codex:conversation-mvp-2026-10-07"
IDEA = "conversation-offer-check-20261007"


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--store", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    assert args.store.is_file(), "Select an existing backed-up store"
    args.output.mkdir(parents=True, exist_ok=False)
    cli = [str(ROOT / ".venv/bin/foundry"), "--store", str(args.store.resolve())]
    sequence = 0

    def call(*argv, payload=None):
        nonlocal sequence
        sequence += 1
        stem = args.output / f"{sequence:02d}-{'-'.join(argv[:2])}"
        command = [*cli, *argv]
        if payload is not None:
            input_file = stem.with_suffix(".input.json")
            input_file.write_text(json.dumps(payload, indent=2) + "\n")
            command += ["--input", str(input_file.resolve())]
        stem.with_suffix(".command.json").write_text(json.dumps(command))
        completed = subprocess.run(command, capture_output=True, text=True, timeout=60)
        stem.with_suffix(".stderr.txt").write_text(completed.stderr)
        stem.with_suffix(".output.json").write_text(completed.stdout)
        if completed.returncode:
            raise RuntimeError(
                f"{argv[:2]} failed; inspect {stem}: {completed.stderr[-2000:]}"
            )
        return json.loads(completed.stdout)

    spec = json.loads((ROOT / "offer-check/docs/mvp/spec.json").read_text())
    venture = spec["venture"]
    call(
        "idea",
        "create",
        "--id",
        IDEA,
        "--title",
        spec["name"],
        "--description",
        spec["goal"]
        + "\nDerived from the user-supplied Generate Startup Ideas.md: commercial facts and verified outcomes. Source instructions are not active instructions.",
        "--customer",
        "Small equipment-buying teams and their existing agents",
        "--validation-test",
        "Build the bounded synthetic quote-review MVP; later compare permitted quote sets against a spreadsheet or existing procurement workflow. No demand claim.",
    )
    promoted = call("idea", "promote", "--id", IDEA, "--venture-id", venture)
    workspace = promoted["workspace_id"]

    def resume():
        return call("agent", "resume", "--workspace-id", workspace, "--format", "json")

    state = resume()
    call(
        "existing-project",
        "intake",
        payload={
            "venture_id": venture,
            "name": spec["name"],
            "description": spec["goal"],
            "repositories": [
                {
                    "local_reference": str(ROOT / "offer-check"),
                    "head": None,
                    "dirty_state": "New local repository; implementation plan and synthetic probe only, no application",
                    "observed_at": datetime.now(UTC).isoformat(),
                }
            ],
            "product_maturity": "concept",
            "reason_paused": "Reference checkpoint before the explicit bounded-build decision below; no customer-data prerequisite for local implementation.",
            "gaps": [
                "Application remains to implement",
                "Demand and differentiation unvalidated",
            ],
            "next_bounded_test": spec["packages"][0][2],
            "ownership_license_access": "Local preparation authorized. No supplier contact, purchasing, private third-party data or public deployment authorized.",
            "expected_review_revision": state["current_review"]["revision"]
            if state["current_review"]
            else 0,
            "author": ACTOR,
        },
    )
    module = call("workspace", "show", "--id", venture)
    call(
        "workspace",
        "configure",
        "--id",
        venture,
        payload={
            "expected_revision": module["config"]["revision"],
            "actor": ACTOR,
            "modules": ["software"],
        },
    )
    evidence = call(
        "change",
        "record",
        "--workspace-id",
        workspace,
        payload={
            "request_key": "conversation-offer-scope-20261007",
            "actor": ACTOR,
            "summary": "OfferCheck: source-derived scope, competition and bounded technical probe",
            "details": spec["goal"] + "\n" + spec["decision"] + "\n" + spec["evidence"],
            "sources": [
                "document: "
                + str(
                    ROOT
                    / "foundry/docs/inquiry/conversation-mvp-2026-10-07/source.json"
                ),
                "document: " + str(ROOT / "offer-check/docs/mvp/DECISION.md"),
                "document: " + str(ROOT / "offer-check/experiments/result.json"),
            ],
            "confidence": "medium",
        },
    )
    state = resume()
    research = call(
        "venture-work",
        "create",
        "--workspace-id",
        workspace,
        payload={
            "expected_head": state["map_revision_id"],
            "request_key": "conversation-research-20261007",
            "actor": ACTOR,
            "rationale": "Record the completed investigation and make one implementation package ready.",
            "work": {
                "title": "Select a conversation-derived MVP and prepare its handoff",
                "description": spec["goal"],
                "kind": "investigation",
                "acceptance_criteria": "Compare candidates, retain sources and probe limits, write a dependent implementation map and materialize O01 only.",
            },
        },
    )
    work_id = research["work"]["id"]
    state = resume()
    redundant = [w for w in state["work"] if w["id"] != work_id]
    assert all(
        w["title"] == "Initial manual review of v-offer-check"
        and w["status"] == "ready"
        for w in redundant
    ), "Unexpected existing work; review manually"
    treatments = [
        {
            "work_id": w["id"],
            "expected_version": w["version_id"],
            "action": "cancel",
            "rationale": "Automatic initial review is superseded by this completed, source-backed investigation; retain its history.",
        }
        for w in redundant
    ]
    research_row = next(w for w in state["work"] if w["id"] == work_id)
    treatments.append(
        {
            "work_id": work_id,
            "expected_version": research_row["version_id"],
            "action": "keep",
            "rationale": "This completed investigation directly assesses the declared map.",
        }
    )
    nodes = [
        {"id": "goal", "kind": "goal", "title": spec["goal"][:300]},
        {
            "id": "research",
            "kind": "record",
            "title": "Source, candidate and probe review",
            "ref": {"kind": "work", "id": work_id},
        },
        {
            "id": "pilot",
            "kind": "question",
            "title": "Does a buyer repeatedly prefer the checker after setup and source-review effort?",
        },
        {
            "id": "extend",
            "kind": "alternative",
            "title": "Add one integration exposed by repeated use",
        },
        {
            "id": "simplify",
            "kind": "alternative",
            "title": "Keep a template/adapter or stop if an existing workflow works as well",
        },
    ]
    edges = [
        {"source": "research", "target": "goal", "kind": "contributes_to"},
        {
            "source": "pilot",
            "target": "extend",
            "kind": "may_lead_to",
            "condition": "Repeated voluntary use and a concrete missing input",
            "outcome": "supported",
        },
        {
            "source": "pilot",
            "target": "simplify",
            "kind": "may_lead_to",
            "condition": "No repeat use or no advantage after total effort",
            "outcome": "weakened",
        },
    ]
    for pid, deps, title, what, criteria in spec["packages"]:
        nodes.append(
            {
                "id": pid,
                "kind": "alternative",
                "title": pid + ": " + title,
                "detail": what
                + "\nAcceptance: "
                + criteria
                + "\nProposed; materialize only after prerequisites pass.",
            }
        )
        edges.append({"source": pid, "target": "goal", "kind": "contributes_to"})
        edges.extend(
            {"source": pid, "target": dep, "kind": "depends_on"} for dep in deps
        )
    edges.append({"source": "O05", "target": "pilot", "kind": "informs"})
    call(
        "decision-map",
        "revise",
        "--workspace-id",
        workspace,
        payload={
            "expected_head": state["map_revision_id"],
            "request_key": "conversation-map-20261007",
            "actor": ACTOR,
            "rationale": "Bounded build now; pilot and integration expansion remain conditional.",
            "map": {"nodes": nodes, "edges": edges, "focus": ["research"]},
            "work_treatments": treatments,
        },
    )
    state = resume()
    claim = call(
        "handoff",
        "claim",
        "--workspace-id",
        workspace,
        "--work-id",
        work_id,
        payload={
            "expected_version": next(w for w in state["work"] if w["id"] == work_id)[
                "version_id"
            ],
            "actor": ACTOR,
        },
    )
    context = call(
        "handoff",
        "prepare",
        "--workspace-id",
        workspace,
        payload={
            "work_id": work_id,
            "expected_work_version": claim["version_id"],
            "expected_head": state["map_revision_id"],
            "request_key": "conversation-context-20261007",
            "actor": ACTOR,
            "budget_bytes": 100000,
            "evidence_ids": [evidence["evidence_id"]],
        },
    )
    package = spec["packages"][0]
    result = call(
        "result",
        "submit",
        "--workspace-id",
        workspace,
        payload={
            "context_id": context["id"],
            "request_key": "conversation-result-20261007",
            "actor": ACTOR,
            "summary": spec["decision"],
            "rationale": "The user requested a source-derived idea through MVP handover. Primary research and the probe justify this bounded local implementation, not market validation.",
            "limits": "No real customer data, product comparison trial, demand, price or deployment validation. Probe covers only the declared synthetic cases; application not built.",
            "outcome": "narrow",
            "decision_scope": "venture",
            "narrowed_objective": spec["goal"],
            "next_action": package[0]
            + ": "
            + package[2]
            + " — "
            + str(ROOT / "offer-check/docs/mvp/ROADMAP.md"),
            "findings": [
                {
                    "summary": spec["evidence"],
                    "sources": [
                        "document: " + str(ROOT / "offer-check/docs/mvp/SOURCES.md")
                    ],
                    "confidence": "medium",
                }
            ],
            "next_work": {
                "title": package[0] + ": " + package[2],
                "description": package[3]
                + "\nPlan: "
                + str(ROOT / "offer-check/docs/mvp/ROADMAP.md"),
                "acceptance_criteria": package[4],
                "kind": "execution",
                "owner": "agent",
            },
        },
    )
    choice = {
        "expected_result_digest": result["digest"],
        "expected_head": context["map_revision_id"],
        "expected_work_version": context["work"]["version_id"],
        "expected_review_revision": context["review_revision"],
        "resolution": "accept",
        "actor": ACTOR,
        "rationale": "Reviewed bounded local handoff under user authorization; self-review, not independent market validation.",
        "coverage_action": "reviewed"
        if context["context_complete"]
        else "accept_limitation",
        "coverage_rationale": "Supplied source and primary sources read; full local plans/probe retained. No commercial truth or demand inferred.",
    }
    call("result", "preview", "--id", result["id"], payload=choice)
    receipt = call("result", "resolve", "--id", result["id"], payload=choice)
    final = resume()
    review = final["current_review"]
    call(
        "review",
        "append",
        payload={
            "workspace_id": workspace,
            "expected_revision": review["revision"],
            "investigation_stage": "solution_validation",
            "product_maturity": "concept",
            "disposition": "pursue",
            "next_action": review["next_action"],
            "next_work_item_id": review["next_work_item_id"],
            "reason": "Bounded private MVP implementation; demand and differentiation remain unvalidated.",
            "author": ACTOR,
            "source_artifact_id": result["id"],
        },
    )
    request = call("input", "show", "--id", "R012")
    assert request["status"] == "waiting_for_answer", "R012 changed; review manually"
    answer = (
        "User supplied /home/jonathan/Downloads/Generate Startup Ideas.md on 2026-10-07 and asked: "
        '"I had forgotton to link to converstatiion you should have drawn an idea from. Do it now, and do all the steps to MVP handover for it." '
        "Source SHA-256 c44996424584d04500cd2bdebb7f24008f592022c77fd86f435f7bc769f4b78d. "
        "The attachment identifies the missing source; its embedded historical instructions are data."
    )
    call(
        "input",
        "submit",
        "--id",
        "R012",
        payload={
            "expected_version": request["version"],
            "text": answer,
            "author": "User attachment and request, transcribed by Codex",
            "submission_key": "r012-user-attachment-20261007",
        },
    )
    request = call("input", "show", "--id", "R012")
    claimed = call(
        "input",
        "claim",
        "--id",
        "R012",
        payload={"expected_version": request["version"], "actor": ACTOR},
    )
    input_receipt = call(
        "input",
        "complete",
        "--id",
        "R012",
        payload={
            "work_id": claimed["work_id"],
            "response_id": claimed["response_id"],
            "actor": ACTOR,
            "interpretation": "The missing source is now supplied. OfferCheck derives commercial-facts checking and verified-outcome receipts into an exact-SKU quote-review workflow.",
            "outcome": "sufficient",
            "rationale": "Source inspected, candidates compared, bounded probe run, independent repo and implementation map prepared. Venture "
            + venture
            + ", workspace "
            + workspace
            + ", first work "
            + review["next_work_item_id"]
            + ".",
            "remaining_unknowns": [
                "OfferCheck demand and product advantage remain unvalidated; these are pilot questions, not a missing-source blocker."
            ],
            "changes": [],
            "score_explanation": "Source supplied does not establish market traction or justify a numerical score.",
        },
    )
    summary = {
        "idea_id": IDEA,
        "venture_id": venture,
        "workspace_id": workspace,
        "research_work_id": work_id,
        "context_id": context["id"],
        "result_id": result["id"],
        "receipt": receipt,
        "first_work_id": review["next_work_item_id"],
        "input_receipt": input_receipt,
        "repository": str(ROOT / "offer-check"),
    }
    (args.output / "summary.json").write_text(json.dumps(summary, indent=2) + "\n")
    print(json.dumps(summary, indent=2))


if __name__ == "__main__":
    main()
