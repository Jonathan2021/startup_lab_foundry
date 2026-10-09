# MVP release readiness — 2026-10-08

Ride Options and Coopain work as bounded local previews in fresh source copies.
Volley Match's application checks pass, but its documented demo setup fails.
**None of the three is yet a committed release with verified GitHub CI for the
current MVP.** Existing accepted Foundry checkpoints prove recorded coordination
and claimed local completion; they do not replace independent release checks.

The user requested review and new handoffs. This audit made no application changes,
commits, pushes, remote repository creations or deployments. Earlier handoffs
explicitly prohibited commits/pushes. Git delivery is a new phase, authorized only
if the user sends the supplied continuation prompt.

## Findings and fresh verification

| Repository | Current verification | Blocking delivery/readiness gaps |
| --- | --- | --- |
| Ride Options | Ruff, strict mypy, 31 core tests; clean install/migration; recorded browser; supported Node/npm frontend rebuild | Unborn Git branch, no remote, no Actions workflow. Complete first-use/regional bootstrap documentation and certify the final distribution/commit. |
| Volley Match | Ruff, strict mypy, 54 core tests; browser flow at 1280/390px | Fresh README `make seed-demo` fails with naive datetime validation. No commits/remote; local workflow covers only core checks. V05 wheel evidence predates V06 repairs. |
| Coopain | Clean locked install/migration/synthetic seed; direct pytest 208 passed, 91.61% coverage, every measured file >=60%; 14 web tests, types/lint/build; desktop/390px browser | Test runner can mask pytest failure. MVP uncommitted; upstream cleanup must be reconciled. Backend-only CI misses frontend/launcher. Primary READMEs contradict current local guide. |

### Volley Match seed defect

In a disposable source copy with no prior application state:

```bash
cp .env.example .env
make install migrate seed-demo
```

`scripts/seed_demo.py:64` passes `session.start_at` into `MatchInput.played_at` after
SQLite persistence/refresh has produced a naive datetime. Validation reports
`Specify a UTC offset for the session time`; make exits 2. Core and browser fixtures
do not cover this actual quickstart. Evidence: `volley-match-clean-setup.txt`.
V07 must repair this without weakening timezone or synthetic-data guards and add
a real command-level startup regression.

### Coopain CI false-success defect

`backend/run_tests.sh` runs pytest and then a separate coverage checker without
propagating pytest's failure. A copied runner with a synthetic pytest exit 7 and
a passing synthetic coverage JSON returns 0. No product test was modified to
produce this result. Evidence: `coopain-runner-exit-reproduction.txt`.

This can hide actual test failures despite sufficient coverage; stale coverage
can also survive a failed invocation. J06 must preserve test exit status, require
fresh coverage evidence, and keep total/per-file gates. Its implicit Conda selection
also needs an explicit interpreter contract so the chosen lock actually applies.

### GitHub provenance

Ride Options and Volley Match have no HEAD and no remotes. Only Coopain was found
when listing matching repository names under authenticated account Jonathan2021.

Coopain local HEAD is `aa382779b79951f843f37b8080f6f0972efe7e3c`, with current MVP
changes uncommitted. Read-only GitHub API reports private remote main
`4f6899287dea2c10236d6293d77d6240587b6703`: cleanup commit `8b2cea38` and PR #1 merge
are ahead of local HEAD. The cleanup overlaps catalog/domain tests and docs and
retires old OpenAPI tooling. Existing cleanup worktree and all local work must be
preserved while integrating the MVP.

The latest green run inspected is
[Backend CI 37444386886](https://github.com/Jonathan2021/coopain/actions/runs/37444386886),
on `4f689928`. It is not evidence for uncommitted MVP changes. Current local workflow
is itself modified and still only covers backend paths. See `coopain-github-actions.json`,
`coopain-github-repo.json`, and `coopain-upstream-compare.json`.

### Documentation and artifact readiness

- Ride has useful architecture/release/recovery docs. Add a user walkthrough and
  a complete regional bootstrap. Its downloader always names the extract
  `andorra.osm.pbf`, whereas the Auvergne prepare example expects a different name.
  This is a static code/document mismatch, not a fresh engine-download experiment.
- Volley has substantial release/privacy/recovery instructions. Preserve these;
  repair and cover the actual README seed command, add an organizer/participant
  walkthrough, and rebuild/certify the current distribution.
- Coopain's `LOCAL_RUN.md` is detailed and its launcher works independently.
  Root/backend/frontend READMEs still lead with older commands and assumptions.
  Promote the current guide, align prerequisites and feature statements, and
  distinguish historical/multi-provider/mobile paths from the certified web MVP.
- All handoffs require code-interface/invariant documentation, reproducible locks,
  current dependency findings, secret/data hygiene, migration/recovery checks and
  source-linked release evidence. They do not require cosmetic rewrites or invented
  licenses. CI must cover the final pushed SHA, not merely exist as a YAML file.

## Scope and interpretation of tests

`PROTOCOL.md` records bounded criteria before runs. `*-baseline.json` records
original Git state and source hashes. Independent copies were made from candidate
source files into disposable directories, excluding existing application state,
environments and Foundry configuration. Installs used locked dependencies.

The first Coopain web check lacked the committed generated OpenAPI file because
the audit copy intentionally omitted generated directories. Regenerating it from
the current backend restored all 14 passes. This is an audit setup issue, not a
product defect. Likewise the initial nonexistent `.venv-mvp` invocation and invalid
launcher port flags were corrected using a fresh environment and documented
environment variables. Their failed logs are retained without counting them as
application failures. Ride's first npm attempt used unsupported host tooling;
Node 22/npm 10 completed the documented rebuild successfully.

Coopain browser stdout records 2 passed in 1.2 minutes. The running tool session
and temporary directory were no longer available after the user's continuation;
the persisted stdout is the retained browser completion evidence, not an
independently retrieved process exit or JSON report. No disposable processes were
found at cleanup. No original application database/environment was changed.
`source-recheck.json` confirms captured Python/shell source hashes stayed unchanged.
The temporary copy was also unavailable for Ride's final asset byte comparison;
that check remains required for release rather than being inferred from an empty
directory traversal.

No fresh live GraphHopper/regional route run, installed-wheel test, PostgreSQL run,
or dependency-wide security audit was performed in this review. Earlier accepted
evidence is retained and distinguished from fresh checks. The release handoffs
require the checks relevant to their final changes. These results do not establish
road access, voluntary adoption, real-person privacy operations or commercial
viability. Ride's 16 unresolved generic restrictions and missing target-duration
options remain visible; Volley/Coopain's actual pilot gates remain unchanged.

## Foundry verification and next work

All three doctor reports verify bridge/contract **2026-10-07.2** and SHA-256
`1e0be09cd1b537864e0b04bbc2358932b1efba7c7a5d4abb4c0b9aff0e91703f`.
R06 (`5e0831c9-e7c5-5bc7-b1a5-c305a3b784f9`), V06
(`d66f428d-0fba-5cc1-abba-2991f4ee7991`) and J05
(`53e6474a-c469-5559-8de2-1f962dba33c1`) are accepted with complete context.
No implementation claim was active when the following unclaimed tasks were created:

| Package | Ready work | Handoff |
| --- | --- | --- |
| R07 | `42b34c32-fc4b-45dc-bd91-7f2456b3f767` | `ride-options/docs/mvp/READINESS_HANDOFF.md` |
| V07 | `3f666496-6be6-4d47-a304-7bc541f76795` | `volley-match/docs/mvp/READINESS_HANDOFF.md` |
| J06 | `118dc039-d6f6-408b-852e-8fd49b79101c` | `coopain/docs/mvp/READINESS_HANDOFF.md` |

The coordinator claimed Foundry audit work `1f29d43f-556a-4fde-bd44-1202f4098b4f`
and covered all 37 returned evidence arrivals in saved context
`bc2ecfd6-f620-5f1d-b581-7a64ca61f1f8`. Two positive reports arrived during the
audit continuation (Crous Queue and Volley Coach). The result coverage guard
correctly required reconciliation: both were fetched, and fresh complete context
`5e92bd71-af26-5b35-98fa-0641f32d0785` includes all 39 records. The initial result
is retained and explicitly superseded. The latest venture feedback reports confirm
useful doctor/map visibility and sequential checkpointing. Retain this positive
evidence. Previously reported superseded-result noise (`f6742d1d-c97a-446a-a457-d2cb7bd410c4`)
is visible but does not block current ownership; defer that UI/history improvement
to separate bounded Foundry work. Dependency-alert feedback (`30cd5b46-f68e-404a-8f23-ae5d96e7696e`)
already points to its own retained maintenance work. No new blocking Foundry defect
was observed; no platform upgrade is required for these release repairs.

`queued-work.json` contains creation receipts. `PROMPTS.md` contains the exact user
continuations, including explicit private Git delivery scope. They authorize no
deployment, public visibility, real sends or paid infrastructure. Final audit
result/resolution identifiers are recorded in `foundry-checkpoint.json`.
