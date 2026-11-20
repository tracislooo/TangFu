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

BASE = ROOT / '卡面98总上移10头像70-v27'
OUT = ROOT / '能力区间自动切换卡面-v28'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
WORLD = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
BACKGROUND = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/ui-backgrounds_assets_common.bundle')
BANNER, STYLE = -4194025542157271532, 8045407476604796436
CARD_IDS = [-910000000000003 - i for i in range(5)]
CARD_NAMES = ['CA000', 'CA120', 'CA140', 'CA160', 'CA180']
FUNCTION_GUID = 'f6f314e9db56227459137669d87c44e9'
ABILITY_PATH = 'Player.PlayerCurrentAbility'

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

def pool(sheet, key, value, typ):
    if value not in sheet[key]:
        sheet[key].append(value)
    return {'m_ValueType': typ, 'valueIndex': sheet[key].index(value)}

def px(v):
    return pool(sheet, 'dimensions', {'unit': 1, 'value': float(v)}, 3)

def pct(v):
    return pool(sheet, 'dimensions', {'unit': 2, 'value': float(v)}, 3)

def enum(v):
    return pool(sheet, 'strings', v, 7)

def prop(pid, v):
    return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1, 'm_Values': [v]}

def add_rule(properties):
    ix = len(sheet['m_Rules'])
    sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': properties, 'line': -1})
    return ix

def string_bytes(value):
    b = value.encode('utf-8')
    n = len(b)
    prefix = bytearray()
    while n >= 128:
        prefix.append((n & 127) | 128)
        n >>= 7
    prefix.append(n)
    return bytes(prefix) + b

def function_args(threshold):
    # Same BinaryWriter framing and visual argument classes as the native example.
    args = [
        ('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]', struct.pack('<i', 4)),
        ('SI.VisualScripting.Int32VisualArg', struct.pack('<i', threshold)),
        ('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]', b'\x01' + string_bytes(ABILITY_PATH)),
    ]
    result = bytearray([len(args)])
    for cls, value in args:
        payload = string_bytes(cls) + value
        result.extend(struct.pack('<i', len(payload)))
        result.extend(payload)
    return list(result)

source = BASE / GLOBAL
source_hash = sha(source.read_bytes())
bg_hash = sha(BACKGROUND.read_bytes())
env, objects = load(source)
bg_env, bg_objects = load(BACKGROUND)
hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
doc, sheet = objects[BANNER].read_typetree(), objects[STYLE].read_typetree()
old_doc, old_sheet = copy.deepcopy(doc), copy.deepcopy(sheet)
refs = {r['rid']: r for r in doc['references']['RefIds']}
card = refs[1162]
card_sd = refs[card['data']['m_SerializedData']['rid']]
assert card_sd['data']['name'] == 'ReportMiddleCA000Layer'
assert card['data']['m_Children'] == []
card_rule_index = card['data']['m_RuleIndex']
card_rule = sheet['m_Rules'][card_rule_index]
assert sum(r.get('data', {}).get('m_RuleIndex') == card_rule_index for r in refs.values()) == 1

def decoded(rule, pid):
    p, = [p for p in rule['m_Properties'] if p['m_Id'] == pid]
    return [sheet[{2:'floats',3:'dimensions',6:'assets',7:'strings'}[v['m_ValueType']]][v['valueIndex']] for v in p['m_Values']]

assert decoded(card_rule, 458753) == [{'m_FileID': 0, 'm_PathID': CARD_IDS[0]}]
assert decoded(card_rule, 131104) == [{'unit': 1, 'value': -10.0}]
assert abs(decoded(card_rule, 327681)[0] - .98) < 1e-6
# Preserve all existing card geometry, replacing only its static image by the conditional children.
card_rule['m_Properties'] = [p for p in card_rule['m_Properties'] if p['m_Id'] != 458753]

native = json.loads((ROOT / 'native-int-switch-template-v28.json').read_text(encoding='utf-8'))
native_info = json.loads((ROOT / 'native-int-switch-info-v28.json').read_text(encoding='utf-8'))
native_refs = {r['rid']: r for r in native['references']['RefIds']}
switch_sd_template = native_refs[native_info['serialized_rid']]
switch_node_template = next(r for r in native_refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == switch_sd_template['rid'])
assert switch_sd_template['data']['Binding']['m_visualFunction']['m_target']['m_guid'] == FUNCTION_GUID
remapper_node_template, remapper_sd_template = json.loads((ROOT / 'native-card-remapper-v28.json').read_text(encoding='utf-8'))

# The native graph routes false to child 0 and true to child 1.
# Known operator 4 is GreaterThan; use >119, >139, >159 and >179.
functions = json.loads((ROOT / 'native-visual-functions-v28.json').read_text(encoding='utf-8'))
graph = next(r['tree'] for r in functions if r['tree']['m_Name'] == 'BindIntComparisonToSwitch')
graph_refs = graph['references']['RefIds']
branch = next(r['data'] for r in graph_refs if r['type']['class'] == 'GeneralVisualFunction_Branch')
for edge, index in [('m_execOutFalse', 0), ('m_execOutTrue', 1)]:
    dest = branch[edge]['m_destinationID']
    node = next(r['data'] for r in graph_refs if r['type']['class'] == 'BindableSwitchElement_SetVisibleIndex' and r['data']['m_execInExecInput']['m_id'] == dest)
    assert node['m_dataInIndex']['m_defaultSocketValue']['m_value'] == index
greater_graph = next(r['tree'] for r in functions if r['tree']['m_Name'] == 'BindListHasGreaterThanBindingCountToSwitch')
assert next(r['data'] for r in greater_graph['references']['RefIds'] if r['type']['class'] == 'GeneralVisualFunction_CompareIntInt')['m_dataInOp']['m_defaultSocketValue']['m_value'] == 4

fill_rule = add_rule([
    prop(131102, enum('absolute')), prop(131089, px(0)), prop(131104, px(0)),
    prop(131105, pct(100)), prop(131087, pct(100)),
    prop(262150, px(0)), prop(262151, px(0)),
])
new_refs = []
next_rid = max(refs) + 1
next_element_id = 1900800000
assert all(r.get('data', {}).get('m_Id', 0) < next_element_id or r.get('data', {}).get('m_Id', 0) > next_element_id + 100 for r in refs.values())

def new_node(node_template, sd_template, parent, name, rule_index):
    global next_rid, next_element_id
    node, sd = copy.deepcopy(node_template), copy.deepcopy(sd_template)
    node['rid'], sd['rid'] = next_rid, next_rid + 1
    next_rid += 2
    eid = next_element_id
    next_element_id += 1
    node['data'].update(m_Id=eid, m_Parent={'rid': parent}, m_Children=[],
                        m_SerializedData={'rid': sd['rid']}, m_RuleIndex=rule_index,
                        m_Classes=[], m_Properties=[], m_StylesheetPaths=[], m_Stylesheets=[], m_SkipClone=0)
    sd['data'].update(uxmlAssetId=eid, name=name, name_UxmlAttributeFlags=1,
                      pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    new_refs.extend([node, sd])
    refs[node['rid']], refs[sd['rid']] = node, sd
    return node, sd

remapper, remapper_sd = new_node(remapper_node_template, remapper_sd_template, card['rid'], 'ReportCACardPlayerRemapper', fill_rule)
remapper_sd['data']['Mappings'] = [{'m_serialisedType':0, 'from':'Player', 'to':{'m_path':'person'}, 'type':{'id':1145176065}}]
remapper_sd['data']['Mappings_UxmlAttributeFlags'] = 1
card['data']['m_Children'] = [{'rid': remapper['rid']}]

switches = []
for i, threshold in enumerate([119, 139, 159, 179]):
    parent = remapper['rid'] if i == 0 else switches[-1][0]['rid']
    node, sd = new_node(switch_node_template, switch_sd_template, parent, f'ReportCAAbove{threshold}Switch', fill_rule)
    sd['data'].update(AlwaysInstantiate=1, AlwaysInstantiate_UxmlAttributeFlags=1,
                      Preview={'Mask':1}, Preview_UxmlAttributeFlags=1)
    sd['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = function_args(threshold)
    sd['data']['Binding_UxmlAttributeFlags'] = 1
    switches.append((node, sd))
remapper['data']['m_Children'] = [{'rid': switches[0][0]['rid']}]

images = []
for i, (pid, name) in enumerate(zip(CARD_IDS, CARD_NAMES)):
    parent = switches[min(i,3)][0]['rid']
    image_rule = add_rule(copy.deepcopy(sheet['m_Rules'][fill_rule]['m_Properties']) + [
        prop(458753, pool(sheet, 'assets', {'m_FileID':0, 'm_PathID':pid}, 6)),
        prop(262153, enum('scale-to-fit')),
    ])
    node, sd = new_node(card, card_sd, parent, 'ReportCACardImage' + name, image_rule)
    images.append(node)
for i, (node, sd) in enumerate(switches):
    node['data']['m_Children'] = [{'rid': images[i]['rid']},
                                 {'rid': switches[i+1][0]['rid'] if i < 3 else images[4]['rid']}]
doc['references']['RefIds'].extend(new_refs)

# Reuse the managed-reference schemas already present in this serialized file.
asset_file = objects[BANNER].assets_file
known_types = {(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in asset_file.ref_types}
assert all((r['type']['class'],r['type']['ns'],r['type']['asm']) in known_types for r in new_refs)

texture_records = []
added_textures = []
refreshed_textures = []
for pid, name in zip(CARD_IDS, CARD_NAMES):
    src = bg_objects[pid]
    tree = src.read_typetree()
    assert tree['m_Name'] == name and tree['m_StreamData']['size'] == 0
    assert src.type.name == 'Texture2D'
    raw = src.get_raw_data()
    if pid in asset_file.objects:
        assert asset_file.objects[pid].serialized_type.old_type_hash == src.serialized_type.old_type_hash
        if sha(asset_file.objects[pid].get_raw_data()) != sha(raw):
            asset_file.objects[pid].set_raw_data(raw)
            refreshed_textures.append(pid)
    else:
        ix = next(i for i,t in enumerate(asset_file.types) if t.class_id == src.serialized_type.class_id and t.old_type_hash == src.serialized_type.old_type_hash)
        texture = copy.copy(src)
        texture.assets_file = asset_file
        texture.type_id = ix
        texture.serialized_type = asset_file.types[ix]
        texture.set_raw_data(raw)
        asset_file.objects[pid] = texture
        added_textures.append(pid)
    texture_records.append({'name':name,'path_id':pid,'width':tree['m_Width'],'height':tree['m_Height'],'format':tree['m_TextureFormat'],'raw_sha256':sha(raw)})

bundle_obj = next(o for o in env.objects if o.type.name == 'AssetBundle')
metadata = bundle_obj.read_typetree()
old_metadata = copy.deepcopy(metadata)
for key, info in metadata['m_Container']:
    pointers = copy.deepcopy(old_metadata['m_PreloadTable'][info['preloadIndex']:info['preloadIndex']+info['preloadSize']])
    if any(p['m_FileID']==0 and p['m_PathID'] in [BANNER,STYLE] for p in pointers):
        for pid in CARD_IDS:
            p = {'m_FileID':0,'m_PathID':pid}
            if p not in pointers:
                pointers.append(p)
        info['preloadIndex'] = len(metadata['m_PreloadTable'])
        info['preloadSize'] = len(pointers)
        metadata['m_PreloadTable'].extend(pointers)
for pid, name in zip(CARD_IDS,CARD_NAMES):
    if not any(info['asset']=={'m_FileID':0,'m_PathID':pid} for key,info in metadata['m_Container']):
        start = len(metadata['m_PreloadTable'])
        metadata['m_PreloadTable'].append({'m_FileID':0,'m_PathID':pid})
        metadata['m_Container'].append((name.lower(),{'preloadIndex':start,'preloadSize':1,'asset':{'m_FileID':0,'m_PathID':pid}}))
metadata['m_Container'].sort(key=lambda row:row[0])

# No pre-existing visual record except the card's children has changed.
for r in old_doc['references']['RefIds']:
    candidate = copy.deepcopy(refs[r['rid']])
    if r['rid'] == 1162:
        candidate['data']['m_Children'] = []
    assert candidate == r, r['rid']
for i, old_rule in enumerate(old_sheet['m_Rules']):
    if i == card_rule_index:
        assert sheet['m_Rules'][i]['m_Properties'] == [p for p in old_rule['m_Properties'] if p['m_Id'] != 458753]
    else:
        assert sheet['m_Rules'][i] == old_rule

objects[BANNER].save_typetree(doc)
objects[STYLE].save_typetree(sheet)
bundle_obj.save_typetree(metadata)
OUT.mkdir(exist_ok=True)
destination = OUT / GLOBAL
destination.write_bytes(env.file.save(packer='lz4'))
_, check = load(destination)
assert set(check) == set(objects) | set(added_textures)
changed = {BANNER,STYLE,bundle_obj.path_id} | set(refreshed_textures)
for pid,digest in hashes.items():
    if pid not in changed:
        assert sha(check[pid].get_raw_data()) == digest,pid
for pid,tree in [(BANNER,doc),(STYLE,sheet),(bundle_obj.path_id,metadata)]:
    assert check[pid].read_typetree() == tree,pid
for pid in CARD_IDS:
    assert check[pid].get_raw_data() == bg_objects[pid].get_raw_data()
    assert check[pid].read().image.tobytes() == bg_objects[pid].read().image.tobytes()
assert sha(source.read_bytes()) == source_hash
assert sha(BACKGROUND.read_bytes()) == bg_hash
shutil.copyfile(BASE / WORLD,OUT / WORLD)
assert (OUT / WORLD).read_bytes() == (BASE / WORLD).read_bytes()

# Evaluate the serialized thresholds and actual child order for every supported CA.
saved_refs = {r['rid']:r for r in check[BANNER].read_typetree()['references']['RefIds']}
image_ids = {}
saved_sheet = check[STYLE].read_typetree()
for node in images:
    image_rule = saved_sheet['m_Rules'][saved_refs[node['rid']]['data']['m_RuleIndex']]
    background_prop, = [p for p in image_rule['m_Properties'] if p['m_Id']==458753]
    handle, = background_prop['m_Values']
    image_ids[node['rid']] = saved_sheet['assets'][handle['valueIndex']]['m_PathID']

def read_string(b, off):
    length=0
    shift=0
    while True:
        n=b[off]
        off+=1
        length|=(n&127)<<shift
        shift+=7
        if not n&128:
            break
    return b[off:off+length].decode('utf-8'),off+length

thresholds = {}
for node,sd in switches:
    saved_sd = saved_refs[saved_refs[node['rid']]['data']['m_SerializedData']['rid']]['data']
    binding = saved_sd['Binding']
    assert binding['m_kind']==2 and binding['m_visualFunction']['m_target']['m_guid']==FUNCTION_GUID
    raw=bytes(binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    assert raw[0]==3
    off=1
    payloads=[]
    for i in range(3):
        size=struct.unpack_from('<i',raw,off)[0]
        off+=4
        payload=raw[off:off+size]
        off+=size
        cls,p=read_string(payload,0)
        payloads.append((cls,payload[p:]))
    assert off==len(raw)
    assert struct.unpack('<i',payloads[0][1])[0]==4
    threshold=struct.unpack('<i',payloads[1][1])[0]
    assert payloads[2][1][0]==1
    path,end=read_string(payloads[2][1],1)
    assert path==ABILITY_PATH and end==len(payloads[2][1])
    thresholds[node['rid']]=threshold
assert list(thresholds.values())==[119,139,159,179]
def selected_card(ca):
    rid = switches[0][0]['rid']
    while rid not in image_ids:
        threshold = thresholds[rid]
        index = 1 if ca > threshold else 0
        rid = saved_refs[rid]['data']['m_Children'][index]['rid']
    return image_ids[rid]
for ca in range(201):
    expected = CARD_IDS[0 if ca < 120 else 1 if ca < 140 else 2 if ca < 160 else 3 if ca < 180 else 4]
    assert selected_card(ca) == expected,ca

readme = '''根据Player.PlayerCurrentAbility自动切换卡面 v28

替换本包global bundle后重启游戏。gameworld与v27相同，随包提供以便保持版本一致。
本次只修改中间卡面：
0–119：CA000，-910000000000003
120–139：CA120，-910000000000004
140–159：CA140，-910000000000005
160–179：CA160，-910000000000006
180–200：CA180，-910000000000007

使用游戏原生BindingRemapper和BindableSwitchElement，原生函数BindIntComparisonToSwitch。
将当前person映射为卡面局部的Player，然后监听Player.PlayerCurrentAbility。
按>119、>139、>159、>179依次选择；只显示对应的一张卡面。
五张图片同步自packages/ui-backgrounds_assets_common.bundle，内嵌global，引用ID不变。
将来替换backgrounds里的图片，仍需同步global内嵌副本。

卡面98%缩放、总共上移10px；头像最终70%、栏目185px、其他层级与布局保持原值。
已重读验证层级、引用、五张纹理、预加载和0–200全部区间边界。
PersonPicture资源及无关资源字节已核对保持不变；游戏内绑定效果待确认。
源packages及旧版成品未覆盖。恢复可替换v27的global文件。
'''
(OUT/'安装说明.txt').write_text(readme,encoding='utf-8-sig')
(OUT/'修改记录.json').write_text(json.dumps({'baseline':str(BASE),'binding_path':ABILITY_PATH,'player_alias_source':'person',
    'native_switch_function_guid':FUNCTION_GUID,'textures':texture_records,'thresholds':[119,139,159,179],
    'card_scale':.98,'card_top_px':-10,'portrait_final_scale':.70,'header_height_px':185,
    'global_source_sha256':source_hash,'background_source_sha256':bg_hash,
    'global_output_sha256':sha(destination.read_bytes()),'added_texture_ids':added_textures,
    'refreshed_texture_ids':refreshed_textures,'untouched_global_assets_verified':len(hashes)-len(changed),
    'gameworld_unchanged':True,'ability_values_structurally_checked':201},ensure_ascii=False,indent=2),encoding='utf-8')
archive=OUT.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for path in OUT.iterdir():
        if path.is_file():z.write(path,path.name)
with zipfile.ZipFile(archive) as z:
    assert z.testzip() is None
print(json.dumps({'output':str(archive),'binding':ABILITY_PATH,'ranges_verified':201,
                  'added_textures':added_textures,'refreshed_textures':refreshed_textures,
                  'new_visual_records':len(new_refs),'untouched_global_assets_verified':len(hashes)-len(changed)},ensure_ascii=True))
