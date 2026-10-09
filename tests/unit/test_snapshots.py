"""Immutable JSON snapshots: keyed retries are idempotent, changes conflict."""

import pytest

from startup_foundry.application import FoundryApplication
from startup_foundry.domain import Artifact, VentureStage
from startup_foundry.errors import ConflictError, ReferenceError
from startup_foundry.migrations import upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory
from startup_foundry.snapshots import read_snapshot, snapshot, transaction

SCHEMA = "test-snapshot/v1"


@pytest.fixture
def store(tmp_path):
    url = f"sqlite:///{tmp_path / 'snapshots.db'}"
    upgrade_database(url)
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    workspaces = [
        FoundryApplication(factory).create_venture(
            venture_id=venture_id,
            name=venture_id,
            objective="Fixture",
            stage=VentureStage.DISCOVERY,
        )["workspace_id"]
        for venture_id in ["v-one", "v-two"]
    ]
    yield factory, workspaces
    engine.dispose()


def test_keyed_snapshot_retry_returns_the_original_record(store):
    factory, (workspace, _) = store
    with transaction(factory) as session:
        first = snapshot(session, workspace, SCHEMA, {"a": 1, "b": [2]}, key="k")
        first_id = first.id
    with transaction(factory) as session:
        retry = snapshot(session, workspace, SCHEMA, {"b": [2], "a": 1}, key="k")
        assert retry.id == first_id
    with factory() as session:
        assert read_snapshot(session, first_id, workspace, SCHEMA) == {
            "a": 1,
            "b": [2],
        }


def test_reused_key_with_different_content_conflicts_without_writing(store):
    factory, (workspace, _) = store
    with transaction(factory) as session:
        original = snapshot(session, workspace, SCHEMA, {"a": 1}, key="k").id
    with pytest.raises(ConflictError, match="different content"):
        with transaction(factory) as session:
            snapshot(session, workspace, SCHEMA, {"a": 2}, key="k")
    with factory() as session:
        assert read_snapshot(session, original, workspace, SCHEMA) == {"a": 1}


def test_unkeyed_snapshots_are_separate_records(store):
    factory, (workspace, _) = store
    with transaction(factory) as session:
        first = snapshot(session, workspace, SCHEMA, {"a": 1}).id
        second = snapshot(session, workspace, SCHEMA, {"a": 1}).id
    assert first != second


def test_read_rejects_foreign_workspace_wrong_schema_and_tampering(store):
    factory, (workspace, other) = store
    with transaction(factory) as session:
        identity = snapshot(session, workspace, SCHEMA, {"a": 1}, key="k").id
    with factory() as session:
        for owner, schema in [(other, SCHEMA), (workspace, "other/v1")]:
            with pytest.raises(ReferenceError):
                read_snapshot(session, identity, owner, schema)
        with pytest.raises(ReferenceError):
            read_snapshot(session, "missing", workspace, SCHEMA)
    with factory.begin() as session:
        session.get(Artifact, identity).metadata_json = {"a": 2}
    with factory() as session:
        with pytest.raises(ReferenceError):
            read_snapshot(session, identity, workspace, SCHEMA)
