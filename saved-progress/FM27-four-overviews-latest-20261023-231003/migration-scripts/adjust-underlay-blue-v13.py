import copy
import hashlib
import json
import shutil
import struct
import sys
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

PACKAGES = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BASE = ROOT / '去光效标志下移头像完整显示-v12'
OUT = ROOT / '蓝光200标志间距80-v13'
DOC_ID = -910000000000201
SHEET_ID = -910000000000202
HEADER_ID = 5775949770471550939
HEADER_STYLE_ID = -1940069326759809061
BLUE_ID = -910000000000002

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

def load(path):
    env = UnityPy.load(str(path))
    return env, {o.path_id: o for o in env.objects}
def named(refs, name):
    serialized = next(r for r in refs.values() if r.get('data', {}).get('name') == name)
    return next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == serialized['rid'])['rid']
def pool(sheet, key, value, typ):
    if value not in sheet[key]:
        sheet[key].append(value)
    return {'m_ValueType': typ, 'valueIndex': sheet[key].index(value)}
def number(sheet, value):
    return pool(sheet, 'floats', struct.unpack('<f', struct.pack('<f', value))[0], 2)
def px(sheet, value):
    return pool(sheet, 'dimensions', {'unit': 1, 'value': float(value)}, 3)
def enum(sheet, value):
    return pool(sheet, 'strings', value, 7)
def prop(pid, values):
    return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1,
            'm_Values': [values] if isinstance(values, dict) else values}
def add_rule(sheet, properties):
    index = len(sheet['m_Rules'])
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': properties, 'line': -1})
    return index
def modify_rule(sheet, ref, properties):
    old = copy.deepcopy(sheet['m_Rules'][ref['data']['m_RuleIndex']]['m_Properties'])
    replace = {p['m_Id'] for p in properties}
    ref['data']['m_RuleIndex'] = add_rule(sheet, [p for p in old if p['m_Id'] not in replace] + properties)

source = PACKAGES / WORLD
env, objects = load(source)
if DOC_ID not in objects:
    source = BASE / WORLD
    env, objects = load(source)
source_hash = hashlib.sha256(source.read_bytes()).digest()
original_hashes = {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in objects.items()}
doc_obj, sheet_obj = objects[DOC_ID], objects[SHEET_ID]
doc, sheet = doc_obj.read_typetree(), sheet_obj.read_typetree()
old_doc, old_sheet = copy.deepcopy(doc), copy.deepcopy(sheet)
refs = {r['rid']: r for r in doc['references']['RefIds']}
stage = named(refs, 'ReportPortraitLayerStage')
icons = named(refs, 'ReportFlagClubBackgroundLayer')
assert refs[stage]['data']['m_Children'] == [{'rid': icons}]
flag_root, club_root = [c['rid'] for c in refs[icons]['data']['m_Children']]

# 150 + 80 + 150 = 380px, centered in the unchanged 450px stage.
modify_rule(sheet, refs[icons], [prop(131105, px(sheet, 380)), prop(131089, px(sheet, 35))])
modify_rule(sheet, refs[club_root], [prop(131091, px(sheet, 80))])

bg_env, bg_objects = load(PACKAGES / 'ui-backgrounds_assets_common.bundle')
blue_source = bg_objects[BLUE_ID]
blue_tree = blue_source.read_typetree()
assert blue_tree['m_Name'] == 'PlayerTopBlueLight'
assert blue_tree['m_TextureFormat'] == 12 and blue_tree['m_StreamData']['size'] == 0
assert blue_source.assets_file.name == 'CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8'
asset_file = doc_obj.assets_file
assert BLUE_ID not in asset_file.objects
texture_type_index = next(i for i, typ in enumerate(asset_file.types)
                          if typ.class_id == blue_source.serialized_type.class_id
                          and typ.old_type_hash == blue_source.serialized_type.old_type_hash)
new_texture = copy.copy(blue_source)
new_texture.assets_file = asset_file
new_texture.type_id = texture_type_index
new_texture.serialized_type = asset_file.types[texture_type_index]
new_texture.set_raw_data(blue_source.get_raw_data())
asset_file.objects[BLUE_ID] = new_texture

# The blue image is in the icon underlay, before the complete PlayerTopBackground layer.
node = copy.deepcopy(refs[stage])
serialized = copy.deepcopy(refs[refs[stage]['data']['m_SerializedData']['rid']])
node['rid'], serialized['rid'] = max(refs) + 1, max(refs) + 2
element_id = 1900700000
assert all(r.get('data', {}).get('m_Id') != element_id for r in refs.values())
node['data'].update(m_Id=element_id, m_Parent={'rid': stage}, m_Children=[], m_Classes=[],
                    m_SerializedData={'rid': serialized['rid']})
serialized['data'].update(uxmlAssetId=element_id, name='ReportBlueLightBelowPlayerTopBackground',
                          name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)
node['data']['m_RuleIndex'] = add_rule(sheet, [
    prop(131102, enum(sheet, 'absolute')), prop(131089, px(sheet, 0)), prop(131104, px(sheet, 0)),
    prop(131105, px(sheet, 450)), prop(131087, px(sheet, 200)),
    prop(262150, px(sheet, 0)), prop(262151, px(sheet, 0)),
    prop(458753, pool(sheet, 'assets', {'m_FileID': 0, 'm_PathID': BLUE_ID}, 6)),
    prop(262153, enum(sheet, 'scale-to-fit')),
    prop(327681, [number(sheet, 2), number(sheet, 2)]),
])
refs[node['rid']], refs[serialized['rid']] = node, serialized
doc['references']['RefIds'].extend([node, serialized])
refs[stage]['data']['m_Children'].append({'rid': node['rid']})
for r in old_doc['references']['RefIds']:
    if r['rid'] not in [stage, icons, club_root]:
        assert refs[r['rid']] == r, r['rid']
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
assert refs[stage]['data']['m_Children'] == [{'rid': icons}, {'rid': node['rid']}]
header = objects[HEADER_ID].read_typetree()
header_refs = {r['rid']: r for r in header['references']['RefIds']}
underlay = named(header_refs, 'ReportIconsUnderBackgroundLayer')
background = named(header_refs, 'PlayerTopBackgroundTextureLayer')
header_order = [p['rid'] for p in header_refs[1004]['data']['m_Children']]
assert header_order.index(underlay) < header_order.index(background)
doc_obj.save_typetree(doc)
sheet_obj.save_typetree(sheet)

bundle_obj = next(o for o in env.objects if o.type.name == 'AssetBundle')
metadata = bundle_obj.read_typetree()
for key, info in metadata['m_Container']:
    pointers = copy.deepcopy(metadata['m_PreloadTable'][info['preloadIndex']:info['preloadIndex'] + info['preloadSize']])
    if any(p['m_FileID'] == 0 and p['m_PathID'] in [HEADER_ID, HEADER_STYLE_ID, DOC_ID, SHEET_ID] for p in pointers):
        info['preloadIndex'] = len(metadata['m_PreloadTable'])
        pointers.append({'m_FileID': 0, 'm_PathID': BLUE_ID})
        info['preloadSize'] = len(pointers)
        metadata['m_PreloadTable'].extend(pointers)
start = len(metadata['m_PreloadTable'])
metadata['m_PreloadTable'].append({'m_FileID': 0, 'm_PathID': BLUE_ID})
metadata['m_Container'].append(('playertopbluelight', {'preloadIndex': start, 'preloadSize': 1,
                                                    'asset': {'m_FileID': 0, 'm_PathID': BLUE_ID}}))
metadata['m_Container'].sort(key=lambda pair: pair[0])
bundle_obj.save_typetree(metadata)
OUT.mkdir(exist_ok=True)
destination = OUT / WORLD
destination.write_bytes(env.file.save(packer='lz4'))
check_env, check = load(destination)
assert set(check) == set(objects) | {BLUE_ID}
for pid, digest in original_hashes.items():
    if pid not in [DOC_ID, SHEET_ID, bundle_obj.path_id]:
        assert hashlib.sha256(check[pid].get_raw_data()).digest() == digest, pid
for pid, tree in [(DOC_ID, doc), (SHEET_ID, sheet), (bundle_obj.path_id, metadata)]:
    assert check[pid].read_typetree() == tree, pid
assert check[BLUE_ID].get_raw_data() == blue_source.get_raw_data()
assert check[BLUE_ID].read().image.tobytes() == blue_source.read().image.tobytes()
assert hashlib.sha256(source.read_bytes()).digest() == source_hash

# Include the unchanged v12 foreground so this is a complete, installable two-bundle package.
global_source = PACKAGES / GLOBAL
g_env, g_objects = load(global_source)
if -910000000000101 not in g_objects:
    global_source = BASE / GLOBAL
else:
    g_doc = g_objects[-4194025542157271532].read_typetree()
    if any(r.get('data', {}).get('name') == 'ReportMiddleBlueLightLayer' for r in g_doc['references']['RefIds']):
        global_source = BASE / GLOBAL
shutil.copyfile(global_source, OUT / GLOBAL)
assert (OUT / GLOBAL).read_bytes() == global_source.read_bytes()

readme = '''蓝光200%、国旗队徽间距80px v13

备份后替换本包global和gameworld两个同名bundle，再重启游戏。
global文件沿用上版头像完整显示版本，本次实际改动在gameworld包。
backgrounds bundle不需要替换。

从下到上的顺序：
俱乐部颜色渐变 → 国旗与队徽 → PlayerTopBlueLight（200%）→ PlayerTopBackground → CA000（115%）→ 球员头像。

国旗和队徽各150×150px，边缘之间间距80px，整组总宽380px，保持居中。
BlueLight以450×200的中间区域为基准，中心缩放200%，透明通道和DXT5图片数据保持不变。
头像外框保持200×200，仅内部头像图片缩放75%、等比完整显示。
其他布局、背景透明度、栏目高度及绑定均保持上版设置。

成品已重读验证层级、缩放、间距、预加载和原有未修改资源字节。源packages文件未覆盖。
游戏内显示效果需确认。
'''
(OUT / '安装说明.txt').write_text(readme, encoding='utf-8-sig')
(OUT / '修改记录.json').write_text(json.dumps({
    'gameworld_source': str(source), 'global_source_unchanged': str(global_source),
    'source_sha256': source_hash.hex(), 'blue_light_scale': 2.0,
    'flag_club_edge_gap_px': 80, 'flag_club_group_width_px': 380,
    'layer_order': ['gradient', 'flag + club logo', 'BlueLight', 'PlayerTopBackground', 'CA000', 'portrait'],
    'untouched_gameworld_objects': len(original_hashes) - 3,
}, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'scale': 2.0, 'gap': 80,
                  'untouched_gameworld_objects': len(original_hashes) - 3,
                  'foreground_global_unchanged': True}, ensure_ascii=True))
