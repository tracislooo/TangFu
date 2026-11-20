"""Replace the crashing merged list with two deferred, independent six-axis charts."""
from pathlib import Path
import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import struct
import sys
import zlib

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite = TypeTreeHelper.write_value
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
for filename, names in [('build-fc-player-hover-layout.py', {'write', 'Styles'}),
                        ('add-card-six-ratings.py', {'validate_ui'}),
                        ('add-two-portrait-hidden-overviews.py', {'refs', 'data', 'named', 'rid_links', 'owned_refs'})]:
    mod = ast.parse((R / filename).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names],
                            type_ignores=[]), filename, 'exec'))
TypeTreeHelper.write_value = write
def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, R / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
rb, cm = module('radar', 'season-radar-builders.py'), module('catalog', 'catalog-binary-v35.py')
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
W, G = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle', 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
indexpath = R / 'current-player-overview-test-variant.json'
previous = json.loads(indexpath.read_text('utf8'))
manifest = json.loads(Path(previous['manifest']).read_text('utf8'))
assert previous['installed'] and manifest.get('merge')
MERGE, MERGE_KEY = manifest['merge'], manifest['merge_guid']
OUT = R / ('season-two-six-axis-radars-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
protected = {str(p): sha(p.read_bytes()) for folder in [GAME, SKIN] for p in folder.glob('*.bundle') if p.name not in [W, G]}
tx, audits = [], []
def add_tx(tag, path, output, original):
    src, backup = OUT / tag / path.name, OUT / ('backup-' + tag) / path.name
    src.parent.mkdir(exist_ok=True)
    backup.parent.mkdir(exist_ok=True)
    src.write_bytes(output)
    backup.write_bytes(original)
    tx.append(dict(target=str(path), source=str(src), backup=str(backup), before=sha(original), after=sha(output)))

def add_node(doc, prototype, parent, name):
    rr = refs(doc)
    node, sd = copy.deepcopy(prototype)
    rid = max(rr) + 1
    ident = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
    assert ident < 2147483647
    node['rid'], sd['rid'] = rid, rid + 1
    node['data'].update(m_Id=ident, m_Parent={'rid': parent}, m_Children=[], m_RuleIndex=-1,
                        m_Classes=[], m_Stylesheets=[], m_SerializedData={'rid': rid + 1})
    sd['data'].update(uxmlAssetId=ident, name=name, name_UxmlAttributeFlags=1)
    doc['references']['RefIds'].extend([node, sd])
    rr[parent]['data']['m_Children'].append({'rid': rid})
    return rid

def graph(doc):
    rr, seen = refs(doc), set()
    def walk(i):
        assert i not in seen
        seen.add(i)
        for ch in rr[i]['data'].get('m_Children', []):
            assert rr[ch['rid']]['data']['m_Parent']['rid'] == i
            walk(ch['rid'])
    walk(doc['m_VisualTree']['rid'])
    for i, r in rr.items():
        if 'm_Parent' in r.get('data', {}):
            assert i in seen
        for link in rid_links(r.get('data', {})):
            assert link == -2 or link in rr

for tag, folder in [('game', GAME), ('skin', SKIN)]:
    print('Preparing ' + tag, flush=True)
    before = {n: (folder / n).read_bytes() for n in [W, G]}
    env = {n: UnityPy.load(b) for n, b in before.items()}
    obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
    oldhash = {n: {i: sha(o.get_raw_data()) for i, o in oo.items()} for n, oo in obs.items()}
    modified = {W: {}, G: {}}
    def save(n, pid, doc):
        obs[n][pid].save_typetree(doc)
        modified[n][pid] = copy.deepcopy(doc)
    doc = obs[W][manifest['stats']].read_typetree()
    olddoc = copy.deepcopy(doc)
    sheet = obs[W][manifest['style']].read_typetree()
    st = Styles(sheet)
    main = obs[W][manifest['page']].read_typetree()
    mr = refs(main)
    plain = (copy.deepcopy(mr[1291]), copy.deepcopy(mr[mr[1291]['data']['m_SerializedData']['rid']]))
    rr = refs(doc)
    sw = named(doc, 'SeasonStatsIsGoalkeeperSwitch')
    switch_proto = (copy.deepcopy(rr[sw]), copy.deepcopy(rr[rr[sw]['data']['m_SerializedData']['rid']]))
    def fill(width):
        return [st.p(131105, width), st.p(131087, st.pct(100)), st.p(131097, st.px(0)),
                st.p(131096, st.px(0)), st.p(131082, st.px(0)), st.p(131084, st.num(1)),
                st.p(131085, st.num(1)), st.p(131073, st.en('stretch'))]
    for panel_name in ['SeasonStatsOutfielderPanel', 'SeasonStatsGoalkeeperPanel']:
        rr = refs(doc)
        panel = named(doc, panel_name)
        setter = rr[panel]['data']['m_Children'][0]['rid']
        sd = data(rr, setter)
        assert len(sd['BindFunction']) == 15 and sd['BindFunction'][-1]['m_target']['m_guid'] == MERGE_KEY
        sd['BindFunction'].pop()
        sd['ReferenceVariables'] = [v for v in sd['ReferenceVariables'] if v['m_name'] != 'radarPoints']
        chart, = [c['rid'] for c in rr[setter]['data']['m_Children']]
        chart_proto = (copy.deepcopy(rr[chart]), copy.deepcopy(rr[rr[chart]['data']['m_SerializedData']['rid']]))
        rr[setter]['data']['m_Children'].remove({'rid': chart})
        row = add_node(doc, plain, setter, 'SeasonRadarTwoChartsRow')
        rr = refs(doc)
        st.edit(rr[row], fill(st.pct(100)) + [st.p(131083, st.en('row'))], reset=True)
        for position, path in [('First', 'radarPointsFirstHalf'), ('Second', 'radarPointsSecondHalf')]:
            gate = add_node(doc, switch_proto, row, 'SeasonRadarReady_' + position)
            rr = refs(doc)
            gs = data(rr, gate)
            gs['Binding'] = dict(m_kind=2, m_direct={'Path': {'m_path': ''}, 'Nullable': 0},
                m_visualFunction=rb.function('a4dffe7b331c90949b43d2d4e3155117', rb.path_arg(path)))
            gs['Binding_UxmlAttributeFlags'] = 1
            st.edit(rr[gate], fill(st.px(0)), reset=True)
            waiting = add_node(doc, plain, gate, 'SeasonRadarWaiting_' + position)
            rr = refs(doc)
            st.edit(rr[waiting], fill(st.pct(100)), reset=True)
            if position == 'First':
                rr[chart]['data']['m_Parent'] = {'rid': gate}
                rr[gate]['data']['m_Children'].append({'rid': chart})
                current = chart
            else:
                current = add_node(doc, chart_proto, gate, 'SeasonRadarSixAxes_' + position)
                rr = refs(doc)
            cs = data(rr, current)
            cs.update(name='SeasonRadarSixAxes_' + position, SpiderChartVertices=6,
                      SpiderChartVertices_UxmlAttributeFlags=1, SpiderChartRadiusPercentage=24.,
                      LabelDistanceFromChart=8.)
            target = cs['BindDataFunction']['m_target']['m_guid']
            cs['BindDataFunction'] = rb.function(target, rb.path_arg(path), rb.bool_arg(False),
                                                rb.bool_arg(False), rb.path_arg('radarZero'))
            st.edit(rr[current], fill(st.pct(100)), reset=True)
    doc.update(m_Name='LeftTestSeasonTwoSixAxisRadars',
               m_ContentHash=struct.unpack('<i', struct.pack('<I', zlib.crc32(b'left-test-two-six-axis-radars-v1')))[0])
    graph(doc)
    validate_ui(doc, sheet)
    assert data(refs(doc), sw) == data(refs(olddoc), sw)
    save(W, manifest['stats'], doc)
    save(W, manifest['style'], sheet)
    label = obs[W][manifest['label']].read_typetree()
    ls = obs[W][manifest['label_style']].read_typetree()
    lst, lr = Styles(ls), refs(label)
    root = named(label, 'SeasonRadarAxisLabel')
    lst.edit(lr[root], [lst.p(131105, lst.px(46)), lst.p(131087, lst.px(20))])
    for i, r in lr.items():
        if r.get('data', {}).get('m_FullTypeName') == 'SI.Bindable.SIText':
            lst.edit(r, [lst.p(65537, lst.px(7)), lst.p(131087, lst.px(10))])
    validate_ui(label, ls)
    save(W, manifest['label_style'], ls)
    global_file = obs[G][MERGE].assets_file
    del global_file.objects[MERGE]
    obs[G].pop(MERGE)
    waf = obs[W][manifest['page']].assets_file
    global_id = next(i + 1 for i, e in enumerate(waf.externals) if e.path.endswith('/' + global_file.name))
    # Rebuild spans so no active or orphan preload entry points to the removed merge function.
    for n in [W, G]:
        ab = next(o for o in obs[n].values() if o.type.name == 'AssetBundle')
        meta = ab.read_typetree()
        if n == G:
            meta['m_Container'] = [(k, e) for k, e in meta['m_Container'] if k != MERGE_KEY]
        oldtable, table = meta['m_PreloadTable'], []
        entries = [e for _, e in meta['m_Container']]
        if isinstance(meta.get('m_MainAsset'), dict) and 'preloadIndex' in meta['m_MainAsset']:
            entries.append(meta['m_MainAsset'])
        for e in entries:
            span = copy.deepcopy(oldtable[e['preloadIndex']:e['preloadIndex'] + e['preloadSize']])
            span = [p for p in span if p != {'m_FileID': 0 if n == G else global_id, 'm_PathID': MERGE}]
            e['preloadIndex'], e['preloadSize'] = len(table), len(span)
            table.extend(span)
        meta['m_PreloadTable'] = table
        save(n, ab.path_id, meta)
    catpath = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    catbefore, hashbefore = catpath.read_bytes(), catpath.with_name('catalog.hash').read_bytes()
    cat = cm.Catalog(catbefore)
    removed_loc, = cat.locations(MERGE_KEY)
    records = []
    for key, locset in cat.key_records:
        if cat.object(key) == MERGE_KEY:
            continue
        locations = [x[0] for x in cat.array(locset, 'I')]
        if removed_loc in locations:
            locations.remove(removed_loc)
            locset = cat.append(b''.join(struct.pack('<I', x) for x in locations), True)
        records.append((key, locset))
    struct.pack_into('<I', cat.data, 8, cat.append(b''.join(struct.pack('<2I', *r) for r in records), True))
    cat = cm.Catalog(bytes(cat.data))
    assert MERGE_KEY not in {k for k, _ in cat.keys()}
    for n, e in env.items():
        output = e.file.save(packer='lz4')
        check = {o.path_id: o for o in UnityPy.load(output).objects}
        assert set(check) == set(obs[n])
        for pid, h in oldhash[n].items():
            if pid == MERGE and n == G:
                assert pid not in check
            elif pid not in modified[n]:
                assert sha(check[pid].get_raw_data()) == h, ('unrelated object changed', tag, n, pid)
        for pid, expected in modified[n].items():
            assert check[pid].read_typetree() == expected, ('roundtrip', tag, n, pid)
        add_tx(tag, folder / n, output, before[n])
    catout = bytes(cat.data)
    add_tx(tag, catpath, catout, catbefore)
    add_tx(tag, catpath.with_name('catalog.hash'), hashlib.md5(catout).hexdigest().encode('ascii'), hashbefore)
    audits.append(dict(target=tag, six_axes_per_chart=6, charts_per_branch=2,
                       deferred_until_list_has_items=True, merge_function_and_preloads_removed=True))
    print('Verified ' + tag + ': independent six-axis charts; empty-list creation guarded.', flush=True)
for row in tx:
    assert sha(Path(row['target']).read_bytes()) == row['before']
for p, h in protected.items():
    assert sha(Path(p).read_bytes()) == h
manifest.update(installed=False, installed_verified=False, runtime_verified=False,
                previous_fix_manifest=previous['manifest'], protected_sha256=protected,
                removed_merge=MERGE, removed_merge_guid=MERGE_KEY, charts_per_branch=2, axes_per_chart=6,
                deferred_until_list_has_items=True, audits=audits,
                runtime_error='NullReferenceException in ConvertToListOfTypedValue; guard chart creation until its list has items')
manifest.pop('merge', None)
manifest.pop('merge_guid', None)
(OUT / 'manifest.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'previous-index.json').write_text(json.dumps(previous, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'installer.py').write_text((R / 'install-independent-resource-patch.py').read_text('utf8').replace('.codex-fitness-', '.codex-two-radars-'), 'utf8')
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT / name).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable +
        "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + mode +
        "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n", 'utf-8-sig')
index = dict(previous, manifest=str(OUT / 'manifest.json'), script=str(Path(__file__).resolve()), installed=False,
             installed_verified=False, runtime_verified=False, previous_manifest=previous['manifest'],
             layout='original seventh layout; two guarded six-axis season radars',
             runtime_failure_fixed='remove list merger; defer each chart until its own six-item list is available')
index.pop('verification', None)
indexpath.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(dict(prepared=True, output=str(OUT), files=len(tx)), ensure_ascii=False))
