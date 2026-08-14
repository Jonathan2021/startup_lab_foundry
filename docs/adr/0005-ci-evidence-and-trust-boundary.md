# ADR-0005: Foundry CI evidence and trust boundary

- Status: Proposed for Slice 003
- Date: 2026-08-13

## Context

Foundry now has a locked Python workload, completed local checks, a non-root
image, and PostgreSQL orchestration. Pull requests still provide no remote,
reviewable evidence that these boundaries hold on a clean runner. The CI design
must teach GitHub Actions fundamentals without publishing images, deploying,
using repository secrets, or coupling Foundry to the parent learning workspace.

## Proposed decision

Keep Foundry's CI workflow in the independent `foundry` repository. Validate
pull requests and the protected branch with least-privilege permissions and
concurrency cancellation. Split evidence by concern:

- a locked Python matrix checks the minimum supported Python and the container's
  Python version, then produces lint, type, and non-container test evidence;
- a PostgreSQL service-container job applies the checked-in migration and runs a
  small real CLI create/show path with synthetic credentials;
- an image job builds the existing Dockerfile and verifies its non-root identity
  and CLI entry point without publishing it; and
- one stable gate depends on all required jobs so branch protection need not
  follow matrix-generated check names.

External actions must be reviewed and pinned to immutable full commit SHAs.
Dependency caches are acceleration only and are keyed from locked inputs;
artifacts are bounded, non-sensitive diagnostic evidence. The untrusted pull
request workflow receives no write permission, environment approval, cloud
identity, or publishing credential.

## Consequences

- Clean-runner evidence becomes repeatable and reviewable, but GitHub-hosted
  execution adds queue/runtime variability that local checks do not have.
- Python matrix coverage catches compatibility drift at additional runner cost.
- Service containers use runner networking, which differs from the existing
  Compose service-DNS path and therefore requires explicit diagnosis.
- Full action pins improve immutability but require an intentional update
  process; a release label in a comment keeps the reviewed version legible.
- Cache hits cannot be treated as correctness evidence, and uploaded artifacts
  must not contain credentials, local dotenv files, venture payloads, or images.

## Revisit when

Revisit in Slice 004 when reusable/composite workflows, manual or scheduled
delivery, GHCR publication, environments, provenance, or OIDC are introduced.
Revisit earlier only if measured runner cost or duration makes the matrix
unreasonable, or if Foundry gains a second independently testable runtime.
