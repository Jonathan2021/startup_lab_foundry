# Foundry-specific instructions

When this product is nested in Startup Lab, read its parent `AGENTS.md` first.
A standalone checkout follows the rules here and its public development/agent guides;
the parent workspace and its learning records are optional.

- Build the Foundry alongside named real ventures. Every capability must unblock a current venture task or record demonstrated friction.
- Implement the smallest capability that serves the current venture. Generalize only after substantially the same need recurs in real use.
- Prefer persistent evidence, decision rationale, artifacts, and history over prompt cleverness or autonomous-looking demos.
- External consequences require explicit human approval. Drafting is not authorization to send, buy, publish, provision, or delete.
- Current direction is `docs/CURRENT_DIRECTION.md` and root ADR-0008. Foundry is
  an internal tool under evaluation. Agent EvalOps is a deferred child-venture
  case study, independently retained under `agentevalops/`; it is not the default
  implementation customer. ADR-0009 delegates discovery across all portfolio
  ideas to the agent; G002 is one candidate, not the designated learning venture.
- Root ADR-0010 prioritizes useful Foundry operation and venture validation;
  learning/slices are paused. Use the permanent configured database and local
  console. Preserve original campaign snapshots. Record missing human inputs in
  `requests/INBOX.md` without replacing inline replies. Model training is deferred.
- Do not put evaluation datasets, release gates, model registries, certification status, or learner mechanics in the Foundry domain.
- Keep storage, provider, model, and action executors behind replaceable interfaces.
- Treat Foundry friction encountered in real venture investigations as evidence. Record it, then add only the narrow capability justified by recurring need and measured benefit.
- Do not pause the child venture to perfect a generic platform.

## Inquiry memory pilot

- Hindsight v0.10.2 is selected for the next real venture investigation using the
  Foundry foundation; installation and runtime benefit are not yet validated.
  Read `/home/jonathan/centralized/inquiry_memory/AGENTS.md`,
  `LIBRARY_SELECTION.md`, and `PILOT_PLAN.md` before helping with the trial.
- Consult Foundry's local records/memory before proposing tests. Keep inquiries,
  domain insights, counterevidence, and decision history local, retaining canonical
  record/artifact IDs. Optional trial notes can live under `docs/inquiry/`.
- Foundry owns its local Hindsight installation and data (proposed ignored volume:
  `.hindsight-data/`, not yet configured). Centralize only library/workflow feedback
  in `/home/jonathan/centralized/inquiry_memory/feedback/foundry/`, with local evidence
  links; central tooling insights help identify recurring shared-library needs.
- Foundry's database remains authoritative. The memory service is an optional
  adapter with a separate store; service failure must not block ordinary venture
  work. Preserve immutable record revisions and follow the central ingestion rules.
- Respect the current learning slice and human-control rules. This pilot does not
  authorize paid/cloud/external actions. ADR-0009 separately authorizes agent-owned
  discovery and justified support fixes; no learner implementation slice is active.
  Hindsight remains an optional comparison, not a mandatory integration.
  If the central folder is unavailable, keep pending
  tooling feedback locally and report the gap.

## Required Foundry workflow and feedback

Use Foundry to coordinate this repository's work. Read [docs/plans/2026-10-07-agent-dogfood/AGENT_HANDOFF.md](docs/plans/2026-10-07-agent-dogfood/AGENT_HANDOFF.md)
for the complete claim, context, result-review and recovery procedure. Run commands
from this repository; `.foundry/project.json` selects its venture/workspace, the
operator's store and the feedback destination.

Before starting an implementation package:

```bash
python3 tools/foundry_agent.py cli agent guide
python3 tools/foundry_agent.py resume
python3 tools/foundry_agent.py start --actor YOUR_AGENT_UNIQUE_SESSION
```

Read the saved context and relevant arrivals before editing. Claim only eligible
work in the assigned scope; do not steal a claim, silently pivot the venture or
create an empty replacement store. If the user's task differs from the reviewed
next package, reconcile the work scope rather than claiming an unrelated task.
Use `python3 tools/foundry_agent.py cli agent schema --name result` and the handoff
to submit checkpoint evidence, actual tests, limits and proposed next work. Preview
and resolve results only within your assigned review authority. A chat summary
alone does not update Foundry. No Codex-specific integration is required.

Report blocking Foundry defects immediately. At each package checkpoint, report
observed bugs, friction, improvement ideas or useful behavior; if none occurred,
say so in the checkpoint result rather than inventing feedback. To submit a report:

```bash
python3 tools/foundry_agent.py feedback-template > .foundry/feedback-input.json
# Fill descriptive fields; keep the generated UUID and venture/workspace IDs.
python3 tools/foundry_agent.py feedback --input .foundry/feedback-input.json
```

Use kind `bug`, `friction`, `idea` or `positive`. Include what you expected, what
happened, reproduction steps, impact, suggested improvement and sanitized evidence
paths. Keep secrets, personal data and confidential documents out of reports.

**Where it goes:** an immutable local outbox entry is saved as
`feedback/<UUID>.json`; successful delivery adds `feedback/<UUID>.receipt.json`.
The helper records it as evidence in **Foundry's own venture (`v-foundry`)**, using
`feedback_workspace_id` from the manifest, while retaining this source venture's
identity. It appears in Foundry's Now/unreviewed evidence for coordinator triage.
A receipt means recorded, not fixed. For failed delivery, retry the identical
outbox file with `feedback --input feedback/<UUID>.json`; use a new template/UUID
for a different report. Continue independent work during an outage only when its
ownership and scope are already established; reconcile on reconnection.

The repository-side helper is coordination tooling; application code must not
import it.
