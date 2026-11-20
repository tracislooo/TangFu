import copy
import hashlib
import json
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

BASE = ROOT / '能力卡面切换修正-v29'
OUT = ROOT / '右侧四项联赛统计Actions右下-v30'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
BANNER = -4194025542157271532
STYLE = 8045407476604796436

original_write_value = TypeTreeHelper.write_value
def write_value(value, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(value, config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type != 'ReferencedObjectData':
                original_write_value(value[child.m_Name], child, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):
            writer.align_stream()
        return
    return original_write_value(value, node, writer, config)
TypeTreeHelper.write_value = write_value

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    env = UnityPy.load(str(path))
    return env, {o.path_id: o for o in env.objects}

env, objects = load(BASE / GLOBAL)
hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
source_hash = sha((BASE / GLOBAL).read_bytes())
doc = objects[BANNER].read_typetree()
sheet = objects[STYLE].read_typetree()
old_doc, old_sheet = copy.deepcopy(doc), copy.deepcopy(sheet)
refs = {r['rid']: r for r in doc['references']['RefIds']}
stats_rows = json.loads((ROOT / 'native-stats-research-v30.json').read_text(encoding='utf-8'))
stats_doc = next(x['tree'] for x in stats_rows if x['tree']['m_Name'] == 'PlayerReportSeasonStatsBlock')
stats_refs = {r['rid']: r for r in stats_doc['references']['RefIds']}
season_rows = json.loads((ROOT / 'season-stats-native-v30.json').read_text(encoding='utf-8'))
coach = next(x['tree'] for x in season_rows if x['tree']['m_Name'] == 'CoachReportBlock_16x7')
coach_refs = {r['rid']: r for r in coach['references']['RefIds']}

IDS = dict(direction=131083, grow=131084, shrink=131085, basis=131082,
           width=131105, height=131087, minwidth=131097, minheight=131096,
           align=131073, self=131074, justify=131088,
           ml=131091, mr=131092, mt=131093, mb=131090,
           pl=131099, pr=131100, pt=131101, pb=131098,
           margin=262150, padding=262151, fontsize=65537, color=65536,
           whitespace=65552)

def val(kind, value):
    if kind in ('px', '%'):
        key, typ, value = 'dimensions', 3, {'unit': 1 if kind == 'px' else 2, 'value': float(value)}
    elif kind == 'float':
        key, typ, value = 'floats', 2, float(value)
    elif kind == 'color':
        key, typ = 'colors', 4
    else:
        key, typ = 'strings', 7
    if value not in sheet[key]:
        sheet[key].append(value)
    return {'m_ValueType': typ, 'valueIndex': sheet[key].index(value)}

def properties(entries):
    return [{'m_Id': IDS[k], 'm_CustomName': '', 'm_Line': -1,
             'm_Values': [val(*value)]} for k, value in entries.items()]

def rule(entries):
    index = len(sheet['m_Rules'])
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': properties(entries), 'line': -1})
    return index

def change_style(rid, entries):
    index = refs[rid]['data']['m_RuleIndex']
    assert index >= 0
    assert sum(r.get('data', {}).get('m_RuleIndex') == index for r in refs.values()) == 1
    props = sheet['m_Rules'][index]['m_Properties']
    changed = {IDS[k] for k in entries}
    sheet['m_Rules'][index]['m_Properties'] = [p for p in props if p['m_Id'] not in changed] + properties(entries)
    return index

px = lambda v: ('px', v)
pct = lambda v: ('%', v)
enum = lambda v: ('enum', v)
num = lambda v: ('float', v)
white = ('color', {'r': 1.0, 'g': 1.0, 'b': 1.0, 'a': 1.0})
new_refs = []
next_rid = max(refs) + 1
next_id = 1901000000

def pair(node_template, sd_template, parent, name, index, classes=None):
    global next_rid, next_id
    node, sd = copy.deepcopy(node_template), copy.deepcopy(sd_template)
    node['rid'], sd['rid'] = next_rid, next_rid + 1
    next_rid += 2
    node['data'].update(m_Id=next_id, m_Parent={'rid': parent}, m_Children=[],
                        m_SerializedData={'rid': sd['rid']}, m_RuleIndex=index,
                        m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[],
                        m_Classes=[] if classes is None else classes, m_SkipClone=0)
    sd['data'].update(uxmlAssetId=next_id, name=name, name_UxmlAttributeFlags=1)
    next_id += 1
    new_refs.extend([node, sd])
    refs[node['rid']], refs[sd['rid']] = node, sd
    return node, sd

def ve(parent, name, index):
    return pair(refs[1140], refs[1141], parent, name, index)

def children(parent, ids):
    refs[parent]['data']['m_Children'] = [{'rid': rid} for rid in ids]
    for rid in ids:
        refs[rid]['data']['m_Parent'] = {'rid': parent}

right = 1008
original_children = [p['rid'] for p in refs[right]['data']['m_Children']]
assert original_children == [1013, 1022, 1020, 1015, 1017, 1019, 1021]
changed_rules = set()
changed_rules.add(change_style(right, {'direction': enum('column'), 'justify': enum('flex-start')}))
changed_rules.add(change_style(1013, {
    'direction': enum('row'), 'align': enum('center'), 'justify': enum('flex-end'),
    'height': px(44), 'minheight': px(44), 'mt': px(2), 'mb': px(0),
}))
for rid in (1022, 1020):
    changed_rules.add(change_style(rid, {
        'width': pct(50), 'basis': px(0), 'grow': num(1), 'shrink': num(1),
        'minwidth': px(0), 'margin': px(0), 'mb': px(0),
    }))

stats_rule = rule({'direction': enum('row'), 'width': pct(100), 'minwidth': px(0),
                   'height': px(60), 'minheight': px(60), 'shrink': num(0),
                   'align': enum('stretch'), 'margin': px(0), 'padding': px(0), 'mb': px(2)})
info_rule = rule({'direction': enum('row'), 'width': pct(100), 'minwidth': px(0),
                 'basis': px(0), 'grow': num(1), 'shrink': num(1), 'minheight': px(0),
                 'align': enum('flex-start'), 'margin': px(0), 'padding': px(0)})
cell_rule = rule({'direction': enum('column'), 'basis': px(0), 'grow': num(1),
                 'shrink': num(1), 'minwidth': px(0), 'align': enum('center'),
                 'margin': px(0), 'padding': px(0), 'pl': px(3), 'pr': px(3)})
title_rule = rule({'width': pct(100), 'minwidth': px(0), 'height': px(34),
                  'shrink': num(0), 'fontsize': px(12), 'whitespace': enum('normal'),
                  'margin': px(0), 'padding': px(0), 'color': white})
value_rule = rule({'minwidth': px(0), 'height': px(26), 'shrink': num(0),
                  'fontsize': px(22), 'whitespace': enum('nowrap'),
                  'self': enum('center'), 'margin': px(0), 'padding': px(0), 'color': white})

# Copy the native coach-report component which binds statistics for Player.Division.
stats_root, stats_sd = pair(coach_refs[1079], coach_refs[1113], right,
                           'ReportLeagueStatsRow', stats_rule)
component_node = copy.deepcopy(coach_refs[1109])
component_sd = copy.deepcopy(coach_refs[1156])
component_node['rid'], component_sd['rid'] = next_rid, next_rid + 1
next_rid += 2
component_node['data'].update(m_Id=next_id, m_Parent={'rid': stats_root['rid']},
                              m_ParentId=stats_root['data']['m_Id'])
component_sd['data']['uxmlAssetId'] = next_id
next_id += 1
for mapping in component_sd['data']['Mappings']:
    assert mapping['to']['m_path'].startswith('Player.')
    mapping['to']['m_path'] = 'person.' + mapping['to']['m_path'][len('Player.'):]
component_node['data']['m_Properties'] = [{'name': 'mappings', 'value':
    'competition:person.Division:comp,seasonStats:person.SeasonStats.SeasonStatsSelectedCompetitionsData:seasonstatsselectedcompetitions'}]
stats_sd['data']['m_components'] = [{'rid': component_sd['rid']}]
stats_sd['data']['m_components_UxmlAttributeFlags'] = 1
new_refs.extend([component_node, component_sd])
refs[component_node['rid']], refs[component_sd['rid']] = component_node, component_sd

specs = [
    ('ExpectedGoalsPer90', 1370, 1371, 'SeasonStats.ExpectedGoalsPer90'),
    ('ExpectedAssistsPer90', 1323, 1324, 'SeasonStats.ExpectedAssistsPer90'),
    ('PassCompletedPer90', 1335, 1336, 'SeasonStats.PassCompletedPer90'),
    ('TacklesCompletedPer90', 1409, 1410, 'SeasonStats.TacklesCompletedPer90'),
]
stat_cells = []
text_records = []
for name, title_rid, value_rid, path in specs:
    cell, _ = ve(stats_root['rid'], 'ReportLeague' + name + 'Cell', cell_rule)
    stat_cells.append(cell['rid'])
    cell_children = []
    for source_rid, suffix, index in [(title_rid, 'Title', title_rule), (value_rid, 'Value', value_rule)]:
        source_sd = stats_refs[source_rid]
        source_node = next(r for r in stats_refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == source_rid)
        node, sd = pair(source_node, source_sd, cell['rid'], 'ReportLeague' + name + suffix,
                        index, copy.deepcopy(source_node['data']['m_Classes']))
        if suffix == 'Value':
            sd['data']['DebugDisplay'] = '--'
        assert sd['data']['TextBinding'] == source_sd['data']['TextBinding']
        text_records.append((node['rid'], sd['rid'], source_rid))
        cell_children.append(node['rid'])
    children(cell['rid'], cell_children)
children(stats_root['rid'], [component_node['rid'], *stat_cells])
info, _ = ve(right, 'ReportScoutAbilityContractRow', info_rule)
children(info['rid'], [1022, 1020])
children(right, [stats_root['rid'], info['rid'], 1015, 1017, 1019, 1021, 1013])
doc['references']['RefIds'].extend(new_refs)

# All imported managed-reference types already exist in this global serialized file.
known_types = {(t.m_ClassName, t.m_NameSpace, t.m_AssemblyName) for t in objects[BANNER].assets_file.ref_types}
assert all((r['type']['class'], r['type']['ns'], r['type']['asm']) in known_types for r in new_refs)
for r in old_doc['references']['RefIds']:
    if r['rid'] not in (right, 1022, 1020):
        assert refs[r['rid']] == r, r['rid']
for index, r in enumerate(old_sheet['m_Rules']):
    if index not in changed_rules:
        assert sheet['m_Rules'][index] == r, index

objects[BANNER].save_typetree(doc)
objects[STYLE].save_typetree(sheet)
OUT.mkdir(exist_ok=True)
dest = OUT / GLOBAL
dest.write_bytes(env.file.save(packer='lz4'))
_, saved = load(dest)
assert saved[BANNER].read_typetree() == doc
assert saved[STYLE].read_typetree() == sheet
assert set(saved) == set(objects)
for pid, digest in hashes.items():
    if pid not in (BANNER, STYLE):
        assert sha(saved[pid].get_raw_data()) == digest, pid

# Check parent links, component ownership, original numeric formatting and translated titles.
saved_doc = saved[BANNER].read_typetree()
rs = {r['rid']: r for r in saved_doc['references']['RefIds']}
seen = set()
def visit(rid):
    assert rid not in seen, ('cycle or duplicate', rid)
    seen.add(rid)
    for child in rs[rid].get('data', {}).get('m_Children', []):
        cid = child['rid']
        assert rs[cid]['data']['m_Parent']['rid'] == rid
        visit(cid)
visit(saved_doc['m_VisualTree']['rid'])
assert all(rid in seen for rid in stat_cells)
assert rs[right]['data']['m_Children'][-1] == {'rid': 1013}
assert rs[stats_sd['rid']]['data']['m_components'] == [{'rid': component_sd['rid']}]
assert rs[component_node['rid']]['data']['m_ParentId'] == rs[stats_root['rid']]['data']['m_Id']
for node_rid, sd_rid, native_rid in text_records:
    assert rs[sd_rid]['data']['TextBinding'] == stats_refs[native_rid]['data']['TextBinding']
assert sha((BASE / GLOBAL).read_bytes()) == source_hash

notes = '''report-player-banner-max 右侧联赛统计 v30

退出游戏，把本包 global bundle 替换到之前的位置，再启动游戏。
本次只需替换 ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle。

右侧顶部四列从左到右：
Expected Goals/90 Mins；Expected Assists/90 Mins；Passes Completed/90 Mins；Tackles Won per Game。
每列上方是游戏原生、随游戏语言翻译的标题，下方是当前球员数值。
沿用原生两位小数格式，不使用示例数字。

取数沿用 CoachReportBlock_16x7 的联赛绑定组件：
competition = person.Division
seasonStats = person.SeasonStats.SeasonStatsSelectedCompetitionsData
四项字段分别为 ExpectedGoalsPer90、ExpectedAssistsPer90、PassCompletedPer90、TacklesCompletedPer90。
最后一项沿用游戏标题 Tackles Won per Game；其原生字段名是 TacklesCompletedPer90。

右侧中间保留考察/能力潜力与合同信息，改为并排；Actions 按钮位于最下方靠右。
栏目185px、左侧、中间头像及卡面、背景层级保持v29原值。

已重读验证组件绑定、四项标题和格式化参数、父子层级、按钮末行以及无关资源字节。
游戏内实时数值和实际排版仍需在运行游戏中确认。
原始packages、游戏安装目录及v29成品未覆盖。
'''
(OUT / '安装说明.txt').write_text(notes, encoding='utf-8-sig')
manifest = {'baseline': str(BASE), 'changed_assets': [BANNER, STYLE],
            'competition_binding': 'person.Division',
            'statistics_binding': 'person.SeasonStats.SeasonStatsSelectedCompetitionsData',
            'native_template': 'CoachReportBlock_16x7',
            'stats': [{'field': x[3], 'native_title_serialized_rid': x[1], 'native_value_serialized_rid': x[2]} for x in specs],
            'stats_row_rid': stats_root['rid'], 'actions_frame_rid': 1013,
            'untouched_assets_byte_verified': len(hashes)-2,
            'existing_modified_records': [1008, 1022, 1020], 'existing_modified_style_rules': sorted(changed_rules),
            'game_runtime_verified': False, 'source_sha256': source_hash,
            'output_sha256': sha(dest.read_bytes())}
(OUT / '修改记录.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in OUT.iterdir():
        z.write(path, path.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'new_records': len(new_refs),
                  'untouched_assets_verified': len(hashes)-2}, ensure_ascii=True))
