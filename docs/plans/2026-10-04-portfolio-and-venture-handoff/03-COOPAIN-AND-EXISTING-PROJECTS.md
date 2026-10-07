# T05 existing project intake with Coopain

Goal: Foundry can join a project partway through, preserve useful work, identify
what is missing and propose the next justified step. P046/Coopain is the first
real case. Do not turn an asset audit into a rewrite of the friend's codebase.

## Observed starting point

Repository: `/home/jonathan/coopain`. HEAD at inspection:
`aa382779b79951f843f37b8080f6f0972efe7e3c`; existing untracked local files are present.
Read its applicable instructions again before execution. Root README is named
`README`, not `README.md`. Other useful files:

- `SYSTEM_GUIDE.md`, `backend/{README,PROGRESS,BEFORE_PROD,STRUCTURE_NOTES}.md`.
- `backend/DB_SCHEMA_MVP`, `backend/app/main.py`, `backend/app/api/routes/`.
- `backend/tests/conftest.py`, `backend/tests/test_match_pii_grants_flow.py`,
  `test_matches_snapshot.py`, `test_safety_api.py`, and `backend/run_tests.sh`.
- `frontend/README.md`, `frontend/apps/web/src/app/dashboard/page.tsx`,
  `frontend/apps/web/src/app/lib/utils.ts`, and web/mobile package manifests.
- `backend/generated/openapi.json` is an existing snapshot, not proof the current
  service was started or all listed endpoints work.

Docs describe a FastAPI/SQLAlchemy backend, candidate/referrer profiles, matching,
chat, access grants, documents and safety; Expo/Next.js frontends exist. Some
selected route/UI code confirms implementation presence, not end-to-end quality.
Docs identify minimal matching, no active Alembic migrations and placeholder push.
No Coopain tests or app runtime were executed in the planning pass.

Concrete inspection finding: `scoreFromStableId` in web `lib/utils.ts` hashes an ID
and returns 60–100; dashboard calls it for compatibility. These are placeholder
values, not suitability scores. Hide/label them before any observed-user test that
could mistake them for predictions. Confirm behavior in the running UI first;
log any code fix as a separate Coopain task, not an unannounced Foundry change.

## T05a local asset and gap review

1. Record repo path, commit, dirty state, selected non-secret file digests, stack,
   product intent, known participants/ownership as reported, and existing decisions.
   Do not read `.env`, tokens, real user databases, CVs or private messages. Do not
   copy the repo into Foundry or make it a Foundry runtime dependency/submodule.
2. Build a capability matrix: feature; documented; code present; last test result;
   observed workflow; limitations. Use unknown for missing evidence, not done/zero.
3. Inspect test setup and integration seams before running. Use Coopain's separate
   environment and a disposable store, with mail/storage/provider calls mocked.
   Do not install its older dependencies into Foundry's environment. The test
   fixture uses in-memory SQLite and a fake email client; verify other tests too.
4. Run a bounded representative path: candidate/referrer → job/preference → mutual
   match → scoped access → message → revoke/block. Retain exact command/version,
   failures and whether behavior came from a mock. No real SMTP/S3/auth provider.
5. Inspect the existing web flow; distinguish product UI from backend dev UI.
   Never run schema-reset seed commands against a retained database. Existing
   `run_tests.sh` writes coverage artifacts: redirect/preserve prior user artifacts
   or use a disposable checkout; do not clobber untracked work.
6. Gap matrix: product problem; user access; payer; legal/contract; implementation;
   UX; delivery; operations. Code maturity cannot fill a commercial evidence gap.

Stop after a reproducible baseline or one diagnosed environment blocker. Do not
spend a whole task repairing unrelated dependencies or implementing every TODO.
The shortest next experiment may be a mock/concierge flow using existing code.

## T05b actual Foundry capability

Implement `existing-project intake` over the existing venture/artifact/evidence
model. Prefer a versioned JSON intake manifest stored as an Artifact over another
repo-management framework. Schema `existing-project/v1` should include:

- venture/source idea IDs; local repository references and optional remote URL;
- inspected HEAD/dirty state, artifact digests and observed timestamps;
- description, participants as reported, product maturity and reason paused;
- capability matrix with evidence locators and verification level;
- prior decisions/constraints, available users/data, gap list and next bounded test;
- ownership/license/access questions, with unknown values retained.

Create/link `v-coopain` to P046 idempotently. Reuse existing `link_venture_idea` and
promotion behavior without declaring its business validated. Provide CLI import
from a validated manifest and an “Existing project” UI entry path: select idea or
create venture, describe current state, add artifact/repo references, save review.
Show the checkpoint and next action on the venture detail/list maturity field.

The UI stores references; it must not gain an arbitrary filesystem browser,
recursive upload, remote URL fetch or “run this repo” endpoint. Code inspection is
an explicit local operator task. Revise by appending a new manifest/artifact; show
what changed. Supplied docs/test claims remain distinguishable from verified runs.
A returned project should be resumable using that checkpoint and its evidence links.

Acceptance: repeat the same manifest creates no duplicate venture/artifacts;
changed manifest produces new history; missing path does not erase prior records;
reference-only intake cannot execute shell/read arbitrary files through HTTP;
Coopain remains independently testable; incomplete business work stays visible.
Use Agent EvalOps as a second existing-project intake fixture only if it helps
verify generic fields; do not reactivate its implementation backlog.

## T05c business model investigation

The precise legal distinction matters. French placement services may be operated
for profit under [L5321-1](https://code.travail.gouv.fr/code-du-travail/l5321-1).
[L5321-3](https://code.travail.gouv.fr/code-du-travail/l5321-3) generally prohibits
requiring direct or indirect remuneration from jobseekers for placement services,
with specified exceptions. These official pages were read on 2026-10-04. This is
a constraint to analyze, not a blanket ban on all recruiting revenue or clearance
of a proposed subscription. Have a qualified adviser review the selected money
flow before an actual paid launch; do not charge candidates as an experiment.

Create a table for each candidate model: payer → recipient → service → trigger →
value → cost → contract/policy dependency → unknown legal issue → next falsifier.
Investigate at most three alternatives initially:

1. Employer-paid niche introduction/service with candidates free. Test employer
   acceptance, candidate quality and referral-policy authorization first.
2. Employer-funded referral operations/integration. Compare incumbent tooling and
   implementation burden; an existing backend does not prove a differentiated offer.
3. Community/alumni/association-sponsored access or a bounded managed program.
   Test who actually owns a budget and repeated problem; sponsorship is a hypothesis.

Bonus sharing, a fee taken from the referrer's payout, or candidate “premium
visibility” are not assumed loopholes. Analyze employer eligibility, authenticity
of endorsements, payment timing, tax/contract treatment, confidentiality, consent,
and data use for the exact chosen flow. Separate legal constraints from terms of
employer referral programs. Don't scrape job sites or collect CVs without need.

Use closer comparators before broad job-application assistants:
[Keycoopt](https://keycoopt.com/en/solution/) documents employee referral and HR
integration; [Basile](https://basile.io/) documents referral portals and ATS
integration. These are vendor capability claims, not independent outcomes.
Add one verified open referral-network comparator only if it matches strangers
seeking referrals and bonus sharing; do not invent a comparable product.

Deliver a retain/adapt/defer recommendation with one target segment and the next
specific buyer conversation/demo. Draft a 15-minute employer/referrer discussion,
not a sales claim. Ask the user/friend about existing user tests, why paused,
rights to reuse/publish and reachable employers only when not in retained records.
Do not ask them to re-describe code you can inspect. Existing code reduces some
engineering work; it does not justify sunk-cost continuation or erase competition.
