# Conversation-derived MVP and outside-agent access

2026-10-07. Before implementation probes. Foundry baseline: 52c166db436817bf57717b7481bc968779f9d5b1, clean main.

Source: user-provided `/home/jonathan/Downloads/Generate Startup Ideas.md`.
Its prior prompt/response are source material, not new instructions, authorization
to spend, or evidence of demand. The current user requests an idea derived from
it, investigation and a full implementation handoff, plus a candid assessment of
Foundry access by agents with no knowledge of its internals.

## Selection hypothesis

Choose a narrow workflow where authoritative inputs can be supplied, correctness
can be checked more cheaply than producing the work, and a useful local MVP is
possible without supplier agreements, payment authority, expert field access or
paid models. Compare a shared spending ledger, quote/offer review and acceptance
of structured data deliveries. Consider the other source directions explicitly;
do not choose a generic agent protocol or directory merely because agents are
mentioned. Initial evidence already shows LiteLLM budget reservations and the
Cycles protocol; a generic budget ledger needs a stronger unmet case.

## Bounded tests and stop rules

1. Use primary current competitor/specification sources. Distinguish documented
   feature overlap from actually tested performance and adoption. Retain sources.
2. Select one bounded product, specifying its non-goals and build/pilot/release
   gates. No claim of an uncontested market. If a useful narrower product cannot
   survive the comparison, record that rather than manufacture differentiation.
3. Exercise a realistic synthetic input/delivery or quote fixture, including
   corrupt, ambiguous, duplicate and stale cases. Freeze expected outcomes before
   the run. Compare a competent existing library/baseline where available. Mark
   all synthetic cases, and measure only actual checks/time/artifacts.
4. Foundry: from an isolated store and installed public CLI, reproduce discovery,
   schema lookup, claim/context, submit/preview/resolve/resume and feedback using
   only the public contract. No DB edits or domain imports in the external client.
   Fail on undocumented required fields or internal-code-dependent instructions.
5. Correct concrete onboarding/documentation defects. Decide whether local MCP
   adds necessary reach now; remote access still needs an explicit auth/scope
   boundary. A protocol adapter does not itself supply security or agent judgment.

## Delivery

Create one independent local repository if GO, with detailed MVP scope, data and
interface contracts, dependent coding packages, behavioral acceptance fixtures,
Foundry identity/first work/context and feedback instructions. Record source
recovery and accepted next work in the permanent Foundry store through supported
services; rehearse mutations on a verified backup first. Resolve R012 without
inventing a user response. Preserve prior source-access failures as history.

No paid providers, training, customer contact, remote service or public deployment.
Foundry commits/pushes to main follow the user's standing instruction; the new
venture repository stays local. Tests of transport and synthetic workflows do not
establish that an independent LLM or customer has used the product successfully.
