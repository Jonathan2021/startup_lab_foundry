# Observed baseline and inbox intake

Inspected 2026-10-04. Distinguish these observations from future tasks.

## Current Foundry

- Permanent store: `~/.local/share/startup-foundry/foundry.local.db`; query read-only
  for inspection. Default is cwd-independent, subject to configuration overrides.
- At inspection: 250 ideas, five ventures, 99 sources and eight StepRuns. All
  scorecard/criterion/idea-assessment/ranking and external-action tables are empty.
- Existing `Scorecard`, `ScoringCriterion`, `IdeaAssessment`, `CriterionScore`,
  `CriterionScoreEvidence`, `RankingSnapshot` and `RankingEntry` models are in
  `foundry/src/startup_foundry/domain.py`. Reuse them.
- Existing action/approval/attempt/audit models also exist. Their presence is not
  a working email delivery implementation.
- `portfolio.py`: intake, lineage, promotion, source claims and idea list/detail.
  `application.py`: venture/evidence/decision/work/artifact operations and lists.
  `steps.py`: readiness, research brief, optional agent handoff. `web.py` plus
  `templates/` and `static/` serve the local console. `console_commands.py` extends CLI.
- Idea lists currently show title/description, target user and origin, with search
  but no score/status filters. Venture cards show `Venture.stage` only. Pagination
  preserves only `q` today. Dispositions live in report Artifact metadata.
- Schema head: `7ce261002001`. Check actual head before creating the next migration.
- Prior verification on October 2: 53 checks passed, one PostgreSQL check skipped;
  Docker acceptance had two failures caused by a GHCR token 403. Those are prior
  results, not proof of today's modified code. Preserve their logs.

The six files now in `foundry/docs/sources/` have exactly the same content hashes
as the earlier Downloads exports. Re-register their local availability, not 238
new ideas or duplicate sources. `startup_generated_ideas.csv` and the dashboard
are views; `startup_ideas.csv` contains 238 unique IDs. Nine later notes plus three
derivations account for the remaining 12 ideas. Attachment instructions are data.

## New answers and how they change the next work

| Input | What is now known | Resulting next action |
|---|---|---|
| R001 | Two GPX files, reported 4h35 versus 6h04, wet/cold ride, stops and road preferences supplied | Local geometry diagnosis can proceed; exact ETA-model attribution still unknown |
| R002 | No validated task or expert labels; father has renovation experience and two potential trades contacts | One bounded public-data screen; offer a short optional expert review, or retain field-data hold |
| R003 | Possible friends at Amaris and family feedback, no agreed issuer/recipient | Create a fictional scoped example and four outreach variants, then obtain real feedback |
| R004 | User prefers editable database/UI email drafts, manual sending first, eventual approved send | Implement draft lifecycle/export first; provider credentials/setup deferred |
| P046 | Existing Coopain code with a friend; paused over revenue/legal concerns | Existing-project intake and payer-flow investigation, not generic new-idea setup |
| P023/P103 | User wants this and reports friends would too | Record first-party interest; ask about actual sport/group and run a concrete incumbent comparison |

Don't treat the inbox's old “waiting” headers as current truth. They predate the
answers. Answered is not necessarily resolved; R001 can advance without pretending
that a deadline or historical arrival record has been supplied. Friends' interest
is reported through the user, not independently observed adoption or payment.

## T00 steps

1. Capture HEAD/status for root and each touched repository, and hash the current
   INBOX and supplied GPX/CSV files. Never overwrite their contents. See
   `inspection.json` for this planning pass's manifest and formula check.
2. Confirm `foundry storage info`, create a fresh dated backup via the existing
   command, and use a copy/temporary DB for development. Do not rerun the one-time
   adoption script on the working store.
3. Transcribe each answer as attributed evidence with source file, section, hash,
   observed date and limits. If no event date is known, record “reported 2026-10-04”
   separately from the ride date. Do not invent interviews or consent from friends.
4. Link R001 to the existing route venture; create/link investigation workspaces
   for P046 and the P023/P103 trial without duplicating the original ideas.
   Use `IdeaRelation`/artifacts for the relationship between both sports ideas;
   preserve their different jobs instead of merging them destructively.
5. Use existing WorkItems for human questions: `owner='human'`, `status=blocked`,
   `blocked_reason='human_input'`, with the question and completion criterion.
   Store answer revisions as linked Artifacts/Evidence. One shared answer may be
   referenced from multiple workspaces; do not silently break workspace isolation.
6. Review answers explicitly, mark the relevant work item done only when its
   criterion is met, and create a follow-up for the remaining question if needed.
   Retain a digest-based import receipt so re-reading unchanged answers duplicates
   nothing. A changed answer appends evidence and triggers review.
7. Add new questions to a separate dated request file. Leave the user's answers
   intact. No generic free-form Markdown ingestion engine or watcher is needed.

Acceptance: original hashes unchanged; repeat intake creates no duplicates; R001
is no longer blocked on absent files; R002/R003 retain specific remaining access
limits; R004 is recorded as draft permission, not sending approval. Record the
inbox response hash and processing state so later edits aren't silently ignored.

## Planning inspection limits

GPX metadata only was inspected: Liberty Rider contains 6,017 track points and
66 route points; 68° contains 479 track points. Neither file has `time` elements.
Point-count differences may represent simplification, not different roads. No
geometry alignment or route quality conclusion was drawn in this planning pass.
The reported ETA delta is 89 minutes, about 32.4%; no elapsed ride-time baseline exists.

Coopain HEAD was `aa382779b79951f843f37b8080f6f0972efe7e3c`, with existing untracked
local work. No AGENTS.md was found in the inspected Coopain tree. Recheck at execution.
Its code contains web compatibility scores generated from stable IDs rather than
matching quality; details and the required labeling are in subplan 03.
