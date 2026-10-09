# Ride Options (`v-route-repair`) — portfolio review 2026-10-09

Reviewer: `reviewer-ride-20261009` (read-only on code and git). Repository
`/home/jonathan/startup_lab/ride-options`, local HEAD `6db7080`; remote main has
moved to `2d6fd6c` (see §7). All checks below ran on local `6db7080`.

## 1 Foundry record audit

**Identity.** Venture `v-route-repair` ("Ride Options", source idea N008), workspace
`6972ac19-0263-41c7-9f09-97b64fd99f80`. The slug is a holdover from the original
ETA-repair idea.

**Current state.**
- Review revision 18 `63d47d23-22be-4714-9214-32ac36a79d4b` (2026-10-08 22:29Z):
  pursue / solution_validation / concept, decision `18f22c69-2afd-497f-adda-e65913e59d76`
  ("0.2.0 delivered").
- Next work `281b3f40-3fb5-4906-b0ec-81cc70fbc030`, the imagery pilot source A/B
  decision (blocked, operator).
- Decision map revision `7b3191e3-ec8a-5fbe-8aa9-dd272d0fdbca` (seq 18, head_version 19):
  28 nodes, 31 edges, focus on the imagery work.
- Counts: 59 evidence, 16 decisions, 26 work items (22 done, 1 cancelled, 3 blocked).
- The three blocked items:
  - `281b3f40` imagery decision (operator).
  - `ae6816fd-bc8a-4feb-a97e-fe6f85b34d99`: rider/Kurviger comparison and regional
    access audit (operator).
  - `6a6b1c22-2ff1-4abe-b619-f4580a70dded`: superseded comparison, still
    `changed_context`/needs_review.
- R001 and R005 are resolved. The R005 continuation
  (`foundry/requests/2026-10-07-ride-R005-trials.md`) still has every operator
  response field empty.

**Score.** `venture-score show --id v-route-repair` works, but `--venture-id` fails
with an argparse error. The only assessment is `80ccd495-e890-4821-8dba-e38aebee4c0a`,
a source baseline:
- covers 2 of 12 factors (founder_fit 9, mvp_speed 5);
- has `total: null`, `scope_stale: true` and `reassessment_suggested: true`;
- uses the old objective ("shorten a specified ride… separate GPX path changes from
  ETA-model changes").

So the venture has no usable score.

**Coherence and navigability.** History is strong. Every package R01–R12 has a work
item, a decision, an evidence record with exact test counts, and a review revision.
A human can trace "what was built and verified" quickly. A five-minute reader would
still be misled in four ways:

1. **Contradictory maturity signals.**
   - The console header says "Discovery", and the map `scope.stage` is `discovery`.
   - The review says `solution_validation`.
   - The Now page shows revision 4's rationale as "Existing project checkpoint".
   - It lists `revamp-2026-10-05/ROUTE.md` as "prepared; trial not run".
2. **Inverted gate order.**
   - The focus and next action are the imagery source choice. The R11 doc itself says
     imagery is research-only, and routing works without it.
   - The gate that decides whether the product is useful is `ae6816fd` (R005 T01–T05,
     especially T03/T04 duration intent). It appears only as a secondary blocked item.
   - The map's `pilot` question ("Does the completed MVP help in repeated real use?")
     has no edge from `ae6816fd` or `281b3f40`.
3. **Map duplication.** Each package appears twice, as an `R0x` alternative node and
   as a `work_*` record node. The map page is 175 KB of text.
4. **Unrecorded delivery.** Remote PR #1 ("Cleanup and CI refresh", 56 new tests,
   merged 2026-10-09 12:26Z) is not in Foundry. Resume still reports "73 core tests"
   at `6db7080`.

Minor: `evidence list` shows blank `created_at`; `6a6b1c22` keeps a permanent
needs-review banner.

**Is "imagery pilot source A/B" the right gate? No.** Choosing an image source cannot
change the GO/NARROW decision. The core job (a 4–5 h ride shaped by preferences, with
fewer manual waypoints than Kurviger) is still unmeasured. Defer `281b3f40`. Make
`ae6816fd` the focus, preceded by the target-duration fix in §6.

## 2 Prior research gaps

All web checks are dated 2026-10-09; 5 of the 8 allowed searches were used.

| Claim (prior reports) | Status now | Source |
| --- | --- | --- |
| Kurviger already offers curvy planning and round trips | **Confirmed.** Round trips are set by distance, direction and curvature, not riding time. The basic tier limits round trips to 300 km; Tourer raises this to 600 km. App Store prices: Tourer €14.99/yr, Tourer+ €29.99/yr (listing undated). A forum thread reports a requested 222 km loop coming back as 450–680 km. | [Kurviger blog](https://blog.kurviger.com/en/kurviger-premium-options-tourer-and-tourer/), [App Store](https://apps.apple.com/app/id6473445827), [forum](https://forum.kurviger.de/t/difference-in-km-between-requested-round-trip-and-proposed-round-trip/5919) |
| Calimoto is a curvy-route incumbent | **Confirmed.** Loops are set by length and direction, with "Twisty/Super Twisty" profiles. Premium is about €59.99/yr (2026 guide). No time-based loop was found. | [GeoRide guide](https://eu.georide.com/blogs/georide/applications-itineraires-moto), [Bennetts review](https://bennetts.co.uk/bikesocial/reviews/products/motorcycle-technology/calimoto-motorcycle-route-planner-review) |
| Scenic, Detecht: overlap | **Partly confirmed.** Scenic sets round trips by distance and direction. Detecht offers curvy routes and round trips, with no duration detail. | [Scenic](https://apps.apple.com/app/id1089668246) |
| Time-budget loops are not novel (T8: Byway, Throttle, MotoRidez) | **Not re-verified.** The big three (Kurviger, Calimoto, Scenic) appear distance-based, which leaves a **narrow** opening for "loop of X riding hours with explicit tradeoffs". Niche claimants are still unverified. | prior evidence `route-t8-counterevidence` |
| Liberty Rider, 68°, MyRoute-app feature set | **Gap.** The search returned nothing specific, so there are no current feature or price facts. | — |
| Demand beyond the founder | **Gap.** The only sources are a self-report and selected Motardie/Kurviger posts. There are no interviews, no prevalence data and no willingness-to-pay evidence. | `route-public-reports`, `route-user-report` |
| GraphHopper Apache-2.0; OSM ODbL attribution | **Confirmed.** Attribution is a link to openstreetmap.org/copyright. The repo shows it on the map and in the GPX `<desc>`. Whether a GPX file is an ODbL "Produced Work" is unresolved, and the repo code licence is "not established". | [GraphHopper attribution](https://www.graphhopper.com/attribution/) |
| Panoramax etalab-2.0 imagery is usable for ML | **Partly.** Licences are set per instance (etalab-2.0 or CC BY-SA 4.0). Etalab permits commercial reuse with attribution but does not mention ML. The instance legal notice is still unread. Mapillary's restriction is a forum opinion, not a verified reading of its terms. | [Panoramax](https://en.wikipedia.org/wiki/Panoramax), [Etalab 2.0](https://www.etalab.gouv.fr/wp-content/uploads/2018/11/open-licence.pdf) |
| Historical 4h35 vs 6h04 ETA gap | Historical context only. The two tracks are close (68° is 3.3 km shorter) and there are no timestamps. | evidence `9e2c534a-…` |

## 3 Product & MVP assessment

**Job.** For one rider: "Give me 2–3 genuinely different A–B or loop rides that fill my
~4–5 h riding budget on nature, twisty, single-carriageway, low-light roads. Explain
the tradeoffs, let me nudge them, and give me a GPX my navigation app will follow."
The user is the founder, a motorcyclist in France with Belgium–France and Paris-exit
rides plus Auvergne. There is no second user yet.

**What works today (0.2.0, verified locally by me):**
- `make check` passes: Ruff, strict mypy and 73 tests.
- All 6 deterministic browser flows pass.
- The bundle rebuilds byte-identically.
- On a loopback run, the recorded Andorra demo generated:
  - an A–B with one option (11.7 km / 14.4 min);
  - a loop with one option (23.6 km / 34.1 min). For both, the other candidates were
    dropped as `duplicate_geometry`.
- The saved plan exported a GPX of 951 `trkpt`, with ODbL attribution.
- Other-owner access returned 401. Missing CSRF and a foreign Origin both returned 403.
- Proxy wording is honest throughout: "curvature proxy… Not beauty or safety", "Engine
  ETA is uncalibrated", and "Scenery proxy unknown" when no data is loaded.
- Feature set: itinerary editor, offline geocoder, approximate radius stops, landscape
  layers, break suggestions, rule-based NL criteria, opt-in edit evidence.

**What is missing for the actual job:**
1. **Riding-time target.** The contract has only `max_riding_minutes`. The loop seeds
   use `minutes/60 × 40 km × (0.45 | 0.65 | 0.85)`
   (`src/ride_options/services/generation.py` ~L244–260), so loops undershoot by
   design. R06 measured a 240-min maximum returning 68/142/156 min, and a 300-min
   maximum returning 89/175/171 min. Zero loops reach the stated 240–300 min.
2. **GPX that survives import.** The export is a track only, with no `<rte>`/`<wpt>`
   shaping points. That is exactly the path-change-on-import failure the user reported
   when moving a route into 68°.
3. **Coverage of the user's real rides.** Only Andorra and Auvergne are loaded; the
   Paris exit and Belgium–France rides are out of coverage.
4. **Road-use clearance.** 16 generic restriction relations remain unenforced
   (`docs/mvp/WARNING_AUDIT.md`).
5. **Any comparison against Kurviger.** No comparative judgment has been recorded
   (all fields null since 2026-10-07).

**Recommendation: NARROW.**
- Keep it as a private, founder-first planner for **time-budgeted loops with explicit
  tradeoffs and navigation-safe GPX**.
- Freeze the imagery and ML scope.
- There is no case for a broader consumer venture yet: competition is intense, the
  incumbents are cheap (€15–60/yr), there is no moat, and there is no external demand
  evidence.

**Single most important validation gate.** After the target-duration fix
(RO-P1), the founder runs R005 T03/T04 (Auvergne loop, 240–300 min) and T01/T02 in
both Ride Options and Kurviger. Record planning minutes, edits, the choice, and
"would repeat". The gate passes only if Ride Options yields at least one acceptable
in-band loop with fewer edits than Kurviger. Otherwise, use Kurviger and stop feature
work.

## 4 Scores (portfolio-reviewed-v1, 1–10)

| Criterion | Score | Rationale |
| --- | --- | --- |
| Revenue potential | 2 | Consumer niche. Incumbents charge €15–60/yr, and there is no B2B angle. |
| Profitability ease | 3 | Local engine cost is low, but hosting France or Europe routing plus low ARPU leaves thin margins. |
| MVP speed | 7 | A working local MVP exists; the target-duration and GPX gaps are bounded M packages. |
| Founder fit | 8 | The founder rides, holds the preferences and is an ML engineer. Geo/routing is adjacent, not core. |
| Go-to-market ease | 3 | App-store category already crowded. The product is desktop-local with no mobile app; rider clubs and forums are the only channel. |
| Moat | 2 | Built on OSM plus GraphHopper and replicable. Preference learning is speculative. |
| Problem intensity | 5 | A real personal pain (manual waypoint shaping), partly solved by incumbents. No external evidence. |
| Retention | 4 | Seasonal, weekend use. Enthusiasts do replan often. |
| Legal/ethical risk (penalty) | 4 | Road-access/safety liability, ODbL questions and imagery rights. Disclaimers are present. |
| Capital intensity (penalty) | 2 | Local and free so far. Regional engines need RAM, but no capex. |
| Network dependency (penalty) | 2 | The core works single-player; social features are deferred. |
| Competition intensity (penalty) | 9 | Kurviger, Calimoto, Scenic, Liberty Rider, 68°, Detecht, MyRoute-app, REVER and niche time-budget apps. |

Confidence: **low–medium**. This is desk research plus a code run, with no demand data.
Score change: **record**. The existing 2/12 baseline is stale and has no total.

## 5 Code audit findings

Checks run on local `6db7080`:

| Command | Result |
| --- | --- |
| `uv sync --locked --check` | no changes |
| `make check` | Ruff: "All checks passed!"; mypy strict: "Success: no issues found in 26 source files"; pytest: **73 passed** (11.3 s) |
| `node_modules/.bin/tsc --noEmit` (TypeScript 5.9.3) | exit 0 |
| `node_modules/.bin/esbuild client/app.ts --bundle --minify` into scratch (esbuild 0.25.12) | output **byte-identical** to committed `static/app.js`; the MapLibre worker, shared and CSS files are also identical to `node_modules` |
| `make test-browser` (`RIDE_BROWSER_EVIDENCE` pointed at scratch) | **6 passed** (76 s) |
| Recorded demo on 127.0.0.1:8141 | health, session, generate, save, GPX, 401 and 403 probes as in §3; server stopped afterwards |

Not run: `npm ci`/`make check-assets` (host npm 6.14.11; the target rewrites tracked
files), the real-GraphHopper replay, release bundle verification, any accessibility
tool.

| Sev | Finding | Path |
| --- | --- | --- |
| High | No riding-time target or minimum, and loop distance seeds deliberately undershoot, so the stated 4–5 h job is unmet (see §3). | `services/generation.py` ~L244–260, `contracts.py` (GenerateRequest) |
| Medium | GPX export is track-only (no `<rte>`/`<wpt>`). Navigation apps may re-route between imported points, which is the user's original pain. | `services/planning.py` ~L229 |
| Medium | Coverage is limited to Andorra and Auvergne; the user's Paris-exit and Belgium–France rides are unsupported. | `engine/*-manifest.json` |
| Medium | Access semantics rely on `car_access` plus a tag adapter, and 16 generic restriction relations are unenforced. This is disclosed correctly, but no road use should happen yet. | `engine/ride-motorcycle.json`, `docs/mvp/WARNING_AUDIT.md` |
| Medium | Client maintainability: `client/app.ts` has 378 lines, 19 of them over 300 chars (max 1122), in hand-minified style. It has no unit tests; it is covered only by end-to-end tests. | `client/app.ts` |
| Low | The API default `avoid_unpaved=True` disagrees with the unchecked UI checkbox. A raw API call with defaults on the recorded demo returns `infeasible` (`hard_constraint_or_unknown_details`). | `contracts.py:58`, `templates/index.html` |
| Low | The recorded or CI demo shows only one option per request. CI never exercises "distinct alternatives" on real data; only the opt-in replay does. | `data/recordings/*`, `tests/browser` |
| Low | UI is English-only (`lang="en"`) for a French rider. Addresses are FR via OSM. | `templates/index.html` |
| Low | Housekeeping: about 29 MB of tracked evidence, a 5.8 GB `.local` with 96 entries, and fixed port 8133 plus a 10 s start in `verify_bundle.py` (flaky, per PR #1). | `evidence/`, `.local/`, `scripts/verify_bundle.py` |

Positives: clean `RoutingProvider` boundary (recorded/fake/GraphHopper); bounded
engine budget (≤12 requests, 30 s); loopback security (CSP, HttpOnly SameSite=strict
session, CSRF plus Origin check, owner isolation); explicit Alembic migrations; locked
`uv.lock` and `package-lock` (dev deps `^` but `npm ci` pins); SHA-pinned Actions with
`contents: read`; honest proxies and ODbL attribution. `httpx2` is Starlette 1.7's
TestClient dependency, not a stray package. The README's recorded 5-minute path
worked as documented.

## 6 Proposed work packages (priority order)

Full descriptions and acceptance are in the JSON block below; summary here.

| ID | Title | Key acceptance | Size | Effort | Depends |
| --- | --- | --- | --- | --- | --- |
| RO-P0 | Foundry record/checkout hygiene: record PR #1 (`2d6fd6c`, run 37930036947), approved fast-forward, cancel `6a6b1c22`, defer `281b3f40`, focus `ae6816fd` linked to `pilot`, record score | resume shows `2d6fd6c`; focus `ae6816fd`; score 12/12 | S | low | — |
| RO-P1 | Target riding-time band: `target_riding_minutes` min/max; bounded iterative loop search on measured durations; honest "closest found" | synthetic-provider tests; Auvergne T03/T04 yields ≥1 loop in 240–300 min or a recorded reason; ≤24 requests, ≤45 s | M | high | P0 |
| RO-P2 | Founder trial vs Kurviger (operator), R005 T01–T04 | `ae6816fd` fields filled; continue/STOP decision recorded | S | low | P1 |
| RO-P3 | Navigation-safe GPX: optional `<rte>` shaping points and `<wpt>` stops beside `<trk>` | GPX 1.1 schema/order tests; one real import with km/min delta recorded | M | medium | P0 |
| RO-P4 | Fixes: `avoid_unpaved` default, reformat `client/app.ts`, free port in `verify_bundle.py`, FR strings | checks/browser/CI green; default pinned by test | S | medium | P0 |
| RO-P5 | Review the 16 generic restriction relations (topology, enforce/omit/narrow) | every relation dispositioned; required before riding any GPX | M | high | P2 |
| RO-P6 | One region matching real rides (Île-de-France or Nord/Belgium), only if P2 passes | pinned manifest; prepare within documented RAM; one trial passes | L | medium | P2 |

Imagery (`281b3f40`) stays deferred until RO-P2 shows scenery is the unmet need.

## 7 Delivery state

- Remote: `git@github.com:Jonathan2021/ride-options.git`.
- Remote main: `2d6fd6caa6110ea86a0f19f087e0154684c9142c`, the merge of PR #1
  "Cleanup and CI refresh (2026-10-09)" (2026-10-09 12:26Z).
- **Last CI run:** 37930036947, push on main, `2d6fd6c`, **success**.

Earlier runs:

| Run | Event | Target | Conclusion |
| --- | --- | --- | --- |
| 37912998474 | pull request | — | success |
| 37853206272 | push | `6db7080` | success |
| 37851908339 | push | `3f33d31` | failure (test race, later fixed) |

- Local checkout: HEAD `6db7080`, and the local `origin/main` ref is also `6db7080`
  (not fetched). The tracked tree is clean.
- Untracked files, all left untouched:
  - `feedback/e691adf6-….json` and its `.receipt.json` (pre-existing);
  - the outbox and receipt pairs this review created, listed in §8.
- Ignored inputs: `.foundry/feedback-input-rv{1..4}.json`.
- No processes were left running; the demo server on port 8141 was stopped.

## 8 Foundry friction filed

All four reports have status `recorded_for_review`.

- `f935582d-89f5-48dd-9cb9-61bf2cca3422` (bug): the Now page shows a stale or
  contradictory stage, a revision-4 checkpoint and a 2026-10-05 brief as current.
- `bc8fb5b7-a1f7-42ea-bd65-05902d2bc1e8` (friction): the focus is the optional imagery
  gate while the real validation gate is unlinked; the map duplicates alternative and
  record nodes.
- `c2d19d42-6edf-4be9-b4b3-ec177290f563` (idea): detect remote delivery drift past the
  last accepted result's SHA.
- `74692ccf-d4b8-48ea-bc07-49ad881e35da` (friction): `venture-score show --id` vs
  `--venture-id` elsewhere, and a permanent needs-review banner for superseded
  `6a6b1c22`. It also records a positive: resume JSON embeds the full proposal.

```json
{"venture":"v-route-repair","recommendation":"NARROW","scores":{"revenue":2,"profitability":3,"mvp_speed":7,"founder_fit":8,"go_to_market":3,"moat":2,"problem":5,"retention":4,"legal_risk":4,"capital":2,"network":2,"competition":9},"confidence":"low-medium","score_change":"record","packages":[{"id":"RO-P0","title":"Foundry record and checkout hygiene","description":"Record PR #1 (2d6fd6c, CI 37930036947) as delivery evidence; human-approved fast-forward of local checkout; cancel superseded 6a6b1c22; defer imagery 281b3f40; set map focus to ae6816fd and link it to the pilot question; record reviewed 12-factor score.","acceptance":"Resume shows 2d6fd6c; focus ae6816fd; no needs_review banner; score 12/12 recorded.","size":"S","effort":"low","depends_on":[]},{"id":"RO-P1","title":"Target riding-time band for loops and A-B","description":"Add target_riding_minutes band to GenerateRequest; replace fixed 0.45/0.65/0.85 loop distance factors with bounded iterative search using measured engine durations; return in-band options or honest closest-found reason.","acceptance":"Synthetic-provider unit tests for convergence, budget cap and infeasible reason; frozen Auvergne T03/T04 yields >=1 loop in 240-300 min or a recorded reason; request budget <=24 and deadline <=45 s documented; make check, browser suite and CI green.","size":"M","effort":"high","depends_on":["RO-P0"]},{"id":"RO-P2","title":"Founder comparison trial vs Kurviger (operator)","description":"Run R005 T01-T04 in Ride Options and Kurviger per COMPARISON_PROTOCOL.md; record planning minutes, edits, rejections, choice and would-repeat.","acceptance":"ae6816fd observation fields filled and a NARROW-continue or STOP decision recorded in Foundry.","size":"S","effort":"low","depends_on":["RO-P1"]},{"id":"RO-P3","title":"Navigation-safe GPX export","description":"Add optional rte shaping points and wpt stops alongside trk; document an import recipe for one navigation app.","acceptance":"GPX 1.1 schema and point-order tests pass; operator records km/min delta after importing one ride into one target app.","size":"M","effort":"medium","depends_on":["RO-P0"]},{"id":"RO-P4","title":"Small correctness and usability fixes","description":"Align API/UI avoid_unpaved default; reformat client/app.ts without behaviour change; free port and 30 s start in verify_bundle.py; FR strings for the main flow.","acceptance":"make check, tsc, browser suite and CI green; test pins the default; rebuilt asset hashes recorded.","size":"S","effort":"medium","depends_on":["RO-P0"]},{"id":"RO-P5","title":"Road-use restriction review for 16 generic relations","description":"Determine from/via/to topology for the 16 unenforced relations; enforce, omit or narrow; directed-turn fixture tests.","acceptance":"All 16 relations have a recorded disposition; T02/T04 exposures resolved; required before any GPX is ridden.","size":"M","effort":"high","depends_on":["RO-P2"]},{"id":"RO-P6","title":"Coverage for the user's real ride region","description":"If RO-P2 passes, add one region matching the founder's real rides (Ile-de-France or Nord/Belgium border) after measuring import RAM/disk/time.","acceptance":"Pinned manifest; local-prepare succeeds within documented memory; one trial in the new region passes.","size":"L","effort":"medium","depends_on":["RO-P2"]}],"feedback_ids":["f935582d-89f5-48dd-9cb9-61bf2cca3422","bc8fb5b7-a1f7-42ea-bd65-05902d2bc1e8","c2d19d42-6edf-4be9-b4b3-ec177290f563","74692ccf-d4b8-48ea-bc07-49ad881e35da"],"blockers":["Operator rider/Kurviger comparison (ae6816fd) unanswered since 2026-10-07","Local checkout 6db7080 behind remote main 2d6fd6c; fast-forward needs human approval","16 generic restriction relations unenforced; no road use of exported GPX","No external demand or willingness-to-pay evidence"]}
```
