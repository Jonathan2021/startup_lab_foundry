"""Isolated synthetic lifecycle demo. Never merges fixtures into an existing store."""

from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.application import FoundryApplication
from startup_foundry.decision_contracts import (
    CaptureInput,
    ContextInput,
    MapInput,
    NewWorkInput,
    ResultInput,
)
from startup_foundry.decision_maps import DecisionMapService
from startup_foundry.domain import VentureStage
from startup_foundry.errors import ConflictError
from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.reviews import ReviewInput, ReviewService

SCENARIOS = (
    {
        "id": "demo-campus",
        "title": "[Demo] Campus lunch decisions",
        "goal": "Help students choose when and where to eat",
        "question": "Do wait estimates change a lunch choice?",
        "task": "Compare waiting-time usefulness with a simple timetable",
        "criteria": "Five synthetic comparisons; record changed choices and unknowns",
        "finding": (
            "Synthetic fixture: 2 of 5 choices changed; sample is not representative"
        ),
        "condition": (
            "At least 3 of 5 students change their choice with reliable estimates"
        ),
        "alternative": "Try a narrow observation pilot",
        "maturity": "concept",
        "stage": "discovery",
        "investigation": "problem_validation",
    },
    {
        "id": "demo-billing",
        "title": "[Demo] Operating billing service",
        "goal": "Keep an existing billing service reliable as releases change",
        "question": "Can release r18 preserve customer account isolation?",
        "task": "Reproduce the staging account-boundary regression",
        "criteria": "Record the fixture, release and reproducible boundary result",
        "finding": (
            "Synthetic staging fixture crosses accounts; production impact unknown"
        ),
        "condition": "Any account-boundary check fails in the candidate release",
        "alternative": "Hold r18 and test a correction",
        "maturity": "operating",
        "stage": "operating",
        "investigation": "solution_validation",
    },
    {
        "id": "demo-supplier",
        "title": "[Demo] Reusable event equipment",
        "goal": "Fulfil repeat event orders without unreliable supplier promises",
        "question": "Can the primary supplier meet next month's booked orders?",
        "task": "Compare supplier capacity and fallback rental cost",
        "criteria": "Retain dated capacity evidence and limits; draft a contingency",
        "finding": "Synthetic supplier message reduces available units from 80 to 45",
        "condition": (
            "Confirmed capacity falls below 60 units before the booking deadline"
        ),
        "alternative": "Draft a fallback rental plan",
        "maturity": "operating",
        "stage": "operating",
        "investigation": "business_validation",
    },
)


def create_demo(path: Path) -> dict[str, Any]:
    path = path.expanduser().resolve()
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        with path.open("xb"):
            pass
    except FileExistsError as exc:
        raise ConflictError(
            "Demo requires a NEW store path; existing data is untouched"
        ) from exc
    path.chmod(0o600)
    url = "sqlite:///" + str(path)
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    handoffs, maps = AgentHandoffService(factory), DecisionMapService(factory)
    entries = []
    try:
        for scenario in SCENARIOS:
            venture = FoundryApplication(factory).create_venture(
                venture_id=scenario["id"],
                name=scenario["title"],
                objective=scenario["goal"],
                stage=VentureStage(scenario["stage"]),
            )
            workspace = str(venture["workspace_id"])
            work = handoffs.create_work(
                workspace,
                NewWorkInput.model_validate(
                    {
                        "request_key": "demo-work",
                        "actor": "synthetic fixture",
                        "rationale": "Exercise an ongoing lifecycle decision",
                        "expected_head": None,
                        "work": {
                            "title": scenario["task"],
                            "description": scenario["question"],
                            "acceptance_criteria": scenario["criteria"],
                            "owner": "agent",
                        },
                    }
                ),
            )
            ReviewService(factory).append(
                ReviewInput.model_validate(
                    {
                        "workspace_id": workspace,
                        "expected_revision": 0,
                        "investigation_stage": scenario["investigation"],
                        "product_maturity": scenario["maturity"],
                        "disposition": "pursue",
                        "next_action": scenario["task"],
                        "next_work_item_id": work["id"],
                        "reason": "Entirely synthetic; no customer or market evidence",
                        "author": "synthetic fixture",
                    }
                )
            )
            finding = handoffs.capture(
                workspace,
                CaptureInput(
                    request_key="initial-fact",
                    actor="synthetic fixture",
                    summary=scenario["finding"],
                    sources=["observation: invented demo fixture"],
                    details=(
                        "Demonstration data only. Do not treat as venture validation."
                    ),
                ),
            )
            head = maps.revise(
                workspace,
                MapInput.model_validate(
                    {
                        "expected_head": None,
                        "request_key": "initial-map",
                        "actor": "synthetic fixture",
                        "rationale": (
                            "Make the current decision and possible outcomes explicit"
                        ),
                        "map": {
                            "nodes": [
                                {
                                    "id": "goal",
                                    "kind": "goal",
                                    "title": scenario["goal"],
                                },
                                {
                                    "id": "question",
                                    "kind": "question",
                                    "title": scenario["question"],
                                },
                                {
                                    "id": "task",
                                    "kind": "record",
                                    "title": scenario["task"],
                                    "ref": {"kind": "work", "id": work["id"]},
                                },
                                {
                                    "id": "finding",
                                    "kind": "record",
                                    "title": scenario["finding"],
                                    "ref": {
                                        "kind": "evidence",
                                        "id": finding["evidence_id"],
                                    },
                                },
                                {
                                    "id": "option",
                                    "kind": "alternative",
                                    "title": scenario["alternative"],
                                },
                                {
                                    "id": "rethink",
                                    "kind": "alternative",
                                    "title": "Gather more evidence or change the plan",
                                },
                            ],
                            "edges": [
                                {
                                    "source": "task",
                                    "target": "question",
                                    "kind": "tests",
                                },
                                {
                                    "source": "question",
                                    "target": "goal",
                                    "kind": "contributes_to",
                                },
                                {
                                    "source": "finding",
                                    "target": "question",
                                    "kind": "informs",
                                },
                                {
                                    "source": "question",
                                    "target": "option",
                                    "kind": "may_lead_to",
                                    "condition": scenario["condition"],
                                    "outcome": "supported",
                                },
                                {
                                    "source": "question",
                                    "target": "rethink",
                                    "kind": "may_lead_to",
                                    "condition": (
                                        "The test is inconclusive or its source is "
                                        "contradicted"
                                    ),
                                    "outcome": "inconclusive",
                                },
                            ],
                            "focus": ["task"],
                        },
                    }
                ),
            )
            context = handoffs.prepare(
                workspace,
                ContextInput(
                    work_id=work["id"],
                    expected_work_version=work["work"]["version_id"],
                    expected_head=head["id"],
                    request_key="context",
                    actor="demo agent",
                ),
            )
            result = handoffs.submit(
                workspace,
                ResultInput(
                    context_id=context["id"],
                    request_key="draft-result",
                    actor="demo agent",
                    summary="Review the limits before proceeding",
                    rationale=scenario["finding"],
                    limits=(
                        "Invented observations; no live research or customer contact"
                    ),
                    outcome="hold",
                    next_action="Revisit when reliable evidence is available",
                    revisit_trigger=(
                        "Independent, dated evidence for the current question"
                    ),
                ),
            )
            if scenario["id"] == "demo-supplier":
                handoffs.capture(
                    workspace,
                    CaptureInput(
                        request_key="late-update",
                        actor="synthetic fixture",
                        summary=(
                            "Synthetic correction: the capacity message "
                            "concerns another date"
                        ),
                        sources=["observation: invented correction"],
                    ),
                )
            entries.append(
                {
                    "venture_id": venture["id"],
                    "workspace_id": workspace,
                    "context_id": context["id"],
                    "result_id": result["id"],
                }
            )
        return {
            "synthetic": True,
            "store": str(path),
            "ventures": entries,
            "open": f"foundry --store {path} ui --port 8766",
        }
    finally:
        engine.dispose()


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--store", type=Path, required=True, help="New isolated SQLite file"
    )
    args = parser.parse_args()
    try:
        print(json.dumps(create_demo(args.store), indent=2))
    except ConflictError as exc:
        parser.error(str(exc))


if __name__ == "__main__":
    main()
