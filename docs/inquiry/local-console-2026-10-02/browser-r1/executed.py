"""Browser smoke over the actual local console; mutations are real named work."""
import asyncio
import json
from pathlib import Path
from pyppeteer import launch

BASE = Path(__file__).resolve().parent
OUT = BASE/'browser-r1'
OUT.mkdir(exist_ok=False)

async def main():
    browser = await launch(executablePath='/usr/bin/chromium', headless=True,
                           userDataDir=str(BASE.parents[2]/'.local/console-browser-r1'),
                           args=['--no-sandbox','--disable-dev-shm-usage','--disable-background-networking'])
    result=[]
    try:
        page=await browser.newPage()
        await page.setViewport({'width':1440,'height':1000})
        for key,path in [('overview','/'),('ideas','/ideas?q=route'),
                         ('rider','/ideas/N008'),('requests','/requests'),
                         ('venture','/ventures/v-route-repair')]:
            response=await page.goto('http://127.0.0.1:8765'+path,waitUntil='networkidle0')
            assert response.status==200,(path,response.status)
            result.append({'page':path,'status':response.status,
                           'heading':await page.evaluate('document.querySelector("h1").textContent'),
                           'horizontal_overflow':await page.evaluate('document.documentElement.scrollWidth > innerWidth')})
            await page.screenshot(path=str(OUT/(key+'.png')))
        # Run a useful readiness check for the retained rider venture via its form.
        await page.click('form[data-api="/api/steps"] button[type="submit"]')
        await page.waitForSelector('h1',timeout=10000)
        await page.waitForFunction('location.pathname.startsWith("/steps/")',timeout=10000)
        text=await page.evaluate('document.body.innerText')
        assert 'Succeeded' in text and 'Input completeness' in text
        result.append({'action':'rider readiness through UI','url':page.url,'outcome':'succeeded'})
        await page.screenshot(path=str(OUT/'readiness.png'))
        await page.setViewport({'width':390,'height':844})
        await page.goto('http://127.0.0.1:8765/',waitUntil='networkidle0')
        await page.screenshot(path=str(OUT/'mobile.png'))
        assert not await page.evaluate('document.documentElement.scrollWidth > innerWidth')
        (OUT/'result.json').write_text(json.dumps(result,indent=2)+'\n')
        print(json.dumps(result,indent=2))
    finally:
        await browser.close()

asyncio.run(main())
