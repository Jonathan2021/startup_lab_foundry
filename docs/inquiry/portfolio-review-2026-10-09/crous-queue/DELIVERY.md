# Crous Queue — delivery, 2026-10-09

Implementer `implementer-crous-20261009`. Repository `/home/jonathan/startup_lab/crous-queue`
(GitHub `Jonathan2021/crous-queue`). Venture `f0b5abfe-0274-42f7-9c9a-72dcbe68c116`,
workspace `81ee3117-de70-411e-9856-07420859ffad`. Starting point: `cfd094c` (PR #1).
The venture is narrowed: no feature expansion.

## Packages completed

| Package | Work id | Result id | Commits | Actions run (exact SHA) | Conclusion |
|---|---|---|---|---|---|
| P3 Sybil and trusted-proxy hardening | `92380c5c-7da8-4b53-b8a6-32f3b144f87f` | `be6bc8b6-37c7-59b0-830b-65d6b18cca08` (accepted; decision `0121e9b0-6c9a-4f20-ad76-d8c31c2751ed`) | `d6b8b3b`, `dabc81c`, `ce48159`, `092bba2` | `37948283870` on `092bba24d0767c7075c0258d902a8c22e9719c9a` | success (85 core, 15 browser, 85 kit) |
| P5 UI honesty polish | `724cd024-36ee-474c-85f7-94859371e6c7` | `d372094d-88f3-5476-9788-64db17d27ec9` (accepted; decision `5ceee4e6-b293-478a-a104-b77d8de980ba`) | `491ac01`, `a4f0487` | `37970042546` on `a4f048703ac7a98b68a44c583cb66ac6e35b977d` | success (90, 16, 90) |
| P4 Hosted private-beta approval payload | `d6baa01f-cc8e-4e91-af1d-c42ea88b3f89` | `211623f5-bcd0-55fa-a39b-0f97903631d0` (accepted; decision `36208822-1a22-42b9-9395-181a96b83988`) | `074ffae`, `784246e` | `37971430794` on `784246e24166aef0174766bc543904570c82272d` | success (90, 16, 90) |

Failed run, kept for the record: `37947027606` on `ce48159` failed. `scripts/release_manifest.py`
pinned exactly 6 packaged migrations, and I had not replayed the release steps locally
before that push. `092bba2` fixed the pin. Later packages replayed the full CI sequence
in a clean clone before pushing.

### Key facts

- **P3.** Reproduced on a scratch copy of the dev database: six fresh cookies gave six
  201s and `recent, 120 min, count 6`. After the fix, the same script gives six 201s and
  `count 2, sources 1, excluded 4`.
  - Version 0.2.1, migration 0007: a 24-hour network key per report and a per-network
    counting budget (`CQ_NETWORK_ESTIMATE_CAP`, default 2) for waits and meal/seat
    observations.
  - Forwarding headers are honoured only from `CQ_TRUSTED_PROXIES` (default none),
    using one selected header and the rightmost untrusted hop.
  - The network hourly ceiling is configurable. Admins can bulk-hide a network bucket.
    The UI says "N appareils · K réseaux".
  - ADR-0009 documents the abuse model: it limits repeats and bursts from one network,
    not identities. Device-age gating was not adopted; the reason is in ADR-0009.
  - `DEPLOYMENT_PROPOSAL.md` and `proposal.json` were refreshed from 0.1.2/0003.
- **P5.**
  - Unknown hours no longer render any "Service :" text.
  - Stale and conflicting intervals say why.
  - Regions show human labels.
  - The footer dates the directory ("relevé le 07/10/2026") next to Licence Ouverte,
    and a banner appears after 30 days.
  - Dates use DD/MM/YYYY.
- **P4.** `deploy/PRIVATE_BETA_APPROVAL.md` (NOT AUTHORIZED):
  - Build: wheel sha256 `bafceb5b…`.
  - Host: Scaleway DEV1-S in fr-par-1 at €0.00898/h before tax. IPv4 and storage
    prices are unknown until a console quote.
  - Cost: €25/month ceiling; stop if the quote exceeds €20 including VAT. Lifetime at
    most 21 days.
  - Access: invite cookie. `/admin` is limited to the operator's IP and still needs the
    bearer token.
  - Also covers retention, moderation duty, secrets, rollback, teardown, a dry-run
    checklist and 8 human inputs.
  - The PostgreSQL branch passed on a throwaway local 18.6 cluster: migrations,
    concurrent retries and throttle, network budget, admin conflict, UTC, retention,
    dump/restore. The cluster was deleted afterwards.
- **Record hygiene.**
  - Evidence `c38602e1-3806-4d12-be38-9cf337ab3700` records PR #1 (cfd094c, run 37928637963).
  - `dbbfbb3d` was cancelled as superseded by the human Android check in R011.
  - Map revision `252496e4` added the question `five_lunch_coverage_gate`, which P6
    tests, and set the focus on it.
  - Revision `7318ce7b` kept P3 to P6 explicitly to clear the `needs_review` noise.
  - Final resume: `needs_review` is empty.

## Intentionally not done

- **P6 not claimed.** It is human-gated.
- **No hosting, accounts, domain, spend or messages.** Teardown commands and the Caddyfile
  are unvalidated drafts; Caddy is not installed locally.
- **PostgreSQL 16 not verified.** The production target is 16 but I verified on 18.6;
  rerunning on 16 is a listed gate.
- **No English UI, no "Crous" trademark check, no conditional-map-node pruning.** These
  are not in my packages; the pruning belongs to coordinator package P2.
- **Local release replay incomplete for P5.** `verify_release` hit the host disk quota
  (OSError 122) in my clean-clone replay. CI ran it.

## Remaining human gates

1. **R011** (`4626ac2b`): queue type and ordinary access.
2. **Android incumbent check** (Affluences, CrousRadar, Croustillapp) for live
   Cuvier/Châtelet data. STOP if an incumbent shows it.
3. **Approve or reject** the exact payload in `deploy/PRIVATE_BETA_APPROVAL.md`. This
   needs: operator name and privacy contact, hostname, provider account, console quote,
   operator IP and invite code, and approval text naming the commit and wheel sha256.
   The pinned CI artifact expires 2026-10-16.
4. **P6** (`12c7e034`): the five-lunch test against the pre-registered thresholds.

## Feedback filed (all `recorded_for_review`)

- `ab89b18a-8302-4f4c-9104-8a7e44b420cb`, friction: a map revise flagged all current
  work as `needs_review` and needed a second "keep" revision.
- `176c4619-4714-4286-b566-4ded3617fb7b`, positive: `start --resume-owned` refreshed
  context after my own map revisions.
- `05edb95a-f95d-4958-8c7d-a2716c1ab241`, friction: later work items carry stale
  literals, here "0.2.0/0006".

## Final state

- `git log -1`: `784246e24166aef0174766bc543904570c82272d docs(deploy): exact NOT AUTHORIZED private-beta approval payload`
- `origin/main`: `784246e24166aef0174766bc543904570c82272d`, with a clean working tree.
- Foundry map head: `4dfad8e8-400a-53ef-ad35-36c533ad2d9a`. Open work: P6 (blocked) and
  R011 (blocked, human).
