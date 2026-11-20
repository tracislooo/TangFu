import ast
import copy
import datetime
import hashlib
import json
import random
import struct
import subprocess
import sys
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
PID = -940000000000105
FULL = -930000000001001
sha = lambda b: hashlib.sha256(b).hexdigest()
OUT = R / ('身体公式改用体质-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
before = {}
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    for name in [GN, WN]:
        target = folder / name
        before[target] = target.read_bytes()
        dest = OUT / ('backup-' + tag) / name
        dest.parent.mkdir(exist_ok=True)
        dest.write_bytes(before[target])
for name in [GN, WN]:
    assert before[GAME / name] == before[SKIN / name], ('game/skin mismatch', name)
catalog_hash = sha((GAME.parent / 'catalog.bin').read_bytes())

oldwrite = TypeTreeHelper.write_value
def write(v, n, w, c):
    if n.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(v, c.assetsfile) is None:
        for ch in n.m_Children:
            if ch.m_Type != 'ReferencedObjectData':
                oldwrite(v[ch.m_Name], ch, w, c)
        if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag): w.align_stream()
        return
    return oldwrite(v, n, w, c)
TypeTreeHelper.write_value = write

ge = UnityPy.load(before[GAME / GN]); go = {o.path_id: o for o in ge.objects}
we = UnityPy.load(before[GAME / WN]); wo = {o.path_id: o for o in we.objects}
gh = {i: sha(o.get_raw_data()) for i, o in go.items()}
wh = {i: sha(o.get_raw_data()) for i, o in wo.items()}
tree = go[PID].read_typetree()
refs = tree['references']['RefIds']
minus = next(r for r in refs if r.get('data', {}).get('m_name') == '20 Minus Injury Proneness')
old_output = minus['data']['m_dataOutInt32']['m_id']
new_output = minus['data']['m_dataInB']['m_sourceID']
replacements = []
def rewrite(v):
    if isinstance(v, dict):
        for key, value in list(v.items()):
            if key == 'm_sourceID' and value == old_output:
                v[key] = copy.deepcopy(new_output); replacements.append(key)
            elif key == 'm_name' and isinstance(value, str):
                v[key] = value.replace('InjuryProneness', 'NaturalFitness')
            else: rewrite(value)
    elif isinstance(v, list):
        for value in v: rewrite(value)
refs[:] = [r for r in refs if r['rid'] != minus['rid']]
tree['m_nodes'] = [r for r in tree['m_nodes'] if r['rid'] != minus['rid']]
rewrite(tree)
assert len(replacements) == 2
tree['m_description'] = 'Physical rating: Strength 50%, Stamina 25%, Aggression 10%, JumpingReach 5%, NaturalFitness 10%; x5, final half-up rounding.'
assert 'Injury' not in json.dumps(tree)

doc = wo[FULL].read_typetree(); original_doc = copy.deepcopy(doc)
sd = next(r for r in doc['references']['RefIds'] if r.get('data', {}).get('name') == 'OverviewCardPhysicalValue')
vf = sd['data']['TextBinding']['m_visualFunction']
encoded = bytes(vf['m_inputs']['m_variable']['m_argumentBytes'])
pos = 1; arguments = []
for index in range(encoded[0]):
    size = struct.unpack_from('<i', encoded, pos)[0]; pos += 4
    argument = encoded[pos:pos + size]; pos += size
    arguments.append(argument)
assert pos == len(encoded) and len(arguments) == 5
old_path = b'person.InjuryProneness.PropertyValue'
new_path = b'person.attributenaturalfitness.AttributeMinValue'
assert arguments[4].endswith(bytes([len(old_path)]) + old_path)
arguments[4] = arguments[4][:-len(old_path) - 1] + bytes([len(new_path)]) + new_path
new_bytes = bytearray([len(arguments)])
for a in arguments:
    new_bytes.extend(struct.pack('<i', len(a))); new_bytes.extend(a)
vf['m_inputs']['m_variable']['m_argumentBytes'] = list(new_bytes)
changed_refs = [a['rid'] for a, b in zip(doc['references']['RefIds'], original_doc['references']['RefIds']) if a != b]
assert changed_refs == [sd['rid']]

# Reuse only the pure validators; importing the original build script would execute it.
module = ast.parse((R / 'add-card-six-ratings.py').read_text(encoding='utf-8'))
selected = [n for n in module.body if isinstance(n, ast.FunctionDef) and n.name in ['gid', 'check_graph', 'graph_runner']]
namespace = {}
exec(compile(ast.Module(body=selected, type_ignores=[]), '<existing graph validators>', 'exec'), namespace)
namespace['check_graph'](tree)
run = namespace['graph_runner'](tree)
tests = 0
for numerator in range(401):
    expected = str(int((Decimal(numerator) / 4).quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
    assert run([10] * 5, numerator) == expected
    tests += 1
weights = [50, 25, 10, 5, 10]
rng = random.Random(20261017)
samples = [[1] * 5, [10] * 5, [20] * 5] + [[rng.randint(1, 20) for _ in range(5)] for _ in range(500)]
for axis in range(5):
    for n in range(1, 21):
        values = [10] * 5; values[axis] = n; samples.append(values)
for values in samples:
    expected = sum(Decimal(w) / 100 * v for w, v in zip(weights, values)) * 5
    expected = str(int(expected.quantize(Decimal('1'), rounding=ROUND_HALF_UP)))
    assert run(values) == expected, values
    tests += 1
for axis in range(5):
    for missing in [None, 0, -1, 21]:
        values = [10] * 5; values[axis] = missing
        assert run(values) == '--'; tests += 1
assert run([20] * 5) == '100'
assert run([10, 10, 10, 10, 20]) == '55'

go[PID].save_typetree(tree); wo[FULL].save_typetree(doc)
result = {GN: ge.file.save(packer='lz4'), WN: we.file.save(packer='lz4')}
for name, data in result.items(): (OUT / name).write_bytes(data)
savedg = {o.path_id: o for o in UnityPy.load(result[GN]).objects}
savedw = {o.path_id: o for o in UnityPy.load(result[WN]).objects}
assert set(savedg) == set(go) and set(savedw) == set(wo)
for i, h in gh.items():
    if i == PID: assert savedg[i].read_typetree() == tree
    else: assert sha(savedg[i].get_raw_data()) == h, ('unrelated global asset', i)
for i, h in wh.items():
    if i == FULL: assert savedw[i].read_typetree() == doc
    else: assert sha(savedw[i].get_raw_data()) == h, ('unrelated world asset', i)
namespace['check_graph'](savedg[PID].read_typetree())
assert namespace['graph_runner'](savedg[PID].read_typetree())([10, 10, 10, 10, 20]) == '55'
processes = subprocess.run(['tasklist', '/FI', 'IMAGENAME eq fm.exe', '/FO', 'CSV', '/NH'], capture_output=True).stdout
assert b'"fm.exe"' not in processes.lower(), 'Exit Football Manager before replacing bundles.'
for path, data in before.items(): assert path.read_bytes() == data, ('target changed', path)
assert sha((GAME.parent / 'catalog.bin').read_bytes()) == catalog_hash
try:
    for folder in [GAME, SKIN]:
        for name, data in result.items():
            (folder / name).write_bytes(data)
            assert (folder / name).read_bytes() == data
except Exception:
    for path, data in before.items(): path.write_bytes(data)
    raise
report = {
    'installed': True, 'runtime_verified': False,
    'formula': '(Strength*0.50 + Stamina*0.25 + Aggression*0.10 + JumpingReach*0.05 + NaturalFitness*0.10)*5',
    'rounding': 'final half-up', 'new_binding': new_path.decode(), 'tests_passed': tests,
    'changed_global_asset': PID, 'changed_world_asset': FULL, 'changed_ui_serialized_reference': sd['rid'],
    'catalog_unchanged_sha256': catalog_hash,
    'before_sha256': {str(p): sha(data) for p, data in before.items()},
    'after_sha256': {n: sha(data) for n, data in result.items()},
    'unrelated_global_objects_verified': len(gh) - 1, 'unrelated_world_objects_verified': len(wh) - 1,
}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), **report}, ensure_ascii=False, indent=2))
