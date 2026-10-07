import asyncio,json
from pathlib import Path
from pyppeteer import launch
out=Path('/home/jonathan/startup_lab/foundry/docs/inquiry/local-console-2026-10-02/gpx-trial-r2');out.mkdir(exist_ok=False)
for name,middle in [('baseline','13.365'),('detour','13.369')]:
 (out/(name+'.gpx')).write_text(f'''<?xml version="1.0" encoding="UTF-8"?><gpx version="1.1" creator="Foundry synthetic fixture" xmlns="http://www.topografix.com/GPX/1/1"><trk><name>Synthetic {name}</name><trkseg><trkpt lat="52.516" lon="13.377"/><trkpt lat="52.519" lon="{middle}"/><trkpt lat="52.515" lon="13.351"/></trkseg></trk></gpx>''')
async def main():
 browser=await launch(executablePath='/usr/bin/chromium',headless=True,userDataDir='/home/jonathan/startup_lab/foundry/.local/gpx-browser-r2',args=['--no-sandbox','--disable-dev-shm-usage'])
 page=await browser.newPage();await page.setViewport({'width':1440,'height':1000});actions=[]
 try:
  response=await page.goto('https://gpx.studio/app',waitUntil='networkidle2',timeout=45000)
  print('HTTP',response.status,flush=True)
  while True:
   data=await page.evaluate('''() => ({url:location.href,text:document.body.innerText,controls:Array.from(document.querySelectorAll('input,button,a,[role=button]')).map(e=>({tag:e.tagName,type:e.type,title:e.title,aria:e.getAttribute('aria-label'),text:e.textContent,accept:e.accept})).filter(e=>e.tag==='INPUT'||e.text||e.title||e.aria)})''')
   (out/f'state-{len(actions)}.json').write_text(json.dumps(data,indent=2)+'\n')
   await page.screenshot(path=str(out/f'screen-{len(actions)}.png'))
   print(json.dumps(data)[:11000],flush=True);print('READY',flush=True)
   cmd=json.loads(await asyncio.to_thread(input));actions.append(cmd)
   (out/'actions.json').write_text(json.dumps(actions,indent=2)+'\n')
   if cmd['op']=='quit':break
   if cmd['op']=='upload':
    element=await page.querySelector(cmd['selector']);await element.uploadFile(*(str(out/name) for name in cmd['files']))
    await asyncio.sleep(2)
   if cmd['op']=='click':await page.click(cmd['selector']);await asyncio.sleep(1)
 finally:await browser.close()
asyncio.run(main())
