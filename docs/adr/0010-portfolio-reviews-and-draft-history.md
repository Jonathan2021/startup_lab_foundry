# ADR-0010: Portfolio reviews and local draft history

Date: 2026-10-04. Status: accepted for the authorized handoff.

## Context

Campaign dispositions reside in artifact JSON, making portfolio filtering and
resumption unreliable. Coopain already has a prototype but an unresolved payer;
these facts cannot share a lifecycle field. The inbox separately requests editable
outreach and scores with retained provenance.

## Decision

Add one append-only WorkspaceReview with ordered revisions and optimistic expected
revision checks. It records investigation stage, technical maturity, investment
choice and next action, referencing existing WorkItems for blockers. References
must stay in the workspace. Venture.stage keeps its original meaning. Import old
campaign metadata separately and idempotently, before current explicit reviews.

Reuse scoring tables with immutable scorecard versions and append-only assessments.
Original and reviewed views select one method and never impute missing scores.
Decimal arithmetic implements the workbook penalty offset and rounding.

Existing-project checkpoints are validated reference-only JSON Artifacts. HTTP
intake neither inspects nor runs repositories. Revisions append checkpoints.

Manual outreach uses ExternalAction PROPOSED with approval_required true. Each
content revision has an Artifact snapshot and AuditEvent; user-reported outcomes
are Evidence linked to the exact snapshot. No transport, approval or delivery
attempt is implemented. Attachment export reads only explicitly selected,
registered, digest-checked files inside configured local approved roots.

## Consequences

One schema migration; no campaign data in migrations. SQL latest-record queries
power HTML, JSON and CLI views. Unknown scores/maturity and not-scheduled work
remain visible. Draft export is usable without any provider or memory service.
SQLite revision uniqueness and optimistic counters reject concurrent stale edits;
PostgreSQL concurrency remains a separate disposable-database check.

## Revisit

Add a provider only after exact setup authorization and revision-bound approval,
uncertain-delivery reconciliation and duplicate-send controls. Reconsider the
review model if multiple concurrent investigation tracks actually require it.
