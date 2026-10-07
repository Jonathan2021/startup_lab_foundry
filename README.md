# Agentic Startup Foundry

Foundry keeps a venture's purpose, evidence, decisions and next work connected
as things change, from the first investigation through everyday operations.
Use the local UI or your existing agent through the CLI. Several ventures can
share a portfolio; each retains its own history and work.

The [local lifecycle MVP](docs/LIFECYCLE_MVP.md) is implemented. It includes
versioned decision maps, attributed changes, concise agent context, reviewed
results, evolving assessments, human input and explicit portfolio fusion.
See the [release evidence](docs/inquiry/lifecycle-mvp-2026-10-06/REPORT.md).
Monetization, managed agents, training and hosted multi-user operation are deferred.

Agents outside Codex can use the [public agent contract](docs/EXTERNAL_AGENTS.md)
with local shell access and a configured store. The repository helper handles
claims, saved context and feedback; `cli` exposes the remaining public commands.
There is no MCP server or authenticated remote agent endpoint yet.

The preserved supplied brief is [docs/startup_foundry_project.md](docs/startup_foundry_project.md).
The [current direction](docs/CURRENT_DIRECTION.md) and
[ADR-0008](../docs/adr/0008-evidence-first-venture-realignment.md) govern investment
as of 2026-10-02: internal use under evaluation, without a validated platform business.
Time-sensitive competitor notes and product comparisons are maintained in the
[competitive landscape](docs/competitive-landscape.md).

## Current scope

The console provides Today, portfolio views and scoped venture workspaces. A
venture's Now page captures changes, prepares agent context and reviews results.
Its map retains purpose, questions, conditional alternatives and exact links to
work and evidence. History, scores and optional software/outreach views remain
inside the venture. The portfolio owns comparison and fusion. Shared inbox and
outreach screens are projections of records with explicit ownership.

Your agent reasons and researches; Foundry performs typed, transactional record
operations. Preparing context does not start a worker. Stale results remain
readable but cannot apply old changes. No model or paid executor is required.

The permanent SQLite default is `~/.local/share/startup-foundry/foundry.local.db`
(or `$XDG_DATA_HOME/startup-foundry/foundry.local.db`). Existing PostgreSQL support
and completed container/CI/delivery checks remain available. No publication or
remote deployment follows from starting the console.

Agent EvalOps is the first documented stop-or-pivot case and is deferred as a
standalone product. Its source remains in `../agentevalops/`; its venture decision
belongs in Foundry. The current
[portfolio campaign](docs/inquiry/portfolio-campaign/REPORT.md) compares existing
tools and records dispositions across all supplied ideas. The earlier
[research handoff / G002](docs/ventures/research-handoff.md) is one preserved
protocol, not a committed product. Agent-operated trials have established some
incumbent capabilities, but no paid demand or semantic-memory advantage.

## Start here

From the repository root:

```bash
make bootstrap
make foundry-ui
# Browse http://127.0.0.1:8765; stop with Ctrl-C.
```

Useful CLI commands, in another terminal:

```bash
.venv/bin/foundry storage info
.venv/bin/foundry venture list
.venv/bin/foundry idea list --query route
.venv/bin/foundry idea show --id N008
.venv/bin/foundry source list --query Distill
.venv/bin/foundry evidence list --venture-id v-route-repair
.venv/bin/foundry step start --subject idea --subject-id D001 --kind research_brief --request-key my-d001-brief-1
.venv/bin/foundry storage backup --output /tmp/foundry-snapshot.local.db
```

A backup refuses to overwrite an existing file. Reusing a step request key returns
that run; a fresh evaluation needs a new key. A successful readiness step checks
input completeness and **does not qualify a business**. Ideas are hypotheses;
opening a venture workspace is an investigation, not a build decision.

Reply inline in [requests/INBOX.md](requests/INBOX.md). The UI displays those files;
it does not consume replies automatically. The next agent session reads the replies
and records the resulting evidence/decision. Do not put credentials in the inbox.

See [DEVELOPMENT.md](DEVELOPMENT.md) for configuration, restore, tests, migration
and adapter details, and [ARCHITECTURE.md](ARCHITECTURE.md) for boundaries.

## Current limits

No model downloads/training, unattended agent queue, automated commercial scoring,
external messages or actions, remote multi-user access, or validated platform
business. The original [portfolio campaign](docs/inquiry/portfolio-campaign/REPORT.md)
remains preserved history; current operations use the permanent database.

The [October 4 handoff execution](docs/inquiry/handoff-2026-10-04/README.md) adds
explainable original/reviewed scores, portfolio filters, separate investigation /
product maturity / disposition reviews, existing-project checkpoints, editable
manual outreach drafts and built-in `/help`. Run `foundry ui --port 8765`, then
open the local console. Drafts have no delivery provider. The permanent store
contains the imported workbook history and current investigations; real-user and
expert-access gates remain in [dated follow-ups](requests/2026-10-04-followups.md).
See [development commands](DEVELOPMENT.md) for JSON input formats and backup/configuration.
