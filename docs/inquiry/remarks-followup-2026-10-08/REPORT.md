# Delivery reconciliation, Foundry upgrade and remarks handoffs

Reviewed 2026-10-08. OfferCheck and Volley Coach remain aside. This pass directly
repairs Coopain's local checkout and Foundry coordination behavior; the three new
feature continuations are handed off for implementation, not claimed complete.

## Coopain resolved

GitHub delivery was real: main already contained `f3a8c13e52adf620d89620a831d721caad50be28`,
with successful [Actions run 37791874356](https://github.com/Jonathan2021/coopain/actions/runs/37791874356).
The canonical `/home/jonathan/startup_lab/coopain` folder was still at `aa382779`.
Comparison of every dirty/untracked file found 172 paths identical to the delivery
agent's scoped checkpoint `d9f5466681653c63f763cd8eef930e7f6527f29b` and 24 unique
operator/generated/support files absent from that checkpoint; no newer source
edits were discovered. A retained stash and private archive preceded a fast-forward.
All 24 unique files were restored without collisions. Ignored environments, local
runs and data remained in place. Tracked source is clean, HEAD equals origin/main,
and seven unrelated untracked files remain intentionally. No redundant push needed.
Other historical worktrees are unchanged.

Recovery archive and inventory:
`/home/jonathan/.local/state/startup-foundry/recovery/coopain-20261008/`.
Permanent recovery ref: `refs/recovery/coopain-pre-sync-20261008`, pointing to
`7ec8c2f2401d4f1bd1ffa841efdded9d6ebbca8b`. Inspect with `git stash show` or restore
individual files into a separate recovery directory/worktree. Do not blindly apply
the entire old stash over the new delivered application. Full receipt:
[coopain-reconciliation.json](coopain-reconciliation.json).

## Current private GitHub provenance

| Repository | Main HEAD | Exact-head successful Actions |
| --- | --- | --- |
| coopain | `f3a8c13e52ad` | [37791874356](https://github.com/Jonathan2021/coopain/actions/runs/37791874356) |
| crous-queue | `699eebf63f8a` | [37772856832](https://github.com/Jonathan2021/crous-queue/actions/runs/37772856832) |
| ride-options | `c08c438ba8d0` | [37764771577](https://github.com/Jonathan2021/ride-options/actions/runs/37764771577) |
| volley-match | `96e4ae94acc9` | [37762687240](https://github.com/Jonathan2021/volley-match/actions/runs/37762687240) |

These CI results were verified through GitHub during this pass. They cover the
second-run application commits, not the newly added local handoffs/helper updates
or the future requested features. Independent app test suites were not rerun just
to repeat existing release evidence. This is not a new full application/security
certification. Details: [github-final.json](github-final.json).

## Foundry feedback disposition and upgrade

Current local bridge/public contract: **2026-10-08.1**, canonical helper SHA256
`3911d27334f0f05a4643913b3c0d681d77a6cd45a4ae6dcd9b5ca4b7b06a2e5e`.
Installed into Foundry, Crous Queue, Ride Options and Volley Match; each doctor
verified version/hash/configuration. Dormant apps and Coopain's delivered helper
were left unchanged. The existing editable local CLI serves the new contract.
No database migration, generic release framework or automatic Git action added.

- Ride Options friction `5dc313c3-bd38-494f-bd31-442cce31e69e` (Foundry evidence
  `f6742d1d-c97a-446a-a457-d2cb7bd410c4`) is fixed. Accepted descendant results now
  annotate unresolved originals as `superseded`, with `superseded_by` pointing to
  the accepted replacement. Immutable proposals/digests/stale reasons remain.
  Pending, rejected and deferred descendants do not retire originals. Chained
  replacements and paginated result views work. The console's attention lists and
  detail page show the same semantics instead of offering repeated reconciliation.
- Real Ride Options result `1fa55e4b-c96f-591f-9d6e-82edd4e1096d` changed from
  `needs_reconciliation` to `superseded`, linking accepted `09300511-4d10-5858-9330-2d5e507048e4`.
  Its original digest is unchanged. Retained before/after resume evidence proves
  the real feedback case, not just a synthetic test.
- The Coopain discrepancy is addressed in public workflow guidance and every new
  handoff: distinguish canonical checkout/worktree, local commit, remote branch,
  main merge and exact CI head, and preserve explicit recovery for dirty files.
  Newly retained friction/receipt links this requirement to actual evidence.
- Latest Q07/J06/C07/O07 feedback supports keeping explicit doctor hashes,
  evidence/full-map coverage, owned resume and exact review pins. No additional
  platform feature was justified by those positive reports. Earlier timeout,
  schema and map-label issues remain covered by the preceding upgrade; no claim
  that the old intermittent latency's root cause was established.

Validation: focused suite **26 passed**; final supersession/console regression
**4 passed**; full `make test-product` **156 passed, 1 skipped** (optional PostgreSQL
requires an explicit test DB); Ruff and strict mypy pass. CLI lifecycle replay and
immutable result behavior are included. Current code changes add no schema fields
or migrations; no fresh PostgreSQL/container run claimed. Evidence logs retained.
The first test-authoring attempt used the wrong service method name; corrected
before recording the meaningful red behavior in `foundry-red.txt`.

## Remarks continuation plans

- **crous-queue**: [handoff](/home/jonathan/startup_lab/crous-queue/docs/mvp/REMARKS_HANDOFF.md), first ready work `e5d292f5-02cd-4d6a-a266-ac413b60e64f` (unclaimed).
- **ride-options**: [handoff](/home/jonathan/startup_lab/ride-options/docs/mvp/REMARKS_HANDOFF.md), first ready work `22e53596-28f7-453a-bcbc-228224144a7b` (unclaimed).
- **volley-match**: [handoff](/home/jonathan/startup_lab/volley-match/docs/mvp/REMARKS_HANDOFF.md), first ready work `4ca1f74c-7bf9-4e5c-8461-41e9a8af1c15` (unclaimed).

Crous Queue: official source-backed hours → nearby map → independent meal/seating
reports and moderated free text → verified release. Ride Options: immediate pins,
unified itinerary and working engine → addresses/radius constraints → landscape,
scenic control points and POI breaks → bounded imagery/preference/NL foundation →
verified release. Volley Match: full UX repair → versioned rules/confirmation →
standalone/public-private sessions and admission/removal semantics → verified release.

Every root remark is mapped to behavior and acceptance. Original `remarks` files
are unchanged. Existing phase documents remain historical; agents must reconcile
new product contracts and conditional roadmap before implementing dependent work.
User remarks and handoff references were recorded as attributed evidence in each
owning venture. Real-use, physical safety, paid actions and public release gates
remain separate; existing scoped private Git/CI authorization persists.

[Copy-paste prompts](PROMPTS.md). New Foundry, helper and handoff edits remain local
and uncommitted under the repository rule; no Foundry commit/push was requested.
Agents' continuation prompts explicitly require scoped private delivery.

Coordinator checkpoint: accepted result `db79ea00-e3c8-59d7-95b5-8c2531d673db`, completed work
`877c61e4-af2b-419a-92f4-996f80333236`. Final Foundry resume has no unreviewed
evidence from this package. See [receipt](foundry-checkpoint.json). Shared tooling
feedback was linked into the central inquiry-memory folder; no memory service was used.
