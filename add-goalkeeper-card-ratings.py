import ast
import copy
import datetime
import hashlib
import importlib.util
import json
import random
import struct
import sys
import uuid
from decimal import Decimal, ROUND_HALF_UP
from pathlib import Path

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
GN = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
FN = 'ui-visualfunctions_assets_all.bundle'
FULL = -930000000001001
SUM = -910000000000303
OLD_SUM_GUID = 'd25e07441190434f86b42ec2ec560039'
SPECS = [
    ('扑救', 'GKSaving', [('AerialReach', 30), ('Reflexes', 55), ('Bravery', 5), ('Agility', 5), ('JumpingReach', 5)]),
    ('站位', 'GKPositioning', [('Positioning', 70), ('CommandOfArea', 30)]),
    ('出球', 'GKDistribution', [('Passing', 55), ('Kicking', 45)]),
    ('反应', 'GKReflexes', [('Reflexes', 70), ('Agility', 10), ('Anticipation', 10), ('WorkRate', 10)]),
    ('神经', 'GKNerves', [('Eccentricity', 90), ('Composure', 10)]),
]
OUT = R / ('卡面门将自动切换和负数神经-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
before = {}
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    for name in [GN, WN]:
        path = folder / name; before[path] = path.read_bytes()
        backup = OUT / ('backup-' + tag) / name
        backup.parent.mkdir(exist_ok=True); backup.write_bytes(before[path])
for name in [GN, WN]: assert before[GAME / name] == before[SKIN / name]
catalog_path = GAME.parent / 'catalog.bin'
catalog_before = catalog_path.read_bytes()
(OUT / 'backup-game' / 'catalog.bin').write_bytes(catalog_before)
before[catalog_path] = catalog_before
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
native_text = functions['BindIntAddOrSubstractToSIText'].read_typetree()
native_sum = functions['BindMultipleIntArgsAsSumToDestination'].read_typetree()
templates = json.loads((R / 'movement-sum-node-templates-v37.json').read_text(encoding='utf-8'))
for obj in functions.values():
    for ref in obj.read_typetree().get('references', {}).get('RefIds', []):
        if ref.get('type', {}).get('class'): templates.setdefault(ref['type']['class'], ref)
module = ast.parse((R / 'add-card-six-ratings.py').read_text(encoding='utf-8'))
needed = ['guid', 'gid', 'link', 'socket_source', 'constant', 'make_function', 'check_graph', 'graph_runner', 'validate_ui']
definitions = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in needed]
namespace = dict(globals())
namespace['poolmap'] = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
exec(compile(ast.Module(body=definitions, type_ignores=[]), '<rating graph helpers>', 'exec'), namespace)
guid = namespace['guid']

def make_nerves(tree):
    refs = tree['references']['RefIds']
    cast = next(r['data'] for r in refs if r['data']['m_name'] == 'Read Composure')
    weighted = next(r['data'] for r in refs if r['data']['m_name'] == 'Composure x2')
    sub = copy.deepcopy(templates['GeneralVisualFunction_Subtract_int_int_int'])
    sub['rid'] = max(r['rid'] for r in refs) + 1
    d = sub['data']; d.update(m_name='20 Minus Composure', m_id=guid(), m_parentID=copy.deepcopy(tree['m_id']))
    for key, value in d.items():
        if isinstance(value, dict) and 'm_id' in value:
            value['m_id'] = guid()
            if 'm_sourceID' in value: value['m_sourceID'] = {'m_idBytes': [0] * 16}
    d['m_dataInA']['m_defaultSocketValue'] = {'m_value': 20}
    d['m_dataInB']['m_sourceID'] = copy.deepcopy(cast['m_dataOutIntValue']['m_id'])
    for key in ['m_dataInA', 'm_dataInB']:
        assert weighted[key]['m_sourceID'] == cast['m_dataOutIntValue']['m_id']
        weighted[key]['m_sourceID'] = copy.deepcopy(d['m_dataOutInt32']['m_id'])
    refs.append(sub); tree['m_nodes'].append({'rid': sub['rid']})
    for r in refs:
        if r['type']['class'] != 'ITextElement_SetText': continue
        value = r['data']['m_dataInText']['m_defaultSocketValue']['m_value']
        if value.isdecimal():
            r['data']['m_dataInText']['m_defaultSocketValue']['m_value'] = str(-int(value))
    tree['m_description'] = '-((Eccentricity*90% + (20-Composure)*10%)*5), final half-up; negative values are valid, -- only when input unavailable.'
    return tree

new_trees = []; details = []; tests = 0; rng = random.Random(20261017)
for index, (title, code, attrs) in enumerate(SPECS):
    assert sum(w for a, w in attrs) == 100
    tree = namespace['make_function'](code, attrs)
    if code == 'GKNerves': tree = make_nerves(tree)
    else: tree['m_description'] = 'Goalkeeper rating x5, final half-up. ' + '; '.join(f'{a}={w}%' for a, w in attrs)
    namespace['check_graph'](tree)
    run = namespace['graph_runner'](tree)
    for numerator in range(401):
        score = Decimal(numerator) / 4
        if code == 'GKNerves': score = -score
        expected = str(int(score.quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
        assert run([10] * len(attrs), numerator) == expected, (code, numerator); tests += 1
    samples = [[n] * len(attrs) for n in range(1, 21)] + [[rng.randint(1, 20) for a in attrs] for _ in range(400)]
    for axis in range(len(attrs)):
        for n in range(1, 21):
            v = [10] * len(attrs); v[axis] = n; samples.append(v)
    for values in samples:
        expected = sum(Decimal(w) / 100 * (20 - v if code == 'GKNerves' and a == 'Composure' else v) for (a, w), v in zip(attrs, values)) * 5
        if code == 'GKNerves': expected = -expected
        expected = str(int(expected.quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
        assert run(values) == expected, (code, values); tests += 1
    for axis in range(len(attrs)):
        for missing in [None, 0, -1, 21]:
            v = [10] * len(attrs); v[axis] = missing
            assert run(v) == '--'; tests += 1
    if code == 'GKNerves':
        assert run([10, 10]) == '-50'
        assert run([20, 1]) == '-100'
        assert run([1, 20]) == '-5'
    else:
        assert run([10] * len(attrs)) == '50'
        assert run([20] * len(attrs)) == '100'
    pid = -940000000000200 - index
    key = uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-overview-goalkeeper-card/' + code).hex
    assert pid not in go
    new_trees.append((pid, key, tree))
    details.append({'title': title, 'code': code, 'weights': attrs, 'path_id': pid, 'guid': key,
                    'paths': ['person.attribute' + a.lower() + '.AttributeMinValue' for a, w in attrs]})

af = go[SUM].assets_file
known = {(t.m_ClassName, t.m_NameSpace, t.m_AssemblyName) for t in af.ref_types}
needed_types = {(r['type']['class'], r['type']['ns'], r['type']['asm']) for pid, key, tree in new_trees for r in tree['references']['RefIds']}
assert needed_types <= known
metaobj = next(o for o in go.values() if o.type.name == 'AssetBundle'); meta = metaobj.read_typetree()
for pid, key, tree in new_trees:
    new = copy.copy(go[SUM]); new.path_id = pid; af.objects[pid] = new; new.save_typetree(tree)
    start = len(meta['m_PreloadTable'])
    meta['m_PreloadTable'].extend([copy.deepcopy(tree['m_Script']), {'m_FileID': 0, 'm_PathID': pid}])
    meta['m_Container'].append((key, {'preloadIndex': start, 'preloadSize': 2, 'asset': {'m_FileID': 0, 'm_PathID': pid}}))
meta['m_Container'].sort(key=lambda v: v[0]); metaobj.save_typetree(meta)

boolobj = functions['BindBoolToSwitch']; booltree = boolobj.read_typetree()
fmeta = next(o.read_typetree() for o in fe.objects if o.type.name == 'AssetBundle')
boolkey = next(k for k, v in fmeta['m_Container'] if v['asset']['m_PathID'] == boolobj.path_id)
br = booltree['references']['RefIds']
branch = next(r['data'] for r in br if r['type']['class'] == 'GeneralVisualFunction_Branch')
for port, index in [('m_execOutTrue', 1), ('m_execOutFalse', 0)]:
    output = next(r['data'] for r in br if r['type']['class'] == 'BindableSwitchElement_SetVisibleIndex' and r['data']['m_execInExecInput']['m_id'] == branch[port]['m_destinationID'])
    assert output['m_dataInIndex']['m_defaultSocketValue']['m_value'] == index

doc = wo[FULL].read_typetree(); original_doc = copy.deepcopy(doc)
rr = {r['rid']: r for r in doc['references']['RefIds']}
sid = doc['inlineSheet']['m_PathID']; sheet = wo[sid].read_typetree(); old_sheet = copy.deepcopy(sheet)
def name(r):
    return rr.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name', '')
def named(n): return next(r for r in rr.values() if name(r) == n)
grid = named('OverviewCardSixRatings'); stage = rr[grid['data']['m_Parent']['rid']]
assert name(stage) == 'ReportPortraitLayerStage'
original_grid = copy.deepcopy(grid)
def handle(typ, value):
    pool = {2: 'floats', 3: 'dimensions', 4: 'colors', 7: 'strings'}[typ]
    sheet[pool].append(value)
    return {'m_ValueType': typ, 'valueIndex': len(sheet[pool]) - 1}
def px(v): return handle(3, {'unit': 1, 'value': float(v)})
def pct(v): return handle(3, {'unit': 2, 'value': float(v)})
def en(v): return handle(7, v)
def prop(pid, value): return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [value]}
def rule(props):
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': props, 'line': -1})
    return len(sheet['m_Rules']) - 1
def override(node, properties):
    current = copy.deepcopy(sheet['m_Rules'][node['m_RuleIndex']]['m_Properties']) if node.get('m_RuleIndex', -1) >= 0 else []
    ids = {p['m_Id'] for p in properties}
    node['m_RuleIndex'] = rule([p for p in current if p['m_Id'] not in ids] + properties)
rid = max(rr) + 1
eid = max(r.get('data', {}).get('m_Id', 0) for r in rr.values()) + 1
def pair(node, serial, parent, label, rule_index, append=True):
    global rid, eid
    n, s = copy.deepcopy(node), copy.deepcopy(serial)
    n['rid'], s['rid'] = rid, rid + 1; rid += 2
    n['data'].update(m_Id=eid, m_Parent={'rid': parent}, m_Children=[], m_SerializedData={'rid': s['rid']}, m_RuleIndex=rule_index,
                     m_Classes=[], m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[], m_SkipClone=0)
    s['data'].update(uxmlAssetId=eid, name=label, name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    eid += 1; rr[n['rid']] = n; rr[s['rid']] = s
    doc['references']['RefIds'].extend([n, s])
    if append: rr[parent]['data']['m_Children'].append({'rid': n['rid']})
    return n, s
BC = 'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
def short(s):
    b = s.encode(); assert len(b) < 128
    return bytes([len(b)]) + b
def vf(key, paths):
    b = bytearray([len(paths)])
    for path in paths:
        arg = short(BC) + b'\x01' + short(path); b.extend(struct.pack('<i', len(arg))); b.extend(arg)
    return {'m_target': {'m_guid': key}, 'm_inputs': {'m_variable': {'m_argumentBytes': list(b)}}, 'm_outputs': {'m_variable': {'m_argumentBytes': []}}}

switch_template = named('ReportCAAbove119Switch')
switch_serial = rr[switch_template['data']['m_SerializedData']['rid']]
switch, switch_sd = pair(switch_template, switch_serial, stage['rid'], 'OverviewCardGoalkeeperSwitch', grid['data']['m_RuleIndex'], append=False)
switch_sd['data']['Binding'] = {'m_kind': 2, 'm_direct': {'Path': {'m_path': ''}, 'Nullable': 0}, 'm_visualFunction': vf(boolkey, ['person.IsGoalkeeper'])}
switch_sd['data']['Binding_UxmlAttributeFlags'] = 1
switch_sd['data']['AlwaysInstantiate'] = 0
switch_sd['data']['AlwaysInstantiate_UxmlAttributeFlags'] = 1
stage['data']['m_Children'] = [{'rid': switch['rid']} if c['rid'] == grid['rid'] else c for c in stage['data']['m_Children']]
grid['data']['m_Parent'] = {'rid': switch['rid']}
switch['data']['m_Children'].append({'rid': grid['rid']})
override(grid['data'], [prop(131089, px(0)), prop(131104, px(0)), prop(131105, pct(100)), prop(131087, pct(100))])
gkgrid, _ = pair(grid, rr[grid['data']['m_SerializedData']['rid']], switch['rid'], 'OverviewCardGoalkeeperRatings', grid['data']['m_RuleIndex'])
row_template = named('OverviewCardRatingRow1')
cell_template = named('OverviewCardPaceCell')
title_template = named('OverviewCardPaceTitle'); value_template = named('OverviewCardPaceValue')
gk_title_rule = copy.deepcopy(sheet['m_Rules'][title_template['data']['m_RuleIndex']])
gk_value_rule = copy.deepcopy(sheet['m_Rules'][value_template['data']['m_RuleIndex']])
def text_rule(source, width):
    props = [p for p in copy.deepcopy(source['m_Properties']) if p['m_Id'] != 131105]
    return rule(props + [prop(131105, px(width))])
gk_title_style = text_rule(gk_title_rule, 26)
gk_value_style = text_rule(gk_value_rule, 34)
speed_original = named('OverviewCardPaceValue')
speed_serial = rr[speed_original['data']['m_SerializedData']['rid']]['data']
speed_vf = copy.deepcopy(speed_serial['TextBinding']['m_visualFunction'])
for row_index in range(2):
    row, _ = pair(row_template, rr[row_template['data']['m_SerializedData']['rid']], gkgrid['rid'], 'OverviewGKRatingRow' + str(row_index + 1), row_template['data']['m_RuleIndex'])
    for col in range(3):
        index = row_index * 3 + col
        info = details[index] if index < 5 else {'title': '速度', 'code': 'GKSpeed'}
        cell, _ = pair(cell_template, rr[cell_template['data']['m_SerializedData']['rid']], row['rid'], 'Overview' + info['code'] + 'Cell', cell_template['data']['m_RuleIndex'])
        title, ts = pair(title_template, rr[title_template['data']['m_SerializedData']['rid']], cell['rid'], 'Overview' + info['code'] + 'Title', gk_title_style)
        ts['data'].update(text=info['title'], text_UxmlAttributeFlags=1, DebugDisplay=info['title'])
        value, vs = pair(value_template, rr[value_template['data']['m_SerializedData']['rid']], cell['rid'], 'Overview' + info['code'] + 'Value', gk_value_style)
        vs['data'].update(text='--', text_UxmlAttributeFlags=1, DebugDisplay='--')
        vs['data']['TextBinding']['m_visualFunction'] = vf(info['guid'], info['paths']) if index < 5 else copy.deepcopy(speed_vf)
        vs['data']['TextBinding_UxmlAttributeFlags'] = 1

assert len(switch['data']['m_Children']) == 2
assert switch['data']['m_Children'] == [{'rid': grid['rid']}, {'rid': gkgrid['rid']}]
assert [rr[r['data']['m_SerializedData']['rid']]['data']['text'] for r in rr.values() if name(r).startswith('OverviewGK') and name(r).endswith('Title')] == ['扑救', '站位', '出球', '反应', '神经', '速度']
original_refs = {r['rid']: r for r in original_doc['references']['RefIds']}
allowed = {grid['rid'], stage['rid']}
for rid_, r in original_refs.items():
    if rid_ not in allowed: assert rr[rid_] == r, ('Existing UI node modified', rid_)
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
namespace['validate_ui'](doc, sheet)
wo[FULL].save_typetree(doc); wo[sid].save_typetree(sheet)

spec = importlib.util.spec_from_file_location('gk_catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec); spec.loader.exec_module(cm)
catalog_data = catalog_before
for pid, key, tree in new_trees:
    cat = cm.Catalog(catalog_data); loc = cat.locations(OLD_SUM_GUID)[0]
    catalog_data = cat.add_key_location(key, loc, loc)
assert catalog_data[:8] == catalog_before[:8] and catalog_data[12:len(catalog_before)] == catalog_before[12:]
cat = cm.Catalog(catalog_data)
assert cat.locations(boolkey)
for pid, key, tree in new_trees: assert len(cat.locations(key)) == 1
result = {GN: ge.file.save(packer='lz4'), WN: we.file.save(packer='lz4')}
for n, data in result.items(): (OUT / n).write_bytes(data)
(OUT / 'catalog.bin').write_bytes(catalog_data)
savedg = {o.path_id: o for o in UnityPy.load(result[GN]).objects}
savedw = {o.path_id: o for o in UnityPy.load(result[WN]).objects}
assert set(savedg) == set(go) | {pid for pid, key, tree in new_trees}
assert set(savedw) == set(wo)
for i, h in gh.items():
    if i == metaobj.path_id: assert savedg[i].read_typetree() == meta
    else: assert sha(savedg[i].get_raw_data()) == h
for i, h in wh.items():
    if i in [FULL, sid]: assert savedw[i].read_typetree() == {FULL: doc, sid: sheet}[i]
    else: assert sha(savedw[i].get_raw_data()) == h
for pid, key, tree in new_trees:
    reread = savedg[pid].read_typetree(); assert reread == tree
    namespace['check_graph'](reread)
    assert namespace['graph_runner'](reread)([10] * (len(tree['m_inputs']) - 2)) == ('-50' if tree['m_Name'].endswith('GKNervesRating') else '50')
namespace['validate_ui'](savedw[FULL].read_typetree(), savedw[sid].read_typetree())
for path, data in before.items(): assert path.read_bytes() == data, ('Source changed', str(path))
for path, expected in protected.items(): assert sha(path.read_bytes()) == expected
try:
    for folder in [GAME, SKIN]:
        for n, data in result.items():
            (folder / n).write_bytes(data); assert (folder / n).read_bytes() == data
    catalog_path.write_bytes(catalog_data); assert catalog_path.read_bytes() == catalog_data
except Exception:
    for path, data in before.items(): path.write_bytes(data)
    raise
report = {'installed': True, 'runtime_verified': False, 'condition': 'person.IsGoalkeeper',
          'goalkeeper_titles': ['扑救', '站位', '出球', '反应', '神经', '速度'],
          'outfield_titles_preserved': ['速度', '射门', '传球', '盘带', '防守', '身体'],
          'goalkeeper_formulas': details, 'goalkeeper_speed_reuses_outfield_speed_function': True,
          'nerves_negative': True, 'rounding': 'final half-up, negative ties away from zero',
          'tests_passed': tests, 'new_function_count': 5, 'negative_value_width': 34,
          'second_version_and_outfield_functions_preserved': True, 'portrait_card_textures_and_layout_preserved': True,
          'unchanged_global_objects_verified': len(gh) - 1, 'unchanged_world_objects_verified': len(wh) - 2,
          'before_sha256': {str(p): sha(data) for p, data in before.items()},
          'after_sha256': {n: sha(data) for n, data in result.items()}, 'after_catalog_sha256': sha(catalog_data)}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), 'installed': True, 'tests_passed': tests,
                  'goalkeeper_titles': report['goalkeeper_titles'], 'after_sha256': report['after_sha256']}, ensure_ascii=False, indent=2))
