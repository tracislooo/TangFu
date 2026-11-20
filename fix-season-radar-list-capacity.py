"""Fix the runtime ten-item StructList limit using two six-point lists."""
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

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

oldwrite = TypeTreeHelper.write_value
for filename, names in [('build-fc-player-hover-layout.py', {'write'}),
                        ('add-card-six-ratings.py', {'check_graph', 'gid'}),
                        ('add-two-portrait-hidden-overviews.py', {'refs', 'data', 'named'})]:
    mod = ast.parse((R / filename).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in mod.body if isinstance(n, ast.FunctionDef) and n.name in names],
                            type_ignores=[]), filename, 'exec'))
TypeTreeHelper.write_value = write
def module(name, filename):
    spec = importlib.util.spec_from_file_location(name, R / filename)
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    return m
rb, cm = module('radar', 'season-radar-builders.py'), module('cat', 'catalog-binary-v35.py')
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
F = 'ui-visualfunctions_assets_all.bundle'
indexpath = R / 'current-player-overview-test-variant.json'
previous = json.loads(indexpath.read_text('utf8'))
m = json.loads(Path(previous['manifest']).read_text('utf8'))
assert previous['installed'] and not m.get('merge'), 'This fix expects the first installed radar revision'
MERGE = -941100000001055
MERGE_KEY = uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-left-test-season-radar-merge-v1').hex
OUT = R / ('season-radar-list-capacity-fix-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
protected = {str(p): sha(p.read_bytes()) for folder in [GAME, SKIN] for p in folder.glob('*.bundle') if p.name not in [W, G]}
fenv = UnityPy.load(str(GAME / F))
functions = {o.peek_name(): o for o in fenv.objects if o.type.name == 'MonoBehaviour'}
templates = {}
for o in functions.values():
    for ref in o.read_typetree().get('references', {}).get('RefIds', []):
        if ref.get('type', {}).get('class'):
            templates.setdefault(ref['type']['class'], ref)
tx = []
def add_tx(tag, path, output, original):
    src, backup = OUT / tag / path.name, OUT / ('backup-' + tag) / path.name
    src.parent.mkdir(exist_ok=True)
    backup.parent.mkdir(exist_ok=True)
    src.write_bytes(output)
    backup.write_bytes(original)
    tx.append(dict(target=str(path), source=str(src), backup=str(backup), before=sha(original), after=sha(output)))

for tag, folder in [('game', GAME), ('skin', SKIN)]:
    print('Preparing ' + tag, flush=True)
    initial = {n: (folder / n).read_bytes() for n in [W, G]}
    env = {n: UnityPy.load(b) for n, b in initial.items()}
    obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
    oldhash = {n: {i: sha(o.get_raw_data()) for i, o in oo.items()} for n, oo in obs.items()}
    modified = {W: {}, G: {}}
    def save(n, pid, doc):
        obs[n][pid].save_typetree(doc)
        modified[n][pid] = copy.deepcopy(doc)
    merge = rb.make_merge_function(functions['BindCreateListToDestination'].read_typetree(), templates,
                                   obs[G][m['function']].read_typetree()['m_Script'])
    check_graph(merge)
    assert MERGE not in obs[G]
    obj = copy.copy(obs[G][m['function']])
    obj.path_id, obj.data, obj._read_until = MERGE, None, None
    obj.assets_file.objects[MERGE] = obj
    obs[G][MERGE] = obj
    for ref in merge['references']['RefIds']:
        assert TypeTreeHelper.get_ref_type_node(ref, obj.assets_file) is not None
    save(G, MERGE, merge)
    stats = obs[W][m['stats']].read_typetree()
    for name in ['SeasonStatsOutfielderPanel', 'SeasonStatsGoalkeeperPanel']:
        rr = refs(stats)
        setter = rr[named(stats, name)]['data']['m_Children'][0]['rid']
        sd = data(rr, setter)
        assert len(sd['BindFunction']) == 13
        original_list_func = sd['BindFunction'].pop()
        list_key = original_list_func['m_target']['m_guid']
        for dest in ['radarPointsFirstHalf', 'radarPointsSecondHalf']:
            sd['ReferenceVariables'].append(dict(m_type={'id': 0}, m_initToNull=1, m_name=dest))
        points = ['seasonRadar' + str(i) + 'Point' for i in range(12)]
        for group, dest in [(points[:6], 'radarPointsFirstHalf'), (points[6:], 'radarPointsSecondHalf')]:
            sd['BindFunction'].append(rb.function(list_key, rb.path_list_arg(group), rb.path_arg(dest)))
        sd['BindFunction'].append(rb.function(MERGE_KEY,
            rb.path_list_arg(['radarPointsFirstHalf', 'radarPointsSecondHalf']), rb.path_arg('radarPoints')))
    save(W, m['stats'], stats)
    gab = next(o for o in obs[G].values() if o.type.name == 'AssetBundle')
    gm = gab.read_typetree()
    source_entry = next(e for k, e in gm['m_Container'] if k == m['function_guid'])
    span = copy.deepcopy(gm['m_PreloadTable'][source_entry['preloadIndex']:source_entry['preloadIndex'] + source_entry['preloadSize']])
    for ptr in span:
        if ptr == {'m_FileID': 0, 'm_PathID': m['function']}:
            ptr['m_PathID'] = MERGE
    if {'m_FileID': 0, 'm_PathID': MERGE} not in span:
        span.append({'m_FileID': 0, 'm_PathID': MERGE})
    gm['m_Container'].append((MERGE_KEY, dict(preloadIndex=len(gm['m_PreloadTable']), preloadSize=len(span),
                                           asset={'m_FileID': 0, 'm_PathID': MERGE})))
    gm['m_PreloadTable'].extend(span)
    gm['m_Container'].sort(key=lambda x: x[0])
    save(G, gab.path_id, gm)
    wab = next(o for o in obs[W].values() if o.type.name == 'AssetBundle')
    wm = wab.read_typetree()
    waf, gaf = obs[W][m['page']].assets_file, obj.assets_file
    global_id = next(i + 1 for i, e in enumerate(waf.externals) if e.path.endswith('/' + gaf.name))
    for key, entry in wm['m_Container']:
        if entry['asset']['m_PathID'] not in [m['page'], m['stats']]:
            continue
        span = copy.deepcopy(wm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex'] + entry['preloadSize']])
        ptr = {'m_FileID': global_id, 'm_PathID': MERGE}
        if ptr not in span:
            span.append(ptr)
        entry['preloadIndex'], entry['preloadSize'] = len(wm['m_PreloadTable']), len(span)
        wm['m_PreloadTable'].extend(span)
    save(W, wab.path_id, wm)
    catpath = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    catbefore, hashbefore = catpath.read_bytes(), catpath.with_name('catalog.hash').read_bytes()
    cat = cm.Catalog(catbefore)
    source_loc, = cat.locations(m['function_guid'])
    cat = cm.Catalog(cat.add_key_location(MERGE_KEY, source_loc, source_loc))
    new_loc, = cat.locations(MERGE_KEY)
    assert cat.location(cat.location(new_loc)['dependencies'][0])['internal'].endswith(G)
    for n, e in env.items():
        output = e.file.save(packer='lz4')
        check = {o.path_id: o for o in UnityPy.load(output).objects}
        assert set(check) == set(obs[n])
        for pid, h in oldhash[n].items():
            if pid not in modified[n]:
                assert sha(check[pid].get_raw_data()) == h, ('unrelated object', tag, n, pid)
        for pid, doc in modified[n].items():
            assert check[pid].read_typetree() == doc, ('roundtrip', tag, n, pid)
        add_tx(tag, folder / n, output, initial[n])
    catout = bytes(cat.data)
    add_tx(tag, catpath, catout, catbefore)
    add_tx(tag, catpath.with_name('catalog.hash'), hashlib.md5(catout).hexdigest().encode('ascii'), hashbefore)
    print('Verified ' + tag + ': native argument lengths 6, 6, 2; output retains all twelve points.', flush=True)
for row in tx:
    assert sha(Path(row['target']).read_bytes()) == row['before']
for p, h in protected.items():
    assert sha(Path(p).read_bytes()) == h
m.update(installed=False, installed_verified=False, runtime_verified=False, merge=MERGE, merge_guid=MERGE_KEY,
         previous_fix_manifest=previous['manifest'], protected_sha256=protected,
         fix='StructList<T> capacity 10: build two six-point lists and flatten them to List<TypedValue>',
         runtime_failure_confirmed=True, runtime_error='Cannot execute visual function BindCreateListToDestination as the inputs are incompatible.')
(OUT / 'manifest.json').write_text(json.dumps(m, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'transaction.json').write_text(json.dumps(tx, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'previous-index.json').write_text(json.dumps(previous, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'installer.py').write_text((R / 'install-independent-resource-patch.py').read_text('utf8').replace('.codex-fitness-', '.codex-radar-fix-'), 'utf8')
for mode, name in [('', 'install.ps1'), (' --restore', 'restore.ps1')]:
    (OUT / name).write_text("$ErrorActionPreference = 'Stop'\n& '" + sys.executable +
        "' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot" + mode +
        "\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n", 'utf-8-sig')
index = dict(previous, manifest=str(OUT / 'manifest.json'), script=str(Path(__file__).resolve()), installed=False,
             installed_verified=False, runtime_verified=False, previous_manifest=previous['manifest'],
             runtime_failure_fixed='split native StructList arguments into 6+6, then merge')
index.pop('verification', None)
indexpath.write_text(json.dumps(index, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(dict(prepared=True, output=str(OUT), files=len(tx)), ensure_ascii=False))
