"""Independently audit the prepared or installed seventh overview and its baseline."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

module = ast.parse((R / 'add-two-portrait-hidden-overviews.py').read_text('utf-8-sig'))
names = {'refs', 'data', 'named', 'owned_refs', 'rid_links'}
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in names],
                        type_ignores=[]), 'read-only-helpers', 'exec'))
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
index_path = R / 'current-player-overview-test-variant.json'
index = json.loads(index_path.read_text('utf8'))
OUT = Path(index['manifest']).parent
manifest = json.loads((OUT / 'manifest.json').read_text('utf8'))
tx = json.loads((OUT / 'transaction.json').read_text('utf8'))
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
installed = '--installed' in sys.argv
V, IC = manifest['version'], manifest['icons']
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
L = 'ui-tileslayouts_assets_all.bundle'
SET, COMP, HOST = 1332213496068314481, 3901662990989568885, 7857044477279960178
sha = lambda b: hashlib.sha256(b).hexdigest()
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}


def load(path):
    return {o.path_id: o for o in UnityPy.load(str(path)).objects}


def prop(doc, sheet, node, key):
    ix = refs(doc)[node]['data']['m_RuleIndex']
    pp = [p for p in sheet['m_Rules'][ix]['m_Properties'] if p['m_Id'] == key]
    assert len(pp) == 1, (node, key)
    return [sheet[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h
            for h in pp[0]['m_Values']]


def dimension(doc, sheet, node, key, value, unit=1):
    assert prop(doc, sheet, node, key) == [{'unit': unit, 'value': float(value)}], (node, key)


results = []
for tag, live in [('game', Path(loc['bundle_root'])), ('skin', Path(loc['skin_packages']))]:
    base = live if installed else OUT / tag
    old = {W: load(OUT / ('backup-' + tag) / W), L: load(OUT / ('backup-' + tag) / L)}
    new = {W: load(base / W), L: load(base / L)}
    world_meta = next(o for o in new[W].values() if o.type.name == 'AssetBundle')
    layout_meta = next(o for o in new[L].values() if o.type.name == 'AssetBundle')
    allowed = {W: {HOST, world_meta.path_id}, L: {SET, COMP, layout_meta.path_id}}
    added = {W: {V['page'], V['style'], IC['page'], IC['style']}, L: {V['description']}}
    unchanged = 0
    for bundle in [W, L]:
        assert set(new[bundle]) - set(old[bundle]) == added[bundle]
        assert not set(old[bundle]) - set(new[bundle])
        for pid, obj in old[bundle].items():
            if pid not in allowed[bundle]:
                assert obj.get_raw_data() == new[bundle][pid].get_raw_data(), ('unrelated change', tag, bundle, pid)
                unchanged += 1
    source = old[W][V['source']].read_typetree()
    doc, sheet = new[W][V['page']].read_typetree(), new[W][V['style']].read_typetree()
    rr = refs(doc)
    portrait, iconnode, identity = [named(doc, n) for n in ['ReportPortraitStatusColumn', IC['alias'], 'ReportIdentityColumn']]
    parent = rr[portrait]['data']['m_Parent']['rid']
    assert [x['rid'] for x in rr[parent]['data']['m_Children']] == [portrait, iconnode, identity, 1173]
    assert all(rr[i]['data']['m_Parent']['rid'] == parent for i in [portrait, iconnode, identity, 1173])
    dimension(doc, sheet, portrait, 131105, 226)
    dimension(doc, sheet, portrait, 131087, 250)
    dimension(doc, sheet, iconnode, 131105, 100)
    dimension(doc, sheet, iconnode, 131087, 250)
    for i in [portrait, iconnode, identity]:
        dimension(doc, sheet, i, 131092, 12)
    for i in [identity, 1173]:
        dimension(doc, sheet, i, 131082, 0)
        assert prop(doc, sheet, i, 131084) == [1.0]
    offset = named(doc, 'ReportIdentityOffsetContent')
    for key in [131091, 131092, 131089, 131090]:
        dimension(doc, sheet, offset, key, 0)
    oldrr = refs(source)
    for i in owned_refs(oldrr, 1002):
        assert rr[i] == oldrr[i]
    source_sheet = old[W][source['inlineSheet']['m_PathID']].read_typetree()
    for field in ['m_Rules', 'floats', 'dimensions', 'colors', 'strings', 'assets']:
        assert sheet[field][:len(source_sheet[field])] == source_sheet[field]
    for i, ref in rr.items():
        if ref.get('type', {}).get('class', '').endswith('/UxmlSerializedData') and i != 1165:
            assert ref == oldrr[i]
    assert data(rr, iconnode)['template']['m_PathID'] == IC['page']
    using = next(u for u in doc['m_Usings'] if u['alias'] == IC['alias'])
    assert using['path'] == IC['guid'] and using['asset']['m_PathID'] == IC['page']
    assert not any(u['alias'] == 'MovedHeader_ReportIconsBelowPlayerTopBackground' for u in doc['m_Usings'])
    icon, isheet = new[W][IC['page']].read_typetree(), new[W][IC['style']].read_typetree()
    ir = refs(icon)
    assert ir[1148]['data']['m_Children'] == [{'rid': 1154}, {'rid': 1150}]
    assert prop(icon, isheet, 1148, 131083) == ['column']
    for i in [1154, 1150]:
        dimension(icon, isheet, i, 131087, 50, 2)
    for i in [1158, 1152]:
        dimension(icon, isheet, i, 131105, 100)
        dimension(icon, isheet, i, 131087, 100)
        assert data(ir, i)['scaleMode'] == data(ir, i)['ScaleMode'] == 2
    original_icon = refs(old[W][IC['source']].read_typetree())
    for i, ref in ir.items():
        if ref.get('type', {}).get('class', '').endswith('/UxmlSerializedData'):
            assert ref == original_icon[i], ('icon binding changed', i)
    for d in [doc, icon]:
        refs0 = refs(d)
        seen = set()
        def visit(i):
            assert i not in seen, ('cycle or multiple parents', i)
            seen.add(i)
            for ch in refs0[i]['data'].get('m_Children', []):
                assert refs0[ch['rid']]['data']['m_Parent']['rid'] == i
                visit(ch['rid'])
        visit(d['m_VisualTree']['rid'])
        for i, ref in refs0.items():
            if 'm_Parent' in ref.get('data', {}):
                assert i in seen, ('orphan visual element', i)
            for link in rid_links(ref.get('data', {})):
                assert link == -2 or link in refs0
    # Only appended menu/title/data mappings are permitted in the shared host.
    host, oldhost = new[W][HOST].read_typetree(), old[W][HOST].read_typetree()
    hr, ohr = refs(host), refs(oldhost)
    assert set(hr) == set(ohr)
    for i, ref in hr.items():
        before = ohr[i]
        if before == ref:
            continue
        a, b = before['data'], ref['data']
        if 'ValueVariables' in b:
            assert b['ValueVariables'][-1]['m_name'] == V['title_key']
            b['ValueVariables'] = b['ValueVariables'][:-1]
        elif 'm_Properties' in b:
            for p, op in zip(b['m_Properties'], a['m_Properties']):
                if p != op:
                    assert p['name'] == op['name'] == 'value-vars'
                    assert p['value'] == op['value'] + ',{' + V['title_key'] + '}{String|' + V['title'] + '|}'
            b['m_Properties'] = copy.deepcopy(a['m_Properties'])
        elif 'Bindings' in b:
            for field in ['m_nameBindings', 'm_gridElementBindingData']:
                assert b['Bindings'][field][:len(a['Bindings'][field])] == a['Bindings'][field]
                b['Bindings'][field] = copy.deepcopy(a['Bindings'][field])
        assert ref == before, ('unrelated host change', i)
    assert host == oldhost
    for pid, field in [(SET, 'm_gridElementDescriptions'), (COMP, 'm_placementBindings')]:
        d, od = new[L][pid].read_typetree(), old[L][pid].read_typetree()
        assert len(d[field]) == len(od[field]) + 1
        d[field] = d[field][:-1]
        assert d == od
    choices = [new[L][p['m_PathID']].read_typetree()['<ID>k__BackingField']
               for p in new[L][SET].read_typetree()['m_gridElementDescriptions'] if p['m_FileID'] == 0
               and new[L][p['m_PathID']].read_typetree().get('<ID>k__BackingField', '').startswith('PlayerOverview')]
    assert len(choices) == 7 and choices[-1] == V['ident']
    catfile = (live.parent if tag == 'game' else live) / 'catalog.bin' if installed else base / 'catalog.bin'
    cat = cm.Catalog(catfile.read_bytes())
    assert catfile.with_name('catalog.hash').read_bytes() == hashlib.md5(catfile.read_bytes()).hexdigest().encode('ascii')
    meta = world_meta.read_typetree()
    for v in [V, IC]:
        locations = cat.locations(v['guid'])
        assert len(locations) == 1
        location = cat.location(locations[0])
        assert location['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset'
        assert locations[0] in cat.locations('GameWorldVisualTreeAssetPreload')
        assert cat.location(location['dependencies'][0])['internal'].endswith(W)
        entries = [e for k, e in meta['m_Container'] if k == v['guid']]
        assert len(entries) == 1 and entries[0]['asset']['m_PathID'] == v['page']
        entry = entries[0]
        span = meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']]
        assert {'m_FileID': 0, 'm_PathID': v['style']} in span
        assert {'m_FileID': 0, 'm_PathID': v['page']} in span
        if v == V:
            assert {'m_FileID': 0, 'm_PathID': IC['page']} in span
    results.append(dict(target=tag, choices=choices, unchanged_existing_objects=unchanged,
                        lower_region_and_bindings_equal=True, portrait_and_icon_geometry_checked=True,
                        actual_catalog_and_preload_checked=True))

for row in tx:
    assert sha(Path(row['backup']).read_bytes()) == row['before']
    path = Path(row['target'] if installed else row['source'])
    assert sha(path.read_bytes()) == row['after']
    if path.name.startswith('PlayerReportOverviewComposition'):
        oldcache, cache = json.loads(Path(row['backup']).read_bytes()), json.loads(path.read_bytes())
        cache['m_placementBindings'] = cache['m_placementBindings'][:-1]
        assert cache == oldcache
for path, h in manifest['protected_sha256'].items():
    assert sha(Path(path).read_bytes()) == h
report = dict(passed=True, installed=installed, runtime_verified=False, results=results, verified_files=len(tx))
outpath = OUT / ('verification-installed.json' if installed else 'verification-prepared.json')
outpath.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
if installed:
    index.update(installed=True, installed_verified=True, verification=str(outpath))
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=False))
