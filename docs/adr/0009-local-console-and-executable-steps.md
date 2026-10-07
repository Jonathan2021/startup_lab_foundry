# ADR-0009: durable local console and bounded steps

Date: 2026-10-02. Status: accepted under the user's explicit product-first request.

## Context

The campaign persisted real evidence, but multiple SQLite paths and missing list/UI
operations made it hard to inspect and operate. The user now prioritizes Foundry
and viable ventures, pauses curriculum work, and requests file-based interventions.
The existing Idea/Revision/Source/WorkItem domain should be used rather than replaced.

## Decision

Use a cwd-independent SQLite default under the user's data directory, with the
existing database-URL override for PostgreSQL. Adopt a backed-up copy of the campaign
as the working database; preserve the original trial stores. Supply an explicit
backup operation. Add list/read and idea create/derive/promote operations through
application services over the existing domain.

Add one explicit step-run record for durable inputs, runner version, outcome and
idempotent submission, linked to WorkItem. Deterministic readiness/brief steps are
usable now. Agent work is an explicit handoff until a runner is configured; the
replaceable runner boundary does not authorize downloading/training models or
paid inference. Runs are evidence of execution, not proof of market validation.

Serve a local FastAPI/Jinja console over the same use cases. Bind loopback only,
validate Host/Origin and mutation tokens, escape source/model text, and expose no
arbitrary file reader or shell command. No hosted authentication platform is needed
for this single-user local scope. Sources and research notes remain untrusted data.
Editable intervention files are authoritative human replies; exact outgoing actions
still require explicit payload approval. No automatic send path is added.

## Consequences

A small HTTP dependency set is added and locked. One migration extends the existing
schema without changing the separate, deferred EvalOps contract. Synchronous bounded
local steps are sufficient initially; a durable worker is required before long or
concurrent agent jobs. An interrupted run is retained and recoverable, never silently
assumed successful. Backups are not replicated/off-machine disaster recovery.

## Revisit

Add PostgreSQL operation, authenticated remote access, background execution or
model training only when current usage requires them. Measure useful outcomes and
compare incumbents before turning internally generated drafts into new ventures.
