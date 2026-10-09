# ADR 0020 — Truthful venture state, open requests and repository drift

Status: accepted, 2026-10-09. Agent contract and repository bridge `2026-10-09.1`.

## Context

On 2026-10-09 six independent review agents audited six ventures through the CLI
and console and filed 26 feedback records in `v-foundry` (evidence 4bb18891,
96a1fca2, 3cd42086, 04d78c36, 94e6a84f, f4b438fa, 8aa87b96, 4ec9d645, c908eedb,
39104eb6, cab3dc58, 51c2624b, 08975103, 9102be35, 88e3370f, 9e59240b, c0055fd2,
6fe7c685, 905f07ba, f7ec997d; the discovery loop added a212add8, 18f00afc,
65daf95c; implementation agents later added f2beefe2, 7d5632c3 and 6968bab5).
Each theme was observed in several ventures:

1. **Contradictory venture state.** The header showed the creation-time
   `venture.stage` ("Discovery") while the current review said
   `solution_validation`; maturity said "Concept" after a CI-verified MVP; the
   300-character next action was printed twice; a score flagged "predates current
   scope" offered no reassessment; a cancelled initial review was offered as
   startable; history rows showed only type, UUID and actor.
2. **Superseded legacy work as permanent "needs review".** Items paused with
   `changed_context` and a "Superseded as an executable priority…" rationale were
   the only `needs_review` entries and raised the console banner, with no one-step
   close.
3. **A stale fusion proposal shown as current focus** (`91fe8686` stayed
   `proposed` after accepted decision `a38e9141` declared it historical lineage).
4. **Open human-request files were invisible** (R006/R011/R013/R015): the venture
   page said "No open human requests", owner agent, no blocker.
5. **Repository drift was invisible**: GitHub `main` moved past the SHA recorded in
   the last accepted result in every venture, and nothing reported it.
6. **CLI inconsistency**: read commands took `--id`, `--venture-id` or
   `--workspace-id` arbitrarily; INFO logs interleaved with JSON on merged
   streams; the Crous Queue venture is a raw UUID, so slug URLs failed.
7. **Discovery loop (F05)**: promotion did not carry an idea's sources,
   competition or evidence into the venture; discovery input schemas were not
   published by `agent schema`; `score rank` returned only counts.

Implementation agents additionally reported that an edge-only map revision
flagged an unchanged work item for review, that a routine work-scoped result
silently replaced a HOLD next action, and that evidence cited by an accepted
result stayed in "Unreviewed evidence changes".

## Decision

**Promotion provenance (F05).** The venture overview shows the source idea's
sources (role/note), current competition and evidence count/IDs. One explicit
resolution rule (`decision_maps.reference_allowed`) lets a venture's map, context
and results cite *evidence* from its source idea's workspace; every other
cross-workspace reference is still rejected. The `agent schema` registry adds
`source`, `market_actor_link`, `idea_revision`, `idea_relation`, `idea_create`
(and `close`, below), so the public contract revision becomes `2026-10-09.1` in
the CLI, both bridge copies and the example manifest. `score rank` adds
`ranked_entries` and `excluded_entries` with a reason
(`partial_total`, `assessed_on_earlier_revision_only`,
`not_assessed_on_scorecard`); count fields are unchanged.

**One derived venture state (F07).** `venture_state.venture_state()` derives
disposition, investigation stage, product maturity, a headline, the selected
score status (`current`/`predates_scope`/`not_scored`), the next action with its
work, and open gates (open human requests, human/access/setup-blocked work, stale
proposals). The venture header, venture list, Today cards and `agent resume`
(`venture_state`) all use it. We chose **display-only** for `Venture.stage`: it
is not synced on `review append`; it is shown as "Lifecycle (recorded)" only when
it differs from the lifecycle the review implies. Nothing is rewritten. The next
action is rendered once (the button label no longer repeats it). A score that
predates the current scope shows a **Reassess** link to the score form. Cancelled
or done initial reviews never show handoff/start actions.

**Superseded work.** Blocked work whose recorded blocker text starts with
"Superseded" is listed under `superseded` ("Superseded (close or revise)") and is
excluded from `needs_review` and the console banner. `venture-work close
--workspace-id WS --input {work_id, expected_version, actor, rationale}` (schema
`close`; console button) cancels one exact unclaimed item through the existing map
`cancel` work treatment, retains a receipt artifact and a `work_closed` audit
event, and is repeat-safe. Claimed work must first be released by its owner.

**Stale proposals.** A still-`proposed` fusion is labelled "Stale — needs
resolution" when its result venture already exists or a participant workspace has
an accepted decision, made after the proposal, that names it (full or 8-character
ID) as superseded/historical/lineage. It is never the venture's current focus. Its
state and history are unchanged; a human still resolves it.

**History, attention and results.** History rows show the record summary (first
120 characters) and a relative date. An added/removed relationship flags an
unchanged work node only when it changes that work's `depends_on` prerequisites.
A work-scoped result keeps a HOLD (or venture-narrowed) next action; only
`decision_scope: venture` changes venture direction. Acceptance effects and
`result preview` list `review_changes` (field, before, after). Evidence an
accepted result cites (finding refs, assessment evidence) is marked reviewed, and
evidence cited by an accepted decision after its last change leaves the
unreviewed list.

**Open human requests (F08).** `input sync --requests-directory PATH --preview |
--apply [--mapping FILE]` parses `#`/`##` headings beginning with an R-number in
`*.md` files (regular UTF-8 files ≤ 100 KB, no symlinks, at most 200 files).
Ventures are matched by an optional `request-ventures.json` (`files`, `requests`,
`ignore`), explicit venture IDs/aliases in the section, venture titles in the
heading, and `v-slug` names in the file name. Unmatched sections are reported, not
stored. A section is `answered` when its latest `Response:`/`My answer:` block has
a non-template answer. Records keep the R-number unless another file or occurrence
already owns it (then `R006-<hash>`); an existing campaign request with the same
file is only linked to additional ventures. Status is never changed and answers
are never consumed: intake remains the reviewed flow. The venture page, Today and
`agent resume` (`human_requests`) list them, with `/requests/{id}/source`.

**Drift and CLI consistency (F09).** `agent resume` reports `latest_delivery`
(newest `main=<sha>` or `sha <sha>` in accepted results or evidence; convention
`Delivery: main=<sha> ci=<run id>`). The bridge's `resume`, `start` and `doctor`
add a `repository` block with local `HEAD`, `refs/remotes/origin/main` (local
metadata only; never fetches) and that delivery, and warn on stderr when the
repository moved past it. `doctor` now reads the store through `agent resume`
unless `--offline` (the ADR-0017 database-free check). The bridge passes all
arguments after `cli` (including `--help`) to Foundry and may select by
`venture_id`/alias when `workspace_id` is absent. Read commands accept `--id`
resolving a venture ID, alias, workspace ID/key or idea ID; existing flags keep
working. Additive migration `b10261009002` adds a nullable unique `ventures.alias`
(`^v-[a-z0-9-]{2,60}$`), set with `venture alias` (version-checked, artifact and
audit). Console `GET /ventures/{alias}…` and `/api/ventures/{alias}…` redirect
(307) to the canonical ID. JSON stdout always ends with one newline; the default
log level is WARNING, INFO only with `--debug`; exit codes are unchanged.

## Consequences

The same derived state appears everywhere and contradictions are visible rather
than silently resolved. Per-card derivation adds a few queries per listed venture;
lists are bounded (≤ 500, defaults 30/6). Proposal staleness uses a textual
convention in decision text; a decision that does not name the proposal leaves it
pending. Request-file matching is heuristic but explicit and previewable; the
mapping file corrects or ignores sections (for example index files such as
`INBOX.md`). Delivery detection depends on agents following the documented
convention. Copies of the bridge and manifests in venture repositories must be
updated to `2026-10-09.1` (doctor reports the mismatch). No provider, network,
fetch, automatic Git action, answer ingestion or proposal resolution is added.

## Revisit

- Sync `Venture.stage` from reviews if operators keep reading the recorded
  lifecycle as current despite the label.
- Add a structured proposal reference on decisions if the textual staleness
  convention misses real cases.
- Replace heuristic request matching with explicit front matter if mappings grow.
- Record delivery as a typed field if the `Delivery:` convention is not followed.
- Revisit `doctor` reading the store if store outages make it slow or noisy.
