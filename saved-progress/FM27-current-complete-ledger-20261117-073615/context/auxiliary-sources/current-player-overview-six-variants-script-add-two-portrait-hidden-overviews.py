"""Prepare two independent portrait/hidden variants from the current resources.

Preparation never installs resources. Run the generated install.ps1 after checking
the manifest; its installer rejects an open game or a changed baseline.
"""
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
helpers = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef)
                             and n.name == 'write'], type_ignores=[]), 'serializer', 'exec'))
TypeTreeHelper.write_value = write
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings',
           6: 'assets', 7: 'strings', 8: 'strings'}
helpers = ast.parse((R / 'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef)
                             and n.name == 'validate_ui'], type_ignores=[]), 'validator', 'exec'))
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)

loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
L = 'ui-tileslayouts_assets_all.bundle'
CACHE = Path.home() / 'AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large'
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S')
OUT = R / ('two-portrait-hidden-overviews-' + stamp)
OUT.mkdir()
sha = lambda data: hashlib.sha256(data).hexdigest()
reserved = json.loads((R / 'reserved-texture-ids.json').read_text('utf8'))
reserved_ids = {int(t['path_id']) for t in reserved['reserved_textures']}
VERSIONS = [
    dict(title='中间版大头像+隐藏', ident='PlayerOverviewMiddlePortraitHidden',
         title_key='OverviewMiddlePortraitHiddenVariantTitle',
         name='OverviewMiddleLargePortraitHidden', source=-930000000001001,
         donor=-930000000001003, description_source=-950000000000232,
         page=-941100000001000, style=-941100000001001, description=-941100000001002,
         guid=uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-player-overview-middle-large-portrait-hidden-v1').hex),
    dict(title='左边版大头像+隐藏', ident='PlayerOverviewLeftPortraitHidden',
         title_key='OverviewLeftPortraitHiddenVariantTitle',
         name='OverviewLeftLargePortraitHidden', source=-940000000010000,
         donor=-940000000012000, description_source=-950000000000230,
         page=-941100000001010, style=-941100000001011, description=-941100000001012,
         guid=uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-player-overview-left-large-portrait-hidden-v1').hex),
]
ORIGINAL_PAGES = [-930000000001001, -930000000001003, -940000000010000, -940000000012000]
SET_ID, COMPOSITION_ID, HOST_ID = 1332213496068314481, 3901662990989568885, 7857044477279960178
transaction, audits, catalog_audits = [], [], []
protected = {str(p): sha(p.read_bytes()) for base in [GAME, SKIN]
             for p in base.glob('*.bundle') if p.name not in [W, L]}


def refs(d):
    return {r['rid']: r for r in d['references']['RefIds']}


def data(rr, i):
    return rr[rr[i]['data']['m_SerializedData']['rid']]['data']


def named(d, name):
    rr = refs(d)
    matches = [i for i, r in rr.items() if r.get('data', {}).get('m_SerializedData', {}).get('rid', -2) != -2
               and data(rr, i).get('name') == name]
    assert len(matches) == 1, (name, matches)
    return matches[0]


def rid_links(value):
    if isinstance(value, dict):
        if set(value) == {'rid'}:
            yield value['rid']
        else:
            for v in value.values():
                yield from rid_links(v)
    elif isinstance(value, list):
        for v in value:
            yield from rid_links(v)


def owned_refs(rr, root):
    found = set()

    def visit(i):
        if i == -2 or i in found:
            return
        assert i in rr, ('missing managed reference', i)
        found.add(i)
        for k, v in rr[i].get('data', {}).items():
            if k != 'm_Parent':
                for link in rid_links(v):
                    visit(link)

    visit(root)
    return found


def replace_portrait(doc, sheet, donor, donor_sheet):
    rr, dr = refs(doc), refs(donor)
    root, donor_root = named(doc, 'ReportPortraitStatusColumn'), named(donor, 'ReportPortraitStatusColumn')
    removed, imported = owned_refs(rr, root), owned_refs(dr, donor_root)
    parent = rr[root]['data']['m_Parent']['rid']
    position = rr[parent]['data']['m_Children'].index({'rid': root})
    rr[parent]['data']['m_Children'].pop(position)
    doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in removed]
    kept = refs(doc)
    assert all(link not in removed for r in kept.values() for link in rid_links(r.get('data', {})))
    next_rid = max(kept) + 1
    ridmap = {i: next_rid + j for j, i in enumerate(sorted(imported))}
    nodes = [i for i in sorted(imported) if 'm_Id' in dr[i].get('data', {})]
    next_id = max(r.get('data', {}).get('m_Id', 0) for r in kept.values()) + 1
    idmap = {dr[i]['data']['m_Id']: next_id + j for j, i in enumerate(nodes)}
    assert next_id + len(nodes) < 2147483647
    rulemap = {}

    def remap(v):
        if isinstance(v, dict):
            if set(v) == {'rid'}:
                if v['rid'] in ridmap:
                    v['rid'] = ridmap[v['rid']]
                else:
                    assert v['rid'] in [-2, dr[donor_root]['data']['m_Parent']['rid']]
            else:
                for k, x in v.items():
                    if k in ['m_Id', 'm_ParentId', 'uxmlAssetId'] and isinstance(x, int) and x in idmap:
                        v[k] = idmap[x]
                    else:
                        remap(x)
        elif isinstance(v, list):
            for x in v:
                remap(x)

    for i in sorted(imported):
        item = copy.deepcopy(dr[i])
        item['rid'] = ridmap[i]
        remap(item['data'])
        a = item['data']
        if i == donor_root:
            a['m_Parent'] = {'rid': parent}
        if i in nodes:
            old_rule = a.get('m_RuleIndex', -1)
            if old_rule >= 0:
                if old_rule not in rulemap:
                    rule = copy.deepcopy(donor_sheet['m_Rules'][old_rule])
                    for prop in rule['m_Properties']:
                        for h in prop['m_Values']:
                            pool = poolmap.get(h['m_ValueType'])
                            if pool:
                                sheet[pool].append(copy.deepcopy(donor_sheet[pool][h['valueIndex']]))
                                h['valueIndex'] = len(sheet[pool]) - 1
                    rulemap[old_rule] = len(sheet['m_Rules'])
                    sheet['m_Rules'].append(rule)
                a['m_RuleIndex'] = rulemap[old_rule]
            alias = a.get('m_TemplateAlias')
            if alias:
                using = next(u for u in donor['m_Usings'] if u['alias'] == alias)
                existing = next((u for u in doc['m_Usings'] if u['alias'] == alias), None)
                if existing:
                    assert existing == using, ('template alias conflict', alias)
                else:
                    doc['m_Usings'].append(copy.deepcopy(using))
        doc['references']['RefIds'].append(item)
    kept[parent]['data']['m_Children'].insert(position, {'rid': ridmap[donor_root]})
    result = refs(doc)
    # Exact donor serialization after remapping proves image fallback, foot and
    # status branches retain their complete data bindings and flags.
    for i in imported:
        expected = copy.deepcopy(dr[i])
        expected['rid'] = ridmap[i]
        remap(expected['data'])
        if i == donor_root:
            expected['data']['m_Parent'] = {'rid': parent}
        if i in nodes and expected['data'].get('m_RuleIndex', -1) >= 0:
            expected['data']['m_RuleIndex'] = rulemap[expected['data']['m_RuleIndex']]
        assert result[ridmap[i]] == expected
    stage = named(doc, 'ReportPortraitLayerStage')
    children = result[stage]['data']['m_Children']
    assert len(children) == 3
    assert [data(result, c['rid']).get('name', '') for c in children] == ['PersonPictureFrame', '', 'CardNativeFootFooter']
    names = [data(result, i).get('name', '') for i in result
             if result[i].get('data', {}).get('m_SerializedData', {}).get('rid', -2) != -2]
    assert 'RightHiddenAttributesPanel' in names
    assert not any(n.startswith(('ReportCAAbove', 'ReportCACardImage', 'OverviewCard')) for n in names)
    assert 'CardNativePlayerSummary' not in names
    assert 'CardLeftFootNativeStepper' in names and 'CardRightFootNativeStepper' in names
    assert 'PlayerStatusFlagsForTeamVisible' in names
    validate_ui(doc, sheet)
    return dict(removed_refs=len(removed), imported_refs=len(imported),
                donor_serialization_equal=True, image_fallback_preserved=True,
                feet_and_status_bindings_preserved=True, external_hidden_panel_preserved=True)


def add_tx(tag, target, output, original):
    source, backup = OUT / tag / target.name, OUT / ('backup-' + tag) / target.name
    source.parent.mkdir(exist_ok=True)
    backup.parent.mkdir(exist_ok=True)
    source.write_bytes(output)
    backup.write_bytes(original)
    transaction.append(dict(target=str(target), source=str(source), backup=str(backup),
                            before=sha(original), after=sha(output)))


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
        assert pid not in obs[n] and pid not in reserved_ids
        obj = copy.copy(obs[n][source])
        obj.path_id, obj.data, obj._read_until = pid, None, None
        obj.assets_file.objects[pid] = obj
        obs[n][pid] = obj
        save(n, pid, doc)

    abobj = next(o for o in obs[W].values() if o.type.name == 'AssetBundle')
    meta = abobj.read_typetree()
    old_meta = copy.deepcopy(meta)
    new_descriptions = []
    for v in VERSIONS:
        source = obs[W][v['source']].read_typetree()
        donor = obs[W][v['donor']].read_typetree()
        doc = copy.deepcopy(source)
        sheet = copy.deepcopy(obs[W][source['inlineSheet']['m_PathID']].read_typetree())
        donor_sheet = obs[W][donor['inlineSheet']['m_PathID']].read_typetree()
        oldrefs = copy.deepcopy(refs(source))
        oldroot = named(source, 'ReportPortraitStatusColumn')
        oldportrait = owned_refs(oldrefs, oldroot)
        parent = oldrefs[oldroot]['data']['m_Parent']['rid']
        detail = replace_portrait(doc, sheet, donor, donor_sheet)
        newrefs = refs(doc)
        for i, r in oldrefs.items():
            if i not in oldportrait and i != parent:
                assert newrefs[i] == r, ('unrelated region changed', tag, v['ident'], i)
        doc.update(m_Name=v['name'], inlineSheet={'m_FileID': 0, 'm_PathID': v['style']},
                   m_ContentHash=struct.unpack('<i', struct.pack('<I', zlib.crc32(v['guid'].encode())))[0])
        sheet['m_Name'] = v['name'] + '_Style'
        add(W, source['inlineSheet']['m_PathID'], v['style'], sheet)
        add(W, v['source'], v['page'], doc)

        src_key, src_entry = next((k, e) for k, e in old_meta['m_Container']
                                  if e['asset']['m_PathID'] == v['source'])
        donor_key, donor_entry = next((k, e) for k, e in old_meta['m_Container']
                                      if e['asset']['m_PathID'] == v['donor'])
        span = []
        for entry in [src_entry, donor_entry]:
            for ptr0 in old_meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']]:
                ptr = copy.deepcopy(ptr0)
                if ptr['m_FileID'] == 0:
                    if ptr['m_PathID'] in [v['source'], v['donor']]:
                        ptr['m_PathID'] = v['page']
                    elif ptr['m_PathID'] in [source['inlineSheet']['m_PathID'], donor['inlineSheet']['m_PathID']]:
                        ptr['m_PathID'] = v['style']
                if ptr not in span:
                    span.append(ptr)
        for ptr in [doc['m_Script'], {'m_FileID': 0, 'm_PathID': v['page']},
                    {'m_FileID': 0, 'm_PathID': v['style']}]:
            if ptr not in span:
                span.append(copy.deepcopy(ptr))
        meta['m_Container'].append((v['guid'], dict(preloadIndex=len(meta['m_PreloadTable']),
                                  preloadSize=len(span), asset={'m_FileID': 0, 'm_PathID': v['page']})))
        meta['m_PreloadTable'].extend(span)
        assert not any(p['m_PathID'] in reserved_ids for p in span)

        src_loc = next(i for i in cat.locations(src_key) if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
        donor_loc = next(i for i in cat.locations(donor_key) if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
        deps = list(dict.fromkeys(cat.location(src_loc)['dependencies'] + cat.location(donor_loc)['dependencies']))
        assert cat.location(deps[0])['internal'].endswith(W)
        raw = list(cat.unpack(src_loc, '7I'))
        depbytes = b''.join(struct.pack('<I', x) for x in deps)
        raw[3], raw[4] = cat.append(depbytes, True), zlib.crc32(depbytes)
        dep_loc = cat.append(struct.pack('<7I', *raw))
        cat = cm.Catalog(cat.add_key_location(v['guid'], src_loc, dep_loc))
        newloc = cat.locations(v['guid'])[0]
        idx = next(i for i, (key, _) in enumerate(cat.key_records)
                   if cat.object(key) == 'GameWorldVisualTreeAssetPreload')
        key, ls = cat.key_records[idx]
        locations = [x[0] for x in cat.array(ls, 'I')] + [newloc]
        ls = cat.append(b''.join(struct.pack('<I', x) for x in locations), True)
        records = list(cat.key_records)
        records[idx] = key, ls
        table = cat.append(b''.join(struct.pack('<2I', *x) for x in records), True)
        struct.pack_into('<I', cat.data, 8, table)
        cat = cm.Catalog(bytes(cat.data))
        assert newloc in cat.locations('GameWorldVisualTreeAssetPreload')
        assert cat.location(newloc)['type'][1] == cat.location(src_loc)['type'][1]
        assert cat.location(newloc)['internal'] == v['guid']
        assert cat.location(newloc)['dependencies'] == deps
        catalog_audits.append(dict(target=tag, guid=v['guid'], page=v['page'],
                                   type=cat.location(newloc)['type'][1], preload=True,
                                   dependency_count=len(deps), owning_bundle_first=True))

        desc = copy.deepcopy(obs[L][v['description_source']].read_typetree())
        desc.update(m_Name=v['name'] + 'Description', m_translationType=2,
                    m_directTitlePath={'m_path': v['title_key']})
        desc['<Name>k__BackingField'] = desc['<ID>k__BackingField'] = v['ident']
        for cfg in desc['<Configurations>k__BackingField']:
            cfg['Description'] = {'m_FileID': 0, 'm_PathID': v['description']}
            cfg['AssetRef']['m_AssetGUID'] = v['guid']
        add(L, v['description_source'], v['description'], desc)
        new_descriptions.append({'m_FileID': 0, 'm_PathID': v['description']})
        audits.append(dict(target=tag, title=v['title'], source=v['source'], donor=v['donor'],
                           **detail, non_portrait_regions_identical=True))
    assert meta['m_Container'][:len(old_meta['m_Container'])] == old_meta['m_Container']
    assert meta['m_PreloadTable'][:len(old_meta['m_PreloadTable'])] == old_meta['m_PreloadTable']
    meta['m_Container'].sort(key=lambda item: item[0])
    save(W, abobj.path_id, meta)

    tile_set = obs[L][SET_ID].read_typetree()
    original_set = copy.deepcopy(tile_set)
    tile_set['m_gridElementDescriptions'].extend(new_descriptions)
    save(L, SET_ID, tile_set)
    composition = obs[L][COMPOSITION_ID].read_typetree()
    old_composition = copy.deepcopy(composition)
    placements = [dict(m_elementID=v['ident'], m_optionalConditions=[], m_optionalConfigConditions=[]) for v in VERSIONS]
    composition['m_placementBindings'].extend(copy.deepcopy(placements))
    check_composition = copy.deepcopy(composition)
    check_composition['m_placementBindings'] = check_composition['m_placementBindings'][:-2]
    assert check_composition == old_composition
    save(L, COMPOSITION_ID, composition)

    # Every bundle entry which loads the shared tile set must preload the two
    # additional local descriptions, including the composition-set entry point.
    layout_ab = next(o for o in obs[L].values() if o.type.name == 'AssetBundle')
    layout_meta = layout_ab.read_typetree()
    preload_updates = 0
    for key, entry in layout_meta['m_Container']:
        span = copy.deepcopy(layout_meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
        if any(p['m_FileID'] == 0 and p['m_PathID'] in [SET_ID, COMPOSITION_ID] for p in span):
            for ptr in new_descriptions:
                if ptr not in span:
                    span.append(copy.deepcopy(ptr))
            entry['preloadIndex'], entry['preloadSize'] = len(layout_meta['m_PreloadTable']), len(span)
            layout_meta['m_PreloadTable'].extend(span)
            preload_updates += 1
    assert preload_updates >= 3
    save(L, layout_ab.path_id, layout_meta)

    host = obs[W][HOST_ID].read_typetree()
    old_host = copy.deepcopy(host)
    hr = refs(host)
    variables = next(r['data'] for r in hr.values() if r.get('type', {}).get('class') == 'BindingVariablesComponent/UxmlSerializedData')
    props = next(r['data']['m_Properties'] for r in hr.values()
                 if r.get('data', {}).get('m_Id') == variables['uxmlAssetId'])
    text_prop = next(p for p in props if p['name'] == 'value-vars')
    grids = [r['data']['Bindings'] for r in hr.values() if 'm_gridElementBindingData' in r.get('data', {}).get('Bindings', {})
             and r['data']['Bindings'].get('m_gridCompositionSet', {}).get('m_PathID') == 1615455816372668659]
    assert len(grids) == 1
    grid = grids[0]
    for v in VERSIONS:
        variables['ValueVariables'].append(dict(m_name=v['title_key'], m_scopeValue={'m_serializedData': 'String|' + v['title'] + '|'}))
        text_prop['value'] += ',{' + v['title_key'] + '}{String|' + v['title'] + '|}'
        grid['m_nameBindings'].append(dict(name=v['title_key'], path={'m_path': v['title_key']}, method=0))
        source_name = obs[L][v['description_source']].read_typetree()['<ID>k__BackingField']
        mappings = copy.deepcopy([m for m in grid['m_gridElementBindingData']
                                  if m['DescriptionAndMapping']['DescriptionName'] == source_name])
        assert {'person', 'team', 'player', 'isonmainscreen'} <= {m['DescriptionAndMapping']['MappingName'] for m in mappings}
        for mapping in mappings:
            mapping['DescriptionAndMapping']['DescriptionName'] = v['ident']
        mappings.append(dict(DescriptionAndMapping=dict(DescriptionName=v['ident'], MappingName=v['title_key'], MappingReferenceID=0),
                             BindingPath={'m_path': ''}, IsDynamic=0))
        grid['m_gridElementBindingData'].extend(mappings)
    # Prove only the title constants and new mappings were appended to the host.
    stripped = copy.deepcopy(host)
    sr = refs(stripped)
    for key in hr:
        before_ref, after_ref = refs(old_host)[key], sr[key]
        if before_ref != after_ref:
            a, b = before_ref['data'], after_ref['data']
            if 'ValueVariables' in b:
                b['ValueVariables'] = b['ValueVariables'][:-2]
            elif 'm_Properties' in b:
                b['m_Properties'] = copy.deepcopy(a['m_Properties'])
            elif 'Bindings' in b:
                for field in ['m_nameBindings', 'm_gridElementBindingData']:
                    b['Bindings'][field] = copy.deepcopy(a['Bindings'][field])
            assert after_ref == before_ref
    assert stripped == old_host
    validate_ui(host, obs[W][host['inlineSheet']['m_PathID']].read_typetree())
    save(W, HOST_ID, host)

    # Exactly six choices in the original order, with all original definitions intact.
    choice_ids = [p['m_PathID'] for p in tile_set['m_gridElementDescriptions'] if p['m_FileID'] == 0
                  and obs[L][p['m_PathID']].read_typetree().get('<ID>k__BackingField', '').startswith('PlayerOverview')]
    assert choice_ids == [-950000000000232, -950000000000231, -950000000000230, -950000000000229] + [v['description'] for v in VERSIONS]
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
    for pid in ORIGINAL_PAGES:
        assert pid not in modified[W]
        sid = obs[W][pid].read_typetree()['inlineSheet']['m_PathID']
        assert sid not in modified[W]
    # Every existing catalog key and location remains identical except the preload
    # label, whose original locations are an unchanged prefix.
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
    print('Verified ' + tag + ': six choices, original four unchanged, two templates preloaded.', flush=True)

if CACHE.exists():
    before_cache = CACHE.read_bytes()
    cache = json.loads(before_cache)
    old_cache = copy.deepcopy(cache)
    cache['m_placementBindings'].extend(copy.deepcopy(placements))
    stripped = copy.deepcopy(cache)
    stripped['m_placementBindings'] = stripped['m_placementBindings'][:-2]
    assert stripped == old_cache
    add_tx('cache', CACHE, json.dumps(cache, ensure_ascii=False, separators=(',', ':')).encode('utf8'), before_cache)

for row in transaction:
    assert sha(Path(row['target']).read_bytes()) == row['before'], ('baseline changed', row['target'])
for path, digest in protected.items():
    assert sha(Path(path).read_bytes()) == digest
manifest = dict(installed=False, runtime_verified=False, versions=VERSIONS,
                audits=audits, catalog_audits=catalog_audits,
                original_four_pages_and_styles_byte_identical=True,
                all_unrelated_bundle_objects_byte_identical=True,
                saved_active_selection_and_positions_unchanged=True,
                main_and_bottom_grid_unchanged=True, protected_sha256=protected,
                offline_scenarios=['donor person image and disabled-image fallback serialized branches identical',
                                   'donor team status visibility and native status template identical',
                                   'donor left/right/preferred foot bindings identical',
                                   'source hidden attributes and goalkeeper/outfield stats branches identical'],
                installer_uses_hash_guards=True)
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transaction, ensure_ascii=False, indent=2), 'utf8')
installer = (R / 'install-independent-resource-patch.py').read_text('utf8')
needle = "for row in tx:\n"
assert installer.count(needle) == 1
installer = installer.replace(needle, 'allowed.add(Path(' + repr(str(CACHE.parent)) + ').resolve())\n' + needle)
installer = installer.replace(".codex-fitness-", ".codex-overview-")
(OUT / 'installer.py').write_text(installer, 'utf8')
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT / name).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable +
                           "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + mode +
                           "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n", 'utf-8-sig')
(R / 'current-player-overview-six-variants.json').write_text(json.dumps(dict(
    manifest=str(OUT / 'manifest.json'), script=str(Path(__file__).resolve()), installed=False,
    runtime_verified=False), ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(dict(prepared=True, installed=False, output=str(OUT), files=len(transaction)), ensure_ascii=False))
