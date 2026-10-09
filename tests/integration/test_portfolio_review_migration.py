"""Upgrade retains pre-review records and agrees with mapped schema."""

from alembic.autogenerate import compare_metadata
from alembic.runtime.migration import MigrationContext
from sqlalchemy import insert, inspect, text

from alembic import command
from startup_foundry.domain import (
    Base,
    Portfolio,
    Venture,
    VentureStage,
    Workspace,
    WorkspaceKind,
    utc_now,
)
from startup_foundry.migrations import alembic_config, upgrade_database
from startup_foundry.repository import create_db_engine, create_session_factory


def test_upgrade_populated_previous_schema_and_metadata_parity(tmp_path):
    url = f"sqlite:///{tmp_path / 'old.db'}"
    command.upgrade(alembic_config(url), "7ce261002001")
    engine = create_db_engine(url)
    factory = create_session_factory(engine)
    # Write the pre-upgrade rows with that schema's columns: the current ORM maps
    # later additive columns (for example ventures.alias) the old schema lacks.
    with factory.begin() as s:
        s.add(Portfolio(id="portfolio-default", key="default", name="Foundry"))
        s.add(
            Workspace(
                id="ws-retained",
                portfolio_id="portfolio-default",
                key="retained",
                title="Retain",
                kind=WorkspaceKind.VENTURE,
            )
        )
        s.flush()
        s.execute(
            insert(Venture.__table__).values(
                id="retained",
                workspace_id="ws-retained",
                objective="No data loss",
                stage=VentureStage.DISCOVERY.value,
                budget_currency="EUR",
                version_id=1,
                created_at=utc_now(),
                updated_at=utc_now(),
            )
        )
    with engine.connect() as c:
        before = c.execute(
            text("SELECT workspace_id FROM ventures WHERE id = 'retained'")
        ).scalar_one()
    upgrade_database(url)
    with factory() as s:
        assert s.get(Venture, "retained").workspace_id == before
        assert s.execute(text("PRAGMA foreign_key_check")).all() == []
    with engine.connect() as c:
        assert "workspace_reviews" in inspect(c).get_table_names()
        assert (
            compare_metadata(
                MigrationContext.configure(
                    c,
                    opts={
                        "autogenerate_plugins": [
                            "alembic.autogenerate.*",
                            "~alembic.autogenerate.checkconstraint_byname",
                        ]
                    },
                ),
                Base.metadata,
            )
            == []
        )
        checks = inspect(c).get_check_constraints("workspace_reviews")
        assert any("revision >= 1" in x["sqltext"] for x in checks)
        assert any("business_validation" in x["sqltext"] for x in checks)
        assert any("prototype" in x["sqltext"] for x in checks)
        assert any("use_existing" in x["sqltext"] for x in checks)
    engine.dispose()
