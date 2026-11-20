"""Prepare an independent seventh overview from each target's current resources."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import struct
import sys
import uuid
import zlib

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
for filename, names in [
    ('build-fc-player-hover-layout.py', {'write', 'Styles'}),
    ('add-card-six-ratings.py', {'validate_ui'}),
    ('add-two-portrait-hidden-overviews.py', {'refs', 'data', 'named', 'rid_links', 'owned_refs'}),
]:
    module = ast.parse((R / filename).read_text('utf-8-sig'))
    nodes = [n for n in module.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    assert len(nodes) == len(names)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'))
TypeTreeHelper.write_value = write
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)

loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
L = 'ui-tileslayouts_assets_all.bundle'
CACHE = Path.home() / 'AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large'
OUT = R / ('left-test-overview-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
reserved = {int(t['path_id']) for t in json.loads((R / 'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
V = dict(title='左边版-测试版', ident='PlayerOverviewLeftTest', title_key='OverviewLeftTestVariantTitle',
         name='OverviewLeftTestPortraitHidden', source=-941100000001000, description_source=-941100000001002,
         page=-941100000001020, style=-941100000001021, description=-941100000001022,
         guid=uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-player-overview-left-test-portrait-hidden-v1').hex)
IC = dict(source=-940000000022000, page=-941100000001030, style=-941100000001031,
          guid=uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-player-overview-left-test-club-flag-v1').hex,
          alias='LeftTestClubFlagColumn')
SET_ID, COMPOSITION_ID, HOST_ID = 1332213496068314481, 3901662990989568885, 7857044477279960178
ORIGINAL_DESCRIPTIONS = [-950000000000232, -950000000000231, -950000000000230, -950000000000229,
                         -941100000001002, -941100000001012]
transaction, audits, catalog_audits = [], [], []
protected = {str(p): sha(p.read_bytes()) for base in [GAME, SKIN]
             for p in base.glob('*.bundle') if p.name not in [W, L]}


def add_tx(tag, target, output, original):
    source, backup = OUT / tag / target.name, OUT / ('backup-' + tag) / target.name
    source.parent.mkdir(exist_ok=True)
    backup.parent.mkdir(exist_ok=True)
    source.write_bytes(output)
    backup.write_bytes(original)
    transaction.append(dict(target=str(target), source=str(source), backup=str(backup),
                            before=sha(original), after=sha(output)))


def prune(doc, root, keep=()):
    rr = refs(doc)
    removed = owned_refs(rr, root) - set(keep)
    parent = rr[root]['data']['m_Parent']['rid']
    rr[parent]['data']['m_Children'].remove({'rid': root})
    doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in removed]
    return removed


def fixed(st, width, height):
    return [st.p(131105, st.px(width)), st.p(131097, st.px(width)), st.p(131095, st.px(width)),
            st.p(131087, st.px(height)), st.p(131096, st.px(height)), st.p(131094, st.px(height)),
            st.p(131084, st.num(0)), st.p(131085, st.num(0)), st.p(131102, st.en('relative')),
            st.p(262150, st.px(0)), st.p(262151, st.px(0))]


def rearrange(doc, sheet):
    rr, st = refs(doc), Styles(sheet)
    portrait = named(doc, 'ReportPortraitStatusColumn')
    identity = named(doc, 'ReportIdentityColumn')
    banner = rr[portrait]['data']['m_Parent']['rid']
    assert [c['rid'] for c in rr[banner]['data']['m_Children']] == [identity, portrait, 1173]
    template = named(doc, 'ReportIconsBackgroundTemplate')
    keep = owned_refs(rr, template)
    removed = prune(doc, named(doc, 'ReportIconsUnderBackgroundLayer'), keep)
    rr = refs(doc)
    rr[template]['data']['m_Parent'] = {'rid': banner}
    rr[template]['data']['m_TemplateAlias'] = IC['alias']
    sd = data(rr, template)
    sd.update(name=IC['alias'], templateId=IC['alias'], template={'m_FileID': 0, 'm_PathID': IC['page']})
    u = next(u for u in doc['m_Usings'] if u['alias'] == 'MovedHeader_ReportIconsBelowPlayerTopBackground')
    u.update(alias=IC['alias'], path=IC['guid'], asset={'m_FileID': 0, 'm_PathID': IC['page']})
    rr[banner]['data']['m_Children'] = [{'rid': i} for i in [portrait, template, identity, 1173]]
    st.edit(rr[portrait], fixed(st, 226, 250) + [st.p(131092, st.px(12)), st.p(131073, st.en('flex-start'))])
    st.edit(rr[template], fixed(st, 100, 250) + [st.p(131092, st.px(12))], reset=True)
    st.edit(rr[identity], [st.p(131084, st.num(1)), st.p(131085, st.num(1)), st.p(131082, st.px(0)),
                           st.p(131097, st.px(0)), st.p(131073, st.en('stretch')),
                           st.p(131099, st.px(0)), st.p(131100, st.px(0)), st.p(131092, st.px(12))])
    offset = named(doc, 'ReportIdentityOffsetContent')
    st.edit(rr[offset], [st.p(131091, st.px(0)), st.p(131092, st.px(0)), st.p(131089, st.px(0)),
                        st.p(131090, st.px(0)), st.p(131073, st.en('flex-start'))])
    # The two information regions use an equal flex basis after the fixed image columns.
    st.edit(rr[1173], [st.p(131084, st.num(1)), st.p(131085, st.num(1)), st.p(131082, st.px(0))])
    for r in doc['references']['RefIds']:
        for link in rid_links(r.get('data', {})):
            assert link == -2 or link in rr, ('dangling reference', link)
    validate_ui(doc, sheet)
    return dict(top_order=[portrait, template, identity, 1173], removed_icon_background_refs=len(removed),
                portrait_pixels=226, header_height=250, icon_pixels=100, icon_slot_percent=50)


def arrange_icons(doc, sheet):
    # Keep the complete original BindingExpect/BindingSetter and both image bindings.
    prune(doc, 1138)
    prune(doc, 1008)
    rr, st = refs(doc), Styles(sheet)
    rr[1004]['data']['m_Children'] = [{'rid': 1140}]
    rr[1148]['data']['m_Children'] = [{'rid': 1154}, {'rid': 1150}]
    for i in [1001, 1002, 1004, 1140, 1146, 1148]:
        st.edit(rr[i], fixed(st, 100, 250) + [st.p(131083, st.en('column')),
                                           st.p(131073, st.en('stretch')), st.p(131088, st.en('flex-start'))], reset=True)
    for i in [1154, 1150]:
        st.edit(rr[i], [st.p(131105, st.px(100)), st.p(131087, st.pct(50)),
                       st.p(131084, st.num(0)), st.p(131085, st.num(0)), st.p(131102, st.en('relative')),
                       st.p(131073, st.en('center')), st.p(131088, st.en('center'))], reset=True)
    for i in [1156, 1158, 1152]:
        st.edit(rr[i], fixed(st, 100, 100) + [st.p(131073, st.en('center')), st.p(131088, st.en('center'))], reset=True)
    validate_ui(doc, sheet)


for tag, base in [('game', GAME), ('skin', SKIN)]:
    print('Preparing ' + tag, flush=True)
    catpath = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    hashpath = catpath.with_name('catalog.hash')
    initial = {n: (base / n).read_bytes() for n in [W, L]}
    catbefore, hashbefore = catpath.read_bytes(), hashpath.read_bytes()
    cat = cm.Catalog(catbefore)
    env = {n: UnityPy.load(b) for n, b in initial.items()}
    obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
    hashes = {n: {i: sha(o.get_raw_data()) for i, o in oo.items()} for n, oo in obs.items()}
    modified = {W: {}, L: {}}

    def save(n, pid, doc):
        obs[n][pid].save_typetree(doc)
        modified[n][pid] = copy.deepcopy(doc)

    def add(n, source, pid, doc):
        assert pid not in obs[n] and pid not in reserved
        obj = copy.copy(obs[n][source])
        obj.path_id, obj.data, obj._read_until = pid, None, None
        obj.assets_file.objects[pid] = obj
        obs[n][pid] = obj
        save(n, pid, doc)

    abobj = next(o for o in obs[W].values() if o.type.name == 'AssetBundle')
    meta = abobj.read_typetree()
    oldmeta = copy.deepcopy(meta)

    def register(source_id, page_id, style_id, guid, extra_span=()):
        src_key, entry = next((k, e) for k, e in oldmeta['m_Container'] if e['asset']['m_PathID'] == source_id)
        source_style = obs[W][source_id].read_typetree()['inlineSheet']['m_PathID']
        span = copy.deepcopy(oldmeta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
        for ptr in span:
            if ptr['m_FileID'] == 0:
                ptr['m_PathID'] = {source_id: page_id, source_style: style_id}.get(ptr['m_PathID'], ptr['m_PathID'])
        for ptr in list(extra_span) + [{'m_FileID': 0, 'm_PathID': page_id}, {'m_FileID': 0, 'm_PathID': style_id}]:
            if ptr not in span:
                span.append(copy.deepcopy(ptr))
        assert not any(ptr['m_PathID'] in reserved for ptr in span)
        meta['m_Container'].append((guid, dict(preloadIndex=len(meta['m_PreloadTable']), preloadSize=len(span),
                                               asset={'m_FileID': 0, 'm_PathID': page_id})))
        meta['m_PreloadTable'].extend(span)
        return src_key, span

    def catalog_add(current, source_key, guid, extra_deps=()):
        src = next(i for i in current.locations(source_key) if current.location(i)['type'][1].endswith('VisualTreeAsset'))
        deps = list(dict.fromkeys(current.location(src)['dependencies'] + list(extra_deps)))
        assert current.location(deps[0])['internal'].endswith(W)
        raw = list(current.unpack(src, '7I'))
        depbytes = b''.join(struct.pack('<I', x) for x in deps)
        raw[3], raw[4] = current.append(depbytes, True), zlib.crc32(depbytes)
        dep_loc = current.append(struct.pack('<7I', *raw))
        current = cm.Catalog(current.add_key_location(guid, src, dep_loc))
        newloc = current.locations(guid)[0]
        idx = next(i for i, (key, _) in enumerate(current.key_records) if current.object(key) == 'GameWorldVisualTreeAssetPreload')
        key, ls = current.key_records[idx]
        locations = [x[0] for x in current.array(ls, 'I')] + [newloc]
        ls = current.append(b''.join(struct.pack('<I', x) for x in locations), True)
        records = list(current.key_records)
        records[idx] = key, ls
        table = current.append(b''.join(struct.pack('<2I', *x) for x in records), True)
        struct.pack_into('<I', current.data, 8, table)
        current = cm.Catalog(bytes(current.data))
        assert newloc in current.locations('GameWorldVisualTreeAssetPreload')
        assert current.location(newloc)['dependencies'] == deps
        catalog_audits.append(dict(target=tag, guid=guid, type=current.location(newloc)['type'][1],
                                   owning_bundle_first=True, actual_preload=True))
        return current, deps

    icon = obs[W][IC['source']].read_typetree()
    icon_style_id = icon['inlineSheet']['m_PathID']
    icon_sheet = obs[W][icon_style_id].read_typetree()
    original_icon = copy.deepcopy(icon)
    arrange_icons(icon, icon_sheet)
    icon.update(m_Name='OverviewLeftTestClubFlag', inlineSheet={'m_FileID': 0, 'm_PathID': IC['style']})
    icon_sheet['m_Name'] = 'OverviewLeftTestClubFlagStyle'
    add(W, icon_style_id, IC['style'], icon_sheet)
    add(W, IC['source'], IC['page'], icon)
    icon_key, icon_span = register(IC['source'], IC['page'], IC['style'], IC['guid'])
    cat, icon_deps = catalog_add(cat, icon_key, IC['guid'])
    # Exact serialized image functions, fallback team logic and nation mappings survive.
    for i, ref in refs(icon).items():
        if ref.get('type', {}).get('class', '').endswith('/UxmlSerializedData'):
            assert ref == refs(original_icon)[i]

    source = obs[W][V['source']].read_typetree()
    doc = copy.deepcopy(source)
    source_style = source['inlineSheet']['m_PathID']
    sheet = obs[W][source_style].read_typetree()
    detail = rearrange(doc, sheet)
    doc.update(m_Name=V['name'], inlineSheet={'m_FileID': 0, 'm_PathID': V['style']},
               m_ContentHash=struct.unpack('<i', struct.pack('<I', zlib.crc32(V['guid'].encode())))[0])
    sheet['m_Name'] = V['name'] + 'Style'
    add(W, source_style, V['style'], sheet)
    add(W, V['source'], V['page'], doc)
    page_key, _ = register(V['source'], V['page'], V['style'], V['guid'], icon_span)
    cat, _ = catalog_add(cat, page_key, V['guid'], icon_deps)
    oldrr, newrr = refs(source), refs(doc)
    lower_refs = owned_refs(oldrr, 1002)
    for i in lower_refs:
        assert newrr[i] == oldrr[i], ('lower region changed', i)
    for i, ref in newrr.items():
        if ref.get('type', {}).get('class', '').endswith('/UxmlSerializedData') and i != 1165:
            assert ref == oldrr[i], ('data binding changed', i)
    audits.append(dict(target=tag, **detail, lower_regions_identical=True, all_other_serialized_bindings_identical=True))
    meta['m_Container'].sort(key=lambda x: x[0])
    save(W, abobj.path_id, meta)

    desc = obs[L][V['description_source']].read_typetree()
    desc.update(m_Name=V['name'] + 'Description', m_translationType=2,
                m_directTitlePath={'m_path': V['title_key']})
    desc['<Name>k__BackingField'] = desc['<ID>k__BackingField'] = V['ident']
    for cfg in desc['<Configurations>k__BackingField']:
        cfg['Description'] = {'m_FileID': 0, 'm_PathID': V['description']}
        cfg['AssetRef']['m_AssetGUID'] = V['guid']
    add(L, V['description_source'], V['description'], desc)
    tile_set = obs[L][SET_ID].read_typetree()
    choice_ids = [p['m_PathID'] for p in tile_set['m_gridElementDescriptions'] if p['m_FileID'] == 0
                  and obs[L][p['m_PathID']].read_typetree().get('<ID>k__BackingField', '').startswith('PlayerOverview')]
    assert choice_ids == ORIGINAL_DESCRIPTIONS, ('unexpected starting choices', choice_ids)
    tile_set['m_gridElementDescriptions'].append({'m_FileID': 0, 'm_PathID': V['description']})
    save(L, SET_ID, tile_set)
    composition = obs[L][COMPOSITION_ID].read_typetree()
    placement = dict(m_elementID=V['ident'], m_optionalConditions=[], m_optionalConfigConditions=[])
    composition['m_placementBindings'].append(copy.deepcopy(placement))
    save(L, COMPOSITION_ID, composition)
    layout_ab = next(o for o in obs[L].values() if o.type.name == 'AssetBundle')
    layout_meta = layout_ab.read_typetree()
    preload_updates = 0
    for key, entry in layout_meta['m_Container']:
        span = copy.deepcopy(layout_meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
        if any(p['m_FileID'] == 0 and p['m_PathID'] in [SET_ID, COMPOSITION_ID] for p in span):
            span.append({'m_FileID': 0, 'm_PathID': V['description']})
            entry['preloadIndex'], entry['preloadSize'] = len(layout_meta['m_PreloadTable']), len(span)
            layout_meta['m_PreloadTable'].extend(span)
            preload_updates += 1
    assert preload_updates >= 3
    save(L, layout_ab.path_id, layout_meta)

    host = obs[W][HOST_ID].read_typetree()
    hr = refs(host)
    variables = next(r['data'] for r in hr.values() if r.get('type', {}).get('class') == 'BindingVariablesComponent/UxmlSerializedData')
    props = next(r['data']['m_Properties'] for r in hr.values() if r.get('data', {}).get('m_Id') == variables['uxmlAssetId'])
    text_prop = next(p for p in props if p['name'] == 'value-vars')
    grids = [r['data']['Bindings'] for r in hr.values() if 'm_gridElementBindingData' in r.get('data', {}).get('Bindings', {})
             and r['data']['Bindings'].get('m_gridCompositionSet', {}).get('m_PathID') == 1615455816372668659]
    assert len(grids) == 1
    grid = grids[0]
    variables['ValueVariables'].append(dict(m_name=V['title_key'], m_scopeValue={'m_serializedData': 'String|' + V['title'] + '|'}))
    text_prop['value'] += ',{' + V['title_key'] + '}{String|' + V['title'] + '|}'
    grid['m_nameBindings'].append(dict(name=V['title_key'], path={'m_path': V['title_key']}, method=0))
    source_name = obs[L][V['description_source']].read_typetree()['<ID>k__BackingField']
    mappings = copy.deepcopy([m for m in grid['m_gridElementBindingData'] if m['DescriptionAndMapping']['DescriptionName'] == source_name])
    assert {'person', 'team', 'player', 'isonmainscreen'} <= {m['DescriptionAndMapping']['MappingName'] for m in mappings}
    for mapping in mappings:
        mapping['DescriptionAndMapping']['DescriptionName'] = V['ident']
    mappings.append(dict(DescriptionAndMapping=dict(DescriptionName=V['ident'], MappingName=V['title_key'], MappingReferenceID=0),
                         BindingPath={'m_path': ''}, IsDynamic=0))
    grid['m_gridElementBindingData'].extend(mappings)
    validate_ui(host, obs[W][host['inlineSheet']['m_PathID']].read_typetree())
    save(W, HOST_ID, host)

    for n, e in env.items():
        output = e.file.save(packer='lz4')
        check = {o.path_id: o for o in UnityPy.load(output).objects}
        assert set(check) == set(obs[n])
        for pid, before_hash in hashes[n].items():
            if pid not in modified[n]:
                assert sha(check[pid].get_raw_data()) == before_hash, ('unrelated object changed', tag, n, pid)
        for pid, expected in modified[n].items():
            assert check[pid].read_typetree() == expected, ('roundtrip mismatch', tag, n, pid)
        add_tx(tag, base / n, output, initial[n])
    oldcat = cm.Catalog(catbefore)
    assert len(cat.key_records) == len(oldcat.key_records) + 2
    current_keys = set(cat.keys())
    for key, old_locations in oldcat.keys():
        if key == 'GameWorldVisualTreeAssetPreload':
            assert cat.locations(key)[:-2] == oldcat.locations(key)
        else:
            assert (key, old_locations) in current_keys
    catout = bytes(cat.data)
    add_tx(tag, catpath, catout, catbefore)
    add_tx(tag, hashpath, hashlib.md5(catout).hexdigest().encode('ascii'), hashbefore)
    print('Verified ' + tag + ': seven choices, original six unchanged, page and icon component preloaded.', flush=True)

if CACHE.exists():
    before_cache = CACHE.read_bytes()
    cache = json.loads(before_cache)
    assert not any(p['m_elementID'] == V['ident'] for p in cache['m_placementBindings'])
    cache['m_placementBindings'].append(copy.deepcopy(placement))
    add_tx('cache', CACHE, json.dumps(cache, ensure_ascii=False, separators=(',', ':')).encode('utf8'), before_cache)

for row in transaction:
    assert sha(Path(row['target']).read_bytes()) == row['before'], ('baseline changed', row['target'])
for path, digest in protected.items():
    assert sha(Path(path).read_bytes()) == digest
manifest = dict(installed=False, runtime_verified=False, version=V, icons=IC, audits=audits,
                catalog_audits=catalog_audits, protected_sha256=protected,
                original_six_pages_and_styles_byte_identical=True, all_unrelated_bundle_objects_byte_identical=True,
                saved_active_selection_and_positions_unchanged=True, main_and_bottom_grid_unchanged=True,
                installer_uses_hash_guards=True)
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transaction, ensure_ascii=False, indent=2), 'utf8')
installer = (R / 'install-independent-resource-patch.py').read_text('utf8')
needle = 'for row in tx:\n'
assert installer.count(needle) == 1
installer = installer.replace(needle, 'allowed.add(Path(' + repr(str(CACHE.parent)) + ').resolve())\n' + needle)
installer = installer.replace('.codex-fitness-', '.codex-overview-')
(OUT / 'installer.py').write_text(installer, 'utf8')
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT / name).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable +
                           "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + mode +
                           "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n", 'utf-8-sig')
index = dict(manifest=str(OUT / 'manifest.json'), script=str(Path(__file__).resolve()),
             title=V['title'], count=7, installed=False, runtime_verified=False)
(R / 'current-player-overview-test-variant.json').write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(dict(prepared=True, installed=False, output=str(OUT), files=len(transaction)), ensure_ascii=False))
