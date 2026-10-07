# Trials: scope, failures and reproduction

Date: 2026-10-02. All operations were agent-owned. No provider/model calls, paid
services, new accounts, customer outreach, route publication or cloud provisioning.
Public page/route requests did occur. Synthetic feedback is not actual human
review. Chromium used isolated profiles, never the user's logged-in browser.

## Evidence index

| Trial | Frozen protocol | Retained result |
|---|---|---|
| T1 MLflow | [PROTOCOL](PROTOCOL.md) | [JSON](mlflow-result.json), attempt logs below |
| T2 changedetection component | [PROTOCOL](PROTOCOL.md) | [JSON](change-result.json) |
| T3 exact provenance | [PROTOCOL](PROTOCOL.md) | [JSON](source-reuse-result.json), frozen revision-1 inputs |
| T4 route smoke | [ROUTING_PROTOCOL](ROUTING_PROTOCOL.md) | [JSON](route-result.json) and raw two GeoJSON responses |
| T5 constraints + diagnostic | [constraints](ROUTE_CONSTRAINT_PROTOCOL.md), [diagnostic](ROUTE_DIAGNOSTIC_PROTOCOL.md) | [six failures](t5/result.json), [diagnostic](t5-diagnostic.json) |
| T6 source-impact controls | [SOURCE_IMPACT_PROTOCOL](SOURCE_IMPACT_PROTOCOL.md) | [JSON](t6/result.json), frozen revision-1 inputs |
| T7 actual rider, partial | [RIDER_CASE_PROTOCOL](RIDER_CASE_PROTOCOL.md) | [JSON](rider-result.json), `t7/`, `t7-r2/`, `t7-liberty/` |
| T8 closer alternatives | [NEW_ROUTING_COMPARATORS_PROTOCOL](NEW_ROUTING_COMPARATORS_PROTOCOL.md) | [JSON](new-routing-result.json), `t7-t8-followups/` |

## Effective environments and failures

Python 3.13.5 ran the product and isolated probes. T1 used MLflow 3.16.1;
T2 used changedetection.io 0.60.8; the latter environment supplied
pyppeteer-ng 2.0.0rc16 for browser probes. Installed dependencies are frozen in
[MLflow requirements](mlflow-requirements.txt) and
[changedetection requirements](change-requirements.txt). Chromium was
153.0.8010.47 (snap). Public routing/backend profiles and vendor pages were not
pinned. No downloaded model or Hindsight service was used.

Retained [logs](logs/) distinguish setup/harness failures from capability misses:

- T1 attempt 1 encountered TraceNotFound before asynchronous persistence completed.
  Synchronous trace logging was enabled. Attempt 2 used the wrong assessment field
  (`type`); the installed API requires `source_type`. Attempt 3 passed.
- Installing changedetection required explicitly allowing its pinned prerelease
  dependencies. The successful installation and component run are retained.
- T5 did not yield valid routes: six HTTP 500s, then a bounded diagnostic with
  another 500 and an HTTP 400 target-island error using numeric option encoding.
  Initial error bodies were not retained. Neither the cause nor the intended
  route-constraint behavior was established; do not rewrite this as feature absence.
- T7 first used an incompatible pyppeteer call signature, before navigation.
  `t7/access.json` is that harness failure, not site-access evidence. Corrected
  keyword arguments produced `t7-r2/`. Liberty interaction includes selector/input
  failures and one lost endpoint whose cause was not isolated. Its final stable
  outputs are the reported observations; automation clicks are no usability metric.
- The product's new experiment-reconstruction test failed first, then passed.
  Full Docker checks failed fetching the pinned uv image with GHCR HTTP 403;
  local and CI-contract checks were run separately. See verification, not an
  invented all-green status.
- Campaign recording first failed on a helper argument named `method`. The helper
  was corrected and recording resumed through the application using the retained
  operation log. No direct DB repair or silent deletion of previous records.

## Safe replay

Run commands from `/home/jonathan/startup_lab`. Existing results are evidence.
`executed/` preserves the effective successful T1–T4 and T6 script versions before
replay guards were added; those archived scripts may overwrite outputs and are
**reference-only**. Scripts beside this README now refuse an existing output
directory. T1 also requires fresh state. T3/T6 default to frozen revision-1 data;
current audited data is a different test input, not the original result.

For example, choose *unused* paths under the ignored local directory:

```bash
FOUNDRY_TRIAL_OUTPUT="$PWD/foundry/.local/portfolio-campaign/replay-t1" \
FOUNDRY_TRIAL_STATE="$PWD/foundry/.local/portfolio-campaign/replay-t1-state" \
foundry/.local/portfolio-campaign/mlflow-venv/bin/python \
foundry/docs/inquiry/portfolio-campaign/trials/mlflow_probe.py

FOUNDRY_TRIAL_OUTPUT="$PWD/foundry/.local/portfolio-campaign/replay-t2" \
foundry/.local/portfolio-campaign/change-venv/bin/python \
foundry/docs/inquiry/portfolio-campaign/trials/change_probe.py

FOUNDRY_TRIAL_OUTPUT="$PWD/foundry/.local/portfolio-campaign/replay-t3" \
python3 foundry/docs/inquiry/portfolio-campaign/trials/source_reuse_probe.py

FOUNDRY_TRIAL_OUTPUT="$PWD/foundry/.local/portfolio-campaign/replay-t6" \
python3 foundry/docs/inquiry/portfolio-campaign/trials/source_impact_probe.py
```

These environments remain available; installation is not required to read the
results. To recreate them, use isolated environments with the recorded Python and
frozen dependency files (changedetection resolution needs `--prerelease=allow`).
Do not install probe dependencies into the product environment. Fresh runs have
new trace/run IDs; compare assertions, versions and inputs rather than UUIDs.

T4/T5 or browser replay sends public requests. Freeze a new bounded protocol and
output directory, check access/terms and public input coordinates, and stop at
login/payment/unavailable-service gates. Repeating the known failed T5 requests
without repairing and specifying inputs adds no evidence. Browser helpers are
case-specific evidence, not a robust reusable automation library.

`record_campaign.py` and `record_route_case.py` are this campaign's persistence
scripts, using the application API and an operation log to resume exact calls.
They are not generic importers, atomic batch transactions or a safe concurrent
retry service. Do not replay them into a populated database after changing inputs
or removing their logs. The initial campaign's T1/T2 setup preceded the bulk log;
portable snapshots describe the resulting state, rather than claiming the bulk
script alone rebuilds it from an empty database.

Read-only reconstruction uses the existing CLI:

```bash
.venv/bin/foundry --store foundry/.local/portfolio-campaign/campaign.local.db \
venture show --id portfolio-campaign
.venv/bin/foundry --store foundry/.local/portfolio-campaign/campaign.local.db \
venture show --id v-route-repair
```

## Resources and cleanup

All campaign state is local and ignored under `foundry/.local/portfolio-campaign/`:
MLflow environment about 655 MB, changedetection/browser environment about 738 MB,
browser profiles about 173 MB total, and databases/artifacts a few MB. These are
observed disk sizes, not cloud charges. Exact setup/interaction times and human
effort were not benchmarked. No API token-cost saving is measured.

The probe browsers were closed and no campaign web service remains running.
Existing unrelated tooling processes were preserved. Keep the Foundry database,
MLflow states, operation logs and final evidence until a deliberate retention
decision. The isolated environments and anonymous browser caches can later be
removed/recreated individually if desired; no broad cleanup command is supplied
or executed. Hindsight installation and comparison remain pending and optional.
