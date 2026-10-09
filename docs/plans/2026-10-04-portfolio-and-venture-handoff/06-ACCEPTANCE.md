# Acceptance and final handoff

Each task must leave working behavior or explicit research results, not just a
new plan. Use existing source boundaries and temporary databases. Root/foundry
repositories are already dirty; preserve unrelated changes. No commit or push.

## Shared implementation checks

From `/home/jonathan/startup_lab`:

```bash
.venv/bin/ruff check foundry/src foundry/tests tests
.venv/bin/mypy foundry/src
.venv/bin/pytest -q tests/repository foundry/tests/unit foundry/tests/integration foundry/tests/acceptance/test_cli_workspace.py foundry/tests/contract
```

Run relevant focused tests during a task, then this suite after integrated changes.
October 2's baseline was 53 passed/one PostgreSQL skip; new functionality needs
meaningful additional coverage. Do not delete checks to retain that count. Use
`make workflow-lint` if workflows change; container acceptance when packaging or
migration/deployment concerns warrant it. GHCR 403 is a recorded environment failure,
not permission to repin images or claim deployment passed. Don't retry it endlessly.

For schema changes: fresh SQLite upgrade, upgrade from a backed-up existing schema
with records, foreign-key integrity and Alembic model/schema parity. Destructive
round trips use disposable stores only. PostgreSQL-specific behavior is verified
only with a disposable configured database; keep SQL portable meanwhile. Update
DBML and contract expectations for genuinely new tables, not to hide lost data.

For UI changes: run the local console and exercise real browser flows on disposable
data for fake mutations. Verify desktop/mobile, forms, preserved filters, empty
states, feedback/errors, XSS escaping and Host/Origin/token protections. Keep output
and score/status labels readable. No deployment is part of this work.

For packaging: wheel contains templates/static assets/migrations and works outside
the source checkout. For database adoption/backfills: backup first; atomic,
idempotent, no changed source files or erased original assessments/decisions.
Never bake today's expected 250 ideas into permanent application tests.

## Deliverable contract per task

| Task | Observable completion |
|---|---|
| T00 | Answer evidence imported once, new replies preserved, old holds reviewed, independent tasks identified |
| T01 | 238 original totals match; all 12 dimensions visible through service/CLI; missing/new scores honest; source relocation deduplicated |
| T02 | Reviewed status history and specific next action/blocker persist; prototype and business uncertainty can coexist |
| T03 | Score/stage/maturity/disposition/blocker filters and stable sorting work across pages and restarts |
| T04 | Supplied GPX compared locally with uncertainty; ETA versus geometry separated; next planning test is concrete |
| T05 | Coopain checkpoint stored and browsable through reusable existing-project intake; capability and business gaps differentiated |
| T06 | Both sports jobs compared against closer incumbents; user test or exact remaining access gate; shared sources reused |
| T07 | Editable draft/export/outcome flow works; four N003 variants and sample prepared; no messages sent |
| T08 | Built-in help explains actual implemented UI and flows with working links |
| T09 | Bounded physical-data screen concluded; work-sample review package ready or real feedback recorded |
| T10 | Targeted updated assessments and dated portfolio recommendation, surviving gaps explicit, data backed up, tests/results retained |

## Research quality checks

Every material conclusion should resolve to: question, source/date, whether it was
observed or reported, limits, assessment and next decision. A vendor page establishes
a claim; a controlled trial establishes behavior within its conditions; a friend
saying “nice” is weaker than repeated voluntary use. Don't collapse those labels.

A good outcome may be use existing software, a small internal/personal utility,
a contributor patch, a narrow paid service, a held project or a stopped premise.
Record which outcome was chosen and why. High priority does not force a build,
and limited monetization does not erase the user's stated utility interest.

Preserve original workbook/ranking and campaign artifacts. Append changed scoped
ideas/assessments with parent/revision links. Recheck source relevance before reuse:
previous general sports administration references don't settle rotating-team balance;
job application assistants don't settle an open referral-bonus network.

T10 should reassess P023, P103, P046 and N008/D001 first, then directly affected
related ideas. Do not rescore all 250 with invented data just to fill the UI. New
combinations need an explicit recurring job and parent/source links. Score tuning
must say which observation changed which judgment or weight.

## Budget and resumption discipline

Work in a small sequential task. Reuse this plan and saved research rather than
rebuilding context. For initial competitor screening, three close comparators per
job and one useful baseline attempt are sufficient; failure can justify one
corrected retry, not an indefinite installation spiral. These are planning bounds,
not hard caps on fixing a discovered production bug. Record justified deviations.

Do not ask the user questions already answered in INBOX. New request files should
state why the answer matters, what work proceeds meanwhile, and accept “unknown”.
Keep real addresses/GPX/CVs/mailbox secrets out of broadly tracked artifacts.
No payment, real outreach, publication or account provisioning without exact approval.
No local model download/training or changes to curriculum.

## Final report template for the executing model

- Completed task/subtask and user-visible behavior.
- Evidence/decision/checkpoint/assessment IDs and relevant files.
- Tests actually run, passed/skipped/failed, and any untested boundary.
- Updated current score/status with why it changed; what remains uncertain.
- Any required human response file and the independent next task.
- No claim that a venture is commercially viable without supporting adoption/buyer evidence.

Update `STATE.md` after each task. At T10, create a dated report and fresh backup,
link them from current direction, and leave prior reports as historical records.
Record effective code/config/input digests for reproducibility. State clearly which
features remain draft-only and which investigations need actual human participation.
