# Foundry agent collaboration tranche

GO: continue the existing lifecycle MVP as the internal coordination tool. Add only demonstrated dogfood improvements. No managed-agent runtime, token billing, MCP server, generic plugin system or multi-user hosted service in this tranche.

Main commit 07ecb37 passed GitHub Python 3.11/3.13, PostgreSQL and image/Compose CI. Current campaign adds a stdlib CLI bridge, local feedback outbox and retry receipts. Actual inspection found an obsolete ready Foundry task and no decision map in its own venture; the campaign corrects the current map/queue while preserving old records. Parent-directory mypy omitted Foundry strict configuration; Makefile now names that configuration.

## F01 — Run one complete agent handoff per venture

Depends on: none.

Use prepared configs and maps; one writer per venture at a time, parallelism across venture repositories. Verify claim, prepare, result preview/accept, resume and feedback receipt. No production model service.

The campaign already passed the six repository startup rehearsals and helper
regressions. Do not repeat those as a substitute for this package. The next
checkpoint is actual V01 and Q01 implementation results, followed by a fresh agent
resuming their accepted next packages. Extend the same procedure to the other
ventures as their implementation starts; they need not all start simultaneously.

Acceptance: Every prepared repo resolves its own workspace and current work; stale/conflicting claims fail; failed feedback send is retained and retry is idempotent.

## F02 — Triage observed agent friction

Depends on: F01.

Inspect Foundry unreviewed feedback evidence plus local outboxes. Reproduce highest-impact issue, classify duplicate/accepted/deferred/rejected with rationale and link a bounded Foundry work item; do not treat every suggestion as mandatory.

Acceptance: At least one completed real venture package can be resumed by a fresh agent without reading full chat; retained feedback has decision and work reference or explicit defer reason.

## F03 — Improve context and queue behavior only where measured

Depends on: F02.

Measure time to identify work, context bytes, omitted information, stale submissions and manual recovery. Fix concrete recurring cases with regression tests. Keep provider/action/storage boundaries replaceable.

Acceptance: No source lost in context; changed evidence invalidates unsafe effects; completed work is absent from executable queue; app remains useful without the helper.

## F04 — Release the dogfood-supported local MVP update

Depends on: F03.

Run standalone lint/types/product/agent-kit/browser/container checks appropriate to changes, installed CLI and backup/restore. Update direction and one operator guide; preserve exact evidence IDs.

Acceptance: A clean checkout supports two separate venture agents and later review; no unconfigured external actions, no claimed commercial or token savings without measurement.

## Boundary

One completed package from volleyball and one from Crous before extending the platform. If manual helper/config work dominates, simplify commands based on the actual failures. Hosted collaboration and autonomous agents need separate requirements and threat/cost design.

The agent kit is repository-side coordination, not venture runtime coupling. Use existing Foundry change/evidence semantics for feedback; a new schema, ticket service or agent orchestrator is unnecessary until recurrence demonstrates a specific gap. Local Foundry is a trusted single-operator tool: actor fields are audit labels, not authentication identities. Never expose port 8765 to untrusted networks.
