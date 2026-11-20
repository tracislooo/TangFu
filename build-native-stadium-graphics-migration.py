from datetime import datetime
from hashlib import md5, sha256
import json
from pathlib import Path
import re
import runpy
import struct
import sys

ROOT = Path(__file__).resolve().parent
read = lambda path: json.loads(path.read_text('utf-8'))
cfg = read(ROOT / 'current-game-location.json')
old = read(ROOT / 'current-club-stadium-comeback.json')
coverage = {row['key']: row for row in read(Path(old['patch']) / 'photo-mapping.json')}
analysis = ROOT / 'analysis/comeback-stadium-20261115'
clubs = {row['id'] for row in read(analysis / 'clubs-client.json')}
teams = read(analysis / 'teams-server.json')
team_data = (analysis / 'server-frame-28.bin').read_bytes()
stadium_data = (analysis / 'client-frame-22.bin').read_bytes()
stadium_count = struct.unpack_from('<I', stadium_data, 8)[0]
mapping = {}
for team in teams:
    if team['id'] not in clubs or team_data[team['start']] != 10:
        continue
    index = team['stadium_index']
    mapping[team['id']] = struct.unpack_from('<I', stadium_data, 43 + 38 * index)[0] if index < stadium_count else 0
assert all(mapping[row['club_id']] == row['stadium_id'] for row in coverage.values())
Catalog = runpy.run_path(str(ROOT / 'catalog-binary-v35.py'))['Catalog']
out = ROOT / ('club-stadium-native-graphics-' + datetime.now().strftime('%Y%m%d-%H%M%S'))
out.mkdir()
print(out, flush=True)
transactions, audits, protected = [], [], {}


def dump(name, data):
    (out / name).write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf-8')


def stage(tag, target, before, after):
    dest = out / tag / target.name
    backup = out / ('backup-' + tag) / target.name
    for path, payload in [(dest, after), (backup, before)]:
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(payload)
    transactions.append(dict(target=str(target), source=str(dest), backup=str(backup),
                             before=sha256(before).hexdigest(), after=sha256(after).hexdigest()))


for tag, folder, bundle_folder in [('game', Path(cfg['aa_root']), Path(cfg['bundle_root'])),
                                    ('skin', Path(cfg['skin_packages']), Path(cfg['skin_packages']))]:
    path = folder / 'catalog.bin'
    before = path.read_bytes()
    catalog = Catalog(before)
    retained, removed = [], set()
    for record in catalog.key_records:
        key = catalog.object(record[0])
        if isinstance(key, str) and re.fullmatch(r'kit2d_\d+_fmetstadium', key):
            assert key in coverage and key not in removed
            for location, in catalog.array(record[1], 'I'):
                info = catalog.location(location)
                assert info['provider'] == 'SI.Core.LocalAssetProvider' and info['type'][1] == 'UnityEngine.Texture2D'
                assert Path(info['internal']).name.casefold() == Path(coverage[key]['image']).name.casefold()
            removed.add(key)
        else:
            retained.append(record)
    assert removed == coverage.keys()
    offset = catalog.append(b''.join(struct.pack('<II', *row) for row in retained), True)
    struct.pack_into('<I', catalog.data, 8, offset)
    after = bytes(catalog.data)
    assert Catalog(after).key_records == retained
    assert before[:8] == after[:8] and before[12:] == after[12:len(before)]
    stage(tag, path, before, after)
    digest = path.with_suffix('.hash')
    stage(tag, digest, digest.read_bytes(), md5(after).hexdigest().encode('ascii'))
    for name in ('ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle', 'ui-visualfunctions_assets_all.bundle'):
        bundle = bundle_folder / name
        if bundle.is_file():
            protected[str(bundle)] = sha256(bundle.read_bytes()).hexdigest()
    audits.append(dict(target=tag, removed_absolute_photo_keys=len(removed), preserved_keys=len(retained)))

dump('tf-native-stadium-clubs.json', mapping)
dump('transaction.json', transactions)
dump('manifest.json', dict(installed=False, runtime_verified=False, protected_sha256=protected,
                           audits=audits, stadium_lookup='FM user graphics config: team ID / kits / fmetstadium',
                           database_clubs=len(mapping)))
for action, extra in [('install', ''), ('restore', ' --restore')]:
    script = f"$ErrorActionPreference='Stop'\n& '{sys.executable}' '{ROOT / 'install-independent-resource-patch.py'}' $PSScriptRoot{extra}\nif ($LASTEXITCODE -ne 0) {{throw 'Operation failed'}}\n"
    (out / (action + '.ps1')).write_text(script, 'utf-8-sig')
