"""Alembic-backed application database lifecycle."""

from __future__ import annotations

import sysconfig
from pathlib import Path

from alembic.config import Config

from alembic import command


def _migration_root() -> Path:
    """Locate migration assets in a source checkout or installed distribution."""

    source_root = Path(__file__).resolve().parents[2]
    installed_root = (
        Path(sysconfig.get_path("data")) / "share" / "startup-foundry"
    )
    for candidate in (source_root, installed_root):
        if (candidate / "alembic.ini").is_file() and (
            candidate / "alembic"
        ).is_dir():
            return candidate
    raise RuntimeError(
        "Alembic assets are missing from the Foundry source or installation"
    )


def alembic_config(database_url: str, *, sql_echo: bool = False) -> Config:
    """Return an Alembic configuration independent of the process cwd."""

    migration_root = _migration_root()
    config = Config(str(migration_root / "alembic.ini"))
    config.set_main_option("script_location", str(migration_root / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.attributes["database_url"] = database_url
    config.attributes["sql_echo"] = sql_echo
    config.attributes["configure_logger"] = False
    return config


def upgrade_database(database_url: str, *, sql_echo: bool = False) -> None:
    """Bring an application database to the current checked-in revision."""

    command.upgrade(alembic_config(database_url, sql_echo=sql_echo), "head")
