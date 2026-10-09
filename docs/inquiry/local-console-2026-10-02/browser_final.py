"""Final browser QA: persisted portfolio + forms in a disposable database."""
import asyncio
import json
from pathlib import Path
from pyppeteer import launch

BASE = Path(__file__).resolve().parent
OUT = BASE/'browser-final'
OUT.mkdir(exist_ok=False)

async def navigation(page, prefix):
    for _ in range(100):
        if page.url.startswith(prefix):
            await page.waitForSelector('h1',timeout=10000)
            return
        await asyncio.sleep(0.1)
    raise AssertionError('Expected navigation: '+prefix)

async def main():
    browser=await launch(executablePath='/usr/bin/chromium',headless=True,
        userDataDir=str(BASE.parents[2]/'.local/console-browser-final'),
        args=['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking'])
    results=[]
    try:
        page=await browser.newPage()
        await page.setViewport({'width':1440,'height':1000})
        # This server uses a disposable database and inbox; no fake portfolio data.
        test='http://127.0.0.1:8766'
        await page.goto(test+'/new',waitUntil='networkidle0')
        for name,value in {'title':'Synthetic browser QA parent','description':'Check creation and derivation forms.','customer':'QA fixture','validation_test':'A child must retain its parent.'}.items():
            await page.type('form[data-api="/api/ideas"] [name="'+name+'"]',value)
        await page.click('form[data-api="/api/ideas"] button[type="submit"]')
        await navigation(page,test+'/ideas/')
        parent=page.url.rsplit('/',1)[-1]
        await page.goto(test+'/new?parent_id='+parent,waitUntil='networkidle0')
        for name,value in {'title':'Synthetic browser QA child','description':'Retain lineage after save.','derivation_reason':'Narrow a problem based on evidence.'}.items():
            await page.type('form[data-api="/api/ideas"] [name="'+name+'"]',value)
        await page.click('form[data-api="/api/ideas"] button[type="submit"]')
        await navigation(page,test+'/ideas/')
        body=await page.evaluate('document.body.innerText')
        assert parent in body and 'Narrow a problem' in body
        results.append({'check':'create and derive via browser forms','database':'disposable','parent':parent,'child_url':page.url})
        await page.click('form[data-api$="/promote"] button[type="submit"]')
        await navigation(page,test+'/ventures/')
        assert 'Discovery' in await page.evaluate('document.body.innerText')
        await page.select('select[name="kind"]','agent_research')
        await page.click('form[data-api="/api/steps"] button[type="submit"]')
        await navigation(page,test+'/steps/')
        assert 'Blocked' in await page.evaluate('document.body.innerText')
        results.append({'check':'promote and request agent via browser','outcome':'explicitly blocked; disposable handoff file'})
        await page.screenshot(path=str(OUT/'blocked-fixture.png'))
        real='http://127.0.0.1:8765'
        for label,path in [('overview','/'),('derived','/ideas/D001'),('sources','/sources?q=Distill'),('route-decisions','/ventures/v-route-repair/records/decisions'),('inbox','/requests')]:
            response=await page.goto(real+path,waitUntil='networkidle0')
            assert response.status==200
            overflow=await page.evaluate('document.documentElement.scrollWidth > innerWidth')
            assert not overflow
            await page.screenshot(path=str(OUT/(label+'.png')))
            results.append({'page':path,'status':response.status,'horizontal_overflow':overflow})
        counts=await page.evaluate("async () => {const r=await fetch('/api/ideas');return (await r.json()).total}")
        assert counts==250
        await page.setViewport({'width':390,'height':844})
        await page.goto(real+'/ideas/D001',waitUntil='networkidle0')
        assert not await page.evaluate('document.documentElement.scrollWidth > innerWidth')
        await page.screenshot(path=str(OUT/'mobile-derived.png'))
        results.append({'check':'restart retained portfolio','ideas':counts,'mobile_horizontal_overflow':False})
        (OUT/'result.json').write_text(json.dumps(results,indent=2)+'\n')
        print(json.dumps(results,indent=2))
    finally:
        await browser.close()

asyncio.run(main())
