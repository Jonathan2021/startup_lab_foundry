"""Readable historical reviews, scoped work and structured exact proposal edits."""

import re

from fastapi.testclient import TestClient
from test_portfolio_proposals import proposal as proposal

from startup_foundry.human_inputs import (
    ClaimInput,
    HumanInputService,
    RequestInput,
    ResponseInput,
    ReviewResult,
    TargetChange,
)
from startup_foundry.proposals import ResolveInput
from startup_foundry.web import create_app


def test_historical_reviews_link_persisted_next_work_and_are_scoped(proposal, tmp_path):
    s, p, seed, f, portfolio = proposal
    ws = portfolio.show_idea("P103")["workspace_id"]
    inputs = HumanInputService(f, tmp_path)
    inputs.register(
        RequestInput(
            id="R006",
            workspace_id=ws,
            target_workspace_ids=[ws],
            title="Sport",
            question="Which sport?",
        )
    )

    def save(text, key):
        return inputs.submit(
            "R006",
            ResponseInput(
                expected_version=inputs.show("R006")["version"],
                text=text,
                author="operator",
                submission_key=key,
            ),
        )

    answer = save("Volleyball", "one")
    claim = inputs.claim(
        "R006", ClaimInput(expected_version=answer["version"], actor="agent")
    )
    result = inputs.complete(
        "R006",
        ReviewResult(
            work_id=claim["work_id"],
            response_id=claim["response_id"],
            actor="agent",
            interpretation="Volleyball",
            outcome="sufficient",
            rationale="Fixture",
            changes=[
                TargetChange(
                    workspace_id=ws,
                    expected_revision=0,
                    next_action="Prepare trial",
                    next_work_title="Prepare fixture trial",
                )
            ],
        ),
    )
    work_id = result["effects"][0]["work_id"]
    save("Clarification", "two")
    with TestClient(create_app(f, tmp_path), base_url="http://127.0.0.1") as c:
        page = c.get("/requests/R006").text
        assert (
            "Historical review · older reply" in page
            and "Current answer has no review yet" in page
        )
        url = "/ideas/P103/work/" + work_id
        assert url in page
        work = c.get(url)
        assert work.status_code == 200 and "Prepare fixture trial" in work.text
        assert "Ready" in work.text and "agent" in work.text
        assert c.get(url.replace("P103", "P023")).status_code == 404


def test_structured_proposal_editor_revises_scope_next_work_and_treatments(
    proposal, tmp_path
):
    s, p, seed, f, portfolio = proposal
    with TestClient(create_app(f, tmp_path), base_url="http://127.0.0.1") as c:
        page = c.get("/proposals/" + p["id"]).text
        assert "data-proposal-edit" in page and "Scope comparison (JSON)" not in page
        assert 'name="next_work_title"' in page and 'name="scope_capability"' in page
        token = re.search(r'name="foundry-token" content="([^"]+)"', page)[1]
        treatment = next(
            w for w in p["content"]["source_state"]["work"] if w["status"] == "ready"
        )
        edited = c.post(
            "/api/proposals/" + p["id"] + "/revise",
            headers={"X-Foundry-Token": token},
            json={
                "expected_version": p["version"],
                "name": "Narrowed",
                "description": "Fixture narrower",
                "actor": "operator",
                "rationale": "Prepare smaller trial",
                "scope": [
                    {
                        "capability": "Fair teams",
                        "treatment": "retained",
                        "provenance": "Fixture",
                        "reason": "Focus",
                    }
                ],
                "alternatives": ["Use manual method"],
                "next_work_title": "One bounded team comparison",
                "work_treatments": [
                    {
                        "work_id": treatment["id"],
                        "treatment": "supersede",
                        "reason": "Combined trial",
                    }
                ],
            },
        )
        assert edited.status_code == 200, edited.text
        current = edited.json()
        assert {"next_work_title", "work_treatments", "scope"} <= {
            d["field"] for d in current["revisions"][0]["differences"]
        }
        stale = c.post(
            "/api/proposals/" + p["id"] + "/resolve",
            headers={"X-Foundry-Token": token},
            json={
                "expected_version": p["version"],
                "revision_id": p["revision_id"],
                "action": "accept",
                "actor": "operator",
                "actor_kind": "user",
                "rationale": "Stale",
                "request_key": "stale",
            },
        )
        assert stale.status_code == 409
        r = s.resolve(
            p["id"],
            ResolveInput(
                expected_version=current["version"],
                revision_id=current["revision_id"],
                action="accept",
                actor="operator",
                actor_kind="user",
                rationale="Fixture exact revision",
                request_key="exact",
            ),
        )
        assert r["state"] == "applied"
        from startup_foundry.domain import WorkItem

        with f() as db:
            assert db.get(WorkItem, treatment["id"]).status.value == "cancelled"
            assert (
                db.get(WorkItem, r["result"]["work_id"]).title
                == "One bounded team comparison"
            )


def test_proposal_controls_serialize_typed_arrays_without_json_editing():
    import json
    import subprocess
    from pathlib import Path

    script = (
        Path(__file__).resolve().parents[2] / "src/startup_foundry/static/console.js"
    )
    result = subprocess.run(
        [
            "node",
            "-e",
            """
const fs=require('fs'),vm=require('vm');
const context={FormData,document:{querySelector:()=>({content:'fixture'}),
  querySelectorAll:()=>[],addEventListener:()=>{}}};
vm.createContext(context);vm.runInContext(fs.readFileSync(process.argv[1],'utf8'),context);
const value=vm.runInContext(`const data=new FormData();
for(const [k,v] of [['scope_capability','Fair teams'],
['scope_treatment','retained'],['scope_provenance','R006'],['scope_reason','Focus'],
['scope_capability','Other sports'],['scope_treatment','deferred'],
['scope_provenance','P103'],['scope_reason','Later'],
['alternative','Use manual method'],['work_id','fixture-work'],
['work_treatment','supersede'],['work_reason','Combined trial']]) data.append(k,v);
JSON.stringify(proposalPayload(data,Object.fromEntries(data)));`,context);
process.stdout.write(value);
""",
            str(script),
        ],
        capture_output=True,
        text=True,
        check=True,
    )
    payload = json.loads(result.stdout)
    assert payload["scope"][1]["treatment"] == "deferred"
    assert payload["work_treatments"] == [
        {
            "work_id": "fixture-work",
            "treatment": "supersede",
            "reason": "Combined trial",
        }
    ]
    assert "scope_capability" not in payload and "work_id" not in payload
