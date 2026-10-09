# Coopain delivery: 2026-10-09

Implementer: `implementer-coopain-20261009`. Venture `v-coopain`, workspace
`9197a72d-23a6-424d-9b00-03e5d4a366f6`, repository `/home/jonathan/startup_lab/coopain`
(GitHub `Jonathan2021/coopain`). Start: `fc5b92b` (= origin/main). Venture remains on HOLD.

## Packages completed

| Package | Work id | Result id (accepted) | Decision | Commits | Actions run (exact SHA) |
| --- | --- | --- | --- | --- | --- |
| C02 Policy and competition desk pack + record hygiene | `87c6f8d6-09b1-4155-8fb0-58b4a3b452e7` | `227c36d5-a23a-546c-9eb0-327259836fa8` | `cdfaea3a-202e-455e-acab-a0f7622e809f` | `78f35af` | `37969597406` on `78f35af`: success |
| C03 Profile stale-load race | `badd9a7c-ca63-442b-a4c2-9449daee1afa` | `60695e0f-3810-5b7a-ab2d-b452ab9ea858` | `a1b9197f-294c-497d-b1e2-ebcf46830a01` | `2588d6b` | `37975495446` on `2588d6b`: success |
| C04 Whole-repo quality gates and enums | `a2c4cfa8-8179-476a-8204-970daeceebeb` | `40feade1-e3f2-54d7-83ae-2ec206152bed` | `05b75a1b-515e-44a8-bd52-df97b55d549c` | `9a2f7b1`, `3c6cf45`, `3135903` | `37980110728` on `3135903`: success |
| C05 Fail-closed configuration and a11y basics | `5212b3b5-9ec4-4e93-88d7-c2d60ff3e822` | `6721053b-7c3c-5f04-93f2-bb352176540e` | `b409d835-3e0f-4d5d-8796-d8c34b3238da` | `20a0634`, `b0c1cd0`, `bfa739b` | `37983853750` on `bfa739b`: success (`37983779070` on `b0c1cd0` was cancelled by the workflow's concurrency group) |

All results used `coverage_action: accept_limitation` (all arrivals paged; none bore on the package).

### C02
- `docs/mvp/REFERRER_POLICY_DESK_PACK.md`: eight published French cooptation agreements
  (Bourg Frères, T3M Lavail, T3M Blanc Rochebois, Transdev Normandie Manche, Harmonie
  Medical Service, Vocaza, Héli-Union, Kermeleuc Distribution). None explicitly requires
  knowing the candidate. Seven of the eight require the relationship to be stated or
  presuppose one. Six exclude candidates "already presented by a third party", and two
  restrict referrals to a closed list of relationships. The desk verdict for R015 is
  "not decided". The pack has a dated comparator table: Basile by Hellowork, Keycoopt,
  Coop-Time (its domain did not resolve on 2026-10-09), BeCoopt, Linkeys, MyJob.Company,
  Blind/Glassdoor and Refer.me. Vendor claims are labelled. It used 9 web searches.
- `docs/mvp/INTERVIEW_GUIDE.md`: five conversations in FR and EN, the R015 pass/stop
  rule and a recording sheet kept outside Git. Nothing was sent.
- Record hygiene:
  - Evidence `f0e42852-7896-476d-9071-4647c9835f13` records PR #3: `fc5b92b`, run
    `37928455952`. The run log shows **267** backend tests at **92.82%** and **19** web
    tests. The 250/14 figures in the brief belong to the older commit `f3a8c13`.
  - Map `88ff9788` removes the J01–J05 duplicate "alternative" placeholder nodes, adds
    the question node `policy` ("Do French employer referral policies allow platform
    strangers?") and sets the focus to it.
  - `285e380e` was cancelled ("superseded by the 2026-10-07 scope and the 2026-10-09
    HOLD review").
  - `90e268be` was kept; its title and description now point at R015.
  - Assessment `617f1e15` marks assumption `51ab9986` inconclusive.
  - `resume` now lists only `90e268be` and has no `needs_review` entries.

### C03
- Root causes, from the API logs and Playwright call logs:
  - Profile: a `GET /referrer/jobs` that started before "Save my employment" resolved
    after it and replaced the saved list.
  - Matches: the selection effect reset the review form on every re-run, which made
    "Accept request" disabled. This is the same class of bug, observed in a local
    failure.
- Fix, in code: `src/app/lib/load-guard.ts` gives each load a ticket ordered against
  writes. A superseded load is ignored. A load overtaken by a write is merged by id.
  Forms reset only on a real selection change, and profile fields hydrate once per user.
- Tests: 8 deterministic node tests. 6 of them fail against the old behaviour.
- The verifier's readiness wait went from 90 s to 240 s, because a cold `next dev`
  compile of `/register` took longer than 90 s under load.
- Verifier runs:
  - Before the fix: 2 runs, with 1 readiness timeout and 1 desktop failure.
  - After the fix: runs 1–5 gave 1 readiness timeout and 4 passes.
  - After the readiness change: 5 consecutive passes, each with desktop + 390px and
    the launcher recovery checks.

### C04
- Lint and formatting:
  - Ruff check and format now cover all of `backend` and `tools`. The vendored
    `tools/foundry_agent.py` is excluded and its hash is unchanged.
  - 503 autofixes, 101 files reformatted and 4 manual fixes.
  - Ruff's unused-import autofix had dropped public re-exports and a side-effect model
    import. The suite caught it (21 failed, 45 errors) and both were restored before
    the commit.
- Types:
  - mypy covers `backend/app`, `backend/scripts` and the verifier. The five previously
    strict modules keep strict overrides; I checked that the overrides still apply.
  - 10 mypy errors were fixed, plus 3 export errors exposed by the strict overrides.
  - No baseline or allowlist was needed.
- CI also runs mobile and design-system lint and design-system tsc.
- Enums: `IntroductionState` and the named state groups (backend), and `USER_MODES` /
  `INTRODUCTION_STATES` (web), replace 34 backend and 39 web hard-coded comparisons.
  Guard tests are `backend/tests/test_enum_literals.py` and
  `apps/web/tests/constants.test.mjs`. The OpenAPI file is byte-identical.
- Backend: 271 passed. Web: 31/31.

### C05
- Fail-closed configuration:
  - The backend refuses to start without `ENVIRONMENT`, without `JWT_SECRET_KEY`, or
    with a placeholder secret (`change-me`). Only `ENVIRONMENT=test` is exempt.
  - Outside dev/test it also requires an explicit `DATABASE_URL`.
  - Configuration errors no longer echo their inputs (`hide_input_in_errors`).
  - 10 tests.
- `<html lang>` follows the FR/EN toggle, and the e2e asserts it.
- Accessibility checks:
  - axe (`@axe-core/playwright` 4.13.0, WCAG 2.1 A/AA) found 0 violations on profile,
    dashboard and matches at 1280px and 390px. It now fails the suite on any serious
    or critical finding.
  - A keyboard Tab-stop check runs on the profile page.
  - axe could not decide colour contrast over the gradient background. I computed it
    from the theme tokens: success, warning, eyebrow and others were below 4.5:1, so
    those tokens were darkened. `tests/contrast.test.mjs` now pins both themes.
  - The pnpm audit snapshot was refreshed for the dev-only lock entries; the advisories
    are the same.
- Backend: 281 passed at 92.87%. Web: 34/34.

## Error and remediation (C04)

My `git add backend` in commit `9a2f7b1` staged and pushed five of the pre-existing
untracked operator files:
- `backend/preprompt`
- `backend/tmp_prompt`
- `backend/openapi_new.yaml`
- `backend/test_results`
- `backend/generated/refactor_scan_20260311.md`

I reviewed them and found no credentials. Commit `bfa739b` untracks them again; the files
stay on disk and all eight operator files are untracked, as at the start. They remain in
history at `9a2f7b1`. Removing them would need a history rewrite or force-push, which is
not authorised. **Human decision needed** if they must be purged from history.

The `feedback/` outbox files are git-ignored in this repository. Following the brief, I
force-added only my own four reports and their receipts.

## Intentionally not done
- **C06** (single source for the transition and password rules) is deferred and not
  scheduled. The web transition table in `apps/web/src/app/lib/introduction.ts` still
  duplicates the backend.
- Legacy dev paths were not removed: Dockerfile/compose, conda scripts,
  `terminal_frontend`/`browser_frontend`, `dev_ui.py`, `fingerprints.py`. Removing them
  is a product decision. Docker/compose now need an explicit secret; this is documented.
- Also not done:
  - Docs archive and renaming `README` to `.md`.
  - Deleting the stray root files (needs a human).
  - Strict mypy over all of `app`.
  - mypy on the tests.
  - Mobile runtime or palette changes.
- Coordinator-level C01 items were not done: score reassessment, and new assumption
  records for policy permission and referrer willingness. The result contract can only
  assess existing assumptions.

## Remaining human gates
- **R015 / work `90e268be`**: five employee conversations using
  `docs/mvp/INTERVIEW_GUIDE.md`, with the pass/stop rule as written.
- Launch gates R1–R4 (rights, licence, operator) and P1–P8 (controller and privacy) are
  still UNKNOWN.
- Purging the five operator files from history (see above) is optional.

## Feedback filed (all `recorded_for_review`)

| UUID | Kind | Topic |
| --- | --- | --- |
| `aa783af4-f328-472b-9cb3-bfa82ad304e8` | friction | A map revise flags the claimant's own work as needing review and invalidates its saved context; WorkTreatment cannot revise question/acceptance criteria. |
| `4e56b8a0-c4d7-45f6-91d7-e979a5963e43` | friction | Accepted findings reappear as unclassified arrivals in the next package's context. |
| `2a942fae-b311-4755-a2dc-26ab5f30afb5` | positive | The claim → preview → resolve flow; suggests printing the context id first. |
| `75fa972d-7e47-41a2-a94a-d485681ed244` | friction | CLI log lines interleave with the JSON output when stderr is merged. |

## Final state
- `git log -1`: `bfa739b9f9ec5edefa314916400a07513e348509 chore: untrack operator notes committed by mistake in 9a2f7b1`
- `origin/main`: `bfa739b9f9ec5edefa314916400a07513e348509` (CI `37983853750` success)
- Working tree: no tracked changes. The eight operator files are untracked, as at the
  start.
