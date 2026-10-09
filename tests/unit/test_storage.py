"""Storage selection and backup refusals never leave a misleading file behind."""

import sqlite3

import pytest

from startup_foundry.errors import ValidationError
from startup_foundry.storage import (
    backup_sqlite,
    prepare_database_directory,
    sqlite_path,
)


@pytest.mark.parametrize(
    "url",
    [
        "postgresql+psycopg://user:secret@localhost:5432/foundry",
        "sqlite://",
        "sqlite:///:memory:",
    ],
)
def test_file_operations_require_a_file_backed_sqlite_store(url):
    with pytest.raises(ValidationError, match="file-backed SQLite"):
        sqlite_path(url)


def test_sqlite_path_is_absolute_and_resolved(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    assert sqlite_path("sqlite:///nested/../store.local.db") == (
        tmp_path.resolve() / "store.local.db"
    )


def test_prepare_creates_only_the_sqlite_parent_directory(tmp_path):
    database = tmp_path / "new" / "parent" / "store.local.db"
    prepare_database_directory(f"sqlite:///{database}")
    assert database.parent.is_dir()
    assert not database.exists()

    prepare_database_directory("sqlite:///:memory:")
    prepare_database_directory("postgresql+psycopg://user@localhost/foundry")


def test_backup_of_a_missing_source_creates_no_destination(tmp_path):
    destination = tmp_path / "backups" / "copy.local.db"
    with pytest.raises(ValidationError, match="does not exist"):
        backup_sqlite(f"sqlite:///{tmp_path / 'absent.local.db'}", destination)
    assert not destination.exists()


def test_failed_backup_removes_its_partial_destination(tmp_path):
    source = tmp_path / "not-a-database.local.db"
    source.write_text("plain text, not SQLite")
    destination = tmp_path / "copy.local.db"
    with pytest.raises(sqlite3.DatabaseError):
        backup_sqlite(f"sqlite:///{source}", destination)
    assert not destination.exists()
    assert source.read_text() == "plain text, not SQLite"


def test_backup_is_private_and_reports_verified_paths(tmp_path):
    source = tmp_path / "source.local.db"
    with sqlite3.connect(source) as connection:
        connection.execute("CREATE TABLE note (body TEXT)")
        connection.execute("INSERT INTO note VALUES ('kept')")
    connection.close()
    destination = tmp_path / "copy.local.db"

    receipt = backup_sqlite(f"sqlite:///{source}", destination)

    assert receipt == {
        "source": str(source.resolve()),
        "backup": str(destination.resolve()),
        "verified": True,
    }
    assert destination.stat().st_mode & 0o777 == 0o600
    with sqlite3.connect(destination) as copy:
        assert copy.execute("SELECT body FROM note").fetchall() == [("kept",)]
    copy.close()
