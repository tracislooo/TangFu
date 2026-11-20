import copy,hashlib,importlib.util,json,struct,sys,uuid,zipfile
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');catmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(catmod)
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
GLOBAL='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';FUNCTIONS='ui-visualfunctions_assets_all.bundle'
OUT=R/'速度爆发灵活求和修正-V37'
BANNER=-4194025542157271532;FPID=-910000000000302;FGUID='d25e07441190434f86b42ec2ec560037'
PATHS=['person.AttributePace.PropertyValue','person.AttributeAcceleration.PropertyValue','person.AttributeAgility.PropertyValue']
sha=lambda b:hashlib.sha256(b).hexdigest()
before_global=(AA/'StandaloneWindows64'/GLOBAL).read_bytes();before_catalog=(AA/'catalog.bin').read_bytes();before_functions=(AA/'StandaloneWindows64'/FUNCTIONS).read_bytes()
assert sha(before_global)=='b7d00babf119fefd7da78d1c56714cf3d9b6a0044b250633b072a408a8c2300f'
assert sha(before_catalog)=='f06e97609bdfb3063ce0d81581d8b2013ce9818c35ec63f5995994200d348650'
oldwrite=TypeTreeHelper.write_value
def write(v,n,w,c):
    if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
        for ch in n.m_Children:
            if ch.m_Type!='ReferencedObjectData':oldwrite(v[ch.m_Name],ch,w,c)
        if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
        return
    return oldwrite(v,n,w,c)
TypeTreeHelper.write_value=write
env=UnityPy.load(str(AA/'StandaloneWindows64'/GLOBAL));objects={o.path_id:o for o in env.objects};af=objects[BANNER].assets_file
fobjects={o.path_id:o for o in UnityPy.load(str(AA/'StandaloneWindows64'/FUNCTIONS)).objects}
native=next(o for o in fobjects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='BindIntAddOrSubstractToSIText')
faf=native.assets_file
templates=json.loads((R/'movement-sum-node-templates-v37.json').read_text(encoding='utf-8'))
tree=copy.deepcopy(native.read_typetree());tree.update(m_Name='ReportMovementSumAsText',m_name='ReportMovementSumAsText',
    m_description='Read pace, acceleration and agility, cast each to integer and add; show -- if any cast fails.',m_outputs=[],m_variables=[],m_nodes=[])
def guid():return {'m_idBytes':list(uuid.uuid4().bytes_le)}
root=guid();tree['m_id']=root
inputs=[]
for i,name in enumerate(['BindingBag','SITextElement','PacePath','AccelerationPath','AgilityPath']):
    p=copy.deepcopy(tree['m_inputs'][i if i<2 else 2]);p.update(m_name=name,m_id=guid(),m_parentID=copy.deepcopy(root));inputs.append(p)
tree['m_inputs']=inputs
refs=[]
def clone(cls,name):
    n=copy.deepcopy(templates[cls]);n['rid']=190370000000000000+len(refs);d=n['data']
    d.update(m_name=name,m_id=guid(),m_parentID=copy.deepcopy(root))
    def reset(v):
        if isinstance(v,dict):
            for k,x in list(v.items()):
                if k=='m_id' and isinstance(x,dict) and 'm_idBytes' in x:v[k]=guid()
                elif k in ['m_sourceID','m_destinationID']:v[k]={'m_idBytes':[0]*16}
                else:reset(x)
        elif isinstance(v,list):
            for x in v:reset(x)
    for k,v in d.items():
        if k not in ['m_id','m_parentID']:reset(v)
    refs.append(n);return d
entry=clone('EntryNode','Entry')
entry['m_dataSockets']=[{'m_id':guid(),'m_name':p['m_name'],'m_dataID':copy.deepcopy(p['m_id'])} for p in inputs]
ports={p['m_name']:p['m_id'] for p in entry['m_dataSockets']}
bind=clone('BindNode','Bind Three Attribute Values')
bind['m_bindingBagDataInputSocket']['m_sourceID']=copy.deepcopy(ports['BindingBag'])
bind['m_componentDataInputSocket']['m_sourceID']=copy.deepcopy(ports['SITextElement'])
din=copy.deepcopy(bind['m_dynamicDataInputSockets'][0]);dout=copy.deepcopy(bind['m_outputAsyncExecSocket']['m_dataOutputSockets'][0])
bind['m_dynamicDataInputSockets']=[];bind['m_outputAsyncExecSocket']['m_dataOutputSockets']=[]
for p in inputs[2:]:
    di,do=copy.deepcopy(din),copy.deepcopy(dout)
    di.update(m_id=guid(),m_name=p['m_name'],m_sourceID=copy.deepcopy(ports[p['m_name']]),m_dataID=copy.deepcopy(p['m_id']))
    do.update(m_id=guid(),m_name=p['m_name'],m_dataID=copy.deepcopy(p['m_id']),m_type={'m_typeString':'SI.Core.TypedValue, SI.Core, Version=0.0.0.0, Culture=neutral, PublicKeyToken=null'})
    bind['m_dynamicDataInputSockets'].append(di);bind['m_outputAsyncExecSocket']['m_dataOutputSockets'].append(do)
casts=[clone('TypedValueVisualFunctionLibrary_TryCastToInt','Cast '+n+' To Int') for n in ['Pace','Acceleration','Agility']]
for cast,out in zip(casts,bind['m_outputAsyncExecSocket']['m_dataOutputSockets']):cast['m_dataInValue']['m_sourceID']=copy.deepcopy(out['m_id'])
ands=[clone('GeneralVisualFunction_AND','All Attribute Casts Valid 1'),clone('GeneralVisualFunction_AND','All Attribute Casts Valid 2')]
ands[0]['m_dataInA']['m_sourceID']=copy.deepcopy(casts[0]['m_dataOutBoolean']['m_id'])
ands[0]['m_dataInB']['m_sourceID']=copy.deepcopy(casts[1]['m_dataOutBoolean']['m_id'])
ands[1]['m_dataInA']['m_sourceID']=copy.deepcopy(ands[0]['m_dataOutBoolean']['m_id'])
ands[1]['m_dataInB']['m_sourceID']=copy.deepcopy(casts[2]['m_dataOutBoolean']['m_id'])
adds=[clone('GeneralVisualFunction_Add_int_int_int','Pace Plus Acceleration'),clone('GeneralVisualFunction_Add_int_int_int','Plus Agility')]
adds[0]['m_dataInA']['m_sourceID']=copy.deepcopy(casts[0]['m_dataOutIntValue']['m_id'])
adds[0]['m_dataInB']['m_sourceID']=copy.deepcopy(casts[1]['m_dataOutIntValue']['m_id'])
adds[1]['m_dataInA']['m_sourceID']=copy.deepcopy(adds[0]['m_dataOutInt32']['m_id'])
adds[1]['m_dataInB']['m_sourceID']=copy.deepcopy(casts[2]['m_dataOutIntValue']['m_id'])
fmt=clone('NumericVisualFunctionLibrary_IntToString_string_int','Sum To String');fmt['m_dataInV']['m_sourceID']=copy.deepcopy(adds[1]['m_dataOutInt32']['m_id'])
branch=clone('GeneralVisualFunction_Branch','Display Sum Or Missing');branch['m_dataInCondition']['m_sourceID']=copy.deepcopy(ands[1]['m_dataOutBoolean']['m_id'])
success=clone('ITextElement_SetText','Display Sum');failed=clone('ITextElement_SetText','Display Missing')
for d in [success,failed]:d['m_target']['m_sourceID']=copy.deepcopy(ports['SITextElement'])
success['m_dataInText']['m_sourceID']=copy.deepcopy(fmt['m_dataOutString']['m_id']);failed['m_dataInText']['m_defaultSocketValue']={'m_value':'--'}
def connect(d,k,to,port):d[k]['m_destinationID']=copy.deepcopy(to[port]['m_id'])
connect(entry,'m_outputExecSocket',bind,'m_inputExecSocket');connect(bind,'m_outputAsyncExecSocket',casts[0],'m_execInExecInput')
for a,b in zip(casts,casts[1:]):connect(a,'m_execOutExecOutput',b,'m_execInExecInput')
connect(casts[-1],'m_execOutExecOutput',ands[0],'m_execInExecInput');connect(ands[0],'m_execOutExecOutput',ands[1],'m_execInExecInput')
connect(ands[1],'m_execOutExecOutput',branch,'m_execInExecInput');connect(branch,'m_execOutTrue',success,'m_execInExecInput');connect(branch,'m_execOutFalse',failed,'m_execInExecInput')
tree['m_nodes']=[{'rid':r['rid']} for r in refs];tree['references']={'version':2,'RefIds':refs}
assert len(refs)==13

# Keep the original visualfunctions bundle intact; add this private graph to global.
ext=faf.externals[native.read_typetree()['m_Script']['m_FileID']-1]
fileid=next((i+1 for i,e in enumerate(af.externals) if e.path==ext.path),None)
if fileid is None:af.externals.append(copy.copy(ext));fileid=len(af.externals)
tree['m_Script']['m_FileID']=fileid
script=copy.copy(faf.script_types[native.serialized_type.script_type_index]);script.local_serialized_file_index=fileid
stype=copy.copy(native.serialized_type);stype.script_type_index=len(af.script_types);af.script_types.append(script);tid=len(af.types);af.types.append(stype)
needed={(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in refs};known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types}
for t in faf.ref_types:
    k=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
    if k in needed and k not in known:af.ref_types.append(copy.copy(t));known.add(k)
assert needed<=known
obj=copy.copy(native);obj.assets_file,obj.path_id,obj.type_id,obj.serialized_type=af,FPID,tid,stype;af.objects[FPID]=obj;obj.save_typetree(tree)
hashes={pid:sha(o.get_raw_data()) for pid,o in objects.items()}
bundle=next(o for o in objects.values() if o.type.name=='AssetBundle');meta=bundle.read_typetree()
banner_key=next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==BANNER)
start=len(meta['m_PreloadTable']);meta['m_PreloadTable'].extend([copy.deepcopy(tree['m_Script']),{'m_FileID':0,'m_PathID':FPID}])
meta['m_Container'].append((FGUID,{'preloadIndex':start,'preloadSize':2,'asset':{'m_FileID':0,'m_PathID':FPID}}));meta['m_Container'].sort(key=lambda x:x[0])
doc=objects[BANNER].read_typetree();old_doc=copy.deepcopy(doc);rs={r['rid']:r for r in doc['references']['RefIds']}
sd=next(r for r in rs.values() if r.get('data',{}).get('name')=='ReportMovementSumSetter')
node=next(r for r in rs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==sd['rid'])
text=next(r for r in rs.values() if r.get('data',{}).get('name')=='ReportMovementSumValue')
base=copy.deepcopy(rs[1141]);base['rid']=sd['rid'];base['data'].update(uxmlAssetId=sd['data']['uxmlAssetId'],name='ReportMovementSumFrame',name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
sd.clear();sd.update(base);node['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
def string(s):
    b=s.encode();assert len(b)<128;return bytes([len(b)])+b
argclass='SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
b=bytearray([3])
for p in PATHS:
    data=string(argclass)+b'\x01'+string(p);b.extend(struct.pack('<i',len(data)));b.extend(data)
text['data']['TextBinding']['m_visualFunction']={'m_target':{'m_guid':FGUID},'m_inputs':{'m_variable':{'m_argumentBytes':list(b)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
text['data']['DebugDisplay']='--'
modified={sd['rid'],node['rid'],text['rid']}
for r in old_doc['references']['RefIds']:
    if r['rid'] not in modified:assert rs[r['rid']]==r,r['rid']
objects[BANNER].save_typetree(doc);bundle.save_typetree(meta)
dest=OUT/'aa/StandaloneWindows64';dest.mkdir(parents=True,exist_ok=True);(dest/GLOBAL).write_bytes(env.file.save(packer='lz4'))
cat=catmod.Catalog(before_catalog);func_key='4433b71944871694ea9b7828afed05d1'
newcat=cat.add_key_location(FGUID,cat.locations(func_key)[0],cat.locations(banner_key)[0]);(OUT/'aa/catalog.bin').write_bytes(newcat)
assert newcat[:8]==before_catalog[:8] and newcat[12:len(before_catalog)]==before_catalog[12:]
saved={o.path_id:o for o in UnityPy.load(str(dest/GLOBAL)).objects}
assert saved[BANNER].read_typetree()==doc and saved[FPID].read_typetree()==tree
for pid,h in hashes.items():
    if pid not in [BANNER,bundle.path_id]:assert sha(saved[pid].get_raw_data())==h,pid
# Every serialized socket reference must refer to a known output or execution input.
exec_inputs={};data_outputs={}
for r in refs:
    d=r['data']
    for k,v in d.items():
        if isinstance(v,dict) and 'm_id' in v:
            if k.startswith('m_execIn') or k=='m_inputExecSocket':exec_inputs[bytes(v['m_id']['m_idBytes'])]=r
            if k.startswith('m_dataOut'):data_outputs[bytes(v['m_id']['m_idBytes'])]=r
    if r['type']['class']=='EntryNode':
        for p in d['m_dataSockets']:data_outputs[bytes(p['m_id']['m_idBytes'])]=r
    if r['type']['class']=='BindNode':
        for p in d['m_outputAsyncExecSocket']['m_dataOutputSockets']:data_outputs[bytes(p['m_id']['m_idBytes'])]=r
def check(v):
    if isinstance(v,dict):
        for k,x in v.items():
            if k=='m_sourceID' and any(x['m_idBytes']):assert bytes(x['m_idBytes']) in data_outputs
            elif k=='m_destinationID' and any(x['m_idBytes']):assert bytes(x['m_idBytes']) in exec_inputs
            else:check(x)
    elif isinstance(v,list):
        for x in v:check(x)
for r in refs:check(r['data'])
assert 12+13+13==38
assert (AA/'StandaloneWindows64'/FUNCTIONS).read_bytes()==before_functions
assert (AA/'StandaloneWindows64'/GLOBAL).read_bytes()==before_global and (AA/'catalog.bin').read_bytes()==before_catalog
backup=OUT/'回退/aa/StandaloneWindows64';backup.mkdir(parents=True,exist_ok=True);(backup/GLOBAL).write_bytes(before_global);(OUT/'回退/aa/catalog.bin').write_bytes(before_catalog)
manifest={'paths':PATHS,'new_function_guid':FGUID,'new_function_path_id':FPID,'graph_nodes':13,'source_global_sha256':sha(before_global),
    'global_sha256':sha((dest/GLOBAL).read_bytes()),'source_catalog_sha256':sha(before_catalog),'catalog_sha256':sha(newcat),
    'original_functions_unchanged_sha256':sha(before_functions),'existing_catalog_keys_preserved':len(cat.key_records),
    'untouched_assets_checked':len(hashes)-2,'input_failure_display':'--','game_runtime_verified':False,'installed':False}
(OUT/'修改记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'安装说明.txt').write_text('''速度、爆发力、灵活总和修正 V37（待游戏运行验证）
V36原生SumIntArgs返回0，本版改为逐项读取、TryCastToInt转换、两次相加，再直接显示文本。
取值成功且属性为12、13、13时应显示38；任何取值转换失败则显示--。
数字位置和字号沿用V36，其他布局保持现状。
原visualfunctions函数包保持原内容。

本版独立函数放在global包内，新增catalog目录记录。因此安装需要两份文件：
aa/catalog.bin -> 游戏 StreamingAssets/aa/catalog.bin
aa/StandaloneWindows64/global bundle -> 游戏 aa/StandaloneWindows64/同名bundle
退出游戏，运行安装.ps1可自动检查版本后安装。
回退时退出游戏、运行回退.ps1。
实际游戏显示尚未验证，不把结构校验等同于运行成功。
''',encoding='utf-8-sig')
for rollback in [False,True]:
    sourcefolder='回退/aa' if rollback else 'aa';recover='aa' if rollback else '回退/aa'
    eg=manifest['global_sha256'] if rollback else manifest['source_global_sha256'];ec=manifest['catalog_sha256'] if rollback else manifest['source_catalog_sha256']
    script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetAA = 'F:\\Steam\\steamapps\\common\\Project Taco\\fm_Data\\StreamingAssets\\aa'
$sourceAA = Join-Path $PSScriptRoot '{sourcefolder}'
$recoveryAA = Join-Path $PSScriptRoot '{recover}'
$globalTarget = Join-Path $targetAA 'StandaloneWindows64/{GLOBAL}'
$catalogTarget = Join-Path $targetAA 'catalog.bin'
if ((Get-FileHash -LiteralPath $globalTarget -Algorithm SHA256).Hash.ToLower() -ne '{eg}') {{ throw 'Global version mismatch.' }}
if ((Get-FileHash -LiteralPath $catalogTarget -Algorithm SHA256).Hash.ToLower() -ne '{ec}') {{ throw 'Catalog version mismatch.' }}
try {{
    Copy-Item -LiteralPath (Join-Path $sourceAA 'StandaloneWindows64/{GLOBAL}') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $sourceAA 'catalog.bin') -Destination $catalogTarget -Force
}} catch {{
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'StandaloneWindows64/{GLOBAL}') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'catalog.bin') -Destination $catalogTarget -Force
    throw
}}
Write-Host 'Complete.'
'''
    (OUT/('回退.ps1' if rollback else '安装.ps1')).write_text(script,encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps(manifest,ensure_ascii=True))
