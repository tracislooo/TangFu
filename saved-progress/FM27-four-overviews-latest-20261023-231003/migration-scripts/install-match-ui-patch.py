"""Install/restore a prepared patch with hash preconditions and transactional rollback."""
from pathlib import Path
import json,sys,hashlib,subprocess,os,uuid

restore='--restore' in sys.argv
out=Path(next(a for a in sys.argv[1:] if not a.startswith('--'))).resolve()
manifest=json.loads((out/'manifest.json').read_text('utf8'))
tx=json.loads((out/'transaction.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
game=Path(tx['game']);skin=Path(tx['skin'])
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():raise SystemExit('Game is running. Exit Football Manager, then run this script again.')
targets={}
for folder in [game,skin]:
 for n in tx['files']:
  target=folder/n if n.endswith('.bundle') or folder==skin else folder.parent/n
  assert target.parent.resolve() in [game.resolve(),game.parent.resolve(),skin.resolve()]
  targets[target]=out/n
current={p:p.read_bytes() if p.exists() else None for p in targets}
for p,source in targets.items():
 assert sha(source.read_bytes())==manifest['after_sha256'][p.name],('damaged patch',source)
 expected=manifest['after_sha256'][p.name] if restore else manifest['before_sha256'].get(str(p))
 actual=sha(current[p]) if current[p] is not None else None
 if not restore and actual==manifest['after_sha256'][p.name]:continue
 assert actual==expected,('file changed since preparation; refusing to overwrite',str(p),actual,expected)
for p,h in manifest['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,('unrelated installed resource changed',p)
def atomic(p,b):
 if b is None:
  if p.exists():p.unlink()
  return
 temp=p.with_name(p.name+'.codex-match-ui-'+uuid.uuid4().hex+'.tmp')
 try:temp.write_bytes(b);os.replace(temp,p)
 finally:
  if temp.exists():temp.unlink()
try:
 for p,source in targets.items():
  data=(Path(tx['before'][str(p)]).read_bytes() if str(p) in tx['before'] else None) if restore else source.read_bytes()
  atomic(p,data)
  assert (p.read_bytes() if p.exists() else None)==data,('write verification failed',p)
 for p,h in manifest['protected_sha256'].items():assert sha(Path(p).read_bytes())==h
except BaseException:
 for p,b in current.items():atomic(p,b)
 raise
manifest.update(installed=not restore,installed_verified=not restore,restored=restore)
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':not restore,'restored':restore,'verified_files':len(targets),'output':str(out)},ensure_ascii=False))
