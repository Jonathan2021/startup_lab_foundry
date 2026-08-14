"""Alembic lifecycle checks against a disposable injected database."""

from __future__ import annotations

from pathlib import Path

from alembic.runtime.migration import MigrationContext
from sqlalchemy import create_engine, inspect

from alembic import command
from startup_foundry import migrations
from startup_foundry.migrations import alembic_config


def test_upgrade_downgrade_upgrade_uses_only_the_injected_database(
    tmp_path: Path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    monkeypatch.chdir(tmp_path)
    database = tmp_path / "migration.db"
    config = alembic_config(f"sqlite:///{database}")

    command.upgrade(config, "head")
    engine = create_engine(f"sqlite:///{database}")
    with engine.connect() as connection:
        assert MigrationContext.configure(connection).get_current_revision() == (
            "149fc56b9af9"
        )
        assert "ventures" in inspect(connection).get_table_names()
    engine.dispose()

    command.downgrade(config, "base")
    engine = create_engine(f"sqlite:///{database}")
    assert inspect(engine).get_table_names() == ["alembic_version"]
    engine.dispose()

    command.upgrade(config, "head")
    assert database.exists()
    assert not (tmp_path / "foundry.local.db").exists()


def test_installed_distribution_locates_packaged_migration_assets(
    tmp_path: Path, monkeypatch
) -> None:  # type: ignore[no-untyped-def]
    installed_root = tmp_path / "share" / "startup-foundry"
    (installed_root / "alembic").mkdir(parents=True)
    (installed_root / "alembic.ini").write_text("[alembic]\n", encoding="utf-8")
    fake_module = tmp_path / "lib" / "site-packages" / "startup_foundry" / "x.py"
    monkeypatch.setattr(migrations, "__file__", str(fake_module))
    monkeypatch.setattr(migrations.sysconfig, "get_path", lambda _name: str(tmp_path))

    config = migrations.alembic_config("sqlite:///installed.db")

    assert config.config_file_name == str(installed_root / "alembic.ini")
    assert config.get_main_option("script_location") == str(
        installed_root / "alembic"
    )
