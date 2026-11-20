import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import struct
import sys
import uuid
from pathlib import Path

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
WN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
GN = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
FN = 'ui-visualfunctions_assets_all.bundle'
FULL = -930000000001001
SUM = -910000000000303
FORMAT_PID = -940000000000300
FORMAT_KEY = uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-card-native-league-rating-missing-dashes').hex
STAMP = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
OUT = R / ('卡面顶部状态左侧资料底部擅长脚-' + STAMP)
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
before = {}
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    for n in [GN, WN]:
        path = folder / n; before[path] = path.read_bytes()
        backup = OUT / ('backup-' + tag) / n
        backup.parent.mkdir(exist_ok=True); backup.write_bytes(before[path])
for n in [GN, WN]: assert before[GAME / n] == before[SKIN / n], ('Game/skin differ', n)
catpath = GAME.parent / 'catalog.bin'; catbefore = catpath.read_bytes()
before[catpath] = catbefore
(OUT / 'backup-game' / 'catalog.bin').write_bytes(catbefore)
protected = {GAME / n: sha((GAME / n).read_bytes()) for n in [FN, 'ui-backgrounds_assets_common.bundle', 'ui-tileslayouts_assets_all.bundle']}
oldwrite = TypeTreeHelper.write_value
def write(v, n, w, c):
    if n.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(v, c.assetsfile) is None:
        for ch in n.m_Children:
            if ch.m_Type != 'ReferencedObjectData': oldwrite(v[ch.m_Name], ch, w, c)
        if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag): w.align_stream()
        return
    return oldwrite(v, n, w, c)
TypeTreeHelper.write_value = write

ge = UnityPy.load(before[GAME / GN]); go = {o.path_id: o for o in ge.objects}
we = UnityPy.load(before[GAME / WN]); wo = {o.path_id: o for o in we.objects}
gh = {i: sha(o.get_raw_data()) for i, o in go.items()}
wh = {i: sha(o.get_raw_data()) for i, o in wo.items()}
fe = UnityPy.load(str(GAME / FN))
functions = {o.peek_name(): o for o in fe.objects if o.type.name == 'MonoBehaviour'}
native_rating = functions['PlayerRating']
formatter = copy.deepcopy(native_rating.read_typetree())
formatter['m_Script'] = copy.deepcopy(go[SUM].read_typetree()['m_Script'])
formatter.update(m_Name='OverviewCardLeagueRatingText', m_name='OverviewCardLeagueRatingText',
                 m_description='Native PlayerRating formatting with -- for absent/nonpositive rating; used only by the card league summary.')
idmap = {}
def remap_ids(v):
    if isinstance(v, dict):
        if set(v) == {'m_idBytes'}:
            old = bytes(v['m_idBytes'])
            if any(old): v['m_idBytes'] = idmap.setdefault(old, list(uuid.uuid4().bytes_le))
        else:
            for x in v.values(): remap_ids(x)
    elif isinstance(v, list):
        for x in v: remap_ids(x)
remap_ids(formatter)
missing = []
for r in formatter['references']['RefIds']:
    if r['type']['class'] == 'ITextElement_SetText':
        p = r['data']['m_dataInText']
        if p.get('m_defaultSocketValue', {}).get('m_value') == '-':
            p['m_defaultSocketValue']['m_value'] = '--'; missing.append(r['rid'])
assert len(missing) == 1
af = go[SUM].assets_file
needed = {(r['type']['class'], r['type']['ns'], r['type']['asm']) for r in formatter['references']['RefIds']}
known = {(t.m_ClassName, t.m_NameSpace, t.m_AssemblyName) for t in af.ref_types}
for t in native_rating.assets_file.ref_types:
    key = (t.m_ClassName, t.m_NameSpace, t.m_AssemblyName)
    if key in needed and key not in known: af.ref_types.append(copy.copy(t)); known.add(key)
assert needed <= known and FORMAT_PID not in go
fo = copy.copy(go[SUM]); fo.path_id = FORMAT_PID; af.objects[FORMAT_PID] = fo; fo.save_typetree(formatter)
gmobj = next(o for o in go.values() if o.type.name == 'AssetBundle'); gm = gmobj.read_typetree()
start = len(gm['m_PreloadTable'])
gm['m_PreloadTable'].extend([copy.deepcopy(formatter['m_Script']), {'m_FileID': 0, 'm_PathID': FORMAT_PID}])
gm['m_Container'].append((FORMAT_KEY, {'preloadIndex': start, 'preloadSize': 2, 'asset': {'m_FileID': 0, 'm_PathID': FORMAT_PID}}))
gm['m_Container'].sort(key=lambda x: x[0]); gmobj.save_typetree(gm)

doc = wo[FULL].read_typetree(); old_doc = copy.deepcopy(doc)
rr = {r['rid']: r for r in doc['references']['RefIds']}
sid = doc['inlineSheet']['m_PathID']; sheet = wo[sid].read_typetree(); old_sheet = copy.deepcopy(sheet)
def named(name):
    return next(r for r in rr.values() if rr.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == name)
stage = named('ReportPortraitLayerStage')
portrait = next(r for r in rr.values() if r.get('data', {}).get('m_Parent', {}).get('rid') == stage['rid'] and rr.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == 'PersonPictureFrame')
status = rr[1172]
assert status['data']['m_Parent']['rid'] == stage['rid']
def val(typ, value):
    pool = {2: 'floats', 3: 'dimensions', 4: 'colors', 7: 'strings'}[typ]
    sheet[pool].append(value); return {'m_ValueType': typ, 'valueIndex': len(sheet[pool]) - 1}
def px(v): return val(3, {'unit': 1, 'value': float(v)})
def pct(v): return val(3, {'unit': 2, 'value': float(v)})
def en(v): return val(7, v)
def num(v): return val(2, float(v))
def color(r, g, b, a=255):
    values = [struct.unpack('<f', struct.pack('<f', n / 255))[0] for n in [r, g, b, a]]
    return val(4, dict(zip(['r', 'g', 'b', 'a'], values)))
def prop(pid, *v): return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1, 'm_Values': list(v)}
def rule(props):
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': props, 'line': -1})
    return len(sheet['m_Rules']) - 1
def override(node, props):
    old = copy.deepcopy(sheet['m_Rules'][node['m_RuleIndex']]['m_Properties']) if node.get('m_RuleIndex', -1) >= 0 else []
    keys = {p['m_Id'] for p in props}
    node['m_RuleIndex'] = rule([p for p in old if p['m_Id'] not in keys] + props)
def zero(): return [prop(262150, px(0)), prop(262151, px(0))]
def box(x, y, w, h, extra=None):
    return rule([prop(131102, en('absolute')), prop(131089, px(x)), prop(131104, px(y)),
                 prop(131105, px(w)), prop(131087, px(h)), prop(131084, num(0)), prop(131085, num(0))] + zero() + (extra or []))
def text_style(w, h, size, bold=False, align='middle-left', wrap='nowrap', black=False):
    return rule([prop(131105, px(w)), prop(131087, px(h)), prop(131097, px(0)), prop(131084, num(0)), prop(131085, num(0)),
                 prop(65537, px(size)), prop(65543, en('bold' if bold else 'normal')), prop(65546, en(align)),
                 prop(65552, en(wrap)), prop(65536, color(0, 0, 0) if black else color(255, 255, 255))] + zero())
override(portrait['data'], [prop(131105, px(128)), prop(131087, px(128)), prop(131089, px(193)), prop(131104, px(34))])
status['data']['m_Classes'] = [c for c in status['data'].get('m_Classes', []) if not c.startswith('margin-')]
override(status['data'], [prop(131089, px(135)), prop(131104, px(0)), prop(131105, px(180)), prop(131087, px(20)),
                          prop(131083, en('row')), prop(131073, en('center')), prop(131088, en('center'))] + zero())
rid = max(rr) + 1
eid = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
def pair(nt, st, parent, name, ri):
    global rid, eid
    n, s = copy.deepcopy(nt), copy.deepcopy(st)
    n['rid'], s['rid'] = rid, rid + 1; rid += 2
    n['data'].update(m_Id=eid, m_Parent={'rid': parent}, m_Children=[], m_SerializedData={'rid': s['rid']}, m_RuleIndex=ri,
                     m_Classes=[], m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[], m_SkipClone=0)
    s['data'].update(uxmlAssetId=eid, name=name, name_UxmlAttributeFlags=1)
    eid += 1; rr[n['rid']] = n; rr[s['rid']] = s
    doc['references']['RefIds'].extend([n, s]); rr[parent]['data']['m_Children'].append({'rid': n['rid']})
    return n, s
ve = named('ReportPortraitLayerStage'); ves = rr[ve['data']['m_SerializedData']['rid']]
text = named('PersonHeightText'); texts = rr[text['data']['m_SerializedData']['rid']]
def ve_pair(parent, name, ri): return pair(ve, ves, parent, name, ri)
def text_pair(parent, name, ri):
    n, s = pair(text, texts, parent, name, ri)
    s['data'].update(text='--', text_UxmlAttributeFlags=1, DebugDisplay='--', pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    return n, s
def short(s):
    b = s.encode(); assert len(b) < 128
    return bytes([len(b)]) + b
def decode_args(a):
    b = bytes(a); p = 1; out = []
    for _ in range(b[0]):
        n = struct.unpack_from('<i', b, p)[0]; p += 4; z = b[p:p+n]; p += n
        l = z[0]; out.append((z[1:1+l].decode(), z[1+l:]))
    assert p == len(b); return out
def encode_args(args):
    b = bytearray([len(args)])
    for cls, value in args:
        z = short(cls) + value; b.extend(struct.pack('<i', len(z))); b.extend(z)
    return list(b)
def visual(key, args):
    return {'m_target': {'m_guid': key}, 'm_inputs': {'m_variable': {'m_argumentBytes': encode_args(args)}}, 'm_outputs': {'m_variable': {'m_argumentBytes': []}}}
def direct(sd, path):
    sd['TextBinding'] = {'m_kind': 1, 'm_direct': {'Path': {'m_path': path}, 'Nullable': 0}, 'm_visualFunction': visual('', [])}
    sd['TextBinding_UxmlAttributeFlags'] = 1
def translated(sd, gameid):
    sd['TextBinding'] = {'m_kind': 2, 'm_direct': {'Path': {'m_path': ''}, 'Nullable': 0},
                         'm_visualFunction': visual('eae2be944eee9e2449baef416111a087', [('SI.VisualScripting.GenericVisualArg`1[SI.Translation.TranslationID]', struct.pack('<i', gameid) + b'\x01\x00')])}
    sd['TextBinding_UxmlAttributeFlags'] = 1

# Native table headings are localized by the game; displayed values stay in the current player's scope.
left, _ = ve_pair(stage['rid'], 'CardNativePlayerSummary', box(126, 28, 60, 145, [prop(131083, en('column'))]))
fields = [('CurrentAbility', 15234, 'person.PlayerCurrentAbility', 24),
          ('PotentialAbility', 15235, 'person.PlayerPotentialAbility', 24),
          ('BestPosition', 17185, 'person.BestPositionShortString', 36),
          ('Height', 3178, None, 24), ('LeagueRating', 4358, None, 24)]
title_style = text_style(60, 11, 9)
value_style = text_style(60, 13, 11, True)
position_style = text_style(60, 25, 10, False, wrap='normal')
field_bindings = []
for index, (label, title_id, path, height) in enumerate(fields):
    group_style = rule([prop(131105, px(60)), prop(131087, px(height)), prop(131085, num(0)), prop(131090, px(0 if index == 4 else 3))] + [prop(262151, px(0))])
    if label == 'LeagueRating':
        n, sd = pair(rr[1321], rr[1322], left['rid'], 'CardLeagueStatsScope', group_style)
        cn, cs = copy.deepcopy(rr[1323]), copy.deepcopy(rr[1324])
        cn['rid'], cs['rid'] = rid, rid+1; rid += 2
        cn['data'].update(m_Id=eid, m_Parent={'rid': n['rid']}, m_ParentId=n['data']['m_Id'])
        cs['data']['uxmlAssetId'] = eid; eid += 1
        rr[cn['rid']], rr[cs['rid']] = cn, cs
        doc['references']['RefIds'].extend([cn, cs]); n['data']['m_Children'].append({'rid': cn['rid']})
        sd['data']['m_components'] = [{'rid': cs['rid']}]; sd['data']['m_components_UxmlAttributeFlags'] = 1
    else:
        n, sd = ve_pair(left['rid'], 'Card' + label + 'Field', group_style)
    title, ts = text_pair(n['rid'], 'Card' + label + 'Title', title_style); translated(ts['data'], title_id)
    value, vs = text_pair(n['rid'], 'Card' + label + 'Value', position_style if label == 'BestPosition' else value_style)
    if path:
        direct(vs['data'], path)
    elif label == 'Height':
        # Preserve the game's unit-aware height formatter, changing only the scope prefix.
        tb = copy.deepcopy(texts['data']['TextBinding']); args = decode_args(tb['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        old = short('Person.Height'); new = short('person.Height')
        assert sum(v.count(old) for c, v in args) == 1
        args = [(c, v.replace(old, new)) for c, v in args]
        tb['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = encode_args(args)
        vs['data']['TextBinding'] = tb; vs['data']['TextBinding_UxmlAttributeFlags'] = 1
        path = 'person.Height'
    else:
        native_cell = go[1947022288692900776].read_typetree()
        native_sd = next(r['data'] for r in native_cell['references']['RefIds'] if r['type']['class'] == 'SIText/UxmlSerializedData')
        tb = copy.deepcopy(native_sd['TextBinding']); tb['m_visualFunction']['m_target']['m_guid'] = FORMAT_KEY
        args = decode_args(tb['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        assert args[1][1] == b'\x01' + short('binding')
        args[1] = (args[1][0], b'\x01' + short('SeasonStats.AverageRating'))
        tb['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = encode_args(args)
        vs['data']['TextBinding'] = tb; vs['data']['TextBinding_UxmlAttributeFlags'] = 1
        path = 'SeasonStats.AverageRating (competition = person.Division; season = current)'
    field_bindings.append({'field': label, 'title_game_id': title_id, 'path': path})

footer, _ = ve_pair(stage['rid'], 'CardNativeFootFooter', box(138, 235, 174, 20))
badge, _ = ve_pair(footer['rid'], 'CardPreferredFootBadge', box(61, 0, 52, 20, [prop(458752, color(15, 230, 150)), prop(262147, px(2))]))
foot_text, foot_sd = text_pair(badge['rid'], 'CardPreferredFootText', text_style(52, 20, 10, True, align='middle-center', black=True))
direct(foot_sd['data'], 'person.Footedness.PreferredFootString')

# Use exactly the control used by PlayerReportFootednessBlock, including native initialization and styling.
native_stepper_doc = wo[9005638743778272087].read_typetree()
sr = {r['rid']: r for r in native_stepper_doc['references']['RefIds']}
for side, x in [('Left', 0), ('Right', 120)]:
    step, step_sd = pair(sr[1016], sr[1022], footer['rid'], 'Card' + side + 'FootNativeStepper', box(x, 7, 54, 6))
    args = decode_args(step_sd['data']['BindFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    assert len(args) == 1 and args[0][1] == b'\x01' + short('footednessValue')
    args[0] = (args[0][0], b'\x01' + short('person.Footedness.' + side + 'Footedness'))
    step_sd['data']['BindFunction']['m_inputs']['m_variable']['m_argumentBytes'] = encode_args(args)
    assert step_sd['data']['InitFunction'] == sr[1022]['data']['InitFunction']
    assert step_sd['data']['StyleFunction'] == sr[1022]['data']['StyleFunction']

# Preserve the complete existing summary switch subtree, all original style rules, and every background texture.
old_refs = {r['rid']: r for r in old_doc['references']['RefIds']}
changed_old = [i for i, r in old_refs.items() if rr[i] != r]
assert set(changed_old) == {portrait['rid'], status['rid'], stage['rid']}, changed_old
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
rating_root = named('OverviewCardGoalkeeperSwitch')['rid']
def subtree(root):
    result = {root}
    for child in rr[root].get('data', {}).get('m_Children', []): result |= subtree(child['rid'])
    serial = rr[root].get('data', {}).get('m_SerializedData', {}).get('rid', -2)
    if serial != -2: result.add(serial)
    return result
ratings = subtree(rating_root)
assert all(rr[i] == old_refs[i] for i in ratings)
def layout_dimension(node, pid):
    p = next(p for p in sheet['m_Rules'][node['data']['m_RuleIndex']]['m_Properties'] if p['m_Id'] == pid)
    h = p['m_Values'][0]
    assert h['m_ValueType'] == 3
    return sheet['dimensions'][h['valueIndex']]['value']
ratings_top = layout_dimension(named('OverviewCardGoalkeeperSwitch'), 131104)
ratings_bottom = ratings_top + layout_dimension(named('OverviewCardGoalkeeperSwitch'), 131087)
assert layout_dimension(portrait, 131104) + layout_dimension(portrait, 131087) <= ratings_top
assert layout_dimension(left, 131104) + layout_dimension(left, 131087) <= ratings_top
assert layout_dimension(footer, 131104) >= ratings_bottom
assert layout_dimension(status, 131104) + layout_dimension(status, 131087) <= layout_dimension(left, 131104)
assert sum(field[3] for field in fields) + 3 * 4 <= layout_dimension(left, 131087)
assert layout_dimension(footer, 131089) + layout_dimension(footer, 131105) / 2 == 225
assert layout_dimension(named('ReportMiddleCA000Layer'), 131105) == 286
assert layout_dimension(named('ReportMiddleCA000Layer'), 131087) == 286
known_w = {(t.m_ClassName, t.m_NameSpace, t.m_AssemblyName) for t in wo[FULL].assets_file.ref_types}
assert all((r['type']['class'], r['type']['ns'], r['type']['asm']) in known_w for r in doc['references']['RefIds'] if r['rid'] != -2)
module = ast.parse((R / 'add-card-six-ratings.py').read_text(encoding='utf-8'))
needed_defs = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in ['gid', 'check_graph', 'validate_ui']]
ns = {'poolmap': {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}}
exec(compile(ast.Module(body=needed_defs, type_ignores=[]), '<existing validators>', 'exec'), ns)
ns['check_graph'](formatter); ns['validate_ui'](doc, sheet)
wo[FULL].save_typetree(doc); wo[sid].save_typetree(sheet)

spec = importlib.util.spec_from_file_location('card_detail_catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec); spec.loader.exec_module(cm)
cat = cm.Catalog(catbefore); oldloc = cat.locations('d25e07441190434f86b42ec2ec560039')[0]
catdata = cat.add_key_location(FORMAT_KEY, oldloc, oldloc)
cat = cm.Catalog(catdata)
assert cat.locations(FORMAT_KEY)
for key in ['eae2be944eee9e2449baef416111a087', 'a31a1c2912379524abe612de3fe1e494', '025ba7f4a4107f4478cf38460e2b096d', 'e7e379c75b5c63e40ba99ed2c0aba362', '106526b643a418c4c8e20bbdcd5ca56d']:
    assert cat.locations(key), ('Missing native dependency', key)
result = {GN: ge.file.save(packer='lz4'), WN: we.file.save(packer='lz4')}
for n, data in result.items(): (OUT / n).write_bytes(data)
(OUT / 'catalog.bin').write_bytes(catdata)
savedg = {o.path_id: o for o in UnityPy.load(result[GN]).objects}
savedw = {o.path_id: o for o in UnityPy.load(result[WN]).objects}
assert set(savedg) == set(go) | {FORMAT_PID} and set(savedw) == set(wo)
for i, h in gh.items():
    if i == gmobj.path_id: assert savedg[i].read_typetree() == gm
    else: assert sha(savedg[i].get_raw_data()) == h, ('Unrelated global asset changed', i)
assert savedg[FORMAT_PID].read_typetree() == formatter
for i, h in wh.items():
    if i in [FULL, sid]: assert savedw[i].read_typetree() == {FULL: doc, sid: sheet}[i]
    else: assert sha(savedw[i].get_raw_data()) == h, ('Unrelated world asset changed', i)
ns['validate_ui'](savedw[FULL].read_typetree(), savedw[sid].read_typetree())
for path, old in before.items(): assert path.read_bytes() == old, ('Target changed during build', str(path))
for path, expected in protected.items(): assert sha(path.read_bytes()) == expected
report = {'installed': False, 'runtime_verified': False, 'portrait': {'size': [128, 128], 'left': 193, 'top': 34},
          'native_status': {'left': 135, 'top': 0, 'width': 180, 'height': 20, 'original_subtree_preserved': True},
          'left_fields': field_bindings, 'preferred_foot_path': 'person.Footedness.PreferredFootString',
          'foot_stepper_source': 'PlayerReportFootednessBlock -> FootednessStepperWithBorderCell',
          'six_ratings_nodes_and_styles_preserved': len(ratings), 'second_version_and_all_textures_preserved': True,
          'all_existing_calculation_functions_preserved': True, 'new_private_formatter': FORMAT_KEY,
          'unchanged_global_objects_verified': len(gh) - 1, 'unchanged_world_objects_verified': len(wh) - 2,
          'before_catalog_sha256': sha(catbefore), 'protected_game_sha256': {p.name: h for p, h in protected.items()},
          'before_sha256': {str(p): sha(data) for p, data in before.items()},
          'after_sha256': {n: sha(data) for n, data in result.items()}, 'after_catalog_sha256': sha(catdata)}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
if '--install' in sys.argv:
    try:
        for folder in [GAME, SKIN]:
            for n, data in result.items():
                (folder / n).write_bytes(data); assert (folder / n).read_bytes() == data
        catpath.write_bytes(catdata); assert catpath.read_bytes() == catdata
    except Exception:
        for path, data in before.items(): path.write_bytes(data)
        raise
    report['installed'] = True
    (OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), 'installed': report['installed'], 'six_ratings_records_preserved': len(ratings), 'after_sha256': report['after_sha256']}, ensure_ascii=False, indent=2))
