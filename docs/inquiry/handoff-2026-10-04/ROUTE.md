# GPX transfer investigation r1

Run ROUTE-20261004-001, frozen in [PROTOCOL.md](PROTOCOL.md) before execution.
The route files remain unchanged and were never uploaded. Full summary, the
largest divergence locations, offline SVG and HTML are under ignored
`.local/handoff-2026-10-04/routes/`; exact coordinates stay local.

| Observation | Liberty Rider | 68° |
|---|---:|---:|
| Detailed track points | 6,017 | 479 |
| Track segments | 1 | 1 |
| Separate shaping route points | 66 | 0 |
| Timestamps | 0 | 0 |
| Haversine polyline length | 240.010 km | 236.684 km |
| Reported ETA (user, inbox R001) | 275 min | 364 min |
| Implied mean speed from these lengths/ETAs | 52.37 km/h | 39.01 km/h |
| Directed 95th percentile nearest-segment deviation | 31.0 m | 31.2 m |
| Samples within 50 m of other track | 99.92% | 99.83% |

Endpoints align within 0.3 m. Both directions' sampled deviations are below 100 m.
At Liberty Rider's implied mean speed, the shorter 68° polyline represents **3.81
fewer minutes**, not 89 extra minutes. The frozen “geometry explains >=44.5 extra
minutes” hypothesis is weakened. Different ETA assumptions or interpretation are
more plausible for this pair; their precise formulas cannot be identified here.
There is no recorded elapsed ride time, so neither ETA's accuracy was measured.

Largest sampled deviations: around 3.4 km along each exported track, 67/77 m;
a 68° sample around 17 km is 54 m; most other largest entries are roughly 40–45 m.
These are approximate along-route positions, not confirmed changed roads. The
nearest-segment test can miss ordering differences and only samples every 200 m.
Haversine measures exported polylines; sparse curves can underestimate road length.
Downsampling Liberty Rider every 13th point loses 12.873 km and produces a 451 m
maximum deviation, illustrating why point count alone is unreliable. This one
control is not a bound on the other app's export error.

Controls passed: identical track; collinear simplification; known detour; and
segmented discontinuities that must not be bridged. Parsing rejects DTD/entities,
nonfinite/out-of-range coordinates and oversized files. `scripts/compare_gpx.py`
reproduces the comparison using the standard library and no network.

The larger N008 job remains shaping/shortening a scenic ride. Its brief retains
nature/views/twisties, few lights and multilane roads, mostly no motorway, broad
areas and about two-hour riding chunks with >=20-minute breaks. A desired 70/90
km/h rhythm is a road preference, not a constant journey-speed assumption.
Maximum riding budget/arrival time and must-keep areas are still unspecified.
[Follow-up R005](../../../requests/2026-10-04-followups.md) asks only those inputs.
Then compare the existing Liberty Rider workflow and one relevant planner under
that brief, measuring edit time, interactions, budget and valued-section retention.
The GPX diagnosis does not qualify a converter business or settle route-planning utility.
