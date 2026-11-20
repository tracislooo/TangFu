from pathlib import Path
import colorsys

# Reuse serialization, backup, catalog, and style helpers without running an installer.
source = Path('combine-tactics-condition-sharpness.py').read_text('utf-8-sig')
exec(compile(source.split('bge = UnityPy.load')[0].replace('tactics-combined-condition-sharpness-', 'tactics-width90-fatigue40-colours-'), 'backup-and-helpers', 'exec'))
FCELL, FSTYLE = -970000000004000, -970000000004001
FGUID = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/TacticsRawFatigueGradient/v1').hex
FATIGUE = 'tactics-fatigue-value'

def props_value(r, s, i, key):
    p = next(p for p in s['m_Rules'][r[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id'] == key)
    h = p['m_Values'][0]
    return s[poolmap[h['m_ValueType']]][h['valueIndex']]

# Reflow the existing combined cell, keeping the large 22px and small 12px rings.
combined = obs[W][CELL].read_typetree()
cr = refs(combined)
cs = obs[W][STYLE].read_typetree()
st = Styles(cs)
st.edit(cr[1001], [st.p(131097, st.px(90)), st.p(131095, st.px(90)), st.p(131105, st.px(90))])
st.edit(cr[1006], [st.p(131105, st.px(90)), st.p(131097, st.px(90)), st.p(131095, st.px(90))])
for i, a in cr.items():
    sid = a.get('data', {}).get('m_SerializedData', {}).get('rid', -2)
    if sid == -2: continue
    name = cr[sid]['data'].get('name', '')
    if not name.startswith('Combined'): continue
    if 'Above' in name or 'Value' in name:
        st.edit(a, [st.p(131105, st.px(90))])
    elif 'Percent' in name:
        left = name.startswith('CombinedCondition')
        st.edit(a, [st.p(131089, st.px(0 if left else 59)), st.p(131105, st.px(30)), st.p(131097, st.px(0)), st.p(131095, st.px(30)), st.p(65537, st.px(11))])
    elif 'Ring' in name:
        left = name.startswith('CombinedCondition')
        st.edit(a, [st.p(131089, st.px(34 if left else 39))])
validate_ui(combined, cs)
save(W, CELL, combined)
save(W, STYLE, cs)
header = obs[W][HEADER].read_typetree()
hr = refs(header)
hs = obs[W][HEADER_STYLE].read_typetree()
hst = Styles(hs)
hst.edit(hr[named(hr, 'CombinedConditionSharpnessTitle')], [hst.p(65537, hst.px(9))])
validate_ui(header, hs)
save(W, HEADER, header)
save(W, HEADER_STYLE, hs)

# Native numeric text stays bound to the raw integer, including negative values.
number_source = obs[W][4189577818871665281]
doc = number_source.read_typetree()
old_sid = doc['inlineSheet']['m_PathID']
sheet = obs[W][old_sid].read_typetree()
doc.update(m_Name='TacticsRawFatigueGradientCell')
doc['inlineSheet']['m_PathID'] = FSTYLE
sheet['m_Name'] = 'TacticsRawFatigueGradientCell_Style'
rr = refs(doc)
textproto, textsd = copy.deepcopy(rr[1004]), copy.deepcopy(serial(rr, 1004))
switchproto = copy.deepcopy(cr[named(cr, 'CombinedConditionAbove-1')])
switchsd = copy.deepcopy(serial(cr, named(cr, 'CombinedConditionAbove-1')))
next_rid = max(rr) + 1
next_id = max(a.get('data', {}).get('m_Id', 0) for a in rr.values()) + 1
discard = {1002, 1004, rr[1002]['data']['m_SerializedData']['rid'], rr[1004]['data']['m_SerializedData']['rid']}
rr = {i: a for i, a in rr.items() if i not in discard}
doc['references']['RefIds'] = [a for a in doc['references']['RefIds'] if a['rid'] in rr]
rr[1001]['data']['m_Children'] = []
st = Styles(sheet)
st.edit(rr[1001], [st.p(131105, st.px(40)), st.p(131097, st.px(40)), st.p(131095, st.px(40)), st.p(131084, st.num(1)), st.p(262150, st.px(0)), st.p(262151, st.px(0))])

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
    st.edit(a, [st.p(131105, st.pct(100)), st.p(131087, st.pct(100)), st.p(131097, st.px(0)), st.p(131096, st.px(0)), st.p(131084, st.num(1)), st.p(131085, st.num(1)), st.p(262150, st.px(0)), st.p(262151, st.px(0))], reset=True)
    return a['rid']

def fatigue_colour(v):
    if v is None: channels = (.5, .5, .5)
    else:
        v = max(-500, min(1000, v))
        hue = (1 - v / 1000) / 3 if v >= 0 else 1 / 3 - (-v / 500) / 4
        channels = colorsys.hsv_to_rgb(hue, .75, .88)
    return dict(zip(['r', 'g', 'b', 'a'], [f32(c) for c in channels] + [1.0]))

def switch(parent, limit):
    i = add(switchproto, switchsd, parent, f'FatigueAbove{limit}')
    data = serial(rr, i)['data']
    args = decode(data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    struct.pack_into('<i', args[1], len(args[1]) - 4, limit)
    oldpath = b'player.Condition'
    assert args[2].endswith(bytes([len(oldpath)]) + oldpath)
    args[2][-len(oldpath) - 1:] = bytes([7]) + b'binding'
    data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = encode(args)
    return i

leaves = {}
def leaf(parent, value):
    i = add(textproto, textsd, parent, f'FatigueRawColour{value}')
    data = serial(rr, i)['data']
    rr[i]['data']['m_Classes'] = []
    if value is None:
        data.update(text='--', text_UxmlAttributeFlags=1, TextBinding_UxmlAttributeFlags=0)
        data['TextBinding']['m_kind'] = 0
    else:
        assert data['TextBinding']['m_direct']['Path']['m_path'] == 'binding'
        data['TextBinding_UxmlAttributeFlags'] = 1
    st.edit(rr[i], [st.p(65537, st.px(11)), st.p(65546, st.en('middle-center')), st.p(65552, st.en('nowrap')), st.p(65536, st.h(4, fatigue_colour(value)))])
    leaves[i] = value
    return i

def tree(parent, lo, hi):
    if lo == hi: return leaf(parent, lo)
    mid = (lo + hi) // 2
    i = switch(parent, mid)
    tree(i, lo, mid)
    tree(i, mid + 1, hi)
    return i

root = switch(1001, -2147483648)
leaf(root, None)
tree(root, -500, 1000)
validate_ui(doc, sheet)
clone(number_source, FCELL, doc)
clone(obs[W][old_sid], FSTYLE, sheet)

# Disable width auto-resizing, and match all six tactical view overrides.
factory = obs[F][-7014073910555419620].read_typetree()
oldfactory = copy.deepcopy(factory)
for c in factory['m_rowData']:
    if c['m_id'] not in ['condition', FATIGUE]: continue
    width = 90.0 if c['m_id'] == 'condition' else 40.0
    c.update(m_defaultWidth=width, m_minimumWidth=width, m_allowWidthAutoResizing=0)
    if c['m_id'] == FATIGUE: c['m_uxmlRef']['m_AssetGUID'] = FGUID
assert sum(a != b for a, b in zip(factory['m_rowData'], oldfactory['m_rowData'])) == 2
save(F, -7014073910555419620, factory)
views = []
for o in obs[V].values():
    if o.type.name != 'MonoBehaviour' or not o.peek_name().startswith('TacticTeamSelection') or 'InMatch' in o.peek_name(): continue
    d = o.read_typetree()
    configs = d.get('m_tableView', {}).get('m_tableConfig', [])
    if not any(c['m_columnID'] == FATIGUE for c in configs): continue
    for c in configs:
        if c['m_columnID'] in ['condition', FATIGUE]:
            width = 90.0 if c['m_columnID'] == 'condition' else 40.0
            c['m_columnMetadata'].update(m_widthOverride=width, m_minWidthOverride=width)
    save(V, o.path_id, d)
    views.append(d['m_Name'])
assert len(views) == 6

def selected(r, value):
    i = root
    while r[i]['data']['m_FullTypeName'] == 'SI.Bindable.BindableSwitchElement':
        args = decode(serial(r, i)['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        assert args[2].endswith(b'\x07binding')
        limit = struct.unpack_from('<i', args[1], len(args[1]) - 4)[0]
        i = r[i]['data']['m_Children'][int(value is not None and value > limit)]['rid']
    return i

cases = [None, -2147483648] + list(range(-1000, 1501))
for value in cases:
    i = selected(rr, value)
    expected_value = None if value is None or value == -2147483648 else max(-500, min(1000, value))
    assert leaves[i] == expected_value, value
    assert props_value(rr, sheet, i, 65536) == fatigue_colour(expected_value)
    if expected_value is not None: assert serial(rr, i)['data']['TextBinding']['m_direct']['Path']['m_path'] == 'binding'
assert len(leaves) == 1502
assert fatigue_colour(0)['g'] > fatigue_colour(0)['r']
assert fatigue_colour(1000)['r'] > fatigue_colour(1000)['g']
assert fatigue_colour(-500)['r'] > fatigue_colour(-500)['g'] > fatigue_colour(-500)['b']

# The 90px geometry must contain both maximum-length labels and concentric rings.
for metric in ['Condition', 'Sharpness']:
    ring = named(cr, f'Combined{metric}Ring100')
    text = named(cr, f'Combined{metric}Percent100')
    x = props_value(cr, cs, ring, 131089)['value']
    y = props_value(cr, cs, ring, 131104)['value']
    size = props_value(cr, cs, ring, 131105)['value']
    assert (x+size/2, y+size/2) == (45, 12)
    assert props_value(cr, cs, text, 131089)['value'] + props_value(cr, cs, text, 131105)['value'] <= 90

# Register only the new fatigue cell; keep the existing combined-cell identity.
metaobj = next(o for o in obs[W].values() if o.type.name == 'AssetBundle')
meta = metaobj.read_typetree()
span = []
def pointers(v):
    if isinstance(v, dict):
        if set(v) == {'m_FileID', 'm_PathID'}:
            if v['m_PathID'] and v not in span: span.append(copy.deepcopy(v))
        else:
            for x in v.values(): pointers(x)
    elif isinstance(v, list):
        for x in v: pointers(x)
pointers(doc)
pointers(sheet)
span.append({'m_FileID': 0, 'm_PathID': FCELL})
meta['m_Container'].append((FGUID, {'preloadIndex': len(meta['m_PreloadTable']), 'preloadSize': len(span), 'asset': {'m_FileID': 0, 'm_PathID': FCELL}}))
meta['m_PreloadTable'].extend(span)
meta['m_Container'].sort(key=lambda x: x[0])
save(W, metaobj.path_id, meta)
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
oldcat = cm.Catalog(before[GAME.parent / 'catalog.bin'])
loc = oldcat.locations('7fb52cbb54bc0be45bb85d725b2f53b9')[0]
cat = cm.Catalog(oldcat.add_key_location(FGUID, loc, loc))
idx = next(i for i, (key, _) in enumerate(cat.keys()) if key == 'GameWorldVisualTreeAssetPreload')
keyobj, locset = cat.key_records[idx]
locs = [a[0] for a in cat.array(locset, 'I')] + cat.locations(FGUID)
records = list(cat.key_records)
records[idx] = (keyobj, cat.append(b''.join(struct.pack('<I', i) for i in locs), True))
struct.pack_into('<I', cat.data, 8, cat.append(b''.join(struct.pack('<2I', *a) for a in records), True))
catout = bytes(cat.data)
newcat = cm.Catalog(catout)
newkeys = dict(newcat.keys())
assert set(newkeys) == set(dict(oldcat.keys())) | {FGUID}
for key, locset in oldcat.keys():
    assert [a[0] for a in newcat.array(newkeys[key], 'I')] == [a[0] for a in oldcat.array(locset, 'I')] + (newcat.locations(FGUID) if key == 'GameWorldVisualTreeAssetPreload' else [])

outputs = {n: e.file.save(packer='lz4') for n, e in env.items()}
for n, b in outputs.items():
    check = {o.path_id: o for o in UnityPy.load(b).objects}
    assert check.keys() == obs[n].keys()
    for i, h in hashes[n].items():
        if i not in expected[n]: assert sha(check[i].get_raw_data()) == h, (n, i)
    for i, d in expected[n].items(): assert check[i].read_typetree() == d, (n, i)
    if n == W:
        checkedrefs = refs(check[FCELL].read_typetree())
        for value in cases: assert selected(checkedrefs, value) == selected(rr, value)
    (OUT / n).write_bytes(b)
(OUT / 'catalog.bin').write_bytes(catout)
hashout = hashlib.md5(catout).hexdigest().encode('ascii')
(OUT / 'catalog.hash').write_bytes(hashout)

from PIL import Image, ImageDraw, ImageFont
font = ImageFont.truetype('C:/Windows/Fonts/arial.ttf', 11 * 4)
preview_values = [-500, -250, 0, 250, 500, 750, 1000]
preview = Image.new('RGB', (160, 24 * 4 * len(preview_values)), (42, 44, 48))
draw = ImageDraw.Draw(preview)
for row, value in enumerate(preview_values):
    c = fatigue_colour(value)
    draw.text((80, (row * 24 + 12) * 4), str(value), font=font, anchor='mm', fill=tuple(round(c[k]*255) for k in ['r','g','b']))
for value in [-500, -1000, 0, 1000]:
    bounds = draw.textbbox((80, 48), str(value), font=font, anchor='mm')
    assert 0 <= bounds[0] and bounds[2] <= 160
preview.save(OUT / 'fatigue-colours-preview.png')

install = {f / n: b for f in [GAME, SKIN] for n, b in outputs.items()}
install.update({GAME.parent / 'catalog.bin': catout, GAME.parent / 'catalog.hash': hashout, SKIN / 'catalog.bin': catout})
report = {'installed': False, 'runtime_verified': False, 'combined_width': 90, 'fatigue_width': 40, 'column_auto_resize': False,
          'gradient': {'-500': fatigue_colour(-500), '0': fatigue_colour(0), '1000': fatigue_colour(1000)},
          'numeric_binding': 'binding.Player.fatigue => binding; raw integer unchanged', 'colour_resolution': 'every integer in -500..1000',
          'out_of_range': 'colour clamps to endpoints; number is unchanged', 'missing': '-- and grey',
          'numeric_cases_verified': len(cases), 'views': views, 'inner_ring': 12, 'outer_ring': 22,
          'new_cell_guid': FGUID, 'after_sha256': {str(p): sha(b) for p, b in install.items()}}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
restore = ['$ErrorActionPreference = "Stop"', "if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer = list(restore)
for p, b in before.items():
    tag = 'backup-skin' if p.parent == SKIN else 'backup-game'
    restore.append("Copy-Item -LiteralPath '" + str(OUT / tag / p.name) + "' -Destination '" + str(p) + "' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '" + str(p) + "' -Algorithm SHA256).Hash.ToLower() -ne '" + sha(b) + "') { throw 'Package changed since preparation.' }")
for p in install: installer.append("Copy-Item -LiteralPath '" + str(OUT / p.name) + "' -Destination '" + str(p) + "' -Force")
(OUT / 'restore.ps1').write_text('\n'.join(restore), 'utf-8-sig')
(OUT / 'install.ps1').write_text('\n'.join(installer), 'utf-8-sig')
for p, b in before.items(): assert p.read_bytes() == b
for p, h in protected.items(): assert sha(p.read_bytes()) == h
proc = subprocess.run(['powershell', '-NoProfile', '-Command', 'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'], capture_output=True, text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared': True, 'installed': False, 'waiting_for_game_exit': True, 'output': str(OUT)})); sys.exit(0)
try:
    for p, b in install.items(): p.write_bytes(b)
    for p, b in install.items(): assert p.read_bytes() == b
    for p, h in protected.items(): assert sha(p.read_bytes()) == h
except BaseException:
    for p, b in before.items(): p.write_bytes(b)
    raise
report.update(installed=True, installed_verified=True)
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps({'installed': True, 'output': str(OUT), 'widths': [90, 40], 'fatigue_cases': len(cases)}))
