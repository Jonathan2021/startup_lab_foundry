# Dependency alert triage — 2026-10-07

The first campaign push surfaced nine open Dependabot alerts. Their manifest
paths distinguish two current-lock issues from seven alerts in a retained
experiment environment. This is a bounded response to those alerts, not a full
security audit or evidence that the application was exploited.

| Scope | Finding | Treatment |
| --- | --- | --- |
| Current `uv.lock` | Mako 1.4.1; [GHSA-5639-2j2p-m4mx](https://github.com/advisories/GHSA-5639-2j2p-m4mx), patched minimum 1.4.2 | Add explicit patched minimum for Alembic's template dependency; lock resolves 1.4.3. The reported attack is Windows-specific template lookup; current development is Linux. |
| Current `uv.lock`, development | pytest 8.4.2; [GHSA-6w46-j5rx-g56g](https://github.com/advisories/GHSA-6w46-j5rx-g56g), patched minimum 9.0.3 | Update both dev/bootstrap constraints to `>=9.0.3,<10`; lock resolves 9.1.1. Recheck tests and supported Python versions. |
| Historical changedetection trial | Six cryptography alerts and one Werkzeug alert in `docs/inquiry/portfolio-campaign/trials/change-requirements.txt` | Preserve the original version receipt and results. Annotate the trial README against normal reuse of that stack. Resolve and validate a patched environment before any new trial; do not dismiss or hide the retained alerts. |

The root Foundry development environment was synchronized from the frozen updated
lock. Only Mako, pytest and the editable Foundry package changed. No trial
environment was started or installed into Foundry. No dependency alerts were
closed manually. Historical frozen environments are not production services.

Compatibility evidence is appended to `verification.json`; the post-patch GitHub
run checks Python 3.11/3.13, PostgreSQL, browser flows and the runtime image/Compose
path. Previous green results remain explicitly attributed to their earlier lock.
The source manifests and lock are the install authority, not this summary.
