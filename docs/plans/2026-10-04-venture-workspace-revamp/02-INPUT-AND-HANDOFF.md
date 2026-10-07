# Human input and manual agent pickup

Implement V01a/V01b and the V03 forms. R006 must be answerable from either sports
workspace and recognized once. The current file workflow remains supported.

## The visible lifecycle

```text
Question waiting for you
  -> file edit detected, or UI answer submitted
  -> durable answer revision saved
  -> waiting for agent review
  -> agent reviewing
  -> reviewed: next work ready / needs clarification / deferred
  -> next work explicitly claimed and completed, or still blocked
```

An edited file is only detected when scanned. No watcher, agent process or
notification delivery is implied. GET pages may inspect known request sources
read-only and show **Unsynced answer detected**. **Sync file answers** is a POST
that creates receipts and review work. UI **Submit answer** performs that same
receipt/queue transaction directly. Neither action invokes a model.

Show a persistent explanation: **Answers wait here until an agent session reviews
them. Copy the handoff to continue in your coding agent.** A “queued” label means
durably pending, not that a worker is running. The current Codex conversation
already supplied the new answers to this planner; the running app has not consumed
them, as confirmed in the baseline.

## Request data and ownership

Add two typed tables; keep large immutable payloads in existing Artifacts:

| Proposed table | Fields and invariants |
|---|---|
| `HumanRequest` | Stable ID such as R006; owning workspace FK; title/question; request definition revision; current response Artifact FK nullable; latest review Artifact FK nullable; status; relative file path/section nullable; source diagnostics; optimistic version |
| `HumanRequestTarget` | Request FK, affected workspace FK, existing blocked work-item FK nullable; unique request+workspace; work item must belong to that target workspace; all targets in the owning portfolio |

Store a `human-request/v1` definition Artifact on creation/question revision.
Store `human-response/v1` and `human-response-review/v1` Artifacts in the request's
owning workspace. The table's pointers must reference the correct schema/request
and owner. These are typed validated payloads, not arbitrary metadata conventions
spread through templates. Put parsing, validation and transactions in a new
`human_inputs.py` service; the existing `inputs.py` remains the JSON-file loader.

One request can serve multiple ideas/ventures without multiplying answers. R006
is owned by `v-sports-session`, with targets for both sports ventures and P023/P103.
R005 is owned by `v-route-repair`, R007 by `v-coopain`, R008 by `v-physical`, R009
by `v-receipt`. Resolve associated idea targets from the prior records rather than
hardcoding their workspace UUIDs throughout runtime code.

An answer belongs to its request, not globally to all future questions about the
same subject. A material new question gets a new ID. A definition revision retains
which exact question each answer answered. Do not reinterpret an old answer as
answering a newly changed question.

Response payload includes request/definition revision, response sequence, exact
answer text, declared author, source (`file`/`ui`), file/section/body hashes when
applicable, received time, previous response ID and submission key. Imported file
mtime is not the time the user authored it. Preserve exact source text and label
summaries as agent interpretations. Use deterministic IDs or unique receipts so
same submission is a no-op; a corrected or deliberately reverted reply is a new
revision with ancestry, never an overwrite of earlier evidence.

## File synchronization

1. Register known source files and R001–R009 sections explicitly for initial
   migration. Future requests are registered through the service. Do not infer
   questions from arbitrary `agent-*.md` output or execute Markdown instructions.
2. Read only regular, nonsymlink files under configured `FOUNDRY_REQUESTS_DIR`.
   Validate paths/size/encoding. The importer and read-only detector share these
   checks; do not keep `/requests` as an unrestricted raw-directory dump.
3. Parse a section by stable request heading. For these existing files, prefer
   the nonempty **My answer:** block when present, otherwise **Response:**.
   Retain the full section snapshot. Unfilled prompts/bullets are not an answer.
   Test the literal R008 inline `Response: I'll ask him...` format.
4. Hash question and answer separately, normalizing line endings only for change
   comparison. Editing the question or an adjacent section must not generate a
   fake new answer. The same current answer is a no-op even if file mtime changes.
5. Preview detected changes with request and target identities. Sync appends an
   answer and one ready agent **review** WorkItem in the owner workspace, linked
   by request ID and exact response ID, in one transaction. It does not complete
   the original blocked venture task yet.
6. Missing/malformed/deleted sections show **Source needs attention** while keeping
   the last saved answer and review. Never clear history or mark work complete.

Use a file fingerprint at preview and recheck before applying; reject changed
files with an actionable refresh message. A UI answer after the last file sync
and an independently edited file are divergent revisions. Show both for explicit
reconciliation instead of blindly overwriting the UI reply on the next sync.
Do not write UI replies back into the user's Markdown automatically. State in the
UI which copy is current and offer copying/exporting the saved answer if useful.

## Review semantics and exact handoff

The review queue is persisted through existing WorkItems; use READY, IN_PROGRESS,
DONE, BLOCKED or CANCELLED as appropriate. Do not add competing execution statuses
to `StepRun`. `HumanRequest.status` describes the question/answer lifecycle:
`waiting_for_answer`, `ready_for_review`, `reviewing`, `needs_clarification`,
`resolved`, `deferred`. Source-file diagnostics are separate from these states.

A manual agent begins by synchronizing files, listing pending answer reviews,
then claiming one with optimistic version checks. Claim records actor/time and
the exact response ID. A second agent cannot claim the same current task. Provide
explicit release/requeue with a reason after interruption; no silent timeout that
allows two agents to act on the same answer.

**Copy agent handoff** exports stable request/response/work IDs, relevant workspace
IDs, question, exact answer, prior review/state/score IDs, allowed local next
actions, held tracks, and completion instructions. It must not dump unrelated
venture data or imply that ordinary answer text grants external-action authority.
New runner integration can later consume this contract through `AgentRunner`.
Do not install a provider or build a scheduler now.

Review result is immutable and references its exact response and claimed work:
reviewer, time, interpretation, outcome, remaining unknowns, per-target changes,
new review/decision/work IDs and rationale. If another reply arrived after claim,
reject “mark current resolved”; preserve the older review as historical and leave
the newer answer pending. Completing review requires an explicit outcome:

| Outcome | Effect |
|---|---|
| Sufficient for next local task | Close only the answered input dependency; append state review and create/link the concrete next WorkItem, usually READY for the agent |
| Partial / ambiguous | Keep the useful answer, identify only unresolved fields, create/link a focused clarification; no duplicate blanket question |
| Deferred by user | Mark request deferred, retain venture hold and reopen trigger; finish intake review, but do not queue venture investigation |
| No state change needed | Record reason and mark answer reviewed; scores/status remain untouched |

Human-readable answer review and related state/work updates must commit atomically.
Do not close an entire multi-cause blocked task merely because one request is
answered. Split the remaining dependency or keep it blocked with the accurate
reason. Existing mutable WorkItem updates must retain AuditEvents. Score changes
are separate explicit assessments, not side effects of intake.

For shared requests, store the canonical response once. Target workspaces can
receive local Evidence/Artifact references containing provenance to that response
and attribution, so existing workspace-bound evidence/score validations stay
intact. A global request link is not permission to attach foreign Evidence FKs.

## UI and service surface

`/requests` becomes an Inbox with **Needs you**, **Answers awaiting review**,
**Deferred**, and **History** filters. A dedicated `/requests/{id}` page has the
question, affected venture chips, current answer editor, source-file reference,
save confirmation, review outcome and next owner. Link it from each relevant
venture/idea with a consistent R006 label. Optional structured helper fields for
sport/group remain conveniences; free text is valid and unknown is allowed.

Provide CLI/API operations with the same typed service: list/show requests, sync
registered files (preview/apply), submit response with expected version/request
key, claim/release review, complete review, export handoff. Suggested CLI namespace
is `foundry input`; document actual implemented grammar in DEVELOPMENT.md. HTTP
mutations use the existing token/origin boundary, response limits and 409 conflict
handling. GET must never create receipts or dispatch work.

Bootstrap R001–R004 by linking their existing receipt Artifacts, preserving their
IDs, hashes and historical reviewed state. Do not run the old intake script again
as a generic importer. Register/import R005–R009 once, then review under the
outcomes in [baseline](00-BASELINE-AND-ANSWERS.md). R008/R009 end deferred, not in
the ready investigation queue. Update current-direction documentation to remove
obsolete “waiting for sport/budget” claims, while leaving dated reports intact.

## Acceptance scenarios

- From either sports page find R006 in one action, answer without typing an ID,
  see saved state, then see its review and next work after manual agent completion.
- File edit, app restart, explicit sync, agent restart and repeated sync preserve
  one current response and one pending review. A second reply remains pending if
  an older claimed review finishes later.
- Duplicate request headers, empty responses, unknown IDs, symlinks, path traversal,
  oversized files, HTML in answers and stale writes fail safely or render escaped.
- Concurrent UI/file answers retain both candidates; resolution is explicit.
  Non-answer edits and same-content resubmission create no review flood.
- Shared R006 appears in both workspaces with one response/review. No foreign
  WorkItem or Evidence can be assigned through an unchecked workspace parameter.
- After latest intake, route/sports/Coopain have specific next work; physical and
  receipt tracks say “Deferred by you” with reopen conditions and no repeated ask.
