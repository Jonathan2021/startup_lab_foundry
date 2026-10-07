# Priority MVPs: investigation and implementation handoffs

2026-10-07. Six tracks are ready for bounded implementation; the
conversation-derived track is held only for its missing source. This report
records build decisions, not demand validation. The new venture applications have
not been implemented in this campaign. Foundry's agent collaboration improvements
were implemented and tested; Coopain's existing prototype was preserved.

## Decisions and entry points

All repositories are under `/home/jonathan/startup_lab`. Each implementation pack
contains a decision, architecture/data/interface contract, dependency roadmap,
behavioral acceptance cases, sources, Foundry manifest, agent handoff and live
first-task snapshot. Read `AGENT_HANDOFF.md` before starting a package.

| Track | Decision and MVP | Implementation map | First package |
| --- | --- | --- | --- |
| Volley Match | GO. Private volleyball groups, sessions, joining, confirmed scores, match history and provisional group Elo. | [Roadmap](../../../../volley-match/docs/mvp/ROADMAP.md) | V01: authenticated groups and revocable invites |
| Crous Queue | GO. National venue directory and fresh user-reported waits, with explicit unknown/stale/conflicting states. | [Roadmap](../../../../crous-queue/docs/mvp/ROADMAP.md) | Q01: safe, repeatable directory import/search |
| Coopain | GO, narrowed. Complete the existing referral-introduction prototype; candidates free, no bonus custody or automated payouts. | [Roadmap](../../../../coopain/docs/mvp/ROADMAP.md) | J01: reproducible baseline and remove invented compatibility scores |
| Ride Options | GO for a regional planning MVP. A–B and loops, preferences, distinct alternatives, tradeoffs and GPX. | [Roadmap](../../../../ride-options/docs/mvp/ROADMAP.md) | R01: routing provider and motorcycle-access verification |
| Volley Coach | GO, narrowed. Availability-aware personal volleyball practice plans and logged progression. | [Roadmap](../../../../volley-coach/docs/mvp/ROADMAP.md) | C01: slots, catalog, profile and source/review status |
| Foundry | GO as existing internal coordination MVP. Support these agents, then fix observed friction. | [Roadmap](../../plans/2026-10-07-agent-dogfood/README.md) | F01: observe real package completion and fresh-agent continuation |
| Conversation-derived idea | INPUT HOLD. Two saved possible links expose no readable transcript; neither is assumed to be the intended source. | [Source checkpoint](CONVERSATION.md) | R012: identify/provide source; other tracks continue |

The four new application repositories are initialized on `main` with no commits
or remotes. Coopain was moved intact from `/home/jonathan/coopain`; the old path is
a compatibility symlink. Its existing Git history, remote and pre-existing
untracked files remain. Foundry remains its existing independent repository.
No new venture remote, deployment, payment, email or agent service was created.

## What the investigation established

### Volleyball: build the small recurring activity first

The user's access to a volleyball group supports a concrete first workflow, but
does not prove adoption. Group rankings already exist in
[Rankade](https://rankade.com/), and [its model documentation](https://rankade.com/ree/)
explains group-relative ranking. The reason to build is the combined session,
roster, score confirmation and progression experience for this group, not a claim
to have invented Elo or sports matchmaking.

The initial contract fixes the rating rule: 1000 starting points, K=24,
equal-size teams of 2–6, team means, win/loss only, and provisional status through
ten rated games. Both sides confirm; pending/disputed/friendly/guest matches do not
change Elo. Immutable results and full ordered replay make corrections explainable.
A synthetic equal 3v3 match moves winners to 1012 and losers to 988. That verifies
arithmetic, not individual skill: fixed teammates cannot be distinguished reliably.

Use `v-sports-session` as the canonical implementation venture. Prior ranking and
session ideas remain source history; the older fusion proposal is not represented
as formally accepted by this campaign. There is one implementation repository and
one current build task, avoiding two overlapping apps. Public matchmaking,
cross-sport ranking and tournaments follow repeated private use.

### Crous: a national directory is feasible; national live coverage is unproven

The [official directory](https://www.data.gouv.fr/datasets/restaurants-brasseries-et-cafeterias-des-crous)
exposes 26 regional feeds under the catalog's `fr-lo` license. This run fetched all
26 and retained **972 rows with 972 region-scoped IDs**. Coordinate fields were
nonempty; that is not a comprehensive geographic-quality check or a guarantee all
locations are open/current. The normalized reusable snapshot and attribution are
in `crous-queue/fixtures/`; counts, feed URLs and hashes are in
[crous-probe.json](crous-probe.json).

The selected restaurants resolve to `paris:r177` (RU Cuvier) and `paris:r175`
(RU Châtelet). Cuvier's cafeteria is a separate row. Shared coordinates must not
merge different services. HTTPS for the Paris feed returned 404 while its catalog
HTTP URL worked; the importer must treat content as untrusted data, use a declared
feed allowlist, reject unsafe XML and preserve the last good regional import.

The MVP does not need prediction or manual observation before implementation.
Estimate-now and completed-wait reports remain separate. Current estimates expire
at 15 minutes; the latest report per device contributes once. With two or more
reports show median and range; strong disagreement is visible, not hidden in a
precise-looking number. Unknown is never displayed as zero. Rate limits, short
retention and moderation reduce abuse without pretending to solve fake identities.

[Affluences](https://www.pro.affluences.com/restaurant-universitaire) and
[CrousRadar's listing](https://apps.apple.com/fr/app/crousradar/id6755202143) show
existing overlap. The hypothesis to test after building is whether students can
create useful fresh coverage with very little reporting effort. A national venue
catalog is not a claim of national live wait data. Start distribution at
Cuvier/Châtelet while leaving other venues searchable with honest empty states.

### Motorcycle: scope corrected, real generation exercised

The venture now means **creating rides**, not explaining ETA differences between
apps. Historical GPX/ETA findings remain evidence. [Kurviger already offers curvy
planning and round trips](https://docs.kurviger.com/web/getting_started), so the
product hypothesis is useful alternatives with visible compromises and fewer
manual waypoints. Broad must-pass areas are a first extension after basic via edits;
social route ratings and universal scenery scores are later work.

A local GraphHopper 11.1 engine used an Andorra OSM extract without paid APIs.
It generated actual A–B road geometries and loops. The first A–B profile returned
a 27.69 km / 38.9 min route plus a 13.17 km / 21.5 min alternative: **the first engine
result must not be labelled fastest**. A 40 km loop request failed; 15 km and 25 km
targets returned approximately 21.0 km and 39.1 km loops. The app therefore needs
bounded retries, actual distance/time display, feasibility checks and honest
one/two/zero-option responses. See [route-probe.json](route-probe.json) and the
replay script/config in `ride-options/experiments/`.

The [stock motorcycle custom model](https://github.com/graphhopper/graphhopper/blob/11.1/core/src/main/resources/com/graphhopper/custom_models/motorcycle.json)
uses car access. The probe does **not** establish motorcycle-specific restriction
correctness. R01 tests motorcycle restrictions, private access, one-way and turn
rules against small fixtures, then adapts the importer or selects a verified
provider. This gates road-use trials; it does not block UI work with labeled fixtures.
Andorra is the technical probe, not the intended limit of the product: expand to a
French region after measuring import memory/disk and coverage behavior.

Curvature, road class and nature proximity are named proxies, not validated beauty
or safety scores. Enforce hard exclusions/time budgets before ranking. Retain OSM
attribution and engine/extract/model versions. [Street View policies](https://developers.google.com/maps/documentation/streetview/policies)
need a separate licensed integration; v1 can link to a selected coordinate without
collecting imagery or promising image-derived scenery judgments.

### Coopain: repair and finish the existing asset

The move preserved commit `aa382779b79951f843f37b8080f6f0972efe7e3c` and existing
local state; [move receipt](coopain-move.json). Seven selected tests passed in an
isolated Python 3.11 environment: privacy grants, referrer job posts, safety,
match snapshots and preference lifecycle. The probe used pinned backend requirements
and bcrypt 4.0.1 for compatibility. It is a baseline, not endorsement of old
dependencies or full browser/security validation.

The dashboard still generates compatibility percentages from IDs. J01 removes
those and shows actual matched criteria or unknown. Later packages complete the
candidate/referrer introduction state machine, explicit data sharing, consent
revocation, usable web flow, migrations and release safeguards. Preserve the
backend and clients; a rewrite would discard working privacy and matching behavior.

[Refer.me](https://refer.me/) and [Hellowork's referral offering](https://recruteur.hellowork.com/fr/produit/cooptation.html)
show that introductions and employer referral tools already have competition.
The useful narrow workflow is a relevant job with a willing employee, mutual
review and controlled information sharing. Employer referral bonuses can motivate
the referrer, but payment custody/splitting is excluded from this MVP.

French [placement payment rules](https://code.travail.gouv.fr/code-du-travail/l5321-3)
and [CNIL recruitment guidance](https://www.cnil.fr/fr/le-guide-du-recrutement)
justify candidate-free scope and careful privacy design; they are not legal
clearance of a future bonus-sharing contract. Public release needs collaborator
rights, employer-policy fit and secure personal-data handling. These are release
gates, not reasons to postpone local implementation with synthetic profiles.

### Coaching: choose personal planning, postpone automated video judgments

Choose volleyball first, sharing potential user access with Volley Match while
keeping the two applications independent. The core job is fitting useful practice
into actual home/gym/court/partner availability, retaining completed history, and
explaining a modest next-week adjustment. A deterministic scheduler is sufficient
for the MVP. Match Elo is not a fitness assessment or a certified skill level.

[Hudl Balltime](https://www.hudl.com/products/balltime) offers volleyball video
analysis and [SwingVision](https://swing.vision/guides/review-your-video-footage)
offers tennis video review. Their marketing does not prove accuracy, but it raises
the bar for a broad new video-analysis product. This campaign has no representative
consented footage, reliable labels or measured strategy benefit. Automated form
and live strategy are held until those inputs support a specific evaluation.

The scheduler can be built using synthetic slots and user-selected existing
programs. A public coaching catalog needs original/licensed descriptions and
appropriate review; publicly accessible [USA Volleyball resources](https://usavolleyball.org/resources-for-coaches/coaches-tools/)
are not a blanket license to copy content or an endorsement of individualized
advice. Plans must respect stated resources and approved recovery constraints;
discomfort input suppresses automatic progression. The synthetic probe checks
scheduling constraints only, not exercise efficacy or medical suitability.

## Foundry collaboration delivered

The live database now contains the six scope decisions, evidence, accepted research
results, dependency/branching maps and one ready first implementation task per
venture. Existing records were retained. Obsolete executable tasks were paused
with rationale; pending human inputs remain later pilot inputs. No live task was
left claimed by a rehearsal. [records.json](records.json) contains exact IDs and
resolution receipts. Scores were not manufactured from synthetic tests; existing
assessments remain, and the new coaching venture can be honestly unscored.

The delivered repository bridge provides:

- Explicit venture/workspace/store identity and `resume` / `start` commands.
- Version-checked claims and immutable context; failed preparation releases the
  exact unchanged claim. Stale contexts and conflicting workers are rejected.
- Local immutable feedback outbox, retry-safe evidence capture and delivery
  receipts. Feedback is attributed to its source venture and reviewed in Foundry.
- Instructions for arrivals/coverage review, result submission, preview, acceptance,
  stale-result recovery and the next dependency-satisfied package.
- Audited venture renaming so the displayed product can follow a clarified scope.

From any prepared repository:

```bash
python3 tools/foundry_agent.py resume
python3 tools/foundry_agent.py start --actor implementer-YOUR_UNIQUE_SESSION
```

Then follow that repository's `AGENT_HANDOFF.md`. Report bugs immediately and
friction/ideas/positive evidence at package checkpoints with `feedback-template`
and `feedback --input FILE`. A receipt means recorded for review, not fixed.
The real campaign feedback receipt is [retained here](feedback-receipt.json).

Use one writer per venture; parallel agents may work in different repositories.
No managed agent runtime, remote authentication, worker scheduler or lease expiry
is implied. Actor labels are local audit attribution. The helper is development
coordination: each resulting application installs and runs without Foundry.
See [ADR-0015](../../adr/0015-repository-agent-handoffs-and-feedback.md) and
[observed friction](FRICTION.md). The root Makefile also now selects Foundry's
strict mypy configuration explicitly; unrelated parent changes were preserved.

## Verification and limits

| Check | Observed result |
| --- | --- |
| Foundry product/unit/integration/CLI/package checks | 144 passed; one host PostgreSQL test skipped because no explicit host URL was configured |
| Final agent-kit and rename checks | 3 passed, including the final added claim/context case |
| Container, isolated PostgreSQL and workflow contract checks | 18 passed |
| Foundry real browser checks | 5 passed |
| Foundry source/helper lint and strict types | Passed; 41 source/helper files type checked |
| Six actual repository handoffs on an isolated live-store copy | All claim/prepare/release passed; complete contexts 5,141–17,553 bytes within 24 KB budget |
| Live manifest/map/ready-task verification | Six passed; dependency packages and helper hashes verified |
| Coopain selected baseline tests | 7 passed; full suite and browser completion remain J01–J04 |
| Synthetic rule probes | Six groups passed; no user/demand/physical-world validation |

The Foundry test groups overlap; do not add them into a unique-test total. Product
checks preceded the final extra helper test, which was then separately run. Exact
command/log references and hashes are in [verification.json](verification.json).
The push also surfaced two alerts in the current dependency lock. Mako and pytest
were patched, while seven alerts from a historical experiment were retained and
explicitly scoped. [Dependency triage](DEPENDENCIES.md) and the appended verification
record distinguish the updated-lock checks from these baseline results.
The earlier main commit `07ecb37` also passed GitHub Python 3.11/3.13,
PostgreSQL and image/Compose jobs; that result alone does not certify later changes.

The service used the existing permanent local DB. A verified pre-change backup,
isolated rehearsals and a post-change integrity/preservation check protect its
history. Raw downloaded data and local databases are under ignored `.local/`;
only reusable sanitized fixtures and bounded evidence summaries belong in Git.

## Order of implementation and checkpoints

1. Start V01 and Q01 in their separate repositories. Both give a quick, concrete
   end-to-end coordination test. Foundry F01 observes their actual returns and a
   fresh agent's ability to continue; do not repeat setup rehearsals as progress.
2. Start J01 to stabilize Coopain and R01 to resolve motorcycle-access behavior.
   These are independent of the first pair. Cap concurrent work to the actual
   agents available; each venture's later packages depend on earlier acceptance.
3. Continue accepted packages toward local usable MVPs. Start C01 after the first
   pair's coordination loop works; its scheduling implementation needs no video
   corpus or manual dataset creation. Source/review limits remain visible.
4. After V01/Q01 return, triage Foundry feedback. Fix demonstrated recurring
   problems before adding integrations or internal specialist agents. Record
   time-to-find-work, context size, stale submissions and manual recovery; token
   savings and hosted demand remain unmeasured.
5. At each app's local release, run its actual browser flow, migrations,
   backup/restore and documented clean installation. Prepare a concrete deployment
   proposal and any remaining operating/content gates. Local acceptance can pass
   before voluntary user trials; do not label synthetic activity real traction.

Example: the Crous agent implements Q01, tests a hostile XML fixture and an
idempotent 972-row import, then returns files, commands, results and limitations
with a proposal for Q02. The coordinator reviews the diff and Foundry preview,
accepts the result and activates Q02. A later agent starts from the repository,
receives the accepted state, and implements fresh-report rules. If its context
missed the distinction between RU Cuvier and Cafétéria Cuvier, it reports that
specific omission to Foundry with source IDs; the venture need not wait for a
general platform redesign.

For the conversation-derived candidate, [R012](../../../requests/2026-10-07-priorities.md)
remains the only source clarification required. Once the intended text is known,
derive and compare concrete jobs from it; do not present an invented substitute
as research from that conversation.

## Reproduction artifacts

[PROTOCOL.md](PROTOCOL.md) precedes the runs. [probe_rules.py](probe_rules.py)
and [rules-probe.json](rules-probe.json) retain synthetic checks and limits.
[campaign-input.json](campaign-input.json) is the frozen recording input;
[record_campaign.py](record_campaign.py) uses typed services and accepted result
contracts, not SQL writes. Its output checkpoint resumes completed ventures only;
an interruption inside a venture requires inspecting/reconciling its partial
state. **Do not blindly replay the campaign on the live store.** Rehearse on a
backup copy, use a new output path, and inspect previewed effects first.
[verify_handoffs.py](verify_handoffs.py) is a read-only live identity/plan check,
and [agent-smoke.json](agent-smoke.json) records isolated startup results.
