"""Configuration precedence and invalid-value tests."""

from __future__ import annotations

from pathlib import Path

import pytest

from startup_foundry.cli import build_parser, get_settings
from startup_foundry.config import DEFAULT_DATABASE_URL, load_settings
from startup_foundry.errors import ConfigurationError


def test_configuration_precedence() -> None:
    parser = build_parser()
    default_args = parser.parse_args(["venture", "show", "--id", "venture-1"])
    assert get_settings(default_args, environment={}, dotenv={}).database_url == (
        DEFAULT_DATABASE_URL
    )
    assert get_settings(
        default_args,
        environment={"FOUNDRY_DATABASE_URL": "sqlite:///environment.db"},
        dotenv={"FOUNDRY_DATABASE_URL": "sqlite:///dotenv.db"},
    ).database_url == "sqlite:///environment.db"

    cli_args = parser.parse_args(
        ["--store", "cli.db", "venture", "show", "--id", "venture-1"]
    )
    assert get_settings(
        cli_args,
        environment={"FOUNDRY_DATABASE_URL": "sqlite:///environment.db"},
        dotenv={"FOUNDRY_DATABASE_URL": "sqlite:///dotenv.db"},
    ).database_url == "sqlite:///cli.db"


def test_debug_does_not_enable_sql_echo() -> None:
    arguments = build_parser().parse_args(
        ["--debug", "venture", "show", "--id", "venture-1"]
    )
    settings = get_settings(arguments, environment={}, dotenv={})
    assert settings.debug is True
    assert settings.sql_echo is False


def test_shared_settings_do_not_implicitly_read_a_dotenv_file(
    tmp_path: Path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.chdir(tmp_path)
    monkeypatch.delenv("FOUNDRY_DATABASE_URL", raising=False)
    # The default is defined relative to the home directory, not a developer's
    # XDG override, so the comparison must not depend on the caller's shell.
    monkeypatch.delenv("XDG_DATA_HOME", raising=False)
    (tmp_path / ".env").write_text(
        "FOUNDRY_DATABASE_URL=sqlite:///unexpected.db\n",
        encoding="utf-8",
    )

    assert load_settings().database_url == DEFAULT_DATABASE_URL


def test_boolean_settings_accept_documented_spellings_only() -> None:
    for raw in ("0", "false", "No", " OFF "):
        assert load_settings({"FOUNDRY_DEBUG": raw}).debug is False
    for raw in ("1", "true", "Yes", " on "):
        assert load_settings({"FOUNDRY_SQL_ECHO": raw}).sql_echo is True
    with pytest.raises(ConfigurationError, match="FOUNDRY_DEBUG must be one of"):
        load_settings({"FOUNDRY_DEBUG": "enabled"})


def test_blank_database_url_is_rejected_instead_of_defaulted() -> None:
    with pytest.raises(ConfigurationError, match="cannot be blank"):
        load_settings({"FOUNDRY_DATABASE_URL": "   "})
    assert (
        load_settings({"FOUNDRY_DATABASE_URL": " sqlite:///x.db "}).database_url
        == "sqlite:///x.db"
    )
