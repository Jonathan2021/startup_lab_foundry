"""CLI dispatch for discovery records (in-process, isolated temporary store)."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Any

import pytest

from startup_foundry import cli


@pytest.fixture
def run(tmp_path, capsys):
    store = tmp_path / "cli.db"

    def invoke(*arguments: str, status: int = 0) -> Any:
        code = cli.main(["--store", str(store), *arguments])
        captured = capsys.readouterr()
        assert code == status, captured.err
        return json.loads(captured.out) if status == 0 else captured.err

    return invoke


def write(tmp_path: Path, name: str, payload: dict[str, Any]) -> str:
    path = tmp_path / name
    path.write_text(json.dumps(payload), encoding="utf-8")
    return str(path)


def test_discovery_loop_through_the_public_cli(run, tmp_path):
    transcript = tmp_path / "agentic_stack_ideas.md"
    transcript.write_text("AS01 eval replay\nAS02 memory audit\n", encoding="utf-8")
    flagged = run(
        "idea", "create", "--id", "AS01", "--title", "Eval replay",
        "--description", "Replay agent traces",
    )  # fmt: skip
    assert flagged["origin"] == "user_added"
    created = run(
        "idea",
        "create",
        "--input",
        write(
            tmp_path,
            "idea.json",
            {
                "id": "AS02",
                "title": "Memory audit",
                "description": "Inspect agent memory",
                "origin": "generated_new",
                "focused_mvp_scope": "Viewer",
            },
        ),
    )
    assert created["origin"] == "generated_new"
    assert created["focused_mvp_scope"] == "Viewer"
    source = run(
        "source",
        "register",
        "--input",
        write(
            tmp_path,
            "source.json",
            {
                "kind": "document",
                "title": "Agentic stack transcript",
                "locator": str(transcript),
                "idea_ids": ["AS01", "AS02"],
            },
        ),
    )
    assert source["created"] is True and len(source["digest"]) == 64
    listed = run("source", "list")
    assert listed["items"][0]["linked_ideas"] == 2
    assert run("source", "show", "--id", source["id"])["linked_ideas"] == 2
    link = run(
        "idea", "link-source", "--id", "AS01", "--source-id", source["id"],
        "--role", "validation", "--note", "Segment 2",
    )  # fmt: skip
    assert link["role"] == "validation" and link["created"] is True

    actor = run(
        "market-actor",
        "register",
        "--input",
        write(
            tmp_path,
            "actor.json",
            {"name": "Braintrust", "website": "https://braintrust.dev"},
        ),
    )
    assert run("market-actor", "list", "--query", "brain")["total"] == 1
    linked = run(
        "idea",
        "link-actor",
        "--id",
        "AS01",
        "--input",
        write(
            tmp_path,
            "link.json",
            {
                "actor_id": actor["id"],
                "relation": "competitor",
                "is_primary": True,
                "note": "Hosted eval platform; gap: local replay",
                "checked_on": "2026-10-09",
                "source_ids": [source["id"]],
            },
        ),
    )
    assert linked["created"] is True
    assert run("market-actor", "show", "--id", actor["id"])["links"][0]["idea_id"] == (
        "AS01"
    )
    revised = run(
        "idea",
        "revise",
        "--id",
        "AS01",
        "--input",
        write(
            tmp_path,
            "revision.json",
            {
                "title": "Local eval replay",
                "change_reason": "Hosted competitors; narrow to local",
                "authored_by": "discovery-agent",
            },
        ),
    )
    assert revised["receipt"]["revision_number"] == 2
    assert revised["idea"]["competition"][0]["name"] == "Braintrust"
    relation = run(
        "idea",
        "relate",
        "--input",
        write(
            tmp_path,
            "relation.json",
            {
                "source_idea_id": "AS02",
                "target_idea_id": "AS01",
                "kind": "combined_with",
                "rationale": "Same buyer",
            },
        ),
    )
    assert relation["kind"] == "combined_with"
    shown = run("idea", "show", "--id", "AS01")
    assert shown["relations"][0]["other_id"] == "AS02"
    assert [r["revision_number"] for r in shown["revisions"]] == [2, 1]
    comparison = run("idea", "compare", "--ids", "AS01", "AS02")
    assert [i["id"] for i in comparison["items"]] == ["AS01", "AS02"]
    assert comparison["items"][0]["total"] is None
    assert comparison["items"][0]["primary_competitors"] == ["Braintrust"]
    cohort = run("idea", "list", "--source-id", source["id"])
    assert cohort["total"] == 2
    assert run("score", "show", "--idea-id", "AS01")["history"] == []


def test_ambiguous_or_incomplete_creation_fails_before_opening_a_store(
    tmp_path, capsys
):
    store = tmp_path / "never.db"
    payload = write(tmp_path, "idea.json", {"title": "x", "description": "y"})
    for arguments in [
        ["idea", "create", "--input", payload, "--title", "Both"],
        ["idea", "create", "--title", "Only title"],
    ]:
        assert cli.main(["--store", str(store), *arguments]) == 2
        assert "error:" in capsys.readouterr().err
    assert not store.exists()


def test_invalid_inputs_report_actionable_errors(run, tmp_path):
    run("idea", "create", "--id", "X", "--title", "X", "--description", "X")
    error = run(
        "source",
        "register",
        "--input",
        write(
            tmp_path,
            "bad.json",
            {"kind": "document", "title": "t", "locator": "/absent/file.md"},
        ),
        status=2,
    )
    assert "does not exist" in error
    error = run(
        "idea",
        "revise",
        "--id",
        "X",
        "--input",
        write(tmp_path, "rev.json", {"title": "Y", "unknown": 1}),
        status=2,
    )
    assert "Invalid JSON input" in error
    error = run("idea", "compare", "--ids", "X", "missing", status=2)
    assert "missing" in error
