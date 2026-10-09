"""Local storage inspection and non-overwriting SQLite online backups."""

from __future__ import annotations

import sqlite3
from pathlib import Path

from sqlalchemy.engine import make_url

from startup_foundry.errors import ConflictError, ValidationError


def sqlite_path(database_url: str) -> Path:
    url = make_url(database_url)
    if (
        url.get_backend_name() != "sqlite"
        or not url.database
        or url.database == ":memory:"
    ):
        raise ValidationError("This operation requires a file-backed SQLite database")
    return Path(url.database).expanduser().resolve()


def prepare_database_directory(database_url: str) -> None:
    url = make_url(database_url)
    if url.get_backend_name() == "sqlite" and url.database not in (
        None,
        "",
        ":memory:",
    ):
        sqlite_path(database_url).parent.mkdir(parents=True, exist_ok=True, mode=0o700)


def backup_sqlite(database_url: str, destination: Path) -> dict[str, object]:
    """Consistent backup, including committed WAL content; never overwrite."""
    source = sqlite_path(database_url)
    destination = destination.expanduser().resolve()
    if not source.is_file():
        raise ValidationError("The SQLite source does not exist yet")
    destination.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        with destination.open("xb"):
            pass
    except FileExistsError as exc:
        raise ConflictError(
            "Backup destination already exists; choose a new name"
        ) from exc
    try:
        with sqlite3.connect(source.as_uri() + "?mode=ro", uri=True) as original:
            with sqlite3.connect(destination) as backup:
                original.backup(backup)
                if backup.execute("PRAGMA quick_check").fetchone() != ("ok",):
                    raise ValidationError("Backup integrity check failed")
        destination.chmod(0o600)
    except BaseException:
        destination.unlink(missing_ok=True)
        raise
    return {"source": str(source), "backup": str(destination), "verified": True}
