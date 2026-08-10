"""Alembic-backed application database lifecycle."""

from __future__ import annotations

from pathlib import Path

from alembic.config import Config

from alembic import command


def alembic_config(database_url: str, *, sql_echo: bool = False) -> Config:
    """Return an Alembic configuration independent of the process cwd."""

    project_root = Path(__file__).resolve().parents[2]
    config = Config(str(project_root / "alembic.ini"))
    config.set_main_option("script_location", str(project_root / "alembic"))
    config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))
    config.attributes["database_url"] = database_url
    config.attributes["sql_echo"] = sql_echo
    config.attributes["configure_logger"] = False
    return config


def upgrade_database(database_url: str, *, sql_echo: bool = False) -> None:
    """Bring an application database to the current checked-in revision."""

    command.upgrade(alembic_config(database_url, sql_echo=sql_echo), "head")
