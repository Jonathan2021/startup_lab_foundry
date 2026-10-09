# Current Foundry direction

Latest update 2026-10-09 (portfolio review): the six running ventures were re-reviewed
through Foundry ([report](inquiry/portfolio-review-2026-10-09/REPORT.md),
[protocol](inquiry/portfolio-review-2026-10-09/PROTOCOL.md)). Dispositions on the reviewed
scorecard: Crous Queue NARROW 30, Ride Options NARROW 35, Volley Match NARROW 37, Coopain
HOLD 31, OfferCheck HOLD 29, Volley Coach HOLD 30; v-sports-ranking is held as lineage.
Twenty-one implementation packages were delivered to GitHub `main` with exact-SHA CI
(`<slug>/DELIVERY.md`). Every venture now waits on a human gate registered from
`requests/` (R005, R006 ×2, R011, R013 by 2026-10-23, R014, R015). The loop's friction
became [ADR-0020](adr/0020-truthful-venture-state-requests-and-drift.md) and package
F10 (implementer follow-ups). Bridge `2026-10-09.1` is installed in all six repositories.

Latest update 2026-10-09: the user-supplied transcript `idea_queue/agentic_stack_ideas.md`
was processed as a Foundry discovery loop ([report](inquiry/agentic-stack-2026-10-09/REPORT.md),
[protocol](inquiry/agentic-stack-2026-10-09/PROTOCOL.md)). Nine transcript-derived
candidates (AS01–AS09) were scored on the reviewed scorecard against five dated
competition passes; they collapse into one open-source wedge, **v-fleet-controller**
(merged idea AS10: outcome ledger, quota-aware failover with durable handover and a
learned model/effort policy for unmodified official CLI agents under the user's own
logins), with five dependent packages C01–C05 and an initial decision map. AS04 is
narrowed to a research-ledger experiment for the ADR-0007 memory pilot; AS02 is held
with a metadata-only revisit test; AS05–AS07 and AS09 are dropped or use existing tools.
GO means a local open-source MVP on the operator's own workloads only. The loop
demonstrated six interface gaps, fixed under [ADR-0019](adr/0019-discovery-records-sources-competition-revisions.md):
source registration/linking, market-actor competition records, idea revisions and
relations, `idea create --input`, a source filter and a cohort comparison page.
Decisions needed from the user are in [R014](../requests/2026-10-09-agentic-stack-R014-wedge-decisions.md).

Latest product update 2026-10-09: Foundry `0.1.0` uses agent contract/bridge
`2026-10-09.1` ([ADR-0020](adr/0020-truthful-venture-state-requests-and-drift.md):
truthful venture state, open request files, repository drift, `--id` selectors).
The 2026-10-08 update used `2026-10-08.1`. Feedback from six implementation agents led to database-independent
schema discovery, conditional-branch guidance, explicit context/full-map coverage,
same-owner interrupted-work recovery, and accepted-result lineage that removes
replaced proposals from pending attention without deleting their history.
[ADR-0017](adr/0017-dogfood-contract-and-recovery-update.md),
[ADR-0018](adr/0018-accepted-result-lineage-and-standalone-release.md), and the
[operator guide](EXTERNAL_AGENTS.md) explain the behavior and upgrade procedure.

The current delivery target is a reproducible standalone repository: locked
installation, documented local use, regression and browser checks, installed-wheel
backup/restore/restart verification, and hosted CI for the pushed commit. See
[release verification](RELEASE_READINESS.md) for scope and commands. Operator
configuration, current venture claims, private review evidence and databases stay
local. Repository delivery does not establish commercial demand or authorize a
hosted deployment. Dated venture investigations below remain historical.

Latest update 2026-10-07: user-selected MVP implementation now takes priority.
[Priority campaign](inquiry/priority-mvps-2026-10-07/REPORT.md) prepares Volley Match,
Coopain, Ride Options, Crous Queue, Volley Coach and Foundry itself as independent
repositories/agent tracks. Local/private MVP construction is authorized; demand,
rights, physical-content review and public deployment are separate gates. Ride
Options owns A–B/loop creation with preference tradeoffs, not ETA diagnosis.
Crous starts with crowd-reported current waits and the national venue directory;
R011 ordinary-visit observations are optional later pilot data, not a build blocker.
Volleyball uses one canonical implementation workspace (v-sports-session), retaining
P023/P103 provenance and the pending historical fusion proposal. No second sports
implementation is queued. Video coaching is deferred in favor of availability-aware
personal progression. The later supplied `Generate Startup Ideas.md` resolves the
conversation source: [OfferCheck](inquiry/conversation-mvp-2026-10-07/REPORT.md)
now has an independent repo, synthetic quote-checking probe, dependent MVP map
and ready first package. It checks exact-SKU supplier offers; demand and advantage
over existing procurement workflows remain unvalidated. R012 is reviewed.

Each repo has .foundry/project.json, a scoped agent handoff and a durable feedback
outbox that syncs into Foundry's own evidence. Existing actor labels and claims
coordinate trusted local agents; they are not authentication for a hosted service.
The [outside-agent contract](EXTERNAL_AGENTS.md) works through the public CLI and
has an installed-wheel replay. No Foundry internals or Codex integration is needed.
MCP-only/remote agents remain unsupported directly; ADR-0016 keeps MCP an optional
adapter to add when a named host needs it.
The prior dated investigations and holds below are historical when superseded by
these explicit user-directed scope changes.

Latest update 2026-10-06: the user authorized a complete useful lifecycle MVP,
with monetization and model training deferred. The implemented direction is a
local venture workbench used with the operator's existing agent: capture a
change, prepare sufficient context, review proposed effects and resume later.
A versioned decision map connects current work with purpose and conditional
future choices. Portfolio views aggregate independently useful venture
workspaces. The [MVP release report](inquiry/lifecycle-mvp-2026-10-06/REPORT.md),
[operating guide](LIFECYCLE_MVP.md) and accepted ADR-0013/0014 supersede the earlier
planning-only status. Synthetic demonstrations cover discovery, an operating
software service and supplier operations. The Crous working map uses existing
records; its remaining inputs and incomplete score are retained. This is a local
release, not a hosted service or a demonstrated business.

The earlier repair report and its browser-access limitation below describe the
state before this implementation. Chromium now exercises the lifecycle and
selected earlier score/input/fusion workflows; exact coverage is in the release
report. Earlier dated evidence remains historical.

Update 2026-10-06: the [repair execution](inquiry/revamp-fixes-2026-10-06/REPORT.md)
fixes the [acceptance review's](inquiry/revamp-review-2026-10-06/REPORT.md) request,
fusion, intake, scoring, navigation and interface defects. Backed-up live migration
is applied; host tests and the official image/PostgreSQL/workflow path pass.
The [correction handoff](plans/2026-10-06-revamp-review-fixes/STATE.md) remains
unaccepted only at the desktop/mobile browser gate: no enabled browser is exposed.
Its retained Foundry task is explicitly blocked on that access. Manual queueing
does not start an unattended worker; the real sports proposal remains pending.
[Crous queue investigation](inquiry/crous-2026-10-06/REPORT.md)
now has primary-source research, three assessed factors, retained Cuvier/Châtelet
selection and a focused R011 input. It is a local coverage/data-supply investigation,
not a product build. Earlier dated context below remains historical where superseded.

As of 2026-10-05, Foundry is an **internal tool under evaluation**. The retained
[portfolio campaign](inquiry/portfolio-campaign/REPORT.md) is agent-owned under
[root ADR-0009](../../docs/adr/0009-agent-owned-portfolio-discovery.md), following
the [evidence-first investment decision](../../docs/adr/0008-evidence-first-venture-realignment.md).
All 238 workbook ideas and nine new bullets are in scope. Root
[ADR-0010](../../docs/adr/0010-product-first-foundry-operation.md) now prioritizes
Foundry and viable ventures; learning/slices are paused. The latest
[October 4 handoff report](inquiry/handoff-2026-10-04/REPORT.md) records criterion
scoring, reviewed portfolio state, filtered lists, existing-project intake,
manual outreach and help, plus bounded route/Coopain/sports/physical/receipt
investigations. The [October 2 report](inquiry/local-console-2026-10-02/REPORT.md)
remains historical. The [workspace revamp report](inquiry/revamp-2026-10-05/REPORT.md)
records durable answer review, independent venture score baselines, scoped console
views and a pending volleyball fusion proposal. No next commercial venture is qualified.

Use the existing application to retain assumptions, frozen protocols, evidence,
assessments, decisions, work and artifact references. Early feasibility/access
holds are distinct from completed competition studies. Technical trial success
is distinct from user adoption. Prefer use/adapt, narrow, defer or stop over
inventing a product to justify curriculum work.

The benchmark is ordinary project files and existing tools. Repeated omissions
in the experiment view justified exposing stored protocol fields; source reuse
and revision impact initially worked with ordinary registers. Repeated portfolio
inspection and restart friction now justify persistent idea/source intake and a
local operator console. Step outputs retain their input and runner identity. Add capabilities
only when actual repeated investigations demonstrate missing behavior and the
smallest change has a useful acceptance criterion. Do not generalize a platform
from shared terminology across unrelated ideas.

Agent EvalOps remains an independent deferred product and stop-or-pivot case.
Its run/trace seams and unfinished contracts are retained, outside current
implementation requirements. G002 research memory is an internal comparison,
not the automatic replacement venture. The original
[product brief](startup_foundry_project.md) and earlier
[G002 protocol](ventures/research-handoff.md) remain preserved source/history.

Hindsight v0.10.2 remains optional, uninstalled and unvalidated locally. Ordinary
records must work without it. Each project owns its data; central inquiry-memory
notes collect only tooling feedback. No paid inference, account creation,
external outreach, publication or provisioning is authorized by these trials.

Commercial value and useful open-source/portfolio value both matter. Future
learning work must serve an evidenced task and retain genuine learner ownership;
agent discovery earns no learner credit. Keep curriculum under `learning/`, and
do not prepare another slice until explicitly requested.


R005–R009 have been imported and reviewed, retaining the original inline answers
and R001–R004 receipts. R005 supplies broad route preferences and a target of
4–5 hours riding, with breaks separate. The supplied GPX geometry still does not
explain the reported ETA gap. The [route comparison brief](inquiry/revamp-2026-10-05/ROUTE.md)
is prepared; actual alternatives need an explicit routing basis and honest ETA
uncertainty. No planning-speed result is claimed.

R006 identifies outdoor friends volleyball, WhatsApp coordination and session
balance/pool/progression jobs. A planned six-person outing is not observed
attendance. P023/P103 remain separate; their
[volleyball-first proposal](http://127.0.0.1:8765/proposals/91fe8686-6638-5dba-bb0a-34fe222a0be5)
is pending. The [trial sheet](inquiry/revamp-2026-10-05/VOLLEYBALL.md) is prepared;
attendance, organizer role, formats and consent remain trial gates.

R007 confirms no real Coopain tests and no ownership/license agreement. Referral
bonus reports indicate possible access, not an employer buyer. The
[tester and ownership brief](inquiry/revamp-2026-10-05/COOPAIN.md) is prepared;
runtime verification and honest compatibility labeling precede private testing.
The earlier shared monetization discussion remains unreadable and unreviewed.
R008 holds N001 and related physical-task ideas pending competent feedback.
R009 holds N003/D003 and related receipt ideas pending a receiving practitioner.
Neither hold is in Needs you or a ready venture-investigation queue. Four receipt
outreach drafts remain unsent. D002 remains an internal integration.

Original idea scores and independent venture histories retain provenance. Nine
venture source baselines are copied and frozen; no new live native assessment was
invented from these replies. N008/D001 retains 2/12 factors and no fabricated
total. No interviews, repeat-use, sports sessions or payment validation occurred.
The console runs locally; schema, integrity and HTTP checks pass. Browser visual
acceptance remains pending because no browser is exposed. Official image checks
remain blocked by GHCR authorization, separately from successful local PostgreSQL
fixture verification. Saved next work is queued, not automatically running.
Use [the dated follow-ups](../requests/2026-10-04-followups.md) alongside
[the preserved editable inbox](../requests/INBOX.md). Reuse checked claims across ideas;
changed claims get new records. Do not turn documentary overlap or failed access
into a runtime pass, missing feature, or demand signal. Model training is deferred.
