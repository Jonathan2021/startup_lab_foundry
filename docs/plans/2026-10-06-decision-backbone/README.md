# Foundry direction and implementation checkpoints

Date: 2026-10-06. The original direction and checkpoints below remain the planning
record. The user subsequently authorized the complete local MVP and deferred
monetization. See [MVP scope](MVP.md), [implemented state](STATE.md) and the
[release report](../../inquiry/lifecycle-mvp-2026-10-06/REPORT.md).

## Chosen direction

Build a venture workbench that keeps **decisions, their supporting evidence and
the work that depends on them current**, through the agents the user already
uses. The user sees why today's step matters and what different outcomes would
lead to. The agent receives a concise current brief and submits a result through
reliable operations instead of reconstructing relationships and writing many
independent records by hand.

Start with a repeat founder or small studio using agents across several active
initiatives. One venture remains useful alone. The recurring entry point is
“resume this investigation with the latest evidence.” It does not require adopting
another chat interface or starting with a large portfolio of scored ideas.

The first paid specialty to investigate is **checking whether new source evidence
requires revisiting existing decisions**. A specialized cheap executor is a
credible route to better economics on that narrow task. The backbone defines the
job, supplies bounded inputs, evaluates the result and allows changing executor.
Training becomes an optimization of a measured task.

The [market review](../../inquiry/wedge-experiments-2026-10-06/LANDSCAPE.md) found
close alternatives, including Vistaly, Productboard Spark and Beads. The chosen
advantage is a hypothesis about reliable and low-effort decision maintenance;
graph canvases, agents and context storage are not new by themselves.

## What the experiments established

Eight invented cases cover discovery, security, suppliers, outreach, pricing,
competition, fusion and pivoting. Inputs and expectations were frozen before
execution. See the [full experiment](../../inquiry/wedge-experiments-2026-10-06/experiments/REPORT.md).

- Strong concise briefs used 13,605 UTF-8 bytes; structured packets used 22,288,
  **63.8% more**. Full organized dossiers used 22,437. Tokens and inference cost
  were not measured. Compact organization helps; JSON does not itself save context.
- Relationship selection recovered 39/40 required facts, missing an unlinked
  supplier cancellation. New/unclassified evidence must be visible; incomplete
  context must be labeled and offer a way to inspect the missing material.
- Ten test-only transition scenarios matched their expected behavior. They
  illustrate desired semantics, not production acceptance.
- Two fresh same-configuration agents reached the same four intended decisions
  from concise files and structured packets. There was no clear quality advantage.
  [Comparison](../../inquiry/wedge-experiments-2026-10-06/AGENT_COMPARISON.md)

Store explicit structure but serve concise task prose. The next proof is whether
maintaining and updating that structure saves repeated work safely. The oracle
file brief hides its curation effort; the graph hides its link-maintenance effort.
Both must be counted next. Agents can expand synthetic cases; the user does not
need to create examples or label a spreadsheet.

## Ordinary use

1. In their existing agent, the user says: “Continue the Crous investigation.”
2. Foundry supplies the current question, supporting and opposing evidence,
   missing inputs, and outcomes that could change the plan.
3. The agent does the authorized work or explicitly delegates a bounded task
   to a configured Foundry executor. No hidden paid chain.
4. The result arrives as findings plus proposed changes. Foundry retains late
   results even if the plan changed, while preventing obsolete effects.
5. A review shows the new evidence, affected decisions and exact work consequences.
   The user or an already authorized agent accepts, edits, rejects or defers.
6. The next session receives current state without reconstructing it.

Routine updates do not require a human click for each row. Agents draft the map
and act within delegated authority. External consequences retain exact approval
requirements. A saved answer or task does not mean a worker is running.

Global navigation remains Today, Ventures and Portfolio. A venture's Now page
shows its scope, qualified score, focus, decision map and next owner. The portfolio
owns allocation and fusion; it does not duplicate venture state. Shared outreach
uses a permitted contact identity with venture-specific messages and follow-ups.
Code, suppliers and revenue appear through relevant connections; specialist tools
retain their operational detail.

## A dynamic decision map

The map connects an intended outcome, current uncertainty, test, evidence conditions
and possible next moves. It shows upstream purpose and a short horizon ahead.

- Current work, possible future work and completed history are visually distinct.
- Outcomes include stop, hold, narrow, continue, conflicting evidence and unknown.
- Written conditions state what would justify a branch. Model scores are not
  proof, and invented numeric probabilities are unnecessary.
- Map changes include rationale and evidence. A new revision preserves the old
  map instead of rewriting the venture's history.
- A changed fact flags dependent decisions for review. It does not automatically
  make every descendant false, cancel everything, or prove a new branch correct.
- Feedback can revisit earlier questions. Execution prerequisites cannot contain
  cycles; explanatory relationships are not a general workflow engine.
- Unexpected outcomes can revise the map; its branches are not exhaustive.

## Crous example with hypothetical outcomes

Goal: determine whether useful local queue guidance is viable. Current question:
is an important student decision unsupported at Cuvier/Châtelet? The following
are invented possibilities, not new restaurant observations.

| Hypothetical finding | Next move | What that could lead to |
|---|---|---|
| Existing information meets the need | Stop the generic waiting-time thesis and preserve the rationale | Reopen only after evidence of a distinct important gap |
| Useful gap and feasible data access | Propose a bounded manual pilot | Test repeat usefulness, then a product/business model; narrow or stop if unsuccessful |
| Useful gap but no viable data access | Hold implementation and test data feasibility | Pilot only if that gate clears; otherwise retain the reasoned hold/stop |
| Coverage or need still unclear | Gather exact local evidence | Return to this decision without claiming validation |

If later evidence shows an incumbent supplies the missing information, Foundry
proposes re-review of that assumption and dependent pilot/build work. An unrelated
accessibility task stays unchanged. The review presents old rationale, new source
and the choice to keep, change or stop specific work.

The same mechanics apply to a supplier quote failing pilot constraints or a
software issue blocking a release. Each does not require a new business app.

## Macro steps and dependencies

| Chunk | Outcome and substeps | Depends on | Checkpoint |
|---|---|---|---|
| 1. One complete decision loop | Repair stop/hold and duplicate intake; retain a small versioned map; prepare concise scoped context; reconcile results; show affected work/history | Existing application and synthetic suite | A fresh agent completes the local loop, including a changed premise, without direct SQL or history loss |
| 2. Fit ordinary agent sessions | Add one thin local integration if CLI friction warrants it; make resume/context/result operations discoverable; let the user's agent draft maps; measure updates and usage | Chunk 1 correctness | Repeated handoffs reduce reconstruction/upkeep versus equally good files without critical omissions or wrong-scope effects |
| 3. One optional executor | Fix source-change impact contract; build held-out cases; compare prompted cheap and strong models; include validation/escalation; trial on demand before scheduling | Chunk 1 contract, Chunk 2 integration, separately authorized inference budget | Comparable accepted-result quality at lower total cost, or documented convenience worth paying for |
| 4a. Make recurring execution reliable | Add freshness, repeat-safe retries, cancellation acknowledgements, budgets, monitoring and recovery | Chunk 3 working on-demand job and approval for any paid hosting | Scheduled jobs remain bounded and recover correctly from failures |
| 4b. Train when justified | Generate/review examples; train only when errors and volume justify it; measure held-out quality, drift and rollback | Chunk 3 evidence and approved training budget | Whole-system quality/cost improve over the prompted executor |
| 5. Paid shared operation | Managed persistence/collaboration, scoped portfolio summaries, recurring jobs and billing; reuse existing fusion views | Chunk 2 repeat use, Chunk 3 service value, Chunk 4a for scheduled jobs, multi-user security/recovery gates | Independent operators repeatedly choose it for real work at positive serving economics |

Chunk 5 need not wait for training (4b) if a prompted model already meets the job.
Recurring-job controls (4a) remain mandatory for scheduled operation either way.
Cross-venture maps follow correct venture semantics; they do not require a second
product or a fusion rewrite. No new provider/framework/training project is a
prerequisite for Chunk 1.

## First implementation checkpoint

The [detailed coding roadmap](CHUNK_1.md) maps work onto actual files and existing
types. It specifies contracts, migrations, races/retries, tests, acceptance commands,
recovery and a copyable implementation-agent instruction.

1. **Correct outcomes:** intake can hold/stop; promotion avoids overlapping reviews.
2. **Correct context:** a versioned map references existing records; compact task
   briefs include mandatory evidence and expose omissions/unclassified inputs.
3. **Correct changes:** result submission gets a receipt; acceptance applies exactly
   the reviewed effects once; stale results remain available for reconciliation.
4. **Usable handoff:** agents use the CLI and humans read the same state in the
   local interface, including purpose and conditional future work.
5. **Measured checkpoint:** run synthetic replays against concise files, reporting
   correctness, payloads, tool calls and actual usage where available.

Rough estimate: 7–12 focused developer-days for the complete first chunk including
review, not a measured velocity or delivery promise. C0/C1 repairs provide an
earlier 1–2-day checkpoint. Limit graph UI to a small readable map and outline;
hosted auth, a canvas framework and orchestration are outside this chunk.

## Commercial shape

Keep BYO-agent use complete and portable. A local/core offering provides entry;
paid managed state, collaboration and scheduled bounded jobs provide service.
License and publication are separate future choices.

Users can reproduce the reasoning with their agent. The paid value is less
orchestration/upkeep, reliable continuation and optional measured task execution.
A subscription user with zero marginal inference cost may pay for convenience,
but should not be promised a cash token saving.

The [economic sensitivity analysis](../../inquiry/wedge-experiments-2026-10-06/ECONOMICS.md)
shows specialization works only under some assumptions. Set no price from a
synthetic model. Measure accepted-result cost including source access, retries,
review, escalation and training amortization first.

## Evidence gates

Synthetic data is sufficient to implement and test this first chunk; it cannot
establish paid demand or cheap-model quality. Agents own fixture generation,
replay and evidence capture. The user is not assigned an example-writing project.

Use the [future repeated-update protocol](REPLAY_PROTOCOL.md) for the Chunk 1
replay and Chunk 2 comparison. It specifies equal evidence/tasks/model conditions,
competent file summaries/indexes, initial setup and ongoing maintenance on both
sides, corrections, pivots, unlinked arrivals, restarts and stale returns. Its
predeclared quality and efficiency gates decide whether to invest in the executor;
missing usage measurements cannot be replaced by a claim based on byte counts.

If an incumbent or files plus a small adapter work as well with less upkeep,
favor that approach and retain useful internal repairs. If the cheap executor
fails quality/economics, keep BYO execution. If paid demand is absent, an internally
useful tool remains worthwhile; adding business departments is not the remedy.
