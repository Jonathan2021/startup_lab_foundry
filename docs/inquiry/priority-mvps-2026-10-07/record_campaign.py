"""Apply typed Foundry campaign decisions to an explicitly selected store.

Rehearse on a backup copy first. No direct SQL writes, external calls or sends.
The output checkpoint makes an interrupted run resumable per venture.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path
from datetime import datetime,timezone
from sqlalchemy import select
from startup_foundry.repository import create_db_engine,create_session_factory
from startup_foundry.migrations import upgrade_database
from startup_foundry.portfolio import PortfolioService,IdeaDraft
from startup_foundry.domain import Venture,Evidence
from startup_foundry.agent_handoffs import AgentHandoffService
from startup_foundry.decision_maps import DecisionMapService
from startup_foundry.decision_contracts import CaptureInput,MapInput,NewWorkInput,ContextInput,WorkClaimInput,ResultInput,ResolveResultInput
from startup_foundry.workspace_modules import WorkspaceModuleService,RenameInput,ConfigInput
from startup_foundry.projects import ExistingProjectService,ExistingProjectInput
from startup_foundry.reviews import ReviewService,ReviewInput
from startup_foundry.venture_scoring import VentureScoringService,VentureAssessmentInput

ACTOR='Codex:priority-mvps-2026-10-07'
ROOT=Path('/home/jonathan/startup_lab')

def main():
 p=argparse.ArgumentParser();p.add_argument('--store',required=True);p.add_argument('--specs',required=True);p.add_argument('--output',required=True);a=p.parse_args()
 specs=json.loads(Path(a.specs).read_text());out=Path(a.output)
 done=json.loads(out.read_text()) if out.exists() else {}
 url='sqlite:///'+str(Path(a.store).resolve());upgrade_database(url)
 engine=create_db_engine(url);factory=create_session_factory(engine)
 service=AgentHandoffService(factory);maps=DecisionMapService(factory);modules=WorkspaceModuleService(factory)
 def save():out.write_text(json.dumps(done,ensure_ascii=False,indent=2)+'\n')
 for slug,s in specs.items():
  if slug in done and done[slug].get('complete'):continue
  with factory() as session:v=session.get(Venture,s['venture'])
  if v is None:
   portfolio=PortfolioService(factory)
   idea=portfolio.create_idea(IdeaDraft(title=s['name'],description=s['goal'],original_text='User request 2026-10-07: personal sport coach versus match-video coach; selected availability-aware volleyball planner.'),idea_id='priority-volley-coach-20261007')
   promoted=portfolio.promote_idea(idea['id'],venture_id=s['venture']);ws=promoted['workspace_id']
  else:ws=v.workspace_id
  s['workspace']=ws
  state=service.resume(ws)
  module=modules.show(s['venture'])
  if module['title']!=s['name']:
   modules.rename(s['venture'],RenameInput(expected_version=module['workspace_version'],title=s['name'],actor=ACTOR,rationale='User clarified the product scope; current short name replaces a historical research task title. Previous names and source ideas retained.'))
  # Repository checkpoint is reference-only; it never reads or executes target code.
  import subprocess
  repo=ROOT/slug
  head=subprocess.run(['git','-C',str(repo),'rev-parse','HEAD'],capture_output=True,text=True)
  maturity='mvp' if slug=='foundry' else 'prototype' if slug=='coopain' else 'concept'
  ExistingProjectService(factory).intake(ExistingProjectInput(venture_id=s['venture'],name=s['name'],description=s['goal'],repositories=[{'local_reference':str(repo),'head':head.stdout.strip() if head.returncode==0 else None,'dirty_state':'Prepared local implementation pack; existing unrelated state preserved','observed_at':datetime.now(timezone.utc)}],product_maturity=maturity,reason_paused='This checkpoint records repository scope before the explicit campaign decision below; not a new field-data hold.',gaps=['Application acceptance remains to implement' if slug!='foundry' else 'Sustained real-agent benefit is not yet measured'],next_bounded_test=s['packages'][0][2],ownership_license_access='Local preparation authorized. No external publication or collaborator rights inferred.',expected_review_revision=state['current_review']['revision'] if state['current_review'] else 0,author=ACTOR))
  modules.configure(s['venture'],ConfigInput(expected_revision=module['config']['revision'],actor=ACTOR,modules=list(dict.fromkeys([*module['config']['modules'],'software']))))
  captured=service.capture(ws,CaptureInput(request_key='priority-scope-20261007',actor=ACTOR,summary=s['name']+': user scope and bounded MVP investigation',details=s['goal']+'\n'+s['decision']+'\n'+s['evidence'],sources=['observation: user priority request 2026-10-07','document: '+str(ROOT/slug/('docs/plans/2026-10-07-agent-dogfood/README.md' if slug=='foundry' else 'docs/mvp/DECISION.md'))],confidence='medium'))
  current=service.resume(ws)
  research=service.create_work(ws,NewWorkInput(expected_head=current['map_revision_id'],request_key='priority-review-20261007',actor=ACTOR,rationale='Record completed bounded investigation and explicit implementation handoff through the normal result loop.',work={'title':'Assess '+s['name']+' MVP boundary and implementation map','description':s['goal'],'acceptance_criteria':'Retain sources, actual probes, limits, dependent roadmap and one next implementation package. No demand or deployment claim.','kind':'investigation'}))
  # Creation returns an artifact payload containing work_id.
  work_id=research['work']['id'];state=service.resume(ws)
  active=[w for w in state['work'] if w['id']!=work_id]
  treatments=[{'work_id':w['id'],'expected_version':w['version_id'],'action':'keep' if w['status']=='blocked' else 'pause','rationale':'Pending human input is retained as a later pilot input.' if w['status']=='blocked' else 'Superseded as an executable priority by the user-approved 2026-10-07 scope and this package roadmap; historical findings preserved.'} for w in active]
  nodes=[{'id':'goal','kind':'goal','title':s['goal'][:300]}, {'id':'research','kind':'record','title':'MVP scope and evidence review','ref':{'kind':'work','id':work_id}}, {'id':'pilot','kind':'question','title':'Does the completed MVP help in repeated real use?'}, {'id':'expand','kind':'alternative','title':'Extend only the demonstrated useful workflow'}, {'id':'revise','kind':'alternative','title':'Narrow or use an existing tool if reuse/benefit fails'}]
  edges=[{'source':'research','target':'goal','kind':'contributes_to'},{'source':'pilot','target':'expand','kind':'may_lead_to','condition':'Repeated voluntary use and a specific next unmet need are observed','outcome':'supported'},{'source':'pilot','target':'revise','kind':'may_lead_to','condition':'Users do not reuse the core or existing tools solve it as well','outcome':'weakened'}]
  for id,deps,title,what,test in s['packages']:
   nodes.append({'id':id,'kind':'alternative','title':id+': '+title,'detail':what+'\nAcceptance: '+test+'\nProposed package: materialize only after prerequisite acceptance.'})
   edges.append({'source':id,'target':'goal','kind':'contributes_to'})
   for dep in deps:edges.append({'source':id,'target':dep,'kind':'depends_on'})
  edges.append({'source':s['packages'][-1][0],'target':'pilot','kind':'informs'})
  draft={'nodes':nodes,'edges':edges,'focus':['research']}
  research_row=next(w for w in state['work'] if w['id']==work_id)
  treatments.append({'work_id':work_id,'expected_version':research_row['version_id'],'action':'keep','rationale':'This investigation explicitly reviews and implements the newly declared current scope.'})
  maps.revise(ws,MapInput(expected_head=state['map_revision_id'],request_key='priority-map-20261007',actor=ACTOR,rationale='Separate the current bounded package from conditional later scope. Historical holds do not block local implementation.',map=draft,work_treatments=treatments))
  work=next(w for w in service.resume(ws)['work'] if w['id']==work_id)
  claimed=service.claim(ws,work_id,WorkClaimInput(expected_version=work['version_id'],actor=ACTOR))
  with factory() as session:evidence_ids=list(session.scalars(select(Evidence.id).where(Evidence.workspace_id==ws)))
  context=service.prepare(ws,ContextInput(work_id=work_id,expected_work_version=claimed['version_id'],expected_head=maps.show(ws)['id'],request_key='priority-context-20261007',actor=ACTOR,budget_bytes=100000,evidence_ids=evidence_ids[:100]))
  package=s['packages'][0]
  result=service.submit(ws,ResultInput(context_id=context['id'],request_key='priority-result-20261007',actor=ACTOR,summary=s['decision'],rationale='The user explicitly prioritized bounded MVP implementation. The retained evidence supports building for a private pilot while keeping business and release unknowns distinct.',limits='No real user tests, market validation, payment clearance or public deployment. Technical probes cover only recorded cases. Full artifacts remain in the owning repositories.',outcome='narrow',decision_scope='venture',narrowed_objective=s['goal'],next_action=package[0]+': '+package[2]+' — '+str(repo/('docs/plans/2026-10-07-agent-dogfood/README.md' if slug=='foundry' else 'docs/mvp/ROADMAP.md')),findings=[{'summary':s['evidence'],'sources':['document: '+str(ROOT/'foundry/docs/inquiry/priority-mvps-2026-10-07/PROTOCOL.md')],'confidence':'medium'}],next_work={'title':package[0]+': '+package[2],'description':package[3]+'\nPlan: '+str(repo/('docs/plans/2026-10-07-agent-dogfood/README.md' if slug=='foundry' else 'docs/mvp/ROADMAP.md')),'acceptance_criteria':package[4],'kind':'execution','owner':'agent'}))
  choice=ResolveResultInput(expected_result_digest=result['digest'],expected_head=context['map_revision_id'],expected_work_version=context['work']['version_id'],expected_review_revision=context['review_revision'],resolution='accept',actor=ACTOR,rationale='Reviewed local planning decision within user authorization. No external execution or implicit commercial validation.',coverage_action='reviewed' if context['context_complete'] else 'accept_limitation',coverage_rationale='Historical and current local summaries consulted; the decision is only to implement the bounded private MVP, not validate all previous claims.')
  service.preview(result['id'],choice);receipt=service.resolve(result['id'],choice)
  next_id=receipt.get('next_work_id') or receipt.get('effects',{}).get('next_work_id')
  # Use current authoritative review if the presentation wrapper changes.
  final=service.resume(ws);next_id=final['current_review']['next_work_item_id']
  ReviewService(factory).append(ReviewInput(workspace_id=ws,expected_revision=final['current_review']['revision'],investigation_stage='solution_validation',product_maturity=maturity,disposition='internal_only' if slug=='foundry' else 'pursue',next_action=final['current_review']['next_action'],next_work_item_id=next_id,reason='Private MVP implementation authorized; demand and public release gates remain explicit in roadmap.',author=ACTOR,source_artifact_id=result['id']))
  done[slug]={'complete':True,'venture_id':s['venture'],'workspace_id':ws,'research_work_id':work_id,'context_id':context['id'],'result_id':result['id'],'receipt':receipt,'next_work_id':next_id,'map_revision_id':maps.show(ws)['id'],'repository':str(repo),'sources':s.get('sources',[])};save();print(slug,ws,next_id,flush=True)
 engine.dispose()
if __name__=='__main__':main()
