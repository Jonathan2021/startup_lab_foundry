# Agentic-stack discovery — report (2026-10-09)

Status: complete for review (2026-10-09). Protocol: [PROTOCOL.md](PROTOCOL.md). Source: the user's
transcript `idea_queue/agentic_stack_ideas.md` (sha256 `df96c651…31adb5`).
Research passes: [R1 orchestration](research/R1-orchestration.md),
[R2 routing](research/R2-routing.md) (+ [direct checks](research/R2-addendum-direct-checks.md)),
[R3 specialists](research/R3-specialists.md), [R4 AI OS](research/R4-ai-os.md),
[R5 research systems](research/R5-research-os.md). Every market statement below is a
dated web read; nothing was installed, run, bought or sent.

## 1. One-paragraph answer

The transcript's five big ideas collapse to one buildable wedge and one later
product thesis. **Wedge:** an open-source, local *agent fleet controller* that runs
the unmodified official CLIs (Claude Code, Codex CLI, local models) under the user's
own logins, keeps an *outcome ledger* of every task (category, model, effort, verifiable
result, quota state), handles subscription-quota exhaustion with circuit breakers and
durable checkpoint handover between providers, and learns an escalate-fast /
downgrade-slow model+effort policy per task category in shadow mode before enforcing
it. This merges AS01, AS08 and AS03 and absorbs AS05's only open residual. **Later
thesis (on hold):** the specialist-agent factory (AS02 + AS09) that would consume that
ledger to decide *when* a local specialist or prompt optimisation is worth it. R3 found
the fine-tuning market shrinking and the lower rungs covered, so it stays a hold with a
concrete revisit trigger rather than a second venture.
Everything else is covered by incumbents (AS07), occupied and a poor founder fit
(AS06), or is really Foundry's own inquiry-memory question (AS04).

## 2. Candidate dispositions

| ID | Candidate | Disposition | Why (evidence) |
| --- | --- | --- | --- |
| AS01 | Adaptive model/effort controller | **Merge → wedge** | Routing is a commodity (LiteLLM, Mastra, gateways; Stripe–OpenRouter, PANW–Portkey). Not Diamond Code (hosted, gated, Claude Code harness) and LiteLLM Auto Router v2 claim per-step model/effort; neither documents machine-verifiable task outcomes keyed by task category as reward, nor quota-as-constraint across vendor CLIs ([R2](research/R2-routing.md), [checks](research/R2-addendum-direct-checks.md)). Paperclip exposes effort per agent but no documented per-run model hook; Model Capacity plugin is deterministic prior art with 0 stars ([R1](research/R1-orchestration.md)). |
| AS02 | Specialist-agent factory | **Hold; its cheapest test folds into the wedge** | The fine-tune-from-traces market is shrinking: TensorZero archived 2026-06-12, OpenPipe closed to new training 2026-07-30 (CoreWeave), Predibase → Rubrik, Humanloop shut, Lamini → AMD, Fireworks dropped managed RL fine-tuning, OpenAI ends self-serve fine-tuning 2027-01-06 and Evals 2026-11-30 citing "fewer use cases that require fine-tuning". Upper rungs crowded (Distil Labs, Pioneer, Inference.net Catalyst, Overmind); lower rungs covered by Microsoft SkillOpt-Sleep (MIT, 18.2k stars: nightly recurring-task mining from Claude Code/Codex transcripts, held-out tests, human-approved skill changes). "Decide *when* fine-tuning is worth it" is unshipped by ~45 actors, plausibly because the answer is usually no. Provider terms restrict outputs as training targets; routers trained on outcome metadata fit the classifier exceptions ([R3](research/R3-specialists.md)). Revisit if the wedge's ledger shows a task class with ≥30 verifiable runs/month. |
| AS03 | Provider-portable competence | **Fold into wedge as a feature** | Prompt rewriting per model (Not Diamond) and mid-session switch checks (vLLM SR) exist; whole-harness calibration on a provider switch does not; not a standalone product ([R2]). |
| AS04 | Self-improving research OS | **Narrow → research ledger experiment (Foundry/ARC3), not a venture** | Inner loop is a commodity (autoresearch 97.6k stars, AIDE/Weco, AlphaEvolve GA, MLE-bench saturated); outer loop crowded at prototype level (autocontext, ShinkaEvolve, GEPA). Residual: typed cross-project ledger with negative results, noise-aware status and trial-aware promotion. Cheapest test: 329 existing ARC3 inquiry records, retrieval A/B, stop rule <10 recall points ([R5](research/R5-research-os.md)). |
| AS05 | Adaptive AI OS, technical teams | **Drop as OS; residual folded into wedge** | Team layer taken by Paperclip (99.1k stars, Team Catalog, export/import, approvals, cloud waitlist), Gas Town, Orchestrator.inc, Ruflo, Symphony; frameworks by LangGraph/Mastra/Agno/CrewAI. Vibe Kanban shut down for lack of a business model. Only residual: one eligibility policy across cloud/local/subscription runtimes, plugin-sized ([R1], [R4](research/R4-ai-os.md)). |
| AS06 | Adaptive AI OS, SMEs | **Drop** | EU-hosted SME workspaces at €21–25/seat (Langdock, Dust, Mistral Vibe Team, Copilot, Gemini); enterprise hubs manage external agents (Agent 365, Frontier, Dataiku Agent Management). Sales/trust/compliance heavy; worker-evaluation use is EU AI Act high-risk. Poor solo-technical-founder fit ([R4]). |
| AS07 | Cross-provider routines dashboard | **Use existing** | Paperclip, Tutti, Agency, Hermes, OpenClaw, Agno schedule across providers; Claude Code routines and Codex scheduled tasks are first-party and expose no list/read API, so a unified first-party dashboard is blocked, not merely unbuilt ([R1]). |
| AS08 | Quota-aware failover + checkpoints | **Merge → wedge (its demand signal leads)** | Strongest demand: four open Paperclip requests since 2026-03 (#2014/#2743/#3317/#11597: 160/400 runs wasted), forks, Flock's hand-built Claude→Codex handoff (merged 2026-10-06), OmniRoute 74.5k / CLIProxyAPI 54.6k stars. Those popular tools proxy or pool login tokens, which Anthropic's rules forbid; the terms-respecting local-supervisor form is open. Risk: Paperclip PR #9367 could close part of it upstream ([R1], [R2]). |
| AS09 | Evaluated workflow packs / eval library | **Drop as an asset; verified outcomes live in the ledger** | Prime Intellect's public Environments Hub, Hermes Agent community skills (252k stars), skills that transfer across harnesses, Braintrust/Langfuse datasets. Defensible only with private, verified, domain-specific outcomes, which do not exist yet ([R3]). |

Transcript claims checked: Paperclip ~99k stars/MIT/alpha SDK **confirmed**; fallback
issues #2743/#3317/#11597 **confirmed and still open**; Anthropic 2026-10-07 update
**mostly confirmed with conditions** (third-party apps may use subscription limits;
Max/Team get monthly API credits that exclude Claude Code; third parties may not route
through or hold users' Pro/Max credentials; limits assume "ordinary, individual usage";
policy changed five times in 2026); OpenAI Codex on Plus/Pro **confirmed** (Sign in with
ChatGPT since 2026-09-29; API keys still "recommended default for automation";
unattended unregistered orchestrators unverified); TensorZero archived 2026-06-12
**confirmed**; Mastra ModelSelectionProcessor 2026-09-24 **confirmed, no learning**;
autoresearch March 2026 / AI Scientist v2 / AIDE–Weco / EvoAgentX **confirmed**.

## 3. Scores (reviewed scorecard `portfolio-reviewed-v1`, agent judgments)

Each idea was scored once by this session (author `agent:fable-agentic-stack-20261009`)
with a per-criterion rationale and the idea's market-research evidence attached to the
*competition* and *moat* criteria. The formula is the workbook's: weighted positives minus
weighted penalties, 0–100; A ≥70, B ≥58, C ≥45, D below. Ranking snapshot
`b90d2635-c817-4302-aa14-e7c84a89a0d8` (13 complete reviewed ideas): AS10 ranks second
overall behind the existing sports-Elo idea (51) and ahead of Coopain (48). These are
judgments about an opportunity, not measurements, and no idea reaches B.

| ID | Total | Grade | Positives rev/prof/mvp/fit/gtm/moat/problem/retention | Penalties legal/capital/network/competition | Confidence | Disposition |
| --- | --- | --- | --- | --- | --- | --- |
| AS10 | 50 | C | 4/4/7/9/6/3/8/6 | 5/1/3/7 | medium | Pursue as a bounded open-source MVP on the operator's own workloads (packages C01–C05 with stop rules) |
| AS08 | 45 | C | 3/4/7/8/6/2/8/6 | 5/1/3/7 | medium | Merge into the fleet-controller wedge; its demand signal leads the MVP (C02/C03) |
| AS01 | 42 | D | 3/4/6/9/5/3/6/6 | 5/2/4/8 | medium | Merge into the fleet-controller wedge (with AS08, AS03); keep as feature lineage, not a standalone product |
| AS03 | 39 | D | 3/4/5/8/3/3/4/5 | 3/2/3/5 | medium | Fold into the wedge as the provider-switch calibration feature (C05) |
| AS04 | 39 | D | 3/3/4/10/3/4/5/6 | 2/5/2/8 | medium | Narrow to a research-ledger experiment inside Foundry's inquiry-memory pilot (internal_only); do not pursue as a venture |
| AS02 | 38 | D | 5/4/3/9/3/5/5/6 | 7/5/4/8 | medium | Hold as a venture; fold its cheapest test (recurring verifiable-task count from the ledger) into the fleet-controller wedge as a later 'specialization opportunity' report |
| AS09 | 33 | D | 3/4/4/7/2/4/4/5 | 3/3/5/7 | medium | Drop as a standalone asset; keep verified evaluations as a property of the wedge's ledger (every run carries a verify result) |
| AS05 | 31 | D | 6/3/2/6/3/3/5/7 | 5/7/5/10 | medium | Drop as an OS; fold the cross-runtime eligibility-policy residual into the wedge |
| AS06 | 29 | D | 8/4/1/3/2/3/7/8 | 8/8/5/10 | medium | Drop: crowded EU SME segment, sales/compliance-heavy, poor solo-technical-founder fit |
| AS07 | 24 | D | 1/2/7/6/3/1/3/3 | 3/1/6/9 | high | Use existing tools; do not build |

Compare them in the console: `/ideas/compare?ids=AS10&ids=AS08&ids=AS01&ids=AS04&ids=AS02&ids=AS03&ids=AS09&ids=AS05&ids=AS06&ids=AS07`
(every criterion's rationale is in the page). The spread is narrow because the whole
cohort shares the same weaknesses: weak direct revenue, thin moats and heavy competition.
What separates AS10 is problem intensity backed by quantified demand, MVP speed on the
operator's own fleet, near-zero capital and founder fit; what caps it is monetisation.

## 4. The wedge: agent fleet controller (merged AS01 + AS08 + AS03) — venture `v-fleet-controller`

**Job.** For a person or small team running several official CLI agents on consumer
subscriptions plus a local model: never lose a task to a usage limit, never spend
Opus on work a cheaper configuration demonstrably handles, and keep the evidence.

**Who.** First user is the operator (this repository, `kaggle/arc3`), then Paperclip,
Tutti and Gas Town users who already run multi-CLI fleets.

**Non-negotiables (from the policy evidence).** Spawn only unmodified official CLIs
under the user's own sign-in; never intermediate, pool or rotate credentials; respect
hard budget caps (a budget denial is a stop, not a fallback); default to shadow mode;
local SQLite; no hosted service.

**MVP packages (dependent, each with a stop rule):**

| # | Package | Proves | Stop/continue rule |
| --- | --- | --- | --- |
| C01 | Outcome ledger: record each task run (category, provider, model, effort, duration, verify-command result, review/retry count, quota-limit event, reset time) from `claude -p` / `codex exec` wrappers and Paperclip `agent.run.completed` events | Can we capture verifiable outcomes without changing how work is done? | ≥50 real tasks recorded on two repos in two weeks, else the pain is too rare to serve |
| C02 | Quota manager: parse usage-limit/reset signals, per-provider circuit breakers, eligible-task rerouting or queueing, budget caps honoured, shadow log of what would have happened | Does quota exhaustion actually cost tasks on the operator's workloads? | ≥3 limit events/week observed; else hold |
| C03 | Durable checkpoint + handover: task worktree + handoff note (requirements, investigation, decisions, status, next steps); `resume --with <cli>` continues an interrupted task in another CLI or local model | Can another provider resume with bounded rework? | Rework fraction measured on ≥10 handovers; ≤30% else narrow to checkpoint-only |
| C04 | Learned policy: per task category, escalate-fast/downgrade-slow with logged evidence and regret; recommendations first, `--enforce` after ≥N observations | Does a learned policy beat static assignment? | Quality-adjusted throughput (verified tasks per quota unit) better on ≥50 tasks; else keep C01–C03 as a utility |
| C05 | Provider-switch calibration report (AS03): rerun a sample of ledger tasks with a new provider; report with uncertainty | Is accumulated competence portable? | Optional; only after C04 |

Integration order: standalone CLI first (orchestrator-agnostic), Paperclip plugin
second (observe/recommend; enforcement only if an upstream hook appears). Gates
before any publication: recheck Anthropic/OpenAI terms on the day; measure, don't
claim, savings; no credential handling code.

## 5. Later thesis on hold: specialist factory (AS02, with AS09 folded in)

R3's verdict is that selling weight training is a contested, shrinking business, that the
prompt/skill rungs already ship as open source on the operator's own tools (SkillOpt-Sleep,
DSPy/GEPA, Hermes), and that the one unshipped capability ("decide when fine-tuning is
worth it", with provenance tracking and specialist retirement) is a feature DSPy, SkillOpt
or Catalyst could add, not obviously a company. Local training also stays deferred under
ADR-0010. The hold has a pre-registered revisit test that costs one day and uses only
metadata the wedge's ledger already collects:

- **E0 (desk, metadata only):** over 60 days of ledger entries for this repository and
  `kaggle/arc3`, count clusters of homogeneous tasks with monthly volume, a programmatic
  verifier, success rate and cost. The weight rungs stay a candidate only if at least one
  cluster has ≥30 instances/month, a verifier and a stable specification.
- **E1 (only on pass, and only with approval to install):** compare off-the-shelf
  SkillOpt-Sleep or GEPA on a held-out split before considering any training; check
  privacy first because Sleep can send transcript excerpts to the chosen provider.
- Otherwise AS02 reduces to a "specialization opportunity" report in the wedge
  (escalation rule, provenance, retirement), and AS09 to the verify-result field every
  ledger row already carries.

## 6. Foundry improvements made during this loop

Six interface gaps blocked the loop on day one and were filed as feedback before being
fixed (receipts `fa2ff832`, `dd10c1db`, `fadc862f`, `1837a96a` in v-foundry). An Opus 5.5
implementation agent (high effort, isolated worktree) delivered them under
[ADR-0019](../../adr/0019-discovery-records-sources-competition-revisions.md); the patch
was applied to the main checkout after a verified store backup, and `make check` (ruff,
strict mypy on 44 files, 174 tests + 12 CI-contract tests) and `make test-browser`
(5 Chromium flows) pass here.

| Gap demonstrated | What Foundry can do now | Where |
| --- | --- | --- |
| A local transcript could not be registered as a source or linked to ideas | `source register --input` (file path or URL; file hashed, never read as instructions; idempotent per content), `source show`, `idea link-source`; Sources page shows digest and linked ideas | `discovery_records.py`, Sources page |
| Competitor records existed in the schema but were unreachable | `market-actor register\|list\|show`, `idea link-actor --input` (relation, primary, note, `checked_on`, source refs; audited updates); idea page **Competition** table | additive migration `b10261009001` |
| Ideas could not be narrowed or pivoted | `idea revise --input` (append-only revisions, stale guard, competition carried forward); assessments labelled with the revision they judged | idea page **Revisions** |
| Only `derived_from` relations existed | `idea relate --input` for `combined_with`, `duplicates`, `pivots_from`; idea page **Related ideas** (both directions) | |
| A same-source cohort could not be compared or filtered | `idea compare --ids`, `/ideas/compare`, `/api/ideas/compare`, `idea list --source-id`, `/ideas?source_id=` with a compare button | `idea_compare.html` |
| Agent-created ideas showed as "User added" | `idea create --input` sets origin, every revision field and source links | |

New frictions found while using the upgraded tool are filed at this checkpoint: promotion
does not carry an idea's sources, competition or evidence into the venture workspace (the
venture map could not reference the idea's evidence; it was re-recorded at venture level),
a fresh venture gets no decision map from `venture-work create` (unlike an existing one),
`score rank` returns counts but not the ranked entries, and the discovery inputs are not
in the published `agent schema` registry (left out to avoid a contract bump; documented in
DEVELOPMENT.md instead). They are queued as maintenance package F05 (work `b4b14912-06f4-4bff-8ab0-3dd725c0a11c`, todo) by the accepted F02 result `d9afae3d-cbba-5c13-8067-f5fdcfeb2d66` (context `691d4370-0c43-5ad1-9283-d959d9eac2ef`; the first submission `2662801f` was superseded after this session's own feedback made it stale). Acceptance was a routine local acceptance by the coordinating session; nothing is committed, pushed, installed, bought, sent or deployed, and the operator store backup from before the migration is at `.local/backups/foundry.local.pre-discovery-records-20261009.db`.

## 7. Where to look in the console (`make foundry-ui`, http://127.0.0.1:8765)

- **Venture:** `/ventures/v-fleet-controller` → *Decision map* tab shows the goal, four
  measurable questions, C01–C05 and the conditional alternatives; *Work* tab lists the
  packages (only C01 is ready; nothing runs until claimed).
- **Cohort:** `/ideas?source_id=b3a1c5e5-c399-5b79-a9ba-4592ed5cd409` lists the ten
  transcript-derived ideas with scores and dispositions; **Compare these ideas** opens the
  per-criterion table.
- **Merged idea:** `/ideas/AS10` shows the seven sources (transcript + five research
  passes + direct checks), the four parents, incoming `combined_with` relations, the
  competition table and the score breakdown. `/ideas/AS04` shows the narrowing revision.
- **Inbox:** `/requests` → R014 lists the five decisions only you can make.

## 8. Limits

Agent judgments and web reads, not customer interviews; star counts are attention,
not adoption; absence of a feature in documentation is not proof of absence; terms of
service are volatile; no demand, pricing or legal clearance is established; a GO here
authorises only a local open-source MVP on the operator's own workloads.
