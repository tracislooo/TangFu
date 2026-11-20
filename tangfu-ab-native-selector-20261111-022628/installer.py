from pathlib import Path
import sys,json,hashlib,subprocess,os,uuid
out=Path(sys.argv[1]);restore='--restore' in sys.argv;m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
current={p:(Path(p).read_bytes() if Path(p).exists() else None) for p in tx['sources']}
for p,source in tx['sources'].items():
 assert (sha(Path(source).read_bytes()) if source else None)==m['after_sha256'][p]
 actual=sha(current[p]) if current[p] is not None else None
 assert actual==(m['after_sha256'][p] if restore else m['before_sha256'][p]),('Target changed',p)
 if tx['before'][p]:assert sha(Path(tx['before'][p]).read_bytes())==m['before_sha256'][p]
for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,('Protected resource changed',p)
running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if running.stdout.strip():raise SystemExit('Exit Football Manager before installing/restoring.')
def write(p,data):
 p=Path(p)
 if data is None:
  assert str(p)==m['removed_old_custom_file'];p.unlink(missing_ok=True);return
 p.parent.mkdir(parents=True,exist_ok=True);temp=p.with_name(p.name+'.tangfu-'+uuid.uuid4().hex+'.tmp')
 try:temp.write_bytes(data);os.replace(temp,p)
 finally:
  if temp.exists():temp.unlink()
try:
 for p,s in tx['sources'].items():
  assert (Path(p).read_bytes() if Path(p).exists() else None)==current[p]
  b=(Path(tx['before'][p]).read_bytes() if tx['before'][p] else None) if restore else (Path(s).read_bytes() if s else None);write(p,b)
  assert (Path(p).read_bytes() if Path(p).exists() else None)==b
 for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h
except BaseException:
 for p,b in current.items():write(p,b)
 raise
m.update(installed=not restore,installed_verified=not restore,restored=restore);(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':not restore,'verified_files':len(current),'output':str(out)}))
