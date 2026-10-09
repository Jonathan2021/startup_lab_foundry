# Bounded venture trials

For every trial, freeze question, baseline, fixtures, measures and stop rule before
running. Record observed/doc-only/user-reported/synthetic evidence separately.
Use Foundry evidence/assessment/decision/artifact records; a failed harness is not
a competitor defect. Keep consequential actions draft-only. Source shortlist and
access failures from planning are in `research-sources.json`.

## T04 route transfer and route planning

Inputs in `foundry/requests/`: `anterioux-thauvenay_liberty_rider.gpx` and
`anterioux-thauvenay_68degres.gpx`; the user gives preferences/settings in INBOX R001.
User-reported estimates are 275 and 364 minutes (89-minute difference). The ride
started around 10:00 on 2026-09-16, with rain/cold prompting Waze without highways.
Typical chunks are about two riding hours then at least a 20-minute break. These
are preferences/recollections, not a recorded time series or arrival deadline.

### T04a local diagnosis that is now unblocked

Hypothesis: changed path geometry explains a material part of the ETA mismatch.
Alternative: different speed/road assumptions, stops or routing interpretation
produce different estimates even for similar geometry. Both may contribute.

1. Preserve/hash originals and treat them as potentially sensitive travel data.
   Never upload these files or detailed tracks to a public comparator without
   explicit permission. Keep derived exact-location artifacts in ignored local
   storage; committed reports can reference hashes and sanitized aggregate findings.
2. Parse bounded XML safely, without network/entity expansion. List track/route
   segments, track points, route waypoints and timestamp presence. Liberty has
   6,017 track points +66 route points; 68° has 479 track points; neither has times.
   Do not concatenate shaping waypoints with the detailed track as another route.
3. Compute per-segment geodesic/polyline distance and start/end alignment. Don't
   bridge discontinuities. Normalize direction if needed, and compare curves at
   equal along-route spacing or use point-to-segment distances in both directions.
   Dense-versus-sparse point counts alone do not measure changed roads.
4. Before interpreting output, freeze tolerances (e.g. inspect 25/50/100 m bands)
   and use synthetic identical/simplified/detoured/segmented controls. Estimate
   sampling/simplification error; annotate uncertain divergence sections.
5. Produce an offline overlay/difference report and a short table of largest
   divergent sections. Use established utilities as the comparison baseline when
   they can run locally, with no demand to install a second editor for a smoke test.
6. Separate distance change from implied mean-speed change using each app's
   reported ETA. Do not “prove” the engine's ETA formula from two polylines.
   No timestamps means no measured ETA accuracy. State any optional road metadata
   lookup separately; don't silently call external routing/geocoding services.

Acceptance: reproducible parse/distance/geometry comparison plus supported,
weakened or inconclusive assessment of the hypothesis. Exact changed roads may
remain uncertain. Do not write a full GPX product just to explain one pair of files.

### T04b the larger job remains important

The user's main job is shaping a scenic ride with broad areas and preferences,
then shortening it quickly without losing all the nice sections. Do not reduce
N008 to a file converter simply because D001 is easier to test.

Build a local ride brief: preferred nature/views/twisties, few traffic lights and
multilane roads, mostly no motorways, tolerable town sections, broad waypoints,
arrival/riding budget, stops separate. The desired 70/90 km/h rhythm is not a safe
constant average-speed assumption or a speed instruction. Weather adaptation
should reflect user constraints, not an unvalidated road-safety judgment.

After T04a, compare at most two relevant existing planners against one specified
ride brief. Reuse October 2 findings about Liberty Rider, Byway, Throttle and
MotoRidez with scope/freshness checks. Request only the missing maximum riding
budget or required arrival time and must-keep areas. An illustrative assumed budget
may support a synthetic UI example, but not a claim that the real case passed.
Measure planning/edit time, interactions/checkpoints, budget fit, retained valued
sections and rider preference. Stop a new product premise if existing workflow
suffices; otherwise isolate the repeated unresolved task for a small adapter.

## T06 P023 and P103 sports with friends

Interpret original notes literally: P023 is ranking/tournaments; P103 includes
match confirmation, head-to-head history, roles, joining a match and balancing
changing teams. “Across sports” does not require one comparable universal rating.

### Task and comparison design

1. Record user's reported interest and a follow-up with only: sport(s), group size,
   frequency, organizer, changing teams/roles, current workaround, and last concrete
   frustration. Use an illustrative 12-player volleyball session meanwhile if needed,
   explicitly labeled synthetic rather than attributing that activity to the user.
2. Freeze two distinct tasks: A, a small private ranking/tournament; B, create fair
   teams from today's changing attendance/roles, record results and repeat next time.
   Include late arrival, new player, correction/dispute and a returning participant.
3. Compare Rankat, Rankade and one sport-specific alternative only if relevant.
   [Rankat's official site](https://www.rankat.app/) currently claims friend groups,
   ELO history, invitation codes and team tournaments. Rankade's indexed official
   pages describe groups/match logging/rankings/API, but direct fetches returned
   errors during planning. Those access failures do not mean features are absent.
   EloSmash's page exposed only a badminton title/loading state; no broader claim.
4. Use public demos or user-assisted existing accounts. If account creation or paid
   access is required, write the exact request; don't let all other comparisons stall.
   Compare the actual workflow, not a feature keyword list or only organizer billing.
5. Measure setup/entry time, required accounts, rotating-team/role support, corrected
   result behavior, exports/history, and repeated willingness to use the workflow.
   Freeze a provisional success threshold, e.g. setup ≤10 minutes and recording
   ≤30 seconds/match, then ask whether it actually suits the group.

### Prototype and decision gate

If a reproducible gap remains, prototype **one local group-session assistant**,
not a social network with discovery, payments and universal sports rankings.
Preserve per-sport skill state; don't implement one ELO across unrelated sports.
Compare simple captains/random/balanced-rating baselines before a sophisticated
rating algorithm. Team result does not uniquely identify each player's skill;
represent uncertainty/newcomers, roles and sparse history explicitly. Synthetic
balance tests verify constraints, not real-world fairness or player satisfaction.

Two recurring sessions voluntarily using the workflow can justify a personal/group
utility iteration. That provisional gate does not qualify a business. A commercial
path additionally needs an organizer/community buyer, a repeated benefit beyond
free incumbents and an observed price conversation. Record adoption by the user
separately from independent participants. Keep P023/P103 source IDs and a parent-linked
narrowed idea if needed; avoid duplicate full competitor research for the two.

## T09a physical-task verification

The updated R002 permits a small public-data investigation; it does not supply
construction-expert labels. Timebox discovery to about 45 minutes or three relevant
sources/datasets. Capture task, public license, input modality, labels, failure
coverage and domain match. Instruction recognition or video summarization alone
cannot validate whether insulation, wiring or structural work is correct.

If usable data exists, run a small retrospective benchmark with a frozen split,
clear failure definitions and a simple baseline. Avoid leakage from demos used to
shape the system. No safety-critical quality assurance claim. If labels/domain
are unsuitable, retain “needs expert/field data” and name the smallest next input.
Offer one optional five-question, ten-minute review for the busy construction
contact, focused on task observability and costly misses. A homeowner's recollection
is useful problem evidence, not expert ground truth. Do not keep expanding dataset
search indefinitely or drop the whole idea solely because a dataset is absent.

## T09b portable work-sample receipt

Prepare one clearly fictional example: bounded exercise, rubric, observable output,
reviewer, date, limits and verification link/reference. Reuse Open Badges concepts;
no invented certificate authority, universal skills claim or fictitious endorsement.
Create formal/informal French/English outreach in T07 (four variants total).
Potential audiences: user's Amaris contacts as receiving practitioners, an actual
hiring/training decision-maker, and family as exploratory feedback. Their roles
are distinct; family approval is not issuer adoption.

Ask what decision the sample would affect, which evidence they trust, what they
would verify and what existing workflow they already use. Stop a platform build if
existing credentials suffice or nobody will use this evidence in a real decision.
Record feedback and exact remaining access question; don't call a polished sample
validation. No actual messages are sent by these tasks.
