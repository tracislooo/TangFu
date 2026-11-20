"""Prepare the numbered layout revision of the existing seventh overview."""
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
    ('add-left-test-overview.py', {'prune'}),
]:
    module = ast.parse((R / filename).read_text('utf-8-sig'))
    nodes = [n for n in module.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    assert len(nodes) == len(names)
    exec(compile(ast.Module(body=nodes, type_ignores=[]), filename, 'exec'))
TypeTreeHelper.write_value = write


class LayoutStyles(Styles):
    def edit(self, node, props, reset=False):
        unique = {(p['m_Id'], p.get('m_CustomName', '')): p for p in props}
        super().edit(node, list(unique.values()), reset)


spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
PAGE, STYLE = -941100000001020, -941100000001021
SOURCE, SELECTOR, SELECTOR_STYLE = -940000000005000, -941100000001040, -941100000001041
GUID = uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-left-test-numbered-pitch-role-comparison-layout-v1').hex
ALIAS = 'LeftTestPitchRolesComparison'
OUT = R / ('left-test-numbered-layout-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
reserved = {int(t['path_id']) for t in json.loads((R / 'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
index_path = R / 'current-player-overview-test-variant.json'
old_index = json.loads(index_path.read_text('utf8'))
while not old_index.get('installed'):
    previous_index = Path(old_index['manifest']).parent / 'previous-index.json'
    assert previous_index.exists(), 'Cannot identify the last installed revision'
    old_index = json.loads(previous_index.read_text('utf8'))
protected = {str(p): sha(p.read_bytes()) for base in [GAME, SKIN]
             for p in base.glob('*.bundle') if p.name not in [W, G]}
tx, audits = [], []


def add_tx(tag, target, output, original):
    source, backup = OUT / tag / target.name, OUT / ('backup-' + tag) / target.name
    source.parent.mkdir(exist_ok=True)
    backup.parent.mkdir(exist_ok=True)
    source.write_bytes(output)
    backup.write_bytes(original)
    tx.append(dict(target=str(target), source=str(source), backup=str(backup), before=sha(original), after=sha(output)))


def move(rr, node, parent):
    a = rr[node]['data']
    rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid': node})
    a['m_Parent'] = {'rid': parent}
    rr[parent]['data']['m_Children'].append({'rid': node})


def box(st, width=None, height=None, grow=0, direction='column'):
    props = [st.p(131102, st.en('relative')), st.p(131083, st.en(direction)),
             st.p(131097, st.px(0)), st.p(131096, st.px(0)),
             st.p(131095, {'m_ValueType': 1, 'valueIndex': 3}),
             st.p(131094, {'m_ValueType': 1, 'valueIndex': 3}),
             st.p(131084, st.num(grow)), st.p(131085, st.num(1)),
             st.p(131073, st.en('stretch')), st.p(131074, st.en('stretch')),
             st.p(131088, st.en('flex-start')), st.p(262150, st.px(0)), st.p(262151, st.px(0))]
    if width is not None:
        props.append(st.p(131105, width))
    if height is not None:
        props.append(st.p(131087, height))
    if grow:
        props.append(st.p(131082, st.px(0)))
    return props


def clone_node(doc, source_id, parent, name):
    rr = refs(doc)
    node = copy.deepcopy(rr[source_id])
    sd = copy.deepcopy(rr[node['data']['m_SerializedData']['rid']])
    nr = max(rr) + 1
    nid = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
    assert nid < 2147483647
    node['rid'], sd['rid'] = nr, nr + 1
    node['data'].update(m_Id=nid, m_Parent={'rid': parent}, m_Children=[], m_SerializedData={'rid': nr + 1}, m_RuleIndex=-1)
    sd['data'].update(uxmlAssetId=nid, name=name, name_UxmlAttributeFlags=1)
    doc['references']['RefIds'].extend([node, sd])
    rr[parent]['data']['m_Children'].append({'rid': nr})
    return nr


def graph_check(doc, sheet):
    validate_ui(doc, sheet)
    rr = refs(doc)
    seen = set()
    def visit(i):
        assert i not in seen, ('cyclic or duplicate visual child', i)
        seen.add(i)
        for child in rr[i]['data'].get('m_Children', []):
            assert rr[child['rid']]['data']['m_Parent']['rid'] == i
            visit(child['rid'])
    visit(doc['m_VisualTree']['rid'])
    for i, r in rr.items():
        if 'm_Parent' in r.get('data', {}):
            assert i in seen, ('orphan node', i)
        for link in rid_links(r.get('data', {})):
            assert link == -2 or link in rr


for tag, base in [('game', GAME), ('skin', SKIN)]:
    print('Preparing ' + tag, flush=True)
    original = {n: (base / n).read_bytes() for n in [W, G]}
    env = {n: UnityPy.load(b) for n, b in original.items()}
    obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
    hashes = {n: {i: sha(o.get_raw_data()) for i, o in oo.items()} for n, oo in obs.items()}
    modified = {W: {}, G: {}}
    catpath = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    catbefore, hashbefore = catpath.read_bytes(), catpath.with_name('catalog.hash').read_bytes()
    cat = cm.Catalog(catbefore)

    def save(n, pid, doc):
        obs[n][pid].save_typetree(doc)
        modified[n][pid] = copy.deepcopy(doc)

    def add(n, source_id, pid, doc):
        assert pid not in obs[n] and pid not in reserved
        obj = copy.copy(obs[n][source_id])
        obj.path_id, obj.data, obj._read_until = pid, None, None
        obj.assets_file.objects[pid] = obj
        obs[n][pid] = obj
        save(n, pid, doc)

    # Clone the whole native selector so its binding components, selection events,
    # comparison source and contentContainer for the injected bans remain together.
    selector = obs[G][SOURCE].read_typetree()
    source_style = selector['inlineSheet']['m_PathID']
    ssheet = obs[G][source_style].read_typetree()
    old_selector = copy.deepcopy(selector)
    sr, st = refs(selector), LayoutStyles(ssheet)
    st.edit(sr[1007], box(st, st.pct(100), st.pct(100), 1, 'row'), reset=True)
    st.edit(sr[2000], box(st, st.pct(35), st.pct(100)) + [st.p(131085, st.num(0)), st.p(131100, st.px(8))], reset=True)
    st.edit(sr[2002], box(st, st.pct(65), st.px(200), direction='row') + [st.p(131085, st.num(0))], reset=True)
    for i in [2010, 2006]:
        st.edit(sr[i], box(st, st.px(0), st.pct(100), 1) +
                [st.p(131092, st.px(8 if i == 2010 else 0))], reset=True)
    st.edit(sr[1010], [st.p(131087, st.px(184)), st.p(131096, st.px(184)),
                        st.p(131094, st.px(184)), st.p(131085, st.num(0))])
    st.edit(sr[1011], [st.p(131085, st.num(0))])
    st.edit(sr[2008], box(st, st.pct(100), st.px(0), 1), reset=True)
    selector.update(m_Name='LeftTestNumberedPitchRolesComparison', inlineSheet={'m_FileID': 0, 'm_PathID': SELECTOR_STYLE},
                    m_ContentHash=struct.unpack('<i', struct.pack('<I', zlib.crc32(GUID.encode())))[0])
    ssheet['m_Name'] = selector['m_Name'] + 'Style'
    assert selector['m_ContentContainerId'] == sr[2008]['data']['m_Id']
    for i, ref in sr.items():
        if ref.get('type', {}).get('class', '').endswith('/UxmlSerializedData'):
            assert ref == refs(old_selector)[i], ('selector binding changed', i)
    graph_check(selector, ssheet)
    add(G, SOURCE, SELECTOR, selector)
    add(G, source_style, SELECTOR_STYLE, ssheet)
    gab = next(o for o in obs[G].values() if o.type.name == 'AssetBundle')
    gm = gab.read_typetree()
    source_key, entry = next((k, e) for k, e in gm['m_Container'] if e['asset']['m_PathID'] == SOURCE)
    span = copy.deepcopy(gm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
    for p in span:
        if p['m_FileID'] == 0:
            p['m_PathID'] = {SOURCE: SELECTOR, source_style: SELECTOR_STYLE}.get(p['m_PathID'], p['m_PathID'])
    for p in [{'m_FileID': 0, 'm_PathID': SELECTOR}, {'m_FileID': 0, 'm_PathID': SELECTOR_STYLE}]:
        if p not in span:
            span.append(p)
    assert not any(p['m_PathID'] in reserved for p in span)
    gm['m_Container'].append((GUID, dict(preloadIndex=len(gm['m_PreloadTable']), preloadSize=len(span),
                                       asset={'m_FileID': 0, 'm_PathID': SELECTOR})))
    gm['m_PreloadTable'].extend(span)
    gm['m_Container'].sort(key=lambda x: x[0])
    save(G, gab.path_id, gm)
    src_loc = next(i for i in cat.locations(source_key) if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
    cat = cm.Catalog(cat.add_key_location(GUID, src_loc, src_loc))
    newloc = cat.locations(GUID)[0]
    assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(G)
    label = 'GlobalVisualTreeAssetPreload'
    idx = next(i for i, (key, _) in enumerate(cat.key_records) if cat.object(key) == label)
    key, ls = cat.key_records[idx]
    locations = [x[0] for x in cat.array(ls, 'I')] + [newloc]
    ls = cat.append(b''.join(struct.pack('<I', i) for i in locations), True)
    records = list(cat.key_records)
    records[idx] = key, ls
    struct.pack_into('<I', cat.data, 8, cat.append(b''.join(struct.pack('<2I', *x) for x in records), True))
    cat = cm.Catalog(bytes(cat.data))
    assert newloc in cat.locations(label)

    doc, sheet = obs[W][PAGE].read_typetree(), obs[W][STYLE].read_typetree()
    old_doc = copy.deepcopy(doc)
    rr, st = refs(doc), LayoutStyles(sheet)
    assert rr[1173]['data']['m_Parent']['rid'] == 1169
    assert rr[5852]['data']['m_Parent']['rid'] == 1011
    # Region 1 gets an exact copy of its old header binding chain at the lower left.
    context = clone_node(doc, 1116, 1002, 'LeftTestStatisticsContext')
    cur = context
    for src, name in [(1118, 'LeftTestStatisticsExpect'), (1119, 'LeftTestStatisticsRemapper'),
                      (1166, 'LeftTestStatisticsBannerExpect'), (1167, 'LeftTestStatisticsTeamSetter')]:
        cur = clone_node(doc, src, cur, name)
    rr = refs(doc)
    move(rr, 1186, cur)
    move(rr, 6286, cur)
    move(rr, 2242, cur)
    for i in [cur, rr[cur]['data']['m_Parent']['rid']]:
        st.edit(rr[i], box(st, st.pct(100), st.pct(100), 1), reset=True)
    walk_context = context
    while walk_context != cur:
        st.edit(rr[walk_context], box(st, st.pct(100), st.pct(100), 1), reset=True)
        walk_context = rr[walk_context]['data']['m_Children'][0]['rid']
    st.edit(rr[context], box(st, st.px(240), st.pct(100)) +
            [st.p(131097, st.px(240)), st.p(131095, st.px(240)), st.p(131085, st.num(0)), st.p(131092, st.px(4))], reset=True)
    st.edit(rr[2242], box(st, st.pct(100), st.px(0), 1), reset=True)
    # Region 2 occupies the old upper statistics position; 8 occupies the old radar position.
    move(rr, 5852, 1173)
    move(rr, 6298, 1703)
    move(rr, 1007, 1703)
    for i in [1349, 1179, 1181, 1183, 1185, 6288, 1011, 1008, 1010]:
        prune(doc, i)
    rr = refs(doc)
    rr[1703]['data']['m_Children'] = [{'rid': 1007}, {'rid': 6298}]
    rr[1173]['data']['m_Children'] = [{'rid': 1026}, {'rid': 5852}]
    st.edit(rr[1173], box(st, st.px(0), st.px(250), 1, 'row') +
            [st.p(131099, st.px(0)), st.p(131100, st.px(0))], reset=True)
    for i in [1026, 5852]:
        st.edit(rr[i], box(st, st.px(0), st.pct(100), 1) +
                [st.p(131092, st.px(8 if i == 1026 else 0))], reset=True)
    st.edit(rr[1043], [st.p(131087, st.pct(100)), st.p(131096, st.px(0)), st.p(131094, st.pct(100)),
                      st.p(131105, st.pct(100))])
    # Region 7 touches 1; the selector's left column is 3/4, right top is 5/6.
    state = named(doc, 'TFNonMatchModuleBackgroundState')
    rr[1002]['data']['m_Children'] = [{'rid': i} for i in [context, 1009, 1703, state]]
    st.edit(rr[1009], [st.p(131105, st.px(640)), st.p(131082, {'m_ValueType': 1, 'valueIndex': 2}),
                      st.p(131097, st.px(480)), st.p(131095, st.px(640)), st.p(131085, st.num(1)),
                      st.p(131092, st.px(8))])
    st.edit(rr[1703], box(st, st.px(0), st.pct(100), 1) + [st.p(131097, st.px(480))], reset=True)
    st.edit(rr[1007], box(st, st.pct(100), st.pct(100), 1), reset=True)
    st.edit(rr[6298], [st.p(131102, st.en('absolute')), st.p(131089, st.pct(35)), st.p(131103, st.px(0)),
                      st.p(131104, {'m_ValueType': 1, 'valueIndex': 2}), st.p(131080, st.px(0)),
                      st.p(131105, st.pct(65)), st.p(131087, st.px(217)), st.p(131096, st.px(0)),
                      st.p(131094, st.px(217)), st.p(131082, {'m_ValueType': 1, 'valueIndex': 2}),
                      st.p(131084, st.num(0)), st.p(131085, st.num(0))])
    st.edit(rr[6228], box(st, st.pct(100), st.px(0), 1) + [st.p(458768, st.en('hidden'))], reset=True)
    use = next(u for u in doc['m_Usings'] if u['alias'] == 'role_selector-large')
    waf, gaf = obs[W][PAGE].assets_file, obs[G][SOURCE].assets_file
    global_file_id = next(i + 1 for i, e in enumerate(waf.externals) if e.path.endswith('/' + gaf.name))
    use.update(alias=ALIAS, path=GUID, asset={'m_FileID': global_file_id, 'm_PathID': SELECTOR})
    rr[1007]['data']['m_TemplateAlias'] = ALIAS
    data(rr, 1007).update(templateId=ALIAS, template={'m_FileID': global_file_id, 'm_PathID': SELECTOR}, template_UxmlAttributeFlags=1)
    doc['m_ContentHash'] = struct.unpack('<i', struct.pack('<I', zlib.crc32(b'fm27-left-test-numbered-layout-v2')))[0]
    graph_check(doc, sheet)
    oldrr = refs(old_doc)
    for i, ref in rr.items():
        if i in oldrr and ref.get('type', {}).get('class', '').endswith('/UxmlSerializedData') and i != rr[1007]['data']['m_SerializedData']['rid']:
            assert ref == oldrr[i], ('existing data binding changed', i)
    save(W, PAGE, doc)
    save(W, STYLE, sheet)
    wab = next(o for o in obs[W].values() if o.type.name == 'AssetBundle')
    wm = wab.read_typetree()
    page_key, entry = next((k, e) for k, e in wm['m_Container'] if e['asset']['m_PathID'] == PAGE)
    span = copy.deepcopy(wm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
    for p in [{'m_FileID': global_file_id, 'm_PathID': SELECTOR}, {'m_FileID': global_file_id, 'm_PathID': SELECTOR_STYLE}]:
        if p not in span:
            span.append(p)
    assert not any(p['m_PathID'] in reserved for p in span)
    entry['preloadIndex'], entry['preloadSize'] = len(wm['m_PreloadTable']), len(span)
    wm['m_PreloadTable'].extend(span)
    save(W, wab.path_id, wm)
    page_loc = next(i for i in cat.locations(page_key) if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
    deps = list(dict.fromkeys(cat.location(page_loc)['dependencies'] + cat.location(newloc)['dependencies']))
    raw = list(cat.unpack(page_loc, '7I'))
    depbytes = b''.join(struct.pack('<I', i) for i in deps)
    raw[3], raw[4] = cat.append(depbytes, True), zlib.crc32(depbytes)
    struct.pack_into('<7I', cat.data, page_loc, *raw)
    cat = cm.Catalog(bytes(cat.data))
    assert cat.location(cat.location(page_loc)['dependencies'][0])['internal'].endswith(W)
    assert set(cat.location(newloc)['dependencies']) <= set(cat.location(page_loc)['dependencies'])
    for n, e in env.items():
        output = e.file.save(packer='lz4')
        check = {o.path_id: o for o in UnityPy.load(output).objects}
        assert set(check) == set(obs[n])
        for pid, digest in hashes[n].items():
            if pid not in modified[n]:
                assert sha(check[pid].get_raw_data()) == digest, ('unrelated object changed', tag, n, pid)
        for pid, expected in modified[n].items():
            assert check[pid].read_typetree() == expected, ('roundtrip mismatch', tag, n, pid)
        add_tx(tag, base / n, output, original[n])
    catout = bytes(cat.data)
    add_tx(tag, catpath, catout, catbefore)
    add_tx(tag, catpath.with_name('catalog.hash'), hashlib.md5(catout).hexdigest().encode('ascii'), hashbefore)
    audits.append(dict(target=tag, context=context, context_leaf=cur, selector_guid=GUID,
                       global_file_id=global_file_id, source_bindings_preserved=True,
                       original_six_and_shared_selector_unchanged=True,
                       top=[2, 8], bottom=[1, 7, '3/4', '5+6/9']))
    print('Verified ' + tag + ': numbered regions rearranged; native selector events unchanged.', flush=True)

for row in tx:
    assert sha(Path(row['target']).read_bytes()) == row['before']
for path, digest in protected.items():
    assert sha(Path(path).read_bytes()) == digest
manifest = dict(installed=False, runtime_verified=False, previous_manifest=old_index['manifest'],
                page=PAGE, style=STYLE, selector=SELECTOR, selector_style=SELECTOR_STYLE,
                selector_source=SOURCE, selector_guid=GUID, audits=audits, protected_sha256=protected,
                original_six_and_shared_selector_byte_identical=True, current_selection_and_bottom_grid_unchanged=True)
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'previous-index.json').write_text(json.dumps(old_index, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'installer.py').write_text((R / 'install-independent-resource-patch.py').read_text('utf8').replace('.codex-fitness-', '.codex-overview-'), 'utf8')
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT / name).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable +
                           "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + mode +
                           "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n", 'utf-8-sig')
index = dict(manifest=str(OUT / 'manifest.json'), script=str(Path(__file__).resolve()),
             title='左边版-测试版', count=7, installed=False, runtime_verified=False,
             previous_manifest=old_index['manifest'], layout='top 2/8; bottom 1/7/3-4/5+6-9')
index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(dict(prepared=True, installed=False, output=str(OUT), files=len(tx)), ensure_ascii=False))
