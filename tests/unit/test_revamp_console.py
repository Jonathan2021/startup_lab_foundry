"""HTTP acceptance supplements visual QA; it does not certify browser layout."""

import re

from fastapi.testclient import TestClient

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import VentureStage
from startup_foundry.human_inputs import (
    ClaimInput,
    HumanInputService,
    RequestInput,
    ResponseInput,
    ReviewResult,
    TargetChange,
)
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.scoring import FACTORS, AssessmentInput, ScoringService
from startup_foundry.venture_scoring import VentureScoringService
from startup_foundry.web import create_app


def test_contextual_answers_holds_scores_history_and_restart(tmp_path):
    url = f"sqlite:///{tmp_path / 'console.db'}"
    upgrade_database(url)
    factory = create_session_factory(create_db_engine(url))
    p = PortfolioService(factory)
    s = ScoringService(factory)
    for identity in ["P103", "P023"]:
        p.create_idea(
            IdeaDraft(title="Outdoor volleyball " + identity, description="Fixture"),
            idea_id=identity,
        )
        p.promote_idea(identity, venture_id="v-" + identity)
        s.assess(
            AssessmentInput(
                idea_id=identity,
                scores={k: 5 for k, *_ in FACTORS},
                rationale="Synthetic idea score",
                author="tester",
            )
        )
    scores = VentureScoringService(factory)
    scores.bootstrap()
    a = FoundryApplication(factory)
    a.create_venture(
        venture_id="v-hold",
        name="Held",
        objective="Fixture",
        stage=VentureStage.DISCOVERY,
    )
    ws = a.show_venture("v-P103")["venture"]["workspace_id"]
    other = a.show_venture("v-P023")["venture"]["workspace_id"]
    held = a.show_venture("v-hold")["venture"]["workspace_id"]
    inputs = HumanInputService(factory, tmp_path)
    inputs.register(
        RequestInput(
            id="R006",
            workspace_id=ws,
            target_workspace_ids=[ws, other],
            title="Sports group",
            question="Which sport?",
            file_path="fixture.md",
        )
    )
    inputs.register(
        RequestInput(
            id="R008",
            workspace_id=held,
            target_workspace_ids=[held],
            title="Contact",
            question="Feedback?",
        )
    )
    item = inputs.show("R008")
    inputs.submit(
        "R008",
        ResponseInput(
            expected_version=item["version"],
            text="Hold until contact replies",
            author="operator",
            submission_key="hold",
        ),
    )
    item = inputs.show("R008")
    claim = inputs.claim(
        "R008", ClaimInput(expected_version=item["version"], actor="agent")
    )
    inputs.complete(
        "R008",
        ReviewResult(
            work_id=claim["work_id"],
            response_id=claim["response_id"],
            actor="agent",
            interpretation="User hold",
            outcome="deferred",
            rationale="Wait for contact",
            changes=[
                TargetChange(
                    workspace_id=held,
                    expected_revision=0,
                    disposition="hold",
                    next_action="Reopen when contact feedback arrives",
                )
            ],
        ),
    )
    for restart in range(2):
        with TestClient(
            create_app(factory, tmp_path), base_url="http://127.0.0.1"
        ) as client:
            token = re.search(
                r'name="foundry-token" content="([^"]+)"', client.get("/").text
            )[1]
            headers = {"X-Foundry-Token": token}
            for v in ["v-P103", "v-P023"]:
                detail = client.get("/ventures/" + v)
                assert (
                    detail.status_code == 200
                    and v in detail.text
                    and (
                        "Reviewed venture judgment"
                        if restart and v == "v-P103"
                        else "Starting estimate"
                    )
                    in detail.text
                    and "R006" in detail.text
                )
            assert client.get("/ideas/P103").status_code == 200
            assert "R008" not in client.get("/requests?status=needs_you").text
            assert "R008" in client.get("/requests?status=deferred").text
            assert client.get("/ventures/v-hold?tab=history").status_code == 200
            assert client.get("/ventures/v-P103?tab=software").status_code == 200
            assert client.get("/ventures/v-P103?tab=settings").status_code == 200
            if not restart:
                item = inputs.show("R006")
                response = client.post(
                    "/api/inputs/R006/responses",
                    json={
                        "expected_version": item["version"],
                        "text": "<script>Volleyball</script>",
                        "author": "operator",
                        "submission_key": "ui",
                    },
                    headers=headers,
                )
                assert response.status_code == 200
                page = client.get("/requests/R006").text
                assert (
                    "&lt;script&gt;Volleyball&lt;/script&gt;" in page
                    and "Saved answer" in page
                )
                assert (
                    client.post(
                        "/api/inputs/R006/responses",
                        json={
                            "expected_version": item["version"],
                            "text": "New",
                            "author": "operator",
                            "submission_key": "stale",
                        },
                        headers=headers,
                    ).status_code
                    == 409
                )
                assert (
                    client.get("/requests/R006/handoff").json()["request"]["answer"][
                        "id"
                    ]
                    == response.json()["id"]
                )
                assert (
                    client.post(
                        "/api/venture-scores",
                        json={
                            "venture_id": "v-P103",
                            "expected_sequence": 1,
                            "request_key": "native",
                            "scores": {
                                k: 1 if d == "positive" else 10
                                for k, n, d, w in FACTORS
                            },
                            "rationale": "Synthetic zero",
                            "author": "tester",
                        },
                        headers=headers,
                    ).json()["total"]
                    == 0
                )
                assert "0.0 / 100" in client.get("/ventures/v-P103").text
            assert client.get("/ventures/v-P103?tab=scores").status_code == 200
            rows = client.get("/api/ventures?direction=asc").json()["items"]
            assert rows[0]["id"] == "v-P103"
            history = client.get("/ventures/v-P103?tab=history")
            event = re.search(r'href="(/ventures/v-P103/events/[^"]+)"', history.text)[
                1
            ]
            assert client.get(event).status_code == 200
            assert client.get(event.replace("v-P103", "v-P023")).status_code == 404
