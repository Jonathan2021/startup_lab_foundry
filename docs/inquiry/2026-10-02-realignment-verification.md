# Realignment verification

- Record: FOUNDRY-VERIFY-20261002-001:r1
- Date: 2026-10-02
- Attribution: agent-owned repository/operation checks; no learner-slice review

## Executed checks

| Command / check | Observed result |
|---|---|
| `make bootstrap` | PASS; frozen Foundry environment checked, 24 packages |
| Pinned `workflow-lint` | PASS |
| Ruff over Foundry and root tests | PASS after correcting one overlong relabelled comment |
| Foundry mypy | PASS; 10 source files |
| Repository source-document check | 1 passed; four preserved supplied files retain exact hashes |
| Foundry fast product suite | 28 passed, 1 expected skip: standalone PostgreSQL integration requires an explicit database URL |
| Container acceptance | **2 passed, 2 failed**; both failures could not fetch the pinned `astral-sh/uv` image authorization token from GHCR (HTTP 403) |
| `make test-ci` after full-check interruption | 12 passed |
| `make test-slice` | 9 passed; CLI support only, learner measurements/review still required |
| `make check-evalops-scaffold` | 1 package regression passed; Ruff and mypy passed (9 source files) |
| `make test-evalops-case-study` | Expected nonzero exit; 12 failures and 2 passes in preserved incomplete contracts |
| Real Foundry CLI operation | All 29 invocations succeeded; 3 ventures reconstructed; IDs/links and source hashes checked; SQLite integrity `ok` |
| Workbook/source preservation and local documentation links | Checked; see scope below |
| `git diff --check` in root and all three submodules | PASS |

`make check` therefore **did not pass overall**: it stopped at the external GHCR
403 during container acceptance. Remaining independent CI and active support
checks were run separately. No failing test was weakened or skipped to claim a
green full run. Retry `make test-container` when registry access works; it still
needs to succeed for a complete current regression result. The two passing
container tests do not substitute for the image/runtime and lifecycle checks.

The root check wiring now excludes only the explicitly deferred EvalOps case.
Its failures remain visible under their named target. Existing accepted Foundry
regressions, container checks and delivery checks remain in the default suite.
New `.local/` state is excluded from Git and Docker build context.

## Integrity and limits

The workbook remains at its original SHA-256:
`ebc5028a27aaed5c574da0355a1a7f1dc361c35493106b77d013b645ba7339e4`.
The portfolio screen retains 238 unique IDs/rows. New current-guidance local links
resolve; original source-document links that predate the monorepo are retained
as source history. Completed learning reviews and unrelated working-tree edits
were not overwritten. Old planning snapshots and the unfinished Slice 005 remain
available with explicit superseded status.

No customer interview, market-size measurement, willingness-to-pay test, source
recovery benchmark or Hindsight runtime test was performed. No learner task was
marked complete, no future slice beyond the replacement 005 was prepared, and
no commit/push, publication, paid provider call or cloud provisioning occurred.

The [operation record](2026-10-02-foundry-operation.md) and
[portable JSON](2026-10-02-foundry-records.json) retain real planning evidence.
The [verification manifest](2026-10-02-realignment-manifest.json) records effective
code/configuration and guidance hashes alongside the unchanged Git baselines.
The separate verification exercise does not establish product-market fit or
independent learner authorship.
