# Observed Foundry friction

| ID | Observation in this campaign | Effect | Treatment |
| --- | --- | --- | --- |
| DF-01 | No repository-side entry point tells a fresh agent its venture/workspace or where to report tooling feedback. Existing workspace issue metadata only classifies bug/security work. | Repeated ID reconstruction and feedback outside the tool. | Add small stdlib CLI bridge plus per-repo identity manifest. Retain one immutable outbox file before existing `change record`; no new domain or service. |
| DF-02 | `agent resume` for Foundry exposes an old ready visual-QA task even though the release record already completed those checks; no decision map existed in Foundry's own venture. | Agent could repeat completed work. | Supersede obsolete ready task with explicit rationale and install current campaign map. Keep history. |
| DF-03 | Root `make typecheck` ran mypy from a directory without Foundry's strict config. Standalone strict mypy caught a real error during the preceding push. | Root green was a weaker check than CI. | Name Foundry config explicitly and include the new bridge. |
| DF-04 | Route venture still titled Scenic ride repair; result narrowing can change objective, but no public command can rename an existing venture. Same mismatch for volleyball. | User sees a stale product scope; direct database editing would be required. | Add audited, version-checked workspace rename through the existing service/CLI, with stale-write regression. No change to immutable prior result context. |

These are observed coordination defects, not measured token savings. Actor strings
are audit attribution in a trusted local tool, not authentication. One writer per
venture at a time keeps shared-map invalidation understandable. Parallel work may
use different venture repositories; same-repo agents need worktrees and explicit
ownership. No scheduler or remote worker was started.

DF-05: In rehearsal, replacing an existing Crous map correctly marked the newly created research task as needing decision review. The agent recorder initially omitted an explicit keep treatment for that task, so its claim was refused. Corrected the recorder to review/keep that work in the same map revision. This was a guarded workflow requirement, not a product race or an excuse to bypass claims. Add this scenario to handoff guidance. The failed rehearsal was isolated from live data.
