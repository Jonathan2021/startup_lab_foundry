# T5 — mixed constraints with an existing route engine

Frozen before route requests, 2026-10-02. Follow-up to T4, not a revision of it.

Hypothesis: the computational part of N008 can already be handled by ordinary
engine calls and selecting among a few acceptable intermediate points. The
remaining value, if any, is a useful planning workflow rather than a new router.

Use public, synthetic Berlin-area coordinates: A=(13.278,52.508),
C=(13.510,52.365), and two acceptable intermediate points B1=(13.417,52.468),
B2=(13.441,52.466). They are test coordinates, not a navigation recommendation.
The acceptable area is the rectangle [13.407,13.451] × [52.456,52.478].

At most **six read-only requests**, 30-second timeout each, sequentially:

1. A→C, car-fast, default motorway preference.
2. A→C, car-fast, `profile:avoid_motorways=true`.
3–6. For each B: A→B default, B→C avoid motorways. Select the smaller returned
   total time among these two composed alternatives. Inspect route tags,
   endpoint snapping and leg continuity; preserve raw responses and parameters.

The profile parameter is documented in BRouter's ServerHandler; upstream
`car-vario.brf` implements motorway avoidance as a cost penalty. The public
server's car-fast profile may differ: absence of a route difference is
**inconclusive**, not proof that it honored an unsupported parameter.

Support for the narrow hypothesis requires valid routes, a positive control
showing motorway preference changes behavior, a joined route through the
acceptable area (junction separation ≤100m), and no motorway tags on its avoided
leg. If those conditions fail, record the exact failure without tuning more
coordinates or exceeding the request budget. No paid API, profile upload,
account, publishing or physical trip.

This is finite candidate selection, not a continuous corridor optimizer or a
beauty metric. It cannot establish safe navigation, optimality, a pleasant trip,
Kurviger UI usability, or user demand. A working composition weakens a novel
routing-engine premise; an integration idea still needs an observed user task.
