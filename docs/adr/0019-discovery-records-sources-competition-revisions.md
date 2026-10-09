# ADR 0019 — Discovery records: sources, competition, revisions and cohorts

Status: accepted, 2026-10-09.

## Context

On 2026-10-09 a discovery loop over a user-supplied transcript
(`idea_queue/agentic_stack_ideas.md`) created nine candidate ideas (AS01–AS09)
and immediately hit gaps in the public CLI and console:

1. A local document or URL could not be registered as a source and linked to
   ideas. Only `source list` existed; `PortfolioService.record_source` had no
   CLI/HTTP caller and accepted only an HTTP(S) "checked claim".
2. `MarketActor` and `IdeaMarketActor` tables existed but nothing created, listed
   or displayed them, so competition research could only be pasted into evidence.
3. `IdeaRevision` already had narrowing/pivot, customer, business model, MVP
   scope/weeks and validation test columns, but there was no `idea revise`.
   Narrowing an idea required creating a new idea.
4. Only `derived_from` relations could be recorded (via `--parent-id`);
   `combined_with`, `duplicates` and `pivots_from` merges were invisible.
5. Ideas from one source could not be compared side by side with per-criterion
   scores; `score rank` ranks the whole portfolio (238+ ideas) and the idea list
   could not be filtered by source.
6. `idea create` could not set origin or attach a source at creation.

All six use existing domain tables; the friction was the missing interface.

## Decision

Add `discovery_records.py`, a small service over the existing tables, with thin
CLI (`source register|show`, `market-actor register|list|show`, `idea revise|
relate|link-source|link-actor|compare`, `idea create --input`, `idea list
--source-id`) and console adapters (`/ideas/compare`, `/api/ideas/compare`,
`/ideas?source_id=`, idea-page Competition/Related/Revisions sections).

- **Sources** are content-addressed. A local file is hashed (never executed or
  interpreted) and stored as `file://…#sha256=DIGEST`; a URL keeps its locator
  and an optional supplied digest. Identity is a stable UUID over kind, stored
  locator and digest, so re-registration is idempotent and a changed file becomes
  a new record with history retained. Links are idempotent per idea/source/role.
  `record_source` keeps its claim-shaped behavior for existing scripts.
- **Market actors** have a stable identity over normalized name and website.
  A same-name actor with a different website is a conflict, not a silent merge.
  Links attach to the idea's **current revision** and carry `checked_on` and
  supporting `source_ids` in two nullable columns (additive migration
  `b10261009001`). A changed observation updates the link and appends an
  AuditEvent containing the previous and new values.
- **Revisions** are append-only. Omitted fields carry over, an empty optional
  field clears it, `change_reason`/`authored_by` are required and an optional
  `expected_revision_id` rejects stale writers. Competition links are copied by
  default. Assessments stay on the revision they judged and are labelled with its
  number; comparisons flag a score from an earlier revision as `stale_revision`.
  A revision without any changed field is rejected. Promotion reuses a venture
  opened from an earlier revision of the same idea, and the original workbook
  import is not repeated onto a later revision.
- **Relations** are explicit, rationale-bearing and idempotent per
  source/target/kind; self-relations and unknown ideas are rejected. The existing
  `parents` output is kept for compatibility alongside new bidirectional
  `relations`.
- **Comparison** uses the latest assessment of each current revision on one
  scorecard, falls back to the latest earlier-revision assessment (flagged), and
  reports missing assessments and factors as unknown rather than inferring them.

The agent schema registry is unchanged: adding names would bump the public
contract revision shared with the repository bridge. The input shapes are
documented in DEVELOPMENT.md ("Discovery records (October 9)") and validated by
Pydantic models with `extra="forbid"`.

## Consequences

Discovery can be recorded without workarounds, and each AS-style cohort can be
filtered by its source and compared. Portfolio list scores follow the current
revision, so a revised idea shows "Not scored" until reassessed; this is
intended. One migration adds two nullable columns; no data is rewritten. No
provider, network fetch, crawler or freshness guarantee is introduced: a URL
digest is only what the operator supplied. Market-actor links are mutable per
revision (with audit history), unlike immutable revisions and assessments.

## Revisit conditions

- Agents repeatedly need these inputs in the public `agent schema` registry, or
  an HTTP mutation API for them, during real discovery work.
- Actor observations need independent versioning beyond the audit trail (for
  example, several dated checks per actor kept side by side).
- Cohorts larger than 20 ideas, or comparisons across scorecards, become a real
  recurring need.
- Source capture needs stored content snapshots rather than digests.
