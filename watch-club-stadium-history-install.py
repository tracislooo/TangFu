"""Install the prepared compact stadium/history patch after normal game exit."""
import datetime,json,subprocess,sys,time
from pathlib import Path
R=Path(__file__).resolve().parent
patch=Path(sys.argv[1]).resolve()
assert patch.parent==R and patch.name.startswith('club-stadium-compact-history-')
status=patch/'automatic-install-status.txt'
flag=getattr(subprocess,'CREATE_NO_WINDOW',0)
def running():
 result=subprocess.run(['tasklist','/FI','IMAGENAME eq fm.exe','/FO','CSV','/NH'],capture_output=True,creationflags=flag)
 assert result.returncode==0
 return b'"fm.exe"' in result.stdout.lower()
try:
 status.write_text('WAITING_FOR_GAME_EXIT\n','utf8')
 deadline=time.monotonic()+86400
 while running():
  if time.monotonic()>deadline:
   status.write_text('EXPIRED_WITHOUT_INSTALL\n','utf8')
   sys.exit(0)
  time.sleep(3)
 result=subprocess.run([sys.executable,str(R/'install-independent-resource-patch.py'),str(patch)],capture_output=True,creationflags=flag)
 (patch/'automatic-install.log').write_bytes(result.stdout+b'\n'+result.stderr)
 assert result.returncode==0,'Installation stopped by process or baseline hash validation.'
 index=R/'current-club-overview.json'
 data=json.loads(index.read_text('utf8'))
 data['stadium_compact_history']={'patch':str(patch),'installed':True,'installed_verified':True,'runtime_verified':False,'row_height':26,'details_height':156,'history_source':'native Club.LeagueHistory','restore':str(patch/'restore.ps1')}
 index.write_text(json.dumps(data,ensure_ascii=False,indent=2)+'\n','utf8')
 status.write_text('INSTALLED_VERIFIED\nRuntime appearance not verified.\n','utf8')
except BaseException as error:
 status.write_text('INSTALL_STOPPED\n'+repr(error)+'\n','utf8')
 raise
