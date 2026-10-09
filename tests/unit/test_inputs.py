"""Bounded CLI JSON files are validated data, never partially accepted."""

import json
from argparse import Namespace

import pytest

from startup_foundry.errors import ValidationError
from startup_foundry.human_inputs import ClaimInput
from startup_foundry.inputs import read_input
from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.revamp_commands import dispatch


def test_valid_input_file_returns_the_typed_contract(tmp_path):
    path = tmp_path / "claim.json"
    path.write_text(json.dumps({"expected_version": 2, "actor": "operator"}))
    assert read_input(ClaimInput, str(path)) == ClaimInput(
        expected_version=2, actor="operator"
    )


def test_input_at_the_limit_is_read_and_one_byte_more_is_rejected(tmp_path):
    payload = json.dumps({"expected_version": 1, "actor": "a"})
    at_limit = tmp_path / "limit.json"
    at_limit.write_text(payload + " " * (100_000 - len(payload)))
    assert read_input(ClaimInput, str(at_limit)).actor == "a"

    oversized = tmp_path / "oversized.json"
    oversized.write_text(payload + " " * (100_001 - len(payload)))
    with pytest.raises(ValidationError, match="^JSON input exceeds 100 KB$"):
        read_input(ClaimInput, str(oversized))


@pytest.mark.parametrize(
    "content",
    [
        "{not json",
        json.dumps({"expected_version": 0, "actor": "operator"}),
        json.dumps({"expected_version": 1, "actor": "operator", "extra": True}),
    ],
)
def test_malformed_or_contract_violating_input_is_rejected(tmp_path, content):
    path = tmp_path / "input.json"
    path.write_text(content)
    with pytest.raises(ValidationError, match="^Invalid JSON input: "):
        read_input(ClaimInput, str(path))


def test_missing_input_file_is_an_actionable_validation_error(tmp_path):
    with pytest.raises(ValidationError, match="^Invalid JSON input: "):
        read_input(ClaimInput, str(tmp_path / "absent.json"))


@pytest.fixture
def sync(tmp_path):
    url = f"sqlite:///{tmp_path / 'inputs.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)

    def run(preview_path):
        arguments = Namespace(
            resource="input",
            action="sync",
            preview=str(preview_path),
            reconciliation=None,
        )
        return dispatch(factory, arguments, tmp_path / "requests")

    yield run
    engine.dispose()


def test_sync_preview_file_is_bounded_before_parsing(sync, tmp_path):
    oversized = tmp_path / "preview.json"
    oversized.write_text('{"items": []}' + " " * 100_000)
    with pytest.raises(ValidationError, match="^Sync preview exceeds 100 KB$"):
        sync(oversized)


@pytest.mark.parametrize("name", ["absent.json", "broken.json"])
def test_unreadable_sync_preview_is_rejected(sync, tmp_path, name):
    (tmp_path / "broken.json").write_text("{not json")
    with pytest.raises(ValidationError, match="^Cannot read sync preview JSON$"):
        sync(tmp_path / name)


def test_parsed_sync_preview_still_requires_the_preview_contract(sync, tmp_path):
    preview = tmp_path / "preview.json"
    preview.write_text(json.dumps({"unexpected": []}))
    with pytest.raises(ValidationError, match="Invalid file-sync preview"):
        sync(preview)
