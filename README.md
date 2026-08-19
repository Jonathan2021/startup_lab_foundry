# Agentic Startup Foundry

The Foundry is a venture operating system for turning ideas into evidence-backed,
human-controlled execution. It retains assumptions, experiments, evidence,
assessments, decisions, work items, artifacts, and history so a venture can
continue without reconstructing context from chats.

The authoritative supplied brief is [docs/startup_foundry_project.md](docs/startup_foundry_project.md).
Time-sensitive competitor notes and product comparisons are maintained in the
[competitive landscape](docs/competitive-landscape.md).

## Current scope

The product is in Stage 0: internal notebook replacement. Slice 001 completed a
small SQLite-backed application path for one venture's experiment, evidence,
assessment, decision, work, and artifact history. Slice 002 completed a
non-root image and readiness-aware PostgreSQL Compose path. Slice 003 used
those existing boundaries as a real GitHub Actions CI workload without
expanding Foundry application behavior. Slice 004 prepares a guarded
image-package delivery boundary and GH-200 readiness gate; its current caller,
reusable-workflow, and composite-action files are intentionally incomplete and
grant no token authority. Agent-run, approval, portfolio-import, API, worker,
and automated product-action behavior remains deferred until a real product
workflow needs it.

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
The active
[Slice 004 brief](../learning/slices/004-advanced-actions-delivery-gh200-readiness/BRIEF.md)
and
[acceptance contract](../learning/slices/004-advanced-actions-delivery-gh200-readiness/ACCEPTANCE.md)
govern the intentionally red delivery work.

## Current non-goals

- no generic autonomous-company generator;
- no provider integration or prompt framework;
- no API server, worker, fake long-running process, cloud, or Kubernetes;
- no registry publication until an exact learner-controlled request is
  separately approved; no production deployment, cloud trust/resource, or
  long-lived delivery credential;
- no Agent EvalOps trace/evaluation domain;
- no automated external actions.
