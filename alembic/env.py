from logging.config import fileConfig

from sqlalchemy import pool

from alembic import context
from startup_foundry.config import load_settings
from startup_foundry.domain import Base
from startup_foundry.repository import create_db_engine

# this is the Alembic Config object, which provides
# access to the values within the .ini file in use.
config = context.config
database_override = config.attributes.get("database_url")
if database_override is None:
    settings = load_settings()
    database_url = settings.database_url
    sql_echo = settings.sql_echo
elif isinstance(database_override, str):
    database_url = database_override
    sql_echo = bool(config.attributes.get("sql_echo", False))
else:
    raise TypeError("Alembic database_url must be a string")
config.set_main_option("sqlalchemy.url", database_url.replace("%", "%%"))

# Interpret the config file for Python logging.
# This line sets up loggers basically.
if config.config_file_name is not None and config.attributes.get(
    "configure_logger", True
):
    fileConfig(config.config_file_name)

# add your model's MetaData object here
# for 'autogenerate' support
# from myapp import mymodel
# target_metadata = mymodel.Base.metadata
target_metadata = Base.metadata

# other values from the config, defined by the needs of env.py,
# can be acquired:
# my_important_option = config.get_main_option("my_important_option")
# ... etc.


def run_migrations_offline() -> None:
    """Run migrations in 'offline' mode.

    This configures the context with just a URL
    and not an Engine, though an Engine is acceptable
    here as well.  By skipping the Engine creation
    we don't even need a DBAPI to be available.

    Calls to context.execute() here emit the given string to the
    script output.

    """
    context.configure(
        url=database_url,
        target_metadata=target_metadata,
        literal_binds=True,
        dialect_opts={"paramstyle": "named"},
    )

    with context.begin_transaction():
        context.run_migrations()


def run_migrations_online() -> None:
    """Run migrations in 'online' mode.

    In this scenario we need to create an Engine
    and associate a connection with the context.

    """
    connectable = create_db_engine(
        database_url,
        echo=sql_echo,
        poolclass=pool.NullPool,
    )

    with connectable.connect() as connection:
        context.configure(
            connection=connection,
            target_metadata=target_metadata,
            autogenerate_plugins=[
                "alembic.autogenerate.*",
                "~alembic.autogenerate.checkconstraint_byname",
            ],
        )

        with context.begin_transaction():
            context.run_migrations()


if context.is_offline_mode():
    run_migrations_offline()
else:
    run_migrations_online()
