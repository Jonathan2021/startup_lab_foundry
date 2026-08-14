# ADR-0004: Containerized Foundry CLI and PostgreSQL lifecycle

- Status: Accepted
- Date: 2026-08-11

## Context

Slice 001 established a run-to-completion Foundry CLI, SQLAlchemy persistence,
and Alembic-managed SQLite workflow. Slice 002 must make that workload
reproducible in containers and verify it against PostgreSQL without inventing a
long-running API or coupling product runtime code to the learning environment.

The material choices are the image build/runtime boundary, ephemeral CLI and
one-shot migration process model, readiness ordering, runtime configuration and
secret flow, named-volume lifecycle, and safe teardown/reset interface.

## Decision

Keep Foundry as a run-to-completion CLI. Starting an ephemeral application
container for each command has overhead, but it matches the current product and
is preferable to keeping a fake process alive. A long-running FastAPI service is
allowed only when a real API/client workflow justifies it.

Use one multi-stage application image for both migration and CLI commands:

- a named build stage uses the committed `uv.lock`, a versioned uv image, and
  production-only synchronization;
- the runtime stage starts again from `python:3.13-slim`, copies only the
  installed environment and Alembic assets, excludes development tools, and
  runs as UID/GID 10001;
- `python:3.13-slim` intentionally follows patched 3.13 releases during local
  development, while uv is pinned to `0.11.29`; digest pinning and automated
  base refresh enter at the CI/release boundary rather than being simulated
  locally; and
- the image entrypoint remains `foundry`, while Compose overrides it only for
  the migration job.

Keep `docker-compose.yaml`, `.env.dev`, and `.env.example` inside the independent
`foundry/` product. Compose loads `.env.dev` through each service's `env_file`,
so `up` and later `run` invocations receive the same runtime configuration
without repeating the CLI `--env-file` option. The populated file is ignored by
Git and the build context. Standard `POSTGRES_*` variables configure the
database image; `FOUNDRY_DATABASE_URL`, `FOUNDRY_DEBUG`, and
`FOUNDRY_SQL_ECHO` remain namespaced application configuration so they cannot
collide when the Foundry is run alongside other products.

Compose owns three process roles:

- `db` is the only long-running service and reports readiness with
  `pg_isready`;
- `migrate` waits for database health, requires an explicit database URL,
  applies `alembic upgrade head`, and must complete successfully; and
- profiled service `foundry` runs one CLI command only after migration succeeds.

Do not assign fixed container names. Compose project names isolate concurrent
developer and acceptance stacks. Do not publish the PostgreSQL port to the
host. Persist PostgreSQL under the Compose project's `db_data` named volume.
Ordinary `docker compose down` preserves it; the deliberately destructive
`docker compose down --volumes` is reserved for an exact-project reset.

The CLI continues to apply migrations defensively for local SQLite and direct
invocations. The explicit Compose migration is therefore temporarily
idempotent/redundant. Remove implicit per-command migration only when a
long-running or replicated application has a separately controlled deployment
phase. SQLite remains a supported local adapter and regression target.

## Consequences

- A fresh application container is isolated, deterministic, non-root, and
  disposable; the cost is process startup latency on every CLI command.
- One image prevents migration and application dependency drift. Alembic assets
  remain in the runtime image even though ordinary CLI execution does not use
  them directly.
- Product-local `env_file` configuration fixes cross-invocation inconsistency,
  but it is local-development configuration, not production secret management.
  The shared file exposes PostgreSQL variables to application containers, so a
  production boundary must narrow access and use an actual secret mechanism.
- A floating Python minor tag receives patched releases on rebuild but is not
  bit-for-bit reproducible across time. CI must record/pin the resolved digest
  and define a refresh policy.
- The PostgreSQL volume survives normal teardown. An explicit volume reset is
  destructive and must remain separately named and documented.
- No API, worker, host database port, registry, or orchestration platform is
  introduced.

## Revisit when

Revisit when a real client needs a long-running API, concurrent replicas require
separate migration locking/control, production deployment requires scoped
secrets and database privileges, backup/restore becomes an operational
requirement, or CI publishes a versioned image. Those triggers may justify
FastAPI, a dedicated release job, digest pinning, or different configuration;
their presence on the roadmap alone does not.
