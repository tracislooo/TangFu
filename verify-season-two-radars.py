"""Check independent chart lists, lazy null guards and removal of the merger."""
from pathlib import Path
import ast
import hashlib
import importlib.util
import json
import struct
import sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
mod = ast.parse((R / 'add-two-portrait-hidden-overviews.py').read_text('utf8'))
names = {'refs', 'data', 'named'}
exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[]), 'helpers', 'exec'))
spec = importlib.util.spec_from_file_location('cat', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
indexpath = R / 'current-player-overview-test-variant.json'
idx = json.loads(indexpath.read_text('utf8'))
OUT = Path(idx['manifest']).parent
m = json.loads((OUT / 'manifest.json').read_text('utf8'))
tx = json.loads((OUT / 'transaction.json').read_text('utf8'))
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
installed = '--installed' in sys.argv
W, G = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle', 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
sha = lambda b: hashlib.sha256(b).hexdigest()
def load(p):
    return {o.path_id: o for o in UnityPy.load(str(p)).objects}
def args(fn):
    b = bytes(fn['m_inputs']['m_variable']['m_argumentBytes'])
    pos, out = 1, []
    for _ in range(b[0]):
        n = struct.unpack_from('<I', b, pos)[0]
        out.append(b[pos + 4:pos + 4 + n])
        pos += 4 + n
    assert pos == len(b)
    return out
results = []
for tag, live in [('game', Path(loc['bundle_root'])), ('skin', Path(loc['skin_packages']))]:
    base = live if installed else OUT / tag
    old = {n: load(OUT / ('backup-' + tag) / n) for n in [W, G]}
    new = {n: load(base / n) for n in [W, G]}
    unchanged = 0
    for n in [W, G]:
        ab = next(o for o in new[n].values() if o.type.name == 'AssetBundle')
        changed = {ab.path_id} | ({m['stats'], m['style'], m['label_style']} if n == W else set())
        assert set(new[n]) == set(old[n]) - ({m['removed_merge']} if n == G else set())
        for pid, o in old[n].items():
            if pid not in changed and not (n == G and pid == m['removed_merge']):
                assert o.get_raw_data() == new[n][pid].get_raw_data(), ('unrelated change', tag, n, pid)
                unchanged += 1
        meta = ab.read_typetree()
        assert not any(p['m_PathID'] == m['removed_merge'] for p in meta['m_PreloadTable'])
    doc, previous = new[W][m['stats']].read_typetree(), old[W][m['stats']].read_typetree()
    r, pr = refs(doc), refs(previous)
    sw = named(doc, 'SeasonStatsIsGoalkeeperSwitch')
    assert data(r, sw) == data(pr, sw)
    for panel in ['SeasonStatsOutfielderPanel', 'SeasonStatsGoalkeeperPanel']:
        p = named(doc, panel)
        setter = r[p]['data']['m_Children'][0]['rid']
        sd, oldsd = data(r, setter), data(pr, setter)
        assert sd['BindFunction'] == oldsd['BindFunction'][:-1]
        assert len(sd['BindFunction']) == 14
        assert sd['ValueVariables'] == oldsd['ValueVariables']
        assert sd['ReferenceVariables'] == [v for v in oldsd['ReferenceVariables'] if v['m_name'] != 'radarPoints']
        row = r[setter]['data']['m_Children'][0]['rid']
        gates = r[row]['data']['m_Children']
        assert len(gates) == 2
        for gate, path in zip(gates, ['radarPointsFirstHalf', 'radarPointsSecondHalf']):
            a = data(r, gate['rid'])
            fn = a['Binding']['m_visualFunction']
            assert fn['m_target']['m_guid'] == 'a4dffe7b331c90949b43d2d4e3155117'
            assert args(fn)[0].endswith(path.encode())
            empty, chart = r[gate['rid']]['data']['m_Children']
            assert r[empty['rid']]['data']['m_Children'] == []
            chartdata = data(r, chart['rid'])
            assert chartdata['SpiderChartVertices'] == 6
            assert args(chartdata['BindDataFunction'])[0].endswith(path.encode())
            assert chartdata['LabelsTemplate']['m_AssetGUID'] == m['label_guid']
        for fn in sd['BindFunction'][12:]:
            first = args(fn)[0]
            assert first[1 + first[0]] == 6
    catpath = (live.parent if tag == 'game' else live) / 'catalog.bin' if installed else base / 'catalog.bin'
    cat, oldcat = cm.Catalog(catpath.read_bytes()), cm.Catalog((OUT / ('backup-' + tag) / 'catalog.bin').read_bytes())
    assert catpath.with_name('catalog.hash').read_bytes() == hashlib.md5(catpath.read_bytes()).hexdigest().encode('ascii')
    keys = set(cat.keys())
    assert len(cat.key_records) == len(oldcat.key_records) - 1
    for key, locations in oldcat.keys():
        if key != m['removed_merge_guid']:
            assert (key, locations) in keys
    assert not any(key == m['removed_merge_guid'] for key, _ in keys)
    for key in [m['stats_guid'], m['label_guid']]:
        locn, = cat.locations(key)
        assert locn in cat.locations('GameWorldVisualTreeAssetPreload')
    results.append(dict(target=tag, charts_per_branch=2, vertices_per_chart=6,
                        empty_list_defers_chart_creation=True, merged_function_removed=True,
                        original_data_bindings_unchanged=True, unchanged_objects=unchanged))
for row in tx:
    assert sha(Path(row['backup']).read_bytes()) == row['before']
    assert sha(Path(row['target'] if installed else row['source']).read_bytes()) == row['after']
for path, h in m['protected_sha256'].items():
    assert sha(Path(path).read_bytes()) == h
report = dict(passed=True, installed=installed, runtime_verified=False, files=len(tx), results=results)
p = OUT / ('verification-installed.json' if installed else 'verification-prepared.json')
p.write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
if installed:
    idx.update(installed=True, installed_verified=True, verification=str(p))
    indexpath.write_text(json.dumps(idx, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=False))
