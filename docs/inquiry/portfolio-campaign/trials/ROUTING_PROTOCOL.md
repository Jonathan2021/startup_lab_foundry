# T4 — existing public route engine smoke test

Frozen before requests, 2026-10-02. The interactive browser tool is unavailable
(`CUA_REPL_ENABLED_SURFACES is required`), so Kurviger UI operation is untested.
This is an access limitation, not a Kurviger defect.

Use the public BRouter endpoint documented by the project with two short public
coordinate pairs from its documentation in Berlin, and two profiles (`trekking`,
`car-fast`). At most two requests, each capped at 30 seconds. No account,
authenticated data, private location, route publication or physical navigation.

Record HTTP outcome, GeoJSON validity, route-coordinate count and provided
distance/time properties. A valid response establishes that an existing engine
can compute a configurable route. It does not establish beautifulness, mixed
segment preferences, flexible corridor support, safety or a willingness to pay.
Failure to access the public service leaves this arm inconclusive, not evidence
that the proposed route product is differentiated. Follow-up must test the
specific mixed-route/corridor job, not compare feature names.
