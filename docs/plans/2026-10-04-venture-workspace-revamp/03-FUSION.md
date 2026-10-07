# Sports fusion proposal and decision workflow

Implement V04a/V04b. This document is a **proposed** portfolio change. It does not
merge records, approve a build, authorize a sports-group trial or establish demand.

## Proposed venture

**Working name: Volleyball Sessions and Fair Tournaments**

For friends and informal outdoor volleyball groups, help an organizer turn today's
attendance into balanced teams and fair tournament pools, record and correct match
results, and show participants' progression and head-to-head history over repeated
sessions. Begin with one reachable group alongside its existing WhatsApp
coordination. Test whether shared participant/result records help both ordinary
sessions and tournament seeding before expanding to finding players or other sports.

Recommendation: combine P023 and P103 into one focused venture with two explicitly
testable jobs: **balanced sessions** and **ranking/tournament seeding**. They share
participants, matches, skill estimates, organizers and distribution through the
same group. Keep separate hypotheses and acceptance criteria for each job so that
a failed tournament feature need not sink useful session tooling.

This is a design inference from the latest R006 answer, not an incumbent gap or
commercial conclusion. The earlier split was useful for investigation; the new
specific volleyball context now supports testing them together.

## Alternatives and trade-offs

| Option | Benefit | Cost or reason not to choose now |
|---|---|---|
| One volleyball venture, two jobs | One history/attendance model; one group trial; fair teams and fair pools can share inputs | Combined scope needs restraint; individual skill estimates in changing teams may be unreliable |
| Keep two independent ventures | Ranking/tournaments and session coordination can target different customers later | Duplicates discovery, data entry and positioning for the same current group |
| Keep both ventures and share only research | Lowest commitment until actual use is observed | Leaves the user's duplicate management problem and product boundary unresolved |
| Adopt existing tools and stop new product work | May solve the problem cheaply | Requires a real task comparison; existing reports are not completed app trials |

Default recommendation is the first option as a **single investigation**. Prefer
adoption of an incumbent if actual trials meet the combined job. Reconsider a split
if independent organizers/buyers, substantially different session workflows or
incompatible pricing/distribution emerge. Do not keep two ventures merely because
two workbook rows existed, or fuse solely because titles share “ELO”.

## Exactly what is retained or left out

| Capability or hypothesis | Provenance | Proposed treatment |
|---|---|---|
| Private ratings, progression and match history | P023/P103 and R006 | Fused into one participant/match history; retained for trial |
| Balanced teams for today's attendance and multiple nets | R006, narrower P103 session job | Core first job; allow organizer override and record why |
| Fair strength distribution across tournament pools | P023 and R006 | Core comparison task using the same roster; distinguish team balance from pool seeding |
| Corrections and disputed results | Necessary for trustworthy retained history | Include a minimal correction/audit path in the trial; do not silently rewrite ratings |
| Player positions and club-ranking initialization | Original P103 | Deferred until the group's actual formats and needs justify them |
| Find partners or fill sessions by skill | R006/P103 | Retained as a future hypothesis, outside the first trial because it needs participation density |
| Other sports | Original breadth | Deferred; separate sport/group rating pools if later supported |
| Universal comparable ELO across different sports | Possible reading of the P103 name, not an established requirement | Explicitly excluded assumption; do not attribute it to the user as an original demand |
| Public paid tournaments, sponsorship and promoted matches | Original P023 | Deferred monetization hypotheses, not commitments or validated demand |
| Replacing WhatsApp, venue booking and a broad social feed | Not required by the current evidence | Excluded from the first scope; no new accounts or messages now |

Do not select a specific rating algorithm in this Foundry revamp. Ratings for
changing teams, newcomers and sparse results need their own bounded comparison;
the term ELO is the user's shorthand, not proof that a particular formula works.

## Proposed first trial after participation is actually available

Prepare a short worksheet using real attendance only with appropriate permission,
or clearly labeled synthetic fixtures for preparation. Compare the current manual
method and an existing tool's available workflow for team assignment, pool seeding,
result entry, correction, newcomer and late arrival. Record setup/entry time,
organizer overrides, perceived fairness and willingness to repeat. Preserve the
earlier provisional targets of setup within ten minutes and result entry within
30 seconds as test criteria, not observed performance.

Two voluntary sessions can inform personal/group utility. Independent organizer
adoption and a payer discussion are separate commercial gates. No actual session,
participant result or payment can be fabricated from the user's planned outing.
The implementation task prepares this brief; it does not build the sports product.

## Review screen

Portfolio **Proposals** shows this suggestion; both source details show a related
proposal card. The detail page must show:

1. Proposed name, complete description, recommendation and alternatives.
2. Each source idea/venture with ID, exact source revision, current score and
   state; clearly distinguish idea estimates from venture assessments.
3. The scope comparison above with **Retained / Combined / Deferred / Excluded**
   labels and reasons. Added scope must say it was added, with its evidence.
4. A concrete effects preview: new idea/venture, source-state changes, links,
   open-work treatment and requests affected. Nothing is deleted.
5. **Accept and apply**, **Edit proposal**, **Reject** and a required rationale.
   Editing creates a new revision and shows its differences. Old acceptance
   cannot apply to edited content. Rejection preserves the proposal and its reason.

Example decision rationale, offered as a draft rather than prefilled consent:
“Use one volleyball investigation because balancing and tournament seeding need
the same group data. Defer partner discovery until repeated use is observed.”

Agents use the same service for proposal drafting/revision and may record their
recommendation/rationale. Resolution records support user or agent actors. An
agent may resolve only against an existing explicit human delegation receipt
covering that action and exact proposal revision; store its reference and verify
its scope. No such receipt is supplied for this sports fusion, so current
application authority remains the local operator accepting its exact revision.
An arbitrary `actor=agent` or generated Markdown statement is not delegation.
Use a narrow validated receipt, not a general delegation engine. Distinguish
proposed-by, edited-by and decided-by, and test accepted/rejected resolutions
through both actor paths with valid and missing authorization fixtures.

## Small persistent representation

Add `PortfolioProposal` with ID, portfolio/owner-workspace FKs, kind (`fusion`
only initially), current revision Artifact FK, optimistic version, state
(`proposed`, `rejected`, `applied`, `reversed`, `superseded`), resolution Artifact FK nullable
and unique creation request key. The owner is the Foundry coordination workspace,
resolved through `v-foundry`, not either source venture's history.

Add `ProposalParticipant` with proposal FK, role (`source`/`result`), exactly one
idea FK or venture FK, and unique membership per role/entity. Validate same
portfolio; pin idea revisions and venture state/scope digests in the immutable
proposal snapshot. Source memberships cannot change silently on an applied
proposal. Revised source sets create a superseding proposal.

Store content in validated `portfolio-fusion-proposal/v1` Artifacts: sources and
versions, proposed description, retained/deferred/excluded scope, alternatives,
evidence links, work/request effects and reviewer rationale. Each edit appends a
snapshot; the root's expected version protects against concurrent changes.
Store decisions/effects in `portfolio-fusion-resolution/v1` Artifacts plus
AuditEvents. Accepted local commitment can additionally use existing `Decision`
with kind PIVOT and rationale. Do not force a rejected proposal into a nonexistent
`DecisionStatus.REJECTED` or misuse external-action delivery approvals.

Use existing `IdeaRelation.DERIVED_FROM` for the new idea's two parents, matching
`PortfolioService._create_idea`. Proposal participants supply explicit venture
lineage without hijacking the single `source_idea_revision_id`. The new venture
points to the new composite idea revision.

Suggested service file `proposals.py`, routes `/proposals` and `/proposals/{id}`,
typed CLI/API create/revise/resolve operations. These are future routes. Detect an
existing pending proposal for the same seed key/source set before creating another.
Seed only this demonstrated sports case; no embedding index or portfolio-wide
automatic merge job. Manual selection of source ideas/ventures should also work.

## Effects of acceptance

Default application creates a **new** composite idea and venture, retaining the
two originals. Suggested venture ID: `v-volley-sessions`; allocate the next derived
idea ID through existing conventions after checking collisions. Reserve resulting
IDs in the effect preview; if collisions/state changes arise, require a refreshed
preview. No renaming P103 to make the other history disappear.

In one transaction, validate exact proposal revision, source versions and explicit
decision; then create composite records, parent/participant links, resolution and
audit records, source/target WorkspaceReviews, and planned work/request links.
The version check covers every affected WorkItem, workspace review and current
request response as well as source idea/venture scope. New work or a corrected
answer must not be silently superseded using an older effects preview.
Repeated identical acceptance returns the existing result. Acceptance racing with
rejection/editing must allow only one transition. No transaction may leave a new
venture without lineage, or old sources held without the target.

On source ideas/ventures append a hold review with **Continued in
v-volley-sessions**, referring to the accepted proposal. “Continued in” is a
relationship label, not a claim that the concept was rejected or commercially
dropped. Keep original titles, definitions, IDs, scores, reviews, work, Evidence
and Artifacts accessible at their original URLs. An explicit portfolio filter can
exclude continued sources from active-work counts while All still displays them.

For open work, preview one of: retain at source, supersede with a linked target
task, or cancel a duplicate with reason. Carry R006 as the same canonical request,
add a target link to the fused workspace, and avoid asking it again. Coalesce the
two sports comparison tasks into one new bounded trial task only when specified
by the accepted preview; mark the source tasks superseded via audit/provenance.
Never move or clone all historical records, transfer ownership silently, or count
the shared answer as two independent observations.

Historical source links remain navigable from the target. Any local target
Evidence needed for scoring references its original source and limits explicitly.
The composite starts **Not yet scored** until an explicit assessment addresses its
new scope; no averaging or automatic copying of either parent's numeric total.

## Reversal and acceptance checks

Reversal is a new, reasoned decision, not deletion or rewriting the accepted one.
It appends a resolution referencing the original and sets the proposal to reversed;
the earlier accepted effects remain inspectable. Replaying an old acceptance key
after reversal returns its historical result/current state and never reapplies it.
For an immediate reversal with no downstream work, reopen source reviews/tasks
and hold the composite, retaining all links. If target activity exists, show it
and require a new explicit work/state treatment; do not mechanically replay old
states over newer work. A basic controlled reversal service/form is in V04b;
arbitrary splitting of mature businesses is not.

Test proposal creation produces no composite; rejection changes no venture;
editing invalidates old revision acceptance; double acceptance creates one result;
stale source state or invalid/cross-portfolio participants aborts everything;
injected failure midway rolls back everything; source URLs/history survive; shared
answers remain single; and reversal preserves later evidence. Before real
application, show the exact name, scope, affected records and work changes to the
user. Test all effects on disposable fixtures even if the real proposal remains
undecided.
