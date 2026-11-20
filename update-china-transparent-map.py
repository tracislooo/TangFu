"""Rebase China's map and club marker positions onto the current installed resources."""
from pathlib import Path
import ast
import copy
import csv
import datetime
import hashlib
import importlib.util
import json
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

cfg = json.loads((R / 'current-game-location.json').read_text('utf8'))
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT = R / ('china-transparent-map-' + stamp)
OUT.mkdir()
(OUT / 'templates').mkdir()
(OUT / 'assets').mkdir()
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
sha = lambda data: hashlib.sha256(data).hexdigest()

def extract(filename, names):
    tree = ast.parse((R / filename).read_text('utf8'))
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'), globals())

oldwrite = TypeTreeHelper.write_value
extract('redesign-card-top-info-foot.py', {'write'})
TypeTreeHelper.write_value = write
extract('add-card-six-ratings.py', {'validate_ui'})
extract('build-match-ui-avatars-layout.py', {'refs', 'sd', 'find', 'pointer_remap', 'import_types', 'Doc'})
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)

registration = json.loads((R / 'analysis/china-transparent-registration.json').read_text('utf8'))
matrix = registration['matrix_old_to_new']
source_map = Path(registration['target'])
mapfile = OUT / 'assets/110.png'
mapfile.write_bytes(source_map.read_bytes())
assert sha(mapfile.read_bytes()) == sha(source_map.read_bytes())
old_data = json.loads((R / 'exports/China-top-two-leagues-2026/club-coordinates.json').read_text('utf8'))
rows = copy.deepcopy(old_data['clubs'])
database = json.loads((R / 'analysis/comeback-stadium-20261115/clubs-client.json').read_text('utf8'))
ningbo_source = 'https://www.cfl-china.cn/zh/content/announcements/rdfn.html'
for row in rows:
    x, y = row['x'], row['y']
    row['previous_x'], row['previous_y'] = x, y
    row['x'] = round(matrix[0][0] * x + matrix[0][1] * y + matrix[0][2], 3)
    row['y'] = round(matrix[1][0] * x + matrix[1][1] * y + matrix[1][2], 3)
    row['x_percent'] = row['x'] / 1920 * 100
    row['y_percent'] = row['y'] / 1080 * 100
    if row['club'] == 'Ningbo':
        record = next(c for c in database if c['id'] == 23366052)
        assert 'Shanghai Jiading Huilong' in record['names']
        row.update(uid=23366052, uid_status='renamed_club_identity_verified', database_names=record['names'], rename_source=ningbo_source)
        row.pop('uid_candidates', None)
    assert 0 <= row['x'] < 1920 and 0 <= row['y'] < 1080
assert len(rows) == len({r['uid'] for r in rows}) == 32
data = dict(old_data, image='assets/110.png', source_sha256=sha(mapfile.read_bytes()), nation_id=110, clubs=rows, registration=registration)
(OUT / 'club-coordinates.json').write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf8')
fields = ['league_zh', 'club_zh', 'uid', 'x', 'y', 'city_zh', 'stadium', 'lat', 'lon', 'needs_review']
with (OUT / 'club-coordinates.csv').open('w', encoding='utf-8-sig', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=fields, extrasaction='ignore')
    writer.writeheader()
    writer.writerows(rows)

# Reuse the single-marker preview, replacing its data and source asset reference.
preview = (R / 'exports/China-top-two-leagues-2026/single-club-preview.html').read_text('utf8')
start = preview.index('const clubs=') + len('const clubs=')
end = preview.index(';const select=', start)
preview = preview[:start] + json.dumps(rows, ensure_ascii=False) + preview[end:]
preview = preview.replace('src="map_China_ninedash.png"', 'src="assets/110.png"')
(OUT / 'single-club-preview.html').write_text(preview, 'utf8')

transactions = []
audits = []
protected = {str(mapfile): sha(mapfile.read_bytes())}

def stage(tag, target, before, after):
    staged = OUT / tag / target.name
    backup = OUT / ('backup-' + tag) / target.name
    for path, content in [(staged, after), (backup, before)]:
        path.parent.mkdir(exist_ok=True)
        path.write_bytes(content)
    transactions.append(dict(target=str(target), source=str(staged), backup=str(backup), before=sha(before), after=sha(after)))

def float32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]

for tag, folder in [('game', Path(cfg['bundle_root'])), ('skin', Path(cfg['skin_packages']))]:
    before = (folder / W).read_bytes()
    environment = UnityPy.load(before)
    env = {W: environment}
    objs = {W: {o.path_id: o for o in environment.objects}}
    hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    changes = {W: {}}
    documents = []
    document = Doc(W, pid=-991100000000030)
    original_refs = copy.deepcopy(document.r)
    existing_gates = {}
    for rid, ref in list(document.r.items()):
        if 'm_SerializedData' not in ref.get('data', {}):
            continue
        name = document.data(rid).get('name', '')
        if name.startswith('TFChinaClubLocationUID'):
            existing_gates[int(name.removeprefix('TFChinaClubLocationUID'))] = rid
    assert len(existing_gates) == 31
    donor = existing_gates[406]

    def clone_node(rid, parent, name):
        children = list(document.a(rid)['m_Children'])
        rule = document.a(rid)['m_RuleIndex']
        cloned = document.add(document, rid, parent, name)
        document.a(cloned)['m_RuleIndex'] = rule
        for child in children:
            child_name = document.data(child['rid']).get('name', '') + 'Ningbo'
            clone_node(child['rid'], cloned, child_name)
        return cloned

    new_gate = clone_node(donor, document.a(donor)['m_Parent']['rid'], 'TFChinaClubLocationUID23366052')
    argument_data = document.data(new_gate)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']
    raw = bytearray(argument_data)
    offset = 1
    for index in range(raw[0]):
        size = struct.unpack_from('<I', raw, offset)[0]
        offset += 4
        if index == 1:
            assert struct.unpack_from('<i', raw, offset + size - 4)[0] == 406
            struct.pack_into('<i', raw, offset + size - 4, 23366052)
        offset += size
    argument_data[:] = raw
    existing_gates[23366052] = new_gate
    modified_attributes = {document.a(donor)['m_Parent']['rid']}
    for row in rows:
        gate = existing_gates[row['uid']]
        anchor = document.a(gate)['m_Children'][1]['rid']
        document.st(anchor, [(131089, document.pct(float32(row['x_percent']))), (131104, document.pct(float32(row['y_percent'])))])
        modified_attributes.add(anchor)
        assert document.data(gate)['AlwaysInstantiate'] == 0
        assert document.data(gate)['Preview']['Mask'] == 1
    for rid, previous_ref in original_refs.items():
        if rid not in modified_attributes:
            assert document.r[rid] == previous_ref, (tag, rid, 'unrelated binding or node changed')
    document.save()
    bundle = environment.file.save(packer='lz4')
    reread = {obj.path_id: obj for obj in UnityPy.load(bundle).objects}
    assert set(reread) == set(objs[W])
    for pid, expected in hashes.items():
        if pid not in changes[W]:
            assert sha(reread[pid].get_raw_data()) == expected, (tag, pid)
    for pid, expected in changes[W].items():
        assert reread[pid].read_typetree() == expected

    catalog_path = (folder.parent if tag == 'game' else folder) / 'catalog.bin'
    old_catalog = catalog_path.read_bytes()
    catalog = cm.Catalog(old_catalog)
    image_guid = document.data(document.named('TFChinaMapBackground'))['StaticImage']['m_AssetGUID']
    locations = catalog.locations(image_guid)
    assert locations
    asset_path = mapfile.as_posix()
    path_offset = catalog.add_string(asset_path) if asset_path.isascii() else catalog.append(asset_path.encode('utf-16le'), True) | 0x80000000
    for location in locations:
        info = catalog.location(location)
        assert info['type'][1] == 'UnityEngine.Texture2D'
        assert info['provider'] == 'SI.Core.LocalAssetProvider'
        struct.pack_into('<I', catalog.data, location + 4, path_offset)
    final_catalog = bytes(catalog.data)
    check_catalog = cm.Catalog(final_catalog)
    assert dict(check_catalog.keys()) == dict(cm.Catalog(old_catalog).keys())
    for location in check_catalog.locations(image_guid):
        assert Path(check_catalog.location(location)['internal']) == mapfile
    stage(tag, folder / W, before, bundle)
    stage(tag, catalog_path, old_catalog, final_catalog)
    hash_path = catalog_path.with_suffix('.hash')
    stage(tag, hash_path, hash_path.read_bytes(), hashlib.md5(final_catalog).hexdigest().encode())
    for name in ['ui-backgrounds_assets_.bundle', 'ui-styles_assets_default.bundle', 'ui-tileslayouts_assets_all.bundle', 'ui-visualfunctions_assets_all.bundle']:
        path = folder / name
        if path.exists():
            protected[str(path)] = sha(path.read_bytes())
    audits.append(dict(target=tag, changed_objects=list(changes[W]), china_clubs=32, unrelated_nodes_and_bindings_preserved=True, unrelated_objects_byte_identical=True, map_guid=image_guid))

manifest = dict(installed=False, runtime_verified=False, map_asset=str(mapfile), map_source=str(source_map), coordinate_table=str(OUT / 'club-coordinates.json'), nation_id=110, coordinate_clubs=32, audits=audits, protected_sha256=protected, ningbo_rename_source=ningbo_source, accuracy='Previous stadium locations transformed by terrain registration; approximate geographic positioning retained.')
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transactions, ensure_ascii=False, indent=2), 'utf8')
for action, flags in [('install', ''), ('restore', ' --restore')]:
    command = "$ErrorActionPreference='Stop'\n& '" + sys.executable + "' '" + str(R / 'install-independent-resource-patch.py') + "' $PSScriptRoot" + flags + "\nif($LASTEXITCODE -ne 0){throw 'Operation failed'}\n"
    (OUT / (action + '.ps1')).write_text(command, 'utf-8-sig')
(OUT / 'previous-state.json').write_bytes((R / 'current-club-location-map.json').read_bytes())
print(str(OUT), flush=True)
