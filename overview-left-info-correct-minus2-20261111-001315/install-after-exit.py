from pathlib import Path
import json,hashlib,subprocess,time
root=Path(__file__).parent
p=root/'manifest.json'
m=json.loads(p.read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
while subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():time.sleep(10)
try:
 for f in m['files']:assert sha(Path(f['target']).read_bytes())==f['before'],'Baseline changed: '+f['target']
 for f in m['files']:assert sha(Path(f['prepared']).read_bytes())==f['after']
 for f in m['files']:Path(f['target']).write_bytes(Path(f['prepared']).read_bytes())
 for f in m['files']:assert sha(Path(f['target']).read_bytes())==f['after']
 m.update(installed=True,installed_verified=True)
 p.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
 (root/'automatic-install-status.txt').write_text('Installed and verified','utf8')
except Exception as ex:
 (root/'automatic-install-status.txt').write_text(str(ex),'utf8')
 raise
