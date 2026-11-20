"""Audit the numbered revision against the exact installation baseline."""
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
names = {'refs', 'data', 'named', 'rid_links', 'owned_refs'}
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in names],
                        type_ignores=[]), 'helpers', 'exec'))
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
index_path = R / 'current-player-overview-test-variant.json'
index = json.loads(index_path.read_text('utf8'))
OUT = Path(index['manifest']).parent
m = json.loads((OUT / 'manifest.json').read_text('utf8'))
tx = json.loads((OUT / 'transaction.json').read_text('utf8'))
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
installed = '--installed' in sys.argv
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
P, S, Q, T = m['page'], m['style'], m['selector'], m['selector_style']
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
sha = lambda b: hashlib.sha256(b).hexdigest()


def load(path):
    return {o.path_id: o for o in UnityPy.load(str(path)).objects}


def value(doc, sheet, node, key):
    ix = refs(doc)[node]['data']['m_RuleIndex']
    pp = [p for p in sheet['m_Rules'][ix]['m_Properties'] if p['m_Id'] == key]
    assert len(pp) == 1, (node, key)
    return [sheet[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h
            for h in pp[0]['m_Values']]


def dim(doc, sheet, node, key, number, unit=1):
    assert value(doc, sheet, node, key) == [{'unit': unit, 'value': float(number)}], (node, key)


def graph(doc):
    rr, seen = refs(doc), set()
    def visit(i):
        assert i not in seen, ('cycle/multiple parents', i)
        seen.add(i)
        for ch in rr[i]['data'].get('m_Children', []):
            assert rr[ch['rid']]['data']['m_Parent']['rid'] == i
            visit(ch['rid'])
    visit(doc['m_VisualTree']['rid'])
    for i, ref in rr.items():
        if 'm_Parent' in ref.get('data', {}):
            assert i in seen
        for link in rid_links(ref.get('data', {})):
            assert link == -2 or link in rr


results = []
for tag, live in [('game', Path(loc['bundle_root'])), ('skin', Path(loc['skin_packages']))]:
    base = live if installed else OUT / tag
    old, new = {}, {}
    for n in [W, G]:
        old[n], new[n] = load(OUT / ('backup-' + tag) / n), load(base / n)
    meta = {n: next(o for o in new[n].values() if o.type.name == 'AssetBundle') for n in [W, G]}
    allowed = {W: {P, S, meta[W].path_id}, G: {meta[G].path_id}}
    unchanged = 0
    for n in [W, G]:
        assert not set(old[n]) - set(new[n])
        assert set(new[n]) - set(old[n]) == ({Q, T} if n == G else set())
        for pid, obj in old[n].items():
            if pid not in allowed[n]:
                assert new[n][pid].get_raw_data() == obj.get_raw_data(), ('unrelated object', tag, n, pid)
                unchanged += 1
    d, s = new[W][P].read_typetree(), new[W][S].read_typetree()
    od, os = old[W][P].read_typetree(), old[W][S].read_typetree()
    r, before = refs(d), refs(od)
    graph(d)
    # The portrait, icon and identity regions retain their complete geometry and data.
    for root in [6736, 1163, 1291]:
        for i in owned_refs(before, root):
            assert r[i] == before[i], ('header identity changed', i)
    for field in ['m_Rules', 'floats', 'dimensions', 'colors', 'strings', 'assets']:
        assert s[field][:len(os[field])] == os[field]
    context = named(d, 'LeftTestStatisticsContext')
    assert [c['rid'] for c in r[1002]['data']['m_Children']][:3] == [context, 1009, 1703]
    assert r[1173]['data']['m_Children'] == [{'rid': 1026}, {'rid': 5852}]
    assert value(d, s, 1173, 131083) == ['row']
    assert r[1703]['data']['m_Children'] == [{'rid': 1007}, {'rid': 6298}]
    assert r[5852]['data']['m_Parent']['rid'] == 1173
    assert value(d, s, 6298, 131102) == ['absolute']
    dim(d, s, 6298, 131089, 35, 2)
    dim(d, s, 6298, 131105, 65, 2)
    dim(d, s, 6298, 131080, 0)
    dim(d, s, 6298, 131087, 217)
    dim(d, s, context, 131105, 240)
    dim(d, s, context, 131092, 4)
    dim(d, s, 1009, 131097, 480)
    dim(d, s, 1009, 131095, 640)
    dim(d, s, 1703, 131097, 480)
    # Original visual functions, events, mappings and attribute values are byte-for-byte
    # equivalent in every surviving serialized node, except the private template target.
    template_sd = r[1007]['data']['m_SerializedData']['rid']
    count = 0
    for i, ref in r.items():
        if i in before and ref.get('type', {}).get('class', '').endswith('/UxmlSerializedData') and i != template_sd:
            assert ref == before[i], ('changed binding', i)
            count += 1
    leaf = context
    for src in [1116, 1118, 1119, 1166, 1167]:
        a, b = copy.deepcopy(data(r, leaf)), copy.deepcopy(data(before, src))
        for k in ['uxmlAssetId', 'name', 'name_UxmlAttributeFlags']:
            a.pop(k, None)
            b.pop(k, None)
        assert a == b, ('statistics binding context changed', src)
        if src != 1167:
            leaf = r[leaf]['data']['m_Children'][0]['rid']
    assert r[leaf]['data']['m_Children'] == [{'rid': 1186}, {'rid': 6286}, {'rid': 2242}]
    q, t = new[G][Q].read_typetree(), new[G][T].read_typetree()
    oq = old[G][m['selector_source']].read_typetree()
    qr, oqr = refs(q), refs(oq)
    graph(q)
    assert q['m_ContentContainerId'] == qr[2008]['data']['m_Id'] == oq['m_ContentContainerId']
    assert set(qr) == set(oqr)
    for i, ref in qr.items():
        if ref.get('type', {}).get('class', '').endswith('/UxmlSerializedData'):
            assert ref == oqr[i], ('selector event/selection changed', i)
    assert qr[1007]['data']['m_Children'] == [{'rid': 2000}, {'rid': 2002}]
    assert qr[2002]['data']['m_Children'] == [{'rid': 2010}, {'rid': 2006}]
    assert value(q, t, 2002, 131083) == ['row']
    dim(q, t, 2000, 131105, 35, 2)
    dim(q, t, 2002, 131105, 65, 2)
    dim(q, t, 2002, 131087, 200)
    assert r[6228]['data']['m_Parent']['rid'] == 1007
    assert r[6228]['data']['m_Children'] == [{'rid': 1035}]
    # The right-column split reserves 8px between 5/6 and 9 at the unchanged body height.
    dim(d, s, 1002, 131087, 425)
    assert 425 - 217 - 200 == 8
    for width in [1280, 1632, 1920]:
        available = width - 240 - 4 - 8
        assert available >= 480 + 480, ('minimum widths overflow', width)
    use = next(u for u in d['m_Usings'] if u['alias'] == 'LeftTestPitchRolesComparison')
    assert use['path'] == m['selector_guid'] and use['asset']['m_PathID'] == Q
    assert data(r, 1007)['template'] == use['asset']
    assert new[W][P].assets_file.externals[use['asset']['m_FileID'] - 1].path.endswith('/' + new[G][Q].assets_file.name)
    catfile = (live.parent if tag == 'game' else live) / 'catalog.bin' if installed else base / 'catalog.bin'
    cat, oldcat = cm.Catalog(catfile.read_bytes()), cm.Catalog((OUT / ('backup-' + tag) / 'catalog.bin').read_bytes())
    assert len(cat.key_records) == len(oldcat.key_records) + 1
    current_keys = set(cat.keys())
    for key, locations in oldcat.keys():
        if key == 'GlobalVisualTreeAssetPreload':
            assert cat.locations(key)[:-1] == [x[0] for x in oldcat.array(locations, 'I')]
        else:
            assert (key, locations) in current_keys
    qm = meta[G].read_typetree()
    entry = next(e for key, e in qm['m_Container'] if key == m['selector_guid'])
    assert entry['asset']['m_PathID'] == Q
    location, = cat.locations(m['selector_guid'])
    assert cat.location(location)['internal'] == m['selector_guid']
    assert cat.location(location)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset'
    assert location in cat.locations('GlobalVisualTreeAssetPreload')
    assert cat.location(cat.location(location)['dependencies'][0])['internal'].endswith(G)
    wm = meta[W].read_typetree()
    page_key, entry = next((key, e) for key, e in wm['m_Container'] if e['asset']['m_PathID'] == P)
    span = wm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']]
    assert use['asset'] in span
    page_loc, = cat.locations(page_key)
    assert set(cat.location(location)['dependencies']) <= set(cat.location(page_loc)['dependencies'])
    assert catfile.with_name('catalog.hash').read_bytes() == hashlib.md5(catfile.read_bytes()).hexdigest().encode('ascii')
    results.append(dict(target=tag, unchanged_existing_objects=unchanged,
                        preserved_main_serialized_nodes=count, selector_bindings_and_slot_identical=True,
                        statistics_context_preserved=True, topology_and_catalog_passed=True))

for row in tx:
    assert sha(Path(row['backup']).read_bytes()) == row['before']
    assert sha(Path(row['target'] if installed else row['source']).read_bytes()) == row['after']
for path, digest in m['protected_sha256'].items():
    assert sha(Path(path).read_bytes()) == digest
report = dict(passed=True, installed=installed, runtime_verified=False, verified_files=len(tx), results=results)
report_path = OUT / ('verification-installed.json' if installed else 'verification-prepared.json')
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
if installed:
    index.update(installed=True, installed_verified=True, verification=str(report_path))
    index_path.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=False))
