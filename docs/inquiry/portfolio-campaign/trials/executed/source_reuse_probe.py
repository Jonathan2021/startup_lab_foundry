"""Exact provenance reuse using ordinary JSON and rg, not semantic memory."""
from datetime import date, timedelta
import json
from pathlib import Path
import subprocess

folder=Path(__file__).resolve().parent.parent
sources=json.loads((folder/'sources.json').read_text())
ideas=json.loads((folder/'ideas.json').read_text())
lookup={s['id']:s for s in sources}
assert len(lookup)==len(sources)
unknown={ref for i in ideas for ref in i['source_ids'] if ref not in lookup}
assert not unknown
queries=[('G021','mlflow'),('P061','change'),('G013','change'),('G012','elicit')]
observations=[]
for idea_id,source_id in queries:
 idea=next(i for i in ideas if i['id']==idea_id)
 assert source_id in idea['source_ids']
 record=lookup[source_id]
 rg=subprocess.run(['rg','--fixed-strings',record['url'],str(folder/'sources.json')],capture_output=True,text=True,check=True)
 assert record['url'] in rg.stdout
 observations.append({'idea':idea_id,'source':source_id,'revision':record['revision'],'url':record['url'],'rg_exact_recovery':True})

def needs_refresh(record,as_of):
 return as_of-date.fromisoformat(record['checked_on']) > timedelta(days=30)

synthetic=dict(lookup['change'],checked_on='2026-08-01')
assert needs_refresh(synthetic,date(2026,10,2))
assert not needs_refresh(lookup['change'],date(2026,10,2))
assert lookup.get('unknown-source') is None
counts={s:sum(s in i['source_ids'] for i in ideas) for s in lookup}
report={'id':'T3','status':'passed','scope':'exact provenance and reference-integrity checks using JSON/rg; no semantic retrieval or human-time comparison','observations':observations,'unique_source_records':len(lookup),'source_idea_links':sum(counts.values()),'multiply_referenced_sources':sum(v>1 for v in counts.values()),'synthetic_staleness_check':True,'unknown_source_rejected':True,'counts':counts,'limits':['Reference reuse is observed, token/time savings unmeasured','Shared source links are not independent customer evidence','Manual freshness policy, no automatic update service']}
(folder/'trials/source-reuse-result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({k:v for k,v in report.items() if k not in ['counts','observations']},indent=2))
