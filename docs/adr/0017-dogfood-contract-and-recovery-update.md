# ADR 0017 Public discovery and explicit interrupted work recovery

Status: accepted for local use, 2026-10-07.

## Context

Six independent MVP agents used Foundry claims, contexts, results and feedback.
OfferCheck found that the published MapEdge schema omitted a runtime branch
requirement. Volley Coach mistook a focused context for missing roadmap nodes.
Ride Options and Crous Queue reported 60-second CLI timeouts. Coopain retained
an owned J03 package after its agent host failed to load workspace requirements.
The original reports remain in the owning operator workspace. See
[public release notes](../RELEASE_READINESS.md) for the shipped changes and checks.

## Decision

Ship agent contract and repository bridge revision `2026-10-07.2`. Static guide
and schema commands bypass configuration, migrations and database access. Stateful
commands retain existing storage and ownership checks. Publish conditional branch
requirements, an example, context map selection counts and an exact full-revision
retrieval command. Retain immutable historical contexts without retroactive edits.

Add a read-only bridge doctor for version/hash/configuration checks, configurable
bounded command timeouts and explicit `start --resume-owned`. Recovery verifies
the current work is in progress with the exact supplied actor, prepares new context
under current versions, and never claims or releases that existing work. A failed
recovery leaves ownership intact. Default start behavior is unchanged. No automatic
mutation retry or expired-lease takeover is introduced. Created IDs remain final
only in a resolution receipt; preview IDs remain explicitly provisional.

## Consequences

Agents can discover contracts during a store outage, verify their installed
bridge and recover their own interrupted context. Doctor checks configuration;
`resume` still verifies live records. This trusted local actor label is not an
authentication boundary. Version/hash checks identify the local update without
claiming a published package release or repairing the external agent host.

Timeouts were not reproduced during this review. Database-independent discovery
removes an unnecessary dependency; it does not prove the original timeout cause
or resolve every slow stateful operation. No database migration, runtime coupling,
model service, new transport or external-action authority is added.

## Revisit

Profile retained stateful latency if another timeout recurs. Add a transfer/lease
protocol only when multiple trusted writers need it, with explicit ownership
semantics. Generalize bridge distribution only if these seven local copies show
recurring deployment failures; current rollout verifies canonical hashes.
