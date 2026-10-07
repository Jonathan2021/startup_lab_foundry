# ADR-0016: Public agent contract before additional transports

2026-10-07. Accepted for the current local MVP.

## Context

The user asks whether unrelated agents can use Foundry without knowing its
internals, and whether MCP is needed. The CLI already exports schemas and exact
versioned operations. Repository handoffs incorrectly sent readers to source code
for ContextInput even though its schema was public. Claim/release schemas were
not published, and a missing configured SQLite store could be silently created.

## Decision

Document and test one self-contained outside-agent contract. Publish claim/release
schemas, add a configured CLI pass-through to the repository bridge, and reject a
missing explicitly configured SQLite store before invoking the CLI. Keep the
existing services, ownership, context and result guards authoritative. Verify a
full new-process checkpoint against a wheel from outside the source checkout.

Keep CLI as a supported interface. MCP is useful for host-native tool discovery,
especially hosts without shell access; it is an optional adapter, not Foundry's
domain or an agent execution engine. Do not add it without a named client and a
workflow whose connection actually requires it. The first adapter should be local
stdio, small, with purpose-specific tools and explicit preview/resolve separation.
Do not publish an unrestricted shell tool as a supposed MCP authorization boundary.

## Consequences

Trusted shell-capable agents can use Foundry without Codex or Python internals.
They still need installation/store configuration, a brief, and task authorization.
The protocol replay does not establish model usability or customer adoption.
Remote and untrusted agents are not supported merely because local claims work.

## MCP checkpoint

When a real local MCP-only host is selected, freeze its supported protocol/SDK
versions. Expose discover/resume, schemas, prepare/arrivals/fetch, record change,
claim/release, submit/show/preview and permitted resolution through the existing
service boundary. Default resolution tools to explicit coordinator enablement;
do not infer approval from tool presence. Bind an adapter to operator-selected
workspace scope. Verify discovery, paging, stale input, retry, cancellation and
error behavior with the actual host plus a protocol test client. Preserve CLI.

For remote access, first design auth and per-workspace authorization across every
path, credential handling, revocation, concurrency/rate limits and audit identity.
MCP supplies transport conventions; it does not supply this app-specific policy.
See [MCP architecture](https://modelcontextprotocol.io/docs/2026-07-28/learn/architecture)
and [authorization](https://modelcontextprotocol.io/specification/2026-07-28/basic/authorization).

Revisit after an actual host connection fails or repeated CLI onboarding friction
is recorded. Do not block OfferCheck or other venture implementation on transport.
