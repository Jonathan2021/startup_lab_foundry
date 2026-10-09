"""Two bounded requests to the documented public BRouter demo."""
import hashlib
import json
import os
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

out=Path(os.environ.get('FOUNDRY_TRIAL_OUTPUT', Path(__file__).parent / 't4-replay'))
out.mkdir(parents=True, exist_ok=False)
observations=[]
for profile in ['trekking','car-fast']:
    url='https://brouter.de/brouter?'+urlencode({'lonlats':'13.377485,52.516247|13.351221,52.515004','profile':profile,'alternativeidx':0,'format':'geojson'})
    entry={'profile':profile,'url':url}
    try:
        with urlopen(Request(url,headers={'User-Agent':'Foundry-local-research/0.1'}),timeout=30) as response:
            body=response.read(2_000_000); entry['http_status']=response.status
        payload=json.loads(body)
        features=payload.get('features',[])
        entry['valid_geojson']=payload.get('type')=='FeatureCollection' and len(features)>0
        entry['response_sha256']=hashlib.sha256(body).hexdigest()
        if features:
            entry['coordinates']=len(features[0].get('geometry',{}).get('coordinates',[]))
            entry['properties']=features[0].get('properties',{})
        (out/f'route-{profile}.json').write_bytes(body)
    except (HTTPError,URLError,TimeoutError,ValueError) as exc:
        entry['error']=str(exc)
    observations.append(entry)
report={'id':'T4','scope':'public-route-engine smoke test only','observations':observations,'status':'passed' if all(x.get('valid_geojson') for x in observations) else 'inconclusive','limitations':['No scenic quality or corridor acceptance measured','No Kurviger UI access','Public sample locations, no personal location data','Public backend version not independently pinned']}
(out/'route-result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps({'status':report['status'],'observations':[{k:v for k,v in e.items() if k!='properties'} for e in observations]},indent=2))
