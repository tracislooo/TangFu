"""Install prepared stadium lookup after normal game exit; rebase if resources changed."""
from pathlib import Path
import sys,json,subprocess,time,hashlib,datetime
R=Path(__file__).resolve().parent;initial=Path(sys.argv[1]).resolve();O=initial
assert O.parent==R and O.name.startswith('club-stadium-comeback-')
status=initial/'automatic-install-status.txt';flag=getattr(subprocess,'CREATE_NO_WINDOW',0)
sha=lambda b:hashlib.sha256(b).hexdigest()
def write(s):status.write_text(s,'utf8')
def running():
 p=subprocess.run(['tasklist','/FI','IMAGENAME eq fm.exe','/FO','CSV','/NH'],capture_output=True,creationflags=flag)
 assert p.returncode==0,'Process check failed'
 return b'"fm.exe"' in p.stdout.lower()
write('WAITING_FOR_GAME_EXIT\nNo game resources installed yet.\n')
deadline=time.monotonic()+86400
try:
 while running():
  if time.monotonic()>deadline:write('EXPIRED_WITHOUT_INSTALL\nExit game and run install.ps1 manually.\n');sys.exit(0)
  time.sleep(3)
 tx=json.loads((O/'transaction.json').read_text('utf8'));m=json.loads((O/'manifest.json').read_text('utf8'))
 changed=any(sha(Path(x['target']).read_bytes()) not in [x['before'],x['after']] for x in tx)
 changed|=any(sha(Path(p).read_bytes())!=h for p,h in m['protected_sha256'].items())
 if changed:
  write('REBASING_ON_LATEST_RESOURCES\n')
  p=subprocess.run([sys.executable,str(R/'build-club-stadium-comeback.py')],capture_output=True,creationflags=flag)
  (initial/'automatic-rebase.log').write_bytes(p.stdout+b'\n'+p.stderr);assert p.returncode==0,'Rebase failed'
  O=Path(json.loads((R/'current-club-stadium-comeback.json').read_text('utf8'))['patch']);tx=json.loads((O/'transaction.json').read_text('utf8'))
 assert not running(),'Game was restarted before install'
 p=subprocess.run([sys.executable,str(R/'install-independent-resource-patch.py'),str(O)],capture_output=True,creationflags=flag)
 (initial/'automatic-install.log').write_bytes(p.stdout+b'\n'+p.stderr);assert p.returncode==0,'Installer hash/process check failed'
 assert all(sha(Path(x['target']).read_bytes())==x['after'] for x in tx)
 ix=R/'current-club-stadium-comeback.json';v=json.loads(ix.read_text('utf8'));assert Path(v['patch'])==O
 v.update(installed=True,installed_verified=True,runtime_verified=False);ix.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
 ix=R/'current-club-overview.json';v=json.loads(ix.read_text('utf8'))
 v.update(installed=True,runtime_verified=False,manifest=str(O/'manifest.json'),verification=str(O/'manifest.json'),stadium_image_binding='Comeback native DatabaseObjectWithColourReplacementFallback: club.MainTeam.KitHome, Kit2DFront, fmetstadium; kit2d_<clubid>_fmetstadium -> existing local stadium photo',stadium_photo_club_mappings=json.loads((O/'manifest.json').read_text('utf8'))['photo_clubs'])
 ix.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
 record=dict(installed=True,installed_verified=True,runtime_verified=False,patch=str(O),verified_resource_files=len(tx),checked_utc=datetime.datetime.now(datetime.timezone.utc).isoformat())
 (O/'verification-installed.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
 write('INSTALLED_VERIFIED\n'+str(O)+'\nRuntime appearance has not been verified.\n')
 if O!=initial:(O/'automatic-install-status.txt').write_text('INSTALLED_VERIFIED\nRuntime appearance has not been verified.\n','utf8')
except BaseException as e:
 write('INSTALL_STOPPED_NO_FORCED_OVERWRITE\n'+repr(e)+'\n');raise
