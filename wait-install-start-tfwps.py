import json,subprocess,sys,time,datetime
from pathlib import Path
out=Path(sys.argv[1]);status=out/'automatic-install-status.json'
def save(state,**extra):status.write_text(json.dumps({'state':state,'time':datetime.datetime.now(datetime.timezone.utc).isoformat(),**extra},ensure_ascii=False,indent=2),'utf8')
save('waiting_for_game_exit')
while True:
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 if not p.stdout.strip():break
 time.sleep(5)
result=subprocess.run([sys.executable,str(Path(__file__).resolve().parent/'start-banner-tfwps-link.py'),'--install',str(out)],capture_output=True,text=True)
(out/'automatic-install-output.txt').write_text(result.stdout+'\n'+result.stderr,'utf8')
manifest=json.loads((out/'manifest.json').read_text('utf8'))
save('installed' if result.returncode==0 and manifest.get('installed') else 'needs_attention',exit_code=result.returncode)
