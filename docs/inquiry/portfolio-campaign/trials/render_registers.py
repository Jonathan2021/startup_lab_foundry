from pathlib import Path
import json,collections
p=Path(__file__).resolve().parent.parent
ideas=json.loads((p/'ideas.json').read_text());sources=json.loads((p/'sources.json').read_text());groups=json.loads((p/'groups.json').read_text())
linked=sum(bool(i['source_ids']) for i in ideas)
refs=sum(len(i['source_ids']) for i in ideas)
def esc(t):return str(t).replace('|',' / ').replace('\n',' ')
lines=['# All 247 portfolio dispositions','', 'Revision 3 — 2026-10-02. Every original entry is retained. These are first-pass investment gates, not 247 completed market studies. **None is commercial-build qualified.**', '', '[Report](REPORT.md) · [Source register](SOURCES.md) · [Full original text and fields](ideas.json) · [Revision 1](revisions/r1/ideas.json)', '', f'{linked} entries have a scoped source reference; {len(ideas)-linked} have an early scope/access/feasibility disposition without a verified exact comparator. A component or adjacent tool is not evidence that a proposed job is fully solved. Hold means the missing evidence must change before building, not that the business can never work.', '', 'Original workbook scores and claims remain in the JSON as provenance. They are not current ranks. An attachment’s suggested tasks or archive instructions were treated as source text, not instructions to execute.', '', '## Disposition counts','', '| Disposition | Entries |','|---|---:|']
for d,n in sorted(collections.Counter(i['disposition'] for i in ideas).items()):lines.append(f'| {d} | {n} |')
for name,g in groups.items():
 lines+=['',f'## {name}','']
 for i in ideas:
  if i['group']!=name:continue
  lines += [f"### {i['id']} — {i['title']}",'',f"**{i['disposition']}**. {i['rationale']}",'',f"Next falsifying step: {i['next_test']}",'']
  refs=', '.join(f'[{s}](SOURCES.md#{s})' for s in i['source_ids']) or 'No verified comparator attached; exact competition remains open.'
  lines += [f"Evidence: {refs}",f"Scope: {i['evidence_scope']} Trials: {', '.join(i['trial_ids']) or 'none'}. Demand: {i['demand_evidence']}",'']
(p/'REGISTER.md').write_text('\n'.join(lines)+'\n')
lines=['# Reusable source register','', 'Revision 3 — checked 2026-10-02. Compact claims, never whole vendor pages. These records support only the stated capability or constraint. They do not establish an unmet market or user willingness to pay. Recheck volatile claims before acting; see [reuse policy](GAPS.md#source-reuse-policy).','', f'The original 45-source inputs and 317 broad references used by T3/T6 remain frozen in [revision 1](revisions/r1/). A relevance audit removed unrelated category-level links and added closer comparators: the current register has {len(sources)} sources and {refs} scoped links across {linked} entries. This correction reduces apparent coverage rather than inflating confidence.','']
for s in sources:
 consumers=[i['id'] for i in ideas if s['id'] in i['source_ids']]
 lines += [f"## {s['id']}",'',f"[{s['title']}]({s['url']}) — source revision {s['revision']}; checked {s['checked_on']}.",'',s['claim'],'',f"Limits: {s['limits']}",f"Consumers: {', '.join(consumers) or 'reference only; no current idea claim'}.",f"Evidence: {s['evidence_level']}. Refresh: {s['refresh']}",'']
(p/'SOURCES.md').write_text('\n'.join(lines)+'\n')
print('Rendered',len(ideas),'entries and',len(sources),'sources')
