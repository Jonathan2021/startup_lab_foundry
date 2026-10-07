"""Record the investigated N008 case through the existing application boundary.

Retrospective persistence, not a claim that these DB records predated T7/T8.
The separate frozen protocols are the before-run records. Campaign support only.
"""
from pathlib import Path
import hashlib
import json
from startup_foundry.application import FoundryApplication
from startup_foundry.domain import (
    ArtifactKind, AssessmentOutcome, AssumptionKind, ConfidenceLevel,
    DecisionKind, EvidenceKind, VentureStage, WorkItemKind, WorkItemStatus,
)
from startup_foundry.repository import create_db_engine, create_session_factory

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[3]
OUT = BASE / 'foundry-recording'
DB = ROOT / 'foundry/.local/portfolio-campaign/campaign.local.db'
LOG = OUT / 'route-operations.json'
commands = json.loads(LOG.read_text()) if LOG.exists() else []
engine = create_db_engine('sqlite:///' + str(DB))
app = FoundryApplication(create_session_factory(engine))
vid = 'v-route-repair'

def record(operation, **kwargs):
    for previous in commands:
        if previous['method'] == operation and previous['input'] == kwargs:
            return previous['output']
    result = getattr(app, operation)(**kwargs)
    commands.append({'method': operation, 'input': kwargs, 'output': result})
    LOG.write_text(json.dumps(commands, indent=2, ensure_ascii=False) + '\n')
    return result

try:
    record('create_venture', venture_id=vid, name='Scenic ride repair: N008 discovery',
           objective='Determine whether configured incumbents can shorten a specified ride within a time budget while preserving valued sections; separate GPX path changes from ETA-model changes. No product build or payment authorization.',
           stage=VentureStage.DISCOVERY)
    for key, kind, statement in [
        ('pain', AssumptionKind.DESIRABILITY, 'At least one rider experienced material manual-planning friction balancing scenic roads, time and GPX/ETA transfer.'),
        ('gap', AssumptionKind.USABILITY, 'Configured existing planners leave a reproducible unmet time-budget repair task for this rider.'),
        ('viability', AssumptionKind.VIABILITY, 'The residual job supports repeated adoption and payment sufficient for a sustainable new product.'),
    ]:
        record('add_assumption', assumption_id='route-'+key, venture_id=vid,
               statement=statement, kind=kind, importance=5, uncertainty=5)
    record('add_work_item', work_item_id='route-first-comparison', venture_id=vid,
           title='Record rider problem, incumbent counterevidence and bounded T7/T8 results',
           kind=WorkItemKind.INVESTIGATION, decision_id=None,
           acceptance_criteria='Preserve reported facts, observed capabilities, failed/access-limited attempts, and remaining uncertainty without claiming a historical trip reproduction.',
           method=None, success_criteria=None, failure_criteria=None,
           assumption_ids=['route-pain', 'route-gap', 'route-viability'])
    evidence = [
        ('route-user-report', EvidenceKind.OBSERVATION, ConfidenceLevel.MEDIUM,
         'First-party user reports manual Liberty Rider/Street View shaping for Belgium–France rides, a recalled 4.5h→6h estimate after GPX transfer to 68°, and rain-driven fallback to Waze without highways. No original GPX, settings, measured time or buyer commitment supplied. Self-report, not reproduced causal diagnosis.'),
        ('route-public-reports', EvidenceKind.MARKET_RESEARCH, ConfidenceLevel.LOW,
         'Selected independent Motardie and Kurviger discussions contain related time/waypoint friction; replies also describe successful tools and workarounds. Sources rider-time-report and route-pain in sources.json. No prevalence estimate.'),
        ('route-t7-result', EvidenceKind.EXPERIMENT_RESULT, ConfidenceLevel.MEDIUM,
         'Anonymous Liberty Rider town-centre Nébouzat→Thauvenay test displayed 2h34/255km with motorways and 3h05/225km without. Export menu only; no cross-app transfer. 68°/MyRoute-app access gates and Kurviger loading prevented fuller comparisons. Harness errors retained. See trials/rider-result.json. Retrospective DB recording; protocol was frozen in files.'),
        ('route-t8-counterevidence', EvidenceKind.DOCUMENT, ConfidenceLevel.MEDIUM,
         'Byway advertises time-budget repair, Throttle curviness/arrival controls and MotoRidez time-budget loops/retained legs. T8 observed private-beta/access/coverage limits; no planning submissions. Existing Kurviger segment controls and MyRoute-app timing/engine comparison further weaken broad novelty. Claims are not performance validation.'),
    ]
    for eid, kind, confidence, summary in evidence:
        record('add_evidence', evidence_id=eid, venture_id=vid,
               origin_work_item_id='route-first-comparison', kind=kind,
               confidence=confidence, summary=summary)
    for key, outcome, confidence, ids, rationale in [
        ('pain', AssessmentOutcome.SUPPORTED, ConfidenceLevel.MEDIUM,
         ['route-user-report', 'route-public-reports'],
         'Supported only as an experienced/reported problem for at least one rider; no frequency, accuracy or payment inference.'),
        ('gap', AssessmentOutcome.INCONCLUSIVE, ConfidenceLevel.LOW,
         ['route-t7-result', 'route-t8-counterevidence'],
         'Basic alternatives work and close competing claims exist. Selected sections/deadline and original transfer inputs are absent, so the exact configured-incumbent comparison is incomplete.'),
        ('viability', AssessmentOutcome.INCONCLUSIVE, ConfidenceLevel.LOW,
         ['route-user-report', 'route-t8-counterevidence'],
         'No repeating adopter, payment, distribution or cost evidence. First-party interest and vendor feature claims cannot qualify a commercial build.'),
    ]:
        record('assess_assumption', assessment_id='route-assess-'+key,
               assumption_id='route-'+key, evidence_ids=ids, outcome=outcome,
               confidence=confidence, rationale=rationale)
    record('add_decision', decision_id='route-narrow', venture_id=vid,
           kind=DecisionKind.NARROW,
           summary='Continue only a specified ride-repair comparison; defer general planner/product build',
           rationale='Next comparison needs a route, budget, valued legs and permitted inputs. Prefer an incumbent or a small integration if it suffices. Keep geometry and ETA questions separate. This accepted local allocation grants no spending, publication or navigation reliability approval.',
           assessment_ids=['route-assess-pain', 'route-assess-gap', 'route-assess-viability'])
    for index, relative in enumerate(['N008-CASE.md', 'trials/RIDER_CASE_PROTOCOL.md',
                                      'trials/rider-result.json',
                                      'trials/NEW_ROUTING_COMPARATORS_PROTOCOL.md',
                                      'trials/new-routing-result.json']):
        path = BASE / relative
        record('add_artifact', artifact_id=f'route-artifact-{index+1}', venture_id=vid,
               work_item_id='route-first-comparison', kind=ArtifactKind.REPORT,
               name=relative+' SHA256 '+hashlib.sha256(path.read_bytes()).hexdigest(),
               location=str(path))
    record('set_work_item_status', work_item_id='route-first-comparison', status=WorkItemStatus.DONE)
    snapshot = app.show_venture(vid)
    (OUT/'route-snapshot.json').write_text(json.dumps(snapshot, indent=2, ensure_ascii=False)+'\n')
    (OUT/'route-provenance.json').write_text(json.dumps({
        'date': '2026-10-02', 'attribution': 'agent-owned, no learner credit',
        'recording': 'retrospective; frozen before-run protocols retained separately',
        'database': str(DB), 'operation_count': len(commands),
        'application_sha256': hashlib.sha256((ROOT/'foundry/src/startup_foundry/application.py').read_bytes()).hexdigest(),
        'counts': {k: len(v) for k,v in snapshot.items() if isinstance(v, list)},
    }, indent=2)+'\n')
    assert not any(x['id'].startswith('triage-') for x in snapshot['work_items'])
    campaign = app.show_venture('portfolio-campaign')
    assert len(campaign['work_items']) == 253
    assert not any(x['id'].startswith('route-') for x in campaign['assumptions'])
    print('Recorded route case:', len(commands), 'operations; venture isolation verified')
finally:
    engine.dispose()
