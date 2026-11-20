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
FULL = -930000000001001
SUM = -910000000000303
TEXT_HEX = '#FFFFFF'
TEXT_COLOR = {'r': 1.0, 'g': 1.0, 'b': 1.0, 'a': 1.0}
SPECS = [
    ('射门', 'Shooting', -940000000000101, [('Finishing', 65), ('LongShots', 10), ('Movement', 10), ('PenaltyTaking', 5), ('Heading', 10)]),
    ('传球', 'Passing', -940000000000102, [('Passing', 55), ('Vision', 15), ('Crossing', 15), ('FreeKicks', 5), ('LongThrows', 5), ('Corners', 5)]),
    ('盘带', 'Dribbling', -940000000000103, [('Dribbling', 70), ('FirstTouch', 5), ('Technique', 5), ('Agility', 5), ('Reflexes', 5), ('Composure', 5), ('Balance', 5)]),
    ('防守', 'Defending', -940000000000104, [('Tackling', 35), ('Positioning', 30), ('Marking', 20), ('Heading', 10), ('WorkRate', 5)]),
    ('身体', 'Physical', -940000000000105, [('Strength', 55), ('Stamina', 10), ('JumpingReach', 20), ('NaturalFitness', 15)]),
]
sha = lambda b: hashlib.sha256(b).hexdigest()
OUT = R / ('卡面新公式白色文字和新图-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
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
hashes = {GN: {i: sha(o.get_raw_data()) for i, o in go.items()}, WN: {i: sha(o.get_raw_data()) for i, o in wo.items()}}
fe = UnityPy.load(str(GAME / FN))
functions = {o.peek_name(): o for o in fe.objects if o.type.name == 'MonoBehaviour'}
templates = json.loads((R / 'movement-sum-node-templates-v37.json').read_text(encoding='utf-8'))
for obj in functions.values():
    for ref in obj.read_typetree().get('references', {}).get('RefIds', []):
        if ref.get('type', {}).get('class'): templates.setdefault(ref['type']['class'], ref)
native_text = functions['BindIntAddOrSubstractToSIText'].read_typetree()
native_sum = functions['BindMultipleIntArgsAsSumToDestination'].read_typetree()
module = ast.parse((R / 'add-card-six-ratings.py').read_text(encoding='utf-8'))
needed = ['guid', 'gid', 'link', 'socket_source', 'constant', 'make_function', 'check_graph', 'graph_runner', 'validate_ui']
definitions = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in needed]
namespace = dict(globals())
namespace['poolmap'] = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
exec(compile(ast.Module(body=definitions, type_ignores=[]), '<existing visual-function builder>', 'exec'), namespace)
doc = wo[FULL].read_typetree(); original_doc = copy.deepcopy(doc)
refs = {r['rid']: r for r in doc['references']['RefIds']}
sid = doc['inlineSheet']['m_PathID']; sheet = wo[sid].read_typetree(); original_sheet = copy.deepcopy(sheet)
def node_name(r):
    return refs.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name', '')
BC = 'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
def short_string(s):
    b = s.encode(); assert len(b) < 128
    return bytes([len(b)]) + b
def encode_paths(paths):
    b = bytearray([len(paths)])
    for path in paths:
        part = short_string(BC) + b'\x01' + short_string(path)
        b.extend(struct.pack('<i', len(part))); b.extend(part)
    return list(b)

changed = {}; tests = 0; details = []; rng = random.Random(20261017)
for title, code, pid, attrs in SPECS:
    assert sum(weight for attribute, weight in attrs) == 100
    tree = go[pid].read_typetree() if code == 'Shooting' else namespace['make_function'](code, attrs)
    if code != 'Shooting':
        tree['m_description'] = 'x5, final half-up rounding. ' + '; '.join(f'{a}={w}%' for a, w in attrs) + '. No weight normalization.'
    namespace['check_graph'](tree)
    run = namespace['graph_runner'](tree)
    for numerator in range(401):
        expected = str(int((Decimal(numerator) / 4).quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
        assert run([10] * len(attrs), numerator) == expected; tests += 1
    samples = [[n] * len(attrs) for n in range(1, 21)] + [[rng.randint(1, 20) for _ in attrs] for _ in range(400)]
    for axis in range(len(attrs)):
        for n in range(1, 21):
            v = [10] * len(attrs); v[axis] = n; samples.append(v)
    for values in samples:
        raw = sum(Decimal(weight) / 100 * value for (a, weight), value in zip(attrs, values)) * 5
        expected = str(int(raw.quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
        assert run(values) == expected, (code, values); tests += 1
    for axis in range(len(attrs)):
        for missing in [None, -1, 0, 21]:
            v = [10] * len(attrs); v[axis] = missing
            assert run(v) == '--'; tests += 1
    assert run([20] * len(attrs)) == '100'
    assert run([10] * len(attrs)) == '50'
    paths = ['person.attribute' + attribute.lower() + '.AttributeMinValue' for attribute, weight in attrs]
    sd = next(r for r in refs.values() if r.get('data', {}).get('name') == 'OverviewCard' + code + 'Value')
    vf = sd['data']['TextBinding']['m_visualFunction']
    vf['m_inputs']['m_variable']['m_argumentBytes'] = encode_paths(paths)
    assert vf['m_target']['m_guid']
    if code != 'Shooting':
        changed[pid] = tree; go[pid].save_typetree(tree)
    details.append({'title': title, 'code': code, 'weights': attrs, 'sum_percent': sum(w for a, w in attrs),
                    'paths': paths, 'path_id': pid, 'function_guid_preserved': vf['m_target']['m_guid']})

text_nodes = [r for r in refs.values() if node_name(r).startswith('OverviewCard') and (node_name(r).endswith('Title') or node_name(r).endswith('Value'))]
assert len(text_nodes) == 12
rules = {r['data']['m_RuleIndex'] for r in text_nodes}
assert len(rules) == 2
for rule_index in rules:
    users = {r['rid'] for r in refs.values() if r.get('data', {}).get('m_RuleIndex') == rule_index}
    assert users <= {r['rid'] for r in text_nodes}
    color_prop = next(p for p in sheet['m_Rules'][rule_index]['m_Properties'] if p['m_Id'] == 65536)
    sheet['colors'].append(copy.deepcopy(TEXT_COLOR))
    color_prop['m_Values'] = [{'m_ValueType': 4, 'valueIndex': len(sheet['colors']) - 1}]
changed_refs = [a['rid'] for a, b in zip(doc['references']['RefIds'], original_doc['references']['RefIds']) if a != b]
assert not changed_refs, 'Only coefficient and color changes are required in the UI.'
assert {i for i, (a, b) in enumerate(zip(sheet['m_Rules'], original_sheet['m_Rules'])) if a != b} == rules
namespace['validate_ui'](doc, sheet)
wo[sid].save_typetree(sheet)

background_before = (GAME / 'ui-backgrounds_assets_common.bundle').read_bytes()
be = UnityPy.load(background_before); bo = {o.path_id: o for o in be.objects}
texture_changes = {}; texture_details = []
for texture_id, texture_name in [(-910000000000003, 'CA000'), (-910000000000004, 'CA120'),
                                 (-910000000000005, 'CA140'), (-910000000000006, 'CA160'), (-910000000000007, 'CA180')]:
    replacement = bo[texture_id].read_typetree(); original = wo[texture_id].read_typetree()
    assert replacement['m_Name'] == original['m_Name'] == texture_name
    assert not replacement['m_StreamData']['size'] and set(replacement) == set(original)
    assert bo[texture_id].read().image.size == (replacement['m_Width'], replacement['m_Height'])
    image_node = next(r for r in refs.values() if node_name(r) == 'ReportCACardImage' + texture_name)
    image_prop = next(p for p in sheet['m_Rules'][image_node['data']['m_RuleIndex']]['m_Properties'] if p['m_Id'] == 458753)
    assert [sheet['assets'][v['valueIndex']] for v in image_prop['m_Values']] == [{'m_FileID': 0, 'm_PathID': texture_id}]
    different = sha(bo[texture_id].get_raw_data()) != sha(wo[texture_id].get_raw_data())
    if different:
        texture_changes[texture_id] = replacement; wo[texture_id].save_typetree(replacement)
    texture_details.append({'name': texture_name, 'path_id': texture_id, 'updated': different,
                            'size': [replacement['m_Width'], replacement['m_Height']],
                            'source_sha256': sha(bo[texture_id].get_raw_data())})
result = {GN: ge.file.save(packer='lz4'), WN: we.file.save(packer='lz4')}
for name, data in result.items(): (OUT / name).write_bytes(data)
for name, changes in [(GN, changed), (WN, {sid: sheet, **texture_changes})]:
    saved = {o.path_id: o for o in UnityPy.load(result[name]).objects}
    assert set(saved) == set(hashes[name])
    for pid, h in hashes[name].items():
        if pid in changes: assert saved[pid].read_typetree() == changes[pid]
        else: assert sha(saved[pid].get_raw_data()) == h, ('Unrelated asset changed', name, pid)
    if name == GN:
        for title, code, pid, attrs in SPECS:
            reread = saved[pid].read_typetree(); namespace['check_graph'](reread)
            assert namespace['graph_runner'](reread)([20] * len(attrs)) == '100'
    else:
        for texture_id in [-910000000000003, -910000000000004, -910000000000005, -910000000000006, -910000000000007]:
            assert saved[texture_id].read().image.tobytes() == bo[texture_id].read().image.tobytes()
        assert saved[FULL].read_typetree() == original_doc
assert (GAME / 'ui-backgrounds_assets_common.bundle').read_bytes() == background_before
for path, data in before.items(): assert path.read_bytes() == data
for path, expected in protected.items(): assert sha(path.read_bytes()) == expected
try:
    for folder in [GAME, SKIN]:
        for name, data in result.items():
            (folder / name).write_bytes(data); assert (folder / name).read_bytes() == data
except Exception:
    for path, data in before.items(): path.write_bytes(data)
    raise
report = {'installed': True, 'runtime_verified': False, 'color': TEXT_HEX, 'changed_text_count': 12,
          'updated_ratings': details, 'tests_passed': tests, 'rounding': 'final half-up',
          'passing_weights_total': 100, 'dribbling_reaction': 'Reflexes', 'card_images': texture_details,
          'speed_and_shooting_functions_preserved': True, 'card_portrait_and_statistics_layout_preserved': True,
          'catalog_unchanged': True, 'unrelated_objects_verified': {GN: len(hashes[GN]) - len(changed), WN: len(hashes[WN]) - 1 - len(texture_changes)},
          'before_sha256': {str(p): sha(data) for p, data in before.items()},
          'after_sha256': {name: sha(data) for name, data in result.items()}}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), 'installed': True, 'tests_passed': tests, 'color': TEXT_HEX,
                  'passing_weights_total': 100, 'updated_card_images': [i['name'] for i in texture_details if i['updated']],
                  'after_sha256': report['after_sha256']}, ensure_ascii=False, indent=2))
