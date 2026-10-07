# T07 outreach drafts and T08 built-in guide

## T07a draft-only operation now

The user wants editable database/UI drafts and manual sending first. They named
an existing mailbox/domain, not credentials or authorization to send any payload.
Use the existing `ExternalAction`, `ApprovalRequest`, `ActionAttempt`, `AuditEvent`
and Artifact models where their semantics fit. Add no email-provider dependency yet.

Suggested smallest design: `ExternalAction(action_type='email', adapter='manual',
status=PROPOSED, risk=EXTERNAL_COMMUNICATION, approval_required=True)` represents a
proposed draft; human-facing label is “Draft”. Validate a typed versioned payload:

```text
schema_version, draft_revision, purpose, sender_identity (unverified/selected),
to[], cc[], bcc[], subject, body_text, language, tone,
attachment_artifact_ids[], related_request_id, unresolved_fields[],
source_evidence_ids[], delivery_mode='manual'
```

Use source Evidence for why the message exists, not for automatically extracting
recipients. No fake addresses or guessing a private address from a person's name.
Templates can leave recipients unresolved. Use existing configured sender choices
later; the mailbox supplied in R004 can be recorded as user-reported, not connected.

### Implementation steps

1. Add `outreach.py` with create/read/list/revise/export/record-outcome services and
   matching CLI operations. Use JSON inputs for multiline text and structured lists.
2. Append an Artifact snapshot for every content revision and an AuditEvent linking
   old/new digests. `version_id` detects stale edits; it is not the complete content
   history. Preserve draft text, rationale and references across restarts.
3. UI `/outreach` lists venture, purpose, recipient or “not chosen”, subject, state,
   last edit and next action. Detail form edits recipients, subject/body, tone and
   selected existing attachments; preview displays To/Cc/Bcc distinctly. Venture
   screens link their drafts. Do not require contact-CRM setup for one draft.
4. Export body/subject for copying and optionally a standards-based `.eml` draft.
   Clearly mark unresolved fields. Do not claim the user's mail client supports
   draft import until tested. Plain copy remains the reliable fallback.
5. Only export attachments explicitly selected by the user from registered,
   authorized artifacts. Verify readable file/digest/size; reject traversal,
   symlinks outside approved roots, arbitrary HTTP URLs and unregistered file reads.
   For the initial sample, generating a small non-sensitive text attachment is enough.
6. “I sent this manually” records actor, stated time, exact draft revision and optional
   receipt as **user-reported** Evidence. Mark the related outreach WorkItem done;
   do not invent a provider ActionAttempt or delivery/read receipt. Define the
   displayed draft state from that linked outcome. Record replies separately as
   evidence, preserving the message/outcome association and explicit next action.
7. Generate four variants for the same N003 research request: French/English ×
   formal/informal. Include a small clearly fictional sample and a specific ask,
   ideally a ten-minute review. No endorsement claims, fabricated prior connection,
   marketing performance claim or unrelated attachment. Draft P046/sports requests
   only when their target role and purpose are concrete.

Target code: new service + focused tests, `console_commands.py`, `web.py`, templates,
nav and existing Artifact/audit persistence. Use only a minimal justified migration
if an existing model cannot retain an essential link; document why first.

Acceptance: editing persists and preserves revisions; stale writes conflict;
missing recipients remain visible; one click exports only the selected draft;
opening/exporting/editing makes **zero network calls**; user-reported send is clearly
attributed; header injection is rejected; Unicode/line breaks preserved; workspace
isolation enforced; draft attachments cannot expose arbitrary local files.

## T07b later approved delivery, specified but gated

This is a later extension, not an excuse to block draft operation. Record provider
choice/setup as a precise input request when the user wants it enabled. Start with
one adapter behind a narrow interface; do not build generic hosted email provisioning,
a subscription system, multiple OAuth integrations or a shared credential store.
Configuration uses environment/secret references, never inbox/DB plaintext passwords.

Required before a live send:

- Freeze sender, To/Cc/Bcc, subject, body and exact attachment bytes/digests.
- Bind approval to the immutable revision/digest, actor and expiry. Editing anything
  after approval invalidates it or creates a new proposed action; stale approval
  cannot authorize the new content. Show the exact payload and consequences.
- A transport adapter supports only that approved envelope and retains provider
  receipt/attempt. Repeated submission must not cause duplicate sending.
- A timeout after provider acceptance is `UNKNOWN`, not safely failed. Require
  reconciliation before retry; SMTP has no universal idempotency guarantee.
- Tests use a fake adapter and then a local mail sink, never the user's real mailbox.
  Test denied/missing/expired approval, changed attachment, double click, stale edit,
  failure before transmission and uncertain response after transmission.
- Live delivery requires the user's explicit approval for the exact action. A
  configured mailbox, previous manual send or this plan supplies no blanket consent.

Record manual sends as user reports; adapter success as a provider acceptance
receipt, not necessarily inbox delivery or reading. Distinguish sent/replied from
whether the venture hypothesis was supported.

## T08 help and guide

Add `/help` linked from persistent navigation. Write for a founder returning after
a gap, with contextual links and short concrete examples. Do not bury ordinary
use behind developer vocabulary or database table names.

Required content and flows:

1. Start with an idea **or join an existing project**. Show how to add P046/Coopain
   without discarding its code/history or calling it commercially validated.
2. Explain idea, venture, assumption, experiment, evidence, assessment, decision,
   artifact and step in plain language. A successful step means it ran, not that
   the business passed. Separate executable steps from drafted agent requests.
3. Explain original/current scoring, 12 criteria, penalties, missing scores,
   confidence and version changes. Show how a high score and human-input hold coexist.
4. Explain advancement, product maturity, dropped/held/internal/use-existing,
   next action, reopening with a reason, and why there is no fabricated progress %.
5. Walk through filtering and sorting, finding a blocked venture, and reviewing its
   next action. Keep screenshots/examples synchronized with actual routes and labels.
6. Explain inbox response review, why a reply might leave a narrower follow-up,
   and how repeated imports avoid duplicate evidence.
7. Walk through draft → edit → manual export → record send/reply → evidence/decision;
   say automatic delivery is unavailable until configured and explicitly approved.
8. Explain local data location and backups, start/stop/restart, and where to put
   feedback. Offer commands in a developer subsection; users needn't understand SQL.

Use a template or a packaged static help page with existing styling; no documentation
CMS, chatbot or new build tool. Provide clear empty states and links from score/status
labels. Browser-check desktop/mobile, navigation links and an actual first-time path.
Tests should check essential routes/links and unsafe rendering, not brittle prose
snapshots. Update README/DEVELOPMENT only after features exist; don't document the
planned provider as already implemented.
