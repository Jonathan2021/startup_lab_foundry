# Agentic Startup Foundry

The Foundry is a venture operating system for turning ideas into evidence-backed,
human-controlled execution. It retains assumptions, experiments, evidence,
assessments, decisions, work items, artifacts, and history so a venture can
continue without reconstructing context from chats.

The authoritative supplied brief is [docs/startup_foundry_project.md](docs/startup_foundry_project.md).

## Current scope

The product is in Stage 0: internal notebook replacement. Slice 001 completed a
small SQLite-backed application path for one venture's experiment, evidence,
assessment, decision, work, and artifact history. Slice 002 completed a
non-root image and readiness-aware PostgreSQL Compose path. Slice 003
used those existing boundaries as a real GitHub Actions CI workload without
expanding Foundry application behavior. Agent-run, approval, portfolio-import,
API, worker, and automated-action behavior remains deferred until a real
product workflow needs it.

Agent EvalOps will be registered as the first venture after the Foundry foundation and delivery learning slices are usable. Its source remains in `../agentevalops/`; only its venture-management records belong in Foundry state.

## Start here

From the repository root:

```bash
make bootstrap
make test-regression
make test-slice
```

Completed behavior is regression. Slice 003's accepted workflow has a
learner-authored foundation and agent-authored production hardening, with
attribution retained in its
[review](../learning/slices/003-github-actions-ci-fundamentals/FEEDBACK.md).
No next slice is prepared.

## Current non-goals

- no generic autonomous-company generator;
- no provider integration or prompt framework;
- no API server, worker, fake long-running process, cloud, or Kubernetes;
- no registry publication, release, production deployment, cloud identity, or
  write-authority GitHub workflow;
- no Agent EvalOps trace/evaluation domain;
- no automated external actions.
