# Repository instruction audit — 2026-10-07

The user requested explicit Foundry and feedback instructions in every prepared
venture repository. All seven already had uppercase `AGENTS.md`. The six venture
files linked detailed handoffs; Foundry's own file lacked the practical workflow.

All seven now contain a self-contained “Required Foundry workflow and feedback”
section: guide/resume/claim, context and scope checks, checkpoint submission,
authorized result review, feedback triggers, exact commands, sanitized fields,
local outbox/receipt paths, central destination and identical-payload retries.

| Repository instructions | Handoff exists | Helper matches configured hash | Feedback template has correct scope | Destination |
| --- | --- | --- | --- | --- |
| [Foundry](../../../AGENTS.md) | Pass | Pass | Pass | v-foundry |
| [Volley Match](../../../../volley-match/AGENTS.md) | Pass | Pass | Pass | v-foundry |
| [Ride Options](../../../../ride-options/AGENTS.md) | Pass | Pass | Pass | v-foundry |
| [Crous Queue](../../../../crous-queue/AGENTS.md) | Pass | Pass | Pass | v-foundry |
| [Volley Coach](../../../../volley-coach/AGENTS.md) | Pass | Pass | Pass | v-foundry |
| [Coopain](../../../../coopain/AGENTS.md) | Pass | Pass | Pass | v-foundry |
| [OfferCheck](../../../../offer-check/AGENTS.md) | Pass | Pass | Pass | v-foundry |

Verification read each file, checked its instruction/link/configuration coverage,
compared helper SHA-256 hashes and executed `feedback-template` from each repo.
No work was claimed and no artificial feedback was submitted for this audit.
Application code and helper behavior did not change; no product regression rerun
was needed for these documentation edits.

Feedback is retained at `feedback/<UUID>.json`; delivery receipts are at
`feedback/<UUID>.receipt.json`. The configured destination is Foundry workspace
`68afabed-a744-47df-94c1-7402f5c7b3b0`, with source venture/workspace attribution.
Blocking issues are reported immediately and observations at package checkpoints.
A receipt records delivery, not a promise that an issue is fixed.

This audit covers the seven active implementation tracks. Inactive learning and
the deferred Agent EvalOps project were not enrolled or given new work. Earlier
dated pack manifests remain snapshots; the AGENTS files were expanded afterward.
