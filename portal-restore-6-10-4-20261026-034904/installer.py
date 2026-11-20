"""Install the two prepared bundles and migrate only their four matching saved grids."""
from pathlib import Path
import sys,json,hashlib,subprocess,os,uuid,datetime
from importlib.util import spec_from_file_location,module_from_spec

restore='--restore' in sys.argv
out=Path(next(a for a in sys.argv[1:] if not a.startswith('--'))).resolve()
manifest=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
spec=spec_from_file_location('grid_migration',out/'grid_migration.py');migration=module_from_spec(spec);spec.loader.exec_module(migration)
sha=lambda b:hashlib.sha256(b).hexdigest()
def assert_game_closed():
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 assert not p.stdout.strip(),'Exit Football Manager normally before installing/restoring this patch.'
assert_game_closed()
game=Path(tx['game']).resolve();skin=Path(tx['skin']).resolve();cache_root=Path(tx['cache_root']).resolve()
targets={};current={};resource_count=0
for folder,tag in [(game,'game'),(skin,'skin')]:
 for name in tx['files']:
  path=folder/name;assert path.parent.resolve()==folder
  previous=path.read_bytes();source=(out/name).read_bytes()
  assert sha(source)==manifest['after_sha256'][name],('Prepared bundle damaged',name)
  expected=manifest['after_sha256'][name] if restore else manifest['before_sha256'][str(path)]
  assert sha(previous)==expected or (not restore and sha(previous)==manifest['after_sha256'][name]),('Installed resource changed since preparation',str(path))
  data=(out/('backup-'+tag)/name).read_bytes() if restore else source
  if restore:assert sha(data)==manifest['before_sha256'][str(path)],('Backup bundle damaged',name)
  targets[path]=data;current[path]=previous;resource_count+=1
for path,h in manifest['protected_sha256'].items():assert sha(Path(path).read_bytes())==h,('Unrelated resource changed',path)
cache_audits=[]
for name,versions in tx['cache_versions'].items():
 path=cache_root/name;assert path.resolve().parent==cache_root
 if not path.exists():continue
 original=path.read_bytes();document=json.loads(original)
 original_backup=out/'backup-custom'/name
 old_limits=json.loads(original_backup.read_text('utf8')) if restore and original_backup.exists() else None
 result=migration.migrate_layout(document,forward=not restore,version=versions['before' if restore else 'after'],limits_from=old_limits,layout_name=name)
 data=json.dumps(result,ensure_ascii=False,separators=(',',':')).encode('utf8')
 if restore:
  backup_dir=out/('backup-before-restore-custom-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
 else:backup_dir=out/'backup-custom'
 backup_dir.mkdir(exist_ok=True)
 backup=backup_dir/name
 if not backup.exists():backup.write_bytes(original)
 if not restore:(out/name).write_bytes(data)
 targets[path]=data;current[path]=original
 cache_audits.append({'path':str(path),'before_sha256':sha(original),'after_sha256':sha(data),'backup':str(backup),'selected_modules_preserved':[c['m_elementID'] for c in result['m_gridComponents']]})
other_caches={path:sha(path.read_bytes()) for path in cache_root.iterdir() if path.is_file() and path not in targets} if cache_root.exists() else {}
assert_game_closed()
for path,b in current.items():assert path.read_bytes()==b,('A target changed during preflight',str(path))
def atomic(path,data):
 temp=path.with_name(path.name+'.codex-highlight-'+uuid.uuid4().hex+'.tmp')
 try:temp.write_bytes(data);os.replace(temp,path)
 finally:
  if temp.exists():temp.unlink()
try:
 for path,data in targets.items():atomic(path,data);assert path.read_bytes()==data
 for path,h in other_caches.items():assert sha(path.read_bytes())==h,('Other saved layout changed',str(path))
 for path,h in manifest['protected_sha256'].items():assert sha(Path(path).read_bytes())==h
except BaseException:
 for path,data in current.items():atomic(path,data)
 raise
manifest.update(installed=not restore,installed_verified=not restore,restored=restore)
manifest['cache_restore' if restore else 'cache_install']=cache_audits
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':not restore,'restored':restore,'verified_resource_files':resource_count,'migrated_saved_layouts':len(cache_audits),'output':str(out)},ensure_ascii=False))
