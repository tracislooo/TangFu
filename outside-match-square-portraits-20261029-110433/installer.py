"""Install or restore a palette patch with independent game/skin style bases."""
from pathlib import Path
import hashlib, json, os, subprocess, sys, uuid

out=Path(next(x for x in sys.argv[1:] if not x.startswith('--'))).resolve()
restore='--restore' in sys.argv
verify='--verify' in sys.argv
m=json.loads((out/'manifest.json').read_text('utf8'))
tx=json.loads((out/'transaction.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()

def game_running():
    p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
    return bool(p.stdout.strip())

targets={Path(k):Path(v) for k,v in tx['sources'].items()}
current={p:p.read_bytes() for p in targets}
for p,source in targets.items():
    assert p.parent.resolve() in [Path(tx['game']).resolve(),Path(tx['game']).parent.resolve(),Path(tx['skin']).resolve()]
    assert sha(source.read_bytes())==m['after_sha256'][str(p)],('Damaged patch',source)
    backup=Path(tx['before'][str(p)])
    assert sha(backup.read_bytes())==m['before_sha256'][str(p)],('Damaged backup',backup)
    wanted=m['after_sha256'][str(p)] if restore or verify else m['before_sha256'][str(p)]
    actual=sha(current[p])
    assert actual==wanted or (not restore and not verify and actual==m['after_sha256'][str(p)]),('Target changed; refusing overwrite',p,actual,wanted)
for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,('Protected resource changed',p)
if verify:
    print(json.dumps({'installed_hashes_verified':True,'protected_hashes_verified':True,'files':len(targets)},ensure_ascii=False))
    sys.exit(0)
if game_running():raise SystemExit('Game is running. Exit Football Manager before installing/restoring.')

def atomic(p,data):
    temp=p.with_name(p.name+'.codex-nav-'+uuid.uuid4().hex+'.tmp')
    try:
        temp.write_bytes(data);os.replace(temp,p)
    finally:
        if temp.exists():temp.unlink()

try:
    for p,source in targets.items():
        assert p.read_bytes()==current[p],('Target changed during validation',p)
        data=Path(tx['before'][str(p)]).read_bytes() if restore else source.read_bytes()
        atomic(p,data);assert p.read_bytes()==data,('Write verification failed',p)
    for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,('Protected resource changed',p)
except BaseException:
    for p,b in current.items():atomic(p,b)
    raise
m.update(installed=not restore,installed_verified=not restore,restored=restore)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':not restore,'restored':restore,'verified_files':len(targets),'output':str(out)},ensure_ascii=False))
