# N008 — shorten a scenic ride without losing its best sections

Record FOUNDRY-N008-20261002:r1. Discovery candidate; **no product build selected**.
The original idea remains N008; this narrower case is not another independent
portfolio input. Agent-owned investigation, no learner credit.

## The actual job

The user described three two-day rides: Court-Saint-Étienne → Antony, sleeping
near Saint-Quentin; Antony → Nébouzat, sleeping near Bourges; and Nébouzat → Antony,
sleeping in Thauvenay. Liberty Rider planning involved placing GPX points and
checking roads with Street View, avoiding fast roads while trying to arrive on
time. Export/import into 68° sometimes changed a displayed estimate from roughly
4.5 hours to six. Rain on the Nébouzat → Thauvenay day made a shorter journey
preferable; manual editing was too slow, so they used Waze without highways.

This is one real first-party problem report. It does not establish how often the
problem occurs, willingness to pay, or the cause of the ETA difference. A separate
[public rider account](https://www.reddit.com/r/Motardie/comments/1mlqqke/) describes
related planning friction; replies also report successful tools and workarounds.
Selected reports are leads, not a prevalence estimate.

A useful job statement is: **given an existing ride, a time budget and sections
I value, propose explainable shorter alternatives and show what I lose.** Rain
can change preferences during a trip. Requiring someone to rebuild a plan point
by point could make an otherwise capable planner impractical for that moment.

## What the incumbent comparison actually established

| Baseline | Evidence as of 2026-10-02 | Remaining uncertainty |
|---|---|---|
| Liberty Rider | Anonymous browser test produced a new town-centre Nébouzat → Thauvenay route: fastest with motorways 2h34 / 255 km; without motorways 3h05 / 225 km. GPX export menu observed. | No valued sections or deadline were supplied; no export/import was performed. These routes do not reproduce the user's ride or establish actual travel time. |
| Kurviger | [Documentation](https://docs.kurviger.com/web/faq/force_motorways) supports different curvature choices by segment, including Fastest. | The isolated browser remained on a loading screen; no interactive workflow verdict. Segment curvature does not prove per-segment avoidance settings or automatic time-budget repair. |
| MyRoute-app | [Features](https://www.myrouteapp.com/en/shop) list Street View, engine comparisons and route calculation across tiers; [waypoint documentation](https://support.myrouteapp.com/en/support/solutions/articles/12000075572-manual-waypoints-) covers time adjustments and section timing. | Route creation redirected to login; exact task untested. |
| 68° | [Access documentation](https://app68.eu/tarification/) distinguishes free mobile, paid desktop and GPX import modes. | Desktop sign-in observed. No authenticated test or purchase; user settings and original files unavailable. |
| Byway | [Engine claims](https://www.byway.world/engine) include scenic verification, weather and repair when a route exceeds a time budget. Private-beta invite form observed. | This is close counterevidence to novelty. No beta access or performance test; varied coverage is not evidence France is unsupported. |
| Throttle | [Site](https://throttlerides.com/) and anonymous planner expose curviness options; arrival warnings advertised. | Stated North America/India coverage does not cover this French task; no route submitted. |
| MotoRidez | [Describes](https://www.motoridez.com/blog/surprise-me-routes/) time-budget round trips and retaining chosen legs while rerolling others. | Australia-first and round-trip scope; French A-to-B use untested. |

[T7 result](trials/rider-result.json), [screenshots and actions](trials/t7-liberty/),
and [T8 result](trials/new-routing-result.json) retain scope and access failures.
The two successful BRouter smoke requests only establish basic routing. The
later six-request constraints probe failed, with a diagnostic target-island error;
that is an inconclusive setup/input result, not proof a competing engine lacks
constraints. No action count from browser automation is a human usability measure.

## Two causes that must not be conflated

**Geometry changed.** A sparse route, track interpretation, snapping, avoidance
settings or recalculation might choose different roads. Compare the ordered path
and divergence locations, not merely file bytes or point count. Liberty Rider
[documents recomputation differences](https://help.liberty-rider.com/hc/fr/articles/18717942560914-Le-trac%C3%A9-est-diff%C3%A9rent-de-mon-GPX)
and manual correction; that does not diagnose this trip.

**Geometry stayed similar, ETA changed.** Speed assumptions, stops, traffic,
weather, rider profile or calculation conventions might differ. The
[GPX schema](https://www.topografix.com/gpx/1/1/) provides routes/tracks/waypoints
and optional times/extensions; it does not impose a universal future ETA model.
Inspect moving time versus total duration and settings before proposing a file
converter. Existing [GPSBabel](https://www.gpsbabel.org/) also weakens the case for
a generic new format-conversion product.

Neither hypothesis is established here. The estimates 4.5h and 6h are recollected
app outputs, not measured on-road ground truth. Do not infer a 33% accuracy error.

## Next decisive comparison and stop conditions

First reconstruct one permitted case, using original GPX files and settings if
available. At minimum it needs start/end, a time budget, stops, valued sections
and acceptable compromises. Use town-level or edited data where possible. These
are necessary inputs to a meaningful comparison, not learner-assigned work.

Freeze one configured-incumbent baseline and a simple manual alternative before
testing: can each produce a rider-acceptable route within the same time budget,
retain the specified sections, explain the changed sections, and transfer the
intended path? Record effort, rejected options, settings and uncertainties. A
shorter displayed estimate alone is not success. Historical ETA accuracy would
require actual timings and conditions, which we do not have.

If an incumbent satisfies the task with reasonable effort, adopt/document that
workflow and stop the general product idea. If a reproducible miss remains, test
it on independent permitted rides before building. A buyer/adopter commitment,
repeat use, distribution and map/API costs are separate gates. A few selected
forum posts and our own interest cannot pass them.

## Possible form, conditional on the result

1. An incumbent configuration guide or contributed improvement may be all that is
   needed. Useful learning can occur here without launching a competing planner.
2. A small open-source path/ETA diagnostic or planner integration could have
   portfolio value if it solves the reproduced problem and existing utilities
   fall short. Paid integration or support would still need a buyer.
3. A hosted companion for repeated route repair is only a later possibility.
   Prefer integrating a routing engine over building maps, a navigation app or
   a scenery classifier first. A paid service needs demonstrated repeat value
   after accounting for routing/data costs and support.

No license, pricing, public release or navigation reliability claim is decided.
N008 currently earns another focused investigation, not default ownership of the
learning roadmap. Physical-task verification and skill evidence remain separate
access-held hypotheses; shared words do not justify combining these products.
