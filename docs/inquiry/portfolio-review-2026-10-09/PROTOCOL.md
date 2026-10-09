# Portfolio review and dogfood loop — protocol (2026-10-09)

Status: frozen before the venture reviews ran. Owner: Claude Fable 5.1 session
`fable-portfolio-20261009`, coordinating Opus 5.5 review and implementation agents.
Request: for Coopain, Crous Queue, Ride Options, Volley Match, OfferCheck and Volley
Coach (Foundry last), inspect what Foundry records, re-check prior research, re-score
where warranted, judge MVP/direction (GO / NARROW / HOLD / STOP), audit code sanity,
implement justified improvements, and leave each venture with clean Foundry entries,
a clear decision history, a tested human-usable codebase with CI, pushed to main.
Foundry friction met along the way is recorded as feedback and fixed at the end.

## Baseline

| Venture | Foundry id | Repo main | Score | Review |
| --- | --- | --- | --- | --- |
| Coopain | v-coopain | f3a8c13 (7 untracked leftovers) | 48 | pursue / prototype / rev 14 |
| Crous Queue | f0b5abfe-… (raw UUID) | 70737c8 | none | pursue / concept / rev 15 |
| Ride Options | v-route-repair | 6db7080 (2 untracked feedback files) | none | pursue / concept / rev 18 |
| Volley Match | v-sports-session | 2679b75 (untracked `remarks/`) | 47 | pursue / concept / rev 17 |
| OfferCheck | v-offer-check | 411d683 | none | pursue / concept / rev 10 |
| Volley Coach | v-volley-coach | 28f611c | none | pursue / concept / rev 10 |
| Foundry | v-foundry | 2836464 + uncommitted ADR-0019 package | none (internal) | internal_only / mvp |

All six venture repos have a GitHub remote under Jonathan2021 and a workflow file.
Last verified exact-head CI (2026-10-08): coopain 37791874356, crous-queue 37772856832,
ride-options 37764771577, volley-match 37762687240; OfferCheck and Volley Coach had
later commits whose runs are to be checked.

## Hypotheses

- H1: Each venture's Foundry record is coherent enough that a human can state its
  purpose, current decision, open gates and next action in five minutes. Expected
  failures: unscored ventures, legacy blocked work with `changed_context`, raw-UUID
  venture id, next actions pointing at old folders, unresolved fusion proposal.
- H2: Prior reports' GO decisions rest on build feasibility, not demand; at least one
  venture should move to HOLD or NARROW once competition and demand are re-checked.
- H3: Code quality is acceptable (tests, lint, types, CI green) but human usability
  and documentation lag; improvements are bounded packages, not rewrites.
- H4: Running six review agents and later implementation agents through the repo
  bridges will surface recurring Foundry friction (navigation, ids, provenance,
  scores) that justifies a bounded Foundry package at the end.

## Bounded checks

1. Review agents (read-only on code): Foundry record audit, prior-research gaps with
   ≤8 web checks each, product/MVP assessment with explicit GO/NARROW/HOLD/STOP,
   12-criterion scores with rationale and confidence, code audit with severity, work
   packages with acceptance criteria, delivery state, Foundry feedback filed through
   the repo bridge. Deliverable per venture: `<slug>/REVIEW.md` with a JSON block.
2. Coordinator: record reviews/scores/evidence/map changes per venture through the
   public CLI; reconcile stale blocked work with explicit treatments; resolve or
   supersede the sports fusion proposal; keep originals immutable.
3. Implementation agents (Opus 5.5, effort by complexity): one writer per repo,
   claim the first ready package through the bridge, implement with tests, run the
   repo's checks and browser suite, commit, push to main, report the exact SHA and
   Actions run; file feedback at each checkpoint.
4. Foundry last: triage all new feedback into bounded packages (F05 provenance and
   schema publication, plus whatever recurs), implement, `make check` + browser,
   commit, push, verify CI on the pushed SHA.

## What a result means

GO means continue bounded private/local implementation; it is not demand validation,
legal clearance or permission for hosting, payments or real-user trials, which remain
human gates in `requests/`. Scores are agent judgments on the reviewed scorecard.
Pushing to main is explicitly requested by the user for these repositories; no new
remote, account, deployment, spend or message is created. Nothing is deleted from
working trees; untracked operator files are reported, not removed.
