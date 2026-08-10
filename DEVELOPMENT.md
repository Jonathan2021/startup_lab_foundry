# Foundry development

## Environment

Use Python 3.11 or newer. From the repository root:

```bash
make bootstrap
```

This uses `uv` and the committed `foundry/uv.lock` when available (including on
hosts whose Python lacks `ensurepip`). The fallback uses a standard-library
virtual environment and the equivalent `bootstrap` extra. Runtime dependencies
are limited to SQLAlchemy, Alembic, and python-dotenv; linting, typing, testing,
and coverage tools are development-only dependencies. Lower bounds admit
compatible security and bug-fix releases while the lockfile makes the normal
development install deterministic.

## Checks

```bash
make test-regression
make test-slice
make test
make lint
make typecheck
make check
```

At Slice 001 completion:

- `make test-regression` covers the preserved relational/schema groundwork;
- `make test-slice` covers the command contract and focused failure boundaries;
- `make lint` and `make typecheck` enforce the production-Python contract; and
- `make check` runs all of the above.

Do not weaken, skip, or delete acceptance checks to make them green. Add focused
unit tests for migration, transaction, reconstruction, and failure behavior;
do not duplicate the agent-owned schema regression tests.

## Local data

Use a path ending in `.local.db` for SQLite experiments so Git ignores it. Keep
WAL/SHM sidecars out of Git as well. Never store credentials or sensitive
customer traces in the workspace. The active slice has no external integrations
or cloud requirements.

The configuration scaffold currently reads real process environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `FOUNDRY_DATABASE_URL` | `sqlite:///foundry.local.db` | SQLAlchemy/Alembic database |
| `FOUNDRY_DEBUG` | `false` | Application diagnostic mode |
| `FOUNDRY_SQL_ECHO` | `false` | Explicit SQL statement/parameter echo |

Copy `foundry/.env.example` for local values. `python-dotenv` reads `.env`
without mutating the process environment; the CLI then merges sources in this
order: CLI options, real environment, `.env`, safe local default. A `.env` file
is ignored and must not be committed. SQL echo remains separate from DEBUG
because emitted bound parameters can disclose venture data. Expected errors
carry a correlation ID in stderr logs without logging command payloads.

## Database lifecycle

Every valid command applies checked-in Alembic migrations before opening its
application session. Startup never calls `Base.metadata.create_all()`. Each
application operation uses one `UnitOfWork`: repositories and use cases flush as
needed, while the unit of work alone commits or rolls back and closes the
session. This makes experiment work, experiment metadata, and assumption links
atomic.

## L-004 disposable migration drill

Run destructive downgrade practice only against a newly created disposable
directory, never against a venture database:

```bash
cd foundry
FOUNDRY_L004_TMP="$(mktemp -d)"
export FOUNDRY_DATABASE_URL="sqlite:///$FOUNDRY_L004_TMP/foundry.local.db"

../.venv/bin/alembic upgrade head
../.venv/bin/alembic current
../.venv/bin/alembic downgrade base
../.venv/bin/alembic upgrade head
../.venv/bin/alembic check
```

Your learner-owned verification should assert revision/table state and that no
default database appeared elsewhere; a successful command transcript alone is
not a transaction or migration test.

## Layout

- `src/startup_foundry/` — product package; currently learner-facing scaffolding.
- `tests/regression/` — completed behavior that must remain green.
- `tests/slice_001/` — executable active-slice contract.
- `tests/unit/` — learner-owned unit-test module.
- `docs/` — the preserved product brief plus future product documentation.
