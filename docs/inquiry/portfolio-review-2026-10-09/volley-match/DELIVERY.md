# Volley Match: delivery, 2026-10-09

Implementer `implementer-volley-match-20261009` (claude-opus-5-5). Repository
`/home/jonathan/startup_lab/volley-match` (Jonathan2021/volley-match). Venture
`v-sports-session`, workspace `417476af-0674-4aba-9022-843957dc3ca2`. Starting point:
HEAD == origin/main == `991d702` (PR #1).

## Packages completed

| Package | Work id | Result id (accepted) | Commit(s) | Actions run | Conclusion |
|---|---|---|---|---|---|
| VM-R1 record hygiene + checkout sync (review VM-R1 agent part + VM-R2) | `098b4a0b-b703-49c8-ac63-0e5f44d62403` | `09ac7dd6-0c9a-581c-8e12-59479f79c7cb` (supersedes `f415e8e3-…`, stale work-treatment versions) | none (verified `991d702`) | 37928573496 | success |
| VM-R3 copy-for-WhatsApp summary | `b07ce566-5adb-452d-81a7-449f47cd55ea` | `7033140c-871d-5d92-8295-2097ab528a22` | `87e76cd` | 37946112249 | success |
| VM-R4 rating-rule transparency | `bee9caef-08ed-478e-a7c5-fc9631c21c4e` | `891768bc-9ac1-5154-abaf-e04a23abe5e8` | `b3666ea` | 37947620068 | success |
| VM-R5 browser harness diagnosability | `b622d63e-6a2c-4a60-a09c-da5b4a28d6f6` | `e434772b-2c6a-528e-afa8-6afe281bf133` | `6462e00` | 37949947178 | success |
| VM-R8 template de-minification + dates | `35de8d78-0fc4-4597-97ea-91c664b12d00` | `a2d902af-5acf-5e1c-8b43-c5d5c639f41e` | `1517010` | 37970831604 | success |
| post-R8: feedback outbox commit | — | evidence `9145b6be-2e71-4c61-9267-5a165bf061b7` | `9b09f1d` | 37971670254 | **failure** (V10 browser race) |
| post-R8: V10 test race fix | — | same evidence | `5b02522` | 37972574492 | success |

Local checks (all with Playwright bundled Chromium, `VOLLEY_BROWSER_EXECUTABLE=""`):

- VM-R1 on `991d702`: `make check` 132 passed. `make test-browser-all` passed 3
  consecutive runs. Runs 1–2 used the unmodified tree; run 3 already contained
  VM-R3 work in progress. The core replay was not flaky in these runs.
- VM-R3: 135 passed; browser suite (adds `share.py`) passed.
- VM-R4: 139 passed; browser suite passed.
- VM-R5: 141 passed; browser suite passed 3 consecutive runs. The core restart replay
  passed 3/3 under an extra 12-process CPU burn (load average 14.6–18.7).
- VM-R8: 144 passed; browser suite and the 390 px organizer rehearsal passed.
  Rendering evidence is in `volley-match/.local/vmr8/compare.txt` (Git-ignored):
  - 21 seeded pages after formatting only: 0 of 21 differ, ignoring whitespace next
    to block tags.
  - After the date changes: only the intended date and zone strings differ.
  - Screenshots of 10 pages at 1280 and 390 px, taken back to back: 16 of 20 are
    pixel-identical. The other 4 differ only in regions that also differ between two
    unchanged baseline runs (tie order).
  - CSS tokens are identical.
- `V10` fix: `tests/browser/v10.py` passed twice locally at 1280 and 390 px.

Foundry records:

- Evidence `9d6d27b9-a6cd-4272-99cb-7a7d8694d7a5` records PR #1, `991d702` and
  run 37928573496.
- Decision-map revision `e2238680`:
  - set focus to the two-outing pilot gate;
  - made VM-R6 `tests` the gate and VM-R7 `depends_on` it;
  - removed the duplicate placeholder alternatives V01–V05 and V09–V11.
- The final revision is `3fe462d6-37f6-52e2-98fc-454913987bbc`, with focus on
  `pilot` and VM-R6. Every acceptance had moved the focus away, so I restored it.
- `resume` shows `needs_review` empty. Only VM-R6 and VM-R7 remain, both blocked.

## Intentionally not done

- **Fusion proposal `91fe8686`, `v-sports-ranking` lineage, score reassessment (~37):**
  each needs a human or coordinator decision. They are not in an implementer's
  authority.
- **VM-R6 and VM-R7:** human-gated or conditional. I did not claim them.
- **Links in the WhatsApp text:** the coordinator said no links to private pages, so
  the text contains none.
- **Elo rule:** I explained it but did not change or compare it (OpenSkill etc.).
- **Repeated status-label dictionaries in templates:** I did not consolidate them.
- **No hosting, accounts, spend, messages or real people.** All data is synthetic.

## Remaining human gates

1. R006 (`foundry/requests/2026-10-07-volley-match-R006-pilot-access.md`) needs an
   organizer, an access arrangement, a consent/retention owner and a spending cap.
   VM-R6 cannot start without it.
2. Resolve fusion proposal `91fe8686` as superseded by decision `a38e9141`, and set
   `v-sports-ranking` to merged lineage.
3. Reassess the stored score: 47, stale; the review proposes ~37. The venture stage
   still shows "discovery".

## Feedback filed (all delivered with receipts and committed under `feedback/`)

| UUID | Kind | Summary |
|---|---|---|
| `90806f7d-5222-4589-b801-b693d94924aa` | friction | A map revise bumps work versions silently. The stale-treatment error names no work id. Acceptance replaces the focus. |
| `77d088f2-3db7-42ee-99b2-122e205d5303` | positive | The VM-R3 package loop ran without friction. |
| `1a06939c-fd4b-4c2e-a83e-d3070c976cdc` | idea | `next_work` holds one item, so a reviewed queue stays invisible. |
| `0a1780f1-e1f1-460e-9720-24ad0628797c` | positive | The claim survived a session interruption. |
| `61841218-7358-4a76-b848-3b163b8b6e4a` | friction | Accepting the last result left the map focus empty. |

The repository's `.gitignore` keeps `feedback/*.json` local. I force-added only my own
outbox files, because the implementation brief asks for them to be committed.

## Final state

- `git log -1`: `5b025229932b777176b5bccab9b13430498cd7bf test: wait for the score proposal reload before amending rules in V10`
- `origin/main`: `5b025229932b777176b5bccab9b13430498cd7bf`. Actions run 37972574492: success.
- Untracked: `remarks`, the operator's note, left untouched.
