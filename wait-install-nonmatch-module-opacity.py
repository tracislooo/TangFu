"""Wait for a normal game exit, then run the guarded installation once."""
from pathlib import Path
import datetime, json, os, subprocess, sys, time

R = Path(__file__).resolve().parent
out = Path(sys.argv[1]).resolve()
assert out.parent == R and out.name.startswith('nonmatch-module-opacity30-')
status = out / 'automatic-install-status.json'
log = out / 'automatic-install.log'
flags = getattr(subprocess, 'CREATE_NO_WINDOW', 0)
def state(value, **extra):
    record = {'status':value, 'pid':os.getpid(), 'updated_at_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(), 'patch':str(out), **extra}
    tmp = status.with_suffix('.tmp'); tmp.write_text(json.dumps(record, ensure_ascii=False, indent=2), 'utf8'); os.replace(tmp, status)
def running():
    p = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True, creationflags=flags)
    if p.returncode not in [0, 1]: raise RuntimeError('Cannot determine game process state: ' + p.stderr)
    return bool(p.stdout.strip())
try:
    assert json.loads((out / 'verification.json').read_text('utf8'))['passed']
    state('waiting_for_game_exit')
    while running(): time.sleep(5)
    state('installing')
    with log.open('w', encoding='utf8') as stream:
        command = [sys.executable, str(R / 'install-native-background-overrides.py'), str(out)]
        p = subprocess.run(command, stdout=stream, stderr=subprocess.STDOUT, creationflags=flags)
        if p.returncode: raise RuntimeError('Guarded installation failed; see automatic-install.log')
        p = subprocess.run(command + ['--verify'], stdout=stream, stderr=subprocess.STDOUT, creationflags=flags)
        if p.returncode: raise RuntimeError('Post-install hash verification failed; see automatic-install.log')
    state('installed_and_hash_verified', runtime_verified=False)
except BaseException as exc:
    state('failed', error=str(exc))
    raise
