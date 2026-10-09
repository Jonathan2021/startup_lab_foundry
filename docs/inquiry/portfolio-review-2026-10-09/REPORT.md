# Portfolio review and dogfood loop — report (2026-10-09)

Status: review and recording complete; implementation deliveries in progress (section 5
fills in as each repository's agent reports). Protocol: [PROTOCOL.md](PROTOCOL.md).
Per-venture reviews: [coopain](coopain/REVIEW.md), [crous-queue](crous-queue/REVIEW.md),
[ride-options](ride-options/REVIEW.md), [volley-match](volley-match/REVIEW.md),
[offer-check](offer-check/REVIEW.md), [volley-coach](volley-coach/REVIEW.md).
Coordinator judgments: [decisions.json](decisions.json); Foundry receipts: [records.json](records.json).

## 1. One-paragraph answer

None of the six ventures is a commercial GO today. All six have working, CI-green local
MVPs; none has a single observed real user, payer or repeat use. Three are **NARROWED**
to the founder's own use with one decisive human test each (Crous Queue: five-lunch
coverage at Cuvier/Châtelet; Ride Options: the rider-vs-Kurviger trial once the 4–5 h
loop and navigation-safe GPX exist; Volley Match: two real outings with WhatsApp-shared
results). Three are **HELD** behind a cheap human question (Coopain: do French employer
referral policies allow platform strangers; OfferCheck: supply two real quotes by
2026-10-23 or stop; Volley Coach: does anyone in the group follow a written 2+/week
program). Every stored score fell or was recorded for the first time (29–37 out of
100); the earlier 47–51 figures were starting estimates for broader ideas. The code is
sane everywhere; the gaps are demand, distribution and a handful of correctness defects
that the implementation agents are fixing now.

## 2. Dispositions and scores

| Venture | Recommendation | Score (reviewed scorecard) | Stage / maturity recorded | Blockers named by the review |
| --- | --- | --- | --- | --- |
| Coopain | HOLD | 48 (idea estimate, scoped to the old concept) → **31** | problem validation / mvp | No demand, referrer-willingness or buyer evidence; Employer referral policies may forbid or not pay stranger referrals (unchecked for France); Launch gates R1-R4 and P1-P4 (rights, controller, privacy, employer policy) a |
| Crous Queue | NARROW | none (3/12 partial) → **30** | solution validation / mvp | R011 human answer (4626ac2b) outstanding since 2026-10-06; Incumbent listing check (dbbfbb3d) blocked on external access; needs a human Android check; No approved hosting/phone-reachable access; local loopback MVP cannot |
| Ride Options | NARROW | none (2/12 partial) → **35** | solution validation / mvp | Operator rider/Kurviger comparison (ae6816fd) unanswered since 2026-10-07; Local checkout 6db7080 behind remote main 2d6fd6c; fast-forward needs human approval; 16 generic restriction relations unenforced; no road use of |
| Volley Match | NARROW | 47 (starting estimate) → **37** | solution validation / mvp | R006 follow-up (foundry/requests/2026-10-07-volley-match-R006-pilot-access.md) unanswered: no willing organizer, access arrangement, consent owner or spending cap recorded; hosting and invitations remain unauthorized; Lo |
| OfferCheck | HOLD | none → **29** | business validation / mvp | R013 owner-authorized redacted request, two existing quotes and designated reviewer: unanswered since 2026-10-08; Local checkout and Foundry record 411d683 while remote main is 7c33c95 (PR #1 unrecorded) |
| Volley Coach | HOLD | none → **30** | problem validation / mvp | No demand evidence; R006 own-program operator decision unanswered; Planner schedules at most one session per goal per week, so real multi-session programs cannot be trialled; Local-only loopback access and English-only U |

Scores are agent judgments on the workbook formula (weighted positives minus penalties,
0–100; C ≥45). Each has a per-criterion rationale in the review and in Foundry
(`venture-score show --id <venture>`), with the review evidence attached to the
competition and moat criteria. The sibling venture `v-sports-ranking` (51, a 2026-10-05
estimate for the broad Elo & tournaments idea) was retired to hold; the fusion proposal
`91fe8686` awaits the user's resolution as superseded because agents cannot resolve
proposals without a human delegation receipt.

## 3. What the re-check of prior research changed

- **Coopain:** four competitors missed earlier (Basile by Hellowork, Keycoopt, Coop-Time,
  BeCoopt) plus free stranger-referral forums; the decisive unchecked risk is that
  employer referral policies often require knowing the candidate.
- **Crous Queue:** the problem worsened in 2026 (€1 meals for all students, meals +48%,
  40–60 min at Cuvier), but Affluences sensors, CrousRadar and Croustillapp cover the
  directory/hours side and the operator side; the first decision's competitor-app check
  was bypassed and is now a human precondition.
- **Ride Options:** six established apps (Kurviger, Calimoto, Scenic, Liberty Rider, 68°,
  Detecht); the core 4–5 h loop was never delivered and the GPX is a track only, which
  reproduces the user's original complaint.
- **Volley Match:** Spond, WhatsApp group events, VolleySmart, Spiker Pro, OpenSports,
  TeamChooser and OpenSkill were never assessed; a match is rated only when every player
  has an account and the other side confirms, so a one-phone trial yields no Elo.
- **OfferCheck:** Umbiko (EU-hosted, free tier), ilisai's free French guide and template
  (2026-09-06) and Precoro's AI quote extraction (2026-04-21) cover the differentiator.
- **Volley Coach:** competitors for personal training plans (Fitbod, Volt, TrueCoach,
  volleyball apps) were never researched; the recorded user pain is Volley Match's.

## 4. Work queued per venture (Foundry work items)

| Venture | Packages recorded (status at creation) |
| --- | --- |
| Coopain | C02 (ready), C03 (todo), C04 (todo), C05 (todo) |
| Crous Queue | P3 (ready), P4 (todo), P5 (todo), P6 (blocked) |
| Ride Options | RO-P0 (ready), RO-P2 (blocked), RO-P6 (blocked) |
| Volley Match | VM-R1 (ready), VM-R6 (blocked), VM-R7 (blocked) |
| OfferCheck | OC-R1 (ready), OC-R4 (todo), OC-T1 (blocked) |
| Volley Coach | VC-P3 (todo), VC-P4 (ready), VC-P5 (blocked) |

Human-gated packages are `blocked` with the gate named; agents chain the others in order
through each repository's Foundry bridge, pushing to main with exact-SHA CI, as the user
requested. Requests for the human gates: R015 (Coopain), R011 addendum (Crous), R005
(Ride), R006 addenda (Volley Match, Volley Coach), R013 addendum (OfferCheck).

## 5. Deliveries

Every venture repository is on GitHub `main` with a green CI run on the exact SHA. Each
package was claimed, checkpointed and accepted in Foundry; the per-venture record is
`<slug>/DELIVERY.md` and the receipts are in `deliveries.json`. The final `main` SHA below
is the bridge update to contract `2026-10-09.1`, recorded in Foundry as
`Delivery: main=<sha> ci=<run>` evidence so `doctor` reports no drift.

| Venture | Packages delivered | Final main (CI run) | Not done / human gate |
| --- | --- | --- | --- |
| Coopain | **C02** result 227c36d5 accepted (decision cdfaea3a); **C03** result 60695e0f accepted (decision a1b9197f); **C04** result 40feade1 accepted (decision 05b75a1b); **C05** result 6721053b accepted (decision b409d835) | `1a5325b` (37985792402) | C06 (single source for transition/password rules) deferred; legacy dev paths (Dockerfile/compose, conda scripts, terminal/browser frontends, dev_ui.py, fingerprints.py) kept: product decision. Gate: R015 five employee conversations (work 90e268be); launch gates R1-R4/P1-P8 unknown |
| Crous Queue | **P3** result be6bc8b6 accepted; **P5** result d372094d accepted; **P4** result 211623f5 accepted | `396054d` (37985797145) | P6 (human gate); PostgreSQL 16 verification. Gate: R011 answer + Android incumbent check + approve/reject the exact P4 payload, then P6 |
| Ride Options | **RO-P0** result 2322ec6f accepted; **RO-P1** result 6a38bb18 accepted; **RO-P3** result e82dd4fc accepted; **RO-P4** result 31489c39 accepted; **RO-P5** result f3b9f508 accepted | `a436d91` (37985800627) | RO-P2 founder trial (human) and RO-P6 (conditional) not claimed; operator's .local/auvergne still holds the old import; repaired import is .local/auvergne-ro-p5b; operator .env caps routing at 12 requests/30 s (left untouched). Gate: R005 rider-vs-Kurviger trial (RO-P2); switch engine import to the repaired one before riding |
| Volley Match | **VM-R1** result 09ac7dd6 accepted; **VM-R3** result 7033140c accepted; **VM-R4** result 891768bc accepted; **VM-R5** result e434772b accepted; **VM-R8** result a2d902af accepted | `39a1c32` (37985804298) | fusion proposal 91fe8686 and v-sports-ranking lineage need the user; VM-R6/VM-R7 blocked. Gate: R006 pilot (organizer, access, consent owner, spending cap) + proposal decision |
| OfferCheck | **OC-R1** result fd782e96 accepted (decision affd0dc2); **OC-R4** result 06a14882 accepted (decision 4dbdccef) | `e200d51` (37985808907) | OC-T1 blocked on R013 (deadline 2026-10-23, default STOP/archive); no extraction/FR/hosting. Gate: R013 by 2026-10-23 |
| Volley Coach | **VC-P4** result 6a9400b1 accepted (first bb34d9e5 superseded to keep the HOLD next action); **VC-P3** result 318836b9 accepted | `7b06738` (37985814380) | VC-P5 blocked on the demand question and phone-access/hosting approval; progress feature left unable to escalate difficulty (would be unreviewed physical advice); copy now says program kept as written. Gate: R006-coach demand question |

Highlights per venture:

- **Coopain** (C02–C05): the referrer-policy desk pack reads eight published French cooptation
  agreements (none requires knowing the candidate, seven assume a relationship, six exclude
  third-party-presented candidates), so R015 stays undecided until five conversations are
  held; a stale-load race in the profile and matches pages is fixed with ordered load tickets;
  lint and type checks cover the whole backend, mobile and design system with no allowlist;
  the backend refuses to start without a real secret; axe reports zero violations. One
  mistake: commit `9a2f7b1` pushed five untracked operator notes (no credentials); `bfa739b`
  untracks them, but they remain in history unless you authorise a rewrite.
- **Crous Queue** (P3, P5, P4): six fresh cookies now count as two queue reports with four
  excluded; forwarding headers are trusted only from configured proxies; the private-beta
  approval file states the exact payload (Scaleway DEV1-S, €25/month ceiling, 21 days) and
  is marked NOT AUTHORIZED; unknown opening hours are shown honestly; 390 px tests.
- **Ride Options** (RO-P0, P1, P3, P4, P5): riding-time band targeting returned two Auvergne
  loops in the 240–300 min band; GPX exports carry stop waypoints and 10 km route points;
  the repaired engine import takes 0 of 9 forbidden turns versus 8 of 9 before. Switch the
  operator import to `.local/auvergne-ro-p5b` and raise the routing cap before riding (R005
  addendum).
- **Volley Match** (VM-R1, R3, R4, R5, R8): plain-text results and standings, an Elo page with
  pre-match win probability, a server log tail on failed starts, byte-identical HTML after
  the reformat; 132 tests and three green browser runs. The fusion proposal `91fe8686` is now
  labelled stale and needs your decision.
- **OfferCheck** (OC-R1, OC-R4): no-change verification plus the quote-comparison
  preparation; everything else waits on R013 (deadline 2026-10-23, default STOP/archive).
- **Volley Coach** (VC-P4, VC-P3): multi-session programs with ordered sessions and explicit
  unscheduled notices; 81 tests, 5 browser checks; VC-P5 blocked on the demand question.

Foundry itself: `0af4c09` (CI 37985672390) ships ADR-0020; the six repositories carry the
new bridge (kit sha256 `c4f497b8…`) and `doctor` reports no drift in any of them.

## 6. Foundry: friction observed and packages

Twenty-six feedback records were filed by the review agents in one afternoon, and the
implementation agents added more while delivering. They cluster into four packages,
implemented by one Opus 5.5 agent (high effort, isolated worktree) under
[ADR-0020](../../adr/0020-truthful-venture-state-requests-and-drift.md), with
`make check` (234 tests, strict mypy on 47 files) and the browser suite green:

- **F05 — promotion provenance, schema publication, rank entries.** The venture overview
  shows the source idea's sources, competition and evidence; a venture's map, context and
  results may cite evidence from its source idea's workspace (every other cross-workspace
  reference is still rejected); the five discovery inputs are in `agent schema` (contract
  `2026-10-09.1`); `score rank` returns ranked and excluded entries with reasons.
- **F07 — one truthful venture state.** Header, venture list, Today and `agent resume`
  derive disposition, stage, maturity, score status and next action from one function;
  the stored lifecycle is shown only when it differs; the next action prints once; a
  score that predates the current scope gets a Reassess link; cancelled or done initial
  reviews are never startable; superseded legacy items leave the attention list and can
  be closed with `venture-work close`; stale fusion proposals are labelled and never
  "focus"; history rows show summaries and relative dates. Three items the implementation
  agents reported were folded in: an edge-only map edit no longer flags unchanged work; a
  work-scoped result keeps a HOLD next action and previews list `review_changes`;
  evidence cited by an accepted result leaves "unreviewed changes".
- **F08 — open human requests.** `input sync --requests-directory` registers `requests/*.md`
  sections as open human requests linked to ventures (mapping file for corrections and
  ignores; answers are never consumed); they appear on the venture page, Today and
  `agent resume`.
- **F09 — drift and CLI consistency.** The bridge's `resume`, `start` and `doctor` show
  local HEAD, local origin/main and the last recorded `Delivery: main=<sha> ci=<run>` and
  warn when the repository moved past it; read commands accept `--id` for a venture id,
  alias, workspace id/key or idea id; venture aliases (additive migration) give the Crous
  venture `v-crous-queue`; JSON output ends with a newline and INFO logs need `--debug`.

Rollout (after the venture agents finish, because the bridge contract changes): apply,
back up the store, check, commit, push, verify CI; copy the new bridge and manifest
versions into each venture repository and run `doctor`; preview then apply the request
sync; set the Crous alias; close any remaining superseded items. Done on 2026-10-09: store backed
up (`.local/backups/foundry.local.pre-f05-f09-20261009.db`), Foundry `0af4c09` pushed with CI
37985672390 green (234 tests, mypy 47 files, 5 browser checks), bridge `2026-10-09.1` committed
and CI-verified in all six repositories, request sync applied (7 open requests registered, R012
linked), alias `v-crous-queue` set, `handoff-foundry-next-r1` closed, F05 accepted (result
`a2594770`). Friction met during the rollout is listed in section 6b.

### 6b. Friction met during the rollout and by the implementers (package F10)

Reported by the six implementation agents (feedback IDs in `deliveries.json`) and by the
coordinator during the rollout; none blocked delivery. They form one follow-up package,
**F10 — Implementer follow-ups**, queued as todo in `v-foundry`:

- **Result acceptance moves the map focus off the gate.** Volley Match and Ride Options both
  had to restore the focus by hand after accepting a work-scoped result (61841218, 53d4ad73).
- **Feedback outbox git-ignored.** Coopain, Crous Queue and Volley Match ignore `feedback/`,
  so reports had to be force-added; `doctor` should warn when the outbox is ignored.
- **Accepted findings reappear as unclassified arrivals** in the next package's context
  (Coopain 4e56b8a0); the context should treat findings of accepted results as reviewed.
- **A map revise flags the claimant's own work for review and invalidates its context**;
  WorkTreatment cannot revise a question or acceptance criteria (Coopain aa783af4).
- **`venture show` has no version**, yet `venture alias` needs `expected_version`; the Crous
  alias was set after a read-only store query (feedback 74b88475).
- **`start` default budget (24000 bytes) is below the Foundry map (43686)**; the error does not
  name the bridge's `--budget` flag (757a0709).
- **`result show` lacks the pins `result resolve` needs** (head, work version, review
  revision); they come from `handoff show` under different names (dc786d6d).
- **`/ventures/<alias>` redirects to the UUID URL** instead of serving the readable address (eaddae0d).
- **`needs_review` is an object while the other work lists are arrays** (5f9a74b7).
- One expected one-time cost, not a defect: the implementers' deliveries predate the
  `Delivery: main=<sha> ci=<run>` convention, so every repository showed drift until the
  coordinator recorded the delivery evidence (`record_delivery.py`).

## 7. Limits

Reviews are dated desk research and local checks, not customer evidence; absence of a
feature in documentation is not proof of absence; scores are judgments; GO/NARROW/HOLD
authorise only bounded local work and the named human tests. Pushing to main was
explicitly requested; no hosting, accounts, spend or messages to real people occurred.
Another session merged "Cleanup and CI refresh" PRs into every repository earlier today;
all local checkouts were fast-forwarded before implementation began.
