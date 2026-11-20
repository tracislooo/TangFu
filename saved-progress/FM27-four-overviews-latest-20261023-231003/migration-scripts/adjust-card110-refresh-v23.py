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

BASE = ROOT / '卡面上移15缩放90-v22'
OUT = ROOT / '卡面110同步新图片-v23'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BACKGROUNDS = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/ui-backgrounds_assets_common.bundle')
BANNER, STYLE, CARD = -4194025542157271532, 8045407476604796436, -910000000000003

def sha(data):
    return hashlib.sha256(data).hexdigest()

def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]

def load(path):
    env = UnityPy.load(str(path))
    return env, {o.path_id: o for o in env.objects}

source = BASE / GLOBAL
source_hash = sha(source.read_bytes())
background_hash = sha(BACKGROUNDS.read_bytes())
env, objects = load(source)
bg_env, bg_objects = load(BACKGROUNDS)
hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
doc = objects[BANNER].read_typetree()
sheet = objects[STYLE].read_typetree()
old_sheet = copy.deepcopy(sheet)
records = {r['rid']: r for r in doc['references']['RefIds']}
card_node = records[1162]
rule_index = card_node['data']['m_RuleIndex']
assert sum(r.get('data', {}).get('m_RuleIndex') == rule_index for r in records.values()) == 1
rule = sheet['m_Rules'][rule_index]

def decoded(rule, pid):
    prop, = [p for p in rule['m_Properties'] if p['m_Id'] == pid]
    return [sheet[{2: 'floats', 3: 'dimensions', 6: 'assets', 7: 'strings'}[v['m_ValueType']]][v['valueIndex']] for v in prop['m_Values']]

assert decoded(rule, 458753) == [{'m_FileID': 0, 'm_PathID': CARD}]
assert decoded(rule, 131104) == [{'unit': 1, 'value': -15.0}]
assert decoded(rule, 327681) == [f32(.9), f32(.9)]
assert decoded(rule, 262153) == ['scale-to-fit']
if f32(1.1) not in sheet['floats']:
    sheet['floats'].append(f32(1.1))
value = {'m_ValueType': 2, 'valueIndex': sheet['floats'].index(f32(1.1))}
scale_prop, = [p for p in rule['m_Properties'] if p['m_Id'] == 327681]
scale_prop['m_Values'] = [copy.deepcopy(value), copy.deepcopy(value)]
assert [p for p in rule['m_Properties'] if p['m_Id'] != 327681] == [p for p in old_sheet['m_Rules'][rule_index]['m_Properties'] if p['m_Id'] != 327681]
for i, old_rule in enumerate(old_sheet['m_Rules']):
    if i != rule_index:
        assert sheet['m_Rules'][i] == old_rule
for key in old_sheet:
    if key not in ['m_Rules', 'floats']:
        assert sheet[key] == old_sheet[key]

# Refresh the existing local texture at the same PathID; the PPtr and preload remain valid.
old_texture = objects[CARD].read_typetree()
new_texture = bg_objects[CARD].read_typetree()
assert objects[CARD].type.name == bg_objects[CARD].type.name == 'Texture2D'
assert objects[CARD].serialized_type.old_type_hash == bg_objects[CARD].serialized_type.old_type_hash
assert new_texture['m_Name'] == 'CA000'
assert new_texture['m_StreamData']['size'] == 0
new_raw = bg_objects[CARD].get_raw_data()
objects[CARD].set_raw_data(new_raw)
objects[STYLE].save_typetree(sheet)
OUT.mkdir(exist_ok=True)
destination = OUT / GLOBAL
destination.write_bytes(env.file.save(packer='lz4'))
check_env, check = load(destination)
assert check.keys() == objects.keys()
assert check[STYLE].read_typetree() == sheet
assert check[CARD].get_raw_data() == new_raw
assert check[CARD].read_typetree() == new_texture
assert check[CARD].read().image.tobytes() == bg_objects[CARD].read().image.tobytes()
for pid, digest in hashes.items():
    if pid not in [STYLE, CARD]:
        assert sha(check[pid].get_raw_data()) == digest, pid
assert sha(source.read_bytes()) == source_hash
assert sha(BACKGROUNDS.read_bytes()) == background_hash
shutil.copyfile(BASE / WORLD, OUT / WORLD)
assert (OUT / WORLD).read_bytes() == (BASE / WORLD).read_bytes()

readme = '''CA000卡面110%、同步最新图片 v23

基于v22。替换global、gameworld两个同名bundle后重启游戏。
实际改动仅在global：
1. CA000卡面scale从90%改为110%，top保持-15px。
2. 将packages/ui-backgrounds_assets_common.bundle中的最新CA000图片同步到global内嵌副本。
   图片尺寸576×800 → 640×680，纹理ID仍为-910000000000003，DXT5格式及新图片数据原样保留。
   卡面继续使用200×200容器、等比完整适配，无需因图片尺寸变化修改引用ID或容器。

当前引用是global内嵌图片。以后只替换backgrounds中的图片，不会自动更新这个内嵌副本；
需要再次同步到global。图片ID和名称保持不变时，不需要改布局中的引用。
gameworld原样随包提供。栏目高度185px、头像、BlueLight、国旗、队徽、左右信息保持原值。
源packages及旧版成品没有覆盖。
已重读验证参数、新图片解码内容及无关资源字节；游戏内效果待确认。
恢复本次修改可替换v22中的global文件。
'''
(OUT / '安装说明.txt').write_text(readme, encoding='utf-8-sig')
(OUT / '修改记录.json').write_text(json.dumps({
    'baseline': str(BASE), 'texture_source': str(BACKGROUNDS), 'texture_source_bundle_sha256': background_hash,
    'node_rid': 1162, 'rule_index': rule_index, 'style_path_id': STYLE, 'texture_path_id': CARD,
    'scale_before': .9, 'scale_after': 1.1, 'top_px': -15,
    'texture_before': {'size': [old_texture['m_Width'], old_texture['m_Height']], 'raw_sha256': hashes[CARD]},
    'texture_after': {'size': [new_texture['m_Width'], new_texture['m_Height']], 'raw_sha256': sha(new_raw)},
    'global_source_sha256': source_hash, 'global_output_sha256': sha(destination.read_bytes()),
    'untouched_global_assets_verified': len(objects) - 2, 'gameworld_unchanged': True,
}, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in OUT.iterdir():
        if path.is_file():
            z.write(path, path.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'scale': 1.1, 'top_px': -15,
                  'texture_size': [new_texture['m_Width'], new_texture['m_Height']],
                  'untouched_global_assets_verified': len(objects) - 2, 'gameworld_unchanged': True}, ensure_ascii=True))
