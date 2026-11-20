import copy
import hashlib
import json
import sys
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

PACKAGES = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
BUNDLE = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT = ROOT / '头部背景图片修复-v8'
HEADER_ID = 5775949770471550939
STYLE_ID = -1940069326759809061
TEXTURE_ID = -910000000000001

# Preserve Unity's null managed-reference registry entries when writing.
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

source_path = PACKAGES / BUNDLE
source_hash = hashlib.sha256(source_path.read_bytes()).digest()
env = UnityPy.load(str(source_path))
objects = {o.path_id: o for o in env.objects}
original_hashes = {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in objects.items()}
header_obj, style_obj = objects[HEADER_ID], objects[STYLE_ID]
asset_file = header_obj.assets_file
header, style = header_obj.read_typetree(), style_obj.read_typetree()
original_header = copy.deepcopy(header)
original_style = copy.deepcopy(style)
original_externals = [(x.path, x.guid, x.type) for x in asset_file.externals]
refs = {r['rid']: r for r in header['references']['RefIds']}
layer_serial = next(r for r in refs.values() if r.get('data', {}).get('name') == 'PlayerTopBackgroundTextureLayer')
layer = next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == layer_serial['rid'])
layer_rule = style['m_Rules'][layer['data']['m_RuleIndex']]
image_prop = next(p for p in layer_rule['m_Properties'] if p['m_Id'] == 458753)
value = image_prop['m_Values'][0]
assert value['m_ValueType'] == 6
index = value['valueIndex']
assert style['assets'][index]['m_PathID'] == TEXTURE_ID
style['assets'][index] = {'m_FileID': 0, 'm_PathID': TEXTURE_ID}

bg = UnityPy.load(str(PACKAGES / 'ui-backgrounds_assets_common.bundle'))
texture_obj = next(o for o in bg.objects if o.path_id == TEXTURE_ID)
texture_data = texture_obj.read_typetree()
assert texture_data['m_Name'] == 'PlayerTopBackground'
assert texture_data['m_StreamData']['size'] == 0
assert len(texture_data['image data']) > 0
assert texture_obj.assets_file.version == asset_file.version
assert texture_obj.assets_file.header.version == asset_file.header.version
assert TEXTURE_ID not in objects

# Copy the original compressed image bytes without changing pixels or format.
texture_type = copy.copy(texture_obj.serialized_type)
assert not texture_type.type_dependencies
asset_file.types.append(texture_type)
local_texture = copy.copy(texture_obj)
local_texture.assets_file = asset_file
local_texture.type_id = len(asset_file.types) - 1
local_texture.serialized_type = texture_type
texture_raw = texture_obj.get_raw_data()
local_texture.set_raw_data(texture_raw)
asset_file.objects[TEXTURE_ID] = local_texture

# Preload the local texture with this header, retaining every existing preload.
bundle_obj = next(o for o in env.objects if o.type.name == 'AssetBundle')
bundle_data = bundle_obj.read_typetree()
original_bundle = copy.deepcopy(bundle_data)
preloads = bundle_data['m_PreloadTable']
changed_containers = []
for key, info in bundle_data['m_Container']:
    start, count = info['preloadIndex'], info['preloadSize']
    existing = copy.deepcopy(preloads[start:start + count])
    if info['asset'] == {'m_FileID': 0, 'm_PathID': HEADER_ID} or any(
        p['m_FileID'] == 0 and p['m_PathID'] in (HEADER_ID, STYLE_ID) for p in existing
    ):
        info['preloadIndex'] = len(preloads)
        info['preloadSize'] = len(existing) + 1
        preloads.extend(existing + [{'m_FileID': 0, 'm_PathID': TEXTURE_ID}])
        changed_containers.append(key)
assert changed_containers

style_obj.save_typetree(style)
bundle_obj.save_typetree(bundle_data)
OUT.mkdir(exist_ok=True)
destination = OUT / BUNDLE
destination.write_bytes(env.file.save(packer='lz4'))

check = UnityPy.load(str(destination))
check_objects = {o.path_id: o for o in check.objects}
assert set(check_objects) == set(objects) | {TEXTURE_ID}
for pid, digest in original_hashes.items():
    if pid not in (STYLE_ID, bundle_obj.path_id):
        assert hashlib.sha256(check_objects[pid].get_raw_data()).digest() == digest, pid
assert check_objects[HEADER_ID].read_typetree() == original_header
assert check_objects[STYLE_ID].read_typetree() == style
assert check_objects[TEXTURE_ID].get_raw_data() == texture_raw
assert check_objects[TEXTURE_ID].read_typetree() == texture_data
assert [(x.path, x.guid, x.type) for x in check_objects[HEADER_ID].assets_file.externals] == original_externals
check_bundle = check_objects[bundle_obj.path_id].read_typetree()
assert check_bundle == bundle_data
for key, info in check_bundle['m_Container']:
    if key in changed_containers:
        pointers = check_bundle['m_PreloadTable'][info['preloadIndex']:info['preloadIndex'] + info['preloadSize']]
        assert {'m_FileID': 0, 'm_PathID': TEXTURE_ID} in pointers
assert hashlib.sha256(source_path.read_bytes()).digest() == source_hash

# Decode the actual embedded texture and compare it with the source image.
actual_image = check_objects[TEXTURE_ID].read().image
source_image = texture_obj.read().image
assert actual_image.size == source_image.size == (1672, 941)
assert actual_image.tobytes() == source_image.tobytes()

readme = '''头部背景图片修复 v8

上一版仅导入两份 JSON 后，样式引用了第 8 个外部文件，但当前 bundle 只有 7 个外部引用，图片无法解析。
本版将 PlayerTopBackground 纹理直接内置到 gameworld bundle，样式使用本地 m_FileID=0，并补齐头部的纹理预加载。

安装方法：
1. 备份皮肤 packages 中的 ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle。
2. 用本包同名 bundle 替换它。本版必须替换 bundle，不是只导入两份 JSON。
3. 重新启动游戏并加载该皮肤。

已在你当前 packages 文件的基础上修复，保留现有头部高度、信息位置、头像布局、国旗与队徽及原有俱乐部动态渐变。
球场图片仍为 30% 不透明度，图片像素、尺寸、格式没有改变。
global bundle 和 ui-backgrounds bundle 不需要替换。

已重读生成的 bundle，验证本地图片引用、纹理解码、预加载，以及所有其他 UI 资源字节未变。
尚未在游戏内验证显示效果。
'''
(OUT / '安装说明.txt').write_text(readme, encoding='utf-8-sig')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'embedded_texture': TEXTURE_ID,
                  'pointer_file_id': 0, 'header_preloaded': changed_containers,
                  'untouched_objects': len(original_hashes) - 2,
                  'decoded_texture_size': actual_image.size,
                  'source_unchanged': True}, ensure_ascii=False))
