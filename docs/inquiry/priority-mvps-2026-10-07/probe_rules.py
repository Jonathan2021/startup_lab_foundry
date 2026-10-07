"""Synthetic specification probes, not venture runtime code or demand evidence."""
from __future__ import annotations
import itertools,json,math,random,statistics
from pathlib import Path


def elo(ratings, a, b, win):
    assert len(a)==len(b) and not set(a)&set(b)
    expected=1/(1+10**((statistics.mean(ratings[x] for x in b)-statistics.mean(ratings[x] for x in a))/400))
    delta=24*(win-expected)
    result=dict(ratings)
    for x in a: result[x]+=delta
    for x in b: result[x]-=delta
    return result


def replay(matches):
    r=dict.fromkeys('abcdef',1000.0)
    for a,b,win in matches: r=elo(r,a,b,win)
    return r


def wait_summary(reports, now=100):
    # Fixture time unit is minutes. Expiry is strictly below 15 minutes.
    fresh={}
    for r in reports:
        if 0<=now-r['at']<15 and not r.get('hidden'):
            key=r['device']
            if key not in fresh or r['at']>fresh[key]['at']: fresh[key]=r
    vals=[r['wait'] for r in fresh.values()]
    if not vals:return {'state':'unknown','count':0}
    if max(vals)-min(vals)>15:return {'state':'conflicting','range':[min(vals),max(vals)],'count':len(vals)}
    return {'state':'single_report' if len(vals)==1 else 'recent_reports','wait':statistics.median(vals),'count':len(vals)}


def route_choices(routes,budget):
    viable=[r for r in routes if r['minutes']<=budget and r['hard_constraints']]
    pareto=[r for r in viable if not any((x['minutes']<=r['minutes'] and x['proxy']>=r['proxy']) and (x['minutes']<r['minutes'] or x['proxy']>r['proxy']) for x in viable)]
    # Same geometry fingerprint is one choice, however it was scored.
    unique={}
    for r in sorted(pareto,key=lambda x:(x['minutes'],-x['proxy'],x['id'])):unique.setdefault(r['geometry'],r)
    return list(unique.values())


def schedule(slots, exercises):
    # No automatic dose/intensity advice: scheduler selects approved fixed sessions.
    result=[]
    for slot in slots:
        allowed=[e for e in exercises if e['minutes']<=slot['minutes'] and set(e['requires'])<=set(slot['available'])]
        result.append({'slot':slot['id'],'exercise':allowed[0]['id'] if allowed and not slot.get('pain') else None})
    return result


def main():
    checks=[]
    r=replay([('abc','def',1)])
    assert r['a']==1012 and r['d']==988 and sum(r.values())==6000
    checks.append('equal teams: +12/-12, zero-sum with fixed equal team size')
    matches=[('abc','def',1),('abd','cef',0),('aef','bcd',1)]
    original=replay(matches);corrected=replay([('abc','def',0),*matches[1:]])
    assert original!=corrected and corrected==replay([('abc','def',0),*matches[1:]])
    checks.append('corrected result changes downstream history deterministically')
    assert wait_summary([])['state']=='unknown'
    assert wait_summary([{'device':'a','at':85,'wait':0}])['state']=='unknown'
    assert wait_summary([{'device':'a','at':99,'wait':0}])['wait']==0
    assert wait_summary([{'device':'a','at':98,'wait':0},{'device':'a','at':99,'wait':10}])['count']==1
    assert wait_summary([{'device':'a','at':99,'wait':0},{'device':'b','at':99,'wait':40}])['state']=='conflicting'
    checks.append('queue: empty, expiry boundary, genuine zero, device dedupe, disagreement')
    routes=[{'id':str(i),'minutes':m,'proxy':s,'hard_constraints':h,'geometry':g} for i,(m,s,h,g) in enumerate([(100,1,True,'a'),(120,4,True,'b'),(130,3,True,'c'),(150,9,True,'d'),(90,10,False,'e'),(120,4,True,'b')])]
    assert [r['id'] for r in route_choices(routes,140)]==['0','1']
    assert route_choices(routes,50)==[]
    checks.append('routes: hard constraints first, non-dominated tradeoffs, no duplicate/fake third route')
    slots=[{'id':'no-court','minutes':20,'available':['ball']},{'id':'court','minutes':40,'available':['court','ball']},{'id':'pain','minutes':40,'available':['court','ball'],'pain':True}]
    ex=[{'id':'court-practice','minutes':30,'requires':['court','ball']},{'id':'short-review','minutes':10,'requires':[]}]
    assert [x['exercise'] for x in schedule(slots,ex)]==['short-review','court-practice',None]
    checks.append('coach: duration/equipment/court constraints; reported pain suppresses auto scheduling')
    # Identifiability counterexample: always-fixed teams give equal changes to all teammates.
    fixed=replay([('abc','def',1)]*10)
    assert fixed['a']==fixed['b']==fixed['c']
    checks.append('rating limitation: fixed teammates cannot be individually distinguished by team results')
    result={'synthetic':True,'checks':checks,'passed':len(checks),'rating_example':r,'limits':['No adoption, coaching effectiveness, real-time queue accuracy or route beauty measurement.','Same-device deduplication is not Sybil resistance.','Elo is a group-relative game statistic, not official ability.']}
    Path(__file__).with_name('rules-probe.json').write_text(json.dumps(result,indent=2))
    print(json.dumps(result,indent=2))

if __name__=='__main__':main()
