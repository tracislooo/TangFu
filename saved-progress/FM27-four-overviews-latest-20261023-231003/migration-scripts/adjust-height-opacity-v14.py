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

BASE = ROOT / '蓝光200标志间距80-v13'
OUT = ROOT / '头部加高50蓝光透明度40-v14'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
HEADER, HEADER_STYLE = 5775949770471550939, -1940069326759809061
BANNER, BANNER_STYLE = -4194025542157271532, 8045407476604796436
UNDERLAY, UNDERLAY_STYLE = -910000000000201, -910000000000202

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

def refs(doc):
    return {r['rid']: r for r in doc['references']['RefIds']}

def nodes_named(doc, name):
    records = refs(doc)
    result = []
    for r in records.values():
        data = r.get('data', {})
        serialized = records.get(data.get('m_SerializedData', {}).get('rid'), {})
        if serialized.get('data', {}).get('name') == name:
            result.append(r)
    return result

def pool(sheet, key, value, typ):
    if value not in sheet[key]:
        sheet[key].append(value)
    return {'m_ValueType': typ, 'valueIndex': sheet[key].index(value)}

def px(sheet, value):
    return pool(sheet, 'dimensions', {'unit': 1, 'value': float(value)}, 3)

def number(sheet, value):
    return pool(sheet, 'floats', struct.unpack('<f', struct.pack('<f', value))[0], 2)

def property_(pid, value):
    return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [value]}

def properties(sheet, node):
    index = node['data']['m_RuleIndex']
    return [] if index < 0 else sheet['m_Rules'][index]['m_Properties']

def get_value(sheet, node, pid):
    matches = [p for p in properties(sheet, node) if p['m_Id'] == pid]
    if not matches:
        return None
    assert len(matches) == 1
    result = []
    for v in matches[0]['m_Values']:
        result.append(sheet[{2: 'floats', 3: 'dimensions', 6: 'assets', 7: 'strings'}[v['m_ValueType']]][v['valueIndex']])
    return result

changes = []
def override(doc, sheet, node, pid, value, label):
    old_value = get_value(sheet, node, pid)
    old_index = node['data']['m_RuleIndex']
    new_properties = [copy.deepcopy(p) for p in properties(sheet, node) if p['m_Id'] != pid]
    new_properties.append(property_(pid, value))
    new_index = len(sheet['m_Rules'])
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': new_properties, 'line': -1})
    node['data']['m_RuleIndex'] = new_index
    changes.append({'label': label, 'rid': node['rid'], 'property_id': pid,
                    'old_inline_value': old_value, 'new_inline_value': get_value(sheet, node, pid),
                    'old_rule_index': old_index, 'new_rule_index': new_index})

def assert_doc_changes(old, new, changed_nodes):
    before, after = refs(old), refs(new)
    assert before.keys() == after.keys()
    for rid, r in before.items():
        candidate = copy.deepcopy(after[rid])
        if rid in changed_nodes:
            candidate['data']['m_RuleIndex'] = r['data']['m_RuleIndex']
        assert candidate == r, ('unexpected doc mutation', rid)
    candidate = copy.deepcopy(new)
    candidate['references']['RefIds'] = old['references']['RefIds']
    assert candidate == old

OUT.mkdir(exist_ok=True)
validation = []
for bundle in [GLOBAL, WORLD]:
    source = BASE / bundle
    original_bundle_hash = sha(source.read_bytes())
    env, objects = load(source)
    raw_hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
    pairs = [(BANNER, BANNER_STYLE)] if bundle == GLOBAL else [(HEADER, HEADER_STYLE), (UNDERLAY, UNDERLAY_STYLE)]
    altered = {}
    for doc_id, style_id in pairs:
        doc, sheet = objects[doc_id].read_typetree(), objects[style_id].read_typetree()
        old_doc, old_sheet = copy.deepcopy(doc), copy.deepcopy(sheet)
        changed = []
        if doc_id == HEADER:
            nodes = nodes_named(doc, 'report-player-full-header-max')
            assert len(nodes) == 2, len(nodes)
            for node in nodes:
                assert get_value(sheet, node, 131087) is None
                override(doc, sheet, node, 131087, px(sheet, 198), 'PlayerReportHeader height: shared 148px -> inline 198px')
                changed.append(node['rid'])
        else:
            node, = nodes_named(doc, 'report-player-banner-max')
            assert get_value(sheet, node, 131096) == [{'unit': 1, 'value': 260.0}]
            override(doc, sheet, node, 131096, px(sheet, 310), 'report-max min-height: 260px -> 310px')
            changed.append(node['rid'])
            if doc_id == UNDERLAY:
                blue, = nodes_named(doc, 'ReportBlueLightBelowPlayerTopBackground')
                assert get_value(sheet, blue, 458767) is None
                assert get_value(sheet, blue, 327681) == [2.0, 2.0]
                override(doc, sheet, blue, 458767, number(sheet, 0.4), 'BlueLight only opacity: default 1.0 -> 0.4')
                changed.append(blue['rid'])
        assert_doc_changes(old_doc, doc, changed)
        assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
        for key in old_sheet:
            if key not in ['m_Rules', 'dimensions', 'floats']:
                assert sheet[key] == old_sheet[key], key
        objects[doc_id].save_typetree(doc)
        objects[style_id].save_typetree(sheet)
        altered[doc_id], altered[style_id] = doc, sheet
    dest = OUT / bundle
    dest.write_bytes(env.file.save(packer='lz4'))
    check_env, check = load(dest)
    assert check.keys() == objects.keys()
    for pid, digest in raw_hashes.items():
        if pid not in altered:
            assert sha(check[pid].get_raw_data()) == digest, ('unrelated object changed', pid)
    for pid, tree in altered.items():
        assert check[pid].read_typetree() == tree, ('saved tree mismatch', pid)
    assert sha(source.read_bytes()) == original_bundle_hash
    validation.append({'bundle': bundle, 'baseline': str(source), 'baseline_sha256': original_bundle_hash,
                       'output_sha256': sha(dest.read_bytes()), 'modified_assets': list(altered),
                       'untouched_objects_verified': len(objects) - len(altered)})

# Check the output keeps all existing layering, sizes, spacing and picture settings.
world_env, world = load(OUT / WORLD)
header = world[HEADER].read_typetree()
header_refs = refs(header)
underlay_root, = nodes_named(header, 'ReportIconsUnderBackgroundLayer')
background, = nodes_named(header, 'PlayerTopBackgroundTextureLayer')
assert header_refs[1004]['data']['m_Children'] == [{'rid': underlay_root['rid']}, {'rid': background['rid']}, {'rid': 1006}]
underlay = world[UNDERLAY].read_typetree()
underlay_refs = refs(underlay)
sheet = world[UNDERLAY_STYLE].read_typetree()
stage, = nodes_named(underlay, 'ReportPortraitLayerStage')
icons, = nodes_named(underlay, 'ReportFlagClubBackgroundLayer')
blue, = nodes_named(underlay, 'ReportBlueLightBelowPlayerTopBackground')
assert stage['data']['m_Children'] == [{'rid': icons['rid']}, {'rid': blue['rid']}]
assert get_value(sheet, blue, 458767) == [struct.unpack('<f', struct.pack('<f', .4))[0]]
assert get_value(sheet, blue, 327681) == [2., 2.]
assert get_value(sheet, stage, 131087) == [{'unit': 1, 'value': 200.}]
assert get_value(sheet, icons, 131105) == [{'unit': 1, 'value': 380.}]
club = underlay_refs[icons['data']['m_Children'][1]['rid']]
assert get_value(sheet, club, 131091) == [{'unit': 1, 'value': 80.}]

readme = '''头部加高50px、BlueLight 40%不透明度 v14

使用方法：备份后，替换本包中的 global、gameworld 两个同名 bundle，重启游戏。
继续使用原有 ui-backgrounds_assets_common.bundle；本次未修改纹理文件。
本包基于上一版 v13（蓝光200%、国旗队徽间距80px、头像完整显示）。

高度值（桌面版）：
1. PlayerReportHeader 的 report-player-full-header-max：
   修改前无内联 height，使用官方共享样式 height:148px。
   本次内联 height:198px（+50px），同时同步底层装饰副本。
2. report-player-banner-max（report-max）：
   官方共享样式 height:92px；当前修改版已有 min-height:260px。
   本次只把 min-height 改为310px（+50px），底层装饰模板同步。
   92px 是官方默认 height，不是当前修改版的最小高度。

BlueLight 节点单独增加 opacity:0.4：图片显示强度为40%，即额外60%透明。
该设置会与图片本身的透明通道相乘，不改变PNG/DXT5数据。
缩放仍为200%，国旗与队徽间距仍为80px；CA000 115%、头像内部75%保持不变。
其他节点、位置、绑定和资源字节已核对保持不变。

恢复方法：
最方便的方法是使用同目录交付的“还原高度透明度到v13.zip”，替换其中两个同名bundle。
如果手动恢复：
- gameworld / PlayerReportHeader / inlineStyle -1940069326759809061：
  将原头部及其装饰副本的新增 height:198px 属性删除，恢复共享148px。
- global / report-player-banner-max / inlineStyle 8045407476604796436：
  将根节点 min-height:310px 改回260px。
- gameworld / ReportIconsBelowPlayerTopBackground / inlineStyle -910000000000202：
  将根节点 min-height:310px 改回260px；删除BlueLight节点新增 opacity:0.4，恢复默认1.0。
修改记录.json 包含具体 rid、属性编号和样式规则索引。

已验证成品可重新读取、目标参数正确、层级和无关资源未改变；游戏内效果尚需确认。
源 packages、官方游戏文件及 v13 成品没有覆盖。
'''
(OUT / '安装与恢复说明.txt').write_text(readme, encoding='utf-8-sig')
(OUT / '修改记录.json').write_text(json.dumps({'changes': changes, 'validation': validation,
    'official_desktop_styles': {'PlayerReportHeader_height_px': 148, 'report_max_height_px': 92},
    'before_modified_report_max_min_height_px': 260}, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None

rollback = ROOT / '还原高度透明度到v13.zip'
with zipfile.ZipFile(rollback, 'w', zipfile.ZIP_DEFLATED) as z:
    for bundle in [GLOBAL, WORLD]:
        z.write(BASE / bundle, bundle)
    z.writestr('恢复说明.txt', '替换本包两个同名bundle即可恢复到v13，包含本次修改前的高度及BlueLight默认不透明度。\n'.encode('utf-8-sig'))
with zipfile.ZipFile(rollback) as z:
    assert z.testzip() is None
    for bundle in [GLOBAL, WORLD]:
        assert z.read(bundle) == (BASE / bundle).read_bytes()
print(json.dumps({'output': str(archive), 'rollback': str(rollback), 'validation': validation,
                  'changes': changes}, ensure_ascii=True))
