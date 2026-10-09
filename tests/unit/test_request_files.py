"""Open human requests from `requests/*.md` files (ADR-0020, package F08)."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.application import FoundryApplication
from startup_foundry.cli import main
from startup_foundry.domain import (
    HumanRequest,
    HumanRequestTarget,
    VentureStage,
)
from startup_foundry.errors import ValidationError
from startup_foundry.human_inputs import HumanInputService, RequestInput
from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.request_files import RequestFileSync, response_state, sections
from startup_foundry.web import create_app

FIXTURES = Path(__file__).parents[1] / "fixtures" / "request_files"
VENTURES = {
    "v-crous": "Crous Queue",
    "v-coopain": "Coopain",
    "v-offer-check": "OfferCheck",
    "v-volley-match": "Volley Match",
    "v-volley-coach": "Volley Coach",
}


@pytest.fixture
def store(tmp_path):
    database = tmp_path / "requests.db"
    url = f"sqlite:///{database}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    app = FoundryApplication(factory)
    for identity, name in VENTURES.items():
        app.create_venture(
            venture_id=identity,
            name=name,
            objective="Synthetic " + name,
            stage=VentureStage.DISCOVERY,
        )
    directory = tmp_path / "requests"
    shutil.copytree(FIXTURES, directory)
    yield factory, directory, database
    engine.dispose()


def by_key(result):
    return {(i["file"], i["request_key"], i["occurrence"]): i for i in result["items"]}


def test_section_and_response_parsing():
    found = sections((FIXTURES / "INBOX.md").read_text())
    assert [(s["request_key"], s["occurrence"]) for s in found] == [
        ("R001", 1),
        ("R006", 1),
        ("R006", 2),
    ]
    assert "Not a request" not in found[-1]["text"]
    assert response_state(found[1]["text"])[0] == "open"
    assert response_state(found[2]["text"])[0] == "answered"
    crous = (FIXTURES / "2026-10-08-crous-R011-pilot-readiness.md").read_text()
    assert response_state(crous)[0] == "open", "trailing prose is not an answer"


def test_preview_plans_without_writing_and_apply_links_ventures(store):
    factory, directory, _ = store
    files = RequestFileSync(factory, directory)
    preview = files.preview()
    assert preview["applied"] is False
    plan = by_key(preview)
    assert ("INBOX.md", "R001", 1) not in plan, "ignored by the mapping file"
    crous = plan[("2026-10-08-crous-R011-pilot-readiness.md", "R011", 1)]
    assert crous["ventures"] == [{"venture_id": "v-crous", "via": "title"}]
    coopain = plan[("2026-10-09-coopain-R015-referrer-policy.md", "R015", 1)]
    assert coopain["ventures"] == [{"venture_id": "v-coopain", "via": "id"}]
    assert coopain["state"] == "answered"
    offer = plan[("2026-10-08-offer-check-R013-quotes.md", "R013", 1)]
    assert offer["ventures"] == [{"venture_id": "v-offer-check", "via": "filename"}]
    mapped = plan[("2026-10-07-priorities.md", "R012", 1)]
    assert mapped["ventures"] == [{"venture_id": "v-offer-check", "via": "mapping"}]
    match = plan[("INBOX.md", "R006", 1)]
    coach = plan[("INBOX.md", "R006", 2)]
    assert match["record_id"] == "R006" and coach["record_id"].startswith("R006-")
    assert coach["ventures"][0]["venture_id"] == "v-volley-coach"
    with factory() as session:
        assert session.scalar(select(func.count()).select_from(HumanRequest)) == 0

    applied = files.apply()
    assert applied["counts"]["create"] == 6 and applied["counts"]["unlinked"] == 0
    with factory() as session:
        request = session.get(HumanRequest, "R011")
        assert request.status == "waiting_for_answer"
        assert request.source_diagnostics["file_sync"]["state"] == "open"
        assert "Crous Queue" in request.title or "private pilot" in request.title
        targets = set(
            session.scalars(
                select(HumanRequestTarget.workspace_id).where(
                    HumanRequestTarget.request_id == "R011"
                )
            )
        )
        crous_ws = FoundryApplication._venture(session, "v-crous")[1].id
        assert targets == {crous_ws}
        answered = session.get(HumanRequest, "R015")
        assert answered.status == "waiting_for_answer", "answers are not consumed"
        assert answered.response_artifact_id is None
        assert answered.source_diagnostics["file_sync"]["state"] == "answered"
    again = files.apply()
    assert again["counts"]["unchanged"] == 6 and again["counts"]["create"] == 0


def test_answering_updates_state_without_a_new_question_revision(store):
    factory, directory, _ = store
    files = RequestFileSync(factory, directory)
    files.apply()
    path = directory / "2026-10-08-crous-R011-pilot-readiness.md"
    path.write_text(
        path.read_text().replace(
            "- Practical ordinary queue/access, or unknown/unavailable:",
            "- Practical ordinary queue/access, or unknown/unavailable: unknown",
        )
    )
    updated = by_key(files.apply())[
        ("2026-10-08-crous-R011-pilot-readiness.md", "R011", 1)
    ]
    assert updated["action"] == "update" and updated["state"] == "answered"
    with factory() as session:
        request = session.get(HumanRequest, "R011")
        assert request.definition_revision == 1
        assert request.source_diagnostics["file_sync"]["state"] == "answered"
    path.write_text(path.read_text().replace("Synthetic fixture.", "Changed ask."))
    files.apply()
    with factory() as session:
        assert session.get(HumanRequest, "R011").definition_revision == 2


def test_existing_registered_request_is_linked_not_replaced(store):
    factory, directory, _ = store
    with factory() as session:
        # The campaign request targets another venture; sync adds Volley Match.
        owner = FoundryApplication._venture(session, "v-volley-coach")[1].id
        match = FoundryApplication._venture(session, "v-volley-match")[1].id
    inputs = HumanInputService(factory, directory)
    inputs.register(
        RequestInput(
            id="R006",
            workspace_id=owner,
            target_workspace_ids=[owner],
            title="Original sports group trial",
            question="Original campaign question",
            file_path="INBOX.md",
        )
    )
    plan = by_key(RequestFileSync(factory, directory).apply())
    assert plan[("INBOX.md", "R006", 1)]["action"] == "link"
    with factory() as session:
        original = session.get(HumanRequest, "R006")
        assert original.title == "Original sports group trial"
        assert "file_sync" not in original.source_diagnostics
        assert match in set(
            session.scalars(
                select(HumanRequestTarget.workspace_id).where(
                    HumanRequestTarget.request_id == "R006"
                )
            )
        )


def test_unsafe_sources_and_unknown_mapping_are_rejected(store):
    factory, directory, _ = store
    (directory / "linked.md").symlink_to(directory / "INBOX.md")
    plan = RequestFileSync(factory, directory).preview()
    assert all(item["file"] != "linked.md" for item in plan["items"])
    (directory / "request-ventures.json").write_text(
        json.dumps({"files": {"INBOX.md": ["v-missing"]}})
    )
    with pytest.raises(ValidationError, match="unknown venture"):
        RequestFileSync(factory, directory).preview()


def test_open_requests_on_venture_page_today_and_resume(store):
    factory, directory, _ = store
    RequestFileSync(factory, directory).apply()
    client = TestClient(create_app(factory, directory), base_url="http://127.0.0.1")
    page = client.get("/ventures/v-crous").text
    assert "Open human requests" in page and "R011" in page
    assert "requests/2026-10-08-crous-R011-pilot-readiness.md" in page
    assert "No open human requests" not in page
    assert "Answer R011" in page and "Owner: you" in page
    coopain = client.get("/ventures/v-coopain").text
    assert "Answered in file — awaiting reviewed intake" in coopain
    today = client.get("/").text
    assert "Open human requests · 6" in today and "R015" in today
    source = client.get("/requests/R011/source")
    assert source.status_code == 200 and "Crous Queue" in source.text
    with factory() as session:
        ws = FoundryApplication._venture(session, "v-crous")[1].id
    resume = AgentHandoffService(factory).resume(ws)
    assert [r["id"] for r in resume["human_requests"]] == ["R011"]
    assert resume["human_requests"][0]["file"].endswith("R011-pilot-readiness.md")
    assert "## Human requests" in resume["markdown"]
    gates = resume["venture_state"]["open_gates"]
    assert gates[0]["kind"] == "human_request" and gates[0]["id"] == "R011"


def test_cli_preview_and_apply(store, capsys):
    _, directory, database = store
    base = ["--store", str(database), "input", "sync"]
    target = ["--requests-directory", str(directory)]
    assert main([*base, *target, "--preview"]) == 0
    assert json.loads(capsys.readouterr().out)["applied"] is False
    assert main([*base, *target, "--apply"]) == 0
    output = capsys.readouterr().out
    assert output.endswith("\n") and json.loads(output)["counts"]["create"] == 6
    assert main([*base, *target, "--preview", "--apply"]) == 2
    assert "exactly one" in capsys.readouterr().err
    assert main([*base]) == 2
