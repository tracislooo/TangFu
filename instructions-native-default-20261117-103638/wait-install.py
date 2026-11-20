from pathlib import Path
import subprocess,sys,time,json
out=Path(sys.argv[1])
while subprocess.run(['powershell','-NoProfile','-Command','Get-Process fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip():time.sleep(4)
p=subprocess.run([sys.executable,str(out/'installer.py'),str(out)],capture_output=True,text=True)
(out/'automatic-install-status.txt').write_text(p.stdout+p.stderr,encoding='utf8')
if p.returncode==0:
 Path(out.parent/'current-instructions-native-default.json').write_text(json.dumps({'manifest':str(out/'manifest.json'),'installed':True,'runtime_verified':False},indent=2),encoding='utf8')
