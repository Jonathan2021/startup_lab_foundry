"""Read-only post-upgrade acceptance on an explicitly supplied backed-up store."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from alembic import command
from startup_foundry.human_inputs import HumanInputService
from startup_foundry.migrations import alembic_config
from startup_foundry.proposals import ProposalService
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.web import create_app


def verify(database: Path, baseline: Path, requests: Path) -> dict[str, object]:
    url = "sqlite:///" + str(database.resolve())
    factory = create_session_factory(create_db_engine(url))
    with (
        sqlite3.connect(database) as current,
        sqlite3.connect(baseline.as_uri() + "?mode=ro", uri=True) as old,
    ):
        assert current.execute("PRAGMA integrity_check").fetchall() == [("ok",)]
        assert not current.execute("PRAGMA foreign_key_check").fetchall()
        for table in [
            "reference_sources",
            "ideas",
            "idea_revisions",
            "idea_sources",
            "scorecards",
            "scoring_criteria",
            "idea_assessments",
            "criterion_scores",
            "criterion_score_evidence",
            "ranking_snapshots",
            "ranking_entries",
            "ventures",
            "artifacts",
            "evidence",
            "decisions",
            "workspace_reviews",
        ]:
            columns = [
                r[1] for r in current.execute("PRAGMA table_info(" + table + ")")
            ]
            index = columns.index("id")
            newer = {r[index]: r for r in current.execute("select * from " + table)}
            assert all(
                newer[r[index]] == r for r in old.execute("select * from " + table)
            ), table
        held = current.execute(
            "select id from work_items where status='ready' "
            "and workspace_id in (select workspace_id from ventures "
            "where id in ('v-physical','v-receipt'))"
        ).fetchall()
        assert not held
        request_rows = current.execute(
            "select id,status,response_artifact_id,review_artifact_id "
            "from human_requests order by id"
        ).fetchall()
    command.check(alembic_config(url))
    proposal = ProposalService(factory).list()["items"][0]
    assert proposal["state"] == "proposed"
    inputs = HumanInputService(factory, requests)
    assert not {"R008", "R009"} & {
        r["id"] for r in inputs.list(status="needs_you")["items"]
    }
    routes = [
        "/",
        "/ideas/P103",
        "/ventures/v-sports-session",
        "/ventures/v-sports-ranking",
        "/requests/R006",
        "/requests?status=needs_you",
        "/requests?status=deferred",
        "/proposals/" + proposal["id"],
        "/ventures/v-coopain?tab=software",
        "/ventures/v-coopain?tab=settings",
        "/ventures/v-route-repair?tab=history",
        "/ventures/v-sports-session?tab=scores",
    ]
    with TestClient(
        create_app(factory, requests), base_url="http://127.0.0.1"
    ) as client:
        statuses = {route: client.get(route).status_code for route in routes}
        assert set(statuses.values()) == {200}
        needs = client.get("/requests?status=needs_you").text
        assert (
            'href="/requests/R008"' not in needs
            and 'href="/requests/R009"' not in needs
        )
        assert "Review fusion proposal" in client.get("/ventures/v-sports-session").text
    return {
        "database": str(database),
        "schema_parity": "passed",
        "integrity": "ok",
        "foreign_keys": [],
        "preserved_original_records": True,
        "held_ready_work": held,
        "requests": request_rows,
        "proposal": proposal,
        "http": statuses,
        "browser": "pending: no enabled browser",
        "input_hashes": {
            str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in [requests / "INBOX.md", requests / "2026-10-04-followups.md"]
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--database", type=Path, required=True)
    parser.add_argument("--baseline", type=Path, required=True)
    parser.add_argument("--requests", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    result = verify(
        args.database.resolve(), args.baseline.resolve(), args.requests.resolve()
    )
    args.output.write_text(json.dumps(result, indent=2))
    print(
        "Passed: schema/integrity/FKs, retained records, quiet holds, "
        "pending proposal and 12 HTTP routes. Browser acceptance remains pending."
    )
