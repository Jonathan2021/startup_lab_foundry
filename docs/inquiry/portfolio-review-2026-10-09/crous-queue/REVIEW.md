# Crous Queue — portfolio review, 2026-10-09

Venture `f0b5abfe-0274-42f7-9c9a-72dcbe68c116`, workspace `81ee3117-de70-411e-9856-07420859ffad`,
repository `/home/jonathan/startup_lab/crous-queue`. Reviewer `reviewer-crous-20261009`.
This review was read-only: no code or git changes, no Foundry claims or results, and no outreach.
The local checkout is `70737c8`. Remote `main` is already at `cfd094c` (see §7).

**Recommendation: NARROW.** Stop feature work. Run one bounded real-use test at RU Cuvier/Châtelet
with explicit stop criteria. Treat the venture as a community utility with near-zero revenue,
not as a business.

## 1 Foundry record audit

**What Foundry records**
- Objective: "Find a university restaurant and see or report a recent wait in seconds…"
- Current review: `61a657df-899b-455f-b987-0b21f56e0c62`, revision 15, decision `4a24337d`.
  Disposition is `pursue`, stage `solution_validation`, maturity `concept`, `work_state: not_scheduled`
  and `next_work_item_id: null`. The next action is to maintain local MVP 0.2.0 and wait for R011 and
  the access/intake approvals.
- Decision map: `d941cc63-e8c7-5c54-855e-4887fd52bdf8` (sequence 18).
- Records: 16 work items (14 done, 2 blocked), 26 evidence items and 13 accepted decisions.
- Last result: `68e2292d-0dcc-58a7-a66a-be419167ded6` (Q11 delivery, CI `37845406291`).
- Open items, both blocked:
  - `dbbfbb3d-3ec5-5cca-8d2a-2eae04cc21b2`: check the Cuvier/Châtelet listings in incumbent apps.
    Agent-owned, `external_access`, open since 2026-10-06.
  - `4626ac2b-ae37-515e-998a-8634086981dd`: R011, the queue type and one own lunch observation.
    Human-owned, `human_input`. The request is in `requests/2026-10-06-crous.md` with a follow-up in
    `requests/2026-10-08-crous-R011-pilot-readiness.md`. The response block is empty.

**Score.** The brief says there is no score. That is wrong: there is one partial reviewed score.
- Assessment `2b38b397-ddd8-4c15-bb1a-f9d36df96e51` on scorecard `portfolio-reviewed-v1`, dated 2026-10-06.
- It covers 3 of 12 factors (problem 7, competition 8, network 8), so the total is `null`.
- Confidence is low. It has `scope_stale: true` and `reassessment_suggested: true`.
- The console reports it correctly: "Partial assessment · 3/12 factors · Assessment predates current scope".

**Five-minute human test: partial pass.**
- Clear: the purpose (objective), the human ask ("Answer R011 · Owner: you") and the two blocked items.
- Unclear or wrong:
  1. **Stage labels conflict.** The console header and map scope say "Discovery". The review says
     `solution_validation` and maturity "Concept", yet a CI-green v0.2.0 MVP exists.
  2. **The gating check was bypassed and never revisited.** Decision `ef07cc0b` said "Continue local
     information-gap investigation; no build commitment" until the incumbent check (`dbbfbb3d`) was done.
     GO decision `1825ca11` was then taken with that check still blocked. It has been agent-owned and
     blocked for three days. A human with an Android phone could close it in minutes.
  3. **The decision map is noisy.** It carries both `conditional_Q01–Q05` alternative nodes and record
     nodes for Q05–Q11, and Q09–Q11 each appear twice. The two blocked items, which are the only open
     work, are missing from the map. The map is a 100 KB single-line JSON on the CLI.
  4. **Evidence is mostly build receipts.** About 20 of 26 items are build/release receipts. None is
     real-user, demand or field evidence. The public September 2026 demand evidence (§2) is not recorded.
  5. **The record is drifting.** Foundry's canonical SHA is `70737c8`, but `origin/main` is `cfd094c`
     (PR #1, merged 2026-10-09 12:13Z, CI `37928637963` green). No Foundry evidence references it.
  6. **The venture is in limbo.** It is marked `pursue` with nothing scheduled and no revisit date. It
     should be an explicit HOLD with a trigger, or a NARROW with a dated test.
  7. **Navigation.** Crous Queue is the only venture with a raw-UUID id; the other 13 use `v-*` slugs.
     `/ventures/crous-queue` returns 404, so I had to copy the UUID from `.foundry/project.json`.
  8. **Revenue and costs** are "Unknown". That is honest, but nothing records that revenue is
     structurally near zero.
- CLI friction I hit: inconsistent ID flags (`--workspace-id`, `--venture-id` and `--id`). The JSON has
  no trailing newline, so it merges with stderr INFO lines and grep-filtering silently drops it. The
  wrapper also swallows `cli --help`. All of this is filed (§8).

## 2 Prior research gaps

| Claim (source) | Status 2026-10-09 | Source / date |
|---|---|---|
| Lunch friction is user-reported only; intensity is unmeasured (desk review 10-06) | **Strengthened, not recorded.** The €1 meal opened to all students on 2026-05-04. Crous meals are up 48% vs the 2025 rentrée. At Cuvier, students report ~40 min, and "at least an hour" after 12:30 classes; arriving at 11:30–11:45 means almost no wait. | [L'Étudiant 2026-09-18](https://www.letudiant.fr/lifestyle/aides-financieres/il-faut-arriver-avant-midi-le-repas-a-un-euro-du-crous-victime-de-son-succes.html); [CIDJ 2026-09-30](https://www.cidj.com/bien-vivre/sa-consommation/repas-a-1-euro-les-etudiants-face-a-l-affluence-des-Crous) |
| Affluences offers restaurant waits; deployed at 5 Clermont sites | **Confirmed, with new detail.** Video sensors (no identification, no storage) plus history, refreshed each minute, with forecasts. Free, no account. Page dated 2026-10-08/09. This is an operator-funded **automated** path that structurally beats crowd reports wherever Crous pays for it. | [Crous Clermont](https://www.crous-clermont.fr/2026/09/25/affluences-lappli-pour-consulter-le-temps-dattente-en-resto-u/) |
| Affluences coverage of Cuvier/Châtelet | **Still unverified.** Searches surfaced no Paris deployment; search absence is not proof. `dbbfbb3d` remains open. | WebSearch 2026-10-09 (no hit) |
| CrousRadar: collaborative queues on iOS, 4 ratings | **Unchanged.** iOS, free, 4 ratings at 5.0, v4.1.2 ("28 mai"); changelog plans "expansion dans toute la France". No city list. Android not checked. | [App Store](https://apps.apple.com/fr/app/crousradar/id6755202143), fetched 2026-10-09 |
| Not in prior research: Croustillapp | **New competitor for directory/hours/menus.** Android (F-Droid), ~1,000 Crous restaurants, menus, open-now filter, distances, 4 languages, Apache-2.0, v2.0.1 dated 2026-08-26, built on the public CROUStillant API. It has no queue feature. It removes most of the directory/hours value Q01/Q08 were built for. | [F-Droid](https://f-droid.org/fr/packages/fr.croustillapp/) |
| Not in prior research: official mitigations | **New.** CNOUS asked each Crous to define a maximum sustainable capacity; entry gauges are considered; takeaway and pre-order are being expanded; 204 FTE were hired. Crous & go' does click & collect on some campuses (e.g. Bordeaux). These reduce the problem, or move it to the operator. | CIDJ above; [Crous & go'](https://apps.apple.com/FR/app/id1570876523) |
| CNOUS directory licence `fr-lo` (verified in Q01) | Accepted; not re-fetched. The UI attributes "Licence Ouverte" but shows no dataset date in the footer. | `docs/THIRD_PARTY_NOTICES.md` |
| Students will report without reminders | **Untested.** Every adoption number is synthetic. | `docs/PILOT.md` |
| Information changes behaviour | **Unexamined.** Students already know "arrive before 12:00". The real constraint is class times, so the decision lever is probably "Cuvier vs Châtelet vs takeaway", which nobody has tested. | — |

## 3 Product and MVP assessment

**Job and user.** A Paris student with a lunch break, deciding where and when to eat. The decision
only matters for those who can shift by 15 minutes or walk about 10 minutes to the other RU.

**What works today** (verified locally on `70737c8`):
- National directory of 972 venues, with Cuvier (`paris:r177`), Cafétéria Cuvier (`paris:r889`) and
  Châtelet (`paris:r175`) kept distinct.
- Honest unknown state: "Aucun signalement récent", never "0 min".
- One-tap estimate or own timer, with 15-minute expiry.
- Map with gray for unknown.
- Meal/seat observations and moderated comments.
- Admin with a bearer token: `/admin/reports` returns 401 without it.
- Strong release discipline: CI, verified artifacts, backup/restore.

**What is missing**
- **Any way to use it at the restaurant.** The app is loopback-only on a laptop. Phones at Cuvier
  cannot reach it, so the five-lunch pilot cannot produce real reports without hosting or a tunnel.
  The hosting gate and the R011 gate are therefore coupled. The docs treat them as separate.
- **Sybil resistance.** I reproduced it. Six fresh cookies from one script posted six 120-minute
  estimates for Cuvier within seconds. The API then showed `state: recent, minutes: 120, count: 6`.
  The architecture documents this ("limits repeats, not Sybil attacks"), but count looks like six
  people, and the only ceiling is 120 per hour per /24. Campus eduroam NAT cuts the other way: one
  shared /24 could rate-limit legitimate users at peak.
- **Distribution**, and any revenue model.

**Verdict: NARROW.**
1. The problem is real and got worse in 2026.
2. The product's differentiator is crowd-reported waits at RUs without sensors. That depends entirely
   on contributor density per venue per 15-minute window. This is the hardest cold-start shape.
3. The directory/hours/map features are commoditised: Croustillapp covers directory and hours, and
   the official tools cover the rest.
4. The operator-side answer (Affluences sensors) exists and may reach Paris.
5. Revenue is near zero. Ads to students or reserved places are unattractive; selling to Crous puts
   it against Affluences.
6. Building more features is not justified. One cheap falsification test is.

**Single most important gate: real fresh coverage at Cuvier.**
- Measure across 5 ordinary lunch days, with checks at 12:15, 12:45 and 13:15.
- Pass: at least 40% of checks have a fresh (<15 min) real estimate.
- Pass: at least 3 distinct devices contribute on 2 or more days, without individual daily reminders.
- Precondition (P1): the human answers R011, checks Affluences/CrousRadar on Android, and the hosted
  payload is approved.
- **STOP/archive** if coverage stays under 20%, or if an incumbent already shows live Cuvier data.

## 4 Scores (portfolio-reviewed-v1, 1–10)

| Key | Score | Rationale |
|---|---|---|
| revenue | 2 | Free student utility. Ads and paid queue places are weak or ethically dubious. The B2B buyer (Crous) already uses Affluences. |
| profitability | 2 | Near-zero cost but no credible income, so it is a hobby/community economics. |
| mvp_speed | 8 | v0.2.0 is built and CI-green. The remaining work is hosting and hardening, not features. |
| founder_fit | 5 | Easy build for an ML engineer, but there is no ML edge until data exists. Success depends on on-campus community activation, which conflicts with limited sales time. |
| go_to_market | 4 | Users are dense at one site and word of mouth is plausible, but each venue/time slot needs local seeding, and any outreach needs approval. |
| moat | 2 | Trivial to copy. CrousRadar already exists. Data value decays in 15 minutes. |
| problem | 7 | Strengthened by public 2026 evidence (40–60 min at Cuvier), but the information lever is partly known already ("arrive before noon"). |
| retention | 5 | Daily habit only if data is fresh. It decays fast when it is not. |
| legal_risk (penalty) | 4 | Anonymous with moderation, so personal-data risk is low. The "Crous" name in the product could be a trademark/confusion issue (unchecked). Comment moderation becomes a duty once public. |
| capital (penalty) | 2 | €0 locally; a hosted beta is planned at ≤€25/month. |
| network (penalty) | 9 | Value is entirely contributor density per venue per 15 minutes. |
| competition (penalty) | 7 | Affluences (official, sensors), CrousRadar (crowd queues), Croustillapp (directory/hours/menus) and Crous & go'. No verified live competitor at Cuvier, hence not 8. |

**Totals and confidence**
- Weighted total is about **30** on the formula inferred from the existing contributions:
  positive = raw × weight × 10; penalty = −(raw − 1) × weight × 10. The formula is inferred, not documented.
- Overall confidence: **low–medium**. Demand is supported by press, but contribution behaviour and
  incumbent coverage are unmeasured.
- **score_change: record.** Replace the stale 3/12 assessment with a full 12/12 assessment that
  cites the new evidence IDs once a coordinator records them. This reviewer has no Foundry write
  authority.

## 5 Code audit

**Checks run on the canonical checkout `70737c8` with the project's `.venv` / `uv`**

| Command | Result |
|---|---|
| `make check` | Exit 0: Ruff "All checks passed", 71 files formatted, strict mypy clean on 32 source files, **40 passed** (36.5 s) |
| `uv run --locked pytest tests/browser` | Exit 0: **14 passed** (Chromium, 57.5 s) |

**Manual run.** I ran the app on a disposable copy of the dev DB (in the scratchpad, migrated
0003→0006) at `127.0.0.1:18090`, then stopped it. I did not run `uv build` or the release scripts.

**CI.** `.github/workflows/ci.yml` is solid:
- Actions are SHA-pinned, permissions are `contents: read`, and it uses `uv sync --locked`.
- It runs check, browser tests, both distributions, wheel and source-kit verification outside the
  checkout, a manifest, and 7-day artifacts.
- Latest run: `37928637963` on `main` (`cfd094c`), success.

**Findings**

| Sev | Finding | Path |
|---|---|---|
| major | Cookie-churn Sybil: new devices are free, so one client can fabricate a "6-report consensus" (reproduced). Needs a device-age/first-contribution delay, per-network new-device caps per venue, and honest wording ("6 appareils", not people). Blocks any shared or hosted use. | `src/crous_queue/security.py`, `services/waits.py:94-130` |
| major | Client IP comes from `request.client.host`, with no trusted-proxy handling. Behind the proposed reverse proxy, every user collapses into one network bucket, so 120 per hour site-wide. Campus NAT has the same effect at a smaller scale. | `app.py` middleware, `deploy/production.env.example` |
| major | Stale deployment proposal: it says "version 0.1.2" and "schema head 0003", while the code is 0.2.0 with migration 0006. Approval must not be sought on it. | `docs/DEPLOYMENT_PROPOSAL.md` |
| major (product) | No phone-reachable path. The pilot design assumes reports from phones but the app is loopback-only. | `docs/PILOT.md` |
| minor | Venue page renders an empty "Service :  (horaire historique)" line when hours are unknown. The two mapped RUs show "unknown" until a networked `refresh-hours` runs. | `templates/hours.html`, `services/hours.py` |
| minor | Raw region slugs appear in the UI ("Orleans.tours", "Nancy.metz", "Reunion"). | `/map` region select |
| minor | Licence Ouverte attribution has no dataset date in the footer. The directory is a frozen 2026-10-07 snapshot with no refresh schedule or age warning. | `templates/base.html` |
| minor | French-only UI: no English for international students. | `templates/` |
| minor | Documentation sprawl: ~16.5k words across `docs/*.md` and `docs/mvp/*.md`. The README is dense; a human 5-minute run works, but the status is hard to find. | `docs/` |
| minor | Duplicate historical `alembic/` (0001–0003) next to the packaged migrations (0001–0006). Intentional per ADR-0005 and documented on remote `main`, but confusing. | `alembic/`, `src/crous_queue/migrations/` |
| ok | Strict CSP; nosniff; no-store; 4 KB body cap. Writes need a custom header, JSON and same origin. Admin uses `hmac.compare_digest` with a separate token. Validation errors never echo input. defusedxml with an allowlisted, bounded, no-redirect fetch. Retention loop. Production config refuses SQLite/HTTP. Dev DB name guard (it refused my unmarked copy). Secrets live in an ignored 0600 `.env`. Dependencies have ranged constraints plus a committed `uv.lock` enforced in CI. | — |

**Test depth vs the MVP promise.** Strong for honesty states, expiry, idempotency, moderation,
migrations and upgrades. Absent: Sybil/abuse, PostgreSQL concurrency and proxy behaviour. Remote
`main` raises the core suite to 63 tests and covers the CLI, which had 0% coverage on `70737c8`.

## 6 Work packages (priority order)

1. **P1 — Human reality check (S, human).** Answer R011 (student queue, ordinary access). On Android,
   search Affluences and CrousRadar for "Cuvier" and "Châtelet" and record what shows. Optionally log
   1–3 own lunches (queue join, served, seat found). This closes `dbbfbb3d` and `4626ac2b`. There is
   no agent effort; it needs about 15 minutes of the founder's time.
2. **P2 — Foundry record reconciliation (S, coordinator, effort medium).**
   - Record the PR #1/`cfd094c` delivery and CI `37928637963`.
   - Record the §2 evidence: press demand, Affluences sensors, Croustillapp, Crous & go'.
   - Record a full 12/12 score.
   - Reassign `dbbfbb3d` to the human.
   - Set disposition NARROW with the stop criteria and a revisit date.
   - Prune the conditional map nodes and add the blocked items to the map.
3. **P3 — Abuse and proxy hardening (M, agent, effort high).**
   - Write red tests first, reproducing the six-cookie consensus and proxy-IP collapse.
   - Add a minimum device age before the first contribution counts toward the aggregate, and a cap on
     new devices per network per venue per 15 minutes.
   - Add trusted-proxy configuration that reads `X-Forwarded-For` only from a configured proxy.
   - Display "N appareils".
   - Add admin bulk-hide by network bucket.
4. **P4 — Hosted private-beta payload (M, agent, effort high, depends on P3).**
   - Refresh `DEPLOYMENT_PROPOSAL.md` and `deploy/proposal.json` to 0.2.0/0006.
   - Validate the PostgreSQL branch against a local disposable container.
   - Produce an exact approval payload: host, budget ≤€25/month, teardown and invite-only access.
   - Provision nothing.
5. **P5 — UI honesty polish (S, agent, effort low).** Fix the empty service line, add proper region
   labels, put the dataset date in the attribution, and add a directory-age notice.
6. **P6 — Real five-lunch test (M, human + agent, depends on P1, P4 and explicit approval).** Run §3's
   gate and report numerator/denominator per check. GO/STOP is decided strictly on the pre-registered
   thresholds.

## 7 Delivery state

- Remote: `git@github.com:Jonathan2021/crous-queue.git`. `origin/main` is `cfd094cc9273abba2f714799a226d3c5a5a043e8`,
  the merge of PR #1 "Cleanup and CI refresh (2026-10-09)".
- The local canonical checkout is still `70737c8a62bfee0ae07b3f990fbe647c73c96030` and is behind
  origin. I did not fetch or pull.
- CI: the last run is `37928637963`, a `main` push on 2026-10-09T12:13Z, conclusion **success**. The
  run before it, `37914570923` (the PR), also succeeded. `37845406291` on `70737c8` succeeded.
- No tracked files are dirty (`git status` is empty).
- Files I created in the repo are all gitignored: `.foundry/feedback-input-{1,2,3}.json` and
  `feedback/<UUID>.json` with their receipts. `.local/development.db` was copied, not modified.

## 8 Foundry friction filed

| UUID | Kind | Summary |
|---|---|---|
| `c8cf70d7-1c9d-464b-a815-1b7a5e46a5a7` | friction | Raw-UUID venture id while the other ventures use slugs; `/ventures/crous-queue` returns 404 |
| `a0ae626c-c0ba-4291-8c5a-684bbb7d6f7d` | bug | JSON stdout has no trailing newline and merges with INFO logs; inconsistent `--id`/`--venture-id`/`--workspace-id`; `cli --help` swallowed |
| `63f92c44-0561-484a-9599-73f0d828fb14` | idea | Stage-label conflict, a bypassed blocked gate never revisited, blocked items off the map, no repo-drift detection, stale score not turned into a task |

All three were delivered (`recorded_for_review`). Positive behaviour: the score's
`scope_stale`/"predates current scope" warning, and resume's explicit blocked owners.

```json
{"venture":"f0b5abfe-0274-42f7-9c9a-72dcbe68c116","recommendation":"NARROW","scores":{"revenue":2,"profitability":2,"mvp_speed":8,"founder_fit":5,"go_to_market":4,"moat":2,"problem":7,"retention":5,"legal_risk":4,"capital":2,"network":9,"competition":7},"confidence":"low-medium","score_change":"record","packages":[{"id":"P1","title":"Human reality check: R011 and incumbent apps on Android","description":"Answer R011 queue/access; search Affluences and CrousRadar for Cuvier and Chatelet on Android and record results; optionally log 1-3 own lunches.","acceptance":"R011 response block filled (unknown allowed); dbbfbb3d and 4626ac2b resolvable with dated observations; no accounts or third-party observation.","size":"S","effort":"low","depends_on":[]},{"id":"P2","title":"Foundry record reconciliation and full score","description":"Record cfd094c delivery and CI 37928637963, 2026 demand/competitor evidence, a 12/12 score, reassign dbbfbb3d to the human, set NARROW with stop criteria and revisit date, prune conditional map nodes and add the blocked items to the map.","acceptance":"venture-score show has coverage 12 and is not scope_stale; review disposition and revisit trigger set; map shows the open blocked items; no conditional duplicates.","size":"S","effort":"medium","depends_on":[]},{"id":"P3","title":"Sybil and trusted-proxy hardening","description":"Red tests reproducing cookie-churn consensus and proxy IP collapse; device-age gating, per-network new-device cap per venue window, trusted-proxy config, 'N appareils' wording, admin bulk-hide by network bucket.","acceptance":"Six fresh cookies from one network cannot produce more than the configured cap of counted estimates; X-Forwarded-For only honoured from configured proxy; make check and browser tests green; ADR updated.","size":"M","effort":"high","depends_on":[]},{"id":"P4","title":"Hosted private-beta approval payload","description":"Refresh DEPLOYMENT_PROPOSAL and deploy/proposal.json to 0.2.0/schema 0006, validate the PostgreSQL branch on a local disposable container, produce exact host/budget/teardown/invite-only payload. No provisioning.","acceptance":"Proposal matches current version/schema/checksum; PostgreSQL concurrency, migration and backup/restore tests pass locally; payload lists resources, max EUR 25/month, teardown commands; status NOT AUTHORIZED.","size":"M","effort":"high","depends_on":["P3"]},{"id":"P5","title":"UI honesty polish","description":"Remove empty service line for unknown hours, human region labels, dataset date in Licence Ouverte attribution, directory-age notice.","acceptance":"Browser test asserts no empty 'Service :' text, proper region labels and visible dataset date; all checks green.","size":"S","effort":"low","depends_on":[]},{"id":"P6","title":"Real five-lunch Cuvier/Chatelet coverage test","description":"After P1 and approved P4, run five ordinary lunch days with checks at 12:15/12:45/13:15; report numerator/denominator and returning devices.","acceptance":"Pre-registered thresholds: >=40% fresh real estimates at checks and >=3 devices on >=2 days without individual reminders = continue; <20% or incumbent live Cuvier data = STOP/archive.","size":"M","effort":"medium","depends_on":["P1","P4"]}],"feedback_ids":["c8cf70d7-1c9d-464b-a815-1b7a5e46a5a7","a0ae626c-c0ba-4291-8c5a-684bbb7d6f7d","63f92c44-0561-484a-9599-73f0d828fb14"],"blockers":["R011 human answer (4626ac2b) outstanding since 2026-10-06","Incumbent listing check (dbbfbb3d) blocked on external access; needs a human Android check","No approved hosting/phone-reachable access; local loopback MVP cannot collect real reports","Cookie-churn Sybil weakness must be fixed before any shared use","Local checkout 70737c8 behind origin/main cfd094c; Foundry unaware of PR #1"]}
```
