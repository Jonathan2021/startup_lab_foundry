"""SQLAlchemy persistence primitives for the Foundry.

The generic repository owns repetitive object persistence only.  It deliberately
does not commit: application use cases group repositories inside one
``UnitOfWork`` so a multi-record operation succeeds or rolls back as a unit.
"""

from __future__ import annotations

from types import TracebackType
from typing import Any, Generic, Literal, Self, TypeVar, cast

from sqlalchemy import create_engine, event, select
from sqlalchemy.engine import Engine
from sqlalchemy.engine.interfaces import DBAPIConnection
from sqlalchemy.orm import Session, sessionmaker
from sqlalchemy.pool import ConnectionPoolEntry

from startup_foundry.domain import IdentityMixin

ModelT = TypeVar("ModelT", bound=IdentityMixin)
SessionFactory = sessionmaker[Session]


class EntityNotFoundError(LookupError):
    """Raised when a required mapped entity does not exist."""

    def __init__(self, model: type[IdentityMixin], entity_id: str) -> None:
        self.model = model
        self.entity_id = entity_id
        super().__init__(f"{model.__name__} {entity_id!r} was not found")


def _enable_sqlite_foreign_keys(
    dbapi_connection: DBAPIConnection,
    _connection_record: ConnectionPoolEntry,
) -> None:
    """Enable SQLite foreign-key enforcement on every new DBAPI connection."""

    sqlite_connection = cast(Any, dbapi_connection)
    previous_autocommit = getattr(sqlite_connection, "autocommit", None)
    if previous_autocommit is not None:
        sqlite_connection.autocommit = True

    try:
        cursor = dbapi_connection.cursor()
        try:
            cursor.execute("PRAGMA foreign_keys=ON")
        finally:
            cursor.close()
    finally:
        if previous_autocommit is not None:
            sqlite_connection.autocommit = previous_autocommit


def create_db_engine(
    database_url: str,
    *,
    echo: bool = False,
    **engine_options: Any,
) -> Engine:
    """Create an engine without reading global configuration or opening a DB."""

    engine = create_engine(database_url, echo=echo, **engine_options)
    if engine.dialect.name == "sqlite":
        event.listen(engine, "connect", _enable_sqlite_foreign_keys)
    return engine


def create_session_factory(engine: Engine) -> SessionFactory:
    """Create the application's synchronous Session factory."""

    return sessionmaker(bind=engine, expire_on_commit=False)


class Repository(Generic[ModelT]):
    """Small generic CRUD adapter for one mapped entity type.

    ``add`` and ``delete`` only stage work in the supplied session. Objects
    returned by ``get``/``require`` are tracked, so ordinary attribute mutation
    is the update operation. ``save`` is provided for detached objects and
    returns the session-owned merged instance.
    """

    def __init__(self, session: Session, model: type[ModelT]) -> None:
        self.session = session
        self.model = model

    def add(self, entity: ModelT) -> ModelT:
        self.session.add(entity)
        return entity

    def add_all(self, entities: list[ModelT]) -> list[ModelT]:
        self.session.add_all(entities)
        return entities

    def get(self, entity_id: str) -> ModelT | None:
        return self.session.get(self.model, entity_id)

    def require(self, entity_id: str) -> ModelT:
        entity = self.get(entity_id)
        if entity is None:
            raise EntityNotFoundError(self.model, entity_id)
        return entity

    def list_all(self) -> list[ModelT]:
        statement = select(self.model).order_by(self.model.id)
        return list(self.session.scalars(statement))

    def save(self, entity: ModelT) -> ModelT:
        """Copy detached/current state into and return the session-owned entity."""

        return self.session.merge(entity)

    def delete(self, entity: ModelT) -> None:
        self.session.delete(entity)

    def delete_by_id(self, entity_id: str) -> bool:
        entity = self.get(entity_id)
        if entity is None:
            return False
        self.delete(entity)
        return True


class UnitOfWork:
    """Own one Session and transaction boundary for an application operation."""

    def __init__(self, session_factory: SessionFactory) -> None:
        self.session_factory = session_factory
        self.session: Session | None = None

    def __enter__(self) -> Self:
        if self.session is not None:
            raise RuntimeError("UnitOfWork cannot be entered more than once")
        self.session = self.session_factory()
        return self

    def repository(self, model: type[ModelT]) -> Repository[ModelT]:
        return Repository(self._active_session(), model)

    def _active_session(self) -> Session:
        if self.session is None:
            raise RuntimeError("UnitOfWork must be entered before repository use")
        return self.session

    def __exit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> Literal[False]:
        del exc_value, traceback
        session = self._active_session()
        try:
            if exc_type is None:
                try:
                    session.commit()
                except BaseException:
                    session.rollback()
                    raise
            else:
                session.rollback()
        finally:
            session.close()
            self.session = None
        return False
