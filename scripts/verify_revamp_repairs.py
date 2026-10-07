"""Read-only preservation and HTTP checks on an explicitly backed-up SQLite store."""

from __future__ import annotations

import argparse
import hashlib
import json
import sqlite3
from pathlib import Path

from fastapi.testclient import TestClient

from alembic import command
from startup_foundry.migrations import alembic_config
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.venture_scoring import VentureScoringService
from startup_foundry.web import create_app


def identifier(value: str) -> str:
    return '"' + value.replace('"', '""') + '"'


def verify(
    database: Path, baseline: Path, requests: Path, allowed_work_ids: list[str]
) -> dict[str, object]:
    changed_work = []
    with (
        sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as current,
        sqlite3.connect(baseline.as_uri() + "?mode=ro", uri=True) as old,
    ):
        assert current.execute("pragma integrity_check").fetchall() == [("ok",)]
        assert not current.execute("pragma foreign_key_check").fetchall()
        tables = [
            row[0]
            for row in old.execute(
                "select name from sqlite_master where type='table' "
                "and name!='alembic_version'"
            )
        ]
        for table in tables:
            columns = [
                r[1]
                for r in old.execute("pragma table_info(" + identifier(table) + ")")
            ]
            query = (
                "select "
                + ",".join(map(identifier, columns))
                + " from "
                + identifier(table)
            )
            key = columns.index("id")
            rows = {r[key]: r for r in current.execute(query)}
            for prior in old.execute(query):
                assert prior[key] in rows, (table, prior[key], "missing")
                newer = rows[prior[key]]
                if newer != prior:
                    assert table == "work_items" and prior[key] in allowed_work_ids, (
                        table,
                        prior[key],
                        "changed",
                    )
                    changed = [
                        name
                        for index, name in enumerate(columns)
                        if prior[index] != newer[index]
                    ]
                    assert set(changed) <= {
                        "status",
                        "owner",
                        "updated_at",
                        "version_id",
                        "blocked_reason",
                    }, changed
                    changed_work.append(
                        {
                            "id": prior[key],
                            "changed_fields": changed,
                            "previous_status": prior[columns.index("status")],
                            "current_status": newer[columns.index("status")],
                        }
                    )
        proposal = current.execute(
            "select id,state,revision_artifact_id from portfolio_proposals where id=?",
            ("91fe8686-6638-5dba-bb0a-34fe222a0be5",),
        ).fetchone()
        assert proposal and proposal[1] == "proposed"
        assert not current.execute(
            "select id from work_items where status='ready' and workspace_id in "
            "(select workspace_id from ventures "
            "where id in ('v-physical','v-receipt'))"
        ).fetchall()
        assert current.execute(
            "select id,status from human_requests "
            "where id in ('R008','R009') order by id"
        ).fetchall() == [("R008", "deferred"), ("R009", "deferred")]
        before_get = {
            table: current.execute(
                "select count(*) from " + identifier(table)
            ).fetchone()[0]
            for table in tables
        }
    url = "sqlite:///" + str(database)
    command.check(alembic_config(url))
    factory = create_session_factory(create_db_engine(url))
    score = VentureScoringService(factory).show("f0b5abfe-0274-42f7-9c9a-72dcbe68c116")[
        "current"
    ]
    assert score["coverage"] == 3 and score["total"] is None
    routes = [
        "/",
        "/ideas/P103",
        "/ventures/v-sports-session?tab=scores&score_view=original",
        "/ventures/v-sports-session?tab=work",
        "/requests/R006",
        "/requests/R011",
        "/ventures/v-coopain?tab=software",
        "/proposals/" + proposal[0],
        "/ideas/a32e67a1-2289-46b4-b12a-d24d2032ef2c",
        "/ventures/f0b5abfe-0274-42f7-9c9a-72dcbe68c116",
        "/ventures/v-route-repair?tab=history&limit=1",
        "/help",
    ]
    with TestClient(
        create_app(factory, requests), base_url="http://127.0.0.1"
    ) as client:
        responses = {route: client.get(route).status_code for route in routes}
        assert set(responses.values()) == {200}, responses
        assert (
            client.get(
                "/ventures/v-sports-session?tab=history&offset=bogus"
            ).status_code
            == 400
        )
        assert (
            client.get("/ventures/v-sports-session?score_view=not-real").status_code
            == 404
        )
        needs = client.get("/requests?status=needs_you").text
        assert (
            'href="/requests/R008"' not in needs
            and 'href="/requests/R009"' not in needs
        )
    with sqlite3.connect(database.as_uri() + "?mode=ro", uri=True) as current:
        assert all(
            current.execute("select count(*) from " + identifier(table)).fetchone()[0]
            == count
            for table, count in before_get.items()
        ), "GET appended records"
    return {
        "database": str(database),
        "integrity": "ok",
        "foreign_keys": [],
        "schema_parity": "passed",
        "preserved_original_tables": tables,
        "authorized_work_changes": changed_work,
        "pending_sports_proposal": proposal,
        "crous_score": {
            "id": score["id"],
            "coverage": score["coverage"],
            "total": score["total"],
        },
        "http": responses,
        "invalid_offset": 400,
        "unknown_card": 404,
        "get_appended_records": False,
        "browser": (
            "pending: inventory empty; creating iab returns Browser is not available"
        ),
        "request_hashes": {
            str(p): hashlib.sha256(p.read_bytes()).hexdigest()
            for p in requests.glob("*.md")
        },
    }


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    for name in ["database", "baseline", "requests", "output"]:
        parser.add_argument("--" + name, type=Path, required=True)
    parser.add_argument("--allowed-work-id", action="append", default=[])
    args = parser.parse_args()
    result = verify(
        args.database.resolve(),
        args.baseline.resolve(),
        args.requests.resolve(),
        args.allowed_work_id,
    )
    args.output.write_text(json.dumps(result, indent=2) + "\n")
    print(
        "Passed: preserved original records, integrity/FKs/parity, live routes, "
        "holds and Crous partial score. Visual acceptance pending."
    )
