"""Add a live, horizontally scrolling roster above the desktop club squad table."""
from pathlib import Path
import datetime
import importlib.util
import json
import zoneinfo

R = Path(__file__).resolve().parent
locations = json.loads((R / 'current-game-location.json').read_text('utf8'))
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = W.replace('gameworld', 'global')
HOST = 6486912801097318829
HOST_GUID = '3c6b24be8ba166141859febbd8e11c20'
PICTURE_GUID = '2bfe44c46f2e547aa395f3dea8b7087d'
ROW = -981106000043010
ROW_STYLE = ROW - 1
ROW_GUID = '0b79ae3b71e45568a4c2ea9bf1d1ecf3'
ROW_NAME = 'TFClubSquadOverviewRosterPlayer'
ROW_WIDTH = 112

# Load the project's bundle codecs and UI editing primitives without its match patch.
helper = (R / 'build-match-ui-avatars-layout.py').read_text('utf8')
exec(compile(helper[helper.index('import sys,copy'):helper.index('GAME=')], '<imports>', 'exec'))
exec(compile(helper[helper.index('oldwrite='):helper.index('portrait=Doc(W,pid=')], '<ui-tools>', 'exec'))
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
catalog = importlib.util.module_from_spec(spec)
spec.loader.exec_module(catalog)

OUT = R / ('squad-overview-player-strip-' + datetime.datetime.now(
    zoneinfo.ZoneInfo('America/Denver')).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
(OUT / 'templates').mkdir()
sha = lambda raw: hashlib.sha256(raw).hexdigest()


def pointer(pid):
    return {'m_FileID': 0, 'm_PathID': pid}


def add_object(source, pid, tree):
    assert pid not in objs[W]
    obj = copy.copy(source)
    obj.path_id = pid
    obj.data = None
    obj._read_until = None
    obj.assets_file.objects[pid] = obj
    objs[W][pid] = obj
    obj.save_typetree(tree)


def make_row():
    position = Doc(W, name='PlayerPositionCombinedStringCell')
    portrait = Doc(W, name='PlayerPortraitCell')
    names = Doc(W, name='PlayerNameCell')
    tree = copy.deepcopy(position.d)
    sheet = copy.deepcopy(position.s)
    tree.update(m_Name=ROW_NAME, inlineSheet=pointer(ROW_STYLE))
    sheet['m_Name'] = ROW_NAME + '_Style'
    root = 1001
    retain = {-2, 1000, root, position.a(root)['m_SerializedData']['rid']}
    tree['references']['RefIds'] = [r for r in tree['references']['RefIds'] if r['rid'] in retain]
    refs(tree)[root]['data'].update(m_Children=[], m_Classes=[], m_RuleIndex=-1)
    add_object(position.obj, ROW, tree)
    add_object(objs[W][position.sid], ROW_STYLE, sheet)
    row = Doc(W, pid=ROW, tree=tree, style=sheet)
    row.size(root, ROW_WIDTH, 66)
    row.st(root, [(131083, row.enum('column')), (131073, row.enum('center'))])

    position_text = row.add(position, 1006, root, 'RosterPosition')
    image_scope = row.add(names, 1004, root, 'RosterPortraitBinding')
    row.data(image_scope).update(
        Mappings=[{'m_serialisedType': 0, 'from': 'person', 'to': {'m_path': 'binding'},
                   'type': {'id': 1145176065}}], Mappings_UxmlAttributeFlags=1)
    row.size(image_scope, 34, 34)
    image = row.add(portrait, 1007, image_scope, 'RosterPortrait')
    row.using(portrait, 'PersonPicture')
    assert row.d['m_Usings'][0]['path'] == PICTURE_GUID
    row.fill(image)
    name_text = row.add(position, 1006, root, 'RosterName')
    row.data(name_text)['TextBinding']['m_direct']['Path']['m_path'] = (
        names.data(1004)['Mappings'][0]['to']['m_path'])

    for node, size, color in [(position_text, 10, 'global-text-secondary'),
                              (name_text, 12, 'global-text-primary')]:
        row.a(node)['m_Classes'] = ['body-sm', 'content-no-wrap', 'content-ellipsis', color]
        row.data(node).update(DebugDisplay='', DisplayTooltipWhenElided=1,
                              DisplayTooltipWhenElided_UxmlAttributeFlags=1)
        row.size(node, ROW_WIDTH - 8, 16)
        row.st(node, [(65537, row.px(size)), (65546, row.enum('middle-center'))])
    assert row.a(root)['m_Children'] == [{'rid': i} for i in (position_text, image_scope, name_text)]
    row.save()
    return row


def update_host():
    host = Doc(W, pid=HOST)
    baseline = copy.deepcopy(host.r)
    assert host.d['m_Name'] == 'SquadOverviewTableBlock'
    assert host.data(1007)['name'] == 'framebox'
    assert host.data(1013)['Binding']['m_direct']['Path']['m_path'] == 'team.FilteredPlayers'

    strip = host.add(host, 1012, 1001, 'TFClubSquadRosterStrip')
    host.move(strip, 1001, host.a(1001)['m_Children'].index({'rid': 1007}))
    visibility = host.data(strip)
    visibility['Binding'] = copy.deepcopy(host.data(1013)['Binding'])
    visibility['Binding']['m_direct']['Path']['m_path'] = 'team.IsClub'
    for key, value in {'Binding': visibility['Binding'], 'InvertDirectBinding': 0,
                       'AcceptNumbers': 0, 'VisibilityType': 0}.items():
        visibility[key] = value
        visibility[key + '_UxmlAttributeFlags'] = 1
    color = {c: struct.unpack('<f', struct.pack('<f', v / 255))[0]
             for c, v in zip('rgba', (38, 52, 69, 255))}
    host.st(strip, [(131074, host.enum('stretch')), (131083, host.enum('column')),
                    (131085, host.num(0)), (131087, host.px(86)),
                    (131090, host.px(8)), (458752, host.val(4, color))])

    native = Doc(W, name='InternationalSquadRegistrationTile_4x4')
    scroller = host.add(native, 1028, strip, 'TFClubSquadRoster')
    values = host.data(scroller)
    assert values['Binding']['m_direct']['Path']['m_path'] == 'team.Players'
    assert values['RowParamName'] == 'binding' and values['Direction'] == 1
    for key, value in {'ScrollViewMode': 1, 'HorizontalScrollerVisibility': 0,
                       'DynamicElements': 0, 'FixedElementSize': float(ROW_WIDTH),
                       'FixedElementSizeControllerOrTouch': float(ROW_WIDTH),
                       'Truncate': 0, 'SetIgnorePickingMode': 0, 'pickingMode': 0}.items():
        values[key] = value
        values[key + '_UxmlAttributeFlags'] = 1
    values['RowTemplate']['m_AssetGUID'] = ROW_GUID
    values['RowTemplate_UxmlAttributeFlags'] = 1
    host.a(scroller)['m_Classes'] = ['row-direction-normal', 'align-items-center']
    host.st(scroller, [(131074, host.enum('stretch')), (131084, host.num(1)),
                       (131096, host.px(0)), (131097, host.px(0))])
    for rid, original in baseline.items():
        if rid == 1001:
            original['data']['m_Children'] = host.a(1001)['m_Children']
        assert host.r[rid] == original, rid
    host.save()


def register_assets(cat_raw, row):
    meta = next(o for o in objs[W].values() if o.type.name == 'AssetBundle')
    tree = meta.read_typetree()
    entries = tree['m_Container']
    preload = tree['m_PreloadTable']
    assert not any(key == ROW_GUID for key, _ in entries)
    row_span = [pointer(ROW), pointer(ROW_STYLE), row.d['m_Script'], row.s['m_Script']]
    new_entry = {'asset': pointer(ROW), 'preloadIndex': len(preload), 'preloadSize': len(row_span)}
    entries.append((ROW_GUID, new_entry))
    preload.extend(row_span)
    entries.sort(key=lambda item: item[0])
    meta.save_typetree(tree)
    changes[W][meta.path_id] = tree

    cat = catalog.Catalog(cat_raw)
    source = next(loc for loc in cat.locations(HOST_GUID)
                  if cat.location(loc)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset')
    cat = catalog.Catalog(cat.add_key_location(ROW_GUID, source, source))
    loc, = cat.locations(ROW_GUID)
    record = cat.location(loc)
    assert record['type'] == cat.location(source)['type']
    assert record['dependencies'] == cat.location(source)['dependencies']
    deps = [cat.location(i)['internal'].split('\\')[-1] for i in record['dependencies']]
    assert deps[0] == W and G in deps
    picture = next(cat.location(i) for i in cat.locations(PICTURE_GUID)
                   if cat.location(i)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset')
    assert cat.location(picture['dependencies'][0])['internal'].endswith(G)
    index = next(i for i, (key, _) in enumerate(cat.keys()) if key == 'GameWorldVisualTreeAssetPreload')
    key, span = cat.key_records[index]
    previous = cat.array(span, 'I')
    assert (source,) in previous
    records = list(cat.key_records)
    records[index] = (key, cat.append(b''.join(struct.pack('<I', i) for i, in previous + [(loc,)]), True))
    struct.pack_into('<I', cat.data, 8,
                     cat.append(b''.join(struct.pack('<2I', *entry) for entry in records), True))
    final = catalog.Catalog(cat.data)
    assert final.array(final.key_records[index][1], 'I') == previous + [(loc,)]
    assert final.locations(ROW_GUID) == [loc]
    return bytes(final.data)


transactions = []
for tag, folder, cat_folder in [
    ('game', Path(locations['bundle_root']), Path(locations['aa_root'])),
    ('skin', Path(locations['skin_packages']), Path(locations['skin_packages'])),
]:
    targets = [folder / W, cat_folder / 'catalog.bin', cat_folder / 'catalog.hash']
    bundle_raw, cat_raw, hash_raw = [path.read_bytes() for path in targets]
    env = {W: UnityPy.load(bundle_raw)}
    objs = {W: {o.path_id: o for o in env[W].objects}}
    original_hashes = {pid: sha(obj.get_raw_data()) for pid, obj in objs[W].items()}
    changes, documents = {W: {}}, []
    row = make_row()
    update_host()
    new_catalog = register_assets(cat_raw, row)
    new_bundle = env[W].file.save(packer='lz4')
    saved = {o.path_id: o for o in UnityPy.load(new_bundle).objects}
    assert set(saved) == set(original_hashes) | {ROW, ROW_STYLE}
    for pid, obj in saved.items():
        if pid in changes[W]:
            assert obj.read_typetree() == changes[W][pid], (tag, pid)
        else:
            assert sha(obj.get_raw_data()) == original_hashes[pid], (tag, pid)
    for doc in documents:
        validate_ui(saved[doc.obj.path_id].read_typetree(), saved[doc.sid].read_typetree())
    payloads = [new_bundle, new_catalog, hashlib.md5(new_catalog).hexdigest().encode('ascii')]
    for target, old, new in zip(targets, [bundle_raw, cat_raw, hash_raw], payloads):
        source, backup = OUT / tag / target.name, OUT / ('backup-' + tag) / target.name
        source.parent.mkdir(exist_ok=True)
        backup.parent.mkdir(exist_ok=True)
        source.write_bytes(new)
        backup.write_bytes(old)
        transactions.append({'target': str(target), 'source': str(source), 'backup': str(backup),
                             'before': sha(old), 'after': sha(new)})

manifest = {'installed': False, 'runtime_verified': False, 'protected_sha256': {},
            'scope': 'Desktop club Squad Overview, directly above the original table',
            'list_binding': 'team.Players', 'row_guid': ROW_GUID, 'row_path_id': ROW,
            'row_order': ['binding.PositionCombinedString', 'PersonPicture', 'binding.Name'],
            'horizontal_scroll': True, 'strip_height_px': 86, 'player_width_px': ROW_WIDTH,
            'catalog_preload_verified': True, 'unrelated_bundle_objects_byte_identical': True}
(OUT / 'manifest.json').write_text(json.dumps(manifest, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transactions, indent=2), 'utf8')
(OUT / 'installer.py').write_bytes((R / 'install-independent-resource-patch.py').read_bytes())
for action, flag in [('install', ''), ('restore', ' --restore')]:
    (OUT / (action + '.ps1')).write_text(
        "$ErrorActionPreference = 'Stop'\n"
        f"& '{sys.executable}' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot{flag}\n"
        "if ($LASTEXITCODE -ne 0) { throw 'Resource transaction failed' }\n", 'utf8')
print(OUT)
