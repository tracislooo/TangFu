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

PACKAGES = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
NAME = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
OUT = ROOT / '中间头像五层叠加-v10'
BANNER_ID = -4194025542157271532
STYLE_ID = 8045407476604796436
PERSON_TEMPLATE_ID = -4696340654933359536
BLUE_ID = -910000000000002
CARD_ID = -910000000000003
PRIVATE_PERSON_ID = -910000000000101
PRIVATE_PERSON_STYLE_ID = -910000000000102
PRIVATE_ALIAS = 'ReportMiddleSquarePersonPicture'

# UnityPy needs the missing null-reference guard when writing Unity 6 UXML data.
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

paths = [PACKAGES / NAME, PACKAGES / 'ui-backgrounds_assets_common.bundle',
         PACKAGES / 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']
source_hashes = {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in paths}
env = UnityPy.load(str(paths[0]))
objects = {o.path_id: o for o in env.objects}
original_object_hashes = {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in objects.items()}
banner_obj, style_obj = objects[BANNER_ID], objects[STYLE_ID]
asset_file = banner_obj.assets_file
banner, style = banner_obj.read_typetree(), style_obj.read_typetree()
old_banner, old_style = copy.deepcopy(banner), copy.deepcopy(style)
refs = {r['rid']: r for r in banner['references']['RefIds']}
original_externals = [(e.path, e.guid, e.type) for e in asset_file.externals]
next_rid = max(refs) + 1
next_element_id = 1900300000

def named(name):
    sd = next(r for r in refs.values() if r.get('data', {}).get('name') == name)
    return next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == sd['rid'])['rid']

middle = named('ReportPortraitStatusColumn')
stage = named('ReportPortraitLayerStage')
icons = named('ReportFlagClubBackgroundLayer')
frame = named('PersonPictureFrame')
person_node = named('PersonPicture')
assert refs[stage]['data']['m_Children'] == [{'rid': icons}, {'rid': frame}]
assert refs[frame]['data']['m_Parent']['rid'] == stage

def pool(sheet, key, value, kind):
    if value not in sheet[key]:
        sheet[key].append(value)
    return {'m_ValueType': kind, 'valueIndex': sheet[key].index(value)}
def px(sheet, value):
    return pool(sheet, 'dimensions', {'unit': 1, 'value': float(value)}, 3)
def pct(sheet, value):
    return pool(sheet, 'dimensions', {'unit': 2, 'value': float(value)}, 3)
def enum(sheet, value):
    return pool(sheet, 'strings', value, 7)
def number(sheet, value):
    # Store the float32 value that will survive serialization exactly.
    value = struct.unpack('<f', struct.pack('<f', value))[0]
    return pool(sheet, 'floats', value, 2)
def prop(pid, values):
    if isinstance(values, dict):
        values = [values]
    return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1, 'm_Values': values}
def rule(sheet, properties):
    result = len(sheet['m_Rules'])
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': properties, 'line': -1})
    return result
def update_rule(sheet, node, properties):
    old_index = node['data']['m_RuleIndex']
    old_properties = copy.deepcopy(sheet['m_Rules'][old_index]['m_Properties']) if old_index >= 0 else []
    changed_ids = {p['m_Id'] for p in properties}
    old_properties = [p for p in old_properties if p['m_Id'] not in changed_ids]
    node['data']['m_RuleIndex'] = rule(sheet, old_properties + properties)

bg = UnityPy.load(str(paths[1]))
bg_objects = {o.path_id: o for o in bg.objects}
texture_sources = {BLUE_ID: bg_objects[BLUE_ID], CARD_ID: bg_objects[CARD_ID]}
assert texture_sources[BLUE_ID].assets_file.name == 'CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8'
assert texture_sources[BLUE_ID].read_typetree()['m_Name'] == 'PlayerTopBlueLight'
assert texture_sources[CARD_ID].read_typetree()['m_Name'] == 'CA000'

# Keep texture pixels and DXT5 encoding exactly as the supplied backgrounds bundle.
texture_type = copy.copy(texture_sources[BLUE_ID].serialized_type)
assert not texture_type.type_dependencies
asset_file.types.append(texture_type)
texture_type_index = len(asset_file.types) - 1
for pid, source in texture_sources.items():
    assert pid not in objects
    assert source.read_typetree()['m_StreamData']['size'] == 0
    assert source.assets_file.version == asset_file.version
    new = copy.copy(source)
    new.assets_file = asset_file
    new.type_id = texture_type_index
    new.serialized_type = texture_type
    new.set_raw_data(source.get_raw_data())
    asset_file.objects[pid] = new

def layer(name, texture_id, left, top, width, height):
    global next_rid, next_element_id
    original = refs[frame]
    original_sd = refs[original['data']['m_SerializedData']['rid']]
    node, sd = copy.deepcopy(original), copy.deepcopy(original_sd)
    node['rid'], sd['rid'] = next_rid, next_rid + 1
    next_rid += 2
    element_id = next_element_id
    next_element_id += 1
    d = node['data']
    d.update(m_Id=element_id, m_Parent={'rid': stage}, m_Children=[], m_Classes=[],
             m_SerializedData={'rid': sd['rid']})
    sd['data'].update(uxmlAssetId=element_id, name=name, name_UxmlAttributeFlags=1,
                      pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    asset = pool(style, 'assets', {'m_FileID': 0, 'm_PathID': texture_id}, 6)
    d['m_RuleIndex'] = rule(style, [
        prop(131102, enum(style, 'absolute')), prop(131089, px(style, left)),
        prop(131104, px(style, top)), prop(131105, px(style, width)),
        prop(131087, px(style, height)), prop(131084, number(style, 0)),
        prop(131085, number(style, 0)), prop(262150, px(style, 0)),
        prop(262151, px(style, 0)), prop(458753, asset),
        prop(262153, enum(style, 'scale-to-fit')),
    ])
    refs[node['rid']], refs[sd['rid']] = node, sd
    banner['references']['RefIds'].extend([node, sd])
    return node['rid']

blue = layer('ReportMiddleBlueLightLayer', BLUE_ID, 0, 0, 450, 200)
card = layer('ReportMiddleCA000Layer', CARD_ID, 125, 0, 200, 200)
# Sibling order determines drawing order. The header background remains below this stage.
refs[stage]['data']['m_Children'] = [{'rid': rid} for rid in [icons, blue, card, frame]]
update_rule(style, refs[frame], [
    prop(131105, px(style, 200)), prop(131087, px(style, 200)),
    prop(327681, [number(style, 0.8), number(style, 0.8)]),
])

# Make a private square template for this one portrait, preserving the shared template.
original_person_obj = objects[PERSON_TEMPLATE_ID]
person = copy.deepcopy(original_person_obj.read_typetree())
original_person_style_id = person['inlineSheet']['m_PathID']
original_person_style_obj = objects[original_person_style_id]
person_style = copy.deepcopy(original_person_style_obj.read_typetree())
person['m_Name'] = PRIVATE_ALIAS
person['inlineSheet'] = {'m_FileID': 0, 'm_PathID': PRIVATE_PERSON_STYLE_ID}
person_style['m_Name'] = PRIVATE_ALIAS + 'InlineStyle'
person_refs = {r['rid']: r for r in person['references']['RefIds']}
plain_sd = next(r for r in person_refs.values() if r['type']['class'] == 'VisualElement/UxmlSerializedData')
square_fitters = []
portrait_images = []
for r in person_refs.values():
    d = r.get('data', {})
    if 'm_RuleIndex' not in d or d['m_FullTypeName'] == 'UnityEngine.UIElements.UXML':
        continue
    if d['m_FullTypeName'] == 'SI.Bindable.SIAspectRatioFitter':
        # Replace automatic image-ratio fitting with a square container only in this copy.
        square_fitters.append(r['rid'])
        d['m_FullTypeName'] = 'UnityEngine.UIElements.VisualElement'
        serialized = person_refs[d['m_SerializedData']['rid']]
        old_data = serialized['data']
        serialized['type'] = copy.deepcopy(plain_sd['type'])
        serialized['data'] = {k: copy.deepcopy(old_data[k]) if k in old_data else copy.deepcopy(v)
                              for k, v in plain_sd['data'].items()}
        update_rule(person_style, r, [
            prop(131105, pct(person_style, 100)), prop(131087, pct(person_style, 100)),
            prop(131102, enum(person_style, 'relative')),
        ])
    elif d['m_FullTypeName'] == 'SI.Bindable.SIImage':
        portrait_images.append(r['rid'])
        image_sd = person_refs[d['m_SerializedData']['rid']]['data']
        image_sd.update(ScaleMode=1, ScaleMode_UxmlAttributeFlags=1,
                        scaleMode=1, scaleMode_UxmlAttributeFlags=1)
        update_rule(person_style, r, [
            prop(131105, pct(person_style, 100)), prop(131087, pct(person_style, 100)),
            prop(262153, enum(person_style, 'scale-and-crop')),
        ])
    elif d['m_FullTypeName'] not in ['FM.UI.PluginContextMenuBindings']:
        update_rule(person_style, r, [
            prop(131105, pct(person_style, 100)), prop(131087, pct(person_style, 100)),
        ])
assert len(square_fitters) == len(portrait_images) == 4

for new_id, original, tree in [
    (PRIVATE_PERSON_ID, original_person_obj, person),
    (PRIVATE_PERSON_STYLE_ID, original_person_style_obj, person_style),
]:
    assert new_id not in asset_file.objects
    new = copy.copy(original)
    new.path_id = new_id
    new.data = None
    new._read_until = None
    new.save_typetree(tree)
    asset_file.objects[new_id] = new

template_hash = hashlib.md5(PRIVATE_ALIAS.encode()).hexdigest()
banner['m_Usings'].append({'alias': PRIVATE_ALIAS, 'path': template_hash,
                           'asset': {'m_FileID': 0, 'm_PathID': PRIVATE_PERSON_ID}})
refs[person_node]['data']['m_TemplateAlias'] = PRIVATE_ALIAS
person_sd_rid = refs[person_node]['data']['m_SerializedData']['rid']
refs[person_sd_rid]['data'].update(
    templateId=PRIVATE_ALIAS, templateId_UxmlAttributeFlags=1,
    template={'m_FileID': 0, 'm_PathID': PRIVATE_PERSON_ID}, template_UxmlAttributeFlags=1)

# Confirm unrelated existing nodes, old rules and bindings are untouched.
allowed_changes = {stage, frame, person_node, person_sd_rid}
for old in old_banner['references']['RefIds']:
    if old['rid'] not in allowed_changes:
        assert refs[old['rid']] == old, old['rid']
assert style['m_Rules'][:len(old_style['m_Rules'])] == old_style['m_Rules']
assert banner['m_Usings'][:-1] == old_banner['m_Usings']
assert refs[middle] == next(r for r in old_banner['references']['RefIds'] if r['rid'] == middle)
seen = set()
def visit(rid):
    assert rid not in seen
    seen.add(rid)
    d = refs[rid].get('data', {})
    for child in d.get('m_Children', []):
        assert refs[child['rid']]['data']['m_Parent']['rid'] == rid
        visit(child['rid'])
visit(banner['m_VisualTree']['rid'])
assert seen == {rid for rid, r in refs.items() if 'm_Id' in r.get('data', {})}
assert len({r['data']['m_Id'] for r in refs.values() if 'm_Id' in r.get('data', {})}) == len(seen)

banner_obj.save_typetree(banner)
style_obj.save_typetree(style)
bundle_obj = next(o for o in env.objects if o.type.name == 'AssetBundle')
bundle = bundle_obj.read_typetree()
old_bundle = copy.deepcopy(bundle)
extra_pointers = [{'m_FileID': 0, 'm_PathID': pid} for pid in
                  [BLUE_ID, CARD_ID, PRIVATE_PERSON_STYLE_ID, PRIVATE_PERSON_ID]]
changed_container_indexes = []
for i, (key, info) in enumerate(bundle['m_Container']):
    pointers = copy.deepcopy(bundle['m_PreloadTable'][info['preloadIndex']:info['preloadIndex'] + info['preloadSize']])
    if any(p['m_FileID'] == 0 and p['m_PathID'] in [BANNER_ID, STYLE_ID] for p in pointers):
        info['preloadIndex'] = len(bundle['m_PreloadTable'])
        info['preloadSize'] = len(pointers) + len(extra_pointers)
        bundle['m_PreloadTable'].extend(pointers + copy.deepcopy(extra_pointers))
        changed_container_indexes.append(i)
assert changed_container_indexes
for key, pid, dependencies in [
    ('playertopbluelight', BLUE_ID, [BLUE_ID]),
    ('ca000', CARD_ID, [CARD_ID]),
    (template_hash, PRIVATE_PERSON_ID, [PRIVATE_PERSON_ID, PRIVATE_PERSON_STYLE_ID]),
    (template_hash, PRIVATE_PERSON_STYLE_ID, [PRIVATE_PERSON_ID, PRIVATE_PERSON_STYLE_ID]),
]:
    start = len(bundle['m_PreloadTable'])
    bundle['m_PreloadTable'].extend({'m_FileID': 0, 'm_PathID': dep} for dep in dependencies)
    bundle['m_Container'].append((key, {'preloadIndex': start, 'preloadSize': len(dependencies),
                                      'asset': {'m_FileID': 0, 'm_PathID': pid}}))
bundle['m_Container'].sort(key=lambda pair: pair[0])
bundle_obj.save_typetree(bundle)
OUT.mkdir(exist_ok=True)
destination = OUT / NAME
destination.write_bytes(env.file.save(packer='lz4'))

check = UnityPy.load(str(destination))
check_objects = {o.path_id: o for o in check.objects}
assert set(check_objects) == set(objects) | {BLUE_ID, CARD_ID, PRIVATE_PERSON_ID, PRIVATE_PERSON_STYLE_ID}
for pid, digest in original_object_hashes.items():
    if pid not in [BANNER_ID, STYLE_ID, bundle_obj.path_id]:
        assert hashlib.sha256(check_objects[pid].get_raw_data()).digest() == digest, pid
for pid, tree in [(BANNER_ID, banner), (STYLE_ID, style), (PRIVATE_PERSON_ID, person),
                  (PRIVATE_PERSON_STYLE_ID, person_style), (bundle_obj.path_id, bundle)]:
    assert check_objects[pid].read_typetree() == tree, pid
assert [(e.path, e.guid, e.type) for e in check_objects[BANNER_ID].assets_file.externals] == original_externals
for pid, source in texture_sources.items():
    assert check_objects[pid].get_raw_data() == source.get_raw_data()
    assert check_objects[pid].read().image.tobytes() == source.read().image.tobytes()
assert all(hashlib.sha256(Path(p).read_bytes()).hexdigest() == digest for p, digest in source_hashes.items())

readme = '''中间头像五层叠加 v10

本次修改的是 global bundle，请备份后替换本目录的同名文件：
ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle
重新启动游戏并加载皮肤。

从下到上的顺序：
1. 现有 PlayerTopBackground 和俱乐部动态渐变（保持 gameworld 的现有背景层）。
2. 现有国旗与俱乐部队徽。
3. PlayerTopBlueLight（-910000000000002），位于450×200的中间叠层区域，保持图片比例居中显示。
4. CA000（-910000000000003），居中位于200×200的区域，卡片保持原图比例完整显示。
5. 球员头像，200×200正方形区域、中心缩放80%，最终显示为160×160。

球员头像使用此中间区域专用的正方形模板，保留原来的球员图片绑定与分支。
只在专用模板中移除按图片比例调整容器的逻辑，图片保持比例并居中裁剪到正方形。
原来的共享 PersonPicture 模板及其他页面头像保持不变。

图片取自你提供的 ui-backgrounds_assets_common.bundle / CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8。
为避免手动导入JSON时漏掉Externals，成品global bundle直接内置两张图片，使用本地FileID=0。
图片Path ID、名字、DXT5数据和透明度不变，并补齐预加载条目。

无需替换 gameworld 或 backgrounds bundle。本次未修改头部高度、左右信息、状态区域及国旗和队徽的现有设置。
源packages文件未覆盖；成品已重新加载，核对层级、绑定、预加载与全部未修改资源字节。
实际显示效果需游戏内确认。
'''
(OUT / '安装与叠层说明.txt').write_text(readme, encoding='utf-8-sig')
record = {'source_sha256': source_hashes, 'output_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
          'source_texture_cab': texture_sources[BLUE_ID].assets_file.name,
          'layer_order': ['PlayerTopBackground (existing header)', 'nation flag + club logo',
                          'PlayerTopBlueLight', 'CA000', 'square player portrait'],
          'portrait_square_px': 200, 'portrait_scale': 0.8,
          'portrait_rendered_px': 160,
          'private_template_path_id': PRIVATE_PERSON_ID,
          'untouched_original_objects': len(original_object_hashes) - 3}
(OUT / '修改记录.json').write_text(json.dumps(record, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'untouched_original_objects': len(original_object_hashes) - 3,
                  'stage': [450, 200], 'portrait': [200, 200], 'portrait_scale': 0.8,
                  'layers': ['header background', 'icons', 'blue light', 'CA000', 'portrait'],
                  'only_global_bundle_changed': True}, ensure_ascii=True))
