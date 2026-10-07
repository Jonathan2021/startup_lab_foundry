# Chunk 1 Venture decision maintenance and agent handoff

Date: 2026-10-06. Original coding roadmap; subsequently implemented under the
user-authorized [MVP scope](MVP.md). See [STATE.md](STATE.md) for refinements
and the release report for acceptance evidence. The roadmap below retains the
original preimplementation criteria.
Prepared from read-only repository inspection under the
[wedge experiment protocol](../../inquiry/wedge-experiments-2026-10-06/PROTOCOL.md).
The [macro plan](README.md) defines scope and later dependencies. No product code,
tests, migrations or live venture records were changed for this document.

## The demonstrable outcome

An operator opens one venture and sees **why the current work matters, what it
could unlock, and what would justify changing course**. Their existing agent can
take a bounded context package, return an attributed result, and propose the
corresponding map/decision changes. A reviewer can accept those precise changes;
retries, concurrent edits and old results cannot silently change today's plan.

The first unit of value is one complete investigation handoff **after new evidence
changes what should happen next**: expose which planned work needs review and
provide the precise new context. A discovery tree by itself is not differentiation;
the existing tool landscape already contains trees, memory and agent interfaces.
It is not an
autonomous founder, an arbitrary workflow builder, or a graph visualization by
itself. A stopped investigation can be a successful outcome.

Ship one local vertical slice and stop at its checkpoint. Do not build paid
execution, fine-tuning, an agent marketplace, a graph database, team permissions,
remote hosting, a plugin system, CRM synchronization or a new frontend framework
as prerequisites. Synthetic scenarios are fixtures, never evidence about a real
venture. User-authored field observations are not required to finish this chunk.

## What already exists and what to reuse

Paths below are relative to `foundry/` unless otherwise stated.

| Existing seam | Reuse and constraint |
|---|---|
| `domain.py`: Workspace, IdeaRevision, Venture | Ownership and current venture scope. Do not create a second independently editable venture brief in the map. Freeze the scope used by a map revision. |
| `domain.py`: Assumption, AssumptionRelation | Hypothesis and its semantic relationships. A map question can reference an Assumption; do not copy its status into a competing master record. |
| `domain.py`: WorkItem, Experiment, ExperimentAssumption | Actual assigned work and bounded test protocol. A possible future branch is not yet a ready WorkItem. `parent_id` is hierarchy, not a general dependency engine. |
| `domain.py`: Evidence, EvidenceSource, ReferenceSource, AssumptionAssessment, AssessmentEvidence | Observations, provenance and interpretations remain distinct. Conflicting evidence remains visible. |
| `domain.py`: Decision, DecisionEvidence, DecisionAssessment | Accepted commitments and their supporting evidence. New decisions supersede old ones; future alternatives are not accepted Decisions. |
| `domain.py`: WorkspaceReview; `reviews.py` | Current disposition/next action and immutable coordination reviews. Keep one authoritative current review, not map-specific duplicate stage/maturity fields. |
| `snapshots.py`: snapshot, read_snapshot, transaction, audit | Immutable typed JSON Artifact payloads, content digests, same-key retry checking and audited transactions. Add schema-specific validation; these helpers alone are not business authorization. |
| `human_inputs.py` | Exact request/target/work dependencies, input answers and review receipts. Never unblock work by workspace proximity. |
| `manual_intake.py` | Initial manual intake, existing claim/release and completion contracts; repair semantics first. Do not create another competing initial-review queue. |
| `steps.py`: StepService and AgentRunner | Optional executor boundary. No model is necessary for context assembly. Its current `_context` uses recent-record slices and can drop all assumptions/evidence above 100KB; do not reuse that silent selection as the new reliable context policy. |
| `workspace_console.py`, Jinja templates, local CSS/JS | Extend the current console with an intelligible venture view; preserve score header, IDs, filters and return navigation. |
| `cli.py`, `revamp_commands.py`, `inputs.py` | Existing argparse CLI and JSON input-file approach. New commands call application services, not their own database logic. |

The schema already contains AgentDefinition/Version/Run and external-action
records. Their presence does not justify activating them for this chunk. Do not
force a manual external-agent result into a fictitious hosted AgentRun or mark
an unexecuted StepRun as successful.

## The smallest additional model

Use **one `DecisionMap` coordination head per workspace**, with a workspace
foreign key/unique constraint, `current_revision_artifact_id`, and the existing
optimistic `version_id` convention. Put complete immutable map revisions in
validated `Artifact` payloads named `decision-map/v1`. This small index provides
an unambiguous current revision and a concurrency boundary; it is not a graph DB.

Map revisions include `schema_version`, workspace ID, sequence, previous revision
ID, author, rationale, captured scope references/digests, node/edge arrays and
current focus node IDs. Each revision has a stable artifact ID and digest.
Preserve removed nodes in the older revision; never rewrite history to make a
failed branch disappear. Use `ArtifactRelation(SUPERSEDES)` where consistent with
existing artifact history. A first empty map is optional; opening a workspace
must not silently invent its strategy.

Keep graph-owned content limited to goals/milestones, questions that are not yet
formal hypotheses, outcome alternatives and explanatory relationships. A node
referring to actual work, an experiment, evidence or a decision uses a typed exact
reference to that authoritative record. A proposed future action can remain a
small bounded draft inside an alternative; create the WorkItem only on acceptance.

An exact reference contains a supported record type and ID, owner workspace,
and immutable revision ID or captured version/content digest. Mutable records
must also have their relevant content frozen inside the snapshot: an optimistic
version counter alone does not let a reader reconstruct the old content.
ReferenceSource is portfolio-scoped; its use still needs venture-owned evidence.
Do not treat a shared URL as independent corroboration.

Use a discriminated Pydantic union, `extra="forbid"`, bounded strings/arrays and
typed reference resolvers. Suggested initial limits: 80 nodes, 160 edges and the
existing 100KB input ceiling. These are operational caps, not product claims;
test the boundary and provide actionable errors instead of truncating a map.
Do not add generic node/edge SQL tables until actual map sizes or query needs
justify them. Do not turn Artifact metadata into unvalidated arbitrary JSON.

Keep context packages (`venture-context/v1`), submitted results
(`venture-result/v1`) and one terminal resolution receipt per result
(`venture-result-resolution/v1`) as immutable typed Artifacts too. Their indexed
workspace/name/ID plus deterministic receipt identity suffice for the first local
slice. There is no need for three more lifecycle tables. If implementation finds
a concrete query/constraint that cannot be enforced, document that specific gap
before adding another entity.

## Decision alternatives are not execution dependencies

Use a small vocabulary with explicit semantics:

- **contributes_to:** this work/question serves this higher goal or milestone;
- **tests:** actual experiment/work examines a question/assumption;
- **may_lead_to:** a described outcome can justify a draft next step or disposition;
- **revisits:** feedback returns to an earlier question with new evidence;
- **depends_on:** a proposed or current step needs a stated prerequisite.

Each `may_lead_to` link has a written condition, outcome category, evidence
requirements and uncertainty/limits. Categories include supported, weakened or
refuted, inconclusive, blocked and conflicting evidence. Do not invent numeric
probabilities, use a score as proof of a condition, or imply that outcome paths
are exhaustive. “Unexpected finding / revise the map” must remain available.

The user should be able to see two steps ahead without scheduling them. Selecting
a branch records a reviewed decision; merely drawing an arrow must not start a
worker, create paid work or authorize an external action.

Cycles through `revisits` and explanatory relationships are legitimate learning.
If `depends_on` connects active work, reject dependency cycles/self-dependencies;
do not reject the entire decision map because it contains a feedback loop.
Do not build a general execution DAG engine in this chunk. Actual readiness uses
existing explicit work/input rules, bounded prerequisite validation and the
shared execution-eligibility check below when creating, claiming and starting work.

## Service operations and contracts

Implement the rules in a new `decision_maps.py` service and a new
`agent_handoffs.py` service, with shared typed contracts in
`decision_contracts.py`. Names are proposed; avoid unnecessary service layers.

### Map create/read/revise

`revise_map(workspace, expected_head, request_key, actor, rationale, map)` validates
all node IDs, references, ownership, edge endpoints, focus nodes and dependency
rules. A matching retry returns the original result. Same key/different payload
conflicts. A concurrent revision cannot overwrite the newer head. The head and
revision artifact are committed together. Read can return current or exact old
revision; an old revision must render its old labels/scope, clearly marked historical.

The trusted local operator may revise the map directly. No human approval click
is required for every annotation. An external agent's result carries a proposed
revision and effect preview; acceptance applies that exact preview under the
operator's established authority.

A changed goal, condition, assumption or accepted conclusion produces an impact
preview for **explicitly dependent** current work/context packages. The service
does not infer that all work in the workspace is affected. For each affected
active item, the change names keep-with-rationale, revise, cancel, or needs-review;
needs-review prevents treating the old plan as ready for authoritative execution.
Use a retained impact artifact and a derived UI/context flag, enforced by one
shared server-side execution-eligibility check. Existing
`BLOCKED`/`blocked_reason="changed_context"` is also persisted for the exact work
items whose accepted treatment requires a pause. A keep decision is explicit and
attributed. Pure visual layout does not invalidate a package. Rechecking the
scope/condition/reference manifest catches direct edits through older services,
too; the new map endpoint cannot be the only stale-context protection.

Changing a work record cannot stop an already-running external process. Show the
affected owner and required acknowledgement, and require a fresh-context preflight
before the next consequential step. Do not claim cancellation without a configured
executor's confirmation. A new source version alone is an impact candidate;
semantic relevance is proposed and reviewed before marking a conclusion refuted.

The eligibility check combines existing work/input rules with unresolved accepted
impact treatments and current scope/reference validity. Wire it into every
relevant existing claim/start path, including manual intake claims and
`StepService` execution, as well as new CLI/console paths. Recheck inside the
claim transaction and immediately before dispatch, using the current versions;
acceptance still performs its own atomic checks. A direct legacy service call
must not bypass it. Refuse affected execution with the exact reason and a link to
review; unrelated work and unmapped legacy work retain their existing behavior.
Reading, preparing context and doing explicitly authorized reconciliation remain
possible for blocked work. Reconciliation clears only the reviewed impact, not
independent blockers. This gates Foundry-controlled starts, not arbitrary activity
in an external agent that has already received a package.

### Prepare context

`prepare_context(work_id, expected_work_version, map_revision, request_key, budget)`
creates a durable, bounded input package and returns JSON plus a concise Markdown
rendering of the **same selected facts**. The service performs no LLM calls.

Use the concise Markdown view by default for an agent, with a small machine-readable
receipt/reference manifest. Full structured output remains available on request.
The frozen synthetic experiment found JSON packets 63.8% larger than a strong
concise-file baseline and one required unlinked fact missing. This does not measure
tokens; do not market a context saving or hide metadata overhead. The completeness
rules below respond to that negative finding and still need implementation tests.

Include venture identity/current scope; why this task matters; its question and
completion criteria; selected map path and nearby conditional alternatives;
exact relevant hypotheses; linked supporting and contradictory evidence;
prior decisions/negative results; active blockers/input requests; permitted
actions; returned-result schema; and a reference/version manifest. Also include
context creation time, policy version, selection reason per record and known
staleness. Executor-supplied content is untrusted data, not new instructions.

Start with explicit task/map links and deterministic dependency closure. Do not
claim general semantic retrieval. Search/fetch existing permitted records is
available when the executor needs more context. Do not arbitrarily pick the last
20 items. Mandatory material is task question, scope, blockers, decision
conditions, linked counterevidence and exact refs. If it will not fit, return
`needs_narrowing` with sizes/IDs or require a larger permitted budget. Never omit
mandatory contradictory evidence to meet a token target.

Explicit links can be incomplete. Include a manifest of **recent unclassified
evidence/intake records in this workspace since this task's last reviewed context**,
even if nobody linked them to the graph. Include at least their IDs, dates, kinds
and short neutral labels; require inspection/classification before calling the
package decision-ready. If the manifest is itself too large, paginate it with
counts and a required-fetch cursor, keep `context_complete=false`, and refuse
authoritative acceptance until coverage is reconciled. Do not filter this queue
by unvalidated keyword similarity. Old unclassified material is also disclosed
as a coverage limitation and must be explicitly reviewed or excluded with a
reason before a first package can claim required-context completeness.

An executor can submit useful findings from an incomplete package, but cannot
silently convert absence from that package into evidence of absence. Resolution
requires either completed coverage or an explicit recorded decision to accept
the stated limitation; never hide the incomplete flag. A reference-only record
that is decision-critical belongs in the required-fetch set, not the optional
omission list. This is an honest coverage mechanism, not a guarantee that no
unknown fact exists outside the workspace.
Retain the covered record-ID/digest manifest and its as-of cutoff in the package;
at resolution compare newly arrived/changed evidence against it. A map-head check
alone misses newly recorded unlinked counterevidence. Accepting a bounded decision
with a stated limitation never relabels its input package as complete.

For optional material, return counts, IDs/locators, explicit omission reasons and
an exact-record fetch operation. The executor knows whether it received a complete
required set and can retrieve a specific item without reloading the entire
venture. Report bytes/words; label tokens estimated unless an identified tokenizer
actually calculated them. Log selected size and preparation time locally without
sensitive payload dumps. Old packages remain readable after map edits.

Context preparation is a mutation because it persists a snapshot. HTTP must use
POST with existing local mutation checks; ordinary GET reads a saved package.

### Submit result

`submit_result(context_id, request_key, executor, findings, source_refs, limits,
recommendation, proposed_effects)` validates the saved context identity/digest,
record ownership, schema and size. It returns a durable receipt, detected stale
references and a human-readable proposed-effects view. A result can report no
change, stop, hold, narrow or continue. It need not contain scores.

Record executor identity as declared audit provenance, not authenticated identity.
Optional model/provider/version and usage information can be null; never invent
token cost. Retain unsupported claims as flagged submissions rather than silently
turning them into accepted Evidence. Each substantive finding references a source
or explicitly says it is inference/unknown; source existence does not prove truth.

Submitting a result saves it and its proposed effects; it does **not** accept a
branch, complete unrelated work, revise scope, update scores or send anything.
Show “Result ready for review” using the pending result projection, distinct from
“worker running.” An active local claim may remain in progress until resolution;
do not invent execution merely because a package was exported. If implementing a
generic claim/release wrapper, share existing optimistic WorkItem claim logic;
do not refactor the human-input lifecycle unnecessarily. Manual release/recovery
with reason suffices; distributed leases are deferred with hosted workers.

Store a structurally valid late result even when its context is stale. Label
`needs_reconciliation`, enumerate changed references, and apply **zero** effects.
This retains useful research without pretending it answered today's question.

### Resolve result

`resolve_result(result_id, expected_map_head, expected_work_version,
expected_review_revision, resolution, actor, rationale)` handles accept, reject,
or defer. Review checks the exact rendered result and payload digest. A terminal
resolution is idempotent; a different second resolution conflicts. Defer is a
nonterminal audit annotation, not a permanent rejection.

On acceptance, one transaction creates explicitly proposed Evidence/source
links, AssumptionAssessment where applicable, a Decision, a new map revision if
changed, an appended WorkspaceReview and only the explicitly listed next work.
It completes only the matching current WorkItem. Each changed work item has an
explicit expected version. No generic patch language or arbitrary table names
are accepted in result payloads. Fixed allowed effect types only.

Current-state assertions are rechecked at accept time even if submit was current.
For stale work, prepare fresh context and submit a superseding proposal citing
the old result and reconciliation rationale. Preserve its findings; do not offer
an unchecked force-apply flag. The reviewer can explicitly judge retained evidence
relevant to the new scope, but that judgment itself is a recorded new proposal.

If two results race, the first accepted matching version wins; the other remains
retained and stale, without duplicate Evidence/Decisions/WorkItems. A failure after
creating evidence but before updating the head rolls back the whole transaction.
Network retry returns the original successful receipt before checking a now-old
version, provided the exact request payload matches.

Use existing local trust boundaries: CLI process access and loopback console
Host/Origin/mutation-token checks. Actor strings and workspace IDs do not create
security principals. This chunk is **single-user local tooling**, not secure remote
MCP/HTTP access. Cross-workspace refs are rejected except permitted public-source
identities and specifically supported existing portfolio links; arbitrary access
to another venture's private artifacts remains out of scope.

## Repair the two intake semantics before layering this flow on top

In `manual_intake.py`, extend `IntakeCompletion` with explicit outcome
`continue|narrow|hold|stop` and optional bounded next-work input. Map continue and
narrow to existing `Disposition.PURSUE`, hold to `HOLD`, stop to `DROPPED`;
retain distinct DecisionKind/rationale for narrowing. Do not invent a new
disposition enum solely to express narrowing.

- Stop completes this intake with no scheduled continuation by default. It does
  not cancel other work unless an exact, reviewed work treatment names it.
- Hold requires a reason and a revisit trigger; no ready investigation is required.
  An optional exact input dependency is allowed when that is the real blocker.
- Continue/narrow require a bounded next action and owner; narrowing identifies
  the changed scope explicitly. A successful research submission never silently
  overwrites current investigation stage or product maturity.
- Nonempty explanatory `next_action` can remain required by WorkspaceReview even
  when `next_work_item_id` is null: “Hold until eligible-site access is available.”
- Accept historical completion receipts under their original schema. Version
  new completion inputs explicitly; do not reinterpret old pursue records as stop.
  Update JSON examples/form choices atomically with the contract change.

For promotion in `portfolio.py`, default behavior with the same source idea
revision and unstarted overlapping initial intake: create venture intake and
explicitly cancel/supersede the old pending idea intake in the same transaction,
with an artifact/audit link both directions. Retain the old task and show the
redirect on the idea. Do not physically move its workspace or erase its handoff.
If the old intake is already claimed/in progress, promotion preserves it and links
to it; do not quietly start another overlapping investigation. A distinct scope
can create explicit separate work with a rationale. Completion in the originating
workspace is not automatically copied as new independent venture evidence.
If initial review was already completed on the exact source scope, promotion
links to that retained result and queues only an identified remaining venture
question, if any; it must not blindly re-run the same initial research. A new
venture's frozen source score baseline is still a baseline, not a new assessment.

Test promotion with no intake, ready intake, claimed intake, finished intake,
different idea revision, distinct investigation scope and identical retries.
The exact resolution policy must be visible in the promotion response and UI.

## File-level implementation order

| Task | Depends on | Concrete work | Exit criterion |
|---|---|---|---|
| C0: baseline and red contracts | none | Record root/Foundry HEAD and dirty-file hashes; read AGENTS and current direction. Add tests below and a disposable synthetic fixture manifest before implementation. | Green existing checks distinguished from red new contracts; no live DB changes. |
| C1: outcome and promotion repairs | C0 | `manual_intake.py`, `portfolio.py`, relevant `revamp_commands.py`/`workspace_console.py` form contracts, `templates/manual_intake.html`, existing intake tests. | Stop/hold have no forced ready work; promotion yields one overlapping active intake and preserved history. |
| C2: typed map and persistence | C0 | New `decision_contracts.py`, `decision_maps.py`; additive DecisionMap in `domain.py`; one Alembic migration after actual current head (currently `b10261006002`); schema docs. | Current/historical reads, exact reference validation, immutable revisions and concurrent edit tests pass on SQLite/PostgreSQL. |
| C3: context package | C2 | New `agent_handoffs.py`; reuse reference resolution and snapshots; narrowly adapt `steps.py` only if it can call the same assembler without changing legacy behavior. | Explicit required closure and fetch manifest; no hidden LLM; oversize mandatory set fails clearly. |
| C4: result and reviewed transition | C1,C3 | `agent_handoffs.py`; focused shared helpers in `reviews.py`/`snapshots.py` only when needed; existing domain effect records; shared eligibility check wired into existing claim and `StepService` start paths. | Current, stale, conflicting, retry and rollback cases pass; exact preview equals accepted effects; legacy and new starts reject unresolved dependent impacts. |
| C5: BYO-agent commands | C2–C4 | New `decision_commands.py`; register via current argparse dispatch; JSON input files through `inputs.py`; document examples in `DEVELOPMENT.md`. | A fresh agent session can show map, prepare/fetch context, submit result and inspect receipt without direct SQL or lengthy private instructions. |
| C6: readable local UI | C2–C4 | New `decision_console.py` registered by `web.py` or current console seam; `templates/decision_map.html`, `templates/decision_result.html`; minimal CSS/JS; existing venture/header/navigation templates. | Venture Now shows why/next/branches; result comparison uses labeled fields; old revisions and stopped/held paths understandable. |
| C7: recovery, acceptance and checkpoint | C1–C6 | Tests, actual browser run if available, migration rehearsal on snapshot copy, docs/ADR update, measured synthetic handoff replay. | Full evidence report with pass/fail/blocked gates and no claim of savings from unmeasured token use. |

Review and accept proposed ADR-0014 before implementation; it records map-as-view,
one-head/immutable-artifact storage, executor-neutral results and local trust
limits. Update `ARCHITECTURE.md`, `DEVELOPMENT.md` and `docs/foundry-domain.dbml`.
Do not silently replace reference definitions. No curriculum work or learner
credit follows from this chunk.

CLI vocabulary can be `decision-map show|revise`, `handoff prepare|show|fetch`,
and `result submit|show|resolve`; choose stable user intent names once and document
them. JSON schemas/examples must be obtainable from the CLI. The same application
services serve the console. A thin local stdio MCP wrapper is a follow-on adapter
if it demonstrably makes the target agent workflow easier; remote OAuth/hosting
is not part of this checkpoint. Do not expose arbitrary SQL, file reads or shell
execution as agent tools.

## UI scope: useful map before a canvas product

Show a compact map beside an accessible structured outline. Current work has a
clear highlight; upstream goal and downstream conditional alternatives are visible.
Clicking a node reveals its owner, exact records, rationale, evidence and history.
Use expandable HTML/SVG with escaped labels and locally served assets. A huge
drag-and-drop editor or graph library is unnecessary for 5–15-node first cases.

Support adding/revising a goal, question and conditional next step through labeled
forms; agent-created maps can use the same contract. Users should not edit raw
JSON to narrow or stop a venture. Layout-only choices must not masquerade as a
strategy change. Preserve score/coverage at the top, copyable ID and return filters.
An empty map says “No decision map yet” and allows creation from current records;
it does not fabricate connections because two text labels look similar.

A result screen shows findings, counterevidence/limits, proposed branch, exact
state/work changes and stale checks. Accept/reject/defer are visible. When an
authorized agent performs acceptance, the UI still displays who did it and why.
An inconclusive result keeps alternative paths visible and can lead to a narrower
test. Future possible work is visually different from assigned ready work.

## Tests to write first

Add tests by behavior, not snapshots mirroring implementation. Proposed files:

- `tests/unit/test_decision_maps.py`: missing/dangling/cross-workspace refs;
  exact historical content; same-key retries/conflicts; concurrent heads; allowed
  feedback vs forbidden active prerequisite cycle; excessive map bounds.
- `tests/unit/test_agent_context.py`: mandatory counterevidence and blockers;
  selection invariant to unrelated record insertion; deterministic stable order;
  budget overflow; omitted/fetch manifest; scope changed after snapshot; empty map.
  Also insert unlinked counterevidence after context preparation: a new package
  must expose it as unclassified, and acceptance of the older proposal must flag
  the new evidence/coverage change rather than declare the old package complete.
- `tests/unit/test_decision_results.py`: supported/refuted/inconclusive/conflicting
  findings; stop/hold; no score requirement; arbitrary effects rejected; stale
  submit retained; stale acceptance no effects; duplicate and concurrent accepted
  result; accepted plan and visible preview match; mid-transaction fault rollback;
  source text containing instructions stays data; unsupported source schemes.
  Verify that a changed condition invalidates only explicitly dependent work,
  preserves unrelated work, shows each treatment, and cannot reactivate a branch
  merely because an out-of-date result recommends it.
- Extend existing claim/step service tests: unresolved dependent impacts block
  both old and new start paths; a change between claim and dispatch is caught;
  unrelated and unmapped work retain prior eligibility; reconciliation clears
  only the intended blocker. A display flag alone cannot satisfy these tests.
- Extend `tests/unit/test_manual_intake.py` for the repair matrix above.
- `tests/integration/test_decision_map_migration.py`: migrate from current head
  with populated old records, retained values/foreign keys, no metadata drift,
  repeated migration and PostgreSQL checks through the existing optional fixture.
- `tests/acceptance/test_decision_handoff_cli.py`: fresh temporary store; create
  synthetic venture/map; export package; submit; accept; restart; reconstruct the
  full chain from exact refs; repeat command with identical payload.
- `tests/unit/test_decision_console.py`: mutation protections, malformed query/
  references, historical labels, escaped content, stop without queued work,
  pending result vs running distinction, return filter preservation, accessible
  labeled forms and server-rendered no-JS outline.

Use at least these scenario fixtures: a local information service with absent,
present or unknown incumbent coverage; an operating software venture whose safety
issue temporarily displaces growth work; a supplier trial with inconclusive
quality; an obsolete research result after customer-segment pivot. Keep existing
sports fusion in its current PortfolioProposal service; a map may link to that
decision, but Chunk 1 does not reimplement portfolio proposal effects.

Suggested commands from `/home/jonathan/startup_lab`, after implementing tests:

```bash
.venv/bin/pytest -q foundry/tests/unit/test_manual_intake.py foundry/tests/unit/test_decision_maps.py foundry/tests/unit/test_agent_context.py foundry/tests/unit/test_decision_results.py foundry/tests/unit/test_decision_console.py foundry/tests/integration/test_decision_map_migration.py foundry/tests/acceptance/test_decision_handoff_cli.py
.venv/bin/ruff check foundry/src foundry/tests
.venv/bin/mypy foundry/src
make check
```

Do not run undocumented commands against the default permanent database. Tests
must use temporary stores (`foundry --store <temporary-path> ...`) or the existing
isolated PostgreSQL test configuration. First rehearse migrations on a verified
backup copy; do not use an already-mutated rehearsal file as a restoration point.
If the browser or container registry is unavailable, state that exact acceptance
gate is blocked. HTML TestClient checks do not establish browser usability.

## The checkpoint and the next decision

Definition of done is a repeatable local demo where a fresh agent receives one
bounded package, finds its exact missing record if needed, returns a result, and
an authorized reviewer changes or stops the plan with an auditable receipt. Repeat
with a changed venture objective and show the late result retained but unapplied.
Do this entirely on synthetic data; provide the user a short walkthrough and
recorded outputs, not an assignment to create fixtures manually.

Then run the [repeated-update protocol](REPLAY_PROTOCOL.md), which includes initial
setup, unlinked arrivals, corrections, pivots and restarting with retained state.
Count all graph/classification upkeep against file/index upkeep. Retain failures
and any case where concise files match or beat Foundry. Payload reduction alone
is not total token-cost or quality improvement; the protocol's primary metric and
quality gates must be fixed before execution, not chosen from the best result.

All scope/idempotency/staleness/rollback tests are release gates. Cost and utility
measurements decide the next investment: if package size plus repeated fetches
and upkeep does not improve the strong file baseline, narrow or change context
selection before adding an executor. If map maintenance dominates, automate draft
map proposals using the user's existing agent before building a diagram editor.

Only after this checkpoint choose between (a) a thin agent integration adapter,
(b) one task-specific cheaper executor, or (c) improving the core handoff further.
Training follows a frozen task/result contract and enough reviewed examples; its
evaluation/experimentation remains outside the Foundry product domain. Synthetic
tests establish mechanics, not willingness to pay or small-model research quality.

Rough planning estimate, not a quote or observed velocity: C0–C1 1–2 focused
developer-days; C2–C4 3–5; C5–C6 2–3; C7 1–2. Total approximately 7–12 days for
one experienced implementer with review. Use the ordered acceptance checkpoints
for a cheaper coding agent, not an unreviewed bulk generation request. If the
first chunk expands beyond that because of graph UX, hosted auth or orchestration,
remove those expansions rather than silently changing this scope.

## Copyable instruction for the implementation agent

> Read root/foundry AGENTS, current direction, the accepted parent proposal and
> this chunk plan. Record dirty-worktree baseline; do not commit, push or mutate
> the live database. Implement C0–C7 in order, writing meaningful failing behavior
> tests before each feature. Reuse the existing evidence/decision/work model,
> snapshots and transactions. Add only the workspace map head and typed immutable
> map/context/result receipts described here. Preserve old records and command
> compatibility explicitly. Stop and report if a requirement would need a new
> provider, paid service, remote permissions or general graph/workflow framework.
> Deliver the synthetic end-to-end demo, precise validation report and migration
> rehearsal evidence. Do not start a second chunk, install a model or pretend a
> queued task has executed. Mark browser tests pending if no browser is available.

Inspection baseline only: root HEAD `e6a83e470d052439e5c8d4a943428f5bbd132f7f`,
Foundry HEAD `3b082507062838df4009d4b636c4f320436f3b41`; both working trees are
substantially dirty. An implementation agent must capture fresh effective hashes;
these commits alone do not identify the inspected runtime code.
