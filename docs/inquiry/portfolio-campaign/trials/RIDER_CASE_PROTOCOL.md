# T7 — the actual rider workflow, incumbent access and comparison

Frozen after the user's trip description on 2026-10-02, before interactive trials.
This is a new case, not a changed success criterion for failed T5.

The user reports multi-day rides Court-Saint-Étienne→Antony (Saint-Quentin stop),
Antony→Nebouzat (Bourges stop), and Nebouzat→Antony (Thauvenay stop). Planning in
Liberty Rider involved manually positioning points and checking Street View;
avoiding fast roads conflicted with the time available. GPX transfer to 68°
sometimes changed estimated duration from about 4.5h to 6h. During rain on the
Nebouzat→Thauvenay day, slow manual replanning led to Waze's fastest non-motorway
option. Dates, exact routes, stops, settings and files are not supplied.

Hypothesis: a narrow opportunity may exist in repairing a scenic day plan to a
time budget, preserving the preferred sections and exposing transfer/ETA changes.
Alternatives: existing segment controls and route-comparison workflows suffice;
the issue is configuration or unfamiliarity; route geometry stayed identical and
only speed estimates changed. GPX transfer alone cannot discriminate these.

Compare public Liberty Rider, 68° Studio, Kurviger and MyRoute-app interfaces.
Use an isolated local Chromium profile, not the user's signed-in browser. CUA is
unavailable, but installed Chromium and the already-installed pyppeteer dependency
permit an independent anonymous test browser. No accounts, trials/subscriptions,
payments, external messages, route publication or private address inputs.

Budget: four initial page visits, ≤45 seconds each; up to ten minutes of actual
anonymous interface testing for one accessible planner. Stop at login/paywall or
unavailable service; do not infer feature absence. Preserve access outcomes,
screen captures and the actions actually performed. Query only town-level public
locations, primarily Nebouzat→Thauvenay. No actual navigation or safety claim.

Observe whether the interface can (a) show time/route alternatives, (b) lock a
preferred section while shortening another, (c) transfer without silently changing
the path, and (d) distinguish moving time from stops and uncertainty. Record
untested items explicitly. An incumbent satisfying the job weakens the build
case. A reproducible miss supports only a narrow follow-up, not a paid market.

The user is one interested first-party user, not multiple customers. Supplement
with independent first-person reports and contradictory successful-tool reports;
selected discussions cannot estimate prevalence. Preserve original T5 failures.
