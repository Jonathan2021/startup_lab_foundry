"""Focused transaction behavior beyond the command acceptance path."""

from __future__ import annotations

from collections.abc import Iterator
from pathlib import Path

import pytest
from sqlalchemy import create_engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from startup_foundry.domain import IdentityMixin
from startup_foundry.repository import Repository, UnitOfWork


class TransactionBase(DeclarativeBase):
    """Independent metadata used only by this test module."""


class TransactionRecord(TransactionBase, IdentityMixin):
    __tablename__ = "test_models"


@pytest.fixture
def engine(tmp_path: Path) -> Iterator[Engine]:
    value = create_engine(f"sqlite:///{tmp_path / 'test.db'}")
    TransactionBase.metadata.create_all(value)
    try:
        yield value
    finally:
        value.dispose()


def test_failed_application_transaction_rolls_back_flushed_records(
    engine: Engine,
) -> None:
    session_factory = sessionmaker(bind=engine)
    with UnitOfWork(session_factory) as unit_of_work:
        repository = unit_of_work.repository(TransactionRecord)
        repository.add(TransactionRecord(id="existing"))

    with pytest.raises(RuntimeError, match="simulated application failure"):
        with UnitOfWork(session_factory) as unit_of_work:
            repository = unit_of_work.repository(TransactionRecord)
            repository.add_all(
                [TransactionRecord(id="first"), TransactionRecord(id="second")]
            )
            assert unit_of_work.session is not None
            unit_of_work.session.flush()
            raise RuntimeError("simulated application failure")

    assert unit_of_work.session is None
    with session_factory() as session:
        records = Repository(session, TransactionRecord).list_all()
        assert [record.id for record in records] == ["existing"]


class FailingCommitSession(Session):
    """Session that simulates a failure after pending rows reach the DBAPI."""

    def commit(self) -> None:
        self.flush()
        raise RuntimeError("simulated commit failure")


def test_commit_failure_rolls_back_and_closes_the_failed_session(
    engine: Engine,
) -> None:
    failing_factory = sessionmaker(bind=engine, class_=FailingCommitSession)
    with pytest.raises(RuntimeError, match="simulated commit failure"):
        with UnitOfWork(failing_factory) as unit_of_work:
            unit_of_work.repository(TransactionRecord).add(
                TransactionRecord(id="not-committed")
            )

    assert unit_of_work.session is None
    with Session(engine) as session:
        assert Repository(session, TransactionRecord).get("not-committed") is None
