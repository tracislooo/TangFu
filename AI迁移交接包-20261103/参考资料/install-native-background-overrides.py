"""Hash-guarded install/restore, including a previously absent skin bundle."""
from pathlib import Path
import hashlib,json,os,subprocess,sys,uuid
out=Path(next(a for a in sys.argv[1:] if not a.startswith('--'))).resolve()
restore='--restore' in sys.argv;verify='--verify' in sys.argv
m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest() if b is not None else None
def read(p):return p.read_bytes() if p.exists() else None
allowed={Path(tx[k]).resolve() for k in ['game','skin','workspace']}
targets={Path(k):Path(v) for k,v in tx['sources'].items()};current={p:read(p) for p in targets}
for p,source in targets.items():
 assert p.parent.resolve() in allowed,p
 assert sha(source.read_bytes())==m['after_sha256'][str(p)],('Damaged patch',source)
 backup=tx['before'][str(p)]
 assert sha(Path(backup).read_bytes() if backup else None)==m['before_sha256'][str(p)],('Damaged backup',p)
 expected=m['after_sha256'][str(p)] if restore or verify else m['before_sha256'][str(p)]
 assert sha(current[p])==expected or (not restore and not verify and sha(current[p])==m['after_sha256'][str(p)]),('Target changed',p)
for p,h in m['protected_sha256'].items():assert sha(read(Path(p)))==h,('Protected resource changed',p)
if verify:
 print(json.dumps({'installed_hashes_verified':True,'protected_hashes_verified':True,'files':len(targets)}));sys.exit(0)
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():raise SystemExit('Exit Football Manager before installing or restoring.')
def atomic(p,data):
 if data is None:
  if p.exists():p.unlink()
  return
 temp=p.with_name(p.name+'.codex-background-'+uuid.uuid4().hex+'.tmp')
 try:temp.write_bytes(data);os.replace(temp,p)
 finally:
  if temp.exists():temp.unlink()
written={}
try:
 for p,source in targets.items():
  assert read(p)==current[p],('Concurrent change',p)
  backup=tx['before'][str(p)];data=(Path(backup).read_bytes() if backup else None) if restore else source.read_bytes()
  written[p]=data
  atomic(p,data);assert read(p)==data
 for p,h in m['protected_sha256'].items():assert sha(read(Path(p)))==h,('Protected resource changed',p)
except BaseException:
 for p,data in reversed(list(written.items())):
  if read(p)==data:atomic(p,current[p])
 raise
m.update(installed=not restore,installed_verified=not restore,restored=restore)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':not restore,'restored':restore,'files_verified':len(targets),'output':str(out)},ensure_ascii=False))
