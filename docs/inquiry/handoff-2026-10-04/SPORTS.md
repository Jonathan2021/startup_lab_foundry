# Friends-group comparison r1

SPORTS-20261004-001 follows the two tasks frozen in [PROTOCOL.md](PROTOCOL.md).
The handoff reports the user's interest and possible friends-group access. This is
first-party/reported interest, not observed independent adoption or payment. P023
(private ranking/tournaments) and P103 (rotating teams, roles, results/history) keep
separate source ideas and workspaces with an explicit shared-comparison relation.

| Comparator | Task A: ranking/tournament | Task B: rotating attendance/roles | Corrections / access / measurement |
|---|---|---|---|
| Rankat | Official page claims friend leagues, ELO/head-to-head history, join codes, round robin/knockout and teams | Team tournament support is claimed; automatic role-constrained team balancing was not established | Public page is informational; app/account/device workflow not tested. Entry time, export and correction behavior unknown |
| Rankade | Indexed official how-to/FAQ describes groups, match entry and rankings | FAQ models factions and players; this is relevant to variable teams, but does not establish role-constrained team proposals | Indexed admin FAQ describes match approval. Current direct fetches timeout/502; these are access failures, not defects or absent features |
| Captains + local session sheet | Manual ranking/tournament record can serve as a baseline | Organizer can assign teams and roles, then record today's result | Illustrative baseline only. No user's session or fairness judgment observed |

Sources checked 2026-10-04: [Rankat official page](https://www.rankat.app/),
[Rankade match-entry FAQ](https://rankade.com/frequently-asked-question/5),
[Rankade admin FAQ](https://rankade.com/frequently-asked-question/3/what-can-an-admin-do/23),
[Rankade learn-more](https://rankade.com/learn-more). Rankade claims were recovered
from indexed official pages; direct fetch failures remain part of the record.
Rankat describes separate groups per sport; no universal cross-sport skill scale
is required for these jobs. Its marketing does not establish observed behavior.

Baseline attempt: Rankade public how-to and match-entry access failed; Rankat's
public page exposed no executable session flow. Browser inventory returned no
enabled browser; opening the in-app browser returned “Browser is not available”.
No account was created, app installed, device access assumed or group data submitted.
Thus setup/entry time, corrections and repeat use remain **unmeasured**. A third
sport-specific comparator waits for the actual sport rather than guessing it.

For a user-assisted test, use one real session and today's attendance. Setup target
<=10 minutes, result entry <=30 seconds per match; record observed accounts/steps,
late arrival, newcomer, corrected result and returning participant. The 12-player
volleyball example is explicitly synthetic and does not identify the user's sport.
Ask for sport/group/frequency/organizer/roles/current workaround/last frustration in
[R006](../../../requests/2026-10-04-followups.md). Compare captains/random assignment
and any incumbent team proposal before implementing a single local session helper.

Recommendation: **pursue a bounded personal/group comparison**, starting with existing
ranking software for P023. P103 remains the unresolved rotating-team job, not a
proven incumbent gap. Do not build a social network or commercial platform now.
Two voluntary sessions can justify a useful community tool; commercial work also
needs an organizer buyer, benefit beyond free incumbents and a price discussion.
