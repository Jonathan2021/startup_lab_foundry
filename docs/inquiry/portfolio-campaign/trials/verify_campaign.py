"""Read-only campaign evidence checks; no network, DB mutations or model calls."""
from pathlib import Path
import collections
import hashlib
import json
import re
import subprocess

BASE = Path(__file__).resolve().parent.parent
ROOT = BASE.parents[3]

def read(relative):
    return json.loads((BASE / relative).read_text())

def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()

ideas, sources = read('ideas.json'), read('sources.json')
ids = [i['id'] for i in ideas]
expected = {f'P{i:03d}' for i in range(1, 213)} | {f'G{i:03d}' for i in range(1, 26)} | {'U001'} | {f'N{i:03d}' for i in range(1, 10)}
assert len(ids) == 247 and set(ids) == expected
assert len(set(s['id'] for s in sources)) == len(sources) == 85
source_ids = {s['id'] for s in sources}
for idea in ideas:
    assert set(idea['source_ids']) <= source_ids
    assert idea['rationale'] and idea['next_test'] and idea['evidence_scope']
    assert not idea['commercial_build_qualified']
for item in read('intake-manifest.json')['files']:
    assert digest(Path(item['path'])) == item['sha256']

recording = read('foundry-recording/provenance.json')
assert digest(ROOT/'foundry/src/startup_foundry/application.py') == recording['code_sha256']
for name, hash_value in recording['input_sha256'].items():
    assert digest(BASE/name) == hash_value
campaign = read('foundry-recording/campaign-snapshot.json')
route = read('foundry-recording/route-snapshot.json')
for key, count in recording['counts'].items():
    assert len(campaign[key]) == count
assert {w['id'][7:] for w in campaign['work_items'] if w['id'].startswith('triage-')} == expected
assert len(route['assumptions']) == len(route['assumption_assessments']) == 3
assert len(route['evidence']) == 4 and len(route['decisions']) == 1
assert len(route['work_items']) == 1 and not route['experiments']
for snapshot in [campaign, route]:
    for artifact in snapshot['artifacts']:
        assert digest(Path(artifact['location'])) == artifact['name'].split(' SHA256 ')[-1]
assert not ({x['id'] for x in campaign['assumptions']} & {x['id'] for x in route['assumptions']})
for name, hash_value in read('trials/t6/result.json')['input_sha256'].items():
    assert digest(BASE/'revisions/r1'/name) == hash_value
assert read('trials/mlflow-result.json')['status'] == 'passed'
assert read('trials/change-result.json')['status'] == 'passed'
assert read('trials/t5/result.json')['outcome'] == 'INCONCLUSIVE'
assert not read('trials/rider-result.json')['liberty']['export_completed']
assert read('trials/new-routing-result.json')['planning_submissions'] == 0

# Local path validation only; URLs are checked/revalidated by scoped research.
missing = []
for md in [*BASE.glob('*.md'), BASE/'trials/README.md']:
    for raw in re.findall(r'\[[^\]]*\]\(([^)]+)\)', md.read_text()):
        target = raw.split('#', 1)[0].strip('<>')
        if not target or '://' in target or target.startswith('mailto:'):
            continue
        if not (md.parent/target).exists():
            missing.append((str(md.relative_to(BASE)), target))
assert not missing, missing

# Reading the supported CLI must reconstruct the persisted portable snapshots.
for venture, snapshot in [('portfolio-campaign', campaign), ('v-route-repair', route)]:
    completed = subprocess.run([
        str(ROOT/'.venv/bin/foundry'), '--store',
        str(ROOT/'foundry/.local/portfolio-campaign/campaign.local.db'),
        'venture', 'show', '--id', venture,
    ], capture_output=True, text=True, check=True, cwd=ROOT)
    assert json.loads(completed.stdout) == snapshot

print(json.dumps({
    'status': 'passed', 'ideas': len(ideas), 'sources': len(sources),
    'scoped_links': sum(len(i['source_ids']) for i in ideas),
    'ideas_with_references': sum(bool(i['source_ids']) for i in ideas),
    'ideas_without_exact_comparator_reference': sum(not i['source_ids'] for i in ideas),
    'commercial_build_qualified': 0,
    'artifact_hashes_checked': sum(len(s['artifacts']) for s in [campaign, route]),
    'cli_snapshots_match': True, 'local_doc_links_resolve': True,
    'original_attachments_unchanged': True, 'frozen_t6_inputs_match': True,
    'disposition_counts': dict(sorted(collections.Counter(i['disposition'] for i in ideas).items())),
}, indent=2))
