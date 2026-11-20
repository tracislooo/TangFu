import copy
import hashlib
import json
import math
import struct
import sys
import uuid
import zipfile
from pathlib import Path

ROOT = Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0, str(ROOT / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

BASE = ROOT / '联赛四项等级图片数值标题-v31'
OUT = ROOT / '四项单图切换整体75-v32'
GLOBAL = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
FUNCTIONS = 'ui-visualfunctions_assets_all.bundle'
FUNCTION_SOURCE = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64') / FUNCTIONS
BACKGROUND = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/ui-backgrounds_assets_common.bundle')
BANNER, STYLE = -4194025542157271532, 8045407476604796436
FUNC_PID = -2894917070210310574
FUNC_GUID = '139a6658c54dcd543a94e04e35f46c9c'
TEXTURES = [-910000000000008-i for i in range(10)]

original_write = TypeTreeHelper.write_value
def write_value(value, node, writer, config):
    if node.m_Type == 'ReferencedObject' and TypeTreeHelper.get_ref_type_node(value, config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type != 'ReferencedObjectData':
                original_write(value[child.m_Name], child, writer, config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):
            writer.align_stream()
        return
    return original_write(value, node, writer, config)
TypeTreeHelper.write_value = write_value

def sha(data):
    return hashlib.sha256(data).hexdigest()

def load(path):
    env = UnityPy.load(str(path))
    return env, {o.path_id: o for o in env.objects}

def guid():
    return {'m_idBytes': list(uuid.uuid4().bytes_le)}

def key(v):
    return bytes(v['m_idBytes']).hex()

ZERO = {'m_idBytes': [0]*16}
source_hash = sha((BASE / GLOBAL).read_bytes())
function_source_hash = sha(FUNCTION_SOURCE.read_bytes())
env, objects = load(BASE / GLOBAL)
fenv, fobjects = load(FUNCTION_SOURCE)
_, bgobjects = load(BACKGROUND)
global_hashes = {pid: sha(o.get_raw_data()) for pid, o in objects.items()}
function_hashes = {pid: sha(o.get_raw_data()) for pid, o in fobjects.items()}
previous = json.loads((BASE / '修改记录.json').read_text(encoding='utf-8'))
groups = previous['ranges']
specs = [
    ('Expected Goal/90 mins', 'ExpectedGoalsPer90', 'SeasonStats.ExpectedGoalsPer90'),
    ('ExpectedAssists/90 mins', 'ExpectedAssistsPer90', 'SeasonStats.ExpectedAssistsPer90'),
    ('Passes Completed/90 mins', 'PassCompletedPer90', 'SeasonStats.PassCompletedPer90'),
    ('tackles won per game', 'TacklesCompletedPer90', 'SeasonStats.TacklesCompletedPer90'),
]

# Extend the existing texture setter only for a numeric statistic source.
# Its original texture source execution path remains intact.
ftree = fobjects[FUNC_PID].read_typetree()
old_ftree = copy.deepcopy(ftree)
assert ftree['m_Name'] == 'SetSIRenderTextureImage'
frefs = {r['rid']: r for r in ftree['references']['RefIds']}
templates = {}
needed = {'GeneralVisualFunction_Branch', 'GeneralVisualFunction_CompareIntInt',
          'GeneralVisualFunction_CompareFloatFloat', 'TypedValueVisualFunctionLibrary_GetInt',
          'TypedValueVisualFunctionLibrary_TryCastToFloat', 'BindingPath_Create'}
for o in fobjects.values():
    if o.type.name != 'MonoBehaviour':
        continue
    t = o.read_typetree()
    for r in t.get('references', {}).get('RefIds', []):
        c = r['type']['class']
        if c in needed and c not in templates:
            templates[c] = r
assert set(templates) == needed
bind_original = next(r for r in frefs.values() if r['type']['class'] == 'BindNode')
setter_original = next(r for r in frefs.values() if r['type']['class'] == 'SIRenderTextureImage_SetTexture2D')
entry = next(r for r in frefs.values() if r['type']['class'] == 'EntryNode')
entry_sockets = {x['m_name']: x['m_id'] for x in entry['data']['m_dataSockets']}
source_socket = bind_original['data']['m_outputAsyncExecSocket']['m_dataOutputSockets'][0]['m_id']
added_nodes = []
next_frid = 190320000000000001

def clone_node(template, name):
    global next_frid
    r = copy.deepcopy(template)
    r['rid'] = next_frid
    next_frid += 1
    mapping = {}
    def collect(v):
        if isinstance(v, dict):
            for k, item in v.items():
                if k == 'm_id' and isinstance(item, dict) and 'm_idBytes' in item:
                    mapping[key(item)] = guid()
                else:
                    collect(item)
        elif isinstance(v, list):
            for item in v:
                collect(item)
    collect(r['data'])
    def replace(v):
        if isinstance(v, dict):
            for k, item in list(v.items()):
                if isinstance(item, dict) and set(item) == {'m_idBytes'}:
                    if k == 'm_parentID':
                        v[k] = copy.deepcopy(ftree['m_id'])
                    elif k == 'm_id':
                        v[k] = copy.deepcopy(mapping[key(item)])
                    elif k in ('m_sourceID', 'm_destinationID'):
                        v[k] = copy.deepcopy(ZERO)
                else:
                    replace(item)
        elif isinstance(v, list):
            for item in v:
                replace(item)
    replace(r['data'])
    r['data']['m_name'] = name
    added_nodes.append(r)
    frefs[r['rid']] = r
    return r['data']

def source(node, socket, src):
    node[socket]['m_sourceID'] = copy.deepcopy(src)

def connect(node, socket, destination, input_socket='m_execInExecInput'):
    node[socket]['m_destinationID'] = copy.deepcopy(destination[input_socket]['m_id'])

def branch(name, condition):
    d = clone_node(templates['GeneralVisualFunction_Branch'], name)
    source(d, 'm_dataInCondition', condition)
    return d

cast = clone_node(templates['TypedValueVisualFunctionLibrary_TryCastToFloat'], 'ReportStat.TryCastNumericSource')
source(cast, 'm_dataInValue', source_socket)
numeric = branch('ReportStat.NumericOrOriginalTexture', cast['m_dataOutBoolean']['m_id'])
connect(bind_original['data'], 'm_outputAsyncExecSocket', cast)
connect(cast, 'm_execOutExecOutput', numeric)
connect(numeric, 'm_execOutFalse', setter_original['data'])

kind_path = clone_node(templates['BindingPath_Create'], 'ReportStat.MetricKindPath')
kind_path['m_dataInPath']['m_defaultSocketValue']['m_value'] = 'reportStatImageMetric'
kind_bind = clone_node(bind_original, 'ReportStat.BindMetricKind')
source(kind_bind, 'm_bindingBagDataInputSocket', entry_sockets['BindingBag'])
source(kind_bind, 'm_componentDataInputSocket', entry_sockets['RenderTextureImageElement'])
kind_id = guid()
kind_bind['m_dynamicDataInputSockets'][0].update(m_name='ReportStatMetricKind',
    m_sourceID=copy.deepcopy(kind_path['m_dataOutBindingPath']['m_id']), m_dataID=copy.deepcopy(kind_id))
kind_bind['m_outputAsyncExecSocket']['m_dataOutputSockets'][0].update(m_name='ReportStatMetricKind', m_dataID=copy.deepcopy(kind_id))
variable = copy.deepcopy(ftree['m_inputs'][2])
variable.update(m_name='ReportStatMetricKindPath', m_id=copy.deepcopy(kind_id))
ftree['m_variables'].append(variable)
connect(numeric, 'm_execOutTrue', kind_bind, 'm_inputExecSocket')
kind_int = clone_node(templates['TypedValueVisualFunctionLibrary_GetInt'], 'ReportStat.GetMetricKind')
source(kind_int, 'm_dataInValue', kind_bind['m_outputAsyncExecSocket']['m_dataOutputSockets'][0]['m_id'])

setters = []
for i, pid in enumerate(TEXTURES):
    d = clone_node(setter_original, f'ReportStat.ReplaceSingleTexture.level{i+1:03d}')
    source(d, 'm_target', entry_sockets['RenderTextureImageElement'])
    d['m_dataInTexture']['m_sourceID'] = copy.deepcopy(ZERO)
    d['m_dataInTexture']['m_defaultSocketValue']['m_value'] = {'m_FileID': 0, 'm_PathID': pid}
    setters.append(d)

metric_dispatch = []
selection_starts = []
for metric, (label, _, _) in enumerate(specs):
    cmp = clone_node(templates['GeneralVisualFunction_CompareIntInt'], f'ReportStat.IsMetric{metric}')
    cmp['m_dataInOp']['m_defaultSocketValue']['m_value'] = 2
    source(cmp, 'm_dataInA', kind_int['m_dataOutInt32']['m_id'])
    cmp['m_dataInB']['m_defaultSocketValue']['m_value'] = metric
    b = branch(f'ReportStat.Metric{metric}Dispatch', cmp['m_dataOutBoolean']['m_id'])
    connect(cmp, 'm_execOutExecOutput', b)
    metric_dispatch.append((cmp, b))
    chain = []
    for i in range(9):
        cmp_float = clone_node(templates['GeneralVisualFunction_CompareFloatFloat'], f'ReportStat.Metric{metric}.BelowLevel{i+2:03d}')
        cmp_float['m_dataInOp']['m_defaultSocketValue']['m_value'] = 0
        source(cmp_float, 'm_dataInA', cast['m_dataOutFloatValue']['m_id'])
        cmp_float['m_dataInB']['m_defaultSocketValue']['m_value'] = struct.unpack(
            '<f', struct.pack('<f', groups[label][i+1]['min']))[0]
        b_float = branch(f'ReportStat.Metric{metric}.ChooseLevel{i+1:03d}', cmp_float['m_dataOutBoolean']['m_id'])
        connect(cmp_float, 'm_execOutExecOutput', b_float)
        connect(b_float, 'm_execOutTrue', setters[i])
        chain.append((cmp_float, b_float))
    for i, (_, b_float) in enumerate(chain):
        connect(b_float, 'm_execOutFalse', chain[i+1][0] if i < 8 else setters[9])
    connect(b, 'm_execOutTrue', chain[0][0])
    selection_starts.append(chain[0][0])
connect(kind_bind, 'm_outputAsyncExecSocket', metric_dispatch[0][0])
for i, (_, b) in enumerate(metric_dispatch):
    connect(b, 'm_execOutFalse', metric_dispatch[i+1][0] if i < 3 else setters[0])
ftree['references']['RefIds'].extend(added_nodes)
ftree['m_nodes'].extend({'rid': r['rid']} for r in added_nodes)

faf = fobjects[FUNC_PID].assets_file
known = {(t.m_ClassName, t.m_NameSpace, t.m_AssemblyName) for t in faf.ref_types}
assert all((r['type']['class'], r['type']['ns'], r['type']['asm']) in known for r in added_nodes)
assert ftree['m_inputs'] == old_ftree['m_inputs']
for r in old_ftree['references']['RefIds']:
    if r['rid'] != bind_original['rid']:
        assert frefs[r['rid']] == r
    else:
        restored = copy.deepcopy(frefs[r['rid']])
        restored['data']['m_outputAsyncExecSocket'] = copy.deepcopy(r['data']['m_outputAsyncExecSocket'])
        assert restored == r

# Texture pointers are local to the function bundle, so no new Addressables IDs are required.
for pid in TEXTURES:
    assert pid not in faf.objects
    src = bgobjects[pid]
    existing = next((i for i, t in enumerate(faf.types) if t.class_id == src.serialized_type.class_id
                     and t.old_type_hash == src.serialized_type.old_type_hash), None)
    if existing is None:
        existing = len(faf.types)
        faf.types.append(copy.copy(src.serialized_type))
    texture = copy.copy(src)
    texture.assets_file, texture.type_id, texture.serialized_type = faf, existing, faf.types[existing]
    texture.set_raw_data(src.get_raw_data())
    faf.objects[pid] = texture

fbundle = next(o for o in fobjects.values() if o.type.name == 'AssetBundle')
fmetadata = fbundle.read_typetree()
matched = False
for container_key, info in fmetadata['m_Container']:
    if info['asset'] == {'m_FileID': 0, 'm_PathID': FUNC_PID}:
        assert container_key == FUNC_GUID
        preload = copy.deepcopy(fmetadata['m_PreloadTable'][info['preloadIndex']:info['preloadIndex']+info['preloadSize']])
        preload.extend({'m_FileID': 0, 'm_PathID': pid} for pid in TEXTURES)
        info.update(preloadIndex=len(fmetadata['m_PreloadTable']), preloadSize=len(preload))
        fmetadata['m_PreloadTable'].extend(preload)
        matched = True
assert matched
fobjects[FUNC_PID].save_typetree(ftree)
fbundle.save_typetree(fmetadata)

# Replace the old ten-image subtree with one native texture image per statistic.
doc, sheet = objects[BANNER].read_typetree(), objects[STYLE].read_typetree()
old_doc, old_sheet = copy.deepcopy(doc), copy.deepcopy(sheet)
refs = {r['rid']: r for r in doc['references']['RefIds']}
names = {r.get('data', {}).get('name'): r for r in refs.values() if r.get('data', {}).get('name')}
def node_for(sd):
    return next(r for r in refs.values() if r.get('data', {}).get('m_SerializedData', {}).get('rid') == sd['rid'])

removed = set()
def remove_subtree(rid):
    removed.add(rid)
    d = refs[rid]['data']
    removed.add(d['m_SerializedData']['rid'])
    for child in d.get('m_Children', []):
        remove_subtree(child['rid'])
for _, name, _ in specs:
    remove_subtree(node_for(names['ReportLeague' + name + 'ImageStack'])['rid'])
assert len(removed) == 248
doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in removed]

def value(pool, typ, v):
    if v not in sheet[pool]:
        sheet[pool].append(v)
    return {'m_ValueType': typ, 'valueIndex': sheet[pool].index(v)}
def px(v): return value('dimensions', 3, {'unit': 1, 'value': float(v)})
def pct(v): return value('dimensions', 3, {'unit': 2, 'value': float(v)})
def en(v): return value('strings', 7, v)
def fl(v): return value('floats', 2, float(v))
def prop(pid, handles):
    return {'m_Id': pid, 'm_CustomName': '', 'm_Line': -1, 'm_Values': handles}

fill_props = [prop(131102,[en('absolute')]), prop(131089,[px(0)]), prop(131104,[px(0)]),
              prop(131105,[pct(100)]), prop(131087,[pct(100)]),
              prop(262150,[px(0)]), prop(262151,[px(0)])]
fill_rule = len(sheet['m_Rules'])
sheet['m_Rules'].append({'m_ComplexSelectors': [], 'm_Properties': copy.deepcopy(fill_props), 'line': -1})
scale_rule = len(sheet['m_Rules'])
sheet['m_Rules'].append({'m_ComplexSelectors': [],
    'm_Properties': copy.deepcopy(fill_props)+[prop(327681,[fl(.75),fl(.75)])], 'line': -1})

render_node_template, render_sd_template = json.loads((ROOT/'render-image-template-v32.json').read_text(encoding='utf-8'))
remapper_node_template, remapper_sd_template = json.loads((ROOT/'native-card-remapper-v28.json').read_text(encoding='utf-8'))
new_refs = []
next_rid = max(refs)+1
next_id = 1901200000
def pair(nt, st, parent, name, rule):
    global next_rid, next_id
    node, sd = copy.deepcopy(nt), copy.deepcopy(st)
    node['rid'], sd['rid'] = next_rid, next_rid+1
    next_rid += 2
    node['data'].update(m_Id=next_id, m_Parent={'rid': parent}, m_Children=[],
        m_SerializedData={'rid': sd['rid']}, m_RuleIndex=rule, m_Classes=[],
        m_Properties=[], m_Stylesheets=[], m_StylesheetPaths=[], m_SkipClone=0)
    sd['data'].update(uxmlAssetId=next_id, name=name, name_UxmlAttributeFlags=1,
        pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    next_id += 1
    refs[node['rid']], refs[sd['rid']] = node, sd
    new_refs.extend([node, sd])
    return node, sd

def children(rid, ids):
    refs[rid]['data']['m_Children'] = [{'rid': x} for x in ids]
    for x in ids:
        refs[x]['data']['m_Parent'] = {'rid': rid}

def image_args(path):
    cls = 'SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'.encode()
    data = path.encode()
    payload = bytes([len(cls)])+cls+b'\x01'+bytes([len(data)])+data
    return list(b'\x01'+struct.pack('<i',len(payload))+payload)

changed_nodes = set()
image_ids = []
for metric, (_, name, path) in enumerate(specs):
    cell = node_for(names['ReportLeague'+name+'Cell'])
    title = node_for(names['ReportLeague'+name+'Title'])
    text = node_for(names['ReportLeague'+name+'Value'])
    group, _ = pair(refs[1140], refs[1141], cell['rid'], 'ReportLeague'+name+'Scaled75', scale_rule)
    mapper, msd = pair(remapper_node_template, remapper_sd_template, group['rid'],
                       'ReportLeague'+name+'ImageMetric', fill_rule)
    msd['data']['Mappings'] = [{'m_serialisedType':0, 'from':'reportStatImageMetric',
        'to':{'m_path':['const.Zero','const.One','const.Two','const.Three'][metric]}, 'type':{'id':0}}]
    msd['data']['Mappings_UxmlAttributeFlags'] = 1
    image, isd = pair(render_node_template, render_sd_template, mapper['rid'],
                      'ReportLeague'+name+'SingleImage', fill_rule)
    isd['data'].update(source={'m_FileID':0,'m_PathID':TEXTURES[0]}, source_UxmlAttributeFlags=1,
                       scaleMode=2, scaleMode_UxmlAttributeFlags=1,
                       m_scaleMode=2, m_scaleMode_UxmlAttributeFlags=1)
    isd['data']['BindImageFunc'] = {'m_target':{'m_guid':FUNC_GUID},
        'm_inputs':{'m_variable':{'m_argumentBytes':image_args(path)}},
        'm_outputs':{'m_variable':{'m_argumentBytes':[]}}}
    isd['data']['BindImageFunc_UxmlAttributeFlags'] = 1
    children(mapper['rid'], [image['rid']])
    children(group['rid'], [mapper['rid'], text['rid'], title['rid']])
    children(cell['rid'], [group['rid']])
    changed_nodes.update([cell['rid'], title['rid'], text['rid']])
    image_ids.append(image['rid'])
doc['references']['RefIds'].extend(new_refs)
known = {(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in objects[BANNER].assets_file.ref_types}
assert all((r['type']['class'],r['type']['ns'],r['type']['asm']) in known for r in new_refs)
for r in old_doc['references']['RefIds']:
    if r['rid'] not in removed and r['rid'] not in changed_nodes:
        assert refs[r['rid']] == r
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])] == old_sheet['m_Rules']
objects[BANNER].save_typetree(doc)
objects[STYLE].save_typetree(sheet)

OUT.mkdir(exist_ok=True)
(OUT/GLOBAL).write_bytes(env.file.save(packer='lz4'))
(OUT/FUNCTIONS).write_bytes(fenv.file.save(packer='lz4'))
_, saved = load(OUT/GLOBAL)
_, fsaved = load(OUT/FUNCTIONS)
assert saved[BANNER].read_typetree() == doc and saved[STYLE].read_typetree() == sheet
assert fsaved[FUNC_PID].read_typetree() == ftree and fsaved[fbundle.path_id].read_typetree() == fmetadata
for pid,digest in global_hashes.items():
    if pid not in (BANNER,STYLE):
        assert sha(saved[pid].get_raw_data()) == digest,pid
for pid,digest in function_hashes.items():
    if pid not in (FUNC_PID,fbundle.path_id):
        assert sha(fsaved[pid].get_raw_data()) == digest,pid
for pid in TEXTURES:
    assert fsaved[pid].get_raw_data() == bgobjects[pid].get_raw_data()

# Validate graph links from the delivered file, and execute the saved numeric selector.
frs = fsaved[FUNC_PID].read_typetree()['references']['RefIds']
exec_inputs = {}
data_outputs = {}
for r in frs:
    d = r.get('data',{})
    for k,v in d.items():
        if isinstance(v,dict) and 'm_id' in v:
            if k in ('m_execInExecInput','m_inputExecSocket'):
                assert key(v['m_id']) not in exec_inputs
                exec_inputs[key(v['m_id'])] = (r['type']['class'],d)
            elif k.startswith('m_dataOut'):
                data_outputs[key(v['m_id'])] = (r['type']['class'],k,d)
    if r['type']['class']=='BindNode':
        for s in d['m_outputAsyncExecSocket']['m_dataOutputSockets']:
            data_outputs[key(s['m_id'])] = ('BindNode',s['m_name'],d)
for r in frs:
    def verify(v):
        if isinstance(v,dict):
            if 'm_destinationID' in v and any(v['m_destinationID']['m_idBytes']):
                assert key(v['m_destinationID']) in exec_inputs
            for x in v.values():verify(x)
        elif isinstance(v,list):
            for x in v:verify(x)
    verify(r.get('data',{}))

def evaluate(metric,value):
    current = copy.deepcopy(kind_bind['m_outputAsyncExecSocket']['m_destinationID'])
    last_bool = None
    count = 0
    while True:
        count += 1
        assert count < 100
        c,d = exec_inputs[key(current)]
        if c=='GeneralVisualFunction_CompareIntInt':
            assert d['m_dataInOp']['m_defaultSocketValue']['m_value']==2
            last_bool = metric == d['m_dataInB']['m_defaultSocketValue']['m_value']
            current=d['m_execOutExecOutput']['m_destinationID']
        elif c=='GeneralVisualFunction_CompareFloatFloat':
            assert d['m_dataInOp']['m_defaultSocketValue']['m_value']==0
            # The runtime node compares System.Single values.
            a=struct.unpack('<f',struct.pack('<f',value))[0]
            b=d['m_dataInB']['m_defaultSocketValue']['m_value']
            last_bool=a < b
            current=d['m_execOutExecOutput']['m_destinationID']
        elif c=='GeneralVisualFunction_Branch':
            current=d['m_execOutTrue' if last_bool else 'm_execOutFalse']['m_destinationID']
        elif c=='SIRenderTextureImage_SetTexture2D':
            assert not any(d['m_dataInTexture']['m_sourceID']['m_idBytes'])
            return d['m_dataInTexture']['m_defaultSocketValue']['m_value']['m_PathID']
        else:
            raise AssertionError(c)

cases=0
for metric,(label,_,_) in enumerate(specs):
    for i,row in enumerate(groups[label]):
        for v in [row['min'],row['max'],(row['min']+row['max'])/2]:
            assert evaluate(metric,v)==row['pid'],(metric,v)
            cases+=1
rs={r['rid']:r for r in saved[BANNER].read_typetree()['references']['RefIds']}
seen=set()
def visit(rid):
    assert rid not in seen
    seen.add(rid)
    for ch in rs[rid].get('data',{}).get('m_Children',[]):
        assert rs[ch['rid']]['data']['m_Parent']['rid']==rid
        visit(ch['rid'])
visit(doc['m_VisualTree']['rid'])
for _,name,_ in specs:
    cell=node_for(names['ReportLeague'+name+'Cell'])
    subtree=[]
    def collect(rid):
        subtree.append(rs[rid])
        for ch in rs[rid].get('data',{}).get('m_Children',[]):collect(ch['rid'])
    collect(cell['rid'])
    assert sum(r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIRenderTextureImage' for r in subtree)==1
    assert not any(r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIVisible' for r in subtree)
assert not (seen & removed)
assert sha((BASE/GLOBAL).read_bytes())==source_hash
assert sha(FUNCTION_SOURCE.read_bytes())==function_source_hash

notes='''四项联赛统计：每项单图切换、图文整体75% v32

退出游戏，把本包两份bundle一起替换到之前的游戏资源目录，再重新启动。
必须一起替换global和ui-visualfunctions_assets_all.bundle。

每项现在只有一个SIRenderTextureImage控件。按实际数值选择level001–level010，
直接替换这个控件的Texture2D，不再叠放十个图片或依赖隐藏层。
沿用新表的四组区间，数值与标题沿用已成功显示的联赛统计绑定。
图、数值、标题整体统一缩放为v31的75%，四个等宽槽位与间距保持原位。
栏目仍185px，统计行仍80px，Actions及其余布局不变。

视觉函数SetSIRenderTextureImage增加数字输入分支，使用TryCastToFloat再比较小数。
原有Texture2D输入继续走原始贴图分支；其余函数与资源字节均已核对不变。
十张纹理在函数bundle内本地引用，不需要修改Addressables catalog。

已重读检查单图结构、缩放、函数图连接、数值分档、纹理及无关资源字节。
游戏内实际显示与刷新仍需运行游戏确认。
源packages和游戏安装文件未覆盖。恢复请使用v31的global与原visualfunctions文件。
'''
(OUT/'安装说明.txt').write_text(notes,encoding='utf-8-sig')
manifest={'baseline':str(BASE),'function_source':str(FUNCTION_SOURCE),'function_pid':FUNC_PID,
          'function_guid':FUNC_GUID,'single_image_ids':image_ids,'scale':.75,'ranges':groups,
          'removed_old_reference_records':len(removed),'new_ui_reference_records':len(new_refs),
          'new_graph_nodes':len(added_nodes),'numeric_cases_checked':cases,'game_runtime_verified':False,
          'global_source_sha256':source_hash,'function_source_sha256':function_source_hash,
          'global_sha256':sha((OUT/GLOBAL).read_bytes()),'functions_sha256':sha((OUT/FUNCTIONS).read_bytes())}
(OUT/'修改记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
archive=OUT.with_suffix('.zip')
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():z.write(p,p.name)
with zipfile.ZipFile(archive) as z:assert z.testzip() is None
print(json.dumps({'output':str(archive),'cases':cases,'single_images':len(image_ids),'graph_nodes':len(added_nodes)},ensure_ascii=True))
