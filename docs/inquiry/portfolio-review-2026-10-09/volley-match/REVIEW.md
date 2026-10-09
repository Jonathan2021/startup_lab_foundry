# Volley Match: portfolio review, 2026-10-09

Reviewer: `reviewer-volley-match-20261009` (read-only on code and git). Venture
`v-sports-session`, workspace `417476af-0674-4aba-9022-843957dc3ca2`, repository
`/home/jonathan/startup_lab/volley-match`. I audited local checkout `2679b75` (release
0.2.0). **Remote `origin/main` has since moved to `991d702`** (see section 7).

## 1. Foundry record audit

**What Foundry records (exact IDs)**

| Record | State |
|---|---|
| Current review | `28ec9289-e1e5-4e42-8b09-bf0f4bffd7b4`, rev 17, pursue / solution_validation / **concept**, work_state not_scheduled. Next action: "Await the user's review of 0.2.0 … no agent work is queued." |
| Decision history | 14 decisions. Venture GO/narrow is `a38e9141-b5be-4e52-99fb-b8cbd4f790f1` (2026-10-07); then one accepted per package (V01 `56ebca3a` … V11 `acb549d8`). |
| Work | 16 items, all done; none ready or claimed. V01–V11 are `73728cfb`, `0ed146e4`, `1a037613`, `fc1377b7`, `437b8fae`, `f0c29b5f`, `3f666496`, `4ca1f74c`, `96e91ea1`, `5b934784`, `594f78a3`. |
| Results | 12 accepted. Latest is `bb34b271-67c4-543d-903a-c069d3b2773a` (0.2.0 pushed, CI 37848352127). |
| Evidence | 24 items. Only **2 are demand-side**: `0cb2ab7f` (user plays outdoors and uses WhatsApp, medium) and `6f954bb0` (handoff, low). Item `9e0cefe9` explicitly says real usefulness is unobserved. The other 21 are technical or delivery evidence. |
| Decision map | Revision `584d51b8-35a5-55f0-afcd-88c6b28f8d24`, 24 nodes / 30 edges, no stale references. Its open question node `pilot` ("Does the completed MVP help in repeated real use?") is the real gate. It says "Do not expand features until voluntary reuse evidence"; V08–V11 were user-authorized exceptions. |
| Score | 47.0, low confidence. Kind `source_baseline` (`c6b7fd44`), dated 2026-10-05, with `scope_stale=true` and `reassessment_suggested=true`. It has never been reassessed. History shows two rows that are both "sequence 1" (47 reviewed card / 45 original card). |
| Human gate | `foundry/requests/2026-10-07-volley-match-R006-pilot-access.md` is OPEN and every response field is blank. The user answered with feature remarks instead. |

**Five-minute clarity.** The purpose is clear and so is the "nothing queued" state. Five things mislead a human reader:

- **Stage and maturity contradict each other.** The venture header says **Discovery**, and agent-resume `scope.stage` is `discovery`. The review says solution_validation. Maturity is still "Concept" after a released, CI-verified MVP.
- **The fusion proposal still looks active.** "Review fusion proposal · Owner: you · Proposed" sits beside the current focus on both sports ventures.
- **The sibling venture looks alive.** `v-sports-ranking` still shows Pursue, with a 2026-10-05 focus ("Review the pending volleyball-first fusion proposal…") and a **higher score (51)** than the venture that was actually built.
- **The score is stale.** It predates every MVP package.
- **Foundry does not know about the remote change.** It has no record of PR #1 or of `991d702` on remote main.

**Fate of the fusion proposal.** Proposal `91fe8686-6638-5dba-bb0a-34fe222a0be5` ("Volleyball Sessions and Fair Tournaments", revision `3d7a168a`) is still `proposed` and has no resolution. It is no longer meaningful as a decision to take:

- Decision `a38e9141` already states that "P103 is the canonical build workspace. Preserve P023 and the historical pending fusion proposal as lineage, not another implementation queue."
- The proposal's `source_state` is pinned to review revision 3. The current revision is 17.
- Its `result_venture_id` would create a **third** venture, `v-volley-sessions`, duplicating the shipped one.

**Recommendation (coordinator or human authority):**

1. Resolve the proposal as *superseded by decision a38e9141*. Do not accept it.
2. Set `v-sports-ranking` to dropped/merged lineage, pointing to `v-sports-session`.
3. Keep P023's tournament, seeding and sponsorship ideas as deferred hypotheses on `v-sports-session`.

Foundry has no staleness signal for this situation; I filed it as feedback `fe29bb87`.

## 2. Prior research gaps

| Prior claim / gap | Status 2026-10-09 | Source |
|---|---|---|
| Rankade already supports private groups and team rankings (SOURCES.md, 2026-10-07) | Not re-checked this pass; still cited as documentary | https://rankade.com/ |
| Green Volley Paris = calendar + WhatsApp coordination | **Confirmed.** Monthly calendar (9 Oct highlighted) and a "rejoins le groupe" WhatsApp link. No sign-up, levels or rankings described. | https://greenvolleyparis.com/fr (fetched 2026-10-09) |
| **Gap: Spond never assessed** | Free group app (web and mobile) with events, RSVP, reminders and polls. Its volleyball page describes availability requests, then **allocating players to teams**. It is the main free coordination incumbent. | https://www.spond.com/en-us/activity/volleyball/ |
| **Gap: WhatsApp native Events** | Events with RSVP now work in ordinary group chats, alongside polls. They cover the coordination half at zero switching cost for a WhatsApp group. | https://lowyat.net/2024/328466/whatsapp-events-group-chats |
| **Gap: VolleySmart** (closest direct comparator) | Free, web. Clubs, invites, one-tap RSVP, **auto-balanced teams by skill and position**, live scoring, public discovery; EN/ES/DE, no French. Launched around June 2026 with negligible visible traction. | https://peerpush.com/p/volleysmart |
| **Gap: Spiker Pro** | iOS. **Elo** with division leaderboards, pickup-game finder, organizer scoring and corrections, Stripe payments; English only. The listing does not mention two-side confirmation. | https://apps.apple.com/kr/app/id6760804767 |
| **Gap: OpenSports** | Drop-in organizers get RSVP limits, an automatic waitlist, payments and level filters. Waitlists are table stakes, and the payer is the drop-in organizer, not friends. | https://apps.apple.com/app/id1056940981 |
| **Gap: TeamChooser** | Long-running team-balancing utility based on manual ratings. | https://apps.apple.com/app/id369608062 |
| **Gap: rating method** | Team-mean Elo (K=24, win/loss) was fixed without comparing alternatives. OpenSkill (MIT, Weng-Lin) handles asymmetric multi-team games and carries uncertainty, which matters for "trustworthy" ratings in rotating 3v3. | https://pypi.org/project/openskill/ |
| Problem intensity and reuse | **Unobserved.** No real session, participant or reuse row; the R006 follow-up is blank. | `docs/pilot/observation_packet.json` |
| Payer | None identified. Drop-in associations (the Green Volley-like or OpenSports segment) were never interviewed. | none |

Eight bounded web calls. No French friends-group tool with two-side-confirmed Elo was found, but every component exists for free.

## 3. Product and MVP assessment

- **Job:** after a casual outdoor game, record who played and who won so a friends group trusts a running Elo and history. A secondary job is organizing the session itself.
- **User:** the founder, as organizer of an outdoor friends group coordinated in WhatsApp (6–12 people). Paid drop-in organizers are the only plausible payer, and they are unvalidated.

**What works today (verified locally on synthetic data):**

- Private groups with hashed, revocable invites and guest seats.
- Sessions with capacity, several matches each, live duplicate-free team building and optional team names.
- Rules and score proposed, then confirmed by the opposing side. Amendments are possible after play has started.
- Exactly-once chronological Elo replay, with a player history chart and table.
- Public sessions with discovery, waitlist, Elo-range auto-admission and creator review. Standalone matches with per-seat links.
- Export and deletion, backup and restore, PostgreSQL support, and an upgrade path from 0.1.1. The mobile layout is clean at 390 px (screenshots inspected).

**What is missing:**

- **Any real use.**
- A low-friction path for a WhatsApp group. Ratings require every player to register and claim a seat, and the other side to confirm. A guest-slot match is never rated (`services/ratings.py` `players()` returns None for unclaimed guests). The cheapest trial, where the organizer records results on one phone, therefore produces no Elo.
- A way to post results back into WhatsApp.
- An explanation of the formula.
- Hosting. It is gated and the R006 answer is blank.

**Verdict: NARROW.** The build is done and solid; more features would be speculative.

- Narrow to the private-group recorder plus Elo, which serves the founder's own group.
- Freeze public discovery, admission and standalone work until reuse is observed.
- Treat it as a personal/community tool: revenue and moat are weak against free Spond, WhatsApp Events, VolleySmart and Spiker Pro.
- STOP is not warranted: build cost is sunk, founder fit is real and validation is cheap.

**Single most important next validation gate:** at two consecutive real outings of the founder's group, results are recorded within ~1 minute per match and shared to WhatsApp. At least half the players look at, or ask about, the standings without prompting, and the group asks to continue at the third outing. If this fails, mark the venture "use existing" (WhatsApp Events plus a spreadsheet, or Spond).

## 4. Scores

Formula as stored: positives are raw × weight × 10; penalties are (raw − 1) × weight × 10.

| Criterion | Stored | Proposed | Rationale |
|---|---|---|---|
| Revenue potential | 5 | **3** | Friends groups will not pay; free incumbents cover every component; payer unidentified. |
| Profitability ease | 4 | **3** | Hosting is cheap but there is no revenue path; drop-in payments are already served by OpenSports. |
| MVP speed | 8 | **9** | The MVP is built, CI-green and upgradeable. |
| Founder fit | 8 | **8** | Plays volleyball, organizes the group, ML/rating competence. |
| Go-to-market ease | 4 | **3** | Each WhatsApp group must be converted whole; no channel beyond the founder's group. |
| Moat | 4 | **2** | Elo and confirmation are easily copied; nothing proprietary beyond the group's own history. |
| Problem intensity | 6 | **4** | The coordination pain is covered by WhatsApp Events; ranking is a nice-to-have; pain unobserved. |
| Retention | 7 | **5** | Weekly cadence if adopted; outdoor play is seasonal; untested. |
| Legal/ethical risk (penalty) | 3 | **3** | GDPR personal data and public venue/time listings; mitigated by design, and moderation is needed before hosting. |
| Capital intensity (penalty) | 2 | **2** | Small VPS or managed PostgreSQL. |
| Network dependency (penalty) | 8 | **8** | Ratings need the whole group registered and confirming. |
| Competition intensity (penalty) | 10 | **8** | Crowded, but no French friends-group tool with confirmed Elo was found. |

The proposed total is **≈ 37 / 100** (positives 45.9 − penalties 8.9). **Lower** it from 47. Confidence is **low to medium**: competition was checked this pass, but demand has not been observed at all.

## 5. Code audit

**Checks I ran on 2026-10-09, all against local `2679b75`:**

| Command | Result |
|---|---|
| `make check` | Ruff passed, mypy strict clean (28 files), **89 passed** in 61 s |
| `VOLLEY_PG_BIN=/usr/lib/postgresql/16/bin uv run python scripts/test_postgres.py` | **89 passed**, pg_dump/restore PASS |
| `VOLLEY_BROWSER_EXECUTABLE="" uv run python tests/browser/replay.py`, run 1 | **FAIL**: "Local synthetic server did not start" when the server restarted (load average about 5.5) |
| Same command, run 2 | PASS at 1280 and 390 |
| `tests/browser/v08.py`, `v09.py`, `v10.py` | PASS at 1280 and 390 |
| Manual loopback probe (port 8137, scratch database) | `/health`, `/login`, `/discover` return 200; `/` returns 303 to login; 8 bad logins return 401, then 429; a POST without CSRF returns 403. Server stopped afterwards. |

Not run locally: `make upgrade-rehearsal`, `scripts/smoke_release.py`, `organizer_rehearsal.py` (CI runs them).

**CI:** `.github/workflows/checks.yml` has three jobs: core and release (including the upgrade rehearsal), Chromium (all browser suites) and PostgreSQL 16. Actions are pinned by SHA, permissions are `contents: read`, and the install uses `uv sync --locked`. This is sound.

**Findings**

| Sev | Finding | Path |
|---|---|---|
| Medium | The browser harness gives the server 10 s to start and discards its stderr, so the restart failure I saw (1 of 2 runs, under load) cannot be diagnosed. | `tests/browser/replay.py` `start_server` (lines 28–55) |
| Medium | **Product and trust model:** an unclaimed guest is never rated, and confirmation needs an account on the opposing side. The cheapest real trial (one organizer device) cannot produce Elo. | `src/volley_match/services/ratings.py` `players()` |
| Medium | Jinja templates and CSS are hand-minified: 50 lines exceed 400 characters, and `match.html` is 8 KB in 38 lines. Diffs are unreviewable and there is no template lint. | `src/volley_match/templates/*.html`, `static/app.css` |
| Medium (scope) | The V10 admission state machine is the largest service. It was built before any private use and adds a public surface needing moderation. It was user-authorized, but it is a complexity cost to freeze. | `services/admission.py` (544 lines) |
| Low | Rating transparency is partial. The UI states 1000, provisional for 10 matches and "estimation locale". It does not state K=24, team-mean expectation, or that win/loss is used and the margin ignored, and match pages show deltas without an expected probability. | `templates/match.html`, `player.html`, `group.html` |
| Low | Every confirmation writes a new `RatingRun` that copies all events, so rows grow about quadratically with matches. `table()` and `history()` issue N+1 queries. Fine at friends scale. | `services/ratings.py` |
| Low | The rate limiter is in-process and keyed on client IP; uvicorn runs without proxy headers, so behind a reverse proxy all users share one bucket. There is no password reset. Both are documented. | `services/limits.py`, `docs/RELEASE.md:163,165,226` |
| Low | The unauthenticated `/discover` page lists venue and time of public sessions; moderation and privacy review are needed before hosting (documented). | `api/ui.py`, `templates/discover.html` |
| Low | French only (`lang="fr"`, strings inline, no i18n layer). Acceptable for the target group. | templates |
| Info | Dates are formatted inconsistently (ISO `2026-10-09` on the player page vs `09/10/2026` elsewhere), and the raw "EUROPE/PARIS" zone name is shown. | `player.html`, `home.html` |
| Info | The seed guard's message does not say that "development" must appear in the database URL. | `scripts/seed_demo.py:17` |

**Positives:** Argon2 and hashed session/invite tokens; signed CSRF, strict CSP, TrustedHost; production config validator; 7 Alembic migrations with CI upgrade/rollback rehearsal; deterministic release manifest; accessible forms (labels, `role=alert`, `aria-live`, 200% zoom tested); no Foundry runtime import.

Test depth matches the MVP promise end to end: invite, join, record, confirm, history and Elo all have service tests and a browser journey.

## 6. Proposed work packages (priority order)

| ID | Title | Size | Effort | Depends on |
|---|---|---|---|---|
| VM-R1 | Foundry record hygiene | S | low | none |
| VM-R2 | Reconcile local checkout with remote main | S | low | none |
| VM-R3 | Share standings and results to WhatsApp | S | medium | VM-R2 |
| VM-R4 | Rating rule transparency | S | medium | VM-R2 |
| VM-R5 | Browser harness diagnosability | S | low | VM-R2 |
| VM-R6 | Real two-outing pilot gate (human) | M | medium | VM-R3 |
| VM-R7 | Organizer-attested rating option (conditional) | M | high | VM-R6 |
| VM-R8 | Template de-minification and date consistency | M | low | VM-R2 |

Details and acceptance for each package are in the JSON block below. Explicitly *not* proposed: more public discovery features, tournaments, payments or matchmaking until VM-R6 passes.

## 7. Delivery state

- **Remote.** `git@github.com:Jonathan2021/volley-match.git`, private. Local `main` = `2679b75`. **`origin/main` = `991d702`**: PR #1 "Cleanup and CI refresh (2026-10-09)", merged 2026-10-09T12:12Z, "scheduled maintenance pass, unattended". The PR body reports 43 added tests and merged duplicate helpers; I did not verify that locally. Foundry has no record of this change.
- **Last CI run.** `37928573496` on `991d702`: **success** (core-and-release, postgres, chromium). The previous run on `main`, `37848352127` on `2679b75`, was also a success.
- **Dirty files (listed, untouched).**
  - Untracked: `remarks` (the user's note).
  - Ignored: `.foundry/`, `.local/` (including `volley-development.db`), `dist/`, `.venv/`, caches, and raw `docs/evidence/*`.
- **Files this review added (all ignored or outbox files, none tracked):**
  - `docs/evidence/review-20261009-*` screenshots, from the browser runs.
  - `.foundry/feedback-input-review-{1,2,3}.json`.
  - `feedback/{fe29bb87…,0a88acc7…,00123a17…}.json`, plus their `.receipt.json` files.

## 8. Foundry friction filed

| UUID | Kind | Evidence ID | Summary |
|---|---|---|---|
| `fe29bb87-9456-471e-9206-136e9926c188` | bug | `f4b438fa-fe90-433f-86f6-e86c89d7f837` | Fusion proposal stays "proposed" and is shown as current focus despite decision a38e9141 and revision drift (3 → 17); no staleness or supersede signal. |
| `0a88acc7-acec-4b17-985a-79f3855a3024` | friction | `94e6a84f-3d01-4b84-b7e0-9b3769606e05` | Header "Discovery" vs review solution_validation; maturity "Concept" after release; stale score not surfaced; two "sequence 1" score rows. |
| `00123a17-e956-4fe4-9011-fc7eb93769e6` | idea | `04d78c36-2979-4937-bf85-d4d56be47bbb` | Detect repository drift (recorded SHA vs HEAD and remote main). Also: `cli --help` is not passed through, and `--venture-id` vs `--workspace-id` is inconsistent across list and show commands. |

Positive: `resume` and `agent resume --format json` gave the complete result chain with receipts in one call, and feedback delivery returned receipts immediately.

```json
{
  "venture": "v-sports-session",
  "recommendation": "NARROW",
  "scores": {"revenue": 3, "profitability": 3, "mvp_speed": 9, "founder_fit": 8, "go_to_market": 3, "moat": 2, "problem": 4, "retention": 5, "legal_risk": 3, "capital": 2, "network": 8, "competition": 8},
  "confidence": "low-medium: competition re-checked 2026-10-09 (8 bounded web calls); demand, reuse and payer entirely unobserved; computed total about 37 vs stored 47",
  "score_change": "lower",
  "packages": [
    {"id": "VM-R1", "title": "Foundry record hygiene", "description": "Coordinator/human: resolve proposal 91fe8686 as superseded by decision a38e9141; mark v-sports-ranking dropped/merged lineage pointing to v-sports-session with P023 tournament/sponsor ideas as deferred hypotheses; set v-sports-session maturity to mvp; append reviewed score about 37; record PR #1 / 991d702 as an external change.", "acceptance": "proposal list shows no pending sports proposal; both venture pages show no 'Review fusion proposal'; v-sports-session shows the reviewed score and mvp maturity; an evidence item cites 991d702 and CI 37928573496.", "size": "S", "effort": "low", "depends_on": []},
    {"id": "VM-R2", "title": "Reconcile local checkout with remote main", "description": "Fast-forward the canonical folder from 2679b75 to origin/main 991d702 (preserving untracked remarks), rerun make check and the browser suite, and record the exact result.", "acceptance": "HEAD == origin/main; make check and make test-browser-all pass locally on 991d702 with counts recorded in Foundry.", "size": "S", "effort": "low", "depends_on": []},
    {"id": "VM-R3", "title": "Share standings and results to WhatsApp", "description": "On group and session pages, add a 'Copier pour WhatsApp' action producing plain text (matches, scores, confirmation state, Elo table with provisional marks, link) so the group stays in WhatsApp.", "acceptance": "Service test renders deterministic text for a seeded session; browser test copies to clipboard at 390 px; no new account, send or external call.", "size": "S", "effort": "medium", "depends_on": ["VM-R2"]},
    {"id": "VM-R4", "title": "Rating rule transparency", "description": "Add a 'Comment est calculé l'Elo' page (1000 start, K=24, team mean, win/loss only, margin ignored, provisional under 10, per-group/format pool, replay on correction) and show the pre-match expected win probability next to each delta.", "acceptance": "Template test asserts rule text and expected percentage; a 3v3 equal-mean match shows 50% and +12/-12; linked from group, player and match pages.", "size": "S", "effort": "medium", "depends_on": ["VM-R2"]},
    {"id": "VM-R5", "title": "Browser harness diagnosability", "description": "Make server start timeout configurable (default 30 s), write server stdout/stderr to a per-run log under .local and print its tail on failure, shared across replay/v08/v09/v10/organizer scripts.", "acceptance": "A forced start failure prints the server log tail; three consecutive make test-browser-all runs pass locally; CI green.", "size": "S", "effort": "low", "depends_on": ["VM-R2"]},
    {"id": "VM-R6", "title": "Real two-outing pilot gate (human)", "description": "User answers the R006 follow-up (organizer, access arrangement, consent/retention owner, spending cap); agent then prepares the exact deployment/invite payload for separate approval and records outcomes in docs/pilot/observation_packet.json.", "acceptance": "Two real outings observed: per-match entry time, confirmation completion, unprompted standings views/requests, and stated wish to continue; GO-continue or use-existing decision recorded in Foundry.", "size": "M", "effort": "medium", "depends_on": ["VM-R3"]},
    {"id": "VM-R7", "title": "Organizer-attested rating option (conditional)", "description": "Only if VM-R6 shows account claiming blocks use: per private group opt-in where organizer attestation rates guest-slot matches provisionally, with dispute after claim triggering replay; ADR on the trust-model change.", "acceptance": "ADR accepted by user; service tests for attest, claim, dispute, replay exactly once; one-device browser journey from session to Elo table for six guests.", "size": "M", "effort": "high", "depends_on": ["VM-R6"]},
    {"id": "VM-R8", "title": "Template de-minification and date consistency", "description": "Reformat minified Jinja templates and app.css into reviewable multi-line form without behavior change; unify date display (dd/mm/yyyy HH:MM local) and humanize the timezone label.", "acceptance": "No line over 160 chars in templates/CSS; rendered HTML of seeded pages unchanged except dates; all unit, integration and browser suites pass.", "size": "M", "effort": "low", "depends_on": ["VM-R2"]}
  ],
  "feedback_ids": ["fe29bb87-9456-471e-9206-136e9926c188", "0a88acc7-acec-4b17-985a-79f3855a3024", "00123a17-e956-4fe4-9011-fc7eb93769e6"],
  "blockers": [
    "R006 follow-up (foundry/requests/2026-10-07-volley-match-R006-pilot-access.md) unanswered: no willing organizer, access arrangement, consent owner or spending cap recorded; hosting and invitations remain unauthorized",
    "Local checkout 2679b75 is behind origin/main 991d702 (unattended PR #1) with no Foundry record",
    "Fusion proposal 91fe8686 and venture v-sports-ranking need a human/coordinator resolution"
  ]
}
```
