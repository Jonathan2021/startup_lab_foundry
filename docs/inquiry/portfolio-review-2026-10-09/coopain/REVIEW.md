# Coopain portfolio review: 2026-10-09

Reviewer: `reviewer-coopain-20261009`. Venture `v-coopain`, workspace `9197a72d-23a6-424d-9b00-03e5d4a366f6`.
Audited source: local `/home/jonathan/startup_lab/coopain` at `f3a8c13` (main as recorded in Foundry). GitHub main is now `fc5b92b` (see §7). Nothing was claimed, resolved, edited or committed.

## 1. Foundry record audit

**What a human can see quickly.** `resume` and `/ventures/v-coopain` show the purpose (a candidate reaches a role through a consenting employee, chooses what to share, and tracks the introduction), the J01–J06 history (all Done), and the decision map `7ee3edb6-0331-5f82-a47f-a8d1013660c8` (goal → research → pilot question → expand/revise). That is clear in under five minutes. Not clear: what to do next, how good the venture is, and what stage it is in.

| Item | ID | Assessment |
| --- | --- | --- |
| Current review | `8a15f7c4-9f23-4745-a788-3c2f936e976d` rev 14, disposition `pursue`, stage `solution_validation`, maturity `prototype`, `work_state not_scheduled`, `next_work_item_id null` | **Stale.** `next_action` points to `/home/jonathan/startup_lab/coopain-readiness-20261008`, the old checkout. The canonical repo was reconciled later (evidence `e493b63e`), but `next_action` was never updated. The console shows this text twice as "Current focus". It is a run-the-app instruction, not a decision. |
| Latest decision | `d125fa87-a10e-428e-8d32-7e4801c4b466` (continue) | This is a CI/release record. The rationale text runs words and numbers together ("runner250 passed", "Actions37791874356"), which makes it hard to read. |
| Scope decision | `6d564adb-b5a8-4ff9-b79a-90ba44630989` (narrow, 2026-10-07) | Clear: candidates are free, with no bonus custody and no scraping. |
| Score | `a4be0de7-b411-4460-8b5b-4d48006e10bd`, 48.0, low confidence, `scope_stale=true`, `reassessment_suggested=true` | **Stale.** It scores the original "Referral-Bonus Job Network / scraped job offers" concept. Eleven of twelve rationales say "carried … not independently revalidated", and every `evidence_ids` is empty. |
| Lifecycle | Header says "v-coopain · Discovery" | Conflicts with the review's `solution_validation/prototype`. Two stage concepts are shown without labels. |
| Blocked legacy work | `285e380e-96b9-4d14-b62b-26684b5e5f71` (blocked, changed_context, needs review), `90e268be-e214-59bc-a2da-fe8c7a63a7b5` (blocked, human_input) | Both have been superseded by J01–J06, but they still show under "Resume work" as the only open items. They should be closed or explicitly kept as the human gate. |
| Assumptions | Only `51ab9986-22c7-5629-8c9f-0da478cc88e5` ("employer will use/pay for a niche candidate-free introduction"), open since 2026-10-04, with no linked test | There are no assumptions for referrer willingness, employer-policy permission or candidate demand. |
| Evidence | 19 records | 15 of 19 are engineering/delivery records. None records demand. 3 are unreviewed (`e493b63e`, `a40f2cf5`, `62eb7eb6`). |
| Map | `7ee3edb6…` | J01–J05 appear twice, once as "alternative" plan nodes and once as `work_` record nodes. The `pilot` question node has no linked work. |
| Missing | — | GitHub PR #3 (main `fc5b92b`, Actions `37928455952`) is not recorded. There is no work item for score reassessment or for the demand gate. |

## 2. Prior research gaps

| Claim (source) | Status | Source, checked 2026-10-09 |
| --- | --- | --- |
| Competition = Refer.me + Hellowork cooptation (SOURCES.md, 2026-10-07) | **Incomplete.** Two comparators are listed with no feature or pricing detail. | — |
| Refer.me is a direct comparator | Confirmed. Vendor claims: "1,300+ active referrers", "14,200 referrals delivered", candidate "Membership" for unlimited referrals, US tech focus, no mention of France. Charging candidates is excluded in France under the cited L5321-3. | https://refer.me/ |
| Hellowork cooptation | Now **Basile by Hellowork**: employer-paid internal programmes, employee referrers only, ATS/SIRH integration, bonus automation. Vendor claims: Safran 1,100 hires in one year, 18% of referred candidates hired. This is a strong incumbent for the employer-paid option in PAYER_EXPERIMENT. | https://recruteur.hellowork.com/fr/produit/cooptation.html |
| Missing French comparators | **Gap.** Keycoopt runs an anonymous external coopter club and a white-label SaaS; press reports 25k coopters and €500–1,000 bonuses (older, unverified). Coop-Time and BeCoopt also exist. A 2026 roundup lists 12 cooptation tools. | https://www.frenchweb.fr/un-tiers-des-cadres-sont-recrutes-par-la-recommandation-keycoopt/211563, https://culture-rh.com/logiciel-rh/cooptation/ |
| Missing free substitute | **Gap.** Blind and Glassdoor referral forums already match strangers to verified employees for free (press, 2025-01). | https://inquirer.com/business/referral-jobs-strangers-bonus-employees-20250118.html |
| Bonus motivates referrers (original concept) | **Unchecked and at risk.** Many referral policies require the referrer to know the candidate, and they warn against referring strangers or pay nothing for such referrals (sample policies and press). This undermines the cross-company-stranger premise. Not checked against any French employer policy. | https://emory.edu/itpays, https://www.nbcnews.com/id/wbna6988121 |
| Demand (candidate, referrer, payer) | **None.** No interviews, no waitlist, no buyer conversation. PAYER_EXPERIMENT's €500/€600 fees and every threshold are labelled as assumptions. | docs/mvp/PAYER_EXPERIMENT.md |
| Legal sources (L5321-3, CNIL) | Cited correctly as constraints, not as clearance. Not re-verified here. | SOURCES.md |

## 3. Product and MVP assessment

- **Job and user.** A job seeker wants a warm introduction to a role. An employee is willing to review the request and refer them. Candidates do not pay.
- **What works today (I re-ran this, §5).** A local, synthetic, loopback web app covers signup/verification, discovery filters with honest stated-criteria comparison (no invented scores), request, review, accept or decline, per-scope contact grants with revocation, messaging, block/report, withdraw/close, export/delete, migrations, backup/restore, and FR/EN UI text. Engineering quality is well above prototype level.
- **What is missing.** Any real user, referrer or employer. Rights inventory, a named controller and an employer policy (launch gates R1–R4 and P1–P4 are all UNKNOWN). Hosting. Any answer to "why would an employee review strangers' requests when policies may forbid paying for them?"
- **Recommendation: HOLD.** Six packages have built a well-tested app for a market with no demand signal. The space has strong incumbents: Basile/Hellowork and Keycoopt on the employer side, Blind for free, Refer.me candidate-paid. The model has a two-sided cold start and depends on HR sales, which fits a solo ML engineer with little sales time poorly. Further engineering has low expected value until one gate passes. HOLD rather than STOP, because the asset is finished and the next test is cheap and needs no code.
- **Most important next gate (policy plus referrer willingness).** Collect at least 8 real French employer cooptation policies and run 5 employee conversations at distinct employers. Pass if at least 3 employees confirm two things: their written policy permits referring a candidate first met through a third-party platform, and they would review at least 2 requests a month. **STOP if** policies generally require prior acquaintance, or fewer than 2 of 5 employees are willing. Buyer (HR) conversations come only after a pass.

## 4. Scores (portfolio-reviewed-v1, 1–10)

| Criterion | Stored | Proposed | Rationale |
| --- | --- | --- | --- |
| Revenue potential | 7 | 4 | Candidates are free by law and scope. The employer budget already goes to Basile/Keycoopt-type tools. A €500 cohort is only a hypothesis. |
| Profitability ease | 3 | 3 | Manual operator hours per cohort and HR sales cycles. |
| MVP speed | 7 | 8 | The MVP exists: 250 tests and a green browser flow, re-run today. |
| Founder fit | 7 | 5 | Engineering fits. HR/B2B sales and a two-sided launch do not. ML is not central. |
| Go-to-market ease | 3 | 2 | Two-sided cold start plus employer approval per company. |
| Moat | 7 | 3 | No data or network yet. Incumbents hold employer relationships. Consent UX is copyable. |
| Problem intensity | 7 | 6 | Referrals clearly matter to seekers (heavy Blind forum activity, per press). Referrer pain is low. |
| Retention | 6 | 3 | Job search is episodic. The referrer side is unpaid and voluntary. |
| Legal/ethical risk (penalty) | 4 | 6 | Recruitment personal data under GDPR, the L5321-3 candidate-fee ban, bonus-splitting and employer-policy conflicts. |
| Capital intensity (penalty) | 3 | 2 | Runs locally. Hosting would be cheap. |
| Network dependency (penalty) | 8 | 9 | Needs seekers, employees and employer policy all at once. |
| Competition (penalty) | 8 | 8 | Basile, Keycoopt, Coop-Time, Blind/Glassdoor forums, Refer.me, LinkedIn. |

Under the card's arithmetic (positive raw×w×10 minus penalty (raw−1)×w×10), the proposed total is about **30.8** against the stored 48.0. Confidence: **medium** for competition and fit, **low** for demand. **Score change: lower.** The stored card scores a different, broader concept and none of it was revalidated.

## 5. Code audit

**Checks run on `f3a8c13`, in-repo ignored envs `.venv-mvp`/`.venv-ci`:**

- `bash tools/run_local_mvp.sh --prepare-only --data-dir <scratch>`: exit 0 in 16 s. Locked install, migrate and seed all worked; the README path works.
- `sh backend/run_tests.sh .venv-mvp/bin/python` with the CI environment: **250 passed**, 3 warnings, 92.22% coverage, every file ≥ 60%. 2 min 23 s.
- CI-scoped `ruff check`/`ruff format --check` on 7 files: pass. `mypy` on 5 configured files: pass.
- Frontend: `check-generated` pass. `node --test` **14/14**. Lint, `next build`, web `tsc` and mobile `tsc` all pass.
- `tools/verify_local_mvp.py` on ports 18400/18401: **2/2 Chromium (desktop, 390px)** plus refusal/restart/shutdown, all PASS, 2 min 4 s.
- Not in CI: `ruff check backend tools` gives **453 findings** (436 auto-fixable). 106 files would be reformatted. Non-strict `mypy app` gives 8 errors. Strict mypy over all of `app` gives 751.

| Sev | Finding | Path | Fix sketch |
| --- | --- | --- | --- |
| major | Lint and types gate only about 7 "changed-scope" files. The remaining roughly 110 backend modules are unchecked: 453 ruff findings, 8 real mypy errors (e.g. `str \| None` passed as `str`, SMTP vs SMTP_SSL). | `.github/workflows/backend.yml`, `pyproject.toml [tool.mypy] files` | One mechanical `ruff --fix`/format commit, fix the 8 errors, then widen CI to `backend tools` with non-strict mypy over `app`. |
| major | Known pre-existing race: a stale `GET /referrer/jobs` overwrites state after a POST, so the e2e flow is flaky under load (PR #3 reports 0/6 local fully green). It passed 1/1 here. | `frontend/apps/web/src/app/profile/page.tsx` | Add a request generation/abort guard and a regression test. Require repeated e2e green. |
| major | Duplicate rules: the web re-implements the backend introduction transition table. Web password rules are stricter than the backend's. | `frontend/apps/web/src/app/lib/introduction.ts`, backend auth schemas | Serve allowed transitions and password rules from the API or OpenAPI. |
| minor | Fail-open default: `ENVIRONMENT` defaults to `dev`, which accepts the `change-me` JWT secret. The launcher supplies a real secret, but a bare `uvicorn` start does not. | `backend/app/config/settings.py:18,30` | Require an explicit ENVIRONMENT and reject `change-me` everywhere except test. |
| minor | 19 role/status string literals remain outside `constants/enums.py` (user remark in `next_propmpt`). | `api/routes/matches.py`, `domain/introductions.py`, `domain/conversations.py` and others | Replace them with `StrEnum` members and add a grep guard test. |
| minor | Legacy paths remain alongside the MVP: Dockerfile/compose, conda `start_backend.sh`, `terminal_frontend`, `browser_frontend`, `dev_ui.py`, unwired `fingerprints.py`. | `backend/` | Delete or move under `legacy/` after a human decision (listed in PR #3). |
| minor | Generated docs (100 files) were tracked and `next-env.d.ts` churns on build; my build dirtied it and I restored it. **Fixed upstream in PR #3.** | `backend/generated/docs`, `frontend/apps/web/next-env.d.ts` | Fast-forward local main. |
| minor | `<html lang="fr">` is static while EN is selectable. i18n uses inline `tr(fr,en)` pairs, which is fine for 2 languages. Only 12 `aria-*` attributes across the web app. The fixed header overlaps content in a full-page screenshot (`desktop-sharing.png`), possibly a screenshot artefact. | `frontend/apps/web/src/app/layout.tsx` | Set `lang` from state. Run an axe pass in e2e. |
| minor | Docs sprawl: 20 MVP docs totalling about 18k words. `README` has no `.md` extension, so GitHub shows it as plain text. Root holds stray files, including an empty file named "unchanged. Venture and coordination records were updated". | repo root, `docs/mvp/` | Keep README, LOCAL_RUN and LAUNCH_GATES as current. Archive the rest under `docs/history/`. Human to delete the stray files. |

Security basics are good. No raw SQL string building was found, and there is no `dangerouslySetInnerHTML`. CORS uses an allow-list. Hash-locked Python is used, actions are SHA-pinned, and `.gitignore` covers databases, env files and traces. CSRF, rate-limit and PII boundary tests exist. A person can run the app in about 5 minutes from the README (verified).

## 6. Proposed work packages (priority order)

1. **C01: Reconcile Coopain's Foundry record (S, low).** Coordinator work, no code. Update `next_action` to the canonical repo and to the HOLD gate. Record PR #3, `fc5b92b` and Actions `37928455952`. Close or supersede `285e380e` and `90e268be`. Review the 3 unreviewed evidence records. Add assumptions for policy permission, referrer willingness and candidate demand. Store a reassessed score from §4. *Acceptance:* `resume` shows a current repo path, a non-null next work item and a score that is not scope-stale; there are no stale blocked items.
2. **C02: Policy and competition desk pack (M, medium; depends on C01).** Collect at least 8 public French employer cooptation policies or charters, recording whether stranger or platform referrals are eligible and bonus conditions. Add a comparator table (Basile, Keycoopt, Coop-Time, BeCoopt, Blind, Refer.me, LinkedIn) with dated URLs. Draft (do not send) a 5-employee and 5-seeker interview guide with pass/stop rules. *Acceptance:* sources are dated, vendor claims are labelled and nothing is sent; Foundry evidence records are linked to the assumptions.
3. **C03: Fast-forward local main and fix the profile race (M, medium; needs human authorisation for any push).** Fast-forward local main to `fc5b92b`. Add a stale-response guard in `profile/page.tsx` with a regression test. *Acceptance:* `verify_local_mvp.py` passes 5 consecutive local runs, and the backend suite stays at or above 267 passing tests.
4. **C04: Whole-repo quality gates and enums (M, low; after C03).** One mechanical ruff fix/format commit. Fix the 8 mypy errors. Widen CI lint/type scope. Replace the role/status literals with `StrEnum`. *Acceptance:* CI runs `ruff check backend tools` and `mypy app` cleanly, the test count is unchanged and green, and the contract OpenAPI is byte-identical.
5. **C05: Fail-closed configuration and a11y basics (S, low; after C03).** Require an explicit `ENVIRONMENT` and reject the default secret. Set a dynamic `lang`. Add an axe check to e2e. *Acceptance:* a new settings test fails on the `change-me` secret outside test, and the axe check reports zero serious violations on the 3 main pages.
6. **C06: Single source for transition and password rules (M, medium; after C03).** *Acceptance:* the web reads the rules from the API or generated contract, and a test covers each disallowed transition.

Under HOLD, C03–C06 should run only if C02 and the human interviews pass. The exception is C03's race fix, which is worth doing if any demo is planned.

## 7. Delivery state

- Remote `git@github.com:Jonathan2021/coopain.git`. Local HEAD `f3a8c13e`; `origin/main` is `fc5b92bd` (PR #3 "Cleanup and CI refresh", merged 2026-10-09T12:11Z, 21 commits). Local main is behind and was not touched.
- Latest CI: run **37928455952**, success, main push of `fc5b92b`. The previous main run was 37791874356 (success, `f3a8c13`).
- Pre-existing untracked files, all left untouched: `backend/generated/refactor_scan_20260311.md`, `backend/openapi_new.yaml`, `backend/preprompt`, `backend/test_results/`, `backend/tmp_prompt`, `next_propmpt`, and an empty file named `unchanged. Venture and coordination records were updated`.
- Ignored artifacts created by this review: `.venv-mvp/`, `.venv-ci/`, frontend build outputs, `backend/generated/coverage.json`, `.foundry/feedback-input-{1,2,3}.json`, and `feedback/<id>.json` plus receipts. No tracked file was left modified.

## 8. Foundry friction filed

- `96a2ae4c-11a3-4898-94b3-cdd2634f3216` (friction): `next_action` points to the old checkout; there is no delivery-drift signal for PR #3.
- `044c6697-318b-43b0-aa4e-86c1abef74e8` (bug): stale, scope-mismatched score; Discovery vs `solution_validation` stage conflict; no reassessment prompt.
- `341bf215-8f3e-4b4c-98c7-a3d72ee53928` (friction, with positive notes): inconsistent `--id`/`--venture-id`/`--workspace-id` flags; run-together rationale text; duplicated map nodes. Positive: the `resume` markdown was the fastest way to get oriented.

All three were recorded as `recorded_for_review`.

```json
{"venture":"v-coopain","recommendation":"HOLD","scores":{"revenue":4,"profitability":3,"mvp_speed":8,"founder_fit":5,"go_to_market":2,"moat":3,"problem":6,"retention":3,"legal_risk":6,"capital":2,"network":9,"competition":8},"confidence":"medium","score_change":"lower","packages":[{"id":"C01","title":"Reconcile Coopain Foundry record","description":"Update next_action to canonical repo and HOLD gate, record PR #3 fc5b92b and run 37928455952, close superseded blocked items 285e380e/90e268be, review 3 unreviewed evidence, add policy/referrer/demand assumptions, store reassessed score.","acceptance":"resume shows current repo path, non-null next work item, non-scope-stale score, no stale blocked items","size":"S","effort":"low","depends_on":[]},{"id":"C02","title":"Policy and competition desk pack","description":"Collect >=8 French employer cooptation policies (stranger/platform referral eligibility, bonus conditions), dated comparator table, unsent interview guide with pass/stop rules.","acceptance":"dated sources, vendor claims labelled, nothing sent, Foundry evidence linked to assumptions","size":"M","effort":"medium","depends_on":["C01"]},{"id":"C03","title":"Sync main and fix profile stale-load race","description":"Fast-forward local main to fc5b92b; guard stale GET /referrer/jobs responses in profile page with regression test.","acceptance":"verify_local_mvp.py passes 5 consecutive runs; backend suite >=267 passed","size":"M","effort":"medium","depends_on":[]},{"id":"C04","title":"Whole-repo quality gates and enums","description":"Mechanical ruff fix/format, fix 8 mypy errors, widen CI lint/type scope, replace role/status literals with StrEnum.","acceptance":"CI ruff check backend tools and mypy app clean; tests unchanged and green; OpenAPI byte-identical","size":"M","effort":"low","depends_on":["C03"]},{"id":"C05","title":"Fail-closed config and a11y basics","description":"Require explicit ENVIRONMENT, reject default JWT secret outside test, dynamic html lang, axe check in e2e.","acceptance":"settings test rejects change-me outside test; axe zero serious violations on 3 main pages","size":"S","effort":"low","depends_on":["C03"]},{"id":"C06","title":"Single source for transition and password rules","description":"Expose introduction transitions and password policy from backend/contract; remove web duplicates.","acceptance":"web consumes API/contract rules; test per disallowed transition","size":"M","effort":"medium","depends_on":["C03"]}],"feedback_ids":["96a2ae4c-11a3-4898-94b3-cdd2634f3216","044c6697-318b-43b0-aa4e-86c1abef74e8","341bf215-8f3e-4b4c-98c7-a3d72ee53928"],"blockers":["No demand, referrer-willingness or buyer evidence","Employer referral policies may forbid or not pay stranger referrals (unchecked for France)","Launch gates R1-R4 and P1-P4 (rights, controller, privacy, employer policy) all UNKNOWN","Local main behind GitHub main fc5b92b; Foundry unaware of PR #3"]}
```
