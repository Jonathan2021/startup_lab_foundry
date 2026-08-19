# ADR-0006: Guarded reusable Foundry image delivery

- Status: Proposed for Slice 004
- Date: 2026-08-14

## Context

Foundry has an accepted read-only CI workflow, a non-root image, and container
acceptance checks. It does not have a delivery path. Adding registry authority
to pull-request CI would expose write capability to an untrusted event; copying
all image logic into an unrelated release workflow would allow verification and
delivery to drift.

Slice 004 must teach reusable workflows, a composite action, typed dispatch,
schedules, environments, GHCR, provenance, permission ceilings, and OIDC
concepts without deploying an application or provisioning a cloud provider.
Scheduled automation also has ongoing runner-cost implications and cannot
receive a human decision for each occurrence.

## Proposed decision

- Keep `.github/workflows/ci.yml` read-only and independently required.
- Add a caller workflow for typed manual dispatch and scheduled validation.
  Publication is a required boolean decision that defaults false. Automatic
  events never publish.
- Put candidate build/runtime evidence and optional publication in one reusable
  workflow with typed inputs and bounded outputs. Its default authority is
  empty/read-only. Caller job permissions are an explicit ceiling.
- Use a repository-local composite action only for release-metadata validation
  and normalization. Treat inputs as hostile data, pass them through step
  environment variables, and publish only validated outputs.
- Give package, attestation, and OIDC write scopes only to the caller's manual
  publication job. The called publication job inherits that ceiling, references
  the selected configured environment, and runs only for an explicit manual
  publication input. Every other called job explicitly downgrades its token.
  Do not redeclare write scopes in the shared called workflow: GitHub validates
  its permission graph against the read-only CI caller before an input-gated
  publication job can be skipped.
- Authenticate to GHCR with the ephemeral repository `GITHUB_TOKEN`; do not add
  a PAT or stored registry credential. Retain and attest the pushed digest.
- Treat the scheduled path as a freshness/portability validation. It may build
  and test but receives no write scope and produces no registry package.
- Use `id-token: write` only for digest provenance. No cloud audience, role,
  provider trust, credential, or resource is created in this slice.
- Require exact human approval of repository, commit, image, tags, visibility,
  environment, expected cost, and cleanup/retention intent before the first
  real publication. Workflow code alone is not that approval.

The learner still owns the skill-bearing choices: interface names, schedule,
job graph, runner, metadata format, build-transfer/rebuild approach, action
vendors and reviewed SHAs, output/summary shape, and environment configuration
supported by the actual repository plan.

## Consequences

- Validation and delivery share a reviewed job-level definition while write
  authority remains visible on the publication caller and read-only downgrades
  remain visible on every non-publishing called job.
- The composite action can be exercised with hostile inputs independently of
  registry publication, but it remains repository-local rather than becoming a
  premature public component.
- A scheduled validation consumes runner capacity after it reaches the default
  branch. Cadence and billing must be inspected before merge.
- Environments add useful history/protection only to the extent supported and
  configured for the repository's visibility and plan. A condition or input
  does not replace an unavailable reviewer control.
- Cross-job image handling must be explicit because hosted jobs do not share a
  Docker daemon or filesystem.
- Tags remain convenient names; downstream evidence and provenance must use the
  immutable digest.
- GHCR publication is package delivery, not application deployment. There is
  no rollout, runtime health observation, rollback, or production SLA here.

## Revisit when

Revisit when a second real product needs substantially the same delivery
workflow, when organization-level workflow/action distribution is available,
when measured scheduled-run cost justifies a different cadence, or when Slice
011 adds an approved cloud OIDC trust. Revisit before any production deployment,
multi-architecture release, signing service, external registry, long-lived
credential, or generic release platform.
