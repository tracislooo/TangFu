import copy
import datetime
import hashlib
import json
import sys
from pathlib import Path

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
N = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT = R / ('卡面六项数值向内收紧-' + datetime.datetime.now().strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda data: hashlib.sha256(data).hexdigest()
before = {folder / N: (folder / N).read_bytes() for folder in [GAME, SKIN]}
assert before[GAME / N] == before[SKIN / N], 'Game and skin bundle versions differ.'
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    (OUT / ('backup-' + tag + '.bundle')).write_bytes(before[folder / N])
protected = {n: sha((GAME / n).read_bytes()) for n in [
    'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',
    'ui-tileslayouts_assets_all.bundle', 'ui-backgrounds_assets_common.bundle']}
env = UnityPy.load(before[GAME / N]); objects = {o.path_id: o for o in env.objects}
hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
doc = objects[-930000000001001].read_typetree()
refs = {r['rid']: r for r in doc['references']['RefIds']}
style_id = doc['inlineSheet']['m_PathID']
sheet = objects[style_id].read_typetree(); old_sheet = copy.deepcopy(sheet)
def name(r):
    return refs.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name', '')
grid = next(r for r in refs.values() if name(r) == 'OverviewCardSixRatings')
cells = [r for r in refs.values() if name(r).startswith('OverviewCard') and name(r).endswith('Cell')]
assert len(cells) == 6
grid_rule = grid['data']['m_RuleIndex']; cell_rules = {r['data']['m_RuleIndex'] for r in cells}
assert len(cell_rules) == 1
cell_rule = next(iter(cell_rules))
assert {r['rid'] for r in refs.values() if r.get('data', {}).get('m_RuleIndex') == grid_rule} == {grid['rid']}
assert {r['rid'] for r in refs.values() if r.get('data', {}).get('m_RuleIndex') == cell_rule} == {r['rid'] for r in cells}
def dimension(rule, pid):
    p = next(p for p in sheet['m_Rules'][rule]['m_Properties'] if p['m_Id'] == pid)
    assert len(p['m_Values']) == 1 and p['m_Values'][0]['m_ValueType'] == 3
    return sheet['dimensions'][p['m_Values'][0]['valueIndex']]
old_left = dimension(grid_rule, 131089)['value']
old_width = dimension(grid_rule, 131105)['value']
old_cell_width = dimension(cell_rule, 131105)['value']
assert (old_width, old_cell_width) == (204.0, 68.0)
new_width = 180
new_left = old_left + (old_width - new_width) / 2
def set_dimension(rule, pid, value):
    p = next(p for p in sheet['m_Rules'][rule]['m_Properties'] if p['m_Id'] == pid)
    sheet['dimensions'].append({'unit': 1, 'value': float(value)})
    p['m_Values'] = [{'m_ValueType': 3, 'valueIndex': len(sheet['dimensions']) - 1}]
set_dimension(grid_rule, 131089, new_left)
set_dimension(grid_rule, 131105, new_width)
set_dimension(cell_rule, 131105, new_width / 3)
assert new_left + new_width / 2 == old_left + old_width / 2
assert new_width / 3 >= 28 + 28  # Preserve the existing title/value widths.
assert dimension(grid_rule, 131104) == {'unit': 1, 'value': 182.0}
assert dimension(grid_rule, 131087) == {'unit': 1, 'value': 44.0}
assert dimension(cell_rule, 131087) == {'unit': 1, 'value': 22.0}
changed_rules = [i for i, (a, b) in enumerate(zip(sheet['m_Rules'], old_sheet['m_Rules'])) if a != b]
assert set(changed_rules) == {grid_rule, cell_rule}
for key in sheet:
    if key not in ['m_Rules', 'dimensions']: assert sheet[key] == old_sheet[key]
objects[style_id].save_typetree(sheet)
data = env.file.save(packer='lz4'); (OUT / N).write_bytes(data)
saved = {o.path_id: o for o in UnityPy.load(data).objects}
assert set(saved) == set(objects)
for i, h in hashes.items():
    if i == style_id: assert saved[i].read_typetree() == sheet
    else: assert sha(saved[i].get_raw_data()) == h, ('Unrelated object changed', i)
for path, original in before.items(): assert path.read_bytes() == original
try:
    for path in before:
        path.write_bytes(data); assert path.read_bytes() == data
except Exception:
    for path, original in before.items(): path.write_bytes(original)
    raise
for n, h in protected.items(): assert sha((GAME / n).read_bytes()) == h
report = {
    'installed': True, 'runtime_verified': False, 'changed_style_asset': style_id,
    'old_rating_width': old_width, 'new_rating_width': new_width,
    'old_cell_width': old_cell_width, 'new_cell_width': new_width / 3,
    'new_left': new_left, 'center_preserved': True,
    'font_size_formula_portrait_and_card_textures_preserved': True,
    'unrelated_objects_verified': len(hashes) - 1,
    'before_sha256': {str(p): sha(b) for p, b in before.items()},
    'after_sha256': sha(data), 'protected_game_sha256': protected,
}
(OUT / 'manifest.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(OUT), **report}, ensure_ascii=False, indent=2))
