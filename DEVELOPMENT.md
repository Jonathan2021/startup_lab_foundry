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

After Slice 003:

- `make test-repository` covers parent-repository source-document boundaries;
- `make test-product` covers fast Foundry unit, persistence, CLI, and package
  behavior without Docker or parent-repository assumptions;
- `make test-container` covers the complete local Compose/image/PostgreSQL
  acceptance path;
- `make test-ci` covers the accepted workflow structure;
- `make test-regression` combines the completed repository, product, container,
  and CI behavior from Slices 001-003;
- `make test-slice` reports that no next slice is prepared;
- `make lint` and `make typecheck` enforce the production-Python contract; and
- `make check` runs all of the above.

Do not weaken, skip, or delete acceptance checks to make them green. Routine
test organization and coverage are agent-owned; learner work remains focused on
the active slice's implementation and diagnosis.

## CI slice

Slice 003's [review](../learning/slices/003-github-actions-ci-fundamentals/FEEDBACK.md)
and [implementation notes](../learning/slices/003-github-actions-ci-fundamentals/IMPLEMENTATION_NOTES.md)
record the accepted workflow and learner/agent attribution. The CI contract,
dependency maintenance, routine documentation, PostgreSQL integration test, and
post-merge production hardening are agent-owned.

This workflow is verification only. It must not require a repository secret,
publish an image, deploy, mutate repository settings, or obtain cloud identity.

## Local data

Use a path ending in `.local.db` for SQLite experiments so Git ignores it. Keep
WAL/SHM sidecars out of Git as well. Never store credentials or sensitive
customer traces in the workspace. The completed container slice adds only a
local PostgreSQL container; it has no provider integration or cloud
requirement.

## Container lifecycle

Read the [Slice 002 brief](../learning/slices/002-foundry-containerization/BRIEF.md),
[TODO](../learning/slices/002-foundry-containerization/TODO.md), and
[acceptance contract](../learning/slices/002-foundry-containerization/ACCEPTANCE.md)
before continuing container work. The accepted topology keeps Foundry as an
ephemeral CLI, uses a healthy PostgreSQL service plus one-shot migration, and
does not publish the database port. Runtime configuration is local and must not
be baked into the image or committed.

The configuration scaffold currently reads real process environment variables:

| Variable | Default | Purpose |
|---|---|---|
| `FOUNDRY_DATABASE_URL` | `sqlite:///foundry.local.db` | SQLAlchemy/Alembic database |
| `FOUNDRY_DEBUG` | `false` | Application diagnostic mode |
| `FOUNDRY_SQL_ECHO` | `false` | Explicit SQL statement/parameter echo |

For a host CLI, copy `.env.example` to `.env`. For Compose development, copy it
to `.env.dev`, replace the password placeholder with a generated URL-safe local
value, and run from `foundry/`. Compose passes that product-local file to every
service, so later `docker compose run` commands do not need to repeat
`--env-file`. Both populated files are ignored and must not be committed.

`python-dotenv` affects only the CLI adapter, which merges sources in this
order: CLI options, real process environment, `.env`, safe local default. The
shared settings parser and Alembic do not search for dotenv files implicitly;
Compose supplies their process environment. SQL echo remains separate from
DEBUG because emitted bound parameters can disclose venture data. Expected
errors carry a correlation ID in stderr logs without logging command payloads.

## Container commands

Run these from the repository root after copying `foundry/.env.example` to the
ignored `foundry/.env.dev` and replacing its password placeholder:

```bash
make foundry-up
make foundry FOUNDRY_ARGS='venture show --id venture-1'
make foundry-down
```

`foundry-up` waits for a healthy database and runs the migration. `foundry`
starts one ephemeral CLI container. `foundry-down` removes containers and the
network but preserves PostgreSQL data. To deliberately delete that data, run
`make foundry-reset CONFIRM=yes`; the confirmation prevents an accidental
volume reset.

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

- `src/startup_foundry/` — completed narrow Stage 0 product package.
- `tests/unit/` — focused application, configuration, migration, and transaction
  behavior.
- `tests/integration/` — relational schema and repository integration.
- `tests/acceptance/` — CLI-workspace and container-stack end-to-end behavior.
- `tests/contract/` — package-boundary and accepted CI workflow structure.
- `.github/workflows/ci.yml` — read-only verification workflow with a
  learner-authored foundation and agent-authored production hardening.
- `docs/` — the preserved product brief plus future product documentation.
