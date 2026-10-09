# ADR 0014 Decision maps and agent context

Date: 2026-10-06. Status: **Accepted and implemented for the local lifecycle MVP**.
The user authorized completing the MVP, including code and synthetic trials.
Elaborates ADR-0013 within the existing product boundaries.

## Context

The user requests a changing decision graph that connects current work to future
possibilities, efficient use by external agents and a path to cheaper specialized
execution. Synthetic probes found verbose JSON larger than strong file briefs and
an unlinked relevant fact omitted by dependency selection. Current alternatives
already offer graphs and agent access. The useful behavior to test is safe,
low-effort maintenance when evidence or objectives change.

See the [experiment conclusions](../inquiry/wedge-experiments-2026-10-06/REPORT.md)
and [first-chunk contracts](../plans/2026-10-06-decision-backbone/CHUNK_1.md).

## Decision

Keep existing assumptions, experiments, evidence, assessments, decisions and work
authoritative. Add one DecisionMap coordination head per workspace and validated
immutable Artifact revisions. Map-owned content is limited to goals, questions,
conditional alternatives and explanatory relationships; actual work/decisions
are exact references to existing records. Freeze relevant mutable reference
content and manifests to retain historical meaning.

Serve concise task prose by default with source IDs and a small receipt manifest;
structured output remains available. Explicit dependency selection must expose
unclassified intake, missing required records, limits and exact fetch operations.
Never silently drop counterevidence to meet a context budget.

Store an executor's result separately from accepting its proposed effects.
Retain stale results without applying obsolete transitions. Recheck scope, map,
work, review and evidence-coverage versions at acceptance; commit exact approved
effects atomically and return repeat-safe receipts. Changed source content is a
candidate for review, not automatically a refutation. Future branches do not
start work. Explanatory feedback links and execution prerequisites have different
cycle rules.

Enforce unresolved accepted impacts through a shared execution-eligibility check
in existing claim/start paths and new handoff paths, not only a UI flag. Preserve
reconciliation access and unrelated work. This cannot terminate an already-running
external agent; that limitation remains visible to the operator.

Reuse the local CLI/console and single-user trust boundary. Defer remote auth,
MCP transport, paid execution and model training until the corresponding checkpoint.
An authorized agent can handle routine changes; existing human-control rules for
external consequences remain.

## Consequences and alternatives

This preserves the existing modular monolith and limits persistence expansion,
but typed artifact validation and reference checks become essential. Additive
migration/recovery and concurrency tests are required before live use.

Generic node/edge tables or a graph database are unnecessary at the proposed small
map size. Rebuilding task tracking, general memory or a discovery canvas would
duplicate substantial existing products. Files plus a skill remain a strong
baseline; an incumbent plus a small adapter may win the subsequent comparison.

## Revisit

Proceed beyond the local chunk only after scope/staleness/retry tests and a
synthetic fresh-agent walkthrough pass. Measure ongoing context/maintenance work
against competent files using the [predeclared repeated-update trial](../plans/2026-10-06-decision-backbone/REPLAY_PROTOCOL.md)
before a larger interface or executor investment. Introduce
training only after a fixed task, held-out quality evidence and whole-job economics
justify it. Revisit artifact-based storage only for demonstrated query/size needs.

## Implementation and limits

The implementation uses `decision_contracts.py`, `decision_maps.py`,
`agent_handoffs.py` and thin CLI/HTTP adapters. Migration `b10261006003` adds
only the coordination head. Existing domain records and immutable Artifacts
retain map, context, result and resolution history. Contexts have explicit byte
and record bounds; over-budget context fails rather than silently dropping facts.

Results distinguish a work decision from venture direction. Operating maturity
and scores do not change implicitly. Evidence absent from the selected context
is disclosed; accepting that limitation requires an explicit reason. Additional
proposed references are pinned at submission. SQLite coordination uses an
immediate write transaction; PostgreSQL uses head row locks and version checks.
An atomic acceptance preview rolls back the same transaction; new IDs in a
preview are provisional. Source timestamps normalize to UTC across both stores.

The CLI is the first external-agent integration. Managed agents, MCP, billing,
training and a hosted multi-user boundary remain later decisions. A running
external process cannot be stopped by changing a Foundry task status.
The [release report](../inquiry/lifecycle-mvp-2026-10-06/REPORT.md) records
functional and recovery checks. Cost savings and long-term user benefit remain
unmeasured; the comparative agent replay stays a future validation checkpoint.
