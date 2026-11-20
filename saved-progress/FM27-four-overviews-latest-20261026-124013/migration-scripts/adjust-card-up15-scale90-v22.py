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

BASE = ROOT / '头部与report-max高度185-v21'
OUT = ROOT / '卡面上移15缩放90-v22'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BANNER, STYLE = -4194025542157271532, 8045407476604796436
CARD_TEXTURE = -910000000000003

def sha(data):
    return hashlib.sha256(data).hexdigest()

def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]

def pooled(sheet, key, value, value_type):
    if value not in sheet[key]:
        sheet[key].append(value)
    return {'m_ValueType': value_type, 'valueIndex': sheet[key].index(value)}

source = BASE / GLOBAL
source_hash = sha(source.read_bytes())
env = UnityPy.load(str(source))
objects = {o.path_id: o for o in env.objects}
hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
doc = objects[BANNER].read_typetree()
sheet = objects[STYLE].read_typetree()
original = copy.deepcopy(sheet)
records = {r['rid']: r for r in doc['references']['RefIds']}

def decoded(rule, pid):
    prop, = [p for p in rule['m_Properties'] if p['m_Id'] == pid]
    return [sheet[{2: 'floats', 3: 'dimensions', 6: 'assets', 7: 'strings'}[v['m_ValueType']]][v['valueIndex']] for v in prop['m_Values']]

card = records[1162]
rule_index = card['data']['m_RuleIndex']
rule = sheet['m_Rules'][rule_index]
assert decoded(rule, 458753) == [{'m_FileID': 0, 'm_PathID': CARD_TEXTURE}]
card_name = records[card['data']['m_SerializedData']['rid']]['data']['name']
assert sum(r.get('data', {}).get('m_RuleIndex') == rule_index for r in records.values()) == 1
old_top = decoded(rule, 131104)
old_scale = decoded(rule, 327681)
assert old_top == [{'unit': 1, 'value': 0.0}]
assert old_scale == [f32(1.15), f32(1.15)]

top_prop, = [p for p in rule['m_Properties'] if p['m_Id'] == 131104]
scale_prop, = [p for p in rule['m_Properties'] if p['m_Id'] == 327681]
top_prop['m_Values'] = [pooled(sheet, 'dimensions', {'unit': 1, 'value': -15.0}, 3)]
scale_prop['m_Values'] = [pooled(sheet, 'floats', f32(.9), 2), pooled(sheet, 'floats', f32(.9), 2)]
assert [p for p in rule['m_Properties'] if p['m_Id'] not in [131104, 327681]] == [p for p in original['m_Rules'][rule_index]['m_Properties'] if p['m_Id'] not in [131104, 327681]]
for i, old_rule in enumerate(original['m_Rules']):
    if i != rule_index:
        assert sheet['m_Rules'][i] == old_rule
for key in original:
    if key not in ['m_Rules', 'dimensions', 'floats']:
        assert sheet[key] == original[key]
objects[STYLE].save_typetree(sheet)
OUT.mkdir(exist_ok=True)
destination = OUT / GLOBAL
destination.write_bytes(env.file.save(packer='lz4'))
check_env = UnityPy.load(str(destination))
check = {o.path_id: o for o in check_env.objects}
assert check.keys() == objects.keys()
assert check[STYLE].read_typetree() == sheet
for pid, digest in hashes.items():
    if pid != STYLE:
        assert sha(check[pid].get_raw_data()) == digest, pid
assert sha(source.read_bytes()) == source_hash
shutil.copyfile(BASE / WORLD, OUT / WORLD)
assert (OUT / WORLD).read_bytes() == (BASE / WORLD).read_bytes()

readme = '''仅调整CA000卡面 v22

基于v21（栏目高度185px）。替换本包global、gameworld两个同名bundle后重启游戏。
实际修改仅在global的CA000卡面样式：
- top:0px → -15px，向上移动15px。
- scale:115% → 90%，水平和垂直均90%。
gameworld原样随包提供，便于保持版本一致。
球员头像、BlueLight、国旗、队徽、左右信息和185px栏目高度保持原值。
源packages及旧版成品没有覆盖。
已重读验证目标参数及其他资源字节；游戏内效果待确认。
恢复本次修改可替换上一版v21中的global文件。
'''
(OUT / '安装说明.txt').write_text(readme, encoding='utf-8-sig')
(OUT / '修改记录.json').write_text(json.dumps({
    'baseline': str(BASE), 'node_name': card_name, 'node_rid': 1162, 'rule_index': rule_index,
    'style_path_id': STYLE, 'texture_path_id': CARD_TEXTURE,
    'top_before': old_top, 'top_after': decoded(rule, 131104),
    'scale_before': old_scale, 'scale_after': decoded(rule, 327681),
    'global_source_sha256': source_hash, 'global_output_sha256': sha(destination.read_bytes()),
    'untouched_global_assets_verified': len(objects) - 1, 'gameworld_unchanged': True,
}, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in OUT.iterdir():
        if path.is_file():
            z.write(path, path.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), 'card_node': card_name, 'top_px': -15,
                  'scale': .9, 'untouched_global_assets_verified': len(objects) - 1,
                  'gameworld_unchanged': True}, ensure_ascii=True))
