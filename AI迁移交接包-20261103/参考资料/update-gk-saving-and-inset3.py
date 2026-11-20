import ast
import copy
import datetime
import hashlib
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
SUM = -910000000000303
FULL = -930000000001001
SAVING = -940000000000200
ATTRS = [('AerialReach', 30), ('Reflexes', 55), ('Bravery', 5), ('Agility', 5), ('JumpingReach', 5)]
OUT = R / ('扑救新公式和两侧内收3px-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda data: hashlib.sha256(data).hexdigest()
before = {}
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    for name in [GN, WN]:
        path = folder / name; before[path] = path.read_bytes()
        backup = OUT / ('backup-' + tag) / name
        backup.parent.mkdir(exist_ok=True); backup.write_bytes(before[path])
for name in [GN, WN]: assert before[GAME / name] == before[SKIN / name]
protected = {GAME / n: sha((GAME / n).read_bytes()) for n in [FN, 'ui-backgrounds_assets_common.bundle', 'ui-tileslayouts_assets_all.bundle']}
protected[GAME.parent / 'catalog.bin'] = sha((GAME.parent / 'catalog.bin').read_bytes())
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
names = ['guid', 'gid', 'link', 'socket_source', 'constant', 'make_function', 'check_graph', 'graph_runner', 'validate_ui']
ns = dict(globals()); ns['poolmap'] = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
exec(compile(ast.Module(body=[n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in names], type_ignores=[]), '<existing graph helpers>', 'exec'), ns)
tree = ns['make_function']('GKSaving', ATTRS)
tree['m_description'] = 'Goalkeeper saving = (AerialReach*30% + Reflexes*55% + Bravery*5% + Agility*5% + JumpingReach*5%)*5; final half-up.'
ns['check_graph'](tree); run = ns['graph_runner'](tree)
tests = 0; rng = random.Random(20261017)
for numerator in range(401):
    expected = str(int((Decimal(numerator) / 4).quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
    assert run([10] * 5, numerator) == expected; tests += 1
samples = [[n] * 5 for n in range(1, 21)] + [[rng.randint(1, 20) for a in ATTRS] for _ in range(400)]
for axis in range(5):
    for v in range(1, 21):
        values = [10] * 5; values[axis] = v; samples.append(values)
for values in samples:
    expected = sum(Decimal(w) / 100 * v for (a, w), v in zip(ATTRS, values)) * 5
    assert run(values) == str(int(expected.quantize(Decimal('1'), rounding=ROUND_HALF_UP))); tests += 1
for axis in range(5):
    for missing in [None, -1, 0, 21]:
        values = [10] * 5; values[axis] = missing
        assert run(values) == '--'; tests += 1
go[SAVING].save_typetree(tree)

doc = wo[FULL].read_typetree(); original_doc = copy.deepcopy(doc)
refs = {r['rid']: r for r in doc['references']['RefIds']}
sid = doc['inlineSheet']['m_PathID']; sheet = wo[sid].read_typetree(); old_sheet = copy.deepcopy(sheet)
def node_name(r): return refs.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name', '')
def named(name): return next(r for r in refs.values() if node_name(r) == name)
sd = refs[named('OverviewGKSavingValue')['data']['m_SerializedData']['rid']]['data']
BC = 'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
def short(s):
    b = s.encode(); assert len(b) < 128
    return bytes([len(b)]) + b
encoded = bytearray([len(ATTRS)])
for attr, weight in ATTRS:
    arg = short(BC) + b'\x01' + short('person.attribute' + attr.lower() + '.AttributeMinValue')
    encoded.extend(struct.pack('<i', len(arg))); encoded.extend(arg)
sd['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = list(encoded)
switch_rule = named('OverviewCardGoalkeeperSwitch')['data']['m_RuleIndex']
cell_rule = named('OverviewCardPaceCell')['data']['m_RuleIndex']
outfield_value_rule = named('OverviewCardPaceValue')['data']['m_RuleIndex']
gk_value_rule = named('OverviewGKSavingValue')['data']['m_RuleIndex']
def dim(rule, pid):
    p = next(p for p in sheet['m_Rules'][rule]['m_Properties'] if p['m_Id'] == pid)
    h = p['m_Values'][0]; assert len(p['m_Values']) == 1 and h['m_ValueType'] == 3
    d = sheet['dimensions'][h['valueIndex']]; assert d['unit'] == 1
    return d['value']
def set_px(rule, pid, value):
    p = next(p for p in sheet['m_Rules'][rule]['m_Properties'] if p['m_Id'] == pid)
    sheet['dimensions'].append({'unit': 1, 'value': float(value)})
    p['m_Values'] = [{'m_ValueType': 3, 'valueIndex': len(sheet['dimensions']) - 1}]
left, width = dim(switch_rule, 131089), dim(switch_rule, 131105)
assert width == 180 and dim(cell_rule, 131105) == 60
assert all(named('Overview' + code + 'Cell')['data']['m_RuleIndex'] == cell_rule for code in ['GKSaving', 'GKPositioning', 'GKDistribution', 'GKReflexes', 'GKNerves', 'GKSpeed'])
set_px(switch_rule, 131089, left + 3)
set_px(switch_rule, 131105, width - 6)
set_px(cell_rule, 131105, (width - 6) / 3)
# Preserve title font sizes and leave enough room for the signed three-digit goalkeeper value.
set_px(outfield_value_rule, 131105, 26)
set_px(gk_value_rule, 131105, 32)
assert dim(switch_rule, 131089) + dim(switch_rule, 131105) / 2 == left + width / 2
assert dim(switch_rule, 131089) - left == 3
assert (left + width) - (dim(switch_rule, 131089) + dim(switch_rule, 131105)) == 3
assert 26 + 32 == dim(cell_rule, 131105)
assert 28 + 26 <= dim(cell_rule, 131105)
assert [a['rid'] for a, b in zip(doc['references']['RefIds'], original_doc['references']['RefIds']) if a != b] == [named('OverviewGKSavingValue')['data']['m_SerializedData']['rid']]
assert {i for i, (a, b) in enumerate(zip(old_sheet['m_Rules'], sheet['m_Rules'])) if a != b} == {switch_rule, cell_rule, outfield_value_rule, gk_value_rule}
ns['validate_ui'](doc, sheet)
wo[FULL].save_typetree(doc); wo[sid].save_typetree(sheet)
result = {GN: ge.file.save(packer='lz4'), WN: we.file.save(packer='lz4')}
for n, data in result.items(): (OUT / n).write_bytes(data)
for n, hashes, changes in [(GN, gh, {SAVING: tree}), (WN, wh, {FULL: doc, sid: sheet})]:
    saved = {o.path_id: o for o in UnityPy.load(result[n]).objects}
    assert set(saved) == set(hashes)
    for i, h in hashes.items():
        if i in changes: assert saved[i].read_typetree() == changes[i]
        else: assert sha(saved[i].get_raw_data()) == h, ('Unrelated asset changed', n, i)
    if n == GN:
        ns['check_graph'](saved[SAVING].read_typetree())
        assert ns['graph_runner'](saved[SAVING].read_typetree())([10] * 5) == '50'
for path, data in before.items(): assert path.read_bytes() == data
for path, expected in protected.items(): assert sha(path.read_bytes()) == expected
try:
    for folder in [GAME, SKIN]:
        for n, data in result.items():
            (folder / n).write_bytes(data); assert (folder / n).read_bytes() == data
except Exception:
    for path, data in before.items(): path.write_bytes(data)
    raise
report = {'installed': True, 'runtime_verified': False, 'saving_formula': ATTRS,
          'tests_passed': tests, 'rating_width': width - 6, 'rating_left': left + 3, 'additional_side_inset': 3,
          'goalkeeper_signed_value_width': 32, 'fonts_colors_and_other_formulas_preserved': True,
          'before_sha256': {str(p): sha(b) for p, b in before.items()}, 'after_sha256': {n: sha(b) for n, b in result.items()},
          'unchanged_global_objects_verified': len(gh) - 1, 'unchanged_world_objects_verified': len(wh) - 2}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), 'installed': True, 'tests_passed': tests, 'additional_side_inset': 3, 'after_sha256': report['after_sha256']}, ensure_ascii=False, indent=2))
