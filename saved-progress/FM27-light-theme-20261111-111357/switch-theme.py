from pathlib import Path
import hashlib,json,os,subprocess,sys,uuid
out=Path(__file__).resolve().parent
m=json.loads((out/'manifest.json').read_text('utf8'));light='--light' in sys.argv
assert ('--light' in sys.argv)!=('--dark' in sys.argv)
def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(p,b):
 tmp=p.with_name(p.name+'.theme-switch-'+uuid.uuid4().hex+'.tmp')
 try:tmp.write_bytes(b);os.replace(tmp,p)
 finally:
  if tmp.exists():tmp.unlink()
allowed={Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64'),Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')}
kind='light' if light else 'dark';previous='dark' if light else 'light';current={}
for name,e in m['files'].items():
 p=Path(name);assert p.parent in allowed
 for k in ['light','dark']:assert digest(out/e[k])==e[k+'_sha256'],('Damaged saved resource',name,k)
 h=digest(p);assert h in [e[previous+'_sha256'],e[kind+'_sha256']],('Target changed; rebase required',p)
 current[p]=p.read_bytes()
for p,h in m['protected_sha256'].items():assert digest(p)==h,('Protected resource changed; rebase required',p)
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
assert proc.returncode in [0,1]
if proc.stdout.strip():raise SystemExit('Exit Football Manager before switching themes; no files changed.')
written={}
try:
 for name,e in m['files'].items():
  p=Path(name);assert p.read_bytes()==current[p],('Concurrent target change',p)
  raw=(out/e[kind]).read_bytes();written[p]=raw;atomic(p,raw);assert digest(p)==e[kind+'_sha256']
 for p,h in m['protected_sha256'].items():assert digest(p)==h,('Concurrent protected change',p)
except BaseException:
 for p,raw in reversed(list(written.items())):
  if p.read_bytes()==raw:atomic(p,current[p])
 raise
root=Path(m['workspace']);states=json.loads((out/'state-before-rollback.json').read_text('utf8'))
if light:
 for name,state in states.items():(root/name).write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
else:
 surface=m['dark_surface_index'].copy();surface['saved_light_theme_archive']=str(out)
 (root/'current-ui-surface-theme.json').write_text(json.dumps(surface,ensure_ascii=False,indent=2),'utf8')
 for name,state in states.items():
  if name=='current-ui-surface-theme.json':continue
  state.update(status='archived_dark_restored',installed=False,current_mode='dark',archive=str(out),restore_light=str(out/'restore-light.ps1'))
  (root/name).write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
m.update(dark_installed=not light,current_mode=kind,installed_hashes_verified=True,protected_hashes_verified=True)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'current_mode':kind,'verified_files':len(m['files']),'protected_resources_unchanged':True,'archive':str(out)},ensure_ascii=False))
