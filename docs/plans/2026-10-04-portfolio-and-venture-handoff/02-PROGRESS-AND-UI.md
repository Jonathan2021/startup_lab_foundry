# T02 advancement and T03 portfolio views

Goal: answer “what is this, how promising, how far along, why paused, what next?”
without opening every idea. Read `portfolio.py`, `application.py`, `web.py`,
`templates/{ideas,ventures,idea,venture,pagination}.html`, and current domain enums.
Keep FastAPI/Jinja/SQLite. No frontend framework rewrite.

## Separate the meanings

| Dimension | Meaning | Examples |
|---|---|---|
| Priority/criteria | Provisional attraction under one scoring method | 49/100; founder fit 8/10 |
| Investigation stage | Current question being investigated | Triage, competitor comparison, user problem, solution test, business model |
| Product maturity | What exists technically | Concept, prototype, MVP, pilot, operating product, unknown |
| Disposition | Current investment choice | Pursue, hold, dropped, internal only, use existing |
| Work/blocker | Whether and why the next task can proceed | Ready, in progress, needs human input, needs external access, needs setup |
| Confidence/coverage | How well-supported the assessment is | Imported confidence; reviewed low confidence; 8/12 factors |

Do not use `Idea.status=archived` as a synonym for dropped. Do not map work-item
completion, page count, stored evidence count or successful readiness steps to a
percentage of business validation. Coopain can be an existing prototype while its
business model is under investigation. These axes must permit that combination.
`Venture.stage` remains its existing lifecycle; don't silently change its semantics.

## T02a smallest persistent representation

Proposed design to settle in a product ADR before implementation: one append-only
`WorkspaceReview` table, reusing existing WorkItems/Artifacts for human requests.
Fields: id, workspace FK, revision number, investigation_stage, product_maturity,
disposition, next_action text, optional next_work_item FK, reason, author, reviewed_at,
optional source_artifact FK and optional decision FK. Unique `(workspace_id, revision)`.
Enumerate allowed values and explicit stage sort order in code; unknown is real.
Use the next work item's owner/status/blocked_reason for operational state; if no
next work is assigned, display “not scheduled”, not “ready”. No second parallel
business stage machine or generic workflow engine.

Suggested investigation values: `intake`, `triage`, `comparison`,
`problem_validation`, `solution_validation`, `business_validation`.
Suggested maturity: `unknown`, `concept`, `prototype`, `mvp`, `pilot`, `operating`.
Suggested disposition: `pursue`, `hold`, `dropped`, `internal_only`, `use_existing`.
Use `blocked_reason` codes `human_input`, `external_access`, `setup`, `other` for
new work, with human-readable details in description/question. Old free text remains
readable as `other`; do not recode historical records destructively.

- Return the latest review through one query/service shared by CLI and UI.
- Append changes with an expected previous revision to reject stale writes.
- Validate referenced work/decision/artifact belongs to the workspace. A source
  reused elsewhere is linked through explicit evidence/provenance, not an invalid FK.
- Keep idea and venture reviews independently attributable. Show linked venture
  summaries on idea rows; do not overwrite the original idea's review on promotion.
  If multiple ventures derive from one idea, show their count and labeled stages,
  never arbitrarily choose one as the single truth.
- Use migration from actual Alembic head and update DBML/schema tests. Keep the
  migration schema-only; campaign import is a separate idempotent command.

If a simpler existing typed model proves sufficient, document that evidence in the
ADR. Do not make the model rediscover every design decision or build a workflow DSL.

## T02b migrate the useful current state

1. Inventory **all** existing disposition strings from `ideas.json` and derived
   Artifact metadata; write a total mapping with an explicit unknown bucket.
2. Map INVESTIGATE/CONTINUE-like decisions to pursue; HOLD_* to hold with the
   specific blocker; STOP/REJECT to dropped; INTERNAL to internal_only;
   adopt/use-existing findings to use_existing. Inspect actual strings, don't
   assume these examples are the literal entire enum.
3. Preserve rationale, source artifact and date. Imported old status never wins
   over a newer explicit reviewed decision. T00's new answers may supersede old holds.
4. Map original triage completion to triage/comparison as supported, not validated.
   Register P023/P103 as actionable comparison candidates; label friends' access
   provisional. Register P046 as existing prototype + business investigation.
5. Human questions use existing WorkItems; capture answer artifacts with source
   section/digest and a reviewed/resolved outcome. Inbox file edits alone don't
   cause an automatic status change. UI can show “new answer awaiting review”.
6. Opening any held/dropped item shows reason, review date, next/reopen condition.
   Reopening appends a new review; old dropped/hold decisions remain accessible.

## T03 query contract and UI

Add one typed query object/service instead of sorting a rendered page in JavaScript.
Both HTML and JSON/CLI paths call it. Keep filtering/sorting/pagination in SQL with
one latest-review/latest-assessment subquery per view, avoiding N+1 record loads.

Supported inputs: `q`, `disposition`, `investigation_stage`, `product_maturity`,
`blocker`, `score_view`, `criterion`, `min_score`, `sort`, `direction`, `limit`, `offset`.
Validate allowlists, numeric range appropriate to selected score (100 vs 10),
nonnegative offsets and page limits. Use existing Venture.stage filter additionally
for ventures. Text query escapes SQL wildcard input consistently with existing code.

- Default: no hidden dropped/held rows; active filter chips and matching count.
  Use original scorecard priority descending initially, clearly labeled. User can
  choose reviewed scores, stage, recent activity or a criterion. “Needs my input”
  is a quick filter, not an implicit business priority score.
- Null scores sort last in both directions, with stable ID ties. Numeric 0 is a
  valid total and differs from null. Penalty columns say “higher = more risk”.
- Filters compose with AND, OR within a multi-select if supported. Reset offset on
  filter/sort changes. Pagination retains every active query parameter, not only q.
- List columns: ID/name; priority + confidence/provenance; founder fit/MVP speed
  or selected factor; investigation stage + maturity; disposition + blocker;
  next action. Do not show 12 cramped numeric columns at once.
- Mobile uses readable cards/stacked cells. Status text is visible independent of
  color. Add accessible sort labels, explicit empty state and clear-reset controls.
- Detail screens: criterion breakdown/history, source and reviewer, current review,
  next work, linked ventures/project checkpoints and outstanding human requests.
- Expose a small “Update review” form and criterion assessment entry/history so
  status/scores can actually change; agent CLI and user UI follow the same validation.
  A dropped→pursue change requires rationale/reopen condition, not a permission dialog.

## Tests and acceptance

Fixture at least six ideas: scored/unscored, dropped but high score, low-score
active, held for a human, existing prototype/business hold, and tied totals.
Assert combined filters, correct totals, numeric order, null-last asc/desc, stable
page boundaries and preserved query parameters. Assert cross-workspace reference
rejection, stale review conflict, explicit reopening and restart persistence.
Legacy import repeat must not overwrite a newer review. Test XSS escaping as today.

Browser tasks: find P046 using existing-project/maturity filters; find waiting-human
items; order sports ideas by founder fit; open an unscored derivation; navigate to
page 2 with filters; reopen a dropped disposable fixture and see its history.
Record desktop/mobile screenshots and check no clipped status/action information.
Do not claim faster human triage without measuring it; one timed task is enough
if you choose to make that claim. Keep provider installation independent.
