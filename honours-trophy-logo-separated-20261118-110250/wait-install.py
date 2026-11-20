"""Wait for a normal game exit, then run the hash-protected prepared installer."""
from pathlib import Path
import sys,json,subprocess,time,datetime
R=Path(__file__).resolve().parents[1];O=Path(sys.argv[1]).resolve()
assert O.parent==R and O.name.startswith('honours-trophy-logo-separated-')
status=O/'automatic-install-status.txt'
def write(s):status.write_text(s,encoding='utf8')
write('WAITING_FOR_GAME_EXIT\nNo game resources installed yet.\n')
deadline=time.monotonic()+86400
while time.monotonic()<deadline:
 p=subprocess.run(['tasklist','/FI','IMAGENAME eq fm.exe','/FO','CSV','/NH'],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
 if p.returncode!=0:
  write('FAILED_PROCESS_CHECK\n');sys.exit(1)
 if b'"fm.exe"' not in p.stdout.lower():
  result=subprocess.run([sys.executable,str(O/'installer.py'),str(O)],capture_output=True,creationflags=subprocess.CREATE_NO_WINDOW)
  (O/'automatic-install.log').write_bytes(result.stdout+b'\n'+result.stderr)
  if result.returncode:
   write('INSTALL_FAILED_HASH_OR_PROCESS_CHECK\nSee automatic-install.log. No forced overwrite attempted.\n');sys.exit(1)
  m=json.loads((O/'manifest.json').read_text('utf8'));assert m.get('installed_verified')
  ix=R/'current-honours-trophy-logo-separation.json';v=json.loads(ix.read_text('utf8'))
  if Path(v['patch']).resolve()==O:
   v.update(installed=True,installed_verified=True,runtime_verified=False);ix.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
  write('INSTALLED_VERIFIED\nInstalled after normal game exit. Runtime appearance has not been verified.\n');sys.exit(0)
 time.sleep(3)
write('EXPIRED_WITHOUT_INSTALL\nGame did not exit within 24 hours. Run install.ps1 after exiting.\n')
