# Foundry operation: real portfolio decision

- Record: FOUNDRY-OPS-20261002-001:r1
- Date: 2026-10-02
- Status: completed local CLI operation; retrieval utility trial remains pending
- Attribution: agent-operated support under the user's realignment request;
  not independent learner evidence or market validation
- Pre-run [plan](2026-10-02-portfolio-realignment-plan.md)
- Portable [commands, outputs, source hashes and snapshots](2026-10-02-foundry-records.json)

## What ran

Used the existing installed `startup_foundry` CLI with a dedicated ignored
`foundry/.local/portfolio-realignment.local.db`. Every one of 29 CLI invocations
returned exit code zero, including final reconstruction of all three ventures.
The pre-existing `foundry/foundry.db` was inspected read-only and preserved; it
contained zero ventures. No runtime feature was implemented to conduct the trial.

Persisted 3 ventures, 3 assumptions, 4 evidence records, 3 assessments, 3 decisions,
3 work items and 3 artifacts. SQLite integrity check returned `ok`; each recorded
decision links to its assessment and each assessment to evidence in its venture.
The source manifest includes content hashes rather than relying on dirty HEADs.

| Venture | Assumption → assessment → decision | Disposition |
|---|---|---|
| `v-evalops` | `a-evalops` → `as-evalops` → `d-evalops` | Paused; standalone implementation deferred, evidence weakens broad differentiation |
| `v-foundry` | `a-foundry` → `as-foundry` → `d-foundry` | Discovery; narrow to internal use and measure utility |
| `v-g002` | `a-g002` → `as-g002` → `d-g002` | Discovery; evidence inconclusive, bounded trial allowed |

The documentary research work items are done. `w-g002-trial` is **todo**, with its
experiment **planned**. Its recorded method, success and failure criteria match
the frozen protocol; no measured outcome is claimed. A database decision marked
`accepted` means an authorized internal planning disposition, not product-market
fit or learner review. Evidence confidence refers to the stated observation,
not a probability of commercial success.

Read a stored view from the repository root:

```bash
.venv/bin/python -m startup_foundry \
  --store foundry/.local/portfolio-realignment.local.db venture show --id v-g002
```

For reproduction use a **new** database, and replay the explicit argument arrays
in the JSON in order with the same CLI entry point. Existing IDs are deliberately
not overwritten. Creation times will differ; compare IDs, links, content and
statuses. The JSON retains input arguments and hashes plus output snapshots;
the local database is operational state and stays out of Git.

## Observed usefulness and friction

- Existing operations can preserve a real changed direction without a custom
  portfolio importer, provider system, agent-run implementation or EvalOps store.
- The evidence→assessment→decision links reconstruct successfully. This is useful
  functionality evidence, not a measured advantage over ordinary files.
- Recording this small case took 29 CLI invocations, with IDs and document links
  supplied manually. It is a plausible capture burden, but command runtime is not
  human working time and no net-benefit claim follows from this run.
- `venture show` exposes work-item summaries but omits experiment method and
  success/failure criteria. Those were retained in the command record, linked
  protocol and database; read-only inspection confirmed persistence. This is one
  observed reconstruction inconvenience, not yet justification for a new API.
- Evidence-source locators are placed in summaries and document artifacts in this
  CLI path. No automatic source freshness or citation validation was demonstrated.

No benchmark of source recovery, human time, record maintenance, memory quality
or buyer demand ran. Hindsight remains uninstalled/unvalidated; its comparison
is unavailable in this operation, not a failed tool. Keep the next trial bounded
and record recurrence before implementing even these small conveniences.
