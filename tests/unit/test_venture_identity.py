"""Venture aliases, `--id` selectors and clean CLI output (ADR-0020, F09)."""

from __future__ import annotations

import json

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import select

from startup_foundry.cli import main
from startup_foundry.domain import AuditEvent, Venture
from startup_foundry.errors import ConflictError
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import IdeaDraft, PortfolioService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.venture_identity import AliasInput, VentureAliasService
from startup_foundry.web import create_app

CROUS = "f0b5abfe-0274-42f7-9c9a-72dcbe68c116"


@pytest.fixture
def crous(tmp_path):
    database = tmp_path / "alias.db"
    url = f"sqlite:///{database}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    portfolio = PortfolioService(factory)
    portfolio.create_idea(
        IdeaDraft(title="Crous Queue", description="Lunch queue"), idea_id="P1"
    )
    venture = portfolio.promote_idea("P1", venture_id=CROUS)
    portfolio.create_idea(IdeaDraft(title="Other", description="x"), idea_id="P2")
    portfolio.promote_idea("P2", venture_id="v-other")
    yield factory, database, venture, tmp_path
    engine.dispose()


def run(database, capsys, *args):
    code = main(["--store", str(database), *args])
    captured = capsys.readouterr()
    return code, captured.out, captured.err


def set_alias(database, tmp_path, capsys, alias, version):
    payload = tmp_path / (alias + ".json")
    payload.write_text(
        json.dumps(
            {
                "alias": alias,
                "actor": "operator",
                "rationale": "Readable URL",
                "expected_version": version,
            }
        )
    )
    return run(
        database, capsys, "venture", "alias", "--id", CROUS, "--input", str(payload)
    )


def test_alias_is_version_checked_unique_and_audited(crous, capsys):
    factory, database, _, tmp_path = crous
    with factory() as session:
        version = session.get(Venture, CROUS).version_id
    code, out, err = set_alias(database, tmp_path, capsys, "v-crous-queue", version)
    assert code == 0, err
    assert json.loads(out)["alias"] == "v-crous-queue"
    code, out, _ = set_alias(database, tmp_path, capsys, "v-crous-queue", version)
    assert code == 0 and json.loads(out)["changed"] is False
    code, _, err = set_alias(database, tmp_path, capsys, "v-other", version + 1)
    assert code == 2 and "another venture" in err
    code, _, err = set_alias(database, tmp_path, capsys, "v-renamed", version)
    assert code == 2 and "refresh" in err
    code, _, err = set_alias(database, tmp_path, capsys, "Crous Queue", version + 1)
    assert code == 2
    with factory() as session:
        event = session.scalar(
            select(AuditEvent).where(AuditEvent.event_type == "venture_alias_set")
        )
        assert event.payload["previous_alias"] is None
        assert event.payload["alias"] == "v-crous-queue"
    service = VentureAliasService(factory)
    with pytest.raises(ConflictError):
        service.set_alias(
            "v-other",
            AliasInput(
                alias="v-crous-queue",
                actor="x",
                rationale="Collision",
                expected_version=1,
            ),
        )


def test_read_commands_accept_id_selectors(crous, capsys):
    factory, database, venture, tmp_path = crous
    with factory() as session:
        version = session.get(Venture, CROUS).version_id
    assert set_alias(database, tmp_path, capsys, "v-crous-queue", version)[0] == 0
    ws = venture["workspace_id"]
    code, out, err = run(database, capsys, "venture", "show", "--id", "v-crous-queue")
    assert code == 0, err
    assert json.loads(out)["venture"]["id"] == CROUS
    assert json.loads(out)["venture"]["alias"] == "v-crous-queue"
    for args in [
        ["agent", "resume", "--id", "v-crous-queue", "--format", "json"],
        ["agent", "resume", "--id", ws, "--format", "json"],
        ["agent", "resume", "--venture-id", "v-crous-queue", "--format", "json"],
        ["agent", "resume", "--workspace-id", ws, "--format", "json"],
    ]:
        code, out, err = run(database, capsys, *args)
        assert code == 0, err
        state = json.loads(out)
        assert state["workspace_id"] == ws
        assert state["venture_state"]["alias"] == "v-crous-queue"
    selectors = [
        (["review", "show", "--id", "v-crous-queue"], "current"),
        (["decision-map", "show", "--id", CROUS], "scope"),
        (["result", "list", "--id", "v-crous-queue"], "items"),
        (["input", "list", "--id", "v-crous-queue"], "items"),
        (["venture-score", "show", "--id", "v-crous-queue"], "history"),
        (["workspace", "show", "--id", "v-crous-queue"], "config"),
        (["existing-project", "show", "--id", "v-crous-queue"], "current"),
        (["evidence", "list", "--id", "v-crous-queue"], "items"),
        (["work-item", "list", "--id", ws], "items"),
        (["outreach", "list", "--id", "v-crous-queue"], "items"),
        (["evidence", "list", "--venture-id", CROUS], "items"),
    ]
    for args, key in selectors:
        code, out, err = run(database, capsys, *args)
        assert code == 0, (args, err)
        assert key in json.loads(out), args
    code, _, err = run(database, capsys, "review", "show", "--id", "v-missing")
    assert code == 2 and "matches" in err


def test_console_redirects_alias_routes(crous, capsys):
    factory, database, _, tmp_path = crous
    with factory() as session:
        version = session.get(Venture, CROUS).version_id
    assert set_alias(database, tmp_path, capsys, "v-crous-queue", version)[0] == 0
    client = TestClient(
        create_app(factory, tmp_path / "requests"), base_url="http://127.0.0.1"
    )
    redirect = client.get("/ventures/v-crous-queue?tab=work", follow_redirects=False)
    assert redirect.status_code == 307
    assert redirect.headers["location"] == "/ventures/" + CROUS + "?tab=work"
    page = client.get("/ventures/v-crous-queue")
    assert page.status_code == 200 and "Crous Queue" in page.text
    api = client.get("/api/ventures/v-crous-queue/scores")
    assert api.status_code == 200 and api.json()["card_id"]
    assert client.get("/ventures/v-other").status_code == 200
    assert client.get("/ventures/v-unknown").status_code == 404


def test_json_ends_with_newline_and_info_logs_need_debug(crous, capsys):
    _, database, _, _ = crous
    code, out, err = run(database, capsys, "venture", "show", "--id", "v-other")
    assert code == 0 and out.endswith("}\n") and out.count("\n") == 1
    assert err == "", "no INFO lines without --debug"
    code, out, err = run(
        database, capsys, "agent", "resume", "--id", "v-other", "--format", "markdown"
    )
    assert code == 0 and out.endswith("\n") and not out.endswith("\n\n")
    code, out, err = run(
        database, capsys, "--debug", "venture", "show", "--id", "v-other"
    )
    assert code == 0 and out.endswith("\n")
    assert "command_started" in err and "INFO" in err
    code, out, err = run(database, capsys, "venture", "show", "--id", "missing")
    assert code == 2 and out == "" and "error:" in err
