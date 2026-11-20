"""Scoped, reversible Combined pitch card trial; no new bundle objects or textures."""
from pathlib import Path
import ast, copy, colorsys, datetime, hashlib, importlib.util, json, struct, subprocess, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PID = 3127595210179668386
stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
OUT = R / ('tactics-combined-layered-card-trial-' + stamp)
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
before = {folder / W: (folder / W).read_bytes() for folder in [GAME, SKIN]}
assert len({sha(b) for b in before.values()}) == 1, 'World bundles differ; patch each separately first.'
for path, raw in before.items():
    directory = OUT / ('backup-game' if path.parent == GAME else 'backup-skin')
    directory.mkdir()
    (directory / W).write_bytes(raw)

protected_names = ['ui-tablefactories_assets_all.bundle', 'ui-tableviews_assets_all.bundle',
                   'ui-backgrounds_assets_common.bundle', 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',
                   'ui-styles_assets_default.bundle', 'ui-styles_assets_common.bundle']
protected_paths = [f / n for f in [GAME, SKIN] for n in protected_names]
protected_paths += [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', SKIN / 'catalog.bin', SKIN / 'catalog.hash']
protected = {p: sha(p.read_bytes()) for p in protected_paths if p.exists()}

def extract(file, names, kinds=(ast.FunctionDef, ast.ClassDef)):
    parsed = ast.parse((R / file).read_text('utf-8-sig'))
    exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n, kinds) and n.name in names],
                            type_ignores=[]), file, 'exec'), globals())

oldwrite = TypeTreeHelper.write_value
extract('redesign-card-top-info-foot.py', {'write'})
TypeTreeHelper.write_value = write
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
extract('build-fc-player-hover-layout.py', {'Styles'})
extract('combine-tactics-condition-sharpness.py', {'decode', 'encode', 'f32', 'colour'})
extract('add-card-six-ratings.py', {'validate_ui'})

source_raw = Path(sys.argv[2]).read_bytes() if len(sys.argv) == 3 and sys.argv[1] == '--base' else before[GAME / W]
if source_raw != before[GAME / W]:
    (OUT / 'backup-original').mkdir()
    (OUT / 'backup-original' / W).write_bytes(source_raw)
env = UnityPy.load(source_raw)
objs = {o.path_id: o for o in env.objects}
hashes = {pid: sha(o.get_raw_data()) for pid, o in objs.items()}
d = objs[PID].read_typetree()
assert d['m_Name'] == 'TacticsPositionCombined'
SID = d['inlineSheet']['m_PathID']
sheet = objs[SID].read_typetree()

def refs(doc): return {a['rid']: a for a in doc['references']['RefIds']}
def serial(r, i): return r[r[i]['data']['m_SerializedData']['rid']]

extract('add-pitch-condition-complexity-columns.py', {'Tree'})
t = Tree(d, sheet)
original = copy.deepcopy(t.r)
st = t.st
P = st.p

def box(i, x, y, w, h):
    st.box(t.r[i], x, y, w, h)
    # Cancel inherited/class right/bottom offsets as well as fixed min/max sizes.
    t.edit(i, [P(131103, {'m_ValueType': 1, 'valueIndex': 3}),
               P(131080, {'m_ValueType': 1, 'valueIndex': 3})])

def rounded(i, radius, clip=False):
    t.edit(i, [P(262147, st.px(radius)), P(458768, st.en('hidden' if clip else 'visible'))])

def ignore(i): t.sd(i).update(pickingMode=1, pickingMode_UxmlAttributeFlags=1)

def add_ve(parent, name):
    i = t.add(t.r, 1165, parent, name)
    t.r[i]['data'].update(m_Classes=[], m_Properties=[])
    ignore(i)
    return i

def move(i, parent):
    old = t.r[i]['data']['m_Parent']['rid']
    t.r[old]['data']['m_Children'].remove({'rid': i})
    t.r[i]['data']['m_Parent'] = {'rid': parent}
    t.r[parent]['data']['m_Children'].append({'rid': i})

# Keep the pitch anchor / footprint 80x70. The portrait extends above the anchor,
# just as the native shirt did; the name and ability row remain beneath the card.
frame = 1165
gate = 1171
fitness_root = 1173
box(1001, 0, 0, 80, 70)
t.edit(1001, [P(131102, st.en('relative'))])
box(1016, 0, 0, 80, 70)
t.edit(1016, [P(131102, st.en('relative')), P(458768, st.en('visible'))])
box(1018, 0, -56, 80, 86)
box(1021, 0, 0, 80, 86)
box(frame, 0, 0, 80, 86)
rounded(frame, 8)

# Reuse the native position-colour function with ColourOnly mode. It returns
# native position palette classes without importing their original row geometry.
border = t.add(t.r, 1075, frame, 'CombinedCardNativePositionBackground')
t.r[border]['data'].update(m_Classes=[], m_Properties=[])
ignore(border)
fn = t.sd(border)['BindFunction']
args = decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
assert args[3].endswith(b'\x05Style')
args[3][-6:] = b'\x0aColourOnly'
# The original footer applies the palette class to its child remapper. This
# new bottom layer has no child; apply the class to the setter itself instead.
assert args[6][-1] == 1
args[6][-1] = 0
fn['m_inputs']['m_variable']['m_argumentBytes'] = encode(args)
box(border, 0, 0, 80, 86)
rounded(border, 8, True)

surface = add_ve(frame, 'CombinedCardInnerSurface')
box(surface, 3, 3, 74, 80)
t.edit(surface, [P(458752, st.h(4, {'r': f32(.035), 'g': f32(.08), 'b': f32(.10), 'a': 1.0}))])
rounded(surface, 5, True)

box(1167, 3, 3, 74, 80)
rounded(1167, 5, True)
# The native PersonPicture keeps its person binding, portrait loading and fallback.
t.edit(1169, [P(262153, st.en('scale-to-fit'))])

# Both native role movement glyphs retain all remapping and internal visibility.
# Other native warnings stay at the upper right rather than covering these glyphs.
for i, y in [(1029, 19), (1033, 37)]:
    move(i, frame)
    box(i, 5, y, 16, 16)
for i, y in [(1032, 4), (1031, 23)]:
    move(i, frame)
    box(i, 60, y, 16, 16)
box(1069, 0, 0, 12, 14)

# Percentage and progress share the EXISTING 0..100 decision tree. Each active
# percentage leaf owns a single lightweight coloured fill; no second state tree.
box(gate, 0, 0, 80, 94)
track = add_ve(gate, 'CombinedCardFitnessTrack')
box(track, 0, 90, 80, 4)
t.edit(track, [P(458752, st.h(4, {'r': f32(.19), 'g': f32(.23), 'b': f32(.26), 'a': 1.0}))])
rounded(track, 2, True)
t.r[gate]['data']['m_Children'] = [{'rid': track}, {'rid': fitness_root}]
leaves = {}
for i, a in list(original.items()):
    if a.get('data', {}).get('m_FullTypeName') != 'SI.Bindable.SIText': continue
    s = serial(original, i)['data']
    name = s.get('name', '')
    if not name.startswith('PitchFitnessPercent'): continue
    suffix = name.removeprefix('PitchFitnessPercent')
    value = None if suffix == 'None' else int(suffix)
    leaves[i] = value
    box(i, 0, 0, 80, 94)
    t.edit(i, [P(65537, st.px(10)), P(65543, st.en('bold')),
               P(65546, st.en('upper-left')), P(131099, st.px(5)), P(131101, st.px(3)),
               P(458768, st.en('visible'))])
    fill = add_ve(i, 'CombinedCardFitnessFill' + str(value))
    box(fill, 0, 90, 0 if value is None else value * .8, 4)
    # Dimensions are single precision in the serialized StyleSheet.
    for dim in sheet['dimensions']: dim['value'] = f32(dim['value'])
    t.edit(fill, [P(458752, st.h(4, colour(value)))])
    rounded(fill, 2, True)

assert len(leaves) == 102

# Reorder the portrait layers: colour, inner surface, hidden shirt, headshot,
# native shirt click target / swap indicator, percentage, native glyphs/warnings.
t.r[frame]['data']['m_Children'] = [{'rid': i} for i in
    [border, surface, 1030, 1167, 1046, 1047, gate, 1029, 1033, 1032, 1031]]

# Keep the actual native IP/OOP position-role controls. Their events, payloads,
# disabled states and tooltips are untouched; only geometry changes.
box(1019, 0, 9, 80, 61)
t.edit(1019, [P(458768, st.en('visible')), P(262147, st.px(0))])
box(1026, 0, 0, 80, 61)
t.edit(1026, [P(458768, st.en('visible'))])
box(1035, 3, 0, 74, 18)
rounded(1035, 4, True)
for i in [1055, 1057, 1075, 1078, 1092, 1094, 1105, 1107]:
    t.edit(i, [P(131097, st.px(0)), P(131096, st.px(0)), P(131087, st.px(18)),
               P(131094, st.px(18)), P(131085, st.num(1)), P(262150, st.px(0)),
               P(262151, st.px(0))])
for i in [1055, 1057]: t.edit(i, [P(131082, st.pct(50)), P(131105, st.pct(50))])
for i in [1075, 1078, 1092, 1094, 1105, 1107]: t.edit(i, [P(131105, st.pct(100))])
# Opaque translucent panel over the native position colour gives a legible footer.
for i in [1105, 1107]:
    t.edit(i, [P(458752, st.h(4, {'r': f32(.025), 'g': f32(.055), 'b': f32(.07), 'a': f32(.92)})),
               P(262147, st.px(0))])
for i in [1119, 1122]:
    t.edit(i, [P(65537, st.px(10)), P(65546, st.en('middle-center')),
               P(65536, st.h(4, {'r': 1.0, 'g': 1.0, 'b': 1.0, 'a': 1.0})),
               P(262150, st.px(0)), P(131097, st.px(0)), P(65552, st.en('nowrap'))])
box(1037, 0, 33, 80, 18)
box(1036, 0, 51, 80, 10)
box(1027, 0, -65, 80, 86)
rounded(1027, 8)

# Structural and semantic acceptance checks, before touching installed files.
for i, a in original.items():
    if 'UxmlSerializedData' in a.get('type', {}).get('class', ''):
        assert t.r[i] == a, ('Existing binding/event changed', i)
assert d['m_Usings'] == objs[PID].read_typetree()['m_Usings']
assert t.r[1105]['data']['m_Parent'] == original[1105]['data']['m_Parent']
assert t.r[1107]['data']['m_Parent'] == original[1107]['data']['m_Parent']
assert t.sd(gate)['Binding']['m_direct']['Path']['m_path'] == 'position.Player'

def property_value(i, key):
    rule = sheet['m_Rules'][t.r[i]['data']['m_RuleIndex']]
    h = next(p for p in rule['m_Properties'] if p['m_Id'] == key)['m_Values'][0]
    return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]

checked = []
for value in [None, -2147483648, -1] + list(range(111)):
    node = fitness_root
    while node not in leaves:
        args = decode(t.sd(node)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        assert args[2].endswith(b'position.Player.Condition')
        limit = struct.unpack_from('<i', args[1], len(args[1])-4)[0]
        node = t.r[node]['data']['m_Children'][int(value is not None and value > limit)]['rid']
    expected = None if value is None or value < 0 else min(value, 100)
    assert leaves[node] == expected
    assert t.sd(node)['text'] == ('--' if expected is None else str(expected) + '%')
    fill = t.r[node]['data']['m_Children'][0]['rid']
    assert property_value(fill, 131105)['value'] == f32(0 if expected is None else expected * .8)
    assert property_value(fill, 458752) == colour(expected)
    if value in [None, 0, 1, 50, 68, 99, 100]: checked.append(value)

reserved = json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
reserved_ids = {int(x['path_id']) for x in reserved}
bg = UnityPy.load(str(GAME/'ui-backgrounds_assets_common.bundle'))
bgobjs = {o.path_id: o for o in bg.objects}
bgmeta = next(o.read_typetree() for o in bg.objects if o.type.name == 'AssetBundle')
assert reserved_ids.isdisjoint(bgobjs)
assert not any(p['m_PathID'] in reserved_ids for p in bgmeta['m_PreloadTable'])
assert not any(v['asset']['m_PathID'] in reserved_ids for _, v in bgmeta['m_Container'])
registry = json.loads((R/'current-custom-textures.json').read_text('utf8'))
for row in registry['textures']:
    assert bgobjs[int(row['path_id'])].peek_name() == row['name']

# No new VTA, function, texture, GUID, bundle object or external dependency.
# Validate the existing Combined entry and the functions actually used by it.
spec = importlib.util.spec_from_file_location('catalog', R/'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec); spec.loader.exec_module(cm)
meta = next(o.read_typetree() for o in objs.values() if o.type.name == 'AssetBundle')
guid = next(k for k, v in meta['m_Container'] if v['asset']['m_PathID'] == PID)
catalog_audits = []
for path in [GAME.parent/'catalog.bin', SKIN/'catalog.bin']:
    c = cm.Catalog(path.read_bytes())
    locs = c.locations(guid)
    assert locs, ('Missing native Combined catalog GUID', path, guid)
    assert any(c.location(loc)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset' for loc in locs)
    for loc in locs:
        entry = c.location(loc)
        assert entry['type'][1] in ['UnityEngine.UIElements.VisualTreeAsset', 'UnityEngine.UIElements.StyleSheet']
        assert entry['dependencies'] and c.location(entry['dependencies'][0])['internal'].endswith('\\' + W)
    for key in ['a3126e03e5bea6348ba86f23b5c5d7de', 'e7d9180d37a23fa45820ee4690008153',
                '4e7f228c580c7864f83a2686d0a2e047', 'f6f314e9db56227459137669d87c44e9']:
        assert c.locations(key), ('Missing reused asset/function', path, key)
    catalog_audits.append(str(path))

validate_ui(d, sheet)
objs[PID].save_typetree(d)
objs[SID].save_typetree(sheet)
output = env.file.save(packer='lz4')
check = {o.path_id: o for o in UnityPy.load(output).objects}
assert set(check) == set(objs)
for i, h in hashes.items():
    if i not in [PID, SID]: assert sha(check[i].get_raw_data()) == h, ('Unrelated object modified', i)
assert check[PID].read_typetree() == d
assert check[SID].read_typetree() == sheet
(OUT/W).write_bytes(output)
(OUT/'TacticsPositionCombined.json').write_text(json.dumps(d, ensure_ascii=False, indent=2), 'utf8')
(OUT/'TacticsPositionCombined.style.json').write_text(json.dumps(sheet, ensure_ascii=False, indent=2), 'utf8')

report = {'installed': False, 'runtime_verified': False, 'template': d['m_Name'], 'path_id': str(PID),
          'style_path_id': str(SID), 'card_size': [80, 86], 'portrait_inset': 3,
          'pitch_anchor_footprint': [80, 70], 'percentage': 'position.Player.Condition direct 0..100',
          'native_role_icons_vertical': [19, 37], 'native_icon_visibility_unchanged': True,
          'all_original_serialized_bindings_and_events_unchanged': True,
          'fitness_state_checks': 114, 'acceptance_values': checked,
          'added_bundle_objects': 0, 'new_textures': 0, 'catalogs_validated_unchanged': catalog_audits,
          'reserved_70_absent': True, 'current_custom_texture_objects_verified': len(registry['textures']),
          'unrelated_world_objects_unchanged': len(hashes)-2,
          'protected_files': {str(p): h for p, h in protected.items()},
          'before_sha256': {str(p): sha(b) for p, b in before.items()}, 'after_sha256': sha(output)}

def record(): (OUT/'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
record()
restore = ['$ErrorActionPreference = "Stop"',
           "if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer = list(restore)
for path, raw in before.items():
    backup = OUT / ('backup-game' if path.parent == GAME else 'backup-skin') / W
    rollback = OUT/'backup-original'/W if source_raw != before[GAME/W] else backup
    restore.append("Copy-Item -LiteralPath '"+str(rollback)+"' -Destination '"+str(path)+"' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '"+str(path)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(raw)+"') { throw 'Package changed since preparation.' }")
for path in before:
    installer.append("Copy-Item -LiteralPath '"+str(OUT/W)+"' -Destination '"+str(path)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore), 'utf-8-sig')
(OUT/'install.ps1').write_text('\n'.join(installer), 'utf-8-sig')

for p, raw in before.items(): assert p.read_bytes() == raw
for p, h in protected.items(): assert sha(p.read_bytes()) == h
running = subprocess.run(['powershell', '-NoProfile', '-Command',
                         'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],
                         capture_output=True, text=True)
if running.stdout.strip():
    print(json.dumps({'prepared': True, 'installed': False, 'waiting_for_game_exit': True, 'output': str(OUT)}))
    sys.exit(0)
try:
    for p in before: p.write_bytes(output)
    for p in before: assert sha(p.read_bytes()) == sha(output)
    for p, h in protected.items(): assert sha(p.read_bytes()) == h
except BaseException:
    for p, raw in before.items(): p.write_bytes(raw)
    raise
report.update(installed=True, installed_verified=True)
record()
print(json.dumps({'installed': True, 'output': str(OUT), 'changed_bundle_objects': 2,
                  'checked_condition_states': 114, 'original_bindings_unchanged': True}))
