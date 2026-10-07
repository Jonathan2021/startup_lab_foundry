# Coopain checkpoint and payer assessment r1

Asset inspection COOPAIN-20261004-001 follows [the frozen protocol](PROTOCOL.md).
The [validated manifest](coopain-checkpoint.json) retains repo HEAD, initial dirty
state, selected non-secret file digests, capability matrix, constraints and gaps.
Foundry imports it as a reference-only existing project linked to P046, idempotently.
Coopain code, retained databases, .env, CVs and messages were not changed or copied.

Selected code and test fixtures establish prototype implementation presence:
profiles/preferences/jobs, mutual match, scoped grants, chat, block/report and
snapshots. `backend/tests/conftest.py` uses memory SQLite and fake email; selected
paths contain no real SMTP/S3/provider use. The attempted three-suite run failed
before collection because Coopain's separate `.venv` has no pytest. Log:
`.local/handoff-2026-10-04/coopain-tests.txt`. No runtime test passed and no frontend
workflow was observed; browser automation is unavailable. The older README safety
caveat and newer route/test presence are retained as a documentation discrepancy.

`frontend/apps/web/src/app/lib/utils.ts:scoreFromStableId` returns 60–100 from a
hash; dashboard code uses it for compatibility. This code inspection confirms a
placeholder, not predictions. A separately recorded Coopain task must verify the
running presentation and hide/label it before real-user testing. No unannounced
code fix was made in the friend's repository.

## Three money flows

| Model | Payer → recipient / service / trigger | Value and cost hypothesis | Policy/legal unknown | Next falsifier |
|---|---|---|---|---|
| Niche introductions, candidate free | Employer → Coopain / consented candidate introductions / agreed service or hire milestone | Better niche candidate access; manual vetting/support cost unknown | Placement terms, employer eligibility, consent, truthful endorsement and data retention | One employer declines network introductions, has no recurring gap, or existing process suffices |
| Referral operations | Employer → Coopain / program support and ATS workflow / program contract | Reduce admin; integration/support cost unknown | Employer referral rules and confidential applicant handling | Incumbent already solves the workflow and no narrow underserved segment is named |
| Community-sponsored program | Association/alumni sponsor → Coopain / bounded free-candidate access / sponsored cohort | Trusted network; moderation and operations cost unknown | Who has budget, membership/data consent and contracting | No sponsor owns a repeated problem or budget |

French placement services can operate for profit; jobseeker remuneration for
placement is generally prohibited, with specified exceptions. This supports
examining an employer payer rather than declaring all recruiting revenue banned.
It does not clear a subscription, bonus-share fee or candidate visibility charge.
[Official L5321-1](https://code.travail.gouv.fr/code-du-travail/l5321-1),
[official L5321-3](https://code.travail.gouv.fr/code-du-travail/l5321-3), checked
2026-10-04. A selected paid launch needs review of that exact contract/money flow.

[Keycoopt](https://keycoopt.com/en/solution/) describes employee referral, HR
integration and reward management. [Basile's current Hellowork page](https://recruteur.hellowork.com/fr/produit/cooptation.html)
describes program setup, portals and ATS workflow. These are closer comparators
for employer-funded operations than job-application assistants; vendor claims do
not establish independent outcomes or that stranger-based bonus sharing is covered.
No sufficiently matched open stranger-referral comparator was established in this
bounded screen; no product absence is inferred.

Recommendation: **retain prototype, hold commercial build, adapt the next test** to
one employer/referrer in a reachable niche (initial hypothesis: small engineering
employers using referrals without dedicated operations). Do not charge candidates
or continue solely because code exists. In fifteen minutes ask for the last referral
workflow, outsider eligibility, current alternative, candidate-quality evidence,
and who would pay for a specific missing step. Rights, past user trials and reachable
buyers remain [R007](../../../requests/2026-10-04-followups.md). Draft only; no outreach sent.
