# OfferCheck (`v-offer-check`): portfolio review, 2026-10-09

Reviewer: `reviewer-offercheck-20261009`. Read-only on code and git. I claimed no Foundry work and submitted or resolved no results.
Workspace `546ed36a-a8be-4639-b88c-1b3bcf96c7d8`. Repository `/home/jonathan/startup_lab/offer-check`.

**Recommendation: HOLD, with a time box that defaults to STOP.** The engineering is sound. The product thesis is weak, and recent public evidence weakens it further.

## 1. Foundry record audit

**What Foundry records** (`resume`, `cli agent resume`, `review show`, `decision-map show`, `venture show`, list commands, console on :8765):

| Item | State |
| --- | --- |
| Current review | `1715a19a-1ae7-46c1-b3fc-c7efbdb7365d`, revision 10, written by `reviewer-offer-release-20261008-o07`. Disposition **pursue**, stage `solution_validation`, maturity `concept`, `work_state=not_scheduled`, `blocker=null`, `owner=null`. |
| Latest decision | `6fda993b-2ae8-4c86-89dc-f479659b7777`, kind `continue` (O07 delivery). There are 8 decisions in total; the first is `2ee34c83-…` (`narrow`: GO for a bounded private MVP). O06's `cde025fb-…` is `defer`. |
| Accepted result | `9dd3dd2e-f4a3-5af5-80b6-4f735175921d` (O07), context `af6598fc-…`. |
| Decision map | Revision `41345a6d-c84c-52b6-b373-eb928f4088f8`, sequence 11, 16 nodes and 14 edges. The focus is `pilot`, which asks "Does OfferCheck improve permitted real quote comparisons?" It has two branches: "one targeted input integration" and "adapter/template or stop". |
| Work items (9) | O01–O07 are done (`8647e0b4`, `d7c274e2`, `f6c34318`, `b1999ef1`, `4da483b9`, `5f244a1b`, `ccb572cc`). Investigation `ed72e9e5` is done. `1aeafba1` is cancelled. No next work item exists. |
| Evidence | 19 items. Two are medium-confidence desk/probe observations; the other 17 are high-confidence technical results. Customer or demand evidence: **none**. |
| Assumptions / experiments | **0 / 0.** This holds even though `experiments/quote_rules_probe.py` and a 13-case probe exist. |
| Score | `venture-score show --id v-offer-check` returns `current: null` and empty history (card `portfolio-reviewed-v1`, idea `conversation-offer-check-20261007`). The console shows "Not yet scored". |
| Human gate | R013 (`foundry/requests/2026-10-08-offer-check-R013-quotes.md`) has an **empty Response block**. It exists only as a markdown file and as free text inside `next_action`. |

**Coherence for a human reading for five minutes.** The technical story is easy to follow (O01→O07, each with evidence and a decision). The product story is not:

- **The blocker is hidden.** The console says "Owner: agent · Not scheduled" and "No open human requests", and it labels the venture "pursue". In reality nothing can proceed without the operator's R013 answer.
- **Three stage labels disagree.** `venture.stage=discovery`, `investigation_stage=solution_validation` and `product_maturity=concept`, while a CI-verified 0.1.0 MVP exists.
- **The map has stale duplicates.** The map still contains placeholder `Question O02..O05` nodes, with no status, beside the `Record O02..O05 Done` nodes.
- **Cancelled work is presented as startable.** The Work tab opens with the cancelled "Initial manual review" and offers "Copy manual review handoff / Start an agent session".
- **The header repeats the 300-character next action twice.**
- **Foundry is stale relative to the repository.** It records final main `411d683`. GitHub main is `7c33c95`: PR #1 "Cleanup and CI refresh (2026-10-09)" was merged at 12:27Z and raised the core tests from 59 to 107. Nothing about it is recorded in Foundry; the PR body says no package was claimed.
- **CLI selectors are inconsistent.** The list commands require `--venture-id`, `decision-map`/`review show` require `--workspace-id`, and `venture-score show` requires `--id`.

## 2. Prior research gaps

| Claim (prior reports, 2026-10-07) | Status 2026-10-09 | Source / date checked |
| --- | --- | --- |
| QuoteWerks VendorRFQ and Fairmarkit already compare supplier bids; Fairmarkit has an RFQ API | Retained. **Not rechecked** within this review's web budget. | quotewerks.com/features/vendor-rfq-software, help.fairmarkit.com/product-guides/compare-bids (cited 2026-10-07) |
| "Neither comparison nor agent access is novel" | **Strengthened.** Umbiko (Product Hunt, launched 2026, about 5 months ago) does AI extraction from PDF, Excel and Word quotes into a ranked side-by-side comparison. It flags "missing items, unusual pricing, divergent specs", is EU-hosted and has a free option. | https://www.producthunt.com/products/umbiko (2026-10-09) |
| Procurement suites cover quotes | Precoro launched AI conversion of supplier quotes into requisitions on 2026-04-21 (extraction only; comparison not stated). Procurify's quote comparison is confirmed only by third-party roundups. Comarch ERP and Odoo ship "compare supplier quotations" and RFQ modules. | newsfilecorp.com release 292748; help.comarch.com/cee/?p=6608; rfp.wiki Procurify pages (2026-10-09) |
| Differentiator: missing terms stay unknown, incomplete totals are not ranked, the source is linked | **Directly matched by free content.** An ilisai (EU AI workspace) French guide published 2026-09-06 uses three states, "Inclus / Exclu / Non précisé". It rules that a missing cost is never zero and an incomplete total is never ranked cheapest, and its extraction prompt cites the source document and page for every field. It ships an XLSX template. | https://www.ilisai.com/fr/blog/comparer-devis-fournisseurs (2026-10-09) |
| LLM quote extraction tools | Several are cheap or free: imagetotable.ai (French blog series on extracting vendor quotes into Excel), Taskade PDF-quote-to-spreadsheet templates, and an Apify "QuoteCheck MVP" actor. The actor appeared in search results, but its page returned 404 on fetch. | taskade.com/convert/pdf-to-spreadsheet/vendor-quote-pdf-to-spreadsheet; imagetotable.ai/fr/blog/* (2026-10-09) |
| Spendesk / Payhawk quote features | **Not checked** (web budget). | — |

**Gaps never addressed:**

1. No named user, interview, or count of how often anyone compares exact-SKU quotes.
2. No pricing or willingness-to-pay hypothesis.
3. No test, before building, of the "usual agent plus template" baseline that now looks like the real competitor.
4. The chosen scope (exact SKU, fixed packs, domestic EUR, no discounts or tiers) removes exactly the cases where spreadsheets and LLMs struggle.
5. It is unclear whose "owner-authorized" quotes R013 expects. The founder has no procurement role.

## 3. Product and MVP assessment

**Job and user.** A small equipment-buying team, or its agent, compares two or more supplier quotes for the same exact SKUs. They want to see the real request total (pack rounding, charges counted once), the missing terms, and a versioned, source-linked receipt before shortlisting.

**What works today (verified locally).**

- Authenticated workspaces with viewer, editor and reviewer roles, plus scoped tokens.
- Immutable request and offer revisions with compare-and-set (CAS) and idempotency keys.
- Deterministic fixed-pack checks in `services/checks.py`: unknown charges stay null, totals are withheld when the input is incomplete or unsupported, and expiry, lateness and SKU blocks apply.
- Human-only field review and decisions.
- Stale-comparison refusal.
- Receipts, backup/restore and retention.
- A desktop and 390 px UI.
- A seeded demo that runs on a fresh data directory. I logged in as the reviewer on port 8093. The outsider token sees `[]`, and unauthenticated requests get 401.

**What is missing for the promise.**

1. **Getting terms out of real quotes.** Capture is manual. Source links are typed as a raw JSON array (`artifact_id`, `sha256`, `locator`, `excerpt`) in a textarea (`templates/offer_form.html`). Competitors automate exactly this step.
2. **Realistic sources.** Every synthetic source, both the seed and `trials/o06/sources/*.txt`, is a JSON dump of the structured offer. Source correspondence and the "independent formula baseline" therefore never touch prose or PDF quotes such as "Port offert dès 150 € HT" or "lot de 10".
3. **French UI.** The UI is English-only (`lang="en"`) although the target is France and EUR.
4. **Users and evidence of value.** No real user and no comparative evidence.

**Verdict: HOLD, defaulting to STOP.** The MVP solves the easy half of the problem: arithmetic over terms a human already transcribed. That half is reproducible with a free template plus a prompt. The hard half (extraction, messy terms, tiered pricing, substitutions) is explicitly out of scope, and incumbents and new tools address it. The founder has no procurement access or channel. Further engineering would be gold-plating.

Keep the repository as a clean, archived-ready asset. Give R013 a deadline of **2026-10-23**. If no permitted quote set and reviewer exist by then, record STOP for the standalone product.

**Single most important gate.** Run R013's matched trial with a **stronger baseline arm**: the operator's usual LLM agent with an ilisai-style "inclus/exclu/non précisé" template, working from the original quote documents. Run OfferCheck on the identical frozen inputs and include its capture time. Continue only if OfferCheck shows fewer material misses at equal or lower total effort, *and* the operator says they would reuse it for the next purchase.

## 4. Scores (portfolio-reviewed-v1, 1–10)

| Factor | Score | Rationale |
| --- | --- | --- |
| Revenue potential | 3 | Quote comparison is a feature inside P2P, ERP or AI workspaces. Use is episodic and SME willingness to pay is low and unproven. |
| Profitability ease | 4 | Software margins are fine, but acquisition cost would dwarf a tiny ARPU. |
| MVP speed | 7 | The MVP exists and is CI-verified. The missing extraction step is moderate work. |
| Founder fit | 4 | ML skills fit extraction. There is no procurement background, buyer network or quote access. |
| Go-to-market ease | 2 | There is no channel. Buyers are diffuse, and incumbents bundle the feature or offer it free. |
| Moat | 1 | The deterministic rules fit in a spreadsheet, and a public French guide already encodes them. |
| Problem intensity | 3 | Comparing two exact-SKU quotes is a 10-minute job. The painful cases are out of scope. |
| Retention | 3 | Purchase-driven and episodic, with no data lock-in. |
| Legal/ethical risk (penalty) | 3 | Confidential commercial documents and GDPR. Mitigated by local-only use and no purchasing authority. |
| Capital intensity (penalty) | 2 | Local software. No inventory, payments or cloud spend. |
| Network dependency (penalty) | 3 | Needs real quotes and a reviewer from someone else, but no two-sided network. |
| Competition intensity (penalty) | 9 | QuoteWerks, Fairmarkit, Precoro, Procurify, ERP RFQ modules, Umbiko, imagetotable, Taskade, general LLMs and free templates. |

Confidence: **medium-low** (desk research only, no primary customer data; competition evidence is strongest). **Record** this score: there is none today, and portfolio comparison needs one.

## 5. Code audit findings

**Commands run on local checkout `411d683`** (clean tree, existing `.venv`, uv 0.11.29, Python 3.13.5):

- `make check` exited 0 in 29 s. Ruff: "All checks passed". mypy: "no issues found in 23 source files". pytest: **59 passed, 6 deselected**, 1 warning (Starlette TestClient/httpx deprecation).
- `uv run pytest -m browser -q` exited 0: **6 passed** (the existing Chromium 1243 install was used).
- `uv run offer-check migrate` and `seed-demo` were run with `OFFER_CHECK_DATA` in my scratchpad. Both succeeded; files were created with 0600/0700 modes.
- `serve --port 8093` ran, I made curl/urllib requests for login, `/`, a request page, API lists and an artifact download, and then stopped the server.

**I did not run the checks on remote main `7c33c95`.** Its PR reports 107 core tests and green run 37911338102.

**CI** (`.github/workflows/ci.yml`): a single ubuntu-24.04 job with read-only permissions, a 20-minute timeout, and SHA-pinned actions (checkout v7.0.1, setup-uv v10.2.0, upload-artifact v7.0.2). It runs `uv sync --locked`, `make check`, a JS syntax check, a schema-drift check, Chromium tests, a locked-hash build, runtime-only wheel startup/recovery/rehearsal, and 1-day artifacts. `gh run list` (5 runs) shows 37930110427 success (main, merge of PR #1), 37911338102 success (PR), 37771813336 success, 37771021623 failure (the commit-visibility 404 later repaired) and 37769883064 success.

| Severity | Finding | Path |
| --- | --- | --- |
| Medium (product) | Source linking requires hand-typed JSON evidence (artifact id, sha256, locator, excerpt). This is impractical for the human user the product targets and is the step competitors automate. | `src/offer_check/templates/offer_form.html` |
| Medium (validation honesty) | Demo and trial "sources" are JSON serializations of the structured offer, so the rehearsal and workbook reconciliation are near-tautological. They never test transcription from realistic quote text or PDFs. | `src/offer_check/seed.py`, `trials/o06/sources/*.txt` |
| Low | English-only UI for a France/EUR target. Login requires typing a workspace UUID. | `templates/base.html`, `templates/login.html` |
| Low | The login throttle is an in-process dict keyed by client host. It is unbounded and resets on restart. scrypt runs only when the user exists, which creates a username-timing oracle. Acceptable on loopback; it should be a deployment gate. | `src/offer_check/app.py` (`login`) |
| Low | The session cookie has no `Secure` flag. Correct for loopback HTTP; it must change before any hosting. | `app.py` (`set_cookie`) |
| Low | The `async def upload` handler does synchronous SQLAlchemy and file I/O on the event loop. Negligible for a single local user. | `app.py` (`upload`) |
| Info, positive | Transaction handling is correct. The DB dependency is function-scoped (`Depends(database, scope="function")`) and commits or rolls back before any success response. Writes use `BEGIN IMMEDIATE`. The upload path commits explicitly after flush and unlinks the file on failure. Four red-first tests cover this in `tests/integration/test_response_commit.py`. | `app.py`, `db.py` |
| Info, positive | Integer cents, no currency conversion. Unknowns stay null. Tax-basis mismatch withholds the total. Expiry uses an injected tz-aware clock. A "source_unreviewed" issue blocks the comparable status, so there is no unlabelled extraction (there is no extraction at all). Field reviews and decisions require a human cookie session with the reviewer role; tokens cannot attest. | `services/checks.py`, `auth.py` |
| Info | Lines match on an operator-assigned `line_id`. A correct SKU under a different id yields `missing_line` plus `unmapped_extra` blocks. Safe, but the error is surprising. | `services/checks.py` |
| Info | Dependencies use ranges in `pyproject.toml`, an exact `uv.lock`, `--locked` installs and hash-checked build constraints. Migrations 0001/0002 applied cleanly to a fresh DB. | `pyproject.toml`, `src/offer_check/migrations/` |
| Info | Stale documentation. `docs/mvp/REVIEW_NEXT.md` says "baseline has no HEAD". The dated handoffs (`FIRST_TASK.md`, `NEXT_HANDOFF.md`, `READINESS_HANDOFF.md`) still name claimable work. The probe in `experiments/` is outside lint. PR #1 flagged the same handoff issue. | `docs/mvp/` |

**README five-minute run.** `uv sync --locked; migrate; seed-demo; serve` worked as documented, and the demo login and comparison pages render. Note that `seed-demo` writes credentials into `OFFER_CHECK_DATA`, not always `.local/`, which the README implies. No dead code was found in my checkout beyond what PR #1 already removed upstream.

## 6. Proposed work packages (HOLD: minimal, in priority order)

Full descriptions and acceptance criteria are in the JSON block below.

1. **OC-R1 Reconcile repository and Foundry state** (S, low effort): fast-forward to `7c33c95`, rerun the checks, record PR #1 and run 37930110427, retire the stale O02–O05 nodes.
2. **OC-R2 Record HOLD and score** (S, low effort; after R1): hold disposition, R013 human blocker owned by the operator, revisit 2026-10-23, section 4 scorecard.
3. **OC-R3 Time-box R013** (S, low effort): add the deadline, the default-to-STOP rule and the usual-agent + template baseline arm, preserving existing text.
4. **OC-R4 Repository hygiene** (S, low effort; after R1): historical banners on dated handoffs, fix the REVIEW_NEXT "no HEAD" line, decide the policy for `feedback/` outbox files.
5. **OC-T1 R013 matched three-arm trial** (M, high effort; only if R013 is answered; after R3).
6. **OC-S1 Stop and archive** (S, low effort; if there is no R013 answer by 2026-10-23 or T1 shows no advantage). Archiving on GitHub requires owner approval.

I deliberately propose no extraction, French UI or hosting work until T1 shows the checker adds value beyond the baseline.

## 7. Delivery state

- **Remote:** `git@github.com:Jonathan2021/offer-check.git` (private). Remote main is `7c33c9538dddc1bb8ad39e61849aee42e06b8f38` (merge of PR #1). The last CI run is **37930110427, success**, 2026-10-09T12:27Z.
- **Local:** the checkout is at `411d683` and is **behind remote by the PR #1 merge**. I did not fetch it.
- **Working tree:** clean at the start. My only changes are six untracked outbox files under `feedback/`, created by the required feedback helper, plus `.foundry/feedback-input-{1,2,3}.json`, which are git-ignored.
- **Demo data and logs:** these went to my scratchpad, not the repository. The server is stopped.
- **Untouched:** the dirty files in the foundry repository listed in the session's git status.

## 8. Foundry friction filed

- `4ed2d64d-4e11-4dbf-b422-d7a8b6d2a325` (friction): the R013 human blocker is invisible ("Owner: agent", "No open human requests", blocker null), and the next action is duplicated. Evidence `f7ec997d-2abe-4b58-b027-4cb49f5bf95a`.
- `3559c1dc-dd4c-4657-a908-91a0be932ea8` (friction): stale placeholder map nodes, contradictory stage fields, and startable actions on cancelled work. Evidence `905f07ba-d74a-49f7-a84e-4d92aae106c2`.
- `b368c596-9ebf-4f86-ac26-c6b9ba582219` (idea): no repository-drift detection (Foundry records 411d683 while remote is 7c33c95), and inconsistent `--id`/`--venture-id`/`--workspace-id` selectors. Evidence `6fe7c685-51fd-49e2-8d8b-951fb71e4fbd`.

```json
{"venture":"v-offer-check","recommendation":"HOLD","scores":{"revenue":3,"profitability":4,"mvp_speed":7,"founder_fit":4,"go_to_market":2,"moat":1,"problem":3,"retention":3,"legal_risk":3,"capital":2,"network":3,"competition":9},"confidence":"medium-low: desk research only, no primary customer data; competition evidence strongest","score_change":"record","packages":[{"id":"OC-R1","title":"Reconcile repository and Foundry state","description":"Fast-forward local checkout to remote main 7c33c95, rerun make check and browser tests, record PR #1 and CI run 37930110427 as evidence, retire stale O02-O05 placeholder map nodes.","acceptance":"Local HEAD equals remote main; Foundry evidence cites 7c33c95 with actual test counts; decision map has no undone duplicate O-nodes.","size":"S","effort":"low","depends_on":[]},{"id":"OC-R2","title":"Record HOLD decision and score","description":"Append review with disposition hold, blocker R013 human input, owner operator, revisit 2026-10-23; record portfolio-reviewed-v1 scorecard from this review.","acceptance":"Console shows hold, operator-owned blocker, score and revisit date; venture-score show returns a current score.","size":"S","effort":"low","depends_on":["OC-R1"]},{"id":"OC-R3","title":"Time-box R013","description":"Append to R013 and INBOX a 2026-10-23 deadline, default-to-STOP rule, and an added usual-agent plus inclus/exclu/non-precise template baseline arm; preserve existing text.","acceptance":"Request names deadline, baseline arm and success rule; original text and replies preserved.","size":"S","effort":"low","depends_on":[]},{"id":"OC-R4","title":"Repository hygiene","description":"Historical banners on dated handoffs, fix REVIEW_NEXT 'no HEAD' statement, decide commit-or-ignore policy for feedback outbox files.","acceptance":"Clean git status after decision; no document presents finished packages as claimable.","size":"S","effort":"low","depends_on":["OC-R1"]},{"id":"OC-T1","title":"R013 matched three-arm trial","description":"Conditional on an R013 answer: template, usual agent plus template, and OfferCheck on identical frozen permitted inputs including capture time.","acceptance":"Filled trial record with times, material misses, unknowns, corrections and reuse intent; GO-narrow or STOP decision recorded in Foundry.","size":"M","effort":"high","depends_on":["OC-R3"]},{"id":"OC-S1","title":"Stop and archive","description":"Conditional on no R013 answer by 2026-10-23 or no advantage in OC-T1: README archived banner, Foundry disposition dropped with rationale, GitHub archive only with explicit owner approval.","acceptance":"Foundry shows dropped with rationale; repository documented as archived.","size":"S","effort":"low","depends_on":["OC-R2"]}],"feedback_ids":["4ed2d64d-4e11-4dbf-b422-d7a8b6d2a325","3559c1dc-dd4c-4657-a908-91a0be932ea8","b368c596-9ebf-4f86-ac26-c6b9ba582219"],"blockers":["R013 owner-authorized redacted request, two existing quotes and designated reviewer: unanswered since 2026-10-08","Local checkout and Foundry record 411d683 while remote main is 7c33c95 (PR #1 unrecorded)"]}
```
