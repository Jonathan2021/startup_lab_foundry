# Crous queue venture first review

2026-10-06. Idea `a32e67a1-2289-46b4-b12a-d24d2032ef2c`; venture
`f0b5abfe-0274-42f7-9c9a-72dcbe68c116`. Continue a bounded **local gap
investigation**, with Cuvier and Châtelet as the user-selected sites. A generic
queue app is already substantially covered by existing products. Do not build
before checking what is missing at these two restaurants and how fresh data would
be obtained repeatedly.

The idea's initial missing score was legitimate: it had never been assessed.
Scoring already supports manual agent/API work; an unattended worker is not
required. Promotion nevertheless left no review or intake task. The separate
[implementation review](../revamp-review-2026-10-06/REPORT.md) makes that a repair
task. This venture review supplies the missing initial investigation and next work.

## What changed our assessment

Affluences explicitly offers restaurant waiting times, forecasts and occupancy;
an official CROUS announcement confirms deployment at five Clermont restaurants.
The restaurant marketing page's equipped-sites link currently returns parking
results, reproducing the user's confusion. That faulty link does not mean its
restaurant service is absent. These are vendor/operator claims, not our accuracy
measurements. [Affluences restaurant page](https://www.pro.affluences.com/restaurant-universitaire),
[linked directory](https://affluences.com/fr/sites?categories=18),
[CROUS deployment announcement](https://www.crous-clermont.fr/2026/09/25/affluences-lappli-pour-consulter-le-temps-dattente-en-resto-u/).

CrousRadar's French Apple listing describes free collaborative queue reporting,
menus and contribution safeguards. It currently shows four ratings; that does not
establish its user count or low adoption. Android availability, useful coverage
and real workflow performance remain unverified. [CrousRadar listing](https://apps.apple.com/fr/app/crousradar/id6755202143).

Official CNOUS catalogs/menus could seed restaurant identities and directory
utility. Their documented fields do not supply live waits or seats. Affluences
mentioning an API does not establish a free, licensed public feed. Verify access
and reuse terms before designing an integration; no integration or scraping is
authorized by this review. [Restaurant catalog](https://www.data.gouv.fr/datasets/restaurants-brasseries-et-cafeterias-des-crous),
[menu catalog](https://www.data.gouv.fr/datasets/menus-des-restaurants-brasseries-et-cafeterias).

## Exact pilot locations

| Place | Official location and access stated on its page | Consequence |
|---|---|---|
| RU Cuvier | 4 place Jussieu; Sorbonne Université students | Confirm the relevant queue and eligibility before comparing waits |
| RU Châtelet | 10 rue Jean Calvin; all students | This is the restaurant in the fifth arrondissement, not Châtelet metro |
| Restaurant administratif Jussieu | 4 place Jussieu; Sorbonne Université staff | Separate optional staff service, not interchangeable with RU Cuvier |

The official pages list weekday lunch service 11:30–14:00 at inspection; confirm
current opening on the day. The shared Cuvier/Jussieu address must not cause staff
and student observations to be pooled. Sources: [Cuvier](https://www.crous-paris.fr/restaurant/ru-cuvier/),
[Châtelet](https://www.crous-paris.fr/restaurant/ru-chatelet/),
[administrative Jussieu](https://www.crous-paris.fr/restaurant/restaurant-administratif-jussieu/).

Public searches did not surface matching incumbent listings for the two RUs.
**Local coverage remains unverified** until an actual app/site search is performed;
search-engine absence is not proof that they are unsupported. Do not substitute a
gym with Châtelet in its name. The user's site selection is recorded separately
from permission, queue eligibility or an agreement to recruit volunteers.

## Provisional scores

Append the following explicit, low-confidence judgments to the idea and its
currently equivalent venture scope, with their own workspace-local evidence links.
These are three factors out of twelve; the total remains unknown. A visible blank
total is preferable to made-up revenue, margins, retention or founder-access data.

| Criterion | Proposed raw score | Reason |
|---|---|---|
| Problem intensity | 7/10 | User reports substantial lunch friction; deployed queue-information services support relevance, but severity/frequency at the pilot sites is unmeasured |
| Competition intensity | 8/10 risk | Affluences overlaps live/predicted waits and occupancy; CrousRadar overlaps collaborative reporting. Local availability and satisfaction could still leave a gap |
| Network dependency | 8/10 risk | The proposed free collaborative model needs enough timely contributors at each venue and lunch period; static menus cannot solve this cold start |

Revenue, profitability, MVP speed, founder fit, go-to-market, moat, retention,
legal/ethical risk and capital remain unknown. Do not score paid queue-place
reservation as an accepted business model. Keep that original suggestion in source
history; defer it while evaluating usefulness, fairness and venue rules. Advertising
is a possible later hypothesis, not demand or expected revenue.

## Narrow hypothesis to test

At this specific restaurant pair, an eligible diner may lack a trustworthy answer
to “where should I eat at my arrival time, after walking, and can I sit down?”
This could justify a small service if incumbents do not answer it and fresh data
can be supplied without constant organizer effort. Seats alone are not novel:
Affluences already describes restaurant seat occupancy. [Affluences FAQ](https://affluences.com/fr/faq).

Separate walking duration, queue wait at arrival, service endpoint and seat search.
A crowd report submitted after finishing a long queue already describes an earlier
condition. Show timestamp, queue class and uncertainty; stale/missing values should
say unknown. Do not assume an empty queue means available seats, or that a current
wait will still apply after walking to another venue.

## Next steps already specified

1. **Incumbent coverage check:** search exact venue names/addresses in actual
   Affluences and CrousRadar surfaces, record device/platform, time, match,
   live/forecast/seat information and freshness. Android is the user's device;
   an iOS-only competitor test can remain unavailable. No account or report upload
   is needed or authorized. A missing tool/browser is an access blocker, not a
   negative product finding.
2. **Optional first observations:** clarify student/staff queue and whether the
   user can log their own ordinary lunches. Start with one visit, up to three
   across eligible sites if practical: queue join, food paid/ready, seat found,
   any displayed estimate and its timestamp, plus actual walking time if relevant.
   No names, photos, tracking strangers or location trails. This is a small
   request for firsthand evidence, not a commitment to run a volunteer study.
3. **Review after three visits:** identify the concrete missing decision and compare
   incumbents with a simple same-venue/time-band baseline. Use existing tools if
   they solve it. Narrow or stop if the remaining benefit is small or data cannot
   stay fresh. Three lunches can establish friction, not forecast accuracy or
   sustainable participation.
4. **Only if a gap survives:** freeze a five-lunch-day, two-venue feasibility screen
   with willing eligible observers. Suggested gates are at least 15 observations,
   six held-out later-day observations, wait error at most five minutes, fresh
   observations at 70% of scheduled checks, and repeated contribution without
   individual daily reminders. These are proposed screening thresholds to settle
   before collection. Compare forecast-at-arrival against incumbent/historical
   baselines; report abstention and whether better advice depended entirely on
   researcher effort. Do not label estimated alternate-venue savings as observed.

No sports fusion, other venture hold, user source text or historical score is
changed by this work. Field observations, mobile trials and commercial validation
remain pending. Full source details and access limits are in [SOURCES.md](SOURCES.md).
