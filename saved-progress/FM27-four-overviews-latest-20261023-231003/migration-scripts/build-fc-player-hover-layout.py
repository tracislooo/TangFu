from pathlib import Path
import copy, datetime, hashlib, importlib.util, json, struct, sys, uuid

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
L = 'ui-tileslayouts_assets_all.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
CARD, STYLE, DESC = -960000000003010, -960000000003011, -960000000003012
CARD_ID = 'TooltipFCPlayerCard'
GUID = uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/TooltipFCPlayerCard/v1').hex
sha = lambda b: hashlib.sha256(b).hexdigest()
before = {p / n: (p / n).read_bytes() for p in [GAME, SKIN] for n in [W, L, G]}
for n in [W, L, G]: assert before[GAME / n] == before[SKIN / n], n
for p in [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', SKIN / 'catalog.bin']:
    before[p] = p.read_bytes()
assert before[GAME.parent / 'catalog.bin'] == before[SKIN / 'catalog.bin']
env = {n: UnityPy.load(before[GAME / n]) for n in [W, L, G]}
obs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
oldhashes = {n: {i: sha(o.get_raw_data()) for i, o in os.items()} for n, os in obs.items()}
expected = {n: {} for n in env}
def named(n, name):
    a = [o for o in obs[n].values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name]
    assert len(a) == 1, (name, len(a))
    return a[0]
oldwrite = TypeTreeHelper.write_value
def write(v, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(v, config.assetsfile) is None:
        for ch in node.m_Children:
            if ch.m_Type != 'ReferencedObjectData': oldwrite(v[ch.m_Name], ch, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag): writer.align_stream()
        return
    return oldwrite(v, node, writer, config)
TypeTreeHelper.write_value = write
def save(n, o, data):
    o.save_typetree(data)
    expected[n][o.path_id] = copy.deepcopy(data)
def clone(n, source, pid, data):
    assert pid not in obs[n]
    o = copy.copy(source)
    o.path_id = pid
    o.data = None
    o._read_until = None
    o.assets_file.objects[pid] = o
    save(n, o, data)
    return o

poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
class Styles:
    def __init__(self, data): self.data = data
    def h(self, typ, value):
        p = self.data[poolmap[typ]]
        p.append(value)
        return {'m_ValueType': typ, 'valueIndex': len(p) - 1}
    def px(self, v): return self.h(3, {'unit': 1, 'value': float(v)})
    def pct(self, v): return self.h(3, {'unit': 2, 'value': float(v)})
    def en(self, v): return self.h(7, v)
    def num(self, v): return self.h(2, struct.unpack('<f', struct.pack('<f', float(v)))[0])
    def p(self, key, *v): return {'m_Id': key, 'm_CustomName': '', 'm_Line': -1, 'm_Values': list(v)}
    def edit(self, node, props, reset=False):
        d = node.get('data', node)
        old = copy.deepcopy(self.data['m_Rules'][d['m_RuleIndex']]['m_Properties']) if d.get('m_RuleIndex', -1) >= 0 and not reset else []
        keys = {p['m_Id'] for p in props}
        d['m_RuleIndex'] = len(self.data['m_Rules'])
        self.data['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': [p for p in old if p['m_Id'] not in keys] + props, 'line': -1})
    def box(self, node, x, y, w, h):
        self.edit(node, [self.p(131102, self.en('absolute')), self.p(131089, self.px(x)), self.p(131104, self.px(y)),
                        self.p(131105, self.px(w)), self.p(131087, self.px(h)), self.p(131097, self.px(0)),
                        self.p(131096, self.px(0)), self.p(131095, {'m_ValueType': 1, 'valueIndex': 3}),
                        self.p(131094, {'m_ValueType': 1, 'valueIndex': 3}), self.p(262150, self.px(0)),
                        self.p(262151, self.px(0)), self.p(131084, self.num(0)), self.p(131085, self.num(0)),
                        self.p(327681, self.num(1), self.num(1))])

# Copy only the FC card subtree. The player-page source and calculations stay intact.
source = obs[W][-930000000001001]
source_data = source.read_typetree()
source_refs = {r['rid']: r for r in source_data['references']['RefIds']}
sheet_source = obs[W][source_data['inlineSheet']['m_PathID']]
sheet = sheet_source.read_typetree()
sheet['m_Name'] = CARD_ID + '_Style'
st = Styles(sheet)
sr = copy.deepcopy(source_refs)
stage = sr[1299]
stage['data']['m_Parent'] = {'rid': 1001}
stage['data']['m_Children'] = [{'rid': i} for i in [1301, 1285, 1819]]
st.edit(stage, [st.p(131102, st.en('relative')), st.p(131105, st.px(340)), st.p(131087, st.px(550)),
                st.p(131084, st.num(0)), st.p(131085, st.num(0)), st.p(262150, st.px(0)), st.p(262151, st.px(0)),
                st.p(458768, st.en('visible'))], reset=True)
st.box(sr[1301], 0, 5, 340, 510)
st.box(sr[1285], 105, 105, 215, 230)
st.box(sr[1819], 32, 415, 276, 55)

# Reflow each outfield/GK six-rating branch into a single six-column row.
for branch_id in [1777, 1821]:
    branch = sr[branch_id]
    rows = [sr[c['rid']] for c in branch['data']['m_Children']]
    cells = [sr[c['rid']] for row in rows for c in row['data']['m_Children']]
    assert len(cells) == 6
    row = rows[0]
    row['data']['m_Children'] = [{'rid': c['rid']} for c in cells]
    branch['data']['m_Children'] = [{'rid': row['rid']}]
    st.edit(row, [st.p(131083, st.en('row')), st.p(131105, st.pct(100)), st.p(131087, st.px(55))], reset=True)
    for cell in cells:
        cell['data']['m_Parent'] = {'rid': row['rid']}
        st.edit(cell, [st.p(131083, st.en('column')), st.p(131105, st.px(46)), st.p(131087, st.px(55)),
                       st.p(131073, st.en('center')), st.p(131085, st.num(0))], reset=True)
        for index, child in enumerate(cell['data']['m_Children']):
            st.edit(sr[child['rid']], [st.p(131105, st.px(46)), st.p(131087, st.px(18 if index == 0 else 28)),
                                      st.p(65537, st.px(10 if index == 0 else 20)), st.p(65546, st.en('middle-center'))])

def managed_ids(v, skip_parent=True):
    if isinstance(v, dict):
        if set(v) == {'rid'}:
            if v['rid'] != -2: yield v['rid']
        else:
            for k, x in v.items():
                if k != 'm_Parent' or not skip_parent: yield from managed_ids(x, skip_parent)
    elif isinstance(v, list):
        for x in v: yield from managed_ids(x, skip_parent)
keep = set()
todo = [1299]
while todo:
    i = todo.pop()
    if i in keep: continue
    keep.add(i)
    todo.extend(managed_ids(sr[i].get('data', {})))

# Reuse the working tooltip-only person binding shell.
shell = named(W, 'TooltipOnly_AttributesTableSmall').read_typetree()
root_refs = {r['rid']: r for r in shell['references']['RefIds'] if r['rid'] not in [1031, 1049]}
root_refs[1001]['data']['m_Children'] = [{'rid': i} for i in [1002, 1003, 1004, 1299]]
st.edit(root_refs[1001], [st.p(131105, st.pct(100)), st.p(131087, st.pct(100)), st.p(131073, st.en('center')),
                            st.p(131088, st.en('center')), st.p(131083, st.en('column'))], reset=True)
root_refs[1001]['data']['m_Classes'] = []
mapping = root_refs[1014]['data']['Mappings']
for name, path, typ in [('localteam', 'person.Team', 1145176088), ('team', 'person.Team', 1145176088),
                         ('nation', 'person.Nation', 1145176074)]:
    mapping.append({'m_serialisedType': 0, 'from': name, 'to': {'m_path': path}, 'type': {'id': typ}})
root_refs[1003]['data']['m_Properties'] = []
refs = {**root_refs, **{i: sr[i] for i in keep}}
doc = copy.deepcopy(shell)
doc['m_Name'] = CARD_ID
doc['inlineSheet'] = {'m_FileID': 0, 'm_PathID': STYLE}
doc['m_ContentHash'] = struct.unpack('<i', bytes.fromhex(GUID[:8]))[0]
doc['m_Usings'] = copy.deepcopy(source_data['m_Usings'])
next_rid = 50000
next_eid = 1950000000
def pair(nt, sd, parent, name):
    global next_rid, next_eid
    a, b = copy.deepcopy(nt), copy.deepcopy(sd)
    a['rid'], b['rid'] = next_rid, next_rid + 1
    next_rid += 2
    a['data'].update(m_Id=next_eid, m_Parent={'rid': parent}, m_Children=[], m_SerializedData={'rid': b['rid']},
                     m_RuleIndex=-1, m_Classes=[], m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[])
    b['data'].update(uxmlAssetId=next_eid, name=name, name_UxmlAttributeFlags=1)
    next_eid += 1
    refs[a['rid']], refs[b['rid']] = a, b
    refs[parent]['data']['m_Children'].append({'rid': a['rid']})
    return a, b
def text(name, path, y, size):
    nt = source_refs[1881]
    a, b = pair(nt, source_refs[nt['data']['m_SerializedData']['rid']], 1299, name)
    st.box(a, 24, y, 292, 30)
    st.edit(a, [st.p(65537, st.px(size)), st.p(65546, st.en('middle-center')), st.p(65543, st.en('bold'))])
    b['data']['TextBinding']['m_kind'] = 1
    b['data']['TextBinding']['m_direct'] = {'Path': {'m_path': path}, 'Nullable': 0}
    b['data']['TextBinding']['m_visualFunction'] = {'m_target': {'m_guid': ''}, 'm_inputs': {'m_variable': {'m_argumentBytes': []}}, 'm_outputs': {'m_variable': {'m_argumentBytes': []}}}
    b['data']['TextBinding_UxmlAttributeFlags'] = 1
text('TooltipCardPlayerName', 'person.Name', 352, 21)
text('TooltipCardPosition', 'person.BestPositionShortString', 381, 13)

# Use native flag/club badge templates; null teams retain the native fallback behavior.
template_source = source_refs[next(i for i, r in source_refs.items() if r.get('data', {}).get('m_TemplateAlias'))]
template_sd = source_refs[template_source['data']['m_SerializedData']['rid']]
for alias, guid, x, y, w, h in [('NationFlag_Small', '419069e4639bbd4488b658673c2d7d9b', 40, 115, 42, 28),
                               ('TeamIcon32px', 'ac8a0a8af03f19e448853702e16e2233', 40, 166, 46, 46)]:
    a, b = pair(template_source, template_sd, 1299, 'TooltipCard_' + alias)
    a['data'].update(m_TemplateAlias=alias, m_AttributeOverrides=[], m_SerializedDataOverride=[], m_SlotUsages=[])
    b['data']['templateId'] = alias
    b['data']['templateId_UxmlAttributeFlags'] = 1
    b['data']['template'] = {'m_FileID': 0, 'm_PathID': 0}
    st.box(a, x, y, w, h)
    st.edit(a, [st.p(327681, st.num(1.3), st.num(1.3))])
    doc['m_Usings'].append({'alias': alias, 'path': guid, 'asset': {'m_FileID': 0, 'm_PathID': 0}})

doc['references']['RefIds'] = list(refs.values())
used_aliases = {r.get('data', {}).get('m_TemplateAlias') for r in refs.values()} - {None}
doc['m_Usings'] = [u for u in doc['m_Usings'] if u['alias'] in used_aliases]
assert len({u['alias'] for u in doc['m_Usings']}) == len(used_aliases)
assert not any('PlayerCurrentAbility' in str(r) or 'PlayerPotentialAbility' in str(r) for r in refs.values()
               if r.get('data', {}).get('name', '').startswith('Card'))

# Compact the copied inline stylesheet to the card's active rules and values.
rules = sorted({r['data']['m_RuleIndex'] for r in refs.values() if r.get('data', {}).get('m_RuleIndex', -1) >= 0})
rulemap = {old: new for new, old in enumerate(rules)}
for r in refs.values():
    d = r.get('data', {})
    if d.get('m_RuleIndex', -1) >= 0: d['m_RuleIndex'] = rulemap[d['m_RuleIndex']]
sheet['m_Rules'] = [sheet['m_Rules'][i] for i in rules]
for pool in set(poolmap.values()):
    active = sorted({h['valueIndex'] for rule in sheet['m_Rules'] for p in rule['m_Properties'] for h in p['m_Values'] if poolmap.get(h['m_ValueType']) == pool})
    remap = {old: new for new, old in enumerate(active)}
    sheet[pool] = [sheet[pool][i] for i in active]
    for rule in sheet['m_Rules']:
        for p in rule['m_Properties']:
            for h in p['m_Values']:
                if poolmap.get(h['m_ValueType']) == pool: h['valueIndex'] = remap[h['valueIndex']]

def validate_ui(d, sheet):
    rs = {r['rid']: r for r in d['references']['RefIds']}
    assert len(rs) == len(d['references']['RefIds'])
    for r in rs.values():
        for i in managed_ids(r.get('data', {}), False): assert i in rs, (r['rid'], i)
        a = r.get('data', {})
        for c in a.get('m_Children', []): assert rs[c['rid']]['data']['m_Parent']['rid'] == r['rid']
        sd = a.get('m_SerializedData', {}).get('rid', -2)
        if sd != -2: assert rs[sd]['data']['uxmlAssetId'] == a['m_Id']
        if a.get('m_RuleIndex', -1) >= 0: assert a['m_RuleIndex'] < len(sheet['m_Rules'])
    for rule in sheet['m_Rules']:
        for p in rule['m_Properties']:
            for h in p['m_Values']:
                if h['m_ValueType'] in poolmap: assert h['valueIndex'] < len(sheet[poolmap[h['m_ValueType']]])
validate_ui(doc, sheet)
clone(W, source, CARD, doc)
clone(W, sheet_source, STYLE, sheet)

# Dedicated FC-card grid description.
desc_source = named(L, 'TooltipOnlyPlayerAttributesTileDescription')
dd = desc_source.read_typetree()
dd.update(m_Name=CARD_ID + 'TileDescription')
dd['<Name>k__BackingField'] = dd['<ID>k__BackingField'] = CARD_ID
cardcfg = copy.deepcopy(dd['<Configurations>k__BackingField'][0])
cardcfg['Description'] = {'m_FileID': 0, 'm_PathID': DESC}
cardcfg['Size'] = {'x': 5, 'y': 10}
cardcfg['AssetRef']['m_AssetGUID'] = GUID
dd['<Configurations>k__BackingField'] = [cardcfg]
clone(L, desc_source, DESC, dd)

# Right: compact header, SMALL attributes, then the original report/mood/position modules.
layout_obj = named(L, 'PlayerReportTooltipGridComposition')
layout = layout_obj.read_typetree()
byid = {c['m_elementID']: c for c in layout['m_gridComponents']}
positions = {'PlayerReportHeaderTooltip': (5, 0, 10, 1), 'TooltipOnlyPlayerAttributes': (5, 1, 10, 7),
             'CoachScoutReportBlock': (5, 8, 4, 2), 'PlayerHappiness': (9, 8, 2, 2), 'PlayerPositionalTooltip': (11, 8, 4, 2)}
for key, (x, y, w, h) in positions.items():
    c = byid[key]
    c['m_location'] = {'x': x, 'y': y, 'width': w, 'height': h}
    c['m_minSize'] = c['m_maxSize'] = {'x': w, 'y': h}
    c['m_isLocked'] = 1
    for cfg in c['m_gridElementConfigs']: cfg['Size'] = {'x': w, 'y': h}
cardcomponent = copy.deepcopy(byid['TooltipOnlyPlayerAttributes'])
cardcomponent.update(m_elementID=CARD_ID, m_configDescriptions=[{'m_FileID': 0, 'm_PathID': DESC}],
                     m_gridElementConfigs=[cardcfg], m_location={'x': 0, 'y': 0, 'width': 5, 'height': 10},
                     m_minSize={'x': 5, 'y': 10}, m_maxSize={'x': 5, 'y': 10}, m_features=0)
layout['m_gridComponents'].append(cardcomponent)
layout['m_placementBindings'].append({'m_elementID': CARD_ID, 'm_optionalConditions': [], 'm_optionalConfigConditions': []})
layout['m_optionalSlices']['m_instantiationOrder'] = list(range(len(layout['m_gridComponents'])))
layout['m_compositionVersion'] += 1
save(L, layout_obj, layout)
for description_name, size in [('TooltipOnlyPlayerAttributesTileDescription', {'x': 10, 'y': 7}),
                                ('PlayerReportHeaderTooltipDescription', {'x': 10, 'y': 1})]:
    o = named(L, description_name)
    d = o.read_typetree()
    for cfg in d['<Configurations>k__BackingField']: cfg['Size'] = size
    save(L, o, d)
setobj = named(L, 'PlayerReportTooltipGridElementSet')
setdata = setobj.read_typetree()
setdata['m_gridElementDescriptions'].append({'m_FileID': 0, 'm_PathID': DESC})
save(L, setobj, setdata)

# Add person binding for the new card and explicitly size only the real-player popup branch.
preview = named(W, 'PlayerReportPreviewTooltip')
pd = preview.read_typetree()
prs = {r['rid']: r for r in pd['references']['RefIds']}
psobj = obs[W][pd['inlineSheet']['m_PathID']]
ps = psobj.read_typetree()
pst = Styles(ps)
grid = next(r for r in prs.values() if r.get('data', {}).get('Bindings', {}).get('m_gridCompositionSet', {}).get('m_PathID') == -241840581472044354)
gb = grid['data']['Bindings']
binding = copy.deepcopy(next(b for b in gb['m_gridElementBindingData'] if b['DescriptionAndMapping']['DescriptionName'] == 'TooltipOnlyPlayerAttributes'))
binding['DescriptionAndMapping']['DescriptionName'] = CARD_ID
gb['m_gridElementBindingData'].append(binding)
gridnode = next(r for r in prs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == grid['rid'])
pst.edit(gridnode, [pst.p(131105, pst.px(1080)), pst.p(131087, pst.px(640)),
                    pst.p(131097, pst.px(1080)), pst.p(131095, pst.px(1080)),
                    pst.p(131096, pst.px(640)), pst.p(131094, pst.px(640)),
                    pst.p(131084, pst.num(0)), pst.p(131085, pst.num(0))])
save(W, preview, pd)
save(W, psobj, ps)

# Remove the duplicate portrait and optional financial column from the tooltip header only.
header = named(G, 'report-player-banner-tooltip')
hd = header.read_typetree()
hrs = {r['rid']: r for r in hd['references']['RefIds']}
hsobj = obs[G][hd['inlineSheet']['m_PathID']]
hs = hsobj.read_typetree()
hst = Styles(hs)
for i in [1008, 1019, 1030]: hst.edit(hrs[i], [hst.p(131081, hst.en('none'))])
for i in [1002, 1004, 1006, 1009, 1015, 1018]:
    hst.edit(hrs[i], [hst.p(131087, hst.px(64)), hst.p(131096, hst.px(0)), hst.p(131097, hst.px(0)),
                      hst.p(131084, hst.num(1)), hst.p(131085, hst.num(1)), hst.p(262150, hst.px(0))])
save(G, header, hd)
save(G, hsobj, hs)

# Register the card VTA and its stylesheet dependency in the existing world bundle.
bundle = next(o for o in obs[W].values() if o.type.name == 'AssetBundle')
meta = bundle.read_typetree()
def pointer_span(value):
    out = []
    def scan(v):
        if isinstance(v, dict):
            if set(v) == {'m_FileID', 'm_PathID'}:
                if v['m_PathID'] and v not in out: out.append(copy.deepcopy(v))
            else:
                for x in v.values(): scan(x)
        elif isinstance(v, list):
            for x in v: scan(x)
    scan(value)
    return out
span = pointer_span(doc)
for p in pointer_span(sheet):
    if p not in span: span.append(p)
span.append({'m_FileID': 0, 'm_PathID': CARD})
meta['m_Container'].append((GUID, {'preloadIndex': len(meta['m_PreloadTable']), 'preloadSize': len(span),
                                  'asset': {'m_FileID': 0, 'm_PathID': CARD}}))
meta['m_PreloadTable'].extend(span)
meta['m_Container'].sort(key=lambda item: item[0])
save(W, bundle, meta)
spec = importlib.util.spec_from_file_location('catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
cat = cm.Catalog(before[GAME.parent / 'catalog.bin'])
assert GUID not in dict(cat.keys())
template_loc = cat.locations('d7961b53b2635ae7b8996007ff34bf6b')[0]
cat = cm.Catalog(cat.add_key_location(GUID, template_loc, template_loc))
idx = next(i for i, (key, _) in enumerate(cat.keys()) if key == 'GameWorldVisualTreeAssetPreload')
keyobj, locset = cat.key_records[idx]
locs = [v[0] for v in cat.array(locset, 'I')] + cat.locations(GUID)
records = list(cat.key_records)
records[idx] = (keyobj, cat.append(b''.join(struct.pack('<I', p) for p in locs), True))
struct.pack_into('<I', cat.data, 8, cat.append(b''.join(struct.pack('<2I', *r) for r in records), True))
catout = bytes(cat.data)
cat = cm.Catalog(catout)
assert cat.location(cat.location(cat.locations(GUID)[0])['dependencies'][0])['internal'].replace('\\', '/').endswith('/' + W)

# Verify all serialized changes and every untouched object before installing.
outputs = {n: e.file.save(packer='lz4') for n, e in env.items()}
verified = {}
for n, b in outputs.items():
    check = {o.path_id: o for o in UnityPy.load(b).objects}
    assert set(check) == set(obs[n]) | set(expected[n])
    for i, o in check.items():
        if i in expected[n]:
            assert json.dumps(o.read_typetree(), sort_keys=True) == json.dumps(expected[n][i], sort_keys=True), (n, i)
        else: assert sha(o.get_raw_data()) == oldhashes[n][i], (n, i)
    verified[n] = len(check) - len(expected[n])
assert source.path_id not in expected[W]
assert sheet_source.path_id not in expected[W]
assert 6067656787038004271 not in expected[L]
assert set(positions) | {CARD_ID} == {c['m_elementID'] for c in layout['m_gridComponents']}
rects = [c['m_location'] for c in layout['m_gridComponents']]
for i, a in enumerate(rects):
    for b in rects[i+1:]:
        assert a['x'] + a['width'] <= b['x'] or b['x'] + b['width'] <= a['x'] or a['y'] + a['height'] <= b['y'] or b['y'] + b['height'] <= a['y']
assert max(a['x'] + a['width'] for a in rects) == 15
assert max(a['y'] + a['height'] for a in rects) == 10
oldcat = cm.Catalog(before[GAME.parent / 'catalog.bin'])
newkeys = dict(cat.keys())
assert set(newkeys) == set(dict(oldcat.keys())) | {GUID}
for key, locset in oldcat.keys():
    oldlocs = [v[0] for v in oldcat.array(locset, 'I')]
    newlocs = [v[0] for v in cat.array(newkeys[key], 'I')]
    assert newlocs == oldlocs + (cat.locations(GUID) if key == 'GameWorldVisualTreeAssetPreload' else [])
    for loc in oldlocs: assert oldcat.location(loc) == cat.location(loc)

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out = R / ('fc-player-hover-layout-' + stamp)
out.mkdir()
for tag, directory in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag)
    backup.mkdir()
    for n in [W, L, G]: (backup / n).write_bytes(before[directory / n])
    cp = GAME.parent / 'catalog.bin' if tag == 'game' else SKIN / 'catalog.bin'
    (backup / 'catalog.bin').write_bytes(before[cp])
(out / 'backup-game' / 'catalog.hash').write_bytes(before[GAME.parent / 'catalog.hash'])
for n, b in outputs.items(): (out / n).write_bytes(b)
(out / 'card.json').write_text(json.dumps(doc, ensure_ascii=False, indent=2), 'utf8')
(out / 'layout.json').write_text(json.dumps(layout, ensure_ascii=False, indent=2), 'utf8')
(out / 'catalog.bin').write_bytes(catout)
hashout = hashlib.md5(catout).hexdigest().encode('ascii')
(out / 'catalog.hash').write_bytes(hashout)
install = {p / n: b for p in [GAME, SKIN] for n, b in outputs.items()}
install.update({GAME.parent / 'catalog.bin': catout, GAME.parent / 'catalog.hash': hashout, SKIN / 'catalog.bin': catout})
for p, b in before.items(): assert p.read_bytes() == b, ('concurrent change', str(p))
try:
    for p, b in install.items(): p.write_bytes(b)
    for p, b in install.items(): assert p.read_bytes() == b
except BaseException:
    for p in install: p.write_bytes(before[p])
    raise
report = {'installed': True, 'runtime_verified': False, 'output': str(out), 'popup_size': [1080, 640],
          'layout_grid': [15, 10], 'card_guid': GUID, 'card_objects': len(refs), 'card_style_rules': len(sheet['m_Rules']),
          'card_nation_binding': 'person.Nation', 'card_club_binding': 'person.Team',
          'main_player_page_unchanged': True, 'original_six_rating_functions_preserved': True,
          'unrelated_objects_verified': verified, 'after_sha256': {str(p): sha(b) for p, b in install.items()}}
(out / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), 'utf8')
print(json.dumps(report, ensure_ascii=True, indent=2))
