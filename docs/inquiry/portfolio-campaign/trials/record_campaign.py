"""One campaign's agent-owned recording; existing application boundary only."""
from pathlib import Path
from enum import Enum
import json,hashlib
from startup_foundry.application import FoundryApplication
from startup_foundry.domain import AssumptionKind,ConfidenceLevel,EvidenceKind,AssessmentOutcome,DecisionKind,WorkItemKind,WorkItemStatus,ArtifactKind,VentureStage
from startup_foundry.repository import create_db_engine,create_session_factory
ROOT=Path('/home/jonathan/startup_lab');BASE=ROOT/'foundry/docs/inquiry/portfolio-campaign';OUT=BASE/'foundry-recording'
OUT.mkdir(exist_ok=True)
engine=create_db_engine('sqlite:///'+str(ROOT/'foundry/.local/portfolio-campaign/campaign.local.db'))
app=FoundryApplication(create_session_factory(engine));vid='portfolio-campaign'
commands=json.loads((OUT/"operations.json").read_text()) if (OUT/"operations.json").exists() else []
def run(operation,**kwargs):
 for previous in commands:
  if previous["method"] == operation and previous["input"] == kwargs:return previous["output"]
 result=getattr(app,operation)(**kwargs)
 commands.append({'method':operation,'input':kwargs,'output':result})
 (OUT/'operations.json').write_text(json.dumps(commands,ensure_ascii=False,indent=2)+'\n')
 return result

def work(id,title,assumptions,kind=WorkItemKind.INVESTIGATION,method=None,success=None,failure=None):
 return run('add_work_item',work_item_id=id,venture_id=vid,title=title,kind=kind,decision_id=None,acceptance_criteria='Scope the finding, preserve counterevidence, and state the missing next evidence. First-pass completion is not market qualification.',method=method,success_criteria=success,failure_criteria=failure,assumption_ids=assumptions)

def artifact(id,name,relative,work_id=None):
 file=BASE/relative
 return run('add_artifact',artifact_id=id,venture_id=vid,work_item_id=work_id,kind=ArtifactKind.REPORT,name=name+' SHA256 '+hashlib.sha256(file.read_bytes()).hexdigest(),location=str(file))
try:
 before=app.show_venture(vid)
 assert commands or not any(x['id'].startswith('triage-') for x in before['work_items'])
 for i in json.loads((BASE/'ideas.json').read_text()):
  id=i['id'];a='candidate-'+id;w='triage-'+id;e='e-'+id;s='as-'+id;d='d-'+id
  run('add_assumption',assumption_id=a,venture_id=vid,statement=f"A new product for {id}: {i['title']} is justified now by a specific unmet job and accessible evidence.",kind=AssumptionKind.VIABILITY,importance=3,uncertainty=5)
  work(w,f"First-pass investigation {id}: {i['title']}",[a])
  summary=f"Agent triage revision {i['revision']}; {i['disposition']}. {i['rationale']} Sources: {', '.join(i['source_ids']) or 'none verified'}. {i['evidence_scope']} Demand: {i['demand_evidence']}"
  run('add_evidence',evidence_id=e,venture_id=vid,origin_work_item_id=w,kind=EvidenceKind.DOCUMENT,confidence=ConfidenceLevel.LOW,summary=summary)
  disposition=i['disposition']
  outcome=AssessmentOutcome.WEAKENED if disposition.startswith(('ADOPT','STOP')) else AssessmentOutcome.INCONCLUSIVE
  run('assess_assumption',assessment_id=s,assumption_id=a,evidence_ids=[e],outcome=outcome,confidence=ConfidenceLevel.LOW,rationale='No commercial-build qualification. '+i['rationale'])
  kind=DecisionKind.DEFER
  if disposition.startswith('STOP'):kind=DecisionKind.STOP
  elif disposition.startswith('REFRAME'):kind=DecisionKind.PIVOT
  elif disposition=='SHORTLIST_DISCOVERY':kind=DecisionKind.NARROW
  elif disposition in ['INTERNAL_TRIAL','INTERNAL_ONLY']:kind=DecisionKind.CONTINUE
  run('add_decision',decision_id=d,venture_id=vid,kind=kind,summary=f"{id}: {disposition}; first-pass allocation only",rationale=i['next_test']+' Accepted means agent-authorized local allocation, not customer validation or spending authority.',assessment_ids=[s])
  run('set_work_item_status',work_item_id=w,status=WorkItemStatus.DONE)
 # Complete the work records for the two preregistered application experiments.
 for key,relative,summary in [
  ('mlflow','trials/mlflow-result.json','Pinned MLflow feedback→dataset→deterministic evaluation worked; broken=0, fixed=1. API/setup failures retained separately. No customer or LLM-judge validation.'),
  ('monitor','trials/change-result.json','Pinned changedetection.io selection/ignore components suppressed noise and retained substantive change. Full service and semantic impact untested.')]:
  run('add_evidence',evidence_id='result-'+key,venture_id=vid,origin_work_item_id='trial-'+key,kind=EvidenceKind.EXPERIMENT_RESULT,confidence=ConfidenceLevel.HIGH,summary=summary)
  run('assess_assumption',assessment_id='assessment-'+key,assumption_id='a-'+key,evidence_ids=['result-'+key],outcome=AssessmentOutcome.REFUTED,confidence=ConfidenceLevel.HIGH,rationale='The narrow necessity-for-custom-plumbing assumption is contradicted by the incumbent result. Broader usefulness/demand is not assessed.')
  run('add_decision',decision_id='decision-'+key,venture_id=vid,kind=DecisionKind.DEFER,summary='Defer custom generic '+key+' substitute',rationale=summary,assessment_ids=['assessment-'+key])
  run('set_work_item_status',work_item_id='trial-'+key,status=WorkItemStatus.DONE)
  artifact('artifact-'+key,key+' pinned result',relative,'trial-'+key)
 for relative in ['ideas.json','sources.json','intake-manifest.json','PLAN.md','CALIBRATION.md','GAPS.md']:
  artifact('register-'+relative.lower().replace('.','-'),relative,relative)
 # The other frozen protocols live in files; recording results here is retrospective.
 for id,path,summary in [
  ('t3','trials/source-reuse-result.json','Original source register/rg lookup passed exact-reference controls; no semantic-memory benchmark or measured time/token savings.'),
  ('t4','trials/route-result.json','Two BRouter profiles returned routes for public Berlin coordinates; scenic/time-budget value untested.'),
  ('t5','trials/t5/result.json','Six route requests returned HTTP 500. Diagnostic numeric encoding returned target-island error. Inconclusive harness/input failure, no competitor deficiency inferred.'),
  ('t6','trials/t6/result.json','Synthetic changed-claim controls queued exactly the prior recorded source consumers, preserving decisions. Source relevance audit later reduced overbroad references; exact links alone cannot judge relevance.')]:
  work('work-'+id,'Record observed '+id+' outcome',[])
  run('add_evidence',evidence_id='evidence-'+id,venture_id=vid,origin_work_item_id='work-'+id,kind=EvidenceKind.EXPERIMENT_RESULT,confidence=ConfidenceLevel.MEDIUM,summary=summary+' Retrospective database entry; original before-run protocol remains in trial files.')
  artifact('artifact-'+id,id+' result',path,'work-'+id)
  run('set_work_item_status',work_item_id='work-'+id,status=WorkItemStatus.DONE)
 snapshot=app.show_venture(vid);(OUT/'campaign-snapshot.json').write_text(json.dumps(snapshot,ensure_ascii=False,indent=2)+'\n')
 (OUT/'provenance.json').write_text(json.dumps({'date':'2026-10-02','attribution':'agent-owned; no learner credit','database':'foundry/.local/portfolio-campaign/campaign.local.db','operation_count':len(commands),'code_sha256':hashlib.sha256((ROOT/'foundry/src/startup_foundry/application.py').read_bytes()).hexdigest(),'input_sha256':{n:hashlib.sha256((BASE/n).read_bytes()).hexdigest() for n in ['ideas.json','sources.json','intake-manifest.json']},'counts':{k:len(v) for k,v in snapshot.items() if isinstance(v,list)},'caveat':'Existing Experiment.status remains planned; work completion and result evidence are separate. No lifecycle state was inferred or patched directly.'},indent=2)+'\n')
 print('Recorded',len(commands),'operations;',len(snapshot['work_items']),'work items')
finally:engine.dispose()
