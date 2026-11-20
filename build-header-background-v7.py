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
OUT = ROOT / '俱乐部渐变球场背景-v7'
BUNDLE = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BG_BUNDLE = 'ui-backgrounds_assets_common.bundle'
HEADER_ID = 5775949770471550939
STYLE_ID = -1940069326759809061
TEXTURE_ID = -910000000000001
CAB = 'CAB-1ab8e16d7264cd64aba00192bdf91ea2'

# Preserve Unity's null-reference registry entry; UnityPy's writer omits its guard.
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

env = UnityPy.load(str(PACKAGES / BUNDLE))
objects = {obj.path_id: obj for obj in env.objects}
header_obj, style_obj = objects[HEADER_ID], objects[STYLE_ID]
asset_file = header_obj.assets_file
assert asset_file.name == CAB
h, s = header_obj.read_typetree(), style_obj.read_typetree()
old_h, old_s = copy.deepcopy(h), copy.deepcopy(s)
old_object_hashes = {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in objects.items()}
old_externals = [(x.path, x.guid, x.type) for x in asset_file.externals]
source_bundle_hash = hashlib.sha256((PACKAGES / BUNDLE).read_bytes()).hexdigest()

bg_env = UnityPy.load(str(PACKAGES / BG_BUNDLE))
texture_obj = next(obj for obj in bg_env.objects if obj.path_id == TEXTURE_ID)
texture = texture_obj.read_typetree()
assert texture_obj.type.name == 'Texture2D' and texture['m_Name'] == 'PlayerTopBackground'
texture_cab = texture_obj.assets_file.name
external_path = f'archive:/{texture_cab}/{texture_cab}'
external_matches = [i + 1 for i, x in enumerate(asset_file.externals) if x.path == external_path]
if external_matches:
    file_id = external_matches[0]
else:
    entry = copy.copy(asset_file.externals[-1])
    entry.path = external_path
    entry.guid = bytes(16)
    entry.type = 0
    entry.temp_empty = ''
    asset_file.externals.append(entry)
    file_id = len(asset_file.externals)

refs = {r['rid']: r for r in h['references']['RefIds']}
node_rid = max(refs) + 1
serialized_rid = node_rid + 1
element_id = 1900200000
assert all(r.get('data', {}).get('m_Id') != element_id for r in refs.values())
image_node = copy.deepcopy(refs[1008])
image_serial = copy.deepcopy(refs[refs[1008]['data']['m_SerializedData']['rid']])
image_node['rid'], image_serial['rid'] = node_rid, serialized_rid
nd = image_node['data']
nd.update(m_Id=element_id, m_Parent={'rid': 1004}, m_Children=[],
          m_Classes=[], m_SerializedData={'rid': serialized_rid})
sd = image_serial['data']
sd.update(uxmlAssetId=element_id, name='PlayerTopBackgroundTextureLayer',
          name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)

def value(pool, item, typ):
    if item not in s[pool]:
        s[pool].append(item)
    return {'m_ValueType': typ, 'valueIndex': s[pool].index(item)}
def px(v):
    return value('dimensions', {'unit': 1, 'value': float(v)}, 3)
def percent(v):
    return value('dimensions', {'unit': 2, 'value': float(v)}, 3)
def enum(v):
    return value('strings', v, 7)
def prop(pid, v):
    return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [v]}

image_pointer = {'m_FileID': file_id, 'm_PathID': TEXTURE_ID}
rule = {'m_ComplexSelectors': [], 'm_Properties': [
    prop(131102, enum('absolute')),
    prop(131089, px(0)), prop(131104, px(0)),
    prop(131105, percent(100)), prop(131087, percent(100)),
    prop(262150, px(0)), prop(262151, px(0)),
    prop(458753, value('assets', image_pointer, 6)),
    prop(262153, enum('scale-and-crop')),
    prop(458767, value('floats', 0.30, 2)),
], 'line': -1}
nd['m_RuleIndex'] = len(s['m_Rules'])
s['m_Rules'].append(rule)
h['references']['RefIds'].extend([image_node, image_serial])
refs[node_rid], refs[serialized_rid] = image_node, image_serial
# Parent paints the bound club gradient, then the photo, then all existing content.
refs[1004]['data']['m_Children'].insert(0, {'rid': node_rid})

for old_ref in old_h['references']['RefIds']:
    expected = copy.deepcopy(old_ref)
    if old_ref['rid'] == 1004:
        expected['data']['m_Children'].insert(0, {'rid': node_rid})
    assert refs[old_ref['rid']] == expected
assert refs[1007] == next(r for r in old_h['references']['RefIds'] if r['rid'] == 1007)
assert s['m_Rules'][:len(old_s['m_Rules'])] == old_s['m_Rules']
assert h['m_Usings'] == old_h['m_Usings']
for ref in h['references']['RefIds']:
    d = ref.get('data', {})
    if 'm_Id' not in d:
        continue
    for child in d.get('m_Children', []):
        assert refs[child['rid']]['data']['m_Parent']['rid'] == ref['rid']
    if 'm_RuleIndex' in d:
        assert -1 <= d['m_RuleIndex'] < len(s['m_Rules'])
    rid = d.get('m_SerializedData', {}).get('rid', -2)
    if rid >= 0:
        assert refs[rid]['data']['uxmlAssetId'] == d['m_Id']

header_obj.save_typetree(h)
style_obj.save_typetree(s)
OUT.mkdir(exist_ok=True)
bundle_path = OUT / BUNDLE
bundle_path.write_bytes(env.file.save(packer='lz4'))

# Reload the actual saved bundle and verify untouched assets, references, and layer order.
check = UnityPy.load(str(bundle_path))
check_objects = {o.path_id: o for o in check.objects}
assert set(check_objects) == set(objects)
for pid, digest in old_object_hashes.items():
    if pid not in [HEADER_ID, STYLE_ID]:
        assert hashlib.sha256(check_objects[pid].get_raw_data()).digest() == digest, pid
check_h = check_objects[HEADER_ID].read_typetree()
check_s = check_objects[STYLE_ID].read_typetree()
assert check_h == h
assert check_s['m_Rules'] == s['m_Rules']
assert check_s['assets'] == s['assets']
check_external = check_objects[HEADER_ID].assets_file.externals
assert [(x.path, x.guid, x.type) for x in check_external[:len(old_externals)]] == old_externals
assert check_external[file_id - 1].path == external_path
assert hashlib.sha256((PACKAGES / BUNDLE).read_bytes()).hexdigest() == source_bundle_hash

def normalize(v, key=''):
    if isinstance(v, dict):
        return {k: normalize(x, k) for k, x in v.items()}
    if isinstance(v, list):
        a = [normalize(x) for x in v]
        if key == 'RefIds':
            for r in a:
                r.setdefault('data', {})
            return a
        return {'Array': a}
    return v

for name, doc in [
    (f'PlayerReportHeader-{CAB}-{HEADER_ID}.json', check_h),
    (f'inlineStyle-{CAB}-{STYLE_ID}.json', check_s),
]:
    (OUT / name).write_text(json.dumps(normalize(doc), ensure_ascii=False, indent=2), encoding='utf-8')

readme = f'''PlayerReportHeader：俱乐部渐变 + PlayerTopBackground 球场背景 v7。

推荐使用方式：
备份皮肤 packages 内的 {BUNDLE}，再用本目录同名 bundle 替换它。
保留现有 {BG_BUNDLE}，其中已含新增图片。
global bundle不需要替换，现有左中右布局、头像、国旗和队徽旋转均保留。

图片：PlayerTopBackground，Texture2D Path ID {TEXTURE_ID}。
保留原有 teamcontainer.TitlebarBackgroundColour 的动态渐变绑定。
该颜色由原游戏根据当前球队提供，原始渐变方式不变。
球场图片以30%不透明度覆盖在渐变上方，信息内容位于图片上方且不受透明度影响。
图片铺满头部，保持比例并居中裁剪；原图的蓝色会少量保留，不属于完全替换图片像素颜色。
没有修改共享图片或栏目高度，也没有改动任何现有信息和操作绑定。

手动导入JSON方式（与替换bundle二选一）：
在gameworld bundle导入两份JSON：
PlayerReportHeader Path ID {HEADER_ID}
inlineStyle Path ID {STYLE_ID}
并确保Externals中下列引用的m_FileID为{file_id}（若列表编号从0开始，则为{file_id - 1}）：
{external_path}
GUID：00000000000000000000000000000000；Type：0。
本包JSON使用m_FileID={file_id}, m_PathID={TEXTURE_ID}。
当前源bundle原有{len(old_externals)}项Externals，已在成品bundle中正确补入引用。

资源说明：e73b49a20543e9ffade1770a3bbc8638.bundle是背景资源包标识；
已实测新增纹理所在的序列化文件名为{texture_cab}，跨文件引用使用这个实际名称。

已重新打开生成的bundle，核对所有未修改资源字节完全一致、原绑定不变、背景引用正确。
源packages文件未覆盖。尚未进入游戏验证实际显示效果。
'''
(OUT / '导入说明.txt').write_text(readme, encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'), 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
print('Saved bundle, two JSONs, and instructions. Reload validation passed.')
print('External FileID:', file_id, 'Texture file:', texture_cab)
print('Untouched assets verified:', len(objects) - 2)
print('ZIP size:', OUT.with_suffix('.zip').stat().st_size)
