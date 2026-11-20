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

BASE = ROOT / '能力区间自动切换卡面-v28'
OUT = ROOT / '能力卡面切换修正-v29'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
BANNER = -4194025542157271532
STYLE = 8045407476604796436
PATH = 'person.PlayerCurrentAbility'

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

def digest(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    env = UnityPy.load(str(path))
    return env, {o.path_id: o for o in env.objects}

def decode_string(raw, offset=0):
    size = shift = 0
    while True:
        b = raw[offset]
        offset += 1
        size |= (b & 127) << shift
        if not b & 128:
            break
        shift += 7
    return raw[offset:offset+size].decode('utf-8'), offset+size

def string_bytes(s):
    raw = s.encode('utf-8')
    assert len(raw) < 128
    return bytes([len(raw)]) + raw

def decode_args(raw):
    result = []
    offset = 1
    for _ in range(raw[0]):
        size, = struct.unpack_from('<i', raw, offset)
        offset += 4
        payload = raw[offset:offset+size]
        offset += size
        cls, pos = decode_string(payload)
        result.append((cls, payload[pos:]))
    assert offset == len(raw)
    return result

def encode_args(args):
    raw = bytearray([len(args)])
    for cls, value in args:
        payload = string_bytes(cls) + value
        raw.extend(struct.pack('<i', len(payload)))
        raw.extend(payload)
    return list(raw)

source = BASE / GLOBAL
source_hash = digest(source.read_bytes())
env, objects = load(source)
before_hashes = {pid: digest(o.get_raw_data()) for pid, o in objects.items()}
doc = objects[BANNER].read_typetree()
before_doc = copy.deepcopy(doc)
refs = {r['rid']: r for r in doc['references']['RefIds']}
by_name = {r.get('data', {}).get('name'): r for r in refs.values() if r.get('data', {}).get('name')}
remapper_sd = by_name['ReportCACardPlayerRemapper']
remapper = next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == remapper_sd['rid'])
card = refs[1162]
assert card['data']['m_Children'] == [{'rid': remapper['rid']}]
root_switch = remapper['data']['m_Children'][0]['rid']
card['data']['m_Children'] = [{'rid': root_switch}]
refs[root_switch]['data']['m_Parent'] = {'rid': card['rid']}
removed = {remapper['rid'], remapper_sd['rid']}
doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in removed]

native = json.loads((ROOT / 'native-int-switch-template-v28.json').read_text(encoding='utf-8'))
native_sd = next(r['data'] for r in native['references']['RefIds'] if r['type']['class'] == 'BindableSwitchElement/UxmlSerializedData')
changes = []
for threshold in (119, 139, 159, 179):
    sd = by_name[f'ReportCAAbove{threshold}Switch']
    data = sd['data']
    # Preserve native conditional-initialisation defaults, including visibility handling.
    for key in ('AlwaysInstantiate', 'AlwaysInstantiate_UxmlAttributeFlags',
                'VisibilityType', 'VisibilityType_UxmlAttributeFlags',
                'FadeOptions', 'FadeOptions_UxmlAttributeFlags'):
        data[key] = copy.deepcopy(native_sd[key])
    raw = bytes(data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    args = decode_args(raw)
    assert struct.unpack('<i', args[0][1])[0] == 4
    assert struct.unpack('<i', args[1][1])[0] == threshold
    assert decode_string(args[2][1], 1)[0] == 'Player.PlayerCurrentAbility'
    args[2] = (args[2][0], b'\x01' + string_bytes(PATH))
    data['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = encode_args(args)
    changes.append(sd['rid'])

# Explicitly verify the banner already receives the current person; no new alias needed.
expect = next(r['data'] for r in refs.values() if r['type']['class'] == 'BindingExpect/UxmlSerializedData')
assert any(p['name'] == 'person' and p['type']['id'] == 1145176065 for p in expect['Parameters'])
allowed = {card['rid'], root_switch, *changes, *removed}
for r in before_doc['references']['RefIds']:
    if r['rid'] not in allowed:
        assert refs[r['rid']] == r

objects[BANNER].save_typetree(doc)
OUT.mkdir(exist_ok=True)
dest = OUT / GLOBAL
dest.write_bytes(env.file.save(packer='lz4'))
_, saved = load(dest)
assert set(saved) == set(objects)
assert saved[BANNER].read_typetree() == doc
for pid, value in before_hashes.items():
    if pid != BANNER:
        assert digest(saved[pid].get_raw_data()) == value, pid

# Check connectivity and deserialize the conditions from the delivered bundle.
tree = saved[BANNER].read_typetree()
rs = {r['rid']: r for r in tree['references']['RefIds']}
seen = set()
def visit(rid):
    assert rid not in seen, ('cycle or duplicate', rid)
    seen.add(rid)
    node = rs[rid]['data']
    for child in node.get('m_Children', []):
        crid = child['rid']
        assert rs[crid]['data']['m_Parent']['rid'] == rid
        visit(crid)
visit(tree['m_VisualTree']['rid'])
assert not (removed & seen)
sheet = saved[STYLE].read_typetree()
def select(ca):
    rid = root_switch
    while rs[rid]['data']['m_FullTypeName'] == 'SI.Bindable.BindableSwitchElement':
        node = rs[rid]['data']
        sd = rs[node['m_SerializedData']['rid']]['data']
        assert sd['AlwaysInstantiate'] == 0
        args = decode_args(bytes(sd['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']))
        assert decode_string(args[2][1], 1)[0] == PATH
        threshold, = struct.unpack('<i', args[1][1])
        rid = node['m_Children'][int(ca > threshold)]['rid']
    rule = sheet['m_Rules'][rs[rid]['data']['m_RuleIndex']]
    p, = [p for p in rule['m_Properties'] if p['m_Id'] == 458753]
    return sheet['assets'][p['m_Values'][0]['valueIndex']]['m_PathID']
for ca in range(201):
    tier = sum(ca >= threshold for threshold in (120, 140, 160, 180))
    assert select(ca) == -910000000000003 - tier
assert digest(source.read_bytes()) == source_hash

notes = '''能力卡面切换修正 v29

退出游戏，将本包 ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle
替换到原来的游戏安装位置，再重新启动游戏。
此包只含需要替换的 global 文件；gameworld、backgrounds 不需替换。

本次修正：
1. 移除 v28 强制同时实例化各卡面的设置，恢复原生切换控件的条件实例化默认值。
2. 移除新增的 Player 别名映射，直接监听 banner 已有当前球员 person.PlayerCurrentAbility。
3. 仍按 >119、>139、>159、>179 四个条件选择唯一的卡面。

区间与图片：0–119 CA000；120–139 CA120；140–159 CA140；160–179 CA160；180–200 CA180。
卡面98%、总上移10px、头像70%、栏目185px，以及其他层级布局保持原值。

验证：已重新读取输出，检查节点连接、绑定参数、201个能力值对应的分支；
除 report-player-banner-max 文档之外，bundle 内所有资源的原始字节完全不变。
这些是文件与分支结构检查，不能证明游戏运行时已取得实际能力值。
请在游戏内切换不同能力档的球员确认；若全部变成同一档，需要继续核对运行时能力值绑定。

v28 的全实例化设置是已发现的异常，但尚未在运行中的游戏确认它是否是唯一原因。
旧版文件与源 packages 未覆盖。需要恢复时使用原来的 v28 或 v27 文件。
'''
(OUT / '安装说明.txt').write_text(notes, encoding='utf-8-sig')
manifest = {'baseline': str(BASE), 'binding_path': PATH,
            'removed_alias_rids': sorted(removed), 'always_instantiate': False,
            'thresholds': [119, 139, 159, 179], 'structural_values_checked': 201,
            'game_runtime_verified': False, 'only_changed_asset': BANNER,
            'untouched_assets_byte_verified': len(objects)-1,
            'source_sha256': source_hash, 'output_sha256': digest(dest.read_bytes())}
(OUT / '修改记录.json').write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
archive = OUT.with_suffix('.zip')
with zipfile.ZipFile(archive, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in OUT.iterdir():
        z.write(path, path.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output': str(archive), **manifest}, ensure_ascii=False))
