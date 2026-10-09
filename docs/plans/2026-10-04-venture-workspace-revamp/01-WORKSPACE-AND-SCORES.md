# Workspace layout and evolving scores

Implement V02/V03 using the existing templates and services. This is a proposed
interaction specification; the wireframes are not screenshots of working UI.

## Two levels of navigation

At portfolio level, use **Overview, Ideas, Ventures, Inbox, Proposals** as primary
navigation. Put Sources, all work/run history, outreach drafts and Help under
secondary navigation. Keep existing URLs working, including `/requests` and
`/steps`; add friendly labels without silently breaking links or CLI contracts.

Overview answers what needs attention: answers waiting for agent review, human
questions, proposed portfolio changes, and ready/blocked work. Show venture cards
with ID, score provenance, state, next action and owner. Counts must link to the
exact filtered queue and exclude resolved/deferred requests from “Needs you”.
Use `PortfolioViewService` instead of the dashboard's old `list_ventures` summary.

Inside a venture, retain a clear **Back to portfolio** link and a venture switcher.
Its scoped navigation is **Overview, Work and input, Evidence, Decisions, History**,
plus enabled modules. Separate **Scores** can be a header link to a detail section;
do not cram every record collection into the overview. All tabs include the same
identity header and operate on the selected workspace. Switching venture resets
scoped searches/filters; returning to the portfolio preserves its list filters.

## First screen contract

At 1280×800 desktop and 390×844 mobile, the initial viewport must include venture
name, ID, score or explicit unknown, and the contextual next-action control.
Descriptions and history belong below this area. Use text labels, keyboard focus,
proper form labels and visible errors; color is supplemental. Avoid fixed-height
cards that clip titles or mobile fields.

```text
Portfolio / Ventures / Cross-Sport ELO & Matchmaking
Cross-Sport ELO & Matchmaking          v-sports-session [Copy ID]
Source idea: P103 [open]

47 / 100   Starting estimate from P103 · reviewed idea · low confidence
12/12 factors · assessed Oct 4          [Breakdown and history]
Concept · Comparing alternatives · Pursue

Next action: Review your volleyball answer
R006 · Answer saved · Waiting for agent review
[View answer and next step]   [Copy agent handoff]

Overview | Work and input | Evidence | Decisions | History
```

This example applies before an independent venture assessment. It must never label
47 as a reviewed venture score. After intake/review, change the action to the
actual next task, such as **Review fusion proposal**. If no answer exists, show
**Answer R006** linking directly to its form; never send the user to “Update review”.

Idea detail uses the same compact header pattern with idea ID, current reviewed
score, original score as a secondary reference, source/parent links and linked
ventures. Show all linked ventures, not an arbitrary single one. Hide long original
source prose behind a disclosure; the current description gets a short readable
summary. Scores and ID precede the full state-review and score-history sections.

Choose the primary action deterministically: an unanswered non-deferred human
request, then an undecided proposal, then a pending answer review, then the explicit
next work item. Show additional concurrent items and owners in a compact list.
For held ventures, prefer the hold and reopen trigger over an unrelated generic
“Start step” control. Do not imply that copying a handoff has started an agent.

## Rename and separate the controls

- **Venture state** replaces “Current review”. It shows investigation question,
  maturity, disposition, blocker and next action. Its secondary edit action is
  **Update state**, with readable work-item choices instead of requiring UUID entry.
- **Questions and answers** has actual response fields, source-file links, saved
  status, review outcome and the next owner. See [input contract](02-INPUT-AND-HANDOFF.md).
- **Work** offers the next relevant task first. Local readiness checks, research
  briefs and manual agent requests remain available as secondary actions with
  accurate descriptions of their effects.
- **History** is a chronological, paginated view combining references to existing
  reviews, scores, answers, decisions, checkpoints and runs. It does not duplicate
  their storage. Each event has actor, date, type and a stable detail link.

## What the score means

Use the existing 12-factor priority rubric, Decimal calculation, bounds and
rounding. It is a provisional judgment of opportunity priority, not probability
of success, implementation progress, revenue or business validation. A score may
fall as work proceeds. No automatic increase for answered questions or closed tasks.

Keep score, confidence/coverage, maturity, disposition and work status distinct.
Revenue estimates are not observed revenue. A venture without evidence for a
criterion leaves it unknown; an incomplete assessment has no total. Display
**Not yet scored** or **Partial assessment · 2/12 factors**, never zero by default.
Actual numeric zero remains valid.

## Independent venture assessments

Do not write venture judgments into `IdeaAssessment`, mutate the source idea or
fabricate a new idea just to score an existing project. Add three narrowly scoped
tables in the next migration and document them in DBML:

| Proposed table | Required contract |
|---|---|
| `VentureAssessment` | Venture FK, scorecard FK, sequence, kind (`source_baseline`/`reviewed`), optional source `IdeaAssessment` FK, total nullable, confidence, rationale, author/time, immutable context JSON/digest, request key |
| `VentureCriterionScore` | Assessment FK, criterion FK, raw/normalized/contribution values, criterion rationale; unique assessment+criterion |
| `VentureCriterionScoreEvidence` | Criterion score FK, Evidence FK, optional note; unique pair; evidence must belong to the assessed venture |

Reuse calculation/scorecard validation and a shared presentation DTO. Avoid
copy-pasting the arithmetic. Keep existing idea tables, `RankingSnapshot` and
their historical IDs intact; do not retrofit venture rows into idea ranking entries.
List sorting of ventures does not require a new ranking snapshot feature.

Assessment sequence is unique per venture and scorecard. Append requires expected
latest sequence, actor and rationale; conflict returns 409. Repeated request keys
with the same payload return the same result; changed payload under that key is
a conflict. The DB enforces uniqueness, not only a pre-insert query. Criterion
FKs must belong to the chosen scorecard. Native assessments cannot use the original
workbook card; only the explicit baseline-import path may copy that card.

Context captures objective, source idea revision, current workspace review ID,
relevant evidence/decision IDs and their digest at assessment time. It explains
what was scored without adding a general venture revision engine. A changed scope
shows **Assessment predates current scope** until reviewed; it does not erase or
recalculate history. New evidence/decisions can flag **Reassessment suggested**
without performing it. On material findings, the manual agent's completion report
must either append an assessment or explain why no factor changed.

## Baseline and selection rules

During an explicit, repeat-safe bootstrap, snapshot the latest original and latest
reviewed assessments of each venture's pinned source idea revision, when present.
Copy values and retain their exact source assessment IDs and original provenance;
label the importer separately from the original assessor. This creates
`source_baseline` records, not new evidence. Later idea rescoring must not move a
venture's baseline. Never overwrite an existing independent venture assessment.
Enforce at most one baseline per venture/card; repeated bootstrap skips it even
if the source idea now has a newer score. Source changes require an explicit
new assessment, not refreshing the baseline in place.
Do not duplicate source-workspace Evidence FKs into venture criterion rows;
the source-assessment link supplies baseline provenance.

For detail headers:

1. Prefer the newest native `reviewed` assessment on the active reviewed scorecard.
2. Otherwise use that card's copied source baseline, explicitly labeled.
3. Otherwise show the copied original baseline as **Original idea estimate**.
4. Otherwise show unknown. A newer partial native assessment takes precedence
   over an older complete one; show the last complete number only as history.

Default list view becomes **Current reviewed** using the active reviewed card;
retain **Original workbook** and explicit custom-card views. A reviewed source
baseline can rank under the same reviewed card with its baseline label. Original
fallbacks appear only as secondary context in Current reviewed and are excluded
from its score filter/order. Never silently rank mixed card versions. Headers
explain a secondary fallback when a list's primary score is unknown.

Original view shows preserved source baselines for ventures and original idea
assessments for ideas. Shared `views.py` selection/filter logic serves HTML, JSON
and CLI. Fix venture cards to show the selected factor and its /10 or /100 scale;
today their query can select a factor while their text still shows priority.
Missing primary scores sort last both directions, with ID tie-breaking and
preserved pagination/filter parameters.

Carry the selected score view into detail links and accept it on detail routes;
label an explicitly selected historical/custom view. Without that parameter use
the active reviewed card. A browser back link must retain the original list query.

Show delta only against the previous assessment of the same subject/card and
compatible scope. Identify any first comparison to a copied source baseline.
Changed methods/scope show **Not directly comparable**. Every history entry opens
the factors, changes, evidence, author and date. The original workbook stays visible.

## Acceptance examples

- P103 detail immediately shows P103 and its reviewed idea score. Its venture
  immediately shows `v-sports-session`, source P103, and a clearly labeled starting
  estimate until an independent score exists.
- Two ventures from P103 can receive different scores; neither changes P103 or
  the other's score. Later P103 rescoring leaves both copied baselines unchanged.
- A venture with no source idea can be scored. A new partial assessment produces
  an unknown current total, with the older complete assessment still accessible.
- Repeated bootstrap and repeated save create no duplicates. Invalid evidence,
  stale edits and cross-card criteria are rejected without partial writes.
- Numbers and labels match across detail, cards, API and CLI for each score view.
