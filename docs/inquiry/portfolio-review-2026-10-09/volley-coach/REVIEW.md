# Volley Coach — portfolio review 2026-10-09

Reviewer: `reviewer-volley-coach-20261009` (read-only; no claims, results or resolutions).
Venture `v-volley-coach`, workspace `9d0ed0f5-960b-4cd0-a52f-4176218a40e5`, repository
`/home/jonathan/startup_lab/volley-coach` (local `main` 28f611c, v0.1.1).

## 1. Foundry record audit

**What is recorded (exact IDs).**

- Current review rev 10 `8e06a775-4052-44f4-b96f-cee216c7f797`: pursue, solution_validation, concept, decision `86bc7d9c-974e-42ae-b06c-95d2f4d12f76`. Next action: hold at R006, no ready package (`next_work_item_id` null).
- Map revision 11 `204f0876-15b4-5b20-94e3-784e8af90f4b`, 13 nodes and 12 edges.
- 9 work items. Done: `9afdbf73` (MVP boundary), C01 `7172fb29`, C02 `e44f23f7`, C03 `69023928`, C04 `4f34d7aa`, C05 `fe479aa6`, C06 `9fb8b808`, C07 `71764075`. Blocked: `da9f64ff-1b76-5e2d-bdce-537234f19324` "Initial manual review".
- 16 evidence records. Only 2 concern the market or scope (`0b30d194` scope, `5e88b3a5` competitor note). The other 14 are engineering or Foundry-procedure results. There are **zero** customer-conversation or operating-metric records.
- 8 accepted decisions: `ddf723c3` (GO planner) and `791a2a4a`…`86bc7d9c` (C01–C07 checkpoints).
- Score: `venture-score show --id v-volley-coach` returns `current:null, history:[]`, card `portfolio-reviewed-v1`, source idea `priority-volley-coach-20261007`. The console says "Not yet scored".

**Coherence and navigability.** A human can find the next action in five minutes, but only by reading past noise:

1. **The legacy item `da9f64ff` is noise.** It is blocked with `changed_context` / "Superseded as an executable priority…". Yet it is the only work item in the resume markdown and the only `needs_review` entry, and it triggers the "Some decisions need review" banner. The Work tab labels it "Manual review completed · Blocked", which contradicts itself. It should be closed as superseded by `ddf723c3`, not reviewed.
2. **The stage is inconsistent.** The header and `agent resume` `scope.stage` say *Discovery*, while the state card says *Solution validation · Concept*. Review rev 2→3 moved business_validation (hold) to solution_validation (pursue) with no demand evidence. The honest stage is discovery or business validation.
3. **The map has duplicates.** C02–C05 appear twice: once as "Question" nodes that still read "Conditional: claim only after predecessor acceptance", and again as done "Record" nodes. The node `status` is null in the JSON. The real gate, `C06_trial_gate`, is a question node. It is not a work item or a human request.
4. **The open human gate is invisible.** The console shows "No open human requests", but `foundry/requests/2026-10-08-volley-coach-R006-own-program.md` is OPEN. The ID R006 is also reused for Volley Match's separate gate.
5. **Delivery has drifted.** Foundry's last result says main is 28f611c with CI 37773032398. GitHub main is now `122968b`: PR #1 "Cleanup and CI refresh (2026-10-09)", merged 12:26Z by an unattended maintenance pass that, per its own body, wrote nothing to Foundry. Foundry and the local checkout are both one merge behind.
6. **Minor issues.** The "Current focus" text appears twice on the venture page. History rows show only the type, a UUID and the actor, with inconsistent quoting and one `null` actor. C06 and C07 have `decision_id` null, while C01–C05 point to the predecessor's decision.

## 2. Prior research gaps

| Claim (source) | Status 2026-10-09 | Evidence (URL, checked 2026-10-09) |
| --- | --- | --- |
| "The user proposed this exact choice" (DECISION.md, evidence `5e88b3a5`) | **Unverified provenance.** The user's only recorded volleyball reply (R006, 2026-10-04) is about balanced teams, fair tournaments, Elo, progression *in matches* and finding partners. That is Volley Match scope. No user statement asking for personal training scheduling is linked. | `foundry/requests/2026-10-04-followups.md` §R006 |
| Video analytics is crowded (Hudl Balltime, SwingVision) | Relevant only to the deferred direction. Not rechecked. | priority-mvps report |
| Competition for the *chosen* job (personal training plans) | **Never researched before.** Volleyball-specific subscription apps sell solo and jump programs: VolleyTrain, House of Volley (100+ workouts), Bulletproof Performance ("week-to-week plans tailored to the season"), Hopp Homie and VertMax. These are store claims and are not verified. | https://apps.apple.com/app/id6745722952, https://apps.apple.com/us/app/id6443681334, https://apps.apple.com/us/app/id6478654657, https://apps.apple.com/app/id6748640285 |
| Adjacent adaptive planners | Fitbod already does equipment profiles per location, durations from 1 min to 4 h and fatigue-aware recovery, at about $15.99/month (third-party prices conflict). Volt costs $800+/year per team with "Cortex" adaptation. TrueCoach starts at about $25.99/month for coaches. | https://fitbod.me/blog/your-gym-profile/, https://www.sensai.fit/blog/fitbod-review-2026, https://voltathletics.com/pricing, https://www.capterra.com/compare/155784-202308/truecoach-vs-TrainHeroic |
| Rescheduling around real availability is unmet | **Weakly supported, as a feature gap.** There are Trainerize feature requests and Garmin Coach complaints. Freeletics and Musclebooster push missed sessions to the next day. None found reads real availability or resources. This signals a feature inside existing tools, not a standalone product. | https://ideas.abcfitness.com/forums/940789-client-gym-members-abc-trainerize/suggestions/42348535-ability-to-restart-pause-or-push-back-workouts-or, https://forums.garmin.com/apps-software/mobile-apps-web/f/garmin-connect-web/209598/annoying-garmin-coach-rescheduling-behaviour-for-missed-workouts/1096592 |
| French market | FFvolley had 245,281 licensees on 31 Aug 2025. Most club players have club coaches and fixed club practice times, so the "own program" need is unproven. No French player-facing planner was found. | https://ressources-associations-sportives.franceolympique.com/api/media/sites/ressources_associations_sportives/files/2025-09/Fiche%20f%C3%A9d%C3%A9ration%20-%20FF%20Volley%20(2).pdf |
| Target players follow a written multi-session program | **Not researched.** This is the load-bearing assumption. | none |
| Willingness to pay | **Not researched.** | none |

## 3. Product and MVP assessment

- **Job:** fit an adult recreational player's existing training program into real weekly time, location, equipment, court and partner availability. Replan after cancellations and log outcomes.
- **User:** a self-coached adult recreational player. For now that is hypothetical: no participant is identified.
- **What works today** (verified by tests and my probe): local accounts, profile, own-program entry, slots with DST handling, deterministic constraint-respecting placement, accept, log, replan that preserves history, discomfort or illness holding progression for 14 days, export, delete, backup and restore. Security headers are present and the "own-program mode" label appears on every page.
- **What is missing or weak:**
  - **One session per goal per week.** In a probe, three free gym evenings plus a 3-session "movement" program (sessions A, B and C) produced exactly one movement session. B and A were silently dropped and `unfilled_goals` came back empty. A real program cannot be represented, and the first real trial would hit this immediately.
  - **No progression in the only usable mode.** Variants require `status=reviewed`, users can only add `user_provided` drills, and no reviewed catalog exists. The "adapt/progress" half of the promise therefore always returns `keep_program` or `held`.
  - **No phone access.** The app runs on loopback only (`TrustedHostMiddleware` allows localhost, and `serve` binds 127.0.0.1). A player cannot log from a phone at the court without hosting, so the 390px checks are emulation only.
  - **No French.** The UI and walkthrough are English-only (`lang="en"`), while Volley Match ships a French mobile UI.
- **Recommendation: HOLD.** The engineering is sound, but there is no demand evidence and the stated provenance does not match the user's recorded pain. The user put this venture "aside" on 2026-10-08 (remarks-followup report), while Volley Match received four rounds of user remarks (V08–V11). Do no more building until the gate below passes. If the gate answer is "no", move to STOP and archive.
- **Separate or merge with Volley Match:** keep the repositories separate and frozen. Do not merge code: the stacks, languages and domains differ, and ADR boundaries would blur. At the venture level, however, treat Coach as a **held candidate feature of the volleyball line led by Volley Match (`v-sports-session`)**, with no separate recruitment, request or roadmap. The two share the same users and access. If players in Volley Match groups later ask "what should I train between sessions", reopen Coach inside that pilot.
- **Most important next gate:** one operator answer, about 5 minutes. Do you, or at least two adults in your volleyball group, currently follow a written program with **two or more sessions a week** outside group play, and does fitting it into the week cause friction you would track in an app for two weeks? Yes → run the narrowed R006 trial after package P3. No → STOP.

## 4. Scores (proposed portfolio-reviewed-v1, 1–10)

| Factor | Score | Rationale |
| --- | --- | --- |
| Revenue potential | 2 | Consumer niche, and subscription apps already sell volleyball plans. A scheduler-only layer has little pricing power. |
| Profitability ease | 3 | Cheap to run, but low ARPU and the need to acquire consumers. |
| MVP speed | 7 | Built and CI-green. The multi-session fix is about M-size. |
| Founder fit | 6 | Plays volleyball and has group access, but the deterministic scheduler uses none of the founder's ML edge. |
| Go-to-market ease | 3 | Individual consumer app. Needs hosting and French; the only channel is Volley Match groups. |
| Moat | 1 | Commodity scheduling; incumbents could add it as a feature. |
| Problem intensity | 3 | The user's recorded pain is elsewhere. Rescheduling friction exists, but as a feature request. |
| Retention | 3 | Weekly use only if a program exists; adherence apps churn. |
| Legal/ethical risk (penalty) | 4 | Health-adjacent flags and physical-activity context. Own-program mode and the discomfort hold mitigate this, but any app-authored guidance needs review. |
| Capital intensity (penalty) | 1 | Local, open-source stack. |
| Network dependency (penalty) | 3 | Single-player value, though partner and court availability matter. |
| Competition intensity (penalty) | 6 | Fitbod, Volt, TrueCoach and TrainHeroic, plus 5+ volleyball training apps. |

Confidence: **low** (desk research only, no user evidence). Score change: **record** this as the first, low-confidence score so the venture stops showing as unscored next to scored siblings.

## 5. Code audit

**Checks run** on local 28f611c, Python 3.13.5, existing `.venv`:

- `make check`: exit 0. Ruff passed, strict mypy found no issues in 24 files, and pytest reported **41 passed**, 1 upstream Starlette/httpx deprecation warning, 0 skips. Took 23 s.
- `make test-browser`: exit 0, **4 passed** (Chromium), 18.7 s.
- `volley-coach migrate` plus `serve --port 8047` on a scratchpad DB: `/health` returned 200 (v0.1.1). An API probe (signup → profile → 3 programs → 4 slots → generate → accept) reproduced H1. The server was then stopped.
- CI: `.github/workflows/ci.yml` uses SHA-pinned actions, `permissions: contents: read`, uv 0.11.29 and `--locked`, and runs lint, types, core and browser tests, source and wheel verification, and a checksum manifest. `gh run list` shows the last 5 runs; the latest is **37930071447 success** (main push of PR #1), and 37771875025 failed on 2026-10-08 before the commit-boundary fix.
- Not run: the build/wheel scripts (CI covers them), and the remote main 122968b. PR #1 itself reports 71 core tests and a fixed `pytest tests` collection error; I did not verify that.

**Findings:**

| Sev | Finding | Path |
| --- | --- | --- |
| High | One session per goal per week (`filled.add(drill.goal)`). Same-goal program sessions are dropped silently, and the one chosen is picked by UUID order, not program order. `unfilled_goals` stays empty, so the user is not told. There is no `sessions_per_week` or session-sequence concept. | `src/volley_coach/services/planner.py` |
| Med | Progression cannot trigger in own-program mode: variants require `reviewed`, `add_drill` rejects anything else, and the catalog is empty. | `services/history.py` `propose`, `services/catalog.py` |
| Med | Loopback-only host allow-list, so a real trial cannot use a phone without a hosting decision. | `src/volley_coach/app.py`, `cli.py` |
| Med | English-only UI and docs for a French audience. | `templates/base.html` (`lang="en"`), `docs/pilot/WALKTHROUGH.md` |
| Low | Login skips scrypt for unknown usernames (timing-based enumeration) and has no rate limit. Acceptable for a local app; fix before any hosting. | `services/accounts.py` |
| Low | The sdist bundles `evidence/`, `feedback/` and `tools/` (flagged in PR #1). Migrations are unlinted (frozen by design). | `pyproject.toml`, `alembic/` |
| Low | Local checkout is behind remote main 122968b. Foundry and the local tree do not reflect PR #1. | repo, Foundry result `45a63c59` |
| Info | Good basics: salted scrypt; hashed 14-day tokens; HttpOnly/SameSite=Strict cookies; CSP `script-src 'none'`; same-origin write check; idempotency keys; transactional commit-before-response (ADR-0006); export and delete; `uv.lock`; strict mypy. Safety copy reads "no professional endorsement", "Rest or skip and seek appropriate professional input". The README 5-minute path works (migrate and serve verified). Test depth is strong for the scheduling invariants but has **no test for multi-session programs**. Accessibility was not audited beyond label presence. |  |

## 6. Proposed work packages (priority order)

| ID | Title | Size | Effort | Depends on |
| --- | --- | --- | --- | --- |
| VC-P1 | Foundry record hygiene | S | low | none |
| VC-P2 | Operator demand gate (replace R006 own-program form) | S | low | none |
| VC-P3 | Multi-session program scheduling | M | medium | VC-P2 = yes |
| VC-P4 | Sync local checkout to remote main and re-verify | S | low | none |
| VC-P5 | French UI and private phone access for a trial | M | medium | VC-P3, operator hosting approval |
| VC-P6 | Venture-level consolidation under Volley Match | S | low | VC-P2 |

- **VC-P1:** close `da9f64ff` as superseded by `ddf723c3`, set the stage to discovery or business validation, record the §4 score at low confidence, link the R006 request to the venture, and record PR #1 / run 37930071447 as delivery evidence. Acceptance: resume shows no needs_review, the header and state agree, the score is visible, and the request is listed.
- **VC-P2:** ask the five-minute question in §3. Acceptance: a dated yes/no with a count of adults who follow a written program of two or more sessions a week, recorded as customer-conversation evidence.
- **VC-P3:** add sessions-per-week and ordered sessions per program, and report every unscheduled session explicitly. Acceptance: red tests first; a 3-session program with 3 feasible slots yields 3 ordered sessions; with 2 slots it yields 2 plus an explicit "1 session unscheduled"; existing invariants stay green.
- **VC-P4:** fast-forward local `main` to `122968b` with no local changes lost, then run `make check` and `make test-browser`. Acceptance: HEAD equals origin/main and the reported test counts match PR #1.
- **VC-P5:** FR locale for the templates and walkthrough, plus an opt-in LAN bind with an allowed-host setting and login throttling. Acceptance: browser flows pass in FR at 390px, and the LAN mode is off by default and documented.
- **VC-P6:** record that Coach is held as a candidate Volley Match feature, so the two have one shared participant gate and no duplicate R006 lineage. Acceptance: a decision is recorded in both ventures and the INBOX shows one volleyball gate.

## 7. Delivery state

- Remote: private `Jonathan2021/volley-coach`. Remote `main` = `122968bed8fb56cfcd0c32d33eab81a5b8ccb690` (PR #1 merged 2026-10-09T12:26:44Z). The last CI run, **37930071447**, concluded **success**.
- Local `main` = `28f611c` and `origin/main` (not fetched) = `28f611c`. I did not fetch, pull or edit anything.
- Tracked files were clean before and after the review. My only additions are the 8 untracked `feedback/<UUID>.json` and `.receipt.json` files written by the feedback helper, plus ignored `.foundry/feedback-input-{1..4}.json`.

## 8. Foundry feedback filed

All four were delivered with status `recorded_for_review`:

- `255b15be-79af-42c9-b0a1-0494633be01e` (friction): the superseded legacy item stays blocked and dominates resume.
- `a5a1a905-7814-4f3a-978c-0c0417392aee` (friction): inconsistent `--id`, `--venture-id` and `--workspace-id` selectors.
- `5bed744e-44dd-4afc-8c34-c67e3f621871` (bug): stage and maturity disagree across surfaces, duplicate stale map nodes, untitled history rows.
- `63d588ac-aa86-43e5-97c7-17d0c4adb56e` (idea): no repository/remote drift view, and the open R006 request is invisible.

```json
{"venture":"v-volley-coach","recommendation":"HOLD","scores":{"revenue":2,"profitability":3,"mvp_speed":7,"founder_fit":6,"go_to_market":3,"moat":1,"problem":3,"retention":3,"legal_risk":4,"capital":1,"network":3,"competition":6},"confidence":"low","score_change":"record","packages":[{"id":"VC-P1","title":"Foundry record hygiene","description":"Close da9f64ff as superseded by ddf723c3; align stage to discovery/business validation; record low-confidence score; link R006 request; record PR #1/run 37930071447 delivery evidence.","acceptance":"Resume has no needs_review; header and state stage agree; score visible; open request listed.","size":"S","effort":"low","depends_on":[]},{"id":"VC-P2","title":"Operator demand gate","description":"Replace R006 own-program form with a five-minute question: do the operator or 2+ group adults follow a written 2+/week program and want to track it for two weeks.","acceptance":"Dated yes/no plus count recorded as customer-conversation evidence.","size":"S","effort":"low","depends_on":[]},{"id":"VC-P3","title":"Multi-session program scheduling","description":"Add sessions-per-week and ordered sessions per program; report every unscheduled session explicitly.","acceptance":"Red tests first; 3-session program with 3 feasible slots yields 3 ordered sessions, with 2 slots yields 2 plus explicit unscheduled notice; existing invariants green.","size":"M","effort":"medium","depends_on":["VC-P2"]},{"id":"VC-P4","title":"Sync local checkout to remote main","description":"Fast-forward local main to 122968b without losing local changes and re-run make check and make test-browser.","acceptance":"HEAD equals origin/main; reported test counts match PR #1.","size":"S","effort":"low","depends_on":[]},{"id":"VC-P5","title":"French UI and private phone access","description":"FR locale for templates and walkthrough; opt-in LAN bind with configurable allowed hosts and login throttling.","acceptance":"Browser flows pass in FR at 390px; LAN mode off by default and documented.","size":"M","effort":"medium","depends_on":["VC-P3"]},{"id":"VC-P6","title":"Consolidate under Volley Match","description":"Record Coach as a held candidate feature of the Volley Match line with one shared participant gate.","acceptance":"Decision recorded in both ventures; INBOX shows one volleyball gate.","size":"S","effort":"low","depends_on":["VC-P2"]}],"feedback_ids":["255b15be-79af-42c9-b0a1-0494633be01e","a5a1a905-7814-4f3a-978c-0c0417392aee","5bed744e-44dd-4afc-8c34-c67e3f621871","63d588ac-aa86-43e5-97c7-17d0c4adb56e"],"blockers":["No demand evidence; R006 own-program operator decision unanswered","Planner schedules at most one session per goal per week, so real multi-session programs cannot be trialled","Local-only loopback access and English-only UI block a realistic French phone-based trial","Foundry and local checkout lag remote main 122968b (PR #1)"]}
```
