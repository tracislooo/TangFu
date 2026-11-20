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

NAME = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
CURRENT = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages') / NAME
PREVIOUS = ROOT / '中间头像五层叠加-v10' / NAME
OUT = ROOT / '中间三层缩放调整-v11'
BANNER_ID = -4194025542157271532
STYLE_ID = 8045407476604796436
SCALE_ID = 327681
SCALES = {'ReportMiddleCA000Layer': 1.15,
          'ReportMiddleBlueLightLayer': 1.85,
          'PersonPictureFrame': 0.75}

def load(path):
    env = UnityPy.load(str(path))
    objects = {o.path_id: o for o in env.objects}
    banner = objects[BANNER_ID].read_typetree()
    refs = {r['rid']: r for r in banner['references']['RefIds']}
    return env, objects, banner, refs

env, objects, banner, refs = load(CURRENT)
names = {r.get('data', {}).get('name') for r in refs.values()}
source = CURRENT
if not set(SCALES).issubset(names):
    source = PREVIOUS
    env, objects, banner, refs = load(source)

source_hash = hashlib.sha256(source.read_bytes()).digest()
current_hash = hashlib.sha256(CURRENT.read_bytes()).digest()
hashes = {pid: hashlib.sha256(o.get_raw_data()).digest() for pid, o in objects.items()}
style_obj = objects[STYLE_ID]
style = style_obj.read_typetree()
old_style = copy.deepcopy(style)
changed_rules = {}
for name, scale in SCALES.items():
    sd = next(r for r in refs.values() if r.get('data', {}).get('name') == name)
    node = next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == sd['rid'])
    index = node['data']['m_RuleIndex']
    # Each scale rule belongs exclusively to this intended middle element.
    assert [r['rid'] for r in refs.values() if r.get('data', {}).get('m_RuleIndex') == index] == [node['rid']]
    assert index not in changed_rules
    actual = struct.unpack('<f', struct.pack('<f', scale))[0]
    if actual not in style['floats']:
        style['floats'].append(actual)
    float_index = style['floats'].index(actual)
    properties = style['m_Rules'][index]['m_Properties']
    properties[:] = [p for p in properties if p['m_Id'] != SCALE_ID]
    properties.append({'m_Id': SCALE_ID, 'm_CustomName': '', 'm_Line': -1,
                       'm_Values': [{'m_ValueType': 2, 'valueIndex': float_index},
                                    {'m_ValueType': 2, 'valueIndex': float_index}]})
    changed_rules[index] = name

for i, old_rule in enumerate(old_style['m_Rules']):
    if i not in changed_rules:
        assert style['m_Rules'][i] == old_rule
    else:
        assert [p for p in style['m_Rules'][i]['m_Properties'] if p['m_Id'] != SCALE_ID] == [
            p for p in old_rule['m_Properties'] if p['m_Id'] != SCALE_ID]
assert style['floats'][:len(old_style['floats'])] == old_style['floats']
for key in style:
    if key not in ['m_Rules', 'floats']:
        assert style[key] == old_style[key]

style_obj.save_typetree(style)
OUT.mkdir(exist_ok=True)
destination = OUT / NAME
destination.write_bytes(env.file.save(packer='lz4'))
check = UnityPy.load(str(destination))
check_objects = {o.path_id: o for o in check.objects}
assert set(check_objects) == set(objects)
for pid, digest in hashes.items():
    if pid != STYLE_ID:
        assert hashlib.sha256(check_objects[pid].get_raw_data()).digest() == digest, pid
assert check_objects[STYLE_ID].read_typetree() == style
assert check_objects[BANNER_ID].read_typetree() == banner
assert hashlib.sha256(source.read_bytes()).digest() == source_hash
assert hashlib.sha256(CURRENT.read_bytes()).digest() == current_hash

readme = '''中间三层缩放调整 v11

CA000：115%（水平、垂直相同缩放）。
PlayerTopBlueLight：185%（水平、垂直相同缩放）。
球员头像：75%（原200×200正方形区域，缩放后150×150）。

只修改这三个中间元素的scale属性。中心位置、图层顺序、容器尺寸、图片绑定、文字、栏目高度及其他所有资源均不变。
备份皮肤packages中的ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle，使用本包同名文件替换，然后重新启动游戏。
gameworld和backgrounds bundle不需要替换。

已重新打开成品，验证三个缩放值及除inlineStyle外所有资源原始字节完全相同。
源文件未覆盖，游戏内效果需确认。
'''
(OUT / '安装说明.txt').write_text(readme, encoding='utf-8-sig')
(OUT / '修改记录.json').write_text(json.dumps({
    'source': str(source), 'source_sha256': source_hash.hex(),
    'output_sha256': hashlib.sha256(destination.read_bytes()).hexdigest(),
    'scales': SCALES, 'changed_rule_indexes': changed_rules,
    'untouched_objects': len(hashes) - 1,
}, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():
        if p.is_file():
            z.write(p, p.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'source': str(source), 'output': str(archive), 'scales': SCALES,
                  'untouched_objects': len(hashes) - 1}, ensure_ascii=True))
