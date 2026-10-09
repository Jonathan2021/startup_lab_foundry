# Volley Coach — delivery 2026-10-09

Implementer: `implementer-volley-coach-20261009`. Venture `v-volley-coach`, workspace
`9d0ed0f5-960b-4cd0-a52f-4176218a40e5`, repository `/home/jonathan/startup_lab/volley-coach`
(private `Jonathan2021/volley-coach`). The venture remains on **HOLD** (review revision 13, disposition hold).

## Packages completed

| Package | Work id | Result id | Commit | Actions run | Conclusion |
| --- | --- | --- | --- | --- | --- |
| VC-P4 Sync and re-verify + record hygiene | `020187bc-4614-4d8d-8845-7e408d77c98a` | `6a9400b1-7860-5804-9a31-d36696f54802` (accepted; supersedes `bb34d9e5-c460-51cf-a499-15d82187c267`, which was resubmitted only to keep the HOLD wording in next_action) | `5fde687107dc75b50b3478a8a6882f0728a17f5c` (feedback outbox only) | 37944729340 | success |
| VC-P3 Multi-session program scheduling | `1e0ee22d-0240-4824-bc3e-ebb04e91ea92` | `318836b9-5745-5098-af7c-5ec68e2f2493` (accepted) | `6ed83edb249ca951a64b8134a28c978f3feac5bd` | 37947467313 | success |

### VC-P4

- Start: HEAD = origin/main = `122968b` (PR #1, CI 37930071447 success).
- `make check` exit 0: ruff pass, 49 files formatted, strict mypy 25 source files, **71 passed**. `make test-browser` exit 0: **4 passed**. The counts match PR #1.
- Evidence `7c4c5336-1c72-4bac-b542-25f13d0ee024` (change record) covers PR #1 / run 37930071447.
- Map revision `5a9a5fa4-15b4-57a6-a100-b6233a4277a1`:
  - cancelled `da9f64ff-1b76-5e2d-bdce-537234f19324` ("superseded by decision ddf723c3 (GO planner) and the 2026-10-09 HOLD review");
  - removed the duplicate question nodes C02–C05 and their depends_on edges (the done record nodes were kept);
  - added the question node `demand_gate` ("Do ≥2 adults in the group follow a written 2+/week program?") and made it the focus;
  - added VC-P5 `depends_on` demand_gate.
- That edge flagged VC-P5 needs_review, so map `115e5a24-7e44-5589-b3b3-34511103f1dd` applied a `keep` treatment to clear it.
- Current map: `389ff7c8-5281-5e96-aff2-10a5a8f9e86e`, focus `["demand_gate"]`. `resume` shows `needs_review: {}`.

### VC-P3

- **Red first.** In `tests/unit/test_multi_session.py`, 8 tests failed because the contract fields were missing. The H1 reproduction failed with `['m1'] == ['m1','m2','m3']`. Output is in `evidence/VC-P3/red-multi-session.txt`.
- **Change:**
  - `DrillInput.sessions_per_week` (1–7, default 1) and ordered `sessions` names. A mismatch returns 422.
  - The planner places at most one session per slot. It serves the program with the fewest sessions placed first, then sorts by goal/id/version, and places at most `sessions_per_week` per program.
  - Preserved sessions count toward the total, so a replan continues the program order.
  - A reviewed variant is treated as an alternative to its selected base.
  - Every session the planner cannot place goes into `PlanContent.unscheduled` with a concrete reason. The week page shows it, for example "1 session unscheduled: no free slot ≥45 min with court access".
  - Rules version is 1.1.0. No migration was needed. ADR `docs/adr/0007-multi-session-programs.md`.
- **Existing invariants unchanged:** duration, location, equipment, court, partners, overlap, recovery and match checks. Pre-existing tests were not modified.
- **Progress honesty:** progression cannot trigger in own-program mode, because there are no reviewed variants. The condition was left unchanged on purpose: enabling it would be app-authored physical guidance. The progress page, the week page and the proposal reason now say that the adjustment only keeps the program as written or holds it.
- **Final checks:**
  - `make check` exit 0: ruff pass, 52 files formatted, mypy 25 files, **81 passed**.
  - `make test-browser` exit 0: **5 passed**. This includes the new 390px multi-session flow.
  - `scripts/verify_distribution.py --mode source` passed.
  - Outputs are in `evidence/VC-P3/green-check.txt` and `evidence/VC-P3/green-browser.txt`.

## Intentionally not done

- **VC-P5** (French UI, LAN/phone access, login throttling) was not claimed. It is blocked on a human gate.
- The review's VC-P1 items outside this assignment were not changed. Those are the venture score, the stage label (scope.stage still shows `discovery` while the review says `problem_validation`), and linking the R006 request.
- VC-P2 (the demand question) and VC-P6 (consolidation under Volley Match) need operator input.
- No hosting, accounts, spend or messages.
- Sessions of one program share its duration and resources. There are no per-session requirements.

## Remaining human gates

1. The demand question (`demand_gate`): does the operator, or do at least two adults in the group, follow a written program of 2+ sessions a week and want to track it for two weeks? Yes → narrowed own-program trial. No → STOP and hold as a Volley Match feature.
2. VC-P5 additionally needs explicit approval for private phone access or hosting.

## Feedback filed (all `recorded_for_review`)

- `23905972-de74-433a-a562-10ef6060f2ff` (friction): adding an edge to a blocked item flags needs_review and appends the whole revision rationale. A second `keep` revision was needed.
- `6968bab5-7d86-49fa-a065-e73ec71f1263` (friction): evidence that was recorded and cited in an accepted result still appears as "Unreviewed evidence changes" in resume (7c4c5336, 55d4c5e2).
- Also committed: the reviewer's four outbox entries (`255b15be…`, `5bed744e…`, `63d588ac…`, `a5a1a905…`) with their receipts.

## Final state

- `git log -1`: `6ed83edb249ca951a64b8134a28c978f3feac5bd fix(planner): schedule every weekly session of a program or report it`
- `origin/main`: `6ed83edb249ca951a64b8134a28c978f3feac5bd` (fetched after push). Working tree clean (tracked and untracked). `.foundry/runs/` is gitignored and holds the inputs and outputs.
