# R014 — Agentic-stack wedge: decisions only you can make (2026-10-09)

Status: open. Affects venture `v-fleet-controller` (merged idea AS10) and the held
AS02/AS04 follow-ups. Source: [discovery report](../docs/inquiry/agentic-stack-2026-10-09/REPORT.md).
Nothing here authorises spending, publishing, provisioning or sending.

## R014.1 — Go / narrow / hold on building package C01 locally

C01 (outcome ledger for official CLI agent runs) is ready to claim. It only wraps
`claude -p` / `codex exec` runs on this repository and `kaggle/arc3` and writes a
local SQLite ledger. Building it is the first measurement of whether the quota and
routing pain is real on your workloads (stop rule: fewer than 50 real runs in two
weeks → hold).

Response:
- Decision (go / narrow / hold):
- Which two repositories should carry the ledger first (default: foundry, arc3):

## R014.2 — Working name and repository location

The venture is recorded as "Agent fleet controller for official CLI agents on
subscriptions". It needs a short working name and a home (default proposal: a new
sibling repository under `/home/jonathan/startup_lab/`, MIT, no hosted service).

Response:
- Working name:
- Repository path (or "default"):

## R014.3 — Subscription-policy stance

Anthropic's rules (read 2026-10-09) tolerate the unmodified `claude` binary under
your own login, forbid third parties from routing through or holding Pro/Max
credentials, and say limits assume "ordinary, individual usage"; the policy changed
five times in 2026. OpenAI recommends API keys for automation and runs partner plan
usage through "Sign in with ChatGPT"; unattended `codex exec` under a Plus/Pro login
by an unregistered orchestrator is unverified. The wedge is designed to never touch
credentials, but unattended fleet volume is your exposure.

Response:
- Accept the design constraint "spawn only unmodified official CLIs under my own
  login; no pooling, no proxying; shadow mode by default" (yes / changes):
- Are you willing to re-check both providers' terms before each public release (yes/no):

## R014.4 — ARC3 research-ledger retrieval experiment (AS04, internal)

R5 proposes a two-week, zero-cost retrieval A/B on the 329 existing ARC3 inquiry
records (typed ledger vs grep/BM25, Hindsight optional), with a pre-registered stop
rule. It touches only `kaggle/arc3/docs/inquiry/` read-only and reports under
`foundry/docs/inquiry/`. It is the next real trial for the ADR-0007 memory pilot.

Response:
- Approve the read-only experiment (yes / later / no):

## R014.5 — AS02 hold revisit (specialist factory)

R3 recommends a one-day metadata-only count (E0) once the C01 ledger has 60 days of
data; E1 would require installing SkillOpt-Sleep or GEPA, which can send transcript
excerpts to a provider. No action now.

Response:
- Note any privacy constraint for E1 ahead of time (optional):
