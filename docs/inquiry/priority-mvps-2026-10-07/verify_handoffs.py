"""Validate preparation artifacts and live resume identities; not app acceptance."""
from __future__ import annotations
import hashlib,json,subprocess
from pathlib import Path
ROOT=Path(__file__).resolve().parents[4]
base=Path(__file__).resolve().parent
records=json.loads((base/'records.json').read_text())
checks=[]
for slug,r in records.items():
 repo=ROOT/slug
 folder=repo/('docs/plans/2026-10-07-agent-dogfood' if slug=='foundry' else 'docs/mvp')
 spec=json.loads((folder/'spec.json').read_text())
 ids={p[0] for p in spec['packages']};assert len(ids)==len(spec['packages'])
 completed=set()
 for id,deps,title,change,criteria in spec['packages']:
  assert set(deps)<=completed and title and change and criteria
  completed.add(id)
 for name in ['AGENT_HANDOFF.md','FIRST_TASK.md']:assert(folder/name).stat().st_size>300
 config=json.loads((repo/'.foundry/project.json').read_text())
 assert config['workspace_id']==r['workspace_id'] and config['venture_id']==r['venture_id']
 assert hashlib.sha256((repo/'tools/foundry_agent.py').read_bytes()).hexdigest()==config['kit_sha256']
 result=subprocess.run(['python3','tools/foundry_agent.py','resume'],cwd=repo,capture_output=True,text=True,check=True)
 state=json.loads(result.stdout)
 assert state['scope']['title']==spec['name']
 assert state['map_revision_id']
 assert state['current_review']['next_work_item_id']==r['next_work_id']
 nextwork=next(w for w in state['work'] if w['id']==r['next_work_id'])
 assert nextwork['status']=='ready' and not nextwork['execution_blockers']
 checks.append({'repository':slug,'venture_id':r['venture_id'],'workspace_id':r['workspace_id'],'next_work_id':nextwork['id'],'next_work_state':nextwork['status'],'packages':len(ids),'plan_integrity':'pass','application_acceptance':'existing Foundry tests separately' if slug=='foundry' else 'not implemented/verified by this check'})
(base/'handoff-verification.json').write_text(json.dumps(checks,indent=2)+'\n')
print(json.dumps(checks,indent=2))
