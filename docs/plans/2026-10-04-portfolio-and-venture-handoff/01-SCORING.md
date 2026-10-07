# T01 scoring import and T10 reassessment

Goal: useful, explainable scores now, with tunable versions later. No learned
success-probability claim. Read `domain.py`'s scoring models, `portfolio.py`,
`docs/adr/0003-foundry-domain-and-dependencies.md`, and the two named source CSVs.

## Exact original calculation recovered

The CSV guide omits a detail: each penalty uses **raw score minus one**. Reading
`xl/worksheets/sheet2.xml` in the original XLSX recovered `Ideas!AK2`:

```text
MAX(0,MIN(100,ROUND(10*(0.22*X2+0.18*AA2+0.12*AB2+0.15*AC2+
0.10*AD2+0.08*AE2+0.10*W2+0.05*AF2-0.10*(AJ2-1)-0.06*(AI2-1)
-0.05*(AH2-1)-0.04*(AG2-1)),0)))
```

All **238** CSV priority values reconcile exactly using Decimal arithmetic and
Excel-compatible half-away-from-zero rounding. The initial naive calculation
without the minus-one penalty offset mismatched 237 rows; do not repeat it.
Examples: P023=49, P046=47, P103=45, G002=79. Preserve these legacy judgments.

| Criterion key | CSV header | Direction | Weight |
|---|---|---|---:|
| revenue | Revenue potential | positive | .22 |
| profitability | Profitability ease | positive | .18 |
| mvp_speed | MVP speed | positive | .12 |
| founder_fit | Founder fit | positive | .15 |
| go_to_market | Go-to-market ease | positive | .10 |
| moat | Moat / defensibility | positive | .08 |
| problem | Problem intensity | positive | .10 |
| retention | Retention potential | positive | .05 |
| legal_risk | Legal / ethical risk | penalty | .10 |
| capital | Capital intensity | penalty | .06 |
| network | Network dependency | penalty | .05 |
| competition | Competition intensity | penalty | .04 |

Raw scale is 1–10. Positive weights sum to 1; penalty weights sum to .25.
`priority = clamp(round_half_away(10*(sum(w*x)-sum(p*(risk-1)))),0,100)`.
Store weights as nonnegative and use existing `ScoreDirection.PENALTY` for sign.
For existing normalized fields use positive `raw/10`, penalty `(raw-1)/10`;
weighted contribution is signed `100*weight*normalized`, in score points.
Don't normalize the combined positive/negative weights to sum to one.

Legacy grades: A≥70, B≥58, C≥45, otherwise D; source category exactly
`Reject: deceptive / harmful` gives X. Preserve the imported grade and recommendation
as source history. The original “A → build” guidance must not automatically create
a build decision. A later review can disagree without editing the original row.

## T01a deterministic core and import

1. Add a small `scoring.py` service with typed assessment input, pure calculation,
   and persistence methods. Use existing scoring tables, transactions and errors.
   No provider/model SDK belongs in this code. No spreadsheet runtime is required.
2. Tests first: formula anchors above, all 238 rows, rounding half values, bounds,
   penalty direction, blank/zero/out-of-range/nonfinite inputs and duplicate IDs.
   New assessments require 1–10 scores or explicitly missing values; 0 is invalid.
3. Register immutable scorecard `portfolio-original-v1`, 12 criteria and one
   imported assessment per original idea revision. Preserve source confidence as
   **reported confidence**, visibly labeled imported/unreviewed, not independently
   established certainty. Preserve original pros/cons and source recommendation.
4. Store CSV SHA, row/Idea ID, original formula identifier, import date, supplied
   rank and monthly-revenue ranges in a linked provenance Artifact. Existing
   `revenue_year_1/year_3` fields are not the same measure as “mature monthly revenue”;
   leave them null. Never convert unvalidated ranges into forecasts or cash flows.
5. Use content/identity-based receipts; reimport of the same source from
   `docs/sources` must reuse provenance already recorded from Downloads. The
   `ReferenceSource.locator` can remain historical; add an availability reference
   instead of silently rewriting it or creating a duplicate for a relocated file.
6. Load all 238 assessments atomically; the remaining 12 ideas display “not scored”.
   On conflicting changed rows, stop that import and report which IDs need explicit
   revisions; no overwriting history or automatic averaging.
7. Add CLI commands such as `scorecard list`, `score show --idea-id`,
   `score import-original --sources-directory`, and `score assess --input FILE`.
   Names may follow existing CLI conventions; document the final actual grammar.

Acceptance: 238 assessments, 2,856 criterion rows for this import, exact score/grade
parity, no duplicate ideas, repeat import does nothing, original files unchanged.
Do not assert those as global database counts after later assessments are added.

## T01b expose multiple useful scores

Show the priority total plus individual criteria. Default list view shows priority
/100, founder fit /10 and MVP speed /10. Detail view shows all 12 dimensions,
penalty direction, rationale/evidence, confidence and version. A list score selector
can switch the sorted/displayed criterion to profitability, problem intensity,
competition, etc. This meets the multiple-score need without inventing unrelated
composite indexes. See subplan 02 for sorting and unknown-value rules.

Allow both **Original workbook** and **Current reviewed** views. Within a view,
compare the same scorecard/version. Do not silently mix newly assessed v2 totals
with unrevised v1 totals in one ranking. Expose unscored/currently unreviewed counts.
Keep founder enthusiasm visible as an attributed observation; it need not imply
market demand. Don't inflate commercial criteria because the founder likes an idea.

## T10 score tuning and evidence

- After a real investigation, append a new assessment for its exact idea revision,
  carrying forward unchanged scores explicitly and explaining changed ones. Use
  source/evidence links; cross-workspace reuse must reference source provenance
  without bypassing the domain's workspace rules. Never rewrite an old assessment.
- Permit partial assessments: omit unknown CriterionScore rows and leave total
  null until all required criteria exist. No silent zero, neutral five or imputed
  average. Show supplied-factor count alongside the confidence label.
- New weights/rubric mean a new Scorecard version. Freeze criteria used by existing
  assessments. Reject duplicate criterion keys and invalid weight/scale values.
- Add a narrow scorecard clone/edit CLI or validated JSON import; avoid building
  a spreadsheet designer. Store old/new rationale and run the same benchmark cases.
- Provide sensitivity output for named profiles or one-factor ±1 changes, keeping
  versions explicit. This reveals fragile rankings; it is not a probability model.
- Record observations that could eventually calibrate scores: tried incumbent,
  repeated use, abandoned trial, actual willingness to pay, actual cost, access.
  Synthetic examples test software only. A handful of friends is not calibration
  data for the whole portfolio. Don't optimize weights to make favorite ideas win.
- `RankingSnapshot` captures explicit comparisons with exact assessment IDs. Missing
  totals are excluded with a stated count; tie-break by stable Idea ID. Legacy CSV
  ranks may use source-row tie order, so preserve them as source ranks separately.

Target files: new `scoring.py`; CLI/console dispatch; `portfolio.py` summaries;
focused unit/integration tests. No schema migration should be required for the
base import. If provenance lacks a needed typed field, prefer an existing Artifact
before adding redundant score tables. Update DBML/ADR only for a material schema change.
