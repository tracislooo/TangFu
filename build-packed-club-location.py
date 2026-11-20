from pathlib import Path
import ast
import copy
import csv
import datetime
import hashlib
import json
import math
import runpy
import struct
import sys
import uuid
import zlib

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
import openpyxl
from PIL import Image
import cv2
import numpy as np
from UnityPy.export.Texture2DConverter import image_to_texture2d
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader

DATA = Path('K:/桌面/27skin/PICTURE/country-new')
WORLD_VTA = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BACKGROUNDS = 'ui-backgrounds_assets_common.bundle'
STADIUM = -991100000000030
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
sha = lambda data: hashlib.sha256(data).hexdigest()
read_json = lambda path: json.loads(path.read_text('utf8'))
float32 = lambda value: struct.unpack('<f', struct.pack('<f', value))[0]

def dump(path, data):
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2), 'utf8')

def extract(filename, names):
    tree = ast.parse((ROOT / filename).read_text('utf8'))
    selected = [node for node in tree.body if isinstance(node, (ast.ClassDef, ast.FunctionDef)) and node.name in names]
    exec(compile(ast.Module(body=selected, type_ignores=[]), filename, 'exec'), globals())

def read_coordinates(calibration):
    book = openpyxl.load_workbook(DATA / 'country-new-ID对应表.xlsx', data_only=True, read_only=True)
    names = {old.removeprefix('map_').removesuffix('_transparent.png'): str(uid) for _, old, _, _, _, uid, *_ in list(book.worksheets[0].values)[1:] if uid}
    book.close()
    names.update(China_ninedash='110', UK='219003', Spain='796')
    book = openpyxl.load_workbook(DATA / 'ALL_clubs_coordinates_latest_球队ID.xlsx', data_only=True, read_only=True)
    workbook_maps = {row[0]: Path(row[8]).stem.removeprefix('map_') for row in list(book.worksheets[1].values)[1:] if row[8]}
    rows = [(workbook_maps[row[0]], row[5], row[17], *row[9:13]) for row in list(book.worksheets[0].values)[1:] if row[0]]
    book.close()
    with (DATA / 'club-coordinates.csv').open(encoding='utf-8-sig', newline='') as file:
        for row in csv.DictReader(file):
            rows.append(('China_ninedash', row['club_zh'], row['uid'], *(row[key] for key in ('x', 'y', 'lat', 'lon'))))
    groups = {name: {} for name in calibration}
    excluded, seen = [], set()
    ox, oy, sx, sy = calibration['world']['transform']
    assert calibration['world']['projection'] == 'mercator' and calibration['world']['mean_clipped_coast_error'] < 3
    for source, club, uid, x, y, lat, lon in rows:
        uid = int(uid) if uid else None
        assert uid is None or (0 < uid <= 0x7fffffff and uid not in seen), (uid, club)
        if uid is not None:
            seen.add(uid)
        key = names.get(source, 'world')
        coords = (lat, lon) if key == 'world' else (x, y)
        if uid is None or any(value in (None, '') for value in coords):
            excluded.append(dict(club=club, uid=uid, map=key, reason='no usable coordinates on selected map' if uid else 'no club UID'))
            continue
        if key == 'world':
            assert -85 < float(lat) < 85 and -180 <= float(lon) <= 180
            px = ox + sx * float(lon)
            py = oy - sy * math.degrees(math.asinh(math.tan(math.radians(float(lat)))))
        elif key in {'110', '796'}:
            px, py = float(x), float(y)
        else:
            fit = calibration[key]
            assert fit['inliers'] >= 50 and fit['p95_error'] < 2
            px, py = [row[0] * float(x) + row[1] * float(y) + row[2] for row in fit['matrix']]
        assert 0 <= px < 1920 and 0 <= py < 1080, (source, club, px, py)
        groups[key][uid] = dict(club=club, x=px, y=py)
    assert sum(map(len, groups.values())) + len(excluded) == len(rows)
    return groups, excluded

def stage(tag, path, before, after):
    dest = OUT / tag / path.name
    backup = OUT / ('backup-' + tag) / path.name
    for filename, data in [(dest, after), (backup, before)]:
        filename.parent.mkdir(exist_ok=True)
        filename.write_bytes(data)
    transactions.append(dict(target=str(path), source=str(dest), backup=str(backup), before=sha(before), after=sha(after)))

def update_catalog(before, function_guid, catalog_type, maps):
    catalog = catalog_type(before)
    keys = dict(catalog.keys())
    donor = None
    for key, offsets in keys.items():
        if not isinstance(key, str) or len(key) != 32:
            continue
        locations = catalog.array(offsets, 'I')
        if locations:
            loc = catalog.location(locations[0][0])
            if loc['type'][1] == 'UnityEngine.Texture2D' and loc['dependencies'] and BACKGROUNDS in catalog.location(loc['dependencies'][0])['internal']:
                donor = loc
                break
    assert donor is not None and 'BundledAssetProvider' in donor['provider']
    records = list(catalog.key_records)
    string_type = next(catalog.unpack(key, '2I')[0] for key, _ in records if isinstance(catalog.object(key), str))
    for name, asset in maps.items():
        if asset['guid'] in keys:
            continue
        guid = catalog.add_string(asset['guid'])
        info = list(donor['raw'])
        info[:2] = [guid, catalog.add_string(name)]
        loc = catalog.append(struct.pack('<7I', *info))
        key = catalog.append(struct.pack('<IHH', guid, 0, 0))
        records.append((catalog.append(struct.pack('<2I', string_type, key)), catalog.append(struct.pack('<I', loc), True)))
    struct.pack_into('<I', catalog.data, 8, catalog.append(b''.join(struct.pack('<2I', *row) for row in records), True))
    meta = next(obj.read_typetree() for obj in objs[WORLD_VTA].values() if obj.type.name == 'AssetBundle')
    stadium_key = next(key for key, value in meta['m_Container'] if value['asset'] == {'m_FileID': 0, 'm_PathID': STADIUM})
    preload = [catalog.location(loc)['internal'] for loc, in catalog.array(keys['GameWorldVisualTreeAssetPreload'], 'I')]
    assert stadium_key in preload
    function = catalog.location(catalog.locations(function_guid)[0])
    assert function['type'][1] == 'SI.VisualScripting.VisualFunction'
    for location in catalog.locations(stadium_key):
        dependencies = catalog.location(location)['dependencies']
        assert WORLD_VTA in catalog.location(dependencies[0])['internal']
        for dependency in function['dependencies'] + donor['dependencies']:
            if dependency not in dependencies:
                dependencies.append(dependency)
        raw = struct.pack(f'<{len(dependencies)}I', *dependencies)
        struct.pack_into('<II', catalog.data, location + 12, catalog.append(raw, True), zlib.crc32(raw))
    result = bytes(catalog.data)
    catalog = catalog_type(result)
    for name, asset in maps.items():
        loc = catalog.location(catalog.locations(asset['guid'])[0])
        assert loc['internal'] == name and loc['type'][1] == 'UnityEngine.Texture2D' and loc['provider'] == donor['provider']
        assert BACKGROUNDS in catalog.location(loc['dependencies'][0])['internal']
    assert dict(catalog.keys()).items() >= keys.items()
    return result

def add_spain(before, source):
    env = UnityPy.load(before)
    assets = env.assets[0]
    objs = assets.objects
    hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs.items()}
    registry = read_json(ROOT / 'current-custom-textures.json')
    reserved = read_json(ROOT / 'reserved-texture-ids.json')['reserved_textures']
    pid = -910000000000186
    assert pid in objs and objs[pid].peek_name() == '796'
    assert all(int(item['path_id']) != pid and item['name'] != '796' for item in reserved)
    assert any(int(item['path_id']) == pid and item['name'] == '796' for item in registry['textures'])
    meta = next(obj for obj in objs.values() if obj.type.name == 'AssetBundle')
    tree = meta.read_typetree()
    ptr = dict(m_FileID=0, m_PathID=pid)
    assert dict(tree['m_Container'])['796']['asset'] == ptr and ptr in tree['m_PreloadTable']
    old = objs[pid]
    image = Image.open(source).convert('RGBA')
    clone = copy.copy(old)
    clone.path_id, clone.data, clone._read_until = pid, None, None
    objs[pid] = clone
    texture = old.read_typetree()
    pixels, fmt = image_to_texture2d(image, 4, clone.platform, texture['m_PlatformBlob'])
    assert image.size == (1920, 1080) and int(fmt) == 4
    texture.update(m_Name='796', m_Width=1920, m_Height=1080, m_TextureFormat=4, m_MipCount=1, m_CompleteImageSize=len(pixels))
    texture['image data'] = pixels
    texture['m_StreamData'] = dict(offset=0, size=0, path='')
    clone.save_typetree(texture)
    result = env.file.save(packer='lz4')
    check = UnityPy.load(result).assets[0].objects
    assert set(check) == set(hashes)
    assert all(sha(check[key].get_raw_data()) == value for key, value in hashes.items() if key != pid)
    assert check[meta.path_id].read_typetree() == tree and check[pid].read().image.convert('RGBA').tobytes() == image.tobytes()
    record = dict(name='796', path_id=str(pid), size=list(image.size), texture_format_id=4,
                  archived_source=str(source), texture_sha256=sha(check[pid].get_raw_data()),
                  decoded_pixel_sha256=sha(image.tobytes()), decoded_alpha_range=list(image.getchannel('A').getextrema()))
    return result, record

def prepare_spain(destination):
    for name in ('796.png', 'map_Spain_transparent.png'):
        source = DATA / name
        if source.is_file():
            image = Image.open(source).convert('RGBA')
            assert image.size == (1920, 1080) and image.getchannel('A').getextrema() == (0, 255)
            image.save(destination)
            return str(source), False
    source = DATA.parent / 'country/map_Spain.png'
    rgb = np.asarray(Image.open(source).convert('RGB'))
    hsv = cv2.cvtColor(rgb, cv2.COLOR_RGB2HSV)
    red, green, blue = np.moveaxis(rgb.astype(np.int16), -1, 0)
    warm = ((hsv[:, :, 0] >= 4) & (hsv[:, :, 0] <= 42) & (hsv[:, :, 1] >= 48)
            & (red >= 35) & (red - blue >= 17) & (red - green >= 6))
    mask = cv2.morphologyEx(warm.astype('uint8'), cv2.MORPH_CLOSE, np.ones((5, 5), 'uint8'))
    count, labels, bounds, _ = cv2.connectedComponentsWithStats(mask)
    keep = [label for label in range(1, count) if bounds[label, cv2.CC_STAT_AREA] >= 10]
    contours, _ = cv2.findContours(np.isin(labels, keep).astype('uint8'), cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    alpha = np.zeros(mask.shape, 'uint8')
    cv2.drawContours(alpha, contours, -1, 255, cv2.FILLED)
    alpha = cv2.GaussianBlur(alpha, (3, 3), .6)
    assert .05 < np.mean(alpha > 127) < .5
    Image.fromarray(np.dstack((rgb, alpha))).save(destination)
    return str(source), True

def sync_catalog_crc(catalog_type, data, bundles, require_options):
    catalog = catalog_type(data)
    checks = {}
    for name, payload in bundles.items():
        reader = EndianBinaryReader(payload)
        bundle = object.__new__(BundleFile)
        bundle.signature = reader.read_string_to_null()
        bundle.version = reader.read_u_int()
        bundle.version_player = reader.read_string_to_null()
        bundle.version_engine = reader.read_string_to_null()
        _, block = bundle.read_fs(reader)
        checks[name] = (zlib.crc32(block.bytes), len(payload))
    found, without_options = set(), set()
    for offset in {loc for _, offsets in catalog.keys() for loc, in catalog.array(offsets, 'I')}:
        loc = catalog.location(offset)
        name = Path(loc['internal'].replace('\\', '/')).name
        if name not in checks or not loc['type'][1].endswith('IAssetBundleResource'):
            continue
        extra = loc['raw'][5]
        if extra == 0xffffffff:
            without_options.add(name)
            continue
        typ, payload = catalog.unpack(extra, '2I')
        assert catalog.typename(typ)[1].endswith('AssetBundleRequestOptions')
        values = list(catalog.unpack(payload, '5I'))
        values[2:4] = checks[name]
        payload = catalog.append(struct.pack('<5I', *values))
        struct.pack_into('<I', catalog.data, offset + 20, catalog.append(struct.pack('<2I', typ, payload)))
        found.add(name)
    assert (found if require_options else found | without_options) == set(checks)
    return bytes(catalog.data), {name: checks[name] for name in found}

def packed_maps(payload, records):
    objects = {obj.path_id: obj for obj in UnityPy.load(payload).objects}
    meta = next(obj.read_typetree() for obj in objects.values() if obj.type.name == 'AssetBundle')
    container = dict(meta['m_Container'])
    assets = {}
    for record in records:
        name, pid = record['name'], int(record['path_id'])
        item = container[name]
        ptr = {'m_FileID': 0, 'm_PathID': pid}
        assert item['asset'] == ptr and ptr in meta['m_PreloadTable'][item['preloadIndex']:item['preloadIndex']+item['preloadSize']]
        texture = objects[pid]
        assert texture.peek_name() == name and sha(texture.get_raw_data()) == record['texture_sha256']
        with Image.open(record['archived_source']) as image:
            assert image.size == (1920, 1080)
            assert sha(image.convert('RGBA').tobytes()) == record['decoded_pixel_sha256']
            right = image.convert('RGBA').getchannel('A').point(lambda alpha: 255 if alpha > 127 else 0).getbbox()[2]
        scale = 1 if name == '796' else min(1, 1040 / right)
        assets[name] = dict(path_id=pid, guid=uuid.uuid5(uuid.NAMESPACE_URL, f'tf27/club-location/packed-map/{name}').hex,
                            scale=scale, top=(1-scale) / 2)
    return assets

def update_layout(groups, assets):
    doc = Doc(WORLD_VTA, pid=STADIUM)
    fit = doc.named('TFUKMapWidthAspect')
    image = doc.named('TFPackedMap110')
    gate = doc.named('TFMapClubUID406')
    empty, anchor = (child['rid'] for child in doc.a(gate)['m_Children'])
    ring = doc.a(anchor)['m_Children'][0]['rid']
    hole = doc.a(ring)['m_Children'][0]['rid']
    dot = doc.a(hole)['m_Children'][0]['rid']
    function = doc.data(gate)['Binding']['m_visualFunction']['m_target']['m_guid']
    old_subtree = set()

    def collect(rid):
        old_subtree.update((rid, doc.a(rid)['m_SerializedData']['rid']))
        for child in doc.a(rid)['m_Children']:
            collect(child['rid'])

    for child in doc.a(fit)['m_Children']:
        collect(child['rid'])
    surface = doc.a(fit)['m_Parent']['rid']
    retained = {rid: copy.deepcopy(ref) for rid, ref in doc.r.items() if rid not in old_subtree and rid not in {fit, surface}}

    def clone(rid, parent, name):
        new = doc.add(doc, rid, parent, name)
        doc.a(new)['m_RuleIndex'] = doc.a(rid)['m_RuleIndex']
        return new

    def switch(parent, kind, value, path):
        new = clone(gate, parent, f'TFMap{kind}{value}')
        data = doc.data(new)
        data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = arguments(value, path)
        assert data['AlwaysInstantiate'] == 0 and data['Preview'] == {'Mask': 1}
        return new

    def circle(rid, parent, name, size, offset, colour):
        new = clone(rid, parent, name)
        doc.size(new, size, size)
        doc.st(new, [(131089, doc.px(offset)), (131104, doc.px(offset)),
                     (458752, doc.val(4, dict(zip(('r', 'g', 'b', 'a'), map(float32, colour)))))])
        return new

    def show(parent, name):
        asset = assets[name]
        scale, top = asset['scale'], asset['top']
        background = clone(image, parent, f'TFPackedMap{name}')
        doc.data(background)['StaticImage']['m_AssetGUID'] = asset['guid']
        doc.st(background, [(131104, doc.pct(float32(top * 100))), (131105, doc.pct(float32(scale * 100))), (131087, doc.pct(float32(scale * 100)))])
        for uid, row in groups[name].items():
            cond = switch(parent, 'ClubUID', uid, 'club.UniqueId')
            off = clone(empty, cond, 'TFMapNoMarker')
            pin = clone(anchor, cond, 'TFMapMarkerAnchor')
            doc.st(pin, [(131089, doc.pct(float32(scale * row['x'] / 19.2))), (131104, doc.pct(float32(top * 100 + scale * row['y'] / 10.8)))])
            outer = circle(ring, pin, 'TFMapMarkerOutline', 26, -13, (.025, .04, .06, 1))
            accent = circle(ring, outer, 'TFMapMarkerCyan', 20, 3, (0, .93, 1, 1))
            inner = circle(hole, accent, 'TFMapMarkerInner', 12, 4, (.025, .04, .06, 1))
            circle(dot, inner, 'TFMapMarkerCenter', 8, 2, (1, 1, 1, 1))
            assert doc.a(cond)['m_Children'] == [{'rid': off}, {'rid': pin}]

    def full_branch(parent, name):
        branch = clone(anchor, parent, name)
        doc.st(branch, [(131089, doc.pct(0)), (131104, doc.pct(0)), (131105, doc.pct(100)), (131087, doc.pct(100))])
        return branch

    doc.a(fit)['m_Children'] = []
    mapping = {int(name): name for name in assets if name != 'world'}
    mapping.update({765: '219003', 801: '219003', 785: '219003', 793: '219003'})
    parent = fit
    for nation in sorted(mapping):
        cond = switch(parent, 'WorldUnlessNation', nation, 'club.nation.UniqueId')
        parent = full_branch(cond, 'TFMapWorldContinue')
        clone(empty, cond, 'TFMapWorldBlocked')
        doc.data(cond)['AlwaysInstantiate'] = 1
    show(parent, 'world')
    for nation, name in sorted(mapping.items()):
        cond = switch(fit, 'Nation', nation, 'club.nation.UniqueId')
        fallback = clone(empty, cond, 'TFMapNoCountry')
        match = full_branch(cond, 'TFMapMatchedNation')
        show(match, name)
        assert doc.a(cond)['m_Children'] == [{'rid': fallback}, {'rid': match}]
    doc.d['references']['RefIds'] = [ref for ref in doc.d['references']['RefIds'] if ref['rid'] not in old_subtree]
    doc.st(surface, [(458752, doc.val(4, dict(r=0., g=0., b=0., a=0.)))])
    assert all(doc.r[rid] == ref for rid, ref in retained.items())
    doc.save()
    return dict(function=function, preserved_original_references=len(retained), nation_to_map=mapping)

if __name__ == '__main__':
    cfg = read_json(ROOT / 'current-game-location.json')
    source = read_json(ROOT / 'country-new-images-20261117/manifest.json')
    assert source['installed']
    calibration = read_json(Path(sys.argv[1]))
    records = source['textures']
    assert set(calibration) == {item['name'] for item in records}
    calibration['796'] = {}
    groups, excluded = read_coordinates(calibration)
    stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
    OUT = ROOT / ('club-country-maps-' + stamp)
    (OUT / 'templates').mkdir(parents=True)
    spain_source = OUT / '796.png'
    spain_original, spain_alpha_derived = prepare_spain(spain_source)
    protected = {}
    print('PATCH=' + str(OUT), flush=True)
    oldwrite = TypeTreeHelper.write_value
    extract('redesign-card-top-info-foot.py', {'write'})
    TypeTreeHelper.write_value = write
    extract('add-card-six-ratings.py', {'validate_ui'})
    extract('build-match-ui-avatars-layout.py', {'refs', 'sd', 'find', 'pointer_remap', 'import_types', 'Doc'})
    extract('build-china-club-location.py', {'arguments'})
    catalog_type = runpy.run_path(str(ROOT / 'catalog-binary-v35.py'))['Catalog']
    transactions, protected, audits = [], {}, []
    for tag, folder in [('game', Path(cfg['bundle_root'])), ('skin', Path(cfg['skin_packages']))]:
        backgrounds_path = folder / BACKGROUNDS
        backgrounds_before = backgrounds_path.read_bytes()
        backgrounds_after, spain_record = add_spain(backgrounds_before, spain_source)
        assets = packed_maps(backgrounds_after, records + [spain_record])
        stage(tag, backgrounds_path, backgrounds_before, backgrounds_after)
        path = folder / WORLD_VTA
        before = path.read_bytes()
        environment = UnityPy.load(before)
        env, objs, changes, documents = {WORLD_VTA: environment}, {WORLD_VTA: {obj.path_id: obj for obj in environment.objects}}, {WORLD_VTA: {}}, []
        baseline = {pid: sha(obj.get_raw_data()) for pid, obj in objs[WORLD_VTA].items()}
        audit = update_layout(groups, assets)
        after = environment.file.save(packer='lz4')
        reread = {obj.path_id: obj for obj in UnityPy.load(after).objects}
        assert set(reread) == set(baseline) and len(changes[WORLD_VTA]) == 2
        for pid, obj in reread.items():
            if pid in changes[WORLD_VTA]:
                assert obj.read_typetree() == changes[WORLD_VTA][pid], (tag, pid, obj.peek_name())
            else:
                assert sha(obj.get_raw_data()) == baseline[pid], (tag, pid)
        stage(tag, path, before, after)
        cp = (folder.parent if tag == 'game' else folder) / 'catalog.bin'
        cb = cp.read_bytes()
        catalog = update_catalog(cb, audit['function'], catalog_type, assets)
        catalog, crc = sync_catalog_crc(catalog_type, catalog, {WORLD_VTA: after, BACKGROUNDS: backgrounds_after}, tag == 'game')
        stage(tag, cp, cb, catalog)
        hp = cp.with_suffix('.hash')
        stage(tag, hp, hp.read_bytes(), hashlib.md5(catalog).hexdigest().encode())
        audits.append(dict(target=tag, **audit, changed_objects=list(changes[WORLD_VTA]), maps=assets, unchanged_objects=len(reread)-2, bundle_crc_size=crc))
        print(tag, 'verified', flush=True)
    registry_path = ROOT / 'current-custom-textures.json'
    registry = read_json(registry_path)
    slot = next(index for index, item in enumerate(registry['textures']) if item['name'] == '796')
    registry['textures'][slot] = spain_record
    registry['active_custom_texture_count'] = len(registry['textures'])
    registry.update(authoritative_source_bundle=str(OUT / 'game' / BACKGROUNDS),
                    source_bundle_sha256=next(row['after'] for row in transactions if Path(row['source']) == OUT / 'game' / BACKGROUNDS),
                    manifest=str(OUT / 'manifest.json'))
    stage('registry', registry_path, registry_path.read_bytes(), json.dumps(registry, ensure_ascii=False, indent=2).encode('utf8'))
    dump(OUT / 'transaction.json', transactions)
    dump(OUT / 'coordinates.json', dict(groups=groups, excluded=excluded))
    dump(OUT / 'manifest.json', dict(installed=False, runtime_verified=False, protected_sha256=protected, audits=audits,
                                     marker_count=sum(map(len, groups.values())), country_maps=len(assets)-1, excluded=excluded,
                                     calibration=str(Path(sys.argv[1]).resolve()), texture_registry_transaction=True,
                                     spain_original=spain_original, spain_alpha_derived=spain_alpha_derived))
    for action, extra in [('install', ''), ('restore', ' --restore')]:
        script = f"$ErrorActionPreference='Stop'\n& '{sys.executable}' '{ROOT / 'install-independent-resource-patch.py'}' $PSScriptRoot{extra}\nif ($LASTEXITCODE -ne 0) {{throw 'Operation failed'}}\n"
        (OUT / (action + '.ps1')).write_text(script, 'utf-8-sig')

