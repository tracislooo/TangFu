import hashlib
import json
import subprocess
import sys
from pathlib import Path

out = Path(sys.argv[1]).resolve()
rollback = '--rollback' in sys.argv[2:]
manifest_path = out / 'manifest.json'
manifest = json.loads(manifest_path.read_text(encoding='utf-8'))
sha = lambda data: hashlib.sha256(data).hexdigest()
game = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
skin = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
catalog = game.parent / 'catalog.bin'
names = list(manifest['after_sha256'])
processes = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq fm.exe', '/FO', 'CSV', '/NH'], capture_output=True).stdout
assert b'"fm.exe"' not in processes.lower(), 'Exit Football Manager before replacing loaded bundles.'
targets = {}
for tag, folder in [('game', game), ('skin', skin)]:
    for name in names:
        target = folder / name
        expected = manifest['after_sha256'][name] if rollback else manifest['before_sha256'][str(target)]
        assert sha(target.read_bytes()) == expected, ('target version changed', str(target))
        data = (out / ('backup-' + tag) / name).read_bytes() if rollback else (out / name).read_bytes()
        assert sha(data) == (manifest['before_sha256'][str(target)] if rollback else manifest['after_sha256'][name])
        targets[target] = data
expected = manifest['after_catalog_sha256'] if rollback else manifest['before_catalog_sha256']
assert sha(catalog.read_bytes()) == expected, 'catalog version changed'
targets[catalog] = (out / ('backup-game/catalog.bin' if rollback else 'catalog.bin')).read_bytes()
for name, expected in manifest['protected_game_sha256'].items():
    assert sha((game / name).read_bytes()) == expected, ('protected file changed', name)
before = {target: target.read_bytes() for target in targets}
try:
    for target, data in targets.items():
        target.write_bytes(data)
        assert target.read_bytes() == data
except Exception:
    for target, data in before.items():
        target.write_bytes(data)
    raise
manifest['installed'] = not rollback
manifest['installation_verified'] = True
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'installed': not rollback, 'verified_files': len(targets), 'manifest': str(manifest_path)}, ensure_ascii=False))
