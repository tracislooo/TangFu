from pathlib import Path
import ast, colorsys, copy, datetime, hashlib, importlib.util, json, struct, subprocess, sys, uuid

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
F = 'ui-tablefactories_assets_all.bundle'
V = 'ui-tableviews_assets_all.bundle'
B = 'ui-backgrounds_assets_common.bundle'
CELL, STYLE = -970000000001000, -970000000001001
HEADER, HEADER_STYLE = -970000000002000, -970000000002001
HEADER_GUID = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/TacticsConditionSharpnessHeader/v1').hex
CELL_GUID = '48ee712ad3785c4a92b20314e4dac8be'
sha = lambda b: hashlib.sha256(b).hexdigest()
OUT = R / ('tactics-combined-condition-sharpness-' + datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
before = {f / n: (f / n).read_bytes() for f in [GAME, SKIN] for n in [W, F, V]}
for n in [W, F, V]:
    assert before[GAME / n] == before[SKIN / n], n
for p in [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', SKIN / 'catalog.bin']:
    before[p] = p.read_bytes()
assert before[GAME.parent / 'catalog.bin'] == before[SKIN / 'catalog.bin']
for p, b in before.items():
    folder = OUT / ('backup-skin' if p.parent == SKIN else 'backup-game')
    folder.mkdir(exist_ok=True)
    (folder / p.name).write_bytes(b)
protected = {p: sha(p.read_bytes()) for f in [GAME, SKIN] for p in f.glob('*.bundle') if p.name not in [W, F, V]}
env = {n: UnityPy.load(before[GAME / n]) for n in [W, F, V]}
obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
hashes = {n: {i: sha(o.get_raw_data()) for i, o in os.items()} for n, os in obs.items()}
expected = {n: {} for n in env}
oldwrite = TypeTreeHelper.write_value
src = ast.parse((R / 'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, ast.FunctionDef) and n.name == 'write'], type_ignores=[]), 'writer', 'exec'))
TypeTreeHelper.write_value = write
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
src = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, ast.ClassDef) and n.name == 'Styles'], type_ignores=[]), 'styles', 'exec'))
src = ast.parse((R / 'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_ui'], type_ignores=[]), 'validator', 'exec'))

def refs(d): return {a['rid']: a for a in d['references']['RefIds']}
def serial(r, i): return r[r[i]['data']['m_SerializedData']['rid']]
def named(r, name):
    ids = [i for i, a in r.items() if a.get('data', {}).get('m_SerializedData', {}).get('rid', -2) != -2 and serial(r, i)['data'].get('name') == name]
    assert len(ids) == 1, (name, ids)
    return ids[0]
def save(n, pid, d):
    obs[n][pid].save_typetree(d)
    expected[n][pid] = copy.deepcopy(d)
def clone(source, pid, d):
    assert pid not in obs[W]
    o = copy.copy(source)
    o.path_id, o.data, o._read_until = pid, None, None
    o.assets_file.objects[pid] = o
    obs[W][pid] = o
    save(W, pid, d)
def decode(raw):
    b, p, result = bytes(raw), 1, []
    for _ in range(b[0]):
        size = struct.unpack_from('<I', b, p)[0]
        p += 4
        result.append(bytearray(b[p:p + size]))
        p += size
    assert p == len(b)
    return result
def encode(args): return list(bytes([len(args)]) + b''.join(struct.pack('<I', len(a)) + a for a in args))
def f32(v): return struct.unpack('<f', struct.pack('<f', float(v)))[0]
def colour(value):
    values = (.45, .47, .50) if value is None else colorsys.hsv_to_rgb(value / 300, .75, .88)
    return dict(zip(['r', 'g', 'b', 'a'], [f32(v) for v in values] + [1.0]))

bge = UnityPy.load(str(GAME / B))
bgo = {o.path_id: o for o in bge.objects}
textures = {o.peek_name(): o.path_id for o in bgo.values() if o.type.name == 'Texture2D' and o.peek_name().startswith('FM27StatusRing')}
fileid = next(i + 1 for i, e in enumerate(obs[W][CELL].assets_file.externals) if e.name.lower() == bge.assets[0].name.lower())
doc = obs[W][CELL].read_typetree()
rr = refs(doc)
sheet = obs[W][STYLE].read_typetree()
st = Styles(sheet)
switchid = named(rr, 'TacticsConditionAbove-1')
textid = named(rr, 'TacticsConditionPercent0')
switchproto, switchsd = copy.deepcopy(rr[switchid]), copy.deepcopy(serial(rr, switchid))
textproto, textsd = copy.deepcopy(rr[textid]), copy.deepcopy(serial(rr, textid))
veproto, vesd = copy.deepcopy(rr[1006]), copy.deepcopy(serial(rr, 1006))
next_rid = max(rr) + 1
next_id = max(a.get('data', {}).get('m_Id', 0) for a in rr.values()) + 1
removed = set()
def remove(i):
    for c in rr[i]['data'].get('m_Children', []): remove(c['rid'])
    removed.update([i, rr[i]['data']['m_SerializedData']['rid']])
for c in rr[1006]['data']['m_Children']: remove(c['rid'])
rr[1006]['data']['m_Children'] = []
for i in removed: rr.pop(i)
doc['references']['RefIds'] = [a for a in doc['references']['RefIds'] if a['rid'] not in removed]

def add(proto, sd, parent, name):
    global next_rid, next_id
    a, s = copy.deepcopy(proto), copy.deepcopy(sd)
    a['rid'], s['rid'] = next_rid, next_rid + 1
    next_rid += 2
    a['data'].update(m_Id=next_id, m_Parent={'rid': parent}, m_Children=[], m_RuleIndex=-1, m_SerializedData={'rid': s['rid']}, m_Classes=[], m_Properties=[])
    s['data'].update(uxmlAssetId=next_id, name=name, name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    next_id += 1
    rr[a['rid']], rr[s['rid']] = a, s
    doc['references']['RefIds'] += [a, s]
    rr[parent]['data']['m_Children'].append({'rid': a['rid']})
    return a['rid']

def absolute(i, x, y, w, h): st.box(rr[i], x, y, w, h)
def stage(i): absolute(i, 0, 0, 100, 24)
st.edit(rr[1001], [st.p(131105, st.pct(100)), st.p(131097, st.px(100)), st.p(131084, st.num(1)), st.p(262150, st.px(0)), st.p(262151, st.px(0))])
st.edit(rr[1002], [st.p(131105, st.pct(100)), st.p(131087, st.pct(100)), st.p(131084, st.num(1)), st.p(131073, st.en('center')), st.p(131088, st.en('center'))])
rr[1006]['data']['m_Classes'] = []
st.edit(rr[1006], [st.p(131105, st.px(100)), st.p(131087, st.px(24)), st.p(131097, st.px(100)), st.p(131096, st.px(24)), st.p(131084, st.num(0)), st.p(131085, st.num(0)), st.p(131102, st.en('relative')), st.p(458768, st.en('visible'))], reset=True)
# Preserve the native condition tooltip over the left half only.
st.edit(rr[1007], [st.p(131102, st.en('absolute')), st.p(131089, st.px(0)), st.p(131104, st.px(0)), st.p(131105, st.pct(50)), st.p(131087, st.pct(100))])
roots, leaves, leafdetails, assethandles = {}, {}, {}, {}
def switch(parent, metric, limit):
    i = add(switchproto, switchsd, parent, f'Combined{metric}Above{limit}')
    stage(i)
    s = serial(rr, i)['data']
    args = decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    struct.pack_into('<i', args[1], len(args[1]) - 4, limit)
    oldpath, newpath = b'player.Condition', ('player.' + metric).encode()
    assert args[2].endswith(bytes([len(oldpath)]) + oldpath)
    args[2][-len(oldpath) - 1:] = bytes([len(newpath)]) + newpath
    s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = encode(args)
    return i
def leaf(parent, metric, value):
    group = add(veproto, vesd, parent, f'Combined{metric}Value{value}')
    stage(group)
    txt = add(textproto, textsd, group, f'Combined{metric}Percent{value}')
    data = serial(rr, txt)['data']
    data.update(text='--' if value is None else f'{value}%', text_UxmlAttributeFlags=1, TextBinding_UxmlAttributeFlags=0, DebugDisplay='')
    data['TextBinding']['m_kind'] = 0
    rr[txt]['data']['m_Classes'] = ['body-md-strong']
    left = metric == 'Condition'
    absolute(txt, 0 if left else 64, 0, 32 if left else 34, 24)
    c = colour(value)
    st.edit(rr[txt], [st.p(65537, st.px(12)), st.p(65543, st.en('bold')), st.p(65546, st.en('middle-right' if left else 'middle-left')), st.p(65552, st.en('nowrap')), st.p(65536, st.h(4, c))])
    ring = add(veproto, vesd, group, f'Combined{metric}Ring{value}')
    absolute(ring, 37 if left else 42, 1 if left else 6, 22 if left else 12, 22 if left else 12)
    texture = textures['FM27StatusRingMissing000' if value is None else f'FM27StatusRingCW{value:03}']
    if texture not in assethandles:
        sheet['assets'].append({'m_FileID': fileid, 'm_PathID': texture})
        assethandles[texture] = {'m_ValueType': 6, 'valueIndex': len(sheet['assets']) - 1}
    st.edit(rr[ring], [st.p(458753, assethandles[texture]), st.p(262153, st.en('scale-to-fit'))])
    leaves[group] = (metric, value)
    leafdetails[group] = {'text': txt, 'ring': ring, 'texture': texture, 'colour': c}
    return group
def tree(parent, metric, lo, hi):
    if lo == hi: return leaf(parent, metric, lo)
    mid = (lo + hi) // 2
    i = switch(parent, metric, mid)
    tree(i, metric, lo, mid)
    tree(i, metric, mid + 1, hi)
    return i
for metric in ['Condition', 'Sharpness']:
    gate = switch(1006, metric, -1)
    roots[metric] = gate
    leaf(gate, metric, None)
    tree(gate, metric, 0, 100)
validate_ui(doc, sheet)
save(W, CELL, doc)
save(W, STYLE, sheet)

# Clone the native sortable header, retaining its button and SortIcon contract.
header_source = obs[W][-7606151087820232286]
headerdoc = header_source.read_typetree()
old_header_sid = headerdoc['inlineSheet']['m_PathID']
headersheet = obs[W][old_header_sid].read_typetree()
headerdoc.update(m_Name='TacticsCombinedConditionSharpnessHeader')
headerdoc['inlineSheet']['m_PathID'] = HEADER_STYLE
headersheet['m_Name'] = 'TacticsCombinedConditionSharpnessHeader_Style'
hr = refs(headerdoc)
hst = Styles(headersheet)
title_id = named(hr, 'text')
title_parent = hr[title_id]['data']['m_Parent']['rid']
title, title_sd = copy.deepcopy(hr[title_id]), copy.deepcopy(serial(hr, title_id))
title['rid'] = max(hr) + 1
title_sd['rid'] = title['rid'] + 1
newid = max(a.get('data', {}).get('m_Id', 0) for a in hr.values()) + 1
title['data'].update(m_Id=newid, m_SerializedData={'rid': title_sd['rid']}, m_RuleIndex=-1, m_Children=[], m_Classes=['table-header-xs', 'global-text-secondary'])
title_sd['data'].update(uxmlAssetId=newid, name='CombinedConditionSharpnessTitle', name_UxmlAttributeFlags=1, text='体能 / 比赛状态', text_UxmlAttributeFlags=1, TextBinding_UxmlAttributeFlags=0, DebugDisplay='', pickingMode=1, pickingMode_UxmlAttributeFlags=1)
title_sd['data']['TextBinding']['m_kind'] = 0
headerdoc['references']['RefIds'] += [title, title_sd]
hr[title_parent]['data']['m_Children'].append({'rid': title['rid']})
hst.edit(hr[title_id], [hst.p(131081, hst.en('none'))])
hst.edit(title, [hst.p(65537, hst.px(10)), hst.p(65552, hst.en('nowrap')), hst.p(131084, hst.num(1)), hst.p(131097, hst.px(0)), hst.p(65546, hst.en('middle-center'))])
validate_ui(headerdoc, headersheet)
clone(header_source, HEADER, headerdoc)
clone(obs[W][old_header_sid], HEADER_STYLE, headersheet)

factory = obs[F][-7014073910555419620].read_typetree()
oldfactory = copy.deepcopy(factory)
col = next(c for c in factory['m_rowData'] if c['m_id'] == 'condition')
assert col['m_uxmlRef']['m_AssetGUID'] == CELL_GUID
col.update(m_defaultWidth=100.0, m_minimumWidth=100.0)
col['m_headerUxmlRef']['m_AssetGUID'] = HEADER_GUID
assert col['m_sortBinding'] == next(c for c in oldfactory['m_rowData'] if c['m_id'] == 'condition')['m_sortBinding']
assert col['m_sortBindingPlugin'] == next(c for c in oldfactory['m_rowData'] if c['m_id'] == 'condition')['m_sortBindingPlugin']
assert sum(a != b for a, b in zip(factory['m_rowData'], oldfactory['m_rowData'])) == 1
save(F, -7014073910555419620, factory)
views = []
for o in obs[V].values():
    if o.type.name != 'MonoBehaviour' or not o.peek_name().startswith('TacticTeamSelection') or 'InMatch' in o.peek_name(): continue
    d = o.read_typetree()
    configs = d.get('m_tableView', {}).get('m_tableConfig', [])
    if not any(c['m_columnID'] == 'condition' for c in configs): continue
    oldview = copy.deepcopy(d)
    for c in configs:
        if c['m_columnID'] == 'condition': c['m_columnMetadata'].update(m_widthOverride=100.0, m_minWidthOverride=100.0)
    d['m_tableView']['m_tableConfig'] = [c for c in configs if c['m_columnID'] != 'sharpness']
    assert [c for c in oldview['m_tableView']['m_tableConfig'] if c['m_columnID'] not in ['condition', 'sharpness']] == [c for c in d['m_tableView']['m_tableConfig'] if c['m_columnID'] != 'condition']
    assert [c['m_columnID'] for c in d['m_tableView']['m_tableConfig']].count('condition') == 1
    assert not any(c['m_columnID'] == 'sharpness' for c in d['m_tableView']['m_tableConfig'])
    save(V, o.path_id, d)
    views.append(d['m_Name'])
assert len(views) == 6

# Register the new header and the existing cell's additional texture dependencies.
metaobj = next(o for o in obs[W].values() if o.type.name == 'AssetBundle')
meta = metaobj.read_typetree()
def pointers(*docs):
    found = []
    def scan(v):
        if isinstance(v, dict):
            if set(v) == {'m_FileID', 'm_PathID'}:
                if v['m_PathID'] and v not in found: found.append(copy.deepcopy(v))
            else:
                for x in v.values(): scan(x)
        elif isinstance(v, list):
            for x in v: scan(x)
    for d in docs: scan(d)
    return found
entry = next(v for k, v in meta['m_Container'] if v['asset']['m_PathID'] == CELL)
span = pointers(doc, sheet) + [{'m_FileID': 0, 'm_PathID': CELL}]
entry.update(preloadIndex=len(meta['m_PreloadTable']), preloadSize=len(span))
meta['m_PreloadTable'].extend(span)
span = pointers(headerdoc, headersheet) + [{'m_FileID': 0, 'm_PathID': HEADER}]
meta['m_Container'].append((HEADER_GUID, {'preloadIndex': len(meta['m_PreloadTable']), 'preloadSize': len(span), 'asset': {'m_FileID': 0, 'm_PathID': HEADER}}))
meta['m_PreloadTable'].extend(span)
meta['m_Container'].sort(key=lambda x: x[0])
save(W, metaobj.path_id, meta)
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
oldcat = cm.Catalog(before[GAME.parent / 'catalog.bin'])
loc = oldcat.locations('23aecb489b191134f8d5da376ca87691')[0]
cat = cm.Catalog(oldcat.add_key_location(HEADER_GUID, loc, loc))
idx = next(i for i, (key, _) in enumerate(cat.keys()) if key == 'GameWorldVisualTreeAssetPreload')
keyobj, locset = cat.key_records[idx]
locs = [a[0] for a in cat.array(locset, 'I')] + cat.locations(HEADER_GUID)
records = list(cat.key_records)
records[idx] = (keyobj, cat.append(b''.join(struct.pack('<I', i) for i in locs), True))
struct.pack_into('<I', cat.data, 8, cat.append(b''.join(struct.pack('<2I', *r) for r in records), True))
catout = bytes(cat.data)
checkcat = cm.Catalog(catout)
newkeys = dict(checkcat.keys())
assert set(newkeys) == set(dict(oldcat.keys())) | {HEADER_GUID}
for key, locset in oldcat.keys():
    oldlocs = [a[0] for a in oldcat.array(locset, 'I')]
    assert [a[0] for a in checkcat.array(newkeys[key], 'I')] == oldlocs + (checkcat.locations(HEADER_GUID) if key == 'GameWorldVisualTreeAssetPreload' else [])
    for loc in oldlocs: assert oldcat.location(loc) == checkcat.location(loc)

# Exercise actual serialized comparisons, bindings, colour handles, and ring assets.
def evaluate(r, root, metric, value):
    i = root
    while r[i]['data']['m_FullTypeName'] == 'SI.Bindable.BindableSwitchElement':
        s = serial(r, i)['data']
        args = decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        path = ('player.' + metric).encode()
        assert args[2].endswith(bytes([len(path)]) + path)
        limit = struct.unpack_from('<i', args[1], len(args[1]) - 4)[0]
        i = r[i]['data']['m_Children'][int(value is not None and value > limit)]['rid']
    return i
def property_value(i, key):
    p = next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id'] == key)
    h = p['m_Values'][0]
    return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]
cases = [None, -2147483648] + list(range(-1, 151))
for metric, root in roots.items():
    for value in cases:
        group = evaluate(rr, root, metric, value)
        percentage = None if value is None or value < 0 else min(100, value)
        assert leaves[group] == (metric, percentage)
        info = leafdetails[group]
        assert serial(rr, info['text'])['data']['text'] == ('--' if percentage is None else f'{percentage}%')
        assert property_value(info['text'], 65536) == colour(percentage)
        assert property_value(info['ring'], 458753) == {'m_FileID': fileid, 'm_PathID': info['texture']}
        assert property_value(info['ring'], 131105)['value'] == (22 if metric == 'Condition' else 12)
for a, b in [(68, 100), (100, 68), (0, 100), (100, 0), (None, 68), (68, None)]:
    assert leaves[evaluate(rr, roots['Condition'], 'Condition', a)] == ('Condition', a)
    assert leaves[evaluate(rr, roots['Sharpness'], 'Sharpness', b)] == ('Sharpness', b)
assert colour(0)['r'] > colour(0)['g'] and colour(100)['g'] > colour(100)['r']
assert len(leaves) == 204

outputs = {n: e.file.save(packer='lz4') for n, e in env.items()}
for n, b in outputs.items():
    check = {o.path_id: o for o in UnityPy.load(b).objects}
    assert check.keys() == obs[n].keys()
    for i, h in hashes[n].items():
        if i not in expected[n]: assert sha(check[i].get_raw_data()) == h, (n, i)
    for i, d in expected[n].items(): assert check[i].read_typetree() == d, (n, i)
    if n == W:
        cr = refs(check[CELL].read_typetree())
        for metric, root in roots.items():
            for value in cases: assert evaluate(cr, root, metric, value) == evaluate(rr, root, metric, value)
    (OUT / n).write_bytes(b)
(OUT / 'cell.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'header.json').write_text(json.dumps(headerdoc, ensure_ascii=False, indent=2), 'utf8')
(OUT / 'catalog.bin').write_bytes(catout)
hashout = hashlib.md5(catout).hexdigest().encode('ascii')
(OUT / 'catalog.hash').write_bytes(hashout)

# A standalone preview uses the same textures, positions, sizes, and colours.
from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('C:/Windows/Fonts/arialbd.ttf', 12 * 4)
examples = [(68, 100), (100, 68), (0, 100), (100, 0), (50, 50), (None, 68)]
preview = Image.new('RGBA', (100 * 4, 24 * 4 * len(examples)), (42, 44, 48, 255))
for row, (a, b) in enumerate(examples):
    for metric, value in [('Condition', a), ('Sharpness', b)]:
        i = evaluate(rr, roots[metric], metric, value)
        info = leafdetails[i]
        left = metric == 'Condition'
        image = bgo[info['texture']].read().image.convert('RGBA')
        size = (22 if left else 12) * 4
        image = image.resize((size, size), Image.Resampling.LANCZOS)
        preview.alpha_composite(image, ((37 if left else 42) * 4, (row * 24 + (1 if left else 6)) * 4))
        text = '--' if value is None else f'{value}%'
        fill = tuple(round(info['colour'][c] * 255) for c in ['r', 'g', 'b']) + (255,)
        draw = ImageDraw.Draw(preview)
        draw.text(((32 if left else 64) * 4, (row * 24 + 12) * 4), text, font=font, fill=fill, anchor='rm' if left else 'lm')
        bbox = draw.textbbox(((32 if left else 64) * 4, (row * 24 + 12) * 4), text, font=font, anchor='rm' if left else 'lm')
        assert bbox[0] >= 0 and bbox[2] <= 100 * 4, (text, bbox)
preview.convert('RGB').save(OUT / 'preview.png')

install = {f / n: b for f in [GAME, SKIN] for n, b in outputs.items()}
install.update({GAME.parent / 'catalog.bin': catout, GAME.parent / 'catalog.hash': hashout, SKIN / 'catalog.bin': catout})
report = {'installed': False, 'runtime_verified': False, 'header': '体能 / 比赛状态', 'column_width': 100,
          'condition': {'binding': 'player.Condition', 'ring': 22, 'text': 'left'},
          'sharpness': {'binding': 'player.Sharpness', 'ring': 12, 'text': 'right'},
          'formula': 'direct UI 0..100 => 0..100%; no subtract-50 or multiply-2',
          'colour': '0% red,50% yellow,100% green; label matches ring', 'missing': '-- and grey ring',
          'independent_metric_cases': 2 * len(cases), 'swapped_and_missing_pairs': 6, 'leaf_count': len(leaves),
          'changed_views': views, 'sort_binding': col['m_sortBinding'], 'sort_plugin': col['m_sortBindingPlugin'],
          'header_guid': HEADER_GUID, 'textures_reused': True, 'avatar_120_percent_preserved': True,
          'changed_objects': {n: list(d) for n, d in expected.items()}, 'after_sha256': {str(p): sha(b) for p, b in install.items()}}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
restore = ['$ErrorActionPreference = "Stop"', "if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
for p in before:
    backup = OUT / ('backup-skin' if p.parent == SKIN else 'backup-game') / p.name
    restore.append("Copy-Item -LiteralPath '" + str(backup) + "' -Destination '" + str(p) + "' -Force")
(OUT / 'restore.ps1').write_text('\n'.join(restore), 'utf-8-sig')
installer = ['$ErrorActionPreference = "Stop"', "if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
for p in before:
    installer.append("if ((Get-FileHash -LiteralPath '" + str(p) + "' -Algorithm SHA256).Hash.ToLower() -ne '" + sha(before[p]) + "') { throw 'Installed files changed; prepare a fresh patch.' }")
for p in install:
    installer.append("Copy-Item -LiteralPath '" + str(OUT / p.name) + "' -Destination '" + str(p) + "' -Force")
(OUT / 'install.ps1').write_text('\n'.join(installer), 'utf-8-sig')
for p, b in before.items(): assert p.read_bytes() == b, ('concurrent change', str(p))
for p, h in protected.items(): assert sha(p.read_bytes()) == h, ('protected file changed', str(p))
proc = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared': True, 'installed': False, 'waiting_for_game_exit': True, 'output': str(OUT)}))
    sys.exit(0)
try:
    for p, b in install.items(): p.write_bytes(b)
    for p, b in install.items(): assert p.read_bytes() == b
    for p, h in protected.items(): assert sha(p.read_bytes()) == h
except BaseException:
    for p, b in before.items(): p.write_bytes(b)
    raise
report.update(installed=True, installed_verified=True)
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'installed': True, 'output': str(OUT), 'independent_metric_cases': report['independent_metric_cases'], 'views': len(views), 'preview': str(OUT / 'preview.png')}))
