# ADR 0013 Venture coordination and executor boundaries

Date: 2026-10-06. Status: **Accepted for the local lifecycle MVP** after the user
authorized implementation. Paid execution, training and hosted operation remain
deferred. ADR-0014 records the implemented coordination and context contracts.

## Context

The user reports unclear boundaries between portfolio management, venture work,
shared outreach and internal versus external agents. The repaired console has
substantial functionality, but task completion still assumes continued pursuit
and idea promotion can leave overlapping investigations. Current alternatives
already combine agent access, records and optional hosted execution. See the
[review and proposal](../inquiry/product-boundary-2026-10-06/REPORT.md).

## Decision

Own the evidence, decision and work handoff workflow for independently useful
venture workspaces. Portfolio scope owns allocation, comparison and fusion
decisions; it aggregates venture state instead of duplicating it. Shared services
retain explicit record ownership and permissions. Connected tools own detailed
operational data such as code, issues, accounting and email delivery.

Retain one modular monolith and the existing storage. Human UI, CLI and future
agent adapters use the same intention-level application operations. Default to
the user's external agent or manual execution. Add optional bounded Foundry
execution only after demonstrated need. Both routes use the same context,
authority, result and review rules; deterministic operations do not require a
model. Investigation completion supports continuing, narrowing, holding or stopping.

Keep provider-specific runners and transport protocols replaceable. Preserve
venture portability and scoped sharing as design requirements. This decision
does not claim export, remote permissions, a scheduler or MCP is implemented.
Prefer a small number of built-in optional views over a plugin framework.

## Alternatives and consequences

Portfolio-only minimizes operational scope but may be useful too infrequently.
A comprehensive venture suite competes with many mature specialist tools.
Splitting products now introduces synchronization before demand is established.
Owning all execution increases cost and provider dependence; external-only
execution may make onboarding and unattended work harder. Optional execution
allows later adjustment without changing canonical venture records.

This proposal narrows the product around a recurring job but could still be
unnecessary compared with files and existing tools. It requires low-upkeep
capture, clear task outcomes and reliable handoffs, not merely more schemas.

## Revisit conditions

Evaluate the proposed matched handoff trial before a broad redesign. Reconsider
scope if portfolio allocation, single-venture continuity or unattended execution
is the only behavior users repeatedly value. Commercial expansion requires
independent operator usage and commitment. Extract services or introduce a
plugin runtime only after recurring integration requirements justify them.
