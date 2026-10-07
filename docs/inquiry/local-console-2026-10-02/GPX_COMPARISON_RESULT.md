# GPX comparison outcome

Date: 2026-10-02. **Inconclusive; no incumbent defect established.**

Both anonymous visits loaded gpx.studio's editor with HTTP 200. The first harness
stopped at stdin EOF before an import. The bounded retry opened the File menu and
observed Open/Export actions, but its DOM inventory omitted menu items and the
harness did not complete file selection within the attempt. It was stopped.
No fixture was imported, no pair of paths was compared, and no exported geometry
was verified. The page's presence cannot count as a successful comparison.

The two three-point Berlin GPX fixtures are synthetic public coordinates. They
contain no timestamps, ETA or user travel data. Retain the first failure as well
as retry artifacts: `gpx-trial-r1/` and `gpx-trial-r2/`. The retry's `actions.json`
records the File-menu click and stop. Both isolated browsers are closed.

RouteConverter's documented conversion and multiple-list display remain documentary
counterevidence to a broad utility, not a runtime pass. Next useful work is R001:
specified files/settings to distinguish geometry change from ETA conventions, or
a concrete new ride budget with valued sections. Do not run the same anonymous
editor smoke again as if it settled that job.
