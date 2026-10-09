# ADR-0015: Repository agent handoffs and durable feedback

Date: 2026-10-07. Status: accepted for local dogfooding.

## Context

Preparing six independent venture repositories exposed repeated reconstruction
of Foundry IDs, stale product names and no consistent route for implementation
agents to return tool feedback. The lifecycle CLI already supplies claims,
immutable context, guarded result resolution and evidence capture. Replacing that
with an agent service would add a second authority before demonstrating a need.

## Decision

Each repository has a small `.foundry/project.json` manifest and a copied,
hash-identified standard-library CLI bridge. The manifest names the CLI argv,
store, venture, workspace and Foundry feedback workspace. The bridge claims work,
prepares context and releases its exact claim if preparation fails. Application
runtime code never imports Foundry. Existing result preview/resolution remains
the review boundary; the bridge neither executes models nor accepts results.

Feedback is retained as an immutable local JSON report before delivery through
`change record`. Its UUID becomes an idempotency key; a separate receipt confirms
delivery. Ideas remain inference, reported observations remain observations, and
neither is automatically accepted as a product requirement. Source venture identity
is checked. The coordinating agent reviews feedback in Foundry's own workspace.

Add a version-checked workspace rename operation to correct product scope labels,
retaining old/new titles, actor and rationale as an immutable artifact. Prepared
contexts retain the old name and become stale through existing scope guards.

Use one active writer per venture initially. Across repositories, separate agents
can work independently. Actor names are attribution in a trusted local store,
not authentication. Claims persist until explicitly released; there is no worker,
lease scheduler, automatic recovery or hosted collaboration promise.

## Consequences

An agent can start from its repository and return feedback during a Foundry outage.
The CLI remains usable without the helper. Copies require explicit hash/version
updates; paths are operator-local configuration and must be changed on a different
machine. Never replace a missing configured store with a new empty one.

Regression tests cover conflict, failure/release, stale context and retry/dedup.
Six actual repository starts were replayed on an isolated copy of the live store;
the preparation does not establish real implementation productivity or cost savings.

## Revisit

After one real package each from Volley Match and Crous, review context omissions,
recovery steps and repeated feedback. Add a stronger transport, shared installation,
lease handling or authenticated collaboration only when recorded failures require
it. See [campaign evidence](../inquiry/priority-mvps-2026-10-07/REPORT.md).
