# ADR-0012 Hash-pinned official uv build source

2026-10-06. Status: implemented; runtime checks recorded in the repair report.

## Context

The official image acceptance path repeatedly fails to authorize
`ghcr.io/astral-sh/uv:0.11.29`, first HTTP 403 on token retrieval and later a denied
manifest request. The host tool is already uv 0.11.29. The repair handoff permits
an equivalent reproducible official source while retaining pins and required
security checks. A cached old Foundry image is insufficient evidence for new code.

## Decision

Install official uv 0.11.29 wheels from PyPI in the Docker build stage, using
`--no-deps --only-binary=:all: --require-hashes` and the explicit official index.
`uv-build-requirements.txt` pins the same release and published SHA-256 values for
Linux amd64 and arm64 wheels. Astral documents this distribution in its
[installation guide](https://docs.astral.sh/uv/getting-started/installation/#pypi);
hashes were checked against the
[pinned release metadata](https://pypi.org/pypi/uv/0.11.29/json).
Retain `uv sync --frozen --no-dev`, the separate runtime stage, non-root UID and
secret/dev-file exclusion. Do not install build tooling into the application
runtime environment or weaken acceptance checks. The package format changes;
we do not claim byte identity with the GHCR binary.

## Consequences

Builds no longer need the GHCR uv image. They require official PyPI wheel access;
an unexpected artifact or unsupported wheel fails hash verification. The Linux
amd64 runtime is exercised locally; arm64 hashes are retained but that platform
is not claimed tested. The existing Python base-image and runtime dependency
policies are unchanged. Pin/hash updates are deliberate dependency work, not an
automatic fallback to latest or an unverified mirror.

## Revisit conditions

Revisit if the supported base/platform changes, the wheel distribution stops
being available, or a verified digest-pinned GHCR path has an operational benefit.
Retain reproducibility and the same required image/security/PostgreSQL gates.
See the [repair report](../inquiry/revamp-fixes-2026-10-06/REPORT.md).
