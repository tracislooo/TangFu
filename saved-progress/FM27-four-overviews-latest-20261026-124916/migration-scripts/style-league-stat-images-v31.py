import copy
import hashlib
import json
import math
import struct
import sys
import zipfile
from pathlib import Path

import openpyxl

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

BASE = ROOT / '右侧四项联赛统计Actions右下-v30'
OUT = ROOT / '联赛四项等级图片数值标题-v31'
BOOK = Path('C:/Users/traci/AppData/Local/Temp/90mins (1).xlsx')
BACKGROUND = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/ui-backgrounds_assets_common.bundle')
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
BANNER, STYLE = -4194025542157271532, 8045407476604796436
FUNCTION_GUID = '690be8be67e3d4a4c932f402d5a73176'

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

def string_bytes(value):
    data = value.encode('utf-8')
    assert len(data) < 128
    return bytes([len(data)]) + data

def read_string(raw, offset=0):
    size = shift = 0
    while True:
        v = raw[offset]
        offset += 1
        size |= (v & 127) << shift
        if not v & 128:
            break
        shift += 7
    return raw[offset:offset+size].decode('utf-8'), offset+size

def args(operator, bound, path):
    values = [
        ('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]', struct.pack('<i', operator)),
        ('SI.VisualScripting.DoubleVisualArg', struct.pack('<d', bound)),
        ('SI.Bindable.BindingKeyVisualArg', b'\x00'),
        ('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]', b'\x01' + string_bytes(path)),
    ]
    raw = bytearray([len(values)])
    for cls, value in values:
        payload = string_bytes(cls) + value
        raw.extend(struct.pack('<i', len(payload)))
        raw.extend(payload)
    return list(raw)

def decode_args(raw):
    offset = 1
    result = []
    for _ in range(raw[0]):
        length, = struct.unpack_from('<i', raw, offset)
        offset += 4
        payload = raw[offset:offset+length]
        offset += length
        cls, pos = read_string(payload)
        result.append((cls, payload[pos:]))
    assert offset == len(raw)
    return result

groups = {}
book_hash = sha(BOOK.read_bytes())
workbook = openpyxl.load_workbook(BOOK, data_only=True, read_only=True)
for row in workbook.active.iter_rows(min_row=2, values_only=True):
    if not row[0]:
        continue
    label, lower, upper, name, pid = row[:5]
    assert isinstance(lower, (float, int)) and isinstance(upper, (float, int)) and lower <= upper
    groups.setdefault(label, []).append({'min': float(lower), 'max': float(upper), 'name': name, 'pid': int(pid)})
workbook.close()
assert len(groups) == 4
for rows in groups.values():
    assert len(rows) == 10 and rows[0]['min'] == 0
    for index, row in enumerate(rows):
        assert row['name'] == f'level{index+1:03d}' and row['pid'] == -910000000000008-index
        if index < 9:
            assert abs(rows[index+1]['min'] - row['max'] - .0001) < 1e-9

specs = [
    ('Expected Goal/90 mins', 'ExpectedGoalsPer90', 'SeasonStats.ExpectedGoalsPer90'),
    ('ExpectedAssists/90 mins', 'ExpectedAssistsPer90', 'SeasonStats.ExpectedAssistsPer90'),
    ('Passes Completed/90 mins', 'PassCompletedPer90', 'SeasonStats.PassCompletedPer90'),
    ('tackles won per game', 'TacklesCompletedPer90', 'SeasonStats.TacklesCompletedPer90'),
]
env, objects = load(BASE / GLOBAL)
_, bg_objects = load(BACKGROUND)
source_hash, background_hash = sha((BASE / GLOBAL).read_bytes()), sha(BACKGROUND.read_bytes())
hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
doc, sheet = objects[BANNER].read_typetree(), objects[STYLE].read_typetree()
old_doc, old_sheet = copy.deepcopy(doc), copy.deepcopy(sheet)
refs = {r['rid']: r for r in doc['references']['RefIds']}
names = {r.get('data', {}).get('name'): r for r in refs.values() if r.get('data', {}).get('name')}
def node_for(sd):
    return next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == sd['rid'])

visible_node_template, visible_sd_template = json.loads((ROOT / 'double-visible-template-v31.json').read_text(encoding='utf-8'))
assert visible_sd_template['data']['Binding']['m_visualFunction']['m_target']['m_guid'] == FUNCTION_GUID
native_args = decode_args(bytes(visible_sd_template['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']))
assert native_args == decode_args(bytes(args(3, 0.0, 'goalsnumber.XgValue')))
assert visible_sd_template['data']['AlwaysInstantiate'] == 0

IDS = dict(width=131105, height=131087, minheight=131096, minwidth=131097,
           direction=131083, grow=131084, shrink=131085, basis=131082,
           align=131073, self=131074, justify=131088,
           margin=262150, padding=262151, ml=131091, mr=131092, mt=131093, mb=131090,
           pl=131099, pr=131100, pt=131101, pb=131098,
           position=131102, left=131089, top=131104,
           fontsize=65537, textalign=65546, whitespace=65552,
           background=458753, bgscale=262153)

def val(kind, value):
    if kind in ('px', '%'):
        key, typ, value = 'dimensions', 3, {'unit': 1 if kind == 'px' else 2, 'value': float(value)}
    elif kind == 'float':
        key, typ, value = 'floats', 2, float(value)
    elif kind == 'asset':
        key, typ = 'assets', 6
    else:
        key, typ = 'strings', 7
    if value not in sheet[key]:
        sheet[key].append(value)
    return {'m_ValueType': typ, 'valueIndex': sheet[key].index(value)}

def props(entries):
    return [{'m_Id': IDS[k], 'm_CustomName': '', 'm_Line': -1, 'm_Values': [val(*v)]} for k, v in entries.items()]

def new_rule(entries):
    index = len(sheet['m_Rules'])
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': props(entries), 'line': -1})
    return index

def edit_rule(index, entries):
    changed = {IDS[k] for k in entries}
    rule = sheet['m_Rules'][index]
    rule['m_Properties'] = [p for p in rule['m_Properties'] if p['m_Id'] not in changed] + props(entries)

px = lambda v: ('px', v)
pct = lambda v: ('%', v)
en = lambda v: ('enum', v)
num = lambda v: ('float', v)
stats_root = node_for(names['ReportLeagueStatsRow'])
stats_index = stats_root['data']['m_RuleIndex']
edit_rule(stats_index, {'height': px(80), 'minheight': px(80)})
first_cell = node_for(names['ReportLeagueExpectedGoalsPer90Cell'])
cell_index = first_cell['data']['m_RuleIndex']
edit_rule(cell_index, {'position': en('relative'), 'height': pct(100),
                       'pl': px(4), 'pr': px(4), 'minwidth': px(0)})
title_index = node_for(names['ReportLeagueExpectedGoalsPer90Title'])['data']['m_RuleIndex']
value_index = node_for(names['ReportLeagueExpectedGoalsPer90Value'])['data']['m_RuleIndex']
edit_rule(title_index, {'position': en('absolute'), 'left': px(0), 'top': pct(76),
                        'width': pct(100), 'height': px(20), 'fontsize': px(10),
                        'textalign': en('upper-center'), 'whitespace': en('normal')})
edit_rule(value_index, {'position': en('absolute'), 'left': px(0), 'top': pct(48),
                        'width': pct(100), 'height': px(22), 'fontsize': px(20),
                        'textalign': en('middle-center'), 'whitespace': en('nowrap')})
edited_rules = {stats_index, cell_index, title_index, value_index}

fill_entries = {'position': en('absolute'), 'left': px(0), 'top': px(0),
                'width': pct(100), 'height': pct(100), 'minwidth': px(0),
                'margin': px(0), 'padding': px(0)}
fill_index = new_rule(fill_entries)
image_indices = {}
texture_ids = [-910000000000008-i for i in range(10)]
for pid in texture_ids:
    image_indices[pid] = new_rule({**fill_entries,
        'background': ('asset', {'m_FileID': 0, 'm_PathID': pid}), 'bgscale': en('scale-to-fit')})

new_refs = []
next_rid = max(refs) + 1
next_id = 1901100000
assert all(not next_id <= r.get('data', {}).get('m_Id', -1) < next_id+500 for r in refs.values())
ve_template = refs[1140]
ve_sd_template = refs[1141]

def pair(node_template, sd_template, parent, name, rule_index):
    global next_rid, next_id
    node, sd = copy.deepcopy(node_template), copy.deepcopy(sd_template)
    node['rid'], sd['rid'] = next_rid, next_rid+1
    next_rid += 2
    node['data'].update(m_Id=next_id, m_Parent={'rid': parent}, m_Children=[],
                        m_SerializedData={'rid': sd['rid']}, m_RuleIndex=rule_index,
                        m_Classes=[], m_Properties=[], m_StylesheetPaths=[], m_Stylesheets=[], m_SkipClone=0)
    sd['data'].update(uxmlAssetId=next_id, name=name, name_UxmlAttributeFlags=1,
                      pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    next_id += 1
    refs[node['rid']], refs[sd['rid']] = node, sd
    new_refs.extend([node, sd])
    return node, sd

def children(parent, ids):
    refs[parent]['data']['m_Children'] = [{'rid': rid} for rid in ids]
    for rid in ids:
        refs[rid]['data']['m_Parent'] = {'rid': parent}

def visible(parent, name, operator, bound, path):
    node, sd = pair(visible_node_template, visible_sd_template, parent, name, fill_index)
    sd['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = args(operator, bound, path)
    return node, sd

conditions = []
changed_cells = set()
for label, key, path in specs:
    cell = node_for(names['ReportLeague' + key + 'Cell'])
    title = node_for(names['ReportLeague' + key + 'Title'])
    value = node_for(names['ReportLeague' + key + 'Value'])
    assert cell['data']['m_RuleIndex'] == cell_index
    assert title['data']['m_RuleIndex'] == title_index and value['data']['m_RuleIndex'] == value_index
    assert cell['data']['m_Children'] == [{'rid': title['rid']}, {'rid': value['rid']}]
    stack, _ = pair(ve_template, ve_sd_template, cell['rid'], 'ReportLeague' + key + 'ImageStack', fill_index)
    bands = []
    for i, row in enumerate(groups[label]):
        # Half-open bands use the next row's lower bound; the supplied .xxxx9 maxima
        # describe the preceding four-decimal interval. The last maximum is inclusive.
        upper = groups[label][i+1]['min'] if i < 9 else row['max']
        lower, lower_sd = visible(stack['rid'], f'ReportLeague{key}Level{i+1:03d}Lower', 5, row['min'], path)
        upper_node, upper_sd = visible(lower['rid'], f'ReportLeague{key}Level{i+1:03d}Upper', 0 if i < 9 else 1, upper, path)
        image, _ = pair(ve_template, ve_sd_template, upper_node['rid'], f'ReportLeague{key}{row["name"]}Image', image_indices[row['pid']])
        children(lower['rid'], [upper_node['rid']])
        children(upper_node['rid'], [image['rid']])
        bands.append(lower['rid'])
        conditions.append({'metric': label, 'path': path, 'min': row['min'], 'source_max': row['max'],
                           'upper': upper, 'upper_inclusive': i == 9, 'texture_id': row['pid'],
                           'lower_sd': lower_sd['rid'], 'upper_sd': upper_sd['rid'], 'image_rid': image['rid']})
    children(stack['rid'], bands)
    children(cell['rid'], [stack['rid'], title['rid'], value['rid']])
    changed_cells.add(cell['rid'])
doc['references']['RefIds'].extend(new_refs)

af = objects[BANNER].assets_file
known_types = {(t.m_ClassName, t.m_NameSpace, t.m_AssemblyName) for t in af.ref_types}
assert all((r['type']['class'], r['type']['ns'], r['type']['asm']) in known_types for r in new_refs)
added = []
texture_info = []
for pid in texture_ids:
    src = bg_objects[pid]
    tree = src.read_typetree()
    assert tree['m_StreamData']['size'] == 0 and tree['m_TextureFormat'] == 12
    assert pid not in af.objects
    tid = next(i for i, t in enumerate(af.types) if t.class_id == src.serialized_type.class_id and t.old_type_hash == src.serialized_type.old_type_hash)
    obj = copy.copy(src)
    obj.assets_file, obj.type_id, obj.serialized_type = af, tid, af.types[tid]
    obj.set_raw_data(src.get_raw_data())
    af.objects[pid] = obj
    added.append(pid)
    texture_info.append({'pid': pid, 'name': tree['m_Name'], 'width': tree['m_Width'], 'height': tree['m_Height'], 'format': tree['m_TextureFormat']})

bundle_obj = next(o for o in env.objects if o.type.name == 'AssetBundle')
metadata = bundle_obj.read_typetree()
old_meta = copy.deepcopy(metadata)
for key, info in metadata['m_Container']:
    preload = copy.deepcopy(old_meta['m_PreloadTable'][info['preloadIndex']:info['preloadIndex']+info['preloadSize']])
    if any(p['m_FileID'] == 0 and p['m_PathID'] in (BANNER, STYLE) for p in preload):
        for pid in texture_ids:
            ptr = {'m_FileID': 0, 'm_PathID': pid}
            if ptr not in preload:
                preload.append(ptr)
        info['preloadIndex'] = len(metadata['m_PreloadTable'])
        info['preloadSize'] = len(preload)
        metadata['m_PreloadTable'].extend(preload)
for info in texture_info:
    start = len(metadata['m_PreloadTable'])
    ptr = {'m_FileID': 0, 'm_PathID': info['pid']}
    metadata['m_PreloadTable'].append(ptr)
    metadata['m_Container'].append((info['name'].lower(), {'preloadIndex': start, 'preloadSize': 1, 'asset': ptr}))
metadata['m_Container'].sort(key=lambda row: row[0])

for r in old_doc['references']['RefIds']:
    if r['rid'] not in changed_cells:
        assert refs[r['rid']] == r, r['rid']
for i, r in enumerate(old_sheet['m_Rules']):
    if i not in edited_rules:
        assert sheet['m_Rules'][i] == r, i

objects[BANNER].save_typetree(doc)
objects[STYLE].save_typetree(sheet)
bundle_obj.save_typetree(metadata)
OUT.mkdir(exist_ok=True)
dest = OUT / GLOBAL
dest.write_bytes(env.file.save(packer='lz4'))
_, check = load(dest)
assert set(check) == set(objects) | set(added)
for pid, expected in [(BANNER, doc), (STYLE, sheet), (bundle_obj.path_id, metadata)]:
    assert check[pid].read_typetree() == expected
modified = {BANNER, STYLE, bundle_obj.path_id}
for pid, digest in hashes.items():
    if pid not in modified:
        assert sha(check[pid].get_raw_data()) == digest, pid
for pid in texture_ids:
    assert check[pid].get_raw_data() == bg_objects[pid].get_raw_data()
    assert check[pid].read().image.tobytes() == bg_objects[pid].read().image.tobytes()

rs = {r['rid']: r for r in check[BANNER].read_typetree()['references']['RefIds']}
seen = set()
def visit(rid):
    assert rid not in seen
    seen.add(rid)
    for child in rs[rid].get('data', {}).get('m_Children', []):
        cid = child['rid']
        assert rs[cid]['data']['m_Parent']['rid'] == rid
        visit(cid)
visit(doc['m_VisualTree']['rid'])

def bound(sd_rid):
    binding = rs[sd_rid]['data']['Binding']
    assert binding['m_visualFunction']['m_target']['m_guid'] == FUNCTION_GUID
    values = decode_args(bytes(binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']))
    assert values[1][0] == 'SI.VisualScripting.DoubleVisualArg'
    path, end = read_string(values[3][1], 1)
    assert end == len(values[3][1])
    return struct.unpack('<i', values[0][1])[0], struct.unpack('<d', values[1][1])[0], path

for c in conditions:
    assert bound(c['lower_sd']) == (5, c['min'], c['path'])
    assert bound(c['upper_sd']) == (1 if c['upper_inclusive'] else 0, c['upper'], c['path'])
    assert c['image_rid'] in seen

def selected(metric, value):
    hits = []
    for c in conditions:
        if c['metric'] != metric:
            continue
        _, lower, _ = bound(c['lower_sd'])
        op, upper, _ = bound(c['upper_sd'])
        if value >= lower and (value <= upper if op == 1 else value < upper):
            hits.append(c['texture_id'])
    return hits

cases = 0
for label, rows in groups.items():
    for i, row in enumerate(rows):
        for value in [row['min'], row['max'], (row['min']+row['max'])/2]:
            assert selected(label, value) == [row['pid']], (label, value)
            cases += 1
        if i:
            value = math.nextafter(row['min'], -math.inf)
            assert selected(label, value) == [rows[i-1]['pid']], (label, value)
            cases += 1
assert sha(BOOK.read_bytes()) == book_hash
assert sha(BACKGROUND.read_bytes()) == background_hash
assert sha((BASE / GLOBAL).read_bytes()) == source_hash

notes = '''联赛四项等级图片、居中数值与下方标题 v31

退出游戏，用本包 global bundle 替换原来的同名文件，重新启动游戏。
gameworld 与 backgrounds 不需替换；十张等级纹理已按原ID内嵌 global。

四项顺序与位置保留：预期进球/90、预期助攻/90、完成传球/90、每场成功抢断。
每项按新上传的 90mins (1).xlsx 对应区间显示 level001 至 level010。
数值和标题沿用已经成功显示的联赛绑定及本地化，数值放在图片中部，标题放在下方。
四列等宽填满右侧统计行，图片保持326:168比例缩放，不拉伸。
统计行高度80px，整个栏目仍为185px，Actions保持右下方。
头像、卡面、背景、左侧信息和其余原有资源保持原值。

使用游戏原生 BindDoubleToVisible 小数比较，不将0.05等数据截断为整数。
各档含最小值、不含下一档最小值；最后一档含1000。
例如表中0–0.0499实现为0≤x<0.05，避免连续小数在两档之间出现空图。
xG level009 从0.45开始，按新表执行。
传球完成数≥4使用level010，也是按新表执行。

已重读核对40档的条件参数、边界、纹理、图层与父子关系，以及其余资源字节。
实际游戏运行时图片切换与排版仍需在游戏内确认。
源表、源packages和旧版成品未覆盖。
'''
(OUT / '安装说明.txt').write_text(notes, encoding='utf-8-sig')
manifest = {'baseline': str(BASE), 'mapping_source': str(BOOK), 'mapping_sha256': book_hash,
            'ranges': groups, 'conditions': conditions, 'textures': texture_info,
            'native_function': 'BindDoubleToVisible', 'function_guid': FUNCTION_GUID,
            'stats_row_height_px': 80, 'header_height_px': 185,
            'changed_existing_nodes': sorted(changed_cells), 'changed_existing_rules': sorted(edited_rules),
            'new_reference_records': len(new_refs), 'unchanged_assets_verified': len(hashes)-len(modified),
            'boundary_cases_checked': cases, 'game_runtime_verified': False,
            'source_sha256': source_hash, 'output_sha256': sha(dest.read_bytes())}
(OUT / '修改记录.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'boundary_cases': cases, 'new_records': len(new_refs),
                  'unchanged_assets_verified': len(hashes)-len(modified)}, ensure_ascii=True))
