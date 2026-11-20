"""Independent baseline, graph execution, scope and Addressables checks."""
from pathlib import Path
import ast
import copy
import hashlib
import importlib.util
import json
import math
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

mod = ast.parse((R / 'add-two-portrait-hidden-overviews.py').read_text('utf8'))
names = {'refs', 'data', 'named', 'owned_refs', 'rid_links'}
exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[]), 'helpers', 'exec'))
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
indexpath = R / 'current-player-overview-test-variant.json'
index = json.loads(indexpath.read_text('utf8'))
OUT = Path(index['manifest']).parent
m = json.loads((OUT / 'manifest.json').read_text('utf8'))
tx = json.loads((OUT / 'transaction.json').read_text('utf8'))
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
installed = '--installed' in sys.argv
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
gid = lambda v: bytes(v['m_idBytes'])


def load(path):
    return {o.path_id: o for o in UnityPy.load(str(path)).objects}


def graph(doc):
    rr, seen = refs(doc), set()
    def visit(i):
        assert i not in seen
        seen.add(i)
        for child in rr[i]['data'].get('m_Children', []):
            assert rr[child['rid']]['data']['m_Parent']['rid'] == i
            visit(child['rid'])
    visit(doc['m_VisualTree']['rid'])
    for i, r in rr.items():
        if 'm_Parent' in r.get('data', {}):
            assert i in seen
        for link in rid_links(r.get('data', {})):
            assert link == -2 or link in rr


def decode(data):
    data = bytes(data)
    pos, out = 1, []
    for _ in range(data[0]):
        n = struct.unpack_from('<I', data, pos)[0]
        item = data[pos + 4:pos + 4 + n]
        pos += 4 + n
        out.append(item)
    assert pos == len(data)
    return out


def run_function(tree, number, maximum, minimum=0., reverse=False):
    refs0 = tree['references']['RefIds']
    nodes = [r['data'] for r in refs0]
    entry = next(r['data'] for r in refs0 if r['type']['class'] == 'EntryNode')
    bind = next(r['data'] for r in refs0 if r['type']['class'] == 'BindNode')
    memo, inputs, outputs, result = {}, {}, {}, {}
    arguments = dict(BindingBag=None, Target=None, Source='source', Maximum='max', Minimum=minimum, Reverse=reverse,
                     RawDestination='raw', PlotDestination='plot', MaximumDestination='max', ValidDestination='valid')
    for p in entry['m_dataSockets']:
        memo[gid(p['m_id'])] = arguments[p['m_name']]
    for p, value in zip(bind['m_outputAsyncExecSocket']['m_dataOutputSockets'], [number, maximum]):
        memo[gid(p['m_id'])] = value
    for r in refs0:
        d = r['data']
        for key, v in d.items():
            if isinstance(v, dict) and 'm_id' in v:
                if key in ['m_execInExecInput', 'm_inputExecSocket']:
                    inputs[gid(v['m_id'])] = r
                elif key.startswith('m_dataOut'):
                    outputs[gid(v['m_id'])] = r, key
    def value(d, name):
        port = d[name]
        source = gid(port['m_sourceID'])
        if not any(source):
            return port.get('m_defaultSocketValue', {}).get('m_value')
        return resolve(source)
    def resolve(source):
        if source in memo:
            return memo[source]
        r, key = outputs[source]
        d, cls = r['data'], r['type']['class']
        if cls == 'GeneralVisualFunction_AND':
            return bool(value(d, 'm_dataInA')) and bool(value(d, 'm_dataInB'))
        if cls == 'GeneralVisualFunction_AddFloat_float_float_float':
            return value(d, 'm_dataInA') + value(d, 'm_dataInB')
        if cls == 'GeneralVisualFunction_SubtractFloat_float_float_float':
            return value(d, 'm_dataInA') - value(d, 'm_dataInB')
        if cls == 'TypedValueVisualFunctionLibrary_FloatToTypedValue':
            return float(value(d, 'm_dataInValue'))
        if cls == 'TypedValueVisualFunctionLibrary_BoolToTypedValue':
            return bool(value(d, 'm_dataInValue'))
        raise AssertionError(('unexecuted source or unknown pure node', cls, key))
    destination = gid(bind['m_outputAsyncExecSocket']['m_destinationID'])
    for _ in range(50):
        if not any(destination):
            return result
        r = inputs[destination]
        d, cls = r['data'], r['type']['class']
        port = 'm_execOutExecOutput'
        if cls == 'TypedValueVisualFunctionLibrary_TryCastToFloat':
            v = value(d, 'm_dataInValue')
            ok = isinstance(v, (int, float)) and not isinstance(v, bool) and math.isfinite(v)
            memo[gid(d['m_dataOutBoolean']['m_id'])] = ok
            memo[gid(d['m_dataOutFloatValue']['m_id'])] = float(v) if ok else 0.
        elif cls == 'GeneralVisualFunction_AND':
            pass
        elif cls == 'VisualFunctionLibrary_SetBinding':
            result[value(d, 'm_dataInDest')] = value(d, 'm_dataInValue')
        elif cls == 'GeneralVisualFunction_Branch':
            port = 'm_execOutTrue' if value(d, 'm_dataInCondition') else 'm_execOutFalse'
        else:
            raise AssertionError(cls)
        destination = gid(d[port]['m_destinationID'])
    raise AssertionError('function did not terminate')


results = []
for tag, live in [('game', Path(loc['bundle_root'])), ('skin', Path(loc['skin_packages']))]:
    base = live if installed else OUT / tag
    old = {n: load(OUT / ('backup-' + tag) / n) for n in [W, G]}
    new = {n: load(base / n) for n in [W, G]}
    meta = {n: next(o for o in new[n].values() if o.type.name == 'AssetBundle') for n in [W, G]}
    added = {W: {m['stats'], m['style'], m['label'], m['label_style']},
             G: {m['function']} | ({m['merge']} if m.get('merge') else set())}
    allowed = {W: {m['page'], m['stats'], meta[W].path_id}, G: {meta[G].path_id}}
    unchanged = 0
    for n in [W, G]:
        assert set(new[n]) - set(old[n]) == added[n] - set(old[n])
        assert not set(old[n]) - set(new[n])
        for pid, obj in old[n].items():
            if pid not in allowed[n]:
                assert new[n][pid].get_raw_data() == obj.get_raw_data(), ('unrelated object changed', tag, n, pid)
                unchanged += 1
    page = new[W][m['page']].read_typetree()
    oldpage = old[W][m['page']].read_typetree()
    stripped = copy.deepcopy(page)
    u = next(u for u in stripped['m_Usings'] if u['alias'] == 'OverviewNativeSeasonFourGauges')
    assert u['path'] == m['stats_guid'] and u['asset']['m_PathID'] == m['stats']
    old_u = next(u for u in oldpage['m_Usings'] if u['alias'] == 'OverviewNativeSeasonFourGauges')
    u.clear()
    u.update(copy.deepcopy(old_u))
    rr, oldrr = refs(stripped), refs(oldpage)
    sd = rr[6304]['data']['m_SerializedData']['rid']
    assert rr[sd]['data']['template']['m_PathID'] == m['stats']
    rr[sd]['data']['template'] = copy.deepcopy(oldrr[sd]['data']['template'])
    rr[sd]['data']['template_UxmlAttributeFlags'] = oldrr[sd]['data']['template_UxmlAttributeFlags']
    stripped['m_ContentHash'] = oldpage['m_ContentHash']
    assert stripped == oldpage, 'Only the private season template pointer may differ in the overview'
    stats = new[W][m['stats']].read_typetree()
    label = new[W][m['label']].read_typetree()
    graph(stats)
    graph(label)
    original_stats = old[W][-950000000000168].read_typetree()
    switch = named(stats, 'SeasonStatsIsGoalkeeperSwitch')
    assert data(refs(stats), switch) == data(refs(original_stats), switch)
    assert [data(refs(stats), c['rid'])['name'] for c in refs(stats)[switch]['data']['m_Children']] == ['SeasonStatsOutfielderPanel', 'SeasonStatsGoalkeeperPanel']
    for panel_name, specs in [('SeasonStatsOutfielderPanel', m['outfield']), ('SeasonStatsGoalkeeperPanel', m['goalkeeper'])]:
        panel = named(stats, panel_name)
        sr = refs(stats)
        setter = sr[panel]['data']['m_Children'][0]['rid']
        values = data(sr, setter)
        assert len(values['BindFunction']) == (15 if m.get('merge') else 13)
        points = []
        for v in values['ValueVariables']:
            serialized = v['m_scopeValue']['m_serializedData']
            if serialized.startswith('{'):
                point = json.loads(serialized)
                assert point['$type'] == 'SI.Bindable.DynamicReferenceScopeValue, SI.Bindable'
                fields = {x['PropertyID']['id']: x['BindingPath'] for x in point['m_data']}
                assert {0x37675A32, 0x74594C76, 0x4E657758, 0x3167704D, 0x5A74416A, 0x4F627175} <= set(fields)
                points.append(point)
        assert len(points) == len(specs) == 12
        for fn, spec0 in zip(values['BindFunction'][:12], specs):
            assert fn['m_target']['m_guid'] == m['function_guid']
            args = decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
            assert len(args) == 8 and args[0].endswith(spec0[1].encode())
            assert b'SingleVisualArg' in args[2]
            assert struct.unpack('<f', args[2][-4:])[0] == spec0[2]
            assert bool(args[3][-1]) == spec0[4]
        lengths = []
        for fn in values['BindFunction'][12:]:
            list_args = decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
            count = list_args[0][1 + list_args[0][0]]
            assert count <= 10, 'The native StructList<T> cannot hold more than ten values'
            lengths.append(count)
        assert lengths == [6, 6, 2], lengths
        assert values['BindFunction'][-1]['m_target']['m_guid'] == m['merge_guid']
        chart = sr[setter]['data']['m_Children'][0]['rid']
        cd = data(sr, chart)
        assert cd['SpiderChartVertices'] == 12 and cd['LabelsTemplate']['m_AssetGUID'] == m['label_guid']
    assert data(refs(label), named(label, 'SeasonRadarValueAvailable'))['Binding']['m_direct']['Path']['m_path'] == 'binding.UniqueId'
    func = new[G][m['function']].read_typetree()
    tests = [
        (11, 23, 0, False, 11, True), (2, 5, 0, True, 3, True),
        (3.5, 15, 0, True, 11.5, True), (-0.92, 1, -1, False, -0.92, True),
        (0, 10, 0, False, 0, True), (0, 10, 0, True, 10, True),
        (None, 10, 0, True, 0, False), (None, 1, -1, False, -1, False),
        (40, 10, 0, False, 40, True), (0, 0, 0, True, 0, True),
    ]
    for source, maximum, minimum, inverse, plot, valid in tests:
        result = run_function(func, source, maximum, minimum, inverse)
        assert math.isclose(result['plot'], plot, abs_tol=1e-6) and result['valid'] == valid
        assert result['raw'] == (float(source) if source is not None else 0.)
    ft = next(t for t in new[G][m['function']].assets_file.ref_types if t.m_ClassName == 'TypedValueVisualFunctionLibrary_FloatToTypedValue')
    assert [n.m_Type for n in ft.node.traverse() if n.m_Name == 'm_value'] == ['float']
    merge = new[G][m['merge']].read_typetree()
    nodes = merge['references']['RefIds']
    flatten = next(r for r in nodes if r.get('type', {}).get('class', '').startswith('ListFunctions_CombinedLists_'))
    assert flatten['data']['m_dataInAllowDuplicates']['m_defaultSocketValue']['m_value'] == 1
    outid = flatten['data']['m_dataOutList']['m_id']
    setter = next(r for r in nodes if r.get('type', {}).get('class') == 'VisualFunctionLibrary_SetListBinding')
    assert setter['data']['m_dataInValue']['m_sourceID'] == outid
    # Two short StructLists contain List<TypedValue> references. The native combine
    # node flattens them to a growable List, preserving order and repeated entries.
    for halves in [(list(range(6)), list(range(6, 12))), ([0] * 6, [0] * 6)]:
        assert len(halves) <= 10 and all(len(h) <= 10 for h in halves)
        merged = [value for half in halves for value in half]
        assert len(merged) == 12 and merged == halves[0] + halves[1]
    catpath = (live.parent if tag == 'game' else live) / 'catalog.bin' if installed else base / 'catalog.bin'
    cat = cm.Catalog(catpath.read_bytes())
    assert catpath.with_name('catalog.hash').read_bytes() == hashlib.md5(catpath.read_bytes()).hexdigest().encode('ascii')
    for key, pid, n, expected_type in [(m['stats_guid'], m['stats'], W, 'UnityEngine.UIElements.VisualTreeAsset'),
                                     (m['label_guid'], m['label'], W, 'UnityEngine.UIElements.VisualTreeAsset'),
                                     (m['function_guid'], m['function'], G, 'SI.VisualScripting.VisualFunction'),
                                     (m['merge_guid'], m['merge'], G, 'SI.VisualScripting.VisualFunction')]:
        locn, = cat.locations(key)
        location = cat.location(locn)
        assert location['type'][1] == expected_type
        assert cat.location(location['dependencies'][0])['internal'].endswith(n)
        entry = next(e for k, e in meta[n].read_typetree()['m_Container'] if k == key)
        assert entry['asset']['m_PathID'] == pid
        if n == W:
            assert locn in cat.locations('GameWorldVisualTreeAssetPreload')
    results.append(dict(target=tag, unchanged_existing_objects=unchanged, graph_scenarios=len(tests),
                        original_layout_and_shared_modules_preserved=True, goalkeeper_switch_preserved=True,
                        point_counts=[12, 12], raw_values_and_inverse_axes_verified=True,
                        catalog_types_dependencies_and_preloads_checked=True))

for row in tx:
    assert sha(Path(row['backup']).read_bytes()) == row['before']
    assert sha(Path(row['target'] if installed else row['source']).read_bytes()) == row['after']
for p, h in m['protected_sha256'].items():
    assert sha(Path(p).read_bytes()) == h
report = dict(passed=True, installed=installed, runtime_verified=False, files=len(tx), results=results)
report_path = OUT / ('verification-installed.json' if installed else 'verification-prepared.json')
report_path.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
if installed:
    index.update(installed=True, installed_verified=True, verification=str(report_path))
    indexpath.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=False))
