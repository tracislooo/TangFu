import ast
import copy
import datetime
import hashlib
import json
import struct
import sys
from pathlib import Path

R = Path(__file__).parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
WN = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
FULL = -930000000001001
sha = lambda data: hashlib.sha256(data).hexdigest()
before = {folder / WN: (folder / WN).read_bytes() for folder in [GAME, SKIN]}
assert before[GAME / WN] == before[SKIN / WN], 'Game/skin bundle differs'
protected_paths = [GAME / n for n in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',
    'ui-visualfunctions_assets_all.bundle', 'ui-backgrounds_assets_common.bundle', 'ui-tileslayouts_assets_all.bundle']]
protected_paths += [GAME.parent / 'catalog.bin', SKIN / 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']
protected = {p: sha(p.read_bytes()) for p in protected_paths}
env = UnityPy.load(before[GAME / WN]); objects = {o.path_id: o for o in env.objects}
old_hashes = {i: sha(o.get_raw_data()) for i, o in objects.items()}
doc = objects[FULL].read_typetree(); old_doc = copy.deepcopy(doc)
sid = doc['inlineSheet']['m_PathID']; sheet = objects[sid].read_typetree(); old_sheet = copy.deepcopy(sheet)
rr = {r['rid']: r for r in doc['references']['RefIds']}
old_refs = copy.deepcopy(rr)

# Reuse only the existing pure serialization/style helpers, without running their build/install code.
oldwrite = TypeTreeHelper.write_value
helper_source = ast.parse((R / 'redesign-card-top-info-foot.py').read_text(encoding='utf-8'))
helper_names = {'write', 'val', 'px', 'en', 'num', 'color', 'prop', 'rule', 'override'}
exec(compile(ast.Module(body=[n for n in helper_source.body if isinstance(n, ast.FunctionDef) and n.name in helper_names], type_ignores=[]), '<existing helpers>', 'exec'))
TypeTreeHelper.write_value = write
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
validator_source = ast.parse((R / 'add-card-six-ratings.py').read_text(encoding='utf-8'))
exec(compile(ast.Module(body=[n for n in validator_source.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_ui'], type_ignores=[]), '<existing validator>', 'exec'))

def named(name):
    matches = [r for r in rr.values() if rr.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name') == name]
    assert len(matches) == 1, (name, len(matches))
    return matches[0]

def property_value(node, pid):
    p = next(p for p in sheet['m_Rules'][node['data']['m_RuleIndex']]['m_Properties'] if p['m_Id'] == pid)
    h = p['m_Values'][0]
    if h['m_ValueType'] == 1: return ('keyword', h['valueIndex'])
    return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]

def dimension(node, pid): return property_value(node, pid)['value']
def auto(): return {'m_ValueType': 1, 'valueIndex': 2}

portrait = rr[1285]
assert dimension(portrait, 131089) == 193
assert dimension(portrait, 131105) == dimension(portrait, 131087) == 128
override(portrait['data'], [prop(131089, px(190))])

removed = set()
changed_allowed = {portrait['rid']}
value_ids = []
for label in ['CurrentAbility', 'PotentialAbility', 'BestPosition', 'Height', 'LeagueRating']:
    title = named('Card' + label + 'Title')
    value = named('Card' + label + 'Value')
    group = rr[title['data']['m_Parent']['rid']]
    assert not title['data']['m_Children']
    removed.update([title['rid'], title['data']['m_SerializedData']['rid']])
    group['data']['m_Children'] = [c for c in group['data']['m_Children'] if c['rid'] != title['rid']]
    override(group['data'], [prop(131087, px(29)), prop(131090, px(0)),
        prop(131073, en('center')), prop(131088, en('center'))])
    value_props = [prop(131087, px(29)), prop(65546, en('middle-center'))]
    if label == 'CurrentAbility':
        assert dimension(value, 65537) == 11
        value_props += [prop(65537, px(13)), prop(65536, color(255, 216, 74))]
    override(value['data'], value_props)
    changed_allowed.update([group['rid'], value['rid']]); value_ids.append(value['rid'])
doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in removed]
for i in removed: del rr[i]

ratings = named('OverviewCardGoalkeeperSwitch')
assert dimension(ratings, 131104) == 182
override(ratings['data'], [prop(131104, px(179))])
changed_allowed.add(ratings['rid'])

footer = named('CardNativeFootFooter')
assert dimension(footer, 131104) == 235
override(footer['data'], [prop(131104, px(229)), prop(131087, px(14)),
    prop(131083, en('row')), prop(131073, en('center')), prop(131088, en('center'))])
badge = named('CardPreferredFootBadge')
override(badge['data'], [prop(131102, en('relative')), prop(131089, auto()), prop(131104, auto()),
    prop(131105, auto()), prop(131087, auto()), prop(131097, px(0)),
    prop(131074, en('center')), prop(131099, px(3)), prop(131100, px(3)),
    prop(131101, px(1)), prop(131098, px(1))])
foot_text = named('CardPreferredFootText')
override(foot_text['data'], [prop(131105, auto()), prop(131087, px(12)), prop(131074, en('center'))])
changed_allowed.update([footer['rid'], badge['rid'], foot_text['rid']])
for side in ['Left', 'Right']:
    stepper = named('Card' + side + 'FootNativeStepper')
    override(stepper['data'], [prop(131104, px(4))])
    changed_allowed.add(stepper['rid'])

# Check that bindings, component scopes, templates, the rating cells and all original rules are untouched.
changed = {i for i in rr if rr[i] != old_refs[i]}
assert changed == changed_allowed, (changed, changed_allowed)
assert len(removed) == 10
assert all(rr[i] == old_refs[i] for i in rr if 'UxmlSerializedData' in rr[i]['type']['class'])
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
for key in old_doc:
    if key != 'references': assert doc[key] == old_doc[key]
assert not any(named_name.endswith('Title') for named_name in [
    rr.get(r.get('data', {}).get('m_SerializedData', {}).get('rid'), {}).get('data', {}).get('name', '')
    for r in rr.values()] if named_name.startswith('Card'))
for i in value_ids:
    assert dimension(rr[i], 131087) == 29
    assert property_value(rr[i], 65546) == 'middle-center'
    if i != value_ids[0]:
        old_rule = old_sheet['m_Rules'][old_refs[i]['data']['m_RuleIndex']]
        for pid in [65537, 65536]:
            old_prop = next(p for p in old_rule['m_Properties'] if p['m_Id'] == pid)
            new_prop = next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id'] == pid)
            assert new_prop == old_prop
assert property_value(badge, 131105) == ('keyword', 2)
assert property_value(badge, 131087) == ('keyword', 2)
assert property_value(foot_text, 131105) == ('keyword', 2)
assert dimension(footer, 131104) - (dimension(ratings, 131104) + dimension(ratings, 131087)) == 6
summary = named('CardNativePlayerSummary')
assert dimension(summary, 131087) == 5 * 29
assert dimension(summary, 131104) + dimension(summary, 131087) <= dimension(ratings, 131104)
assert dimension(portrait, 131104) + dimension(portrait, 131087) <= dimension(ratings, 131104)
card = named('ReportMiddleCA000Layer')
assert dimension(card, 131105) == dimension(card, 131087) == 286
assert dimension(footer, 131104) + dimension(footer, 131087) < dimension(card, 131104) + dimension(card, 131087)
assert dimension(footer, 131089) + dimension(footer, 131105) / 2 == 225
for side in ['Left', 'Right']:
    stepper = named('Card' + side + 'FootNativeStepper')
    assert dimension(stepper, 131104) + dimension(stepper, 131087) <= 14
    assert dimension(card, 131089) < dimension(footer, 131089) + dimension(stepper, 131089)
    assert dimension(footer, 131089) + dimension(stepper, 131089) + dimension(stepper, 131105) < dimension(card, 131089) + 286
node_count = validate_ui(doc, sheet)

objects[FULL].save_typetree(doc); objects[sid].save_typetree(sheet)
output = env.file.save(packer='lz4')
saved = {o.path_id: o for o in UnityPy.load(output).objects}
assert set(saved) == set(objects)
for i, h in old_hashes.items():
    if i in [FULL, sid]: assert saved[i].read_typetree() == {FULL: doc, sid: sheet}[i]
    else: assert sha(saved[i].get_raw_data()) == h, ('Unrelated object changed', i)
validate_ui(saved[FULL].read_typetree(), saved[sid].read_typetree())
for path, data in before.items(): assert path.read_bytes() == data, ('Source changed during build', str(path))
for path, h in protected.items(): assert sha(path.read_bytes()) == h, ('Protected file changed', str(path))

stamp = datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out = R / ('卡面内部排版微调-' + stamp); out.mkdir()
for tag, folder in [('game', GAME), ('skin', SKIN)]:
    backup = out / ('backup-' + tag); backup.mkdir()
    (backup / WN).write_bytes(before[folder / WN])
(out / WN).write_bytes(output)
report = {'installed': False, 'runtime_verified': False,
    'changed_bundle': WN, 'changed_asset_ids': [FULL, sid], 'removed_title_records': sorted(removed),
    'portrait': {'left': 190, 'top': 34, 'size': [128, 128]},
    'left_column': {'left': 126, 'top': 28, 'width': 60, 'height': 145, 'row_height': 29,
                    'alignment': 'middle-center', 'current_ability_font': 13, 'current_ability_color': '#FFD84A'},
    'six_ratings_top': 179, 'footer': {'left': 138, 'top': 229, 'width': 174, 'height': 14,
        'gap_below_six_ratings': 6, 'badge_width': 'auto', 'badge_padding': [1, 3, 1, 3], 'text_height': 12},
    'native_bindings_and_components_preserved': True, 'original_styles_preserved': True,
    'second_version_and_all_textures_preserved': True,
    'unchanged_world_objects_verified': len(old_hashes) - 2, 'validated_nodes': node_count,
    'before_sha256': {str(p): sha(data) for p, data in before.items()}, 'after_sha256': {WN: sha(output)},
    'protected_sha256': {str(p): h for p, h in protected.items()}}
manifest = out / 'manifest.json'
manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
if '--install' in sys.argv:
    try:
        for folder in [GAME, SKIN]:
            (folder / WN).write_bytes(output)
            assert (folder / WN).read_bytes() == output
        for p, h in protected.items(): assert sha(p.read_bytes()) == h
    except Exception:
        for p, data in before.items(): p.write_bytes(data)
        raise
    report['installed'] = True
    manifest.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
print(json.dumps({'output': str(out), 'installed': report['installed'],
    'unchanged_world_objects_verified': report['unchanged_world_objects_verified'],
    'after_sha256': report['after_sha256']}, ensure_ascii=False, indent=2))
