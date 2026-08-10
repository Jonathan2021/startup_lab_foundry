"""Configuration precedence and invalid-value tests."""

from __future__ import annotations

from startup_foundry.cli import build_parser, get_settings
from startup_foundry.config import DEFAULT_DATABASE_URL


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
