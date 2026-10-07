# ADR-0008: Reconstruct stored experiment protocols in the venture view

- Status: Accepted
- Date: 2026-10-02
- Scope: additive, read-only Foundry CLI/application behavior

## Context

The earlier portfolio inquiry had to inspect the database or a separate document
to recover stored method/success/failure criteria. The new campaign reproduced
the same omission for the MLflow and change-monitor comparisons. See the saved
[before view](../inquiry/portfolio-campaign/trials/foundry-before.json), the frozen
[protocol](../inquiry/portfolio-campaign/trials/PROTOCOL.md), and prior
[operation record](../inquiry/2026-10-02-foundry-operation.md).

These are repeated internal operations, not independent customer-demand evidence.
The information already exists in Foundry's schema; a generic export service or
new persistence model is unnecessary.

## Decision

Add an `experiments` collection to `venture show`, containing experiment ID,
work-item ID, stored status, method, success/failure criteria, result summary and
linked assumption IDs. Query only work in that venture and order deterministically.
Preserve all existing response collections and commands. No schema migration or
implicit experiment-status transition is introduced.

## Consequences and validation

A paused investigation can recover its test criteria through the same supported
view as its assumptions and evidence. Existing JSON consumers must tolerate this
additive collection. Stored status remains faithfully reported; setting a work
item done does not currently synchronize the separate experiment lifecycle.

A behavior test was written and observed failing on the missing collection,
then passed after the change. It covers protocol content, assumption links,
deterministic reconstruction, ordinary work and isolation between two ventures.
The real [after view](../inquiry/portfolio-campaign/trials/foundry-after.json)
contains the two protocols. This agent-owned fix earns no learner slice credit.

## Revisit

Add targeted querying/export or explicit experiment-completion semantics only
when observed operation requires it. Do not generalize this small read-path fix
into a memory framework or automatic business decision engine.
