# Foundry-specific instructions

Read the root `AGENTS.md` first.

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
