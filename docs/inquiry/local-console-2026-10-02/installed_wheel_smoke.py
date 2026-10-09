import json,os,subprocess,time
from importlib.metadata import version
from pathlib import Path
from urllib.request import urlopen
from zipfile import ZipFile

out=Path('/home/jonathan/startup_lab/foundry/docs/inquiry/local-console-2026-10-02')
wheel=Path('/tmp/foundry-console-final-wheel/startup_foundry-0.0.1-py3-none-any.whl')
with ZipFile(wheel) as z:
 names=z.namelist()
 assets=[x for x in names if '/templates/' in x or '/static/' in x]
 assert len(assets)==17
 assert any('7ce261002001' in x for x in names)
env=dict(os.environ,FOUNDRY_DATABASE_URL='sqlite:////tmp/foundry-wheel-smoke.local.db',FOUNDRY_REQUESTS_DIR='/tmp/foundry-wheel-requests')
with (out/'logs/installed-wheel-server.txt').open('w') as log:
 process=subprocess.Popen(['/tmp/foundry-console-installed-wheel/bin/foundry','ui','--port','8767'],cwd='/tmp',env=env,stdout=log,stderr=log)
 try:
  for attempt in range(60):
   try:
    with urlopen('http://127.0.0.1:8767/',timeout=1) as response:
     html=response.read().decode();assert response.status==200 and 'Find what is worth building' in html
    break
   except OSError:
    if process.poll() is not None: raise
    time.sleep(.2)
  else:raise AssertionError('Installed server did not become ready')
  for path in ['/static/console.css','/static/console.js','/new','/requests']:
   with urlopen('http://127.0.0.1:8767'+path,timeout=3) as response:
    assert response.status==200 and len(response.read())>50
  with urlopen('http://127.0.0.1:8767/api/ideas') as response:
   assert json.load(response)['total']==0
 finally:
  process.terminate();process.wait(timeout=10)
report={'cwd':'/tmp','installed_wheel':str(wheel),'migration':'fresh database upgraded through 7ce261002001','templates_and_static_assets':len(assets),'http_pages_and_assets':'passed','server_stopped':True,'dependency_policy':'unlocked wheel install within declared version bounds; main regression used uv.lock','versions':{name:version(name) for name in ['startup-foundry','sqlalchemy','alembic','fastapi','starlette','jinja2','uvicorn']}}
(out/'installed-wheel-smoke.json').write_text(json.dumps(report,indent=2)+'\n')
print(json.dumps(report,indent=2))
