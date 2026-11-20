"""Add the current profile pitch to all three player popup paths.

Rebuild against the currently installed bundles; do not execute old installers.
"""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys, uuid

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
PITCH, STYLE = -960000000003030, -960000000003031
NAME = 'TooltipVerticalPositionPitch'
GUID = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/TooltipVerticalPositionPitch/v1').hex
SOURCE = -940000000010020
sha = lambda b: hashlib.sha256(b).hexdigest()
f32 = lambda v: struct.unpack('<f', struct.pack('<f', float(v)))[0]

before = {p / n: (p / n).read_bytes() for p in [GAME, SKIN] for n in [W, G]}
for n in [W, G]:
    assert before[GAME / n] == before[SKIN / n], ('Game/skin mismatch', n)
for p in [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', SKIN / 'catalog.bin']:
    before[p] = p.read_bytes()
assert before[GAME.parent / 'catalog.bin'] == before[SKIN / 'catalog.bin']
protected = {GAME / n: sha((GAME / n).read_bytes()) for n in ['ui-tileslayouts_assets_all.bundle', 'ui-styles_assets_default.bundle']}
env = {n: UnityPy.load(before[GAME / n]) for n in [W, G]}
obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
hashes = {n: {i: sha(o.get_raw_data()) for i, o in os.items()} for n, os in obs.items()}
expected = {W: {}, G: {}}
oldwrite = TypeTreeHelper.write_value
helpers = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n, ast.FunctionDef) and n.name == 'write'
                             or isinstance(n, ast.ClassDef) and n.name == 'Styles'], type_ignores=[]), '<helpers>', 'exec'))
TypeTreeHelper.write_value = write
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}

def refs(d): return {r['rid']: r for r in d['references']['RefIds']}
def serial(rs, i): return rs[rs[i]['data']['m_SerializedData']['rid']]['data']
def named(bundle, name):
    found = [o for o in obs[bundle].values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name]
    assert len(found) == 1, (name, len(found))
    return found[0]
def save(bundle, o, d):
    o.save_typetree(d)
    expected[bundle][o.path_id] = copy.deepcopy(d)
def clone(bundle, source, pid, d):
    assert pid not in obs[bundle]
    o = copy.copy(source)
    o.path_id, o.data, o._read_until = pid, None, None
    o.assets_file.objects[pid] = o
    save(bundle, o, d)
    return o
def managed_ids(v, include_parent=False):
    if isinstance(v, dict):
        if set(v) == {'rid'}:
            if v['rid'] != -2: yield v['rid']
        else:
            for k, x in v.items():
                if k != 'm_Parent' or include_parent: yield from managed_ids(x, include_parent)
    elif isinstance(v, list):
        for x in v: yield from managed_ids(x, include_parent)
def node_by_name(rs, name):
    found = [r for r in rs.values() if rs.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == name]
    assert len(found) == 1, (name, len(found))
    return found[0]
def prop_value(sheet, node, key):
    ps = sheet['m_Rules'][node['data']['m_RuleIndex']]['m_Properties']
    p = next((p for p in ps if p['m_Id'] == key), None)
    if p is None: return None
    h = p['m_Values'][0]
    return sheet['dimensions'][h['valueIndex']]['value'] if h['m_ValueType'] == 3 else None

# Profile source: keep its actual fitter, hidden native hit layer, image and all fourteen zones.
source = obs[G][SOURCE]
pitch = source.read_typetree()
original_pitch = copy.deepcopy(pitch)
rs = refs(pitch)
style_source = obs[G][pitch['inlineSheet']['m_PathID']]
sheet = style_source.read_typetree()
st = Styles(sheet)
component_sd = serial(rs, 1001)
component_for_node = {}
for c in component_sd['m_components']:
    data = rs[c['rid']]['data']
    node = next(r for r in rs.values() if r.get('data', {}).get('m_Id') == data['uxmlAssetId'])
    component_for_node[node['rid']] = c['rid']
assert set([1002, 1003, 1005, 1006]) <= set(component_for_node)
expect = rs[component_for_node[1002]]['data']
expect['Parameters'] = [p for p in expect['Parameters'] if p['name'] == 'person']
assert len(expect['Parameters']) == 1
rs[1002]['data']['m_Properties'] = [{'name': 'params', 'value': 'person:person:False'}]
variables = rs[component_for_node[1006]]['data']
variables['ValueVariables'] = [{'m_name': 'positionmask', 'm_scopeValue': {'m_serializedData': 'Int|0|'}}]
variables['ReferenceVariables'] = [{'m_type': {'id': 1313106539}, 'm_initToNull': 1, 'm_name': 'rolemask'}]
variables['ValueVariables_UxmlAttributeFlags'] = variables['ReferenceVariables_UxmlAttributeFlags'] = 1
rs[1006]['data']['m_Properties'] = [
    {'name': 'value-vars', 'value': '{positionmask}{Int|0|}'},
    {'name': 'reference-vars', 'value': 'rolemask:roleabilityrow:True'}]
mapper = rs[component_for_node[1005]]['data']
mapper['Mappings'] = [m for m in mapper['Mappings'] if m['from'] in ['player', 'selectedPositionMask']]
rs[1005]['data']['m_Properties'] = []
order = [1002, 1006, 1003, 1005]
component_sd['m_components'] = [{'rid': component_for_node[i]} for i in order]
rs[1001]['data']['m_Children'] = [{'rid': i} for i in order + [2014]]
rs[1001]['data']['m_Classes'] = []
rs[2014]['data']['m_Parent'] = {'rid': 1001}
for j, i in enumerate(order): rs[i]['data']['m_OrderInDocument'] = j
ratio = serial(rs, 2014)['AspectRatio']
assert abs(ratio - .7) < 1e-6
height = f32(200 / ratio)
top = f32((596 - height) / 2)
st.edit(rs[1001], [st.p(131105, st.px(200)), st.p(131087, st.px(596)), st.p(131097, st.px(200)),
                   st.p(131096, st.px(0)), st.p(131084, st.num(0)), st.p(131085, st.num(0)),
                   st.p(262150, st.px(0)), st.p(262151, st.px(0)),
                   st.p(458752, st.h(4, {'r': 0., 'g': 0., 'b': 0., 'a': 0.}))], reset=True)
st.box(rs[2014], 0, top, 200, height)
for i in [1022, 1023, 2018]: assert rs[i]['data']['m_Parent'] == {'rid': 2014}
keep, todo = {-2}, [1000]
while todo:
    i = todo.pop()
    if i in keep: continue
    keep.add(i)
    todo.extend(managed_ids(rs[i].get('data', {})))
pitch['references']['RefIds'] = [r for r in pitch['references']['RefIds'] if r['rid'] in keep]
pitch['m_Name'] = NAME
pitch['inlineSheet'] = {'m_FileID': 0, 'm_PathID': STYLE}
pitch['m_ContentHash'] = struct.unpack('<i', bytes.fromhex(GUID[:8]))[0]
pitch['m_ContentContainerId'] = 0
sheet['m_Name'] = NAME + '_Style'
# Filter unused templates while preserving any direct custom references.
aliases = {r.get('data', {}).get('m_TemplateAlias') for r in pitch['references']['RefIds']} - {None}
pitch['m_Usings'] = [u for u in pitch['m_Usings'] if u['alias'] in aliases]
assert {rs[i]['data']['m_FullTypeName'] for i in [1022, 1023, 2018]} == {'SI.Bindable.SIImage', 'FM.UI.FMTacticsPanel', 'SI.Bindable.WrappedObjectList'}
assert not any('StreamedTable' in r['type']['class'] for r in pitch['references']['RefIds'])
clone(G, source, PITCH, pitch)
clone(G, style_source, STYLE, sheet)

# Every popup owns a copied fixed content region; update all three explicitly.
regions = {
    'Fixed_PlayerHeader': (626, 12, 744, 64),
    'Fixed_SmallAttributes': (626, 88, 744, 380),
    'Fixed_CoachScoutReport': (626, 480, 292, 128),
    'Fixed_PlayerMood': (930, 480, 146, 128),
    'Fixed_PlayerPosition': (1088, 480, 282, 128),
    'RightPanelBackground': (626, 12, 744, 596),
}
routes = []
for index, name in enumerate(['PlayerReportPreviewTooltip', 'PlayerCellInMatch', 'MatchPlayerReport']):
    o = named(W, name)
    d = o.read_typetree()
    rr = refs(d)
    so = obs[W][d['inlineSheet']['m_PathID']]
    s = so.read_typetree()
    styles = Styles(s)
    root_name = 'MatchClickPlayerReportFCLayout' if name == 'MatchPlayerReport' else 'FixedPlayerPreview1280x620'
    root = node_by_name(rr, root_name)
    assert prop_value(s, root, 131105) == 1280 and prop_value(s, root, 131087) == 620
    # Extend the click report shell and safe area too, preserving their existing heights.
    width_updates = 0
    for r in list(rr.values()):
        a = r.get('data', {})
        if a.get('m_RuleIndex', -1) < 0: continue
        props = []
        for key in [131105, 131097, 131095]:
            if prop_value(s, r, key) == 1280: props.append(styles.p(key, styles.px(1392)))
        if props:
            styles.edit(r, props)
            width_updates += 1
    serial(rr, root['rid'])['name'] = 'MatchClickPlayerReportFCPitchLayout' if name == 'MatchPlayerReport' else 'FixedPlayerPreview1392x620'
    for key, (x, y, w, h) in regions.items():
        n = node_by_name(rr, key)
        styles.box(n, x, y, w, h)
        styles.edit(n, [styles.p(131095, styles.px(w)), styles.p(131094, styles.px(h))])
    prototype = next(r for r in rr.values() if r.get('data', {}).get('m_TemplateAlias') == 'FCPlayerCard')
    prototype_sd = rr[prototype['data']['m_SerializedData']['rid']]
    a, b = copy.deepcopy(prototype), copy.deepcopy(prototype_sd)
    a['rid'], b['rid'] = 120000, 120001
    assert a['rid'] not in rr and b['rid'] not in rr
    eid = 1990000000 + index
    a['data'].update(m_Id=eid, m_Parent={'rid': root['rid']}, m_Children=[], m_SerializedData={'rid': b['rid']},
                     m_RuleIndex=-1, m_Classes=[], m_TemplateAlias='VerticalPositionPitch',
                     m_AttributeOverrides=[], m_SerializedDataOverride=[], m_SlotUsages=[])
    b['data'].update(uxmlAssetId=eid, name='Fixed_VerticalPositionPitch', name_UxmlAttributeFlags=1,
                     templateId='VerticalPositionPitch', templateId_UxmlAttributeFlags=1, template={'m_FileID': 0, 'm_PathID': 0})
    styles.box(a, 414, 12, 200, 596)
    styles.edit(a, [styles.p(131095, styles.px(200)), styles.p(131094, styles.px(596)),
                    styles.p(458752, styles.h(4, {'r': 0., 'g': 0., 'b': 0., 'a': 0.}))])
    rr[a['rid']], rr[b['rid']] = a, b
    root['data']['m_Children'].append({'rid': a['rid']})
    d['m_Usings'].append({'alias': 'VerticalPositionPitch', 'path': GUID, 'asset': {'m_FileID': 0, 'm_PathID': 0}})
    d['references']['RefIds'] = list(rr.values())
    save(W, o, d)
    save(W, so, s)
    routes.append({'asset': name, 'width_nodes_updated': width_updates, 'content_size': [1392, 620]})

# Register the independent pitch and its style in the global bundle and Addressables.
bundle = next(o for o in obs[G].values() if o.type.name == 'AssetBundle')
metadata = bundle.read_typetree()
source_guid = next(k for k, v in metadata['m_Container'] if v['asset'] == {'m_FileID': 0, 'm_PathID': SOURCE})
def pointers(v):
    if isinstance(v, dict):
        if set(v) == {'m_FileID', 'm_PathID'}:
            if v['m_PathID']: yield v
        else:
            for x in v.values(): yield from pointers(x)
    elif isinstance(v, list):
        for x in v: yield from pointers(x)
span = []
for p in list(pointers(pitch)) + list(pointers(sheet)) + [{'m_FileID': 0, 'm_PathID': PITCH}]:
    if p not in span: span.append(copy.deepcopy(p))
metadata['m_Container'].append((GUID, {'preloadIndex': len(metadata['m_PreloadTable']), 'preloadSize': len(span),
                                      'asset': {'m_FileID': 0, 'm_PathID': PITCH}}))
metadata['m_PreloadTable'].extend(span)
metadata['m_Container'].sort(key=lambda entry: entry[0])
save(G, bundle, metadata)
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
oldcat = cm.Catalog(before[GAME.parent / 'catalog.bin'])
assert GUID not in dict(oldcat.keys())
base_loc = oldcat.locations(source_guid)[0]
assert oldcat.location(oldcat.location(base_loc)['dependencies'][0])['internal'].replace('\\', '/').endswith('/' + G)
cat = cm.Catalog(oldcat.add_key_location(GUID, base_loc, base_loc))
label = 'GlobalVisualTreeAssetPreload'
idx = next(i for i, (k, _) in enumerate(cat.keys()) if k == label)
keyobj, locset = cat.key_records[idx]
locs = [p[0] for p in cat.array(locset, 'I')] + cat.locations(GUID)
records = list(cat.key_records)
records[idx] = (keyobj, cat.append(b''.join(struct.pack('<I', p) for p in locs), True))
struct.pack_into('<I', cat.data, 8, cat.append(b''.join(struct.pack('<2I', *r) for r in records), True))
catout = bytes(cat.data)
cat = cm.Catalog(catout)
newkeys = dict(cat.keys())
custom_locations = cat.locations(GUID)
assert set(newkeys) == set(dict(oldcat.keys())) | {GUID}
for key, locset in oldcat.keys():
    oldlocs = [p[0] for p in oldcat.array(locset, 'I')]
    newlocs = [p[0] for p in cat.array(newkeys[key], 'I')]
    assert newlocs == oldlocs + (custom_locations if key == label else [])
    for loc in oldlocs: assert oldcat.location(loc) == cat.location(loc)

def validate_ui(d, s):
    rr = refs(d)
    assert len(rr) == len(d['references']['RefIds'])
    seen, eids = set(), set()
    def visit(i):
        assert i not in seen
        seen.add(i)
        a = rr[i]['data']
        assert a['m_Id'] not in eids
        eids.add(a['m_Id'])
        for child in a.get('m_Children', []):
            assert rr[child['rid']]['data']['m_Parent']['rid'] == i
            visit(child['rid'])
    visit(d['m_VisualTree']['rid'])
    for r in rr.values():
        a = r.get('data', {})
        if 'm_Parent' in a: assert r['rid'] in seen
        for i in managed_ids(a, True): assert i in rr
        sd = a.get('m_SerializedData', {}).get('rid', -2)
        if sd != -2: assert rr[sd]['data']['uxmlAssetId'] == a['m_Id']
        if a.get('m_RuleIndex', -1) >= 0: assert a['m_RuleIndex'] < len(s['m_Rules'])
        if a.get('m_TemplateAlias'):
            assert a['m_TemplateAlias'] in {u['alias'] for u in d['m_Usings']}
            assert rr[sd]['data']['templateId'] == a['m_TemplateAlias']
    for rule in s['m_Rules']:
        for p in rule['m_Properties']:
            for h in p['m_Values']:
                if h['m_ValueType'] in poolmap: assert h['valueIndex'] < len(s[poolmap[h['m_ValueType']]])
validate_ui(pitch, sheet)
for name in ['PlayerReportPreviewTooltip', 'PlayerCellInMatch', 'MatchPlayerReport']:
    o = named(W, name)
    d = expected[W][o.path_id]
    validate_ui(d, expected[W][d['inlineSheet']['m_PathID']])
    rr = refs(d)
    s = expected[W][d['inlineSheet']['m_PathID']]
    ns = ['Fixed_FCPlayerCard', 'Fixed_VerticalPositionPitch'] + [k for k in regions if k != 'RightPanelBackground']
    boxes = []
    for n in ns:
        node = node_by_name(rr, n)
        x, y, w, h = [prop_value(s, node, p) for p in [131089, 131104, 131105, 131087]]
        assert x >= 0 and y >= 0 and x + w <= 1392 and y + h <= 620
        boxes.append((x, y, w, h))
    for i, (x, y, w, h) in enumerate(boxes):
        for xx, yy, ww, hh in boxes[i+1:]:
            assert x + w <= xx or xx + ww <= x or y + h <= yy or yy + hh <= y

outputs = {n: e.file.save(packer='lz4') for n, e in env.items()}
verified = {}
for n, b in outputs.items():
    check = {o.path_id: o for o in UnityPy.load(b).objects}
    assert set(check) == set(obs[n]) | set(expected[n])
    for i, o in check.items():
        if i in expected[n]: assert json.dumps(o.read_typetree(), sort_keys=True) == json.dumps(expected[n][i], sort_keys=True), (n, i)
        else: assert sha(o.get_raw_data()) == hashes[n][i], (n, i)
    verified[n] = len(check) - len(expected[n])
assert SOURCE not in expected[G]
assert style_source.path_id not in expected[G]
assert -960000000003010 not in expected[W], 'FC card content changed'
assert -960000000003020 not in expected[G], 'Shared SMALL content changed'
for p, h in protected.items(): assert sha(p.read_bytes()) == h

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out = R / ('player-popups-vertical-pitch-' + stamp)
out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag)
    backup.mkdir()
    for n in [W, G]: (backup / n).write_bytes(before[folder / n])
    p = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    (backup / 'catalog.bin').write_bytes(before[p])
(out / 'backup-game' / 'catalog.hash').write_bytes(before[GAME.parent / 'catalog.hash'])
for n, b in outputs.items(): (out / n).write_bytes(b)
(out / 'pitch.json').write_text(json.dumps(pitch, ensure_ascii=False, indent=2), 'utf8')
(out / 'catalog.bin').write_bytes(catout)
hashout = hashlib.md5(catout).hexdigest().encode('ascii')
(out / 'catalog.hash').write_bytes(hashout)
install = {p / n: b for p in [GAME, SKIN] for n, b in outputs.items()}
install.update({GAME.parent / 'catalog.bin': catout, SKIN / 'catalog.bin': catout, GAME.parent / 'catalog.hash': hashout})
for p, b in before.items(): assert p.read_bytes() == b, ('Concurrent change', str(p))
try:
    for p, b in install.items(): p.write_bytes(b)
    for p, b in install.items(): assert p.read_bytes() == b
except BaseException:
    for p in install: p.write_bytes(before[p])
    raise
report = {'installed': True, 'runtime_verified': False, 'output': str(out), 'size': [1392, 620], 'right_width': 744,
          'pitch_guid': GUID, 'pitch_asset': NAME, 'pitch_source': source.peek_name(), 'pitch_source_unchanged': True,
          'pitch_render_size': [200, height], 'pitch_vertical_offset_in_region': top, 'pitch_state': 'private local positionmask and rolemask',
          'routes': routes, 'regions': regions, 'unrelated_assets_verified': verified,
          'after_sha256': {str(p): sha(b) for p, b in install.items()}}
(out / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=True, indent=2))
