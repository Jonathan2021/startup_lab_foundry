# ADR 0018 — Accepted result lineage and standalone delivery

Status: accepted, 2026-10-08.

## Context

A venture agent reported that an accepted correction left the earlier proposal
listed as requiring reconciliation. Separately, a completed delivery in a Git
worktree left the canonical checkout stale. A fresh Foundry clone also lacked the
Makefile invoked by its README. These are observed recovery/delivery problems.

## Decision

Project accepted replacement lineage in result show/list/resume and the console.
An unresolved original becomes `superseded` only if an accepted descendant exists;
`superseded_by` identifies the latest accepted replacement. Walk chains within the
workspace independently of result-list pagination. Preserve original proposals,
digests, receipts and stale reasons. Pending/rejected/deferred proposals cannot
retire historical work. Existing acceptance/ownership guards remain unchanged.

Publish standalone development commands and usage/recovery guidance. Verify an
installed wheel from an empty cwd with locked runtime dependencies in both Python
CI jobs. Keep operator manifests local and ship a portable example. State canonical
checkout, worktree, local commit, remote branch and exact CI SHA separately in
agent delivery reports. Git actions remain under existing explicit authorization.

## Consequences and revisit

No database migration, authentication change or automatic agent/Git execution.
Lineage is a read projection, not a fabricated resolution. Review query cost if
large result histories make resume slow. Keep physical/market validation separate
from product tests. If concurrent authenticated agents or hosted users become a
real requirement, design authorization independently of trusted local actor labels.

Release validation and operational limits: [release readiness](../RELEASE_READINESS.md).
