"""Save the current light theme and reverse only the verified theme transaction chain."""
from pathlib import Path
import datetime,hashlib,json,os,shutil,subprocess,sys,uuid,zipfile,zoneinfo
R=Path(__file__).resolve().parent
SWITCH_SCRIPT=r'''from pathlib import Path
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
'''
steps=['light-ui-trial-20261111-092031','light-ui-trial-20261111-094236','light-ui-trial-20261111-095115','global-light-theme-20261111-102400','light-ui-readability-fix-20261111-104833']
stamp=datetime.datetime.now(zoneinfo.ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S')
out=R/'saved-progress'/('FM27-light-theme-'+stamp);out.mkdir(parents=True)
sha=lambda b:hashlib.sha256(b).hexdigest()
def digest(p):
 with Path(p).open('rb') as f:return hashlib.file_digest(f,'sha256').hexdigest()
latest={};first={};dark_hash={};protected={}
for step in steps:
 m=json.loads((R/step/'manifest.json').read_text('utf8'));tx=json.loads((R/step/'transaction.json').read_text('utf8'))
 for p,h in m['after_sha256'].items():
  if p in latest:assert latest[p]==m['before_sha256'][p],('Non-contiguous theme chain',step,p)
  else:first[p]=Path(tx['before'][p]);dark_hash[p]=m['before_sha256'][p]
  latest[p]=h
 protected.update(m['protected_sha256'])
dest_roots={'game':Path(tx['game']),'skin':Path(tx['skin'])}
assert dest_roots['game']==Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
protected={p:h for p,h in protected.items() if p not in latest}
for p,h in latest.items():assert digest(p)==h,('Live resource changed; rebase required',p)
for p,h in dark_hash.items():assert digest(first[p])==h,('Damaged original dark backup',p)
for p,h in protected.items():assert digest(p)==h,('Unrelated resource changed',p)
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
assert proc.returncode in [0,1]
if proc.stdout.strip():raise SystemExit('Exit Football Manager before restoring; game resources were not changed.')
files={}
for name,h in latest.items():
 p=Path(name);tag=next(tag for tag,root in dest_roots.items() if p.parent==root)
 rel=Path('game/aa/StandaloneWindows64')/p.name if tag=='game' else Path('skin/packages')/p.name
 light=out/rel;dark=out/'dark-before-light'/tag/p.name
 for target,src in [(light,p),(dark,first[name])]:target.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,target)
 assert digest(light)==h and digest(dark)==dark_hash[name]
 files[name]={'light':str(rel),'dark':str(dark.relative_to(out)),'light_sha256':h,'dark_sha256':dark_hash[name]}
for tag,root in dest_roots.items():
 for n in ['catalog.bin','catalog.hash']:
  src=(root.parent if tag=='game' else root)/n
  if src.exists():
   dst=out/('game/aa' if tag=='game' else 'skin/packages')/n;dst.parent.mkdir(parents=True,exist_ok=True);shutil.copy2(src,dst);assert digest(src)==digest(dst)
indexes=['current-ui-surface-theme.json','current-global-light-theme.json','current-light-ui-trial.json','current-light-readability-fix.json']
states={n:json.loads((R/n).read_text('utf8')) for n in indexes if (R/n).exists()}
(out/'state-before-rollback.json').write_text(json.dumps(states,ensure_ascii=False,indent=2),'utf8')
source_dir=out/'source';source_dir.mkdir()
for name in ['apply-page-surfaces-theme.py','build-light-ui-trial.py','build-global-light-theme.py','fix-light-theme-readability.py','install-global-light-theme.py','install-light-ui-trial.py','verify-light-readability-fix.py','verify-global-light-theme.py']:
 shutil.copy2(R/name,source_dir/name)
for step in steps:
 dst=out/'history'/step;dst.mkdir(parents=True)
 for n in ['manifest.json','transaction.json','qa-prepared.json','qa-readability.json']:
  if (R/step/n).exists():shutil.copy2(R/step/n,dst/n)
initial=json.loads((R/steps[0]/'manifest.json').read_text('utf8'))['original_ui_surface_index']
record={'scope':'All changes made by this chat for the light theme','steps':steps,'workspace':str(R),'archive':str(out),
        'files':files,'protected_sha256':protected,'dark_surface_index':initial,'saved_light_runtime_verified':False,
        'archive_verified':True,'dark_installed':False}
(out/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8')
(out/'switch-theme.py').write_text(SWITCH_SCRIPT,'utf8')
for name,flag in [('restore-light','--light'),('restore-dark','--dark')]:
 (out/(name+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'switch-theme.py') "+flag+"\nif($LASTEXITCODE -ne 0){throw 'Theme switch failed; see the error above.'}\n",'utf-8-sig')
(out/'说明.md').write_text('已归档当前浅色主题及其修正资源、源代码、校验与历史记录。game/aa为游戏资源，skin/packages为独立皮肤资源，dark-before-light为本聊天开始前的暗色基线。\n\nrestore-light.ps1仅在当前资源仍完全匹配这次暗色基线时恢复归档浅色版。restore-dark.ps1执行相反切换。两者均要求退出游戏，并校验当前资源和未修改资源；后续资源有改动时应增量迁移，不能旧整包覆盖。\n\n浅色版实际显示问题仍以用户截图为准，归档不代表所有问题已通过游戏验证。游戏存档、偏好、字体、纹理及侧栏原始布局不在本次回退范围。\n','utf8')
zpath=R/'exports'/('FM27-light-theme-saved-'+stamp+'.zip');zpath.parent.mkdir(exist_ok=True)
with zipfile.ZipFile(zpath,'w',compression=zipfile.ZIP_STORED) as z:
 for p in out.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(out))
with zipfile.ZipFile(zpath) as z:
 assert z.testzip() is None
 for entry in files.values():assert sha(z.read(entry['light'].replace('\\','/')))==entry['light_sha256']
print(json.dumps({'saved':str(out),'zip':str(zpath),'files':len(files),'archive_verified':True},ensure_ascii=False),flush=True)
result=subprocess.run([sys.executable,str(out/'switch-theme.py'),'--dark'],check=True,capture_output=True,text=True)
print(result.stdout,flush=True)
(R/'current-light-theme-archive.json').write_text(json.dumps({'archive':str(out),'zip':str(zpath),'archive_verified':True,'game_and_skin_mode':'dark','files_restored':len(files),'restore_light':str(out/'restore-light.ps1')},ensure_ascii=False,indent=2),'utf8')

