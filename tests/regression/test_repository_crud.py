"""Regression tests for agent-owned generic persistence plumbing."""

from __future__ import annotations

from collections.abc import Iterator

import pytest
from sqlalchemy import text
from sqlalchemy.engine import Engine

from startup_foundry.config import ConfigurationError, load_settings
from startup_foundry.domain import Base, Portfolio
from startup_foundry.repository import (
    EntityNotFoundError,
    Repository,
    create_db_engine,
    create_session_factory,
)


@pytest.fixture
def engine() -> Iterator[Engine]:
    value = create_db_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(value)
    try:
        yield value
    finally:
        value.dispose()


def test_sqlite_factory_enables_foreign_keys_on_each_connection(
    engine: Engine,
) -> None:
    with engine.connect() as connection:
        assert connection.scalar(text("PRAGMA foreign_keys")) == 1


def test_debug_does_not_implicitly_enable_sensitive_sql_echo() -> None:
    settings = load_settings({"FOUNDRY_DEBUG": "true"})
    assert settings.debug is True
    assert settings.sql_echo is False

    with pytest.raises(ConfigurationError, match="FOUNDRY_SQL_ECHO"):
        load_settings({"FOUNDRY_SQL_ECHO": "sometimes"})


def test_generic_repository_handles_crud_without_owning_commits(
    engine: Engine,
) -> None:
    session_factory = create_session_factory(engine)

    with session_factory() as session:
        repository = Repository(session, Portfolio)
        repository.add(Portfolio(id="rollback", key="rollback", name="Rollback"))
        session.flush()
        session.rollback()

    with session_factory() as session:
        repository = Repository(session, Portfolio)
        assert repository.get("rollback") is None
        repository.add_all(
            [
                Portfolio(id="portfolio-b", key="b", name="Portfolio B"),
                Portfolio(id="portfolio-a", key="a", name="Portfolio A"),
            ]
        )
        session.commit()

    with session_factory() as session:
        repository = Repository(session, Portfolio)
        assert [item.id for item in repository.list_all()] == [
            "portfolio-a",
            "portfolio-b",
        ]
        detached = repository.require("portfolio-b")
        with pytest.raises(EntityNotFoundError, match="missing"):
            repository.require("missing")

    detached.name = "Updated while detached"
    with session_factory() as session:
        repository = Repository(session, Portfolio)
        merged = repository.save(detached)
        assert merged is not detached
        session.commit()

    with session_factory() as session:
        repository = Repository(session, Portfolio)
        assert repository.require("portfolio-b").name == "Updated while detached"
        assert repository.delete_by_id("portfolio-a") is True
        assert repository.delete_by_id("missing") is False
        session.commit()

    with session_factory() as session:
        repository = Repository(session, Portfolio)
        assert [item.id for item in repository.list_all()] == ["portfolio-b"]
