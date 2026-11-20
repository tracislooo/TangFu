"""Install/restore prepared native bookmark resources and exactly one PlayerPrefs value."""
from pathlib import Path
import hashlib
import json
import os
import subprocess
import sys
import uuid
import winreg

out = Path(next(x for x in sys.argv[1:] if not x.startswith('--'))).resolve()
restore = '--restore' in sys.argv
manifest = json.loads((out / 'manifest.json').read_text('utf8'))
tx = json.loads((out / 'transaction.json').read_text('utf8'))
sha = lambda b: hashlib.sha256(b).hexdigest()
KEY = r'Software\Sports Interactive\Football Manager 27'
NAME = 'SelectedBookmarksKey_h3185478356'
prefs = json.loads((out / 'bookmark-preference.json').read_text('utf8'))
assert prefs['key'] == KEY and prefs['name'] == NAME

def closed():
    p = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
    assert not p.stdout.strip(), 'Save and exit Football Manager normally before installation/restoration.'

def get_pref():
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY) as key:
        value, kind = winreg.QueryValueEx(key, NAME)
        assert kind == winreg.REG_BINARY
        return value

def put_pref(value):
    with winreg.OpenKey(winreg.HKEY_CURRENT_USER, KEY, 0, winreg.KEY_SET_VALUE) as key:
        winreg.SetValueEx(key, NAME, 0, winreg.REG_BINARY, value)
        winreg.FlushKey(key)

def atomic(path, data):
    temp = path.with_name(path.name + '.codex-bookmark-' + uuid.uuid4().hex + '.tmp')
    try:
        temp.write_bytes(data)
        os.replace(temp, path)
    finally:
        if temp.exists():
            temp.unlink()

closed()
previous_pref = get_pref()
expected_pref = bytes.fromhex(prefs['after_hex' if restore else 'before_hex'])
wanted_pref = bytes.fromhex(prefs['before_hex' if restore else 'after_hex'])
assert previous_pref == expected_pref or (not restore and previous_pref == wanted_pref), 'Bookmark preference changed after preparation.'
previous, wanted = {}, {}
allowed = {
    Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64').resolve(),
    Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa').resolve(),
}
for entry in tx:
    path = Path(entry['target'])
    assert path.resolve().parent in allowed
    data = Path(entry['backup' if restore else 'source']).read_bytes()
    assert sha(data) == entry['before' if restore else 'after']
    current = path.read_bytes()
    assert sha(current) == entry['after' if restore else 'before'] or (not restore and sha(current) == entry['after']), ('Target changed', path)
    previous[path], wanted[path] = current, data
for path, value in manifest['protected_sha256'].items():
    assert sha(Path(path).read_bytes()) == value, ('Protected file changed', path)
closed()
assert get_pref() == previous_pref
assert all(path.read_bytes() == data for path, data in previous.items())
try:
    for path, data in wanted.items():
        atomic(path, data)
        assert path.read_bytes() == data
    put_pref(wanted_pref)
    assert get_pref() == wanted_pref
    for path, value in manifest['protected_sha256'].items():
        assert sha(Path(path).read_bytes()) == value
except BaseException:
    for path, data in previous.items():
        atomic(path, data)
    put_pref(previous_pref)
    raise
manifest.update(installed=not restore, restored=restore, installed_hash_verified=not restore,
                selected_bookmark_preference_verified=True)
(out / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'installed': not restore, 'restored': restore, 'resource_files': len(wanted),
                  'selected_bookmark_count': len(wanted_pref.rstrip(b'\0').decode('ascii').strip(',').split(',')),
                  'runtime_verified': False, 'output': str(out)}, ensure_ascii=False))
