"""Install/restore the exact prepared palette with baseline and concurrency guards."""
from pathlib import Path
import datetime, hashlib, json, os, subprocess, sys, uuid, zoneinfo

out = Path(next(x for x in sys.argv[1:] if not x.startswith('--'))).resolve()
restore, verify = '--restore' in sys.argv, '--verify' in sys.argv
m = json.loads((out / 'manifest.json').read_text('utf8'))
tx = json.loads((out / 'transaction.json').read_text('utf8'))
targets = {Path(k): Path(v) for k, v in tx['sources'].items()}
if restore and m.get('rollback_contains_reported_crash'):
    raise SystemExit('This backup is the reported crashing version. Rebase a rollback to the earlier safe palette instead.')
sha = lambda b: hashlib.sha256(b).hexdigest()

def filehash(p):
    with p.open('rb') as f: return hashlib.file_digest(f, 'sha256').hexdigest()

def running():
    proc = subprocess.run(['powershell', '-NoProfile', '-Command',
                           'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],
                          capture_output=True, text=True, check=False)
    if proc.returncode not in [0, 1]: raise RuntimeError('Could not check game process')
    return bool(proc.stdout.strip())

def atomic(p, data):
    temp = p.with_name(p.name + '.codex-light-' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_bytes(data)
        os.replace(temp, p)
    finally:
        if temp.exists(): temp.unlink()

allowed = {Path(tx[k]).resolve() for k in ['game', 'skin']}
assert Path(tx['game']) == Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
current = {p: p.read_bytes() for p in targets}
for p, source in targets.items():
    assert p.parent.resolve() in allowed, ('Unexpected target', p)
    assert filehash(source) == m['after_sha256'][str(p)], ('Damaged patch', source)
    assert filehash(Path(tx['before'][str(p)])) == m['before_sha256'][str(p)], ('Damaged backup', p)
    wanted = m['after_sha256'][str(p)] if restore or verify else m['before_sha256'][str(p)]
    assert sha(current[p]) == wanted, ('Target changed; rebase before installing/restoring', p)
for name, digest in m['protected_sha256'].items():
    assert filehash(Path(name)) == digest, ('Unrelated resource changed; rebase required', name)
if verify:
    print(json.dumps({'installed_hashes_verified': True, 'protected_hashes_verified': True,
                      'files': len(targets), 'runtime_verified': False}))
    sys.exit(0)
if running(): raise SystemExit('Game is running; exit Football Manager before installing/restoring.')
written = {}
try:
    for p, source in targets.items():
        assert p.read_bytes() == current[p], ('Concurrent target change', p)
        data = Path(tx['before'][str(p)]).read_bytes() if restore else source.read_bytes()
        written[p] = data
        atomic(p, data)
        assert p.read_bytes() == data, ('Installed bytes differ', p)
    for name, digest in m['protected_sha256'].items():
        assert filehash(Path(name)) == digest, ('Concurrent unrelated resource change', name)
except BaseException:
    for p, raw in reversed(list(written.items())):
        if p.read_bytes() == raw: atomic(p, current[p])
    raise
now = datetime.datetime.now(zoneinfo.ZoneInfo('America/Denver')).isoformat()
m.update(installed=not restore, installed_verified=not restore, restored=restore, changed_at=now)
(out / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2), 'utf8')
root = Path(tx['workspace'])
state = {'status': 'restored' if restore else 'installed', 'installed': not restore,
         'runtime_verified': False, 'changed_at': now, 'record': str(out), 'palette': m['palette'],
         'scope': m['scope'], 'manifest': str(out / 'manifest.json'), 'restore': str(out / 'restore.ps1')}
if m.get('crash_fix'): state['crash_fix'] = m['crash_fix']
if restore and m.get('original_ui_surface_index', {}).get('light_trial'):
    state = m['original_ui_surface_index']['light_trial']
(root / 'current-light-ui-trial.json').write_text(json.dumps(state, ensure_ascii=False, indent=2), 'utf8')
surface = root / 'current-ui-surface-theme.json'
surface_state = json.loads(surface.read_text('utf8'))
if restore:
    old_trial = m.get('original_ui_surface_index', {}).get('light_trial')
    if old_trial: surface_state['light_trial'] = old_trial
    else: surface_state.pop('light_trial', None)
else: surface_state['light_trial'] = state
surface.write_text(json.dumps(surface_state, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'installed': not restore, 'restored': restore, 'verified_files': len(targets),
                  'output': str(out), 'runtime_verified': False}, ensure_ascii=False))
