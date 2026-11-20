"""Install a verified main-version build into the game, with guarded rollback."""
import hashlib
import json
from pathlib import Path
import subprocess
import sys


def digest(data):
    return hashlib.sha256(data).hexdigest()


out = Path(sys.argv[1]).resolve(strict=True)
manifest_path = out / 'manifest.json'
manifest = json.loads(manifest_path.read_text('utf-8'))
verification = json.loads((out / 'verification.json').read_text('utf-8'))
assert verification['custom_catalog_types_and_bundle_dependencies_verified']
assert (out / 'contract-override-verification.json').is_file()
assert (out / 'scope-1-16-verification.json').is_file()
assert not manifest['installed']

location = json.loads(Path('current-game-location.json').read_text('utf-8'))
aa = Path(location['aa_root']).resolve(strict=True)
bundles = Path(location['bundle_root']).resolve(strict=True)
assert bundles.parent == aa and 'Football Manager 27' in aa.parts
sidebar = json.loads(Path('current-sidebar-version.json').read_text('utf-8'))
assert sidebar['current_game_mode'] == 'non-sidebar'
pending = {}
for name, expected in manifest['after_sha256'].items():
    assert Path(name).name == name and name.endswith('.bundle')
    data = (out / name).read_bytes()
    assert digest(data) == expected
    pending[bundles / name] = (data, manifest['new_game_before_sha256'][name])

catalog = (out / 'catalog.bin').read_bytes()
catalog_hash = (out / 'catalog.hash').read_bytes()
assert digest(catalog) == manifest['catalog_after_sha256']
assert catalog_hash.decode('ascii').strip() == hashlib.md5(catalog).hexdigest()
pending[aa / 'catalog.bin'] = (catalog, manifest['catalog_before_sha256'])
pending[aa / 'catalog.hash'] = (catalog_hash, digest((out / 'backup-game/catalog.hash').read_bytes()))

process = subprocess.run(
    ['powershell', '-NoProfile', '-Command',
     'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],
    capture_output=True, text=True,
)
assert not process.stdout.strip(), 'Football Manager is still running'

changes = {}
for target, (data, before) in pending.items():
    original = target.read_bytes()
    assert digest(original) == before, f'File changed during preparation: {target}'
    assert (out / 'backup-game' / target.name).read_bytes() == original
    if data != original:
        changes[target] = (data, original)


def quote(path):
    return "'" + str(path).replace("'", "''") + "'"


restore = ['$ErrorActionPreference = "Stop"']
for target, (data, _) in changes.items():
    restore.append(
        f"if ((Get-FileHash -LiteralPath {quote(target)} -Algorithm SHA256).Hash "
        f"-ne '{digest(data)}') {{ throw 'Current file differs from installed build: {target.name}' }}"
    )
for target in changes:
    restore.append(f"Copy-Item -LiteralPath {quote(out / 'backup-game' / target.name)} "
                   f"-Destination {quote(target)} -Force")
(out / 'restore.ps1').write_text('\n'.join(restore) + '\n', 'utf-8-sig')

written = []
try:
    for target, (data, original) in changes.items():
        assert target.read_bytes() == original, f'Concurrent change: {target}'
        written.append(target)
        target.write_bytes(data)
        assert digest(target.read_bytes()) == digest(data), target
except BaseException:
    for target in reversed(written):
        target.write_bytes(changes[target][1])
    raise

manifest['installed'] = True
manifest['installed_paths'] = [str(target) for target in written]
manifest['scope'] = 'Pinned 1–16, main variant'
manifest_path.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf-8')
print(json.dumps({'installed': True, 'files_written': len(written), 'output': str(out)}))
