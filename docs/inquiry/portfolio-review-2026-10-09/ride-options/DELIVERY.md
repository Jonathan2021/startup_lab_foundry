# Ride Options (`v-route-repair`) — delivery 2026-10-09

Implementer: `implementer-ride-20261009`. Repository `/home/jonathan/startup_lab/ride-options`
(GitHub `Jonathan2021/ride-options`), workspace `6972ac19-0263-41c7-9f09-97b64fd99f80`.
Start: HEAD == origin/main `2d6fd6c` (PR #1, Actions 37930036947 success).

## Packages completed

| Package | Work id | Result id (accepted) | Commits | Actions run (exact SHA) |
| --- | --- | --- | --- | --- |
| RO-P0 record/checkout hygiene | `7701912a-2791-4d08-ae4a-50906f2e2fb8` | `2322ec6f-204c-55dd-948d-1631010aa123` | none (verified 2d6fd6c) | 37930036947 success on 2d6fd6c |
| RO-P1 target riding-time band | `16177cb6-162c-4a9e-b239-2225cceaab0e` | `6a38bb18-5e67-52ef-9583-214f7b8a9012` | d4c9225, fc4c25e | 37949876329 success on fc4c25e |
| RO-P3 navigation-safe GPX | `3bcf1079-022f-46a1-a6ef-7dccf86a0407` | `e82dd4fc-ac9d-578c-b883-26ae68f307bb` | 498fe10, c87312a | 37969991972 success on c87312a |
| RO-P4 small fixes + French | `127a870d-633a-4221-855f-4e85def2b551` | `31489c39-7ae4-511a-a1d7-ae8cc8e79973` | 4fbaaca, 6a86a6f, eb9ef30, 8e668ff | 37971408624 success on 8e668ff |
| RO-P5 restriction review | `90bd5d5d-e8b7-40cc-b1fd-9544e16affe6` | `f3b9f508-bf90-515c-8558-f12ec9be931c` | 53ca227, c0f775c | 37975693265 success on c0f775c |

All results were resolved `accept` with `coverage_action: accept_limitation`. Each
package ran `make check`, `tsc --noEmit`, an esbuild rebuild compared byte for byte
with the committed bundle and `make test-browser` before push. The test count went
from 129 to 183; browser flows went from 6 to 7.

### Facts per package

- **RO-P0**: `make check` 129 passed, tsc 0, bundle byte-identical, 6 browser flows.
  - PR #1 was recorded as evidence `8ce0832c-4b7b-40e4-a343-ba2693d3de22`.
  - Map revisions: `89693130…` removed the 9 duplicate R0x placeholders, added
    `ae6816fd`/`8436324d` tests→`pilot`, cancelled `6a6b1c22` and paused `281b3f40`.
    `a28cddbb…` cleared the review flags with keep treatments.
  - The 12/12 score `5276b9b1` already existed (total 35.0).
- **RO-P1**: `target_riding_minutes {min,max}` (default 240–300) with a bounded round-trip search (≤24 requests, ≤45 s) and honest "Closest found".
  - The spec was RED on 2d6fd6c and then passed: 16 tests.
  - Real local Auvergne engine, T03/T04 restated as 240–300: both in band after 9 requests. Loops of 249.3 min / 258.3 km and 257.6 min / 227.1 km. R06 had 0 in band.
- **RO-P3**: `<wpt>` stops and `<rte>` shaping points (about 10 km apart, at most 50) sit beside the unchanged `<trk>`.
  - The file validates against the vendored GPX 1.1 XSD; the test uses the `xmlschema` dev dependency.
  - `docs/GPX_IMPORT.md` documents the Kurviger import (vendor doc). No vendor import documentation was found for 68° or Liberty Rider.
  - Sample file: `evidence/ro-p3/T03-band-loop-249min.gpx`.
- **RO-P4**:
  - `avoid_unpaved` API default changed to False to match the form; a test pins it.
  - `client/app.ts` reformatted (378→1524 lines); the rebuilt bundle is byte-identical.
  - `verify_bundle.py` now uses a free port and a 30 s start; a local release build and verify passed.
  - The main flow is in French via `?lang=` or Accept-Language, with a new French browser flow.
- **RO-P5**: all 16 relations dispositioned: 6 enforce, 5 narrow, 5 omit (`docs/mvp/RESTRICTION_REVIEW.md`).
  - A fresh local re-import logged 47 ignored relations instead of 58.
  - Directed probes: the stock engine took 8 of the 9 forbidden movements; the repaired engine took 0.
  - The 5 omitted relations, plus 2 more found by the adapter, label nearby options.

## Intentionally not done

- RO-P2 `8436324d` (operator trial) and RO-P6 `1a384cb0` (conditional region) are human-gated or conditional, so they were not claimed.
- No navigation-app import, no accounts, no spend and no messages. The km/min delta after an import is an operator follow-up.
- No OSM edits.
- The operator's untracked `.env` (still 12 requests / 30 s) and `.local/auvergne` (stock import) were left untouched.
  - The repaired import is in `.local/auvergne-ro-p5b` (local only).
  - A `.env` value of 12/30 shortens the loop search.
- French covers the main flow only. Server explanations and the learning, break and detail panels stay English.
- Imagery/ML stays frozen (`281b3f40` paused).

## Remaining human gates

1. **RO-P2:** the founder runs R005 T01–T04 in Ride Options and in Kurviger. Record planning minutes, edits, the choice, "would repeat", and one GPX import with its km/min delta. The result decides continue or STOP.
2. **Road use:** 7 restrictions remain unresolved (labelled only), and legal/current access is unverified.
3. **RO-P6:** only if RO-P2 passes.

The map focus was restored to `ae6816fd` + `8436324d` (map `3c493b04-20d8-592e-88a4-c3738c610a4a`).

## Foundry feedback filed (all `recorded_for_review`)

| Id | Kind | Summary |
| --- | --- | --- |
| `72f11bd7-1e32-46ef-b11f-3a0a8dab42c1` | friction | Adding map edges flags work items for review using the full map rationale; `start` with the default budget claims the work and then fails. |
| `3ab2bb88-70b9-4019-9413-29a7c1d96c65` | friction | Accepting a result that has `next_work` replaces the map focus (the gate was lost after every package; the final accept left focus empty). |
| `f34ec599-5ee0-49c7-ace0-37d1339a292d` | positive | `resume` recovered the in-progress claim after a session interruption. |
| `a496b610-4fcf-4965-b731-ec28bb88ce8b` | idea | Add typed delivery/CI fields to results. |
| `53d4ad73-a298-4986-afe6-4662f60cd517` | friction | `next_work` cannot declare `depends_on`. |

The outbox files for these, and the reviewer's earlier `e691adf6`, `f935582d`, `bc8fb5b7`, `c2d19d42` and `74692ccf`, are committed under `feedback/`.

## Final state

- `git log -1`: `c0f775cbac88a46e2bf1617e2951097d15ba1617 docs: RO-P5 restriction review, repaired-import and directed-probe evidence`
- `origin/main`: `c0f775cbac88a46e2bf1617e2951097d15ba1617`. The working tree is clean (no untracked files), and no engine or app process is left running.
