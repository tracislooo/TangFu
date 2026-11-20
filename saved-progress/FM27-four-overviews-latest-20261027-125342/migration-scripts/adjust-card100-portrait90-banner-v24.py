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

BASE = ROOT / '卡面110同步新图片-v23'
OUT = ROOT / '卡面100头像90-banner-v24'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BANNER, STYLE = -4194025542157271532, 8045407476604796436
PERSON, PERSON_STYLE = -910000000000101, -910000000000102

def sha(data):
    return hashlib.sha256(data).hexdigest()

def f32(value):
    return struct.unpack('<f', struct.pack('<f', value))[0]

def load(path):
    env = UnityPy.load(str(path))
    return env, {o.path_id: o for o in env.objects}

source = BASE / GLOBAL
source_hash = sha(source.read_bytes())
env, objects = load(source)
hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
doc = objects[BANNER].read_typetree()
sheet = objects[STYLE].read_typetree()
old_sheet = copy.deepcopy(sheet)
records = {r['rid']: r for r in doc['references']['RefIds']}

def decoded(sheet, rule, pid):
    props = [p for p in rule['m_Properties'] if p['m_Id'] == pid]
    if not props:
        return None
    prop, = props
    return [sheet[{2: 'floats', 3: 'dimensions', 6: 'assets', 7: 'strings'}[v['m_ValueType']]][v['valueIndex']] for v in prop['m_Values']]

person = objects[PERSON].read_typetree()
person_sheet = objects[PERSON_STYLE].read_typetree()
image_nodes = [r for r in person['references']['RefIds'] if r.get('data', {}).get('m_FullTypeName') == 'SI.Bindable.SIImage']
assert len(image_nodes) == 4
for node in image_nodes:
    person_rule = person_sheet['m_Rules'][node['data']['m_RuleIndex']]
    assert decoded(person_sheet, person_rule, 327681) == [.75, .75]

changes = []
changed_rules = []
for rid, old_scale, new_scale in [(1162, f32(1.1), 1.0), (1132, None, 1.2)]:
    node = records[rid]
    rule_index = node['data']['m_RuleIndex']
    assert sum(r.get('data', {}).get('m_RuleIndex') == rule_index for r in records.values()) == 1
    rule = sheet['m_Rules'][rule_index]
    assert decoded(sheet, rule, 327681) == (None if old_scale is None else [old_scale, old_scale])
    if rid == 1162:
        assert decoded(sheet, rule, 458753) == [{'m_FileID': 0, 'm_PathID': -910000000000003}]
        assert decoded(sheet, rule, 131104) == [{'unit': 1, 'value': -15.0}]
    value = f32(new_scale)
    if value not in sheet['floats']:
        sheet['floats'].append(value)
    handle = {'m_ValueType': 2, 'valueIndex': sheet['floats'].index(value)}
    props = [p for p in rule['m_Properties'] if p['m_Id'] == 327681]
    if props:
        prop, = props
        prop['m_Values'] = [copy.deepcopy(handle), copy.deepcopy(handle)]
    else:
        rule['m_Properties'].append({'m_Id': 327681, 'm_CustomName': '', 'm_Line': -1,
                                    'm_Values': [copy.deepcopy(handle), copy.deepcopy(handle)]})
    assert [p for p in rule['m_Properties'] if p['m_Id'] != 327681] == [p for p in old_sheet['m_Rules'][rule_index]['m_Properties'] if p['m_Id'] != 327681]
    changed_rules.append(rule_index)
    changes.append({'node_rid': rid, 'name': records[node['data']['m_SerializedData']['rid']]['data']['name'],
                    'rule_index': rule_index, 'old_scale': old_scale, 'new_scale': new_scale})
for i, rule in enumerate(old_sheet['m_Rules']):
    if i not in changed_rules:
        assert sheet['m_Rules'][i] == rule
for key in old_sheet:
    if key not in ['m_Rules', 'floats']:
        assert sheet[key] == old_sheet[key]
objects[STYLE].save_typetree(sheet)
OUT.mkdir(exist_ok=True)
destination = OUT / GLOBAL
destination.write_bytes(env.file.save(packer='lz4'))
_, check = load(destination)
assert check.keys() == objects.keys()
assert check[STYLE].read_typetree() == sheet
for pid, digest in hashes.items():
    if pid != STYLE:
        assert sha(check[pid].get_raw_data()) == digest, pid
assert abs(.75 * decoded(sheet, sheet['m_Rules'][records[1132]['data']['m_RuleIndex']], 327681)[0] - .9) < 1e-6
assert sha(source.read_bytes()) == source_hash
shutil.copyfile(BASE / WORLD, OUT / WORLD)
assert (OUT / WORLD).read_bytes() == (BASE / WORLD).read_bytes()

readme = '''卡面100%、头像最终90%，缩放设置在report-player-banner-max v24

基于v23。替换global bundle后重启游戏；gameworld未变，随包提供以便保持版本一致。
实际只修改global的report-player-banner-max内联样式8045407476604796436：
- ReportMiddleCA000Layer：scale 110% → 100%，top仍为-15px。
- PersonPictureFrame：在banner中新增scale 120%。

PersonPicture内部原先已有75%缩放，本次严格保留其模板和样式。
头像最终缩放为75% × 120% = 90%，新增缩放控制位于report-player-banner-max。
如果外层直接填90%，与原75%相乘会变成67.5%，所以这里用120%补偿。
以后仅在banner外层调整：外层scale = 期望最终比例 / 0.75。
例如最终100%需外层133.333%，最终90%需120%。

新CA000图片640×680、栏目185px、头像等比适配、BlueLight、国旗队徽与左右信息保持原值。
所有PersonPicture资源和其他非目标资源字节已校验未改变。
源packages与旧版成品没有覆盖，游戏内效果待确认。
恢复本次修改可替换v23中的global文件。
'''
(OUT / '安装说明.txt').write_text(readme, encoding='utf-8-sig')
(OUT / '修改记录.json').write_text(json.dumps({
    'baseline': str(BASE), 'changes': changes, 'style_path_id': STYLE,
    'person_picture_internal_scale_unchanged': .75, 'portrait_final_scale': .9,
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
print(json.dumps({'output': str(archive), 'card_scale': 1.0, 'banner_portrait_scale': 1.2,
                  'person_picture_unchanged': True, 'portrait_final_scale': .9,
                  'untouched_global_assets_verified': len(objects) - 1}, ensure_ascii=True))
