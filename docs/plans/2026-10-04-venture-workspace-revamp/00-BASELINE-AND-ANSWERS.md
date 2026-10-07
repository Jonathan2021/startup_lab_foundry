# Baseline and latest answers

Inspection date: 2026-10-04. Paths below are relative to the Startup Lab root.
This document records observations and proposed interpretation; it is not a
database intake receipt.

## Verified implementation baseline

- Root HEAD: `e6a83e470d052439e5c8d4a943428f5bbd132f7f`.
- Foundry HEAD: `3b082507062838df4009d4b636c4f320436f3b41`.
- Both trees are heavily dirty, including untracked runtime files. HEAD alone
  does not describe the application. Preserve staged and unstaged edits.
- Read-only inspection of `~/.local/share/startup-foundry/foundry.local.db`
  found Alembic head `9af261004001`. Re-resolve configuration during execution;
  do not assume every installation uses this path. Ordinary Foundry CLI reads
  apply migrations, so this planning pass used SQLite `mode=ro` directly.
- Current stack is FastAPI, Jinja templates, small CSS/JS, SQLAlchemy and Alembic.
  No frontend framework or storage replacement is justified by the reported UX.

| Observed friction | Verified source and implication |
|---|---|
| Venture identity disappears on detail | `templates/venture.html` shows lifecycle in its eyebrow, but no venture ID. Idea details already show their ID. |
| Venture score is absent on detail | No score context/component in `web.py:venture_detail` or `venture.html`. `views.py` obtains list scores through `Venture.source_idea_revision_id`, so these are idea scores. |
| Idea score is too low on the page | `idea.html` includes full `review.html` before `scoring.html`; no compact header score. |
| There is nowhere obvious to answer R006 | `review.html` edits state/reason/next work, not answers. `/requests` renders entire files in preformatted text. |
| New replies are not reliably routed | `ReviewService.inbox_status` handles only R001–R004 from INBOX.md. The database has those four answer receipts; no R005–R009 answer receipts were found. |
| Two sports records need a deliberate decision | `IdeaRelation` supports derivation/combination, but `/new?parent_id=...` creates immediately; it is not a revisioned proposal and decision workflow. |
| Detail pages become record dumps | `venture.html` stacks checkpoint, outreach and seven record collections; the generic step form occupies the second column regardless of the next useful action. |
| Agent execution is overstated by navigation | `steps.py` has an optional `AgentRunner`; missing runner produces a blocked handoff. Saving an answer does not launch an agent. |

Use the existing `reviews.py`, `scoring.py`, `projects.py`, `outreach.py` and
`steps.py` services. Preserve workspace reference checks, optimistic concurrency,
immutable evidence, local token/origin controls and independent product boundaries.

## Concrete identities and historical scores

| Source idea | Existing venture | Venture workspace |
|---|---|---|
| P023 — Amateur Sports ELO & Tournaments | `v-sports-ranking` | `6e2795a7-2457-44e1-b3e1-0bc66ed4f734` |
| P103 — Cross-Sport ELO & Matchmaking | `v-sports-session` | `417476af-0674-4aba-9022-843957dc3ca2` |

Current source revisions observed: P023
`dd0f21eb-aba1-4974-bb66-7264c2f538c7`; P103
`8908cee4-b62d-4dd1-8719-58a5c0ad44ee`. Verify before mutations.
The [previous records](../../inquiry/handoff-2026-10-04/records.json) retain
P023 original 49/reviewed 51 and P103 original 45/reviewed 47, both reviewed at
low confidence with 12 factors. These are idea judgments, not venture validation.
Do not invent a fused score of 49 by averaging 51 and 47.

## Preserve the answer files

Observed SHA-256 values:

| File | Digest |
|---|---|
| `foundry/requests/INBOX.md` | `383231335395f22202b8fc59786f09a0625b6118d826b821cb1b045da8468971` |
| `foundry/requests/2026-10-04-followups.md` | `8705a386ac0e8588cfd8d70e397c509ef56391ce6a85f1e8f1d94a4ef0411d7b` |

A changed digest means reread the file; it does not mean reject a later user edit.
No reply in either file should be overwritten by generated summaries or statuses.

## R005 route planning

User reports a desired 4–5 hours, winding Auvergne areas and river/canal riding,
plus the real frustration: time spent comparing Street View and placing exact
GPX points. They want broad markers/preferences and three editable alternatives:
quicker, scenic and balanced. Preserve prior rain/cold, break and road preferences.

Interpretation: unlock planning comparison, not another geometry-only diagnostic.
Treat 4–5 hours as the target riding window with breaks separate (the question's
framing), label that assumption, and show elapsed time separately. Do not silently
turn five hours into an inviolable maximum. Ask about a hard deadline only if a
concrete alternative exceeds it. A scenic option outside the target must say so.

Next deliverable: a frozen comparison brief with broad must-keep areas, the three
candidate trade-offs, editable choices and measures of planning effort. No fake
routable GPX or exact ETA without a routing basis. Keep precise GPX tracks local;
this answer grants no permission to upload them. Store a selected option, rejected
alternatives and reason as preference evidence; model training remains deferred.
Targets: `v-route-repair`, N008/D001. Completing intake removes the old budget/
areas question, not all route feasibility uncertainty.

## R006 volleyball

Known: outdoor volleyball with friends; a planned outing with five other people
(six including the user); WhatsApp coordination; larger drop-in groups also
exist. Pain includes balancing teams across multiple nets, fair strength spread
across tournament pools, ratings/progression and head-to-head history. Future
desire: find partners and fill sessions with appropriately skilled players.
User has not used Rankat/Rankade.

Unknown: normal attendance/frequency, organizer role, exact team formats/roles,
consent to collect participants' data and whether the proposed session occurred.
Do not convert “in an hour” into an observed session or a calendar commitment.
Six-person attendance is one planned case, not the default group size or proof
that all matches are 3v3.

Next deliverable: the [fusion proposal](03-FUSION.md), a short volleyball-specific
trial sheet, and reuse of prior comparator findings with their limits. Only ask
the remaining questions when needed for an actual trial; do not request the whole
sport/group description again. Both sports ventures share one R006 response.
No build of ranking algorithms, scheduling or a community network follows yet.

The supplied [Green Volley Paris page](https://greenvolleyparis.com/fr), accessed
on 2026-10-04, exposes a calendar and directs people to WhatsApp for real-time
coordination. That supports relevance to the coordination context; it does not
establish missing balancing features, adoption or permission to contact members.
No group was joined or contact made.

## R007 Coopain

Known: no real user tests; user/friends report referral bonuses at companies;
project paused for personal scheduling reasons. Rights, ownership and license
have not been agreed. Friends may test the app. This does not establish an
employer payer, a validated referral workflow, or transferable commercial rights.

Next deliverable: update the existing project brief to distinguish a recruitment
access opportunity from a verified buyer; prepare a private tester walkthrough
and a short cofounder ownership checklist without offering legal conclusions.
Retain the documented placeholder compatibility-score issue and runtime-test gap.
Do not publish, represent rights as settled, or contact friends on this answer.

The supplied [monetization discussion](https://chatgpt.com/share/6ac24a31-a968-83ed-a08f-1858fda8a507)
returned a page title but no readable conversation body on 2026-10-04. Its ideas
have **not** been reviewed. Retain the URL with this access result; request a text
excerpt only if that discussion becomes necessary to choose the payer test.
Do not replace it with remembered or invented content.

## R008 and R009 explicit holds

R008: wait for the construction contact's feedback; `v-physical` and related
N001/G014/P007 remain held. R009: wait for the user to identify a receiving
practitioner; `v-receipt` and related N003/G005/P106 remain held. Record each
response as reviewed with outcome **deferred by user**, retaining the precise
reopen trigger. Intake review is complete, the venture's validation task is not.

Do not create repeated reminders, new outreach, replacements for the held trials,
or ready agent investigation jobs for these tracks. Independent Foundry and other
venture work can proceed. R004's draft-only outreach authority is unchanged.
