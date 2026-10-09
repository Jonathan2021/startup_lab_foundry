import asyncio,json
from pathlib import Path
from pyppeteer import launch
out=Path('/home/jonathan/startup_lab/foundry/docs/inquiry/portfolio-campaign/trials/t7-liberty');out.mkdir(exist_ok=False)
state='/home/jonathan/startup_lab/foundry/.local/portfolio-campaign/t7-liberty-browser'
async def main():
 b=await launch(executablePath='/usr/bin/chromium',headless=True,userDataDir=state,args=['--no-sandbox','--disable-dev-shm-usage'])
 p=await b.newPage();await p.setViewport({'width':1440,'height':960});log=[]
 try:
  await p.goto('https://liberty-rider.com/fr/roadbooks/edit',waitUntil='networkidle2',timeout=45000)
  while True:
   print('READY',flush=True)
   line=await asyncio.to_thread(input);cmd=json.loads(line);log.append(cmd)
   if cmd['op']=='quit':break
   try:
    if cmd['op']=='type':await p.type(cmd['selector'],cmd['text'])
    elif cmd['op']=='click':await p.click(cmd['selector'])
    elif cmd['op']=='press':await p.keyboard.press(cmd['key'])
    elif cmd['op']=='wait':await p.waitForSelector(cmd['selector'],timeout=10000)
    elif cmd['op']=='upload':await (await p.querySelector(cmd['selector'])).uploadFile(cmd['path'])
    elif cmd['op']=='screenshot':await p.screenshot(path=str(out/cmd['name']))
    elif cmd['op']=='inspect':
     data=await p.evaluate("""() => ({body:document.body.innerText,controls:Array.from(document.querySelectorAll('input,button,select,[role=option],li')).map(e=>({tag:e.tagName,type:e.type,text:e.innerText,title:e.title,placeholder:e.placeholder,cls:e.className,aria:e.getAttribute('aria-label')})).filter(e=>e.tag==='INPUT'||e.text||e.title||e.aria)})""")
     (out/f"state-{len(log)}.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n');print(json.dumps(data,ensure_ascii=False)[:13000],flush=True)
   except Exception as e: print(type(e).__name__,str(e),flush=True);log.append({'error':str(e)})
   (out/'actions.json').write_text(json.dumps(log,ensure_ascii=False,indent=2)+'\n')
 finally:await b.close()
asyncio.run(main())
