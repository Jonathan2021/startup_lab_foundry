# Foundry lifecycle MVP release

2026-10-06. Foundry now supports a complete local loop for maintaining venture
decisions as evidence and work change. Its user can work in the browser or with
an existing agent through the CLI, from initial investigation through operating
software and supplier decisions. The useful unit is one venture; the portfolio
coordinates several without owning a second copy of their work.

This implements the user-authorized [MVP](../../plans/2026-10-06-decision-backbone/MVP.md).
Paid agents, billing, training and remote multi-user operation are deferred.
Local software readiness does not establish commercial demand or token savings.
The [operating guide](../../LIFECYCLE_MVP.md) covers use, installation and recovery.

## What ships

| Capability | Result |
| --- | --- |
| Today | Pending results and evidence changes across mapped ventures, human inputs and portfolio proposals |
| Venture Now | Visible ID and score, bounded work, change capture, context preparation and result review |
| Decision map | Goals, questions, conditional alternatives and existing record references; revision rationale, immutable history and affected-work preview |
| Context for an existing agent | Concise Markdown plus typed JSON, exact scope/versions, linked evidence and counterevidence, explicit missing coverage and fetch operations |
| Reviewed results | Findings retained separately from effects; mandatory UI effect preview before acceptance; accept/reject/defer with rationale; explicit task versus venture scope |
| Safe continuation | Changed context blocks dependent starts; stale results remain readable; reconciliation, claims/releases, duplicate receipts and atomic effects |
| Lifecycle semantics | Stop/hold without invented continuation; narrowing and follow-up work; operating maturity preserved; no automatic score increase |
| Existing portfolio features | Independent score histories, input reviews, fusion with scope/work treatment, scoped history, software and outreach views retained |
| Synthetic examples | Isolated discovery, operating billing and equipment-supplier scenarios; late supplier correction demonstrates stale-result handling |
| Local distribution | Wheel/source archive, installed-package migration/UI verification and official container/PostgreSQL checks |

The CLI exposes `agent resume`, `decision-map`, `handoff`, `result`, `change` and
`venture-work`; `agent guide` and `agent schema` make the contracts discoverable.
HTTP and CLI call the same services. Preparing context starts no worker.
An external agent performs the reasoning, then submits attributed findings and
explicit effects. A later managed executor could use these same contracts.

The map uses one coordination-head table and immutable artifact revisions.
Existing assumptions, evidence, decisions and work remain authoritative. There
is no graph database, new task engine, model dependency or plugin framework.
[ADR-0013](../../adr/0013-venture-coordination-and-executor-boundaries.md) and
[ADR-0014](../../adr/0014-decision-map-and-agent-context.md) record the boundaries.

## Concrete lifecycle examples

The billing demo already represents an operating service. Its release check can
be held because an account-boundary test fails while the venture keeps its
operating maturity. The next decision can revisit a corrected release. A hold
on that task does not secretly close the business or cancel unrelated work.

The supplier demo receives a correction after its agent returned a result. The
old findings remain available. Acceptance refuses obsolete effects, and a fresh
result can identify exactly what was retained or changed. These observations are
invented test data, never evidence about a real supplier.

The real Crous map connects the user's Cuvier/Châtelet investigation to the
already saved desk research. Its branches explain when to use an incumbent,
test one remaining arrival-choice gap, or hold because reliable observations or
data supply are missing. The criteria are explicit proposals, not measured
outcomes. The four existing evidence records, R010 answer, R011 pending input,
work blockers and partial 3/12 score remain intact. See [canonical records](records.json)
and [the exact map input](crous-map-input.json).

## Verification

The [functional trial protocol](../../plans/2026-10-06-decision-backbone/LIFECYCLE_TRIALS.md)
was recorded before the replays. Tests cover contradiction, new unlinked evidence,
scope changes, restarts, competing results, retries and an injected failure after
partial work had been staged. All trials use disposable stores except explicitly
identified live setup and read-only verification.

| Gate | Evidence |
| --- | --- |
| Full repository release suite | `make check`: Ruff, actionlint, strict mypy over 40 source files, repository boundary, product/CLI, official container and workflow contracts |
| Product checks | 142 passed; one explicit PostgreSQL-URL-dependent host test skips without that URL |
| Official container checks | 6 passed, including the new concurrent lifecycle acceptance test against PostgreSQL |
| Workflow contracts | 12 passed; browser tests are included in CI on Python 3.13 |
| Real Chromium interaction | 5 passed at 1280px and 390px, with no JavaScript errors or horizontal overflow in the checked flows |
| Earlier repair UI gate | Fresh idea/request/promotion/manual completion, source/partial/zero/custom scores, stale-tab errors, corrected inputs and older-reply labels, software links and hidden data, preserved filters/paging, scope/work edits, fusion accept/reject/reverse and keyboard focus |
| Lifecycle browser flow | Create a conditional branch, record evidence, expand context, return findings, defer, preview and accept, then reopen in a fresh browser session |
| Installed wheel | New environment outside the checkout; migrations, all three demo scenarios and eight UI/static routes pass |
| SQLite migration/recovery | 53 existing tables preserved, integrity/FKs and Alembic parity pass; online backup restored into a separate verified copy |
| Live UI/data | Six desktop/mobile route checks; 8,290 original rows unchanged before explicit repair-completion bookkeeping; no synthetic real-venture evidence |

Logs, screenshots, package hashes and reproducibility manifests are in ignored
`foundry/.local/lifecycle-mvp-2026-10-06/`. Final gates are `release-check.txt`,
`release-browser.txt`, `installed-wheel.json`, `migration-recovery.json` and
`live-verification.json`. Retained red/intermediate logs distinguish actual
failures from green checks. One existing FastAPI/Starlette/httpx deprecation
warning remains; no runtime failure is attributed to it.

The Chromium checks also close the earlier repair's browser-access limitation.
They use Playwright with a local Chromium executable, rather than requiring an
available in-app browser. The real sports fusion was not applied or rejected.

## Repairs found while building

- Initial intake previously assumed continuation. Stop/hold now finish without
  a fabricated ready task; holds require a revisit trigger. Later reviews retain
  operating maturity, including a previously operating venture with no review.
- Promotion could leave overlapping initial investigations. An unstarted source
  review is superseded into venture intake; claimed/completed source work remains
  explicitly linked instead of duplicated. Retry returns the same routing policy.
- A new evidence timestamp differed in memory and after SQLite reload. UTC
  normalization prevents unchanged accepted evidence from reappearing as new.
- Proposed references outside the original context are now pinned at submission.
  Changes to them prevent accepting the old result. Source associations are part
  of evidence fingerprints.
- Deferral now has a visible persisted state and rationale after restart, while
  remaining reviewable. An accepted result retains exact context-evidence links.
- Existing work-start and agent-step paths enforce the decision review boundary.
  Legacy broad agent execution is refused for mapped workspaces; callers use the
  bounded context/result flow instead.

## Live migration and recovery note

`foundry storage info` unexpectedly performed the additive `b10261006003`
migration before printing settings, because normal CLI setup migrated first.
That invocation added the empty decision-map table before the intended fresh
backup/rehearsal sequence. It did not change existing venture rows. The command
is now read-only and has an acceptance regression test; storage backup was already
exempt from migration.

A verified online backup, `live-before-maps.db` (mode 0600), was then made before
any real map or completion bookkeeping. On a copy only, the empty new table was
downgraded to `b10261006002`, re-upgraded and compared against all 53 pre-existing
tables. Integrity, foreign keys and schema parity passed; restoring a further
copy also passed. The live database was never downgraded. Earlier October 6
pre-upgrade backups remain untouched.

The initial ad hoc parity check used different Alembic autogeneration options and
reported reflected enum CHECK constraints as removals. Repeating with the
repository's existing migration configuration produced no schema differences;
no constraints were removed to make the test pass.

Before completion bookkeeping, the only additions were the Crous map head, its
artifact and audit entry; all 8,290 original rows matched. Closing the earlier
A01–A07 repair updates only its named work item and appends a release artifact,
audit event and explicit Foundry state review. Final canonical IDs and the exact
allowed change are retained in `records.json` and local verification evidence.
The prior reports and reviews remain historical records.

## Shipping and next use

Run `make foundry-ui` for the permanent store or follow the isolated demo commands
in the operating guide. The local console and demo are available on ports 8765
and 8766 respectively. Wheel and source archive are retained under
`.local/lifecycle-mvp-2026-10-06/dist/`; the package has not been published.
Both repositories were dirty at the start. Baseline file hashes/statuses and the
final changed-file manifest are retained; unrelated edits were preserved. No
commit, push, external deployment, paid inference, outreach or learning work was
performed.

The next useful checkpoint is repeated real use: record a new observation or
operating change, let an existing agent resume from Foundry context, and inspect
what had to be reconstructed manually. The earlier comparative agent-versus-file
cost replay remains unrun here. Smaller context and successful synthetic trials
do not establish lower whole-job token cost. Add managed execution or training
only after a repeatable task, measured quality and practical savings justify it.

The local trust boundary, bounded map/context sizes and inability to terminate
external agent processes are deliberate limits of this MVP. It is ready for
local use and distribution, not an authenticated hosted SaaS.
