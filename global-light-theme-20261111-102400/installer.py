"""Hash-guarded installation of the global palette; preserve the safe trial on rollback."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, uuid, zoneinfo

out = Path(next(x for x in sys.argv[1:] if not x.startswith('--'))).resolve()
restore, verify = '--restore' in sys.argv, '--verify' in sys.argv
m = json.loads((out/'manifest.json').read_text('utf8')); tx = json.loads((out/'transaction.json').read_text('utf8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
def digest(p):
    with p.open('rb') as f: return hashlib.file_digest(f,'sha256').hexdigest()
def atomic(p,raw):
    temp = p.with_name(p.name+'.codex-global-light-'+uuid.uuid4().hex+'.tmp')
    try: temp.write_bytes(raw); os.replace(temp,p)
    finally:
        if temp.exists(): temp.unlink()
assert Path(tx['game']) == Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
targets = {Path(k):Path(v) for k,v in tx['sources'].items()}; allowed = {Path(tx[k]).resolve() for k in ['game','skin']}
current = {p:p.read_bytes() for p in targets}
for p,source in targets.items():
    assert p.parent.resolve() in allowed
    assert digest(source) == m['after_sha256'][str(p)] and digest(Path(tx['before'][str(p)])) == m['before_sha256'][str(p)]
    wanted = m['after_sha256'][str(p)] if restore or verify else m['before_sha256'][str(p)]
    assert sha(current[p]) == wanted, ('Target changed; regenerate against latest resources',p)
for path,h in m['protected_sha256'].items(): assert digest(Path(path)) == h, ('Protected resource changed',path)
if verify:
    print(json.dumps({'installed_hashes_verified':True,'protected_hashes_verified':True,'files':len(targets),'runtime_verified':False}));sys.exit(0)
proc = subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
assert proc.returncode in [0,1], 'Could not check game process'
if proc.stdout.strip(): raise SystemExit('Exit Football Manager before installing/restoring; no files changed.')
written = {}
try:
    for p,source in targets.items():
        assert p.read_bytes() == current[p], ('Concurrent target change',p)
        raw = Path(tx['before'][str(p)]).read_bytes() if restore else source.read_bytes()
        written[p] = raw; atomic(p,raw); assert p.read_bytes() == raw
    for path,h in m['protected_sha256'].items(): assert digest(Path(path)) == h, ('Concurrent protected change',path)
except BaseException:
    for p,raw in reversed(list(written.items())):
        if p.read_bytes() == raw: atomic(p,current[p])
    raise
now = datetime.datetime.now(zoneinfo.ZoneInfo('America/Denver')).isoformat()
m.update(installed=not restore,installed_verified=not restore,restored=restore,changed_at=now)
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
root = Path(tx['workspace'])
state = {'status':'restored' if restore else 'installed','installed':not restore,'record':str(out),
         'palette':m['palette'],'scope':m['scope'],'manifest':str(out/'manifest.json'),
         'restore':str(out/'restore.ps1'),'runtime_verified':False,'changed_at':now}
if m.get('coverage'):state['coverage']=m['coverage']
if restore and m.get('previous_global_state'): state = m['previous_global_state']
(root/'current-global-light-theme.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
surface = root/'current-ui-surface-theme.json'
if restore: surf = m['original_ui_surface_index']
else:
    surf = json.loads(surface.read_text('utf8'))
    surf.update(color='#E7E7E7',card_color='#F7F7F5',scope=m['scope'],install_record=str(out/'manifest.json'),
                runtime_verified=False,global_light_theme=state)
trial_index=root/'current-light-ui-trial.json'
if restore:
    prior_trial=m['original_ui_surface_index'].get('light_trial')
    if prior_trial:trial_index.write_text(json.dumps(prior_trial,ensure_ascii=False,indent=2),'utf8')
elif trial_index.exists():
    prior_trial=json.loads(trial_index.read_text('utf8'))
    prior_trial.update(status='superseded_by_global_theme',installed=False,global_record=str(out))
    trial_index.write_text(json.dumps(prior_trial,ensure_ascii=False,indent=2),'utf8')
    if 'light_trial' in surf:surf['light_trial']=prior_trial
surface.write_text(json.dumps(surf,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':not restore,'restored':restore,'verified_files':len(targets),'record':str(out),'runtime_verified':False},ensure_ascii=False))
