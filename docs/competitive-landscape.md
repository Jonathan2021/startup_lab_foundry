# Competitive landscape

This document records time-sensitive market observations for the Agentic
Startup Foundry. It complements, but does not redefine, the authoritative
[product brief](startup_foundry_project.md). Vendor claims are identified as
such and should be rechecked before they drive a product decision.

## NanoCorp

**Last reviewed:** 2026-08-18  
**Relationship:** future direct competitor; current adjacent benchmark

[NanoCorp](https://www.nanocorp.so/) presents itself as a hosted platform that
turns a one-sentence company description into a running software business. Its
agents build and host the application, configure payments and email, prospect
for customers, and run Meta advertising. The founder steers the system through
a CEO agent.

This overlaps strongly with the Foundry's eventual ambition to coordinate
agents and humans across venture execution. It is not a feature-for-feature
competitor to the current Stage 0 Foundry, which is an internal, durable
notebook replacement for evidence-backed and human-controlled venture work.

### Comparison with the Foundry

| Dimension | NanoCorp | Agentic Startup Foundry |
|---|---|---|
| Primary promise | Create and operate a company from one prompt | Turn ideas into evidence-backed ventures with durable, human-controlled execution |
| Primary user | Non-technical founders seeking a quickly launched software business | Initially an internal founder/operator launching real child ventures |
| Starting point | One company description | An idea portfolio, explicit assumptions, and uncertainty |
| Core workflow | Build, deploy, sell, advertise, and report through a CEO agent | Evaluate, experiment, retain evidence, decide, execute, and learn |
| Optimization target | Revenue, constrained by company and credit budgets | Quality of evidence and decisions, safe progress, and reusable venture knowledge |
| Autonomy model | Long-running agent execution with coarse autonomy and budget controls | Progressive delegation with exact approval of consequential actions |
| Human control | Mission steering and selected high-level controls; NanoCorp says it has no per-action approval gate | External actions freeze payload, risk, cost, and expiry before explicit approval |
| Durable state | Hosted company, code, task/chat history, integrations, and operational results | Assumptions, experiments, evidence, assessments, decisions, work, artifacts, agent runs, approvals, and receipts |
| Product ownership | NanoCorp-managed hosting and private repository; repository access is available on higher tiers | Provider-, model-, storage-, and executor-independent domain boundaries |
| Business model | Subscription and usage credits, plus a vendor-documented 20% withdrawal fee | Not yet commercialized; initially an internal bootstrap system |
| Current maturity | Commercial hosted product with product, payments, email, advertising, and agent operations | Stage 0 local application; agent execution and external-action adapters are intentionally deferred |

### Strategic interpretation

NanoCorp validates demand for a recognizable "AI company operating system"
category and is a direct competitor if the Foundry later promises instant,
autonomous company creation to non-technical founders.

The stronger differentiation is for the Foundry to remain the venture control
plane that knows:

- what should be built and which assumptions remain unproven;
- what was attempted, what evidence resulted, and why decisions were made;
- which actions an agent may take and which exact actions require approval;
- what knowledge and workflows can be reused across otherwise independent
  ventures.

Under that positioning, NanoCorp may also become a potential execution adapter
or benchmark rather than only a competitor. The Foundry should not race a
hosted generator on landing-page deployment speed unless real venture friction
shows that capability is necessary.

### Validation questions

1. Do founders value explicit validation before an agent invests in building
   and distribution?
2. Does granular approval become important after an autonomous system makes a
   costly, reputational, or difficult-to-reverse mistake?
3. Do multi-venture operators need portable evidence and decision history
   outside the platform that executes their work?
4. Can the Foundry advance a venture by delegating bounded execution to a tool
   such as NanoCorp while retaining authoritative evidence, approval, and
   decision records?

### Sources

All product and pricing statements below are NanoCorp's own descriptions unless
otherwise noted:

- [Product homepage](https://www.nanocorp.so/)
- [Documentation overview](https://docs.nanocorp.so/)
- [Plans and credits](https://docs.nanocorp.so/plans-and-credits)
- [CLI quickstart](https://docs.nanocorp.so/cli)
- [GitHub access and operator permissions](https://docs.nanocorp.so/github-access)
- [Advertising controls](https://docs.nanocorp.so/advertising)
- [NanoCorp's explanation of its autonomy model](https://www.nanocorp.so/blog/nanocorp-vs-polsia)
- [Y Combinator company profile](https://www.ycombinator.com/companies/nanocorp)
