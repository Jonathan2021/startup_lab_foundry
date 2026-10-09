"""Probe upstream content extraction only; no web server or notifications."""
from __future__ import annotations
import importlib.metadata
import json
import os
from pathlib import Path
from changedetectionio import html_tools

OUT = Path(os.environ.get('FOUNDRY_TRIAL_OUTPUT', Path(__file__).parent / 't2-replay'))
OUT.mkdir(parents=True, exist_ok=False)

base = '<main><p class="claim">Review queues included.</p><p>Updated: Monday</p></main><footer>Visitors 10</footer>'
noise = base.replace('Monday', 'Tuesday').replace('Visitors 10', 'Visitors 20')
changed = noise.replace('Review queues included.', 'Review queues require team plan.')
missing = base.replace('<main>', '<article>').replace('</main>', '</article>')

def extract(html: str) -> str:
    selected = html_tools.include_filters('main', html)
    text = html_tools.html_to_text(selected)
    return html_tools.strip_ignore_text(text, ['/^Updated:.*$/']).strip()

outputs = {name: extract(value) for name,value in [('base',base),('noise',noise),('changed',changed),('missing',missing)]}
assert outputs['base'] == outputs['noise']
assert outputs['base'] != outputs['changed']
assert 'team plan' in outputs['changed']
assert outputs['missing'] == ''
report = {'id':'T2','status':'passed','version':importlib.metadata.version('changedetection.io'),'scope':'upstream HTML filter/text/ignore component, not full service','outputs':outputs,'assertions':{'noise_ignored':True,'claim_change_retained':True,'missing_selector_empty':True},'limits':['No crawl scheduling or notifications','No authenticated/browser-rendered site','Empty selection needs caller handling; not proof upstream silently misses it','Synthetic changes do not establish legal or commercial impact']}
(OUT / 'change-result.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
