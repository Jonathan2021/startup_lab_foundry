"""Typed process configuration shared by CLI and migration adapters."""

from __future__ import annotations

import os
from collections.abc import Mapping
from dataclasses import dataclass
from pathlib import Path

from startup_foundry.errors import ConfigurationError


def data_directory(environment: Mapping[str, str] | None = None) -> Path:
    """Use one user-owned location, independent of the launch directory."""

    values = os.environ if environment is None else environment
    root = Path(values.get("XDG_DATA_HOME", str(Path.home() / ".local/share")))
    if not root.is_absolute():
        raise ConfigurationError("XDG_DATA_HOME must be an absolute path")
    return root / "startup-foundry"


DEFAULT_DATABASE_URL = (
    f"sqlite:///{Path.home() / '.local/share/startup-foundry/foundry.local.db'}"
)
TRUE_VALUES = frozenset({"1", "true", "yes", "on"})
FALSE_VALUES = frozenset({"0", "false", "no", "off"})


def _boolean_value(name: str, raw_value: str | None, *, default: bool) -> bool:
    if raw_value is None:
        return default
    normalized = raw_value.strip().lower()
    if normalized in TRUE_VALUES:
        return True
    if normalized in FALSE_VALUES:
        return False
    allowed = ", ".join(sorted(TRUE_VALUES | FALSE_VALUES))
    raise ConfigurationError(f"{name} must be one of: {allowed}")


@dataclass(frozen=True, slots=True)
class Settings:
    """Validated settings after configuration-source precedence is resolved."""

    database_url: str = DEFAULT_DATABASE_URL
    debug: bool = False
    sql_echo: bool = False


def load_settings(environment: Mapping[str, str] | None = None) -> Settings:
    """Load the currently supported operating-system environment source.

    A mapping parameter makes precedence and invalid-value tests deterministic.
    SQL echo is intentionally independent of DEBUG because SQL parameters may
    contain sensitive venture data.
    """

    values = os.environ if environment is None else environment
    database_url = values.get("FOUNDRY_DATABASE_URL")
    if database_url is None:
        database_url = f"sqlite:///{data_directory(values) / 'foundry.local.db'}"
    database_url = database_url.strip()
    if not database_url:
        raise ConfigurationError("FOUNDRY_DATABASE_URL cannot be blank")

    return Settings(
        database_url=database_url,
        debug=_boolean_value(
            "FOUNDRY_DEBUG", values.get("FOUNDRY_DEBUG"), default=False
        ),
        sql_echo=_boolean_value(
            "FOUNDRY_SQL_ECHO", values.get("FOUNDRY_SQL_ECHO"), default=False
        ),
    )
