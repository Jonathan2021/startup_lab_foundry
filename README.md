# Agentic Startup Foundry

The Foundry is a venture operating system for turning ideas into evidence-backed,
human-controlled execution. It retains assumptions, experiments, evidence,
assessments, decisions, work items, artifacts, and history so a venture can
continue without reconstructing context from chats.

The authoritative supplied brief is [docs/startup_foundry_project.md](docs/startup_foundry_project.md).

## Current scope

The product is in Stage 0: internal notebook replacement. The complete relational
domain map and schema regression were agent-prepared after portfolio analysis.
Slice 001 asks the learner to implement only a small SQLite-backed application
path for one venture's experiment, evidence, assessment, decision, work, and
artifact history. Agent-run, approval, portfolio-import, and automated-action
application behavior remains deferred until a real workflow needs it.

Agent EvalOps will be registered as the first venture after the Foundry foundation and delivery learning slices are usable. Its source remains in `../agentevalops/`; only its venture-management records belong in Foundry state.

## Start here

From the repository root:

```bash
make bootstrap
make test-regression
make test-slice
```

At the start of Slice 001, regression tests pass and slice acceptance tests fail. Read the [slice brief](../learning/slices/001-foundry-python-foundations/BRIEF.md) before implementation.

## Non-goals for the active slice

- no generic autonomous-company generator;
- no provider integration or prompt framework;
- no API server, PostgreSQL server, worker, Docker, cloud, or Kubernetes;
- no Agent EvalOps trace/evaluation domain;
- no automated external actions.
