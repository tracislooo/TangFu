import copy
import hashlib
import importlib.util
import json
import math
import shutil
import struct
import sys
import uuid
import zipfile
from pathlib import Path

ROOT=Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0,str(ROOT/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
spec=importlib.util.spec_from_file_location('catalog35',ROOT/'catalog-binary-v35.py')
catmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(catmod)
BASE=ROOT/'原生卡面写法检测75-v33'
OUT=ROOT/'独立小数选图75-v35'
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
GLOBAL='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
FUNCTIONS='ui-visualfunctions_assets_all.bundle'
BANNER,STYLE=-4194025542157271532,8045407476604796436
FUNCTION_PID=-910000000000301
FUNCTION_GUID='d82407339a994dc881b209b5b5650035'
NATIVE_PID=468212822105936887

original_write=TypeTreeHelper.write_value
def write(value,node,writer,config):
    if node.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(value,config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type!='ReferencedObjectData':original_write(value[child.m_Name],child,writer,config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):writer.align_stream()
        return
    return original_write(value,node,writer,config)
TypeTreeHelper.write_value=write
def sha(b):return hashlib.sha256(b).hexdigest()
def load(p):
    e=UnityPy.load(str(p));return e,{o.path_id:o for o in e.objects}
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]

function_bytes=(AA/'StandaloneWindows64'/FUNCTIONS).read_bytes()
assert sha(function_bytes)=='3aa259ab3b4621828cd4f74fd9ec387e971da80788912129ac5588e09fe3dc2d'
catalog_bytes=(AA/'catalog.bin').read_bytes()
env,objects=load(BASE/GLOBAL)
_,funcs=load(AA/'StandaloneWindows64'/FUNCTIONS)
original_hashes={pid:sha(o.get_raw_data()) for pid,o in objects.items()}
af=objects[BANNER].assets_file
source=funcs[NATIVE_PID];faf=source.assets_file
ft=copy.deepcopy(source.read_typetree());old_function=copy.deepcopy(ft)
ft['m_Name']=ft['m_name']='ReportStatDecimalComparisonToSwitch'
new_root={'m_idBytes':list(uuid.UUID(FUNCTION_GUID).bytes_le)}
old_root=copy.deepcopy(ft['m_id'])
def replace_root(v):
    if isinstance(v,dict):
        for k,x in list(v.items()):
            if x==old_root:v[k]=copy.deepcopy(new_root)
            else:replace_root(x)
    elif isinstance(v,list):
        for x in v:replace_root(x)
replace_root(ft)
ft['m_description']='Private decimal comparison for the four player-report league statistics.'
threshold=next(x for x in ft['m_inputs'] if x['m_name']=='CompareInt')
threshold['m_type']['m_typeString']=threshold['m_type']['m_typeString'].replace('System.Int32','System.Single')
for r in ft['references']['RefIds']:
    cls=r['type']['class'];d=r['data']
    if cls=='TypedValueVisualFunctionLibrary_TryCastToInt':
        r['type']['class']='TypedValueVisualFunctionLibrary_TryCastToFloat'
        d['m_name']='TryCastToFloat'
        d['m_dataOutFloatValue']=d.pop('m_dataOutIntValue')
        d['m_dataOutFloatValue']['m_name']='float Value'
    elif cls=='GeneralVisualFunction_CompareIntInt':
        r['type']['class']='GeneralVisualFunction_CompareFloatFloat'
        d['m_name']='CompareFloatFloat'
        for k in ['m_dataInA','m_dataInB']:d[k]['m_defaultSocketValue']['m_value']=float(d[k]['m_defaultSocketValue']['m_value'])
assert len(ft['m_nodes'])==len(old_function['m_nodes'])==8

# Register the original VisualFunction MonoScript in this serialized file.
external=source.assets_file.externals[ft['m_Script']['m_FileID']-1]
fileid=next((i+1 for i,e in enumerate(af.externals) if e.path==external.path),None)
if fileid is None:
    af.externals.append(copy.copy(external));fileid=len(af.externals)
ft['m_Script']['m_FileID']=fileid
script=copy.copy(faf.script_types[source.serialized_type.script_type_index])
script.local_serialized_file_index=fileid
st=copy.copy(source.serialized_type)
st.script_type_index=len(af.script_types);af.script_types.append(script)
tid=len(af.types);af.types.append(st)
needed={(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in ft['references']['RefIds']}
known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types}
for typ in faf.ref_types:
    key=(typ.m_ClassName,typ.m_NameSpace,typ.m_AssemblyName)
    if key in needed and key not in known:
        af.ref_types.append(copy.copy(typ));known.add(key)
assert needed<=known
assert FUNCTION_PID not in objects
newobj=copy.copy(source)
newobj.assets_file,newobj.path_id,newobj.type_id,newobj.serialized_type=af,FUNCTION_PID,tid,st
af.objects[FUNCTION_PID]=newobj
newobj.save_typetree(ft)

bundle=next(o for o in objects.values() if o.type.name=='AssetBundle')
meta=bundle.read_typetree();oldmeta=copy.deepcopy(meta)
banner_key=next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==BANNER)
start=len(meta['m_PreloadTable'])
meta['m_PreloadTable'].extend([copy.deepcopy(ft['m_Script']),{'m_FileID':0,'m_PathID':FUNCTION_PID}])
assert all(k!=FUNCTION_GUID for k,v in meta['m_Container'])
meta['m_Container'].append((FUNCTION_GUID,{'preloadIndex':start,'preloadSize':2,'asset':{'m_FileID':0,'m_PathID':FUNCTION_PID}}))
meta['m_Container'].sort(key=lambda x:x[0])

doc=objects[BANNER].read_typetree();sheet=objects[STYLE].read_typetree()
before_doc,before_sheet=copy.deepcopy(doc),copy.deepcopy(sheet)
refs={r['rid']:r for r in doc['references']['RefIds']}
names={r.get('data',{}).get('name'):r for r in refs.values() if r.get('data',{}).get('name')}
def node(sd):return next(r for r in refs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==sd['rid'])
switch_sd=names['ReportCAAbove119Switch'];switch_node=node(switch_sd)
switch_nt,switch_st=copy.deepcopy(switch_node),copy.deepcopy(switch_sd)
assert switch_st['data']['AlwaysInstantiate']==0
ve_nt,ve_st=copy.deepcopy(refs[1140]),copy.deepcopy(refs[1141])
ranges=json.loads((ROOT/'联赛四项等级图片数值标题-v31/修改记录.json').read_text(encoding='utf-8'))['ranges']
specs=[('Expected Goal/90 mins','ExpectedGoalsPer90'),('ExpectedAssists/90 mins','ExpectedAssistsPer90'),
    ('Passes Completed/90 mins','PassCompletedPer90'),('tackles won per game','TacklesCompletedPer90')]
removed=set();changed=set();new=[]
def remove(rid):
    assert rid not in removed
    removed.update([rid,refs[rid]['data']['m_SerializedData']['rid']])
    for c in refs[rid]['data']['m_Children']:remove(c['rid'])
for label,key in specs:
    group=node(names['ReportLeague'+key+'Scaled75'])
    for c in group['data']['m_Children']:
        sd=refs[refs[c['rid']]['data']['m_SerializedData']['rid']]['data']
        if 'Probe' in sd['name']:remove(c['rid'])
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]

def val(pool,typ,v):
    if v not in sheet[pool]:sheet[pool].append(v)
    return {'m_ValueType':typ,'valueIndex':sheet[pool].index(v)}
def px(v):return val('dimensions',3,{'unit':1,'value':float(v)})
def pct(v):return val('dimensions',3,{'unit':2,'value':float(v)})
def en(v):return val('strings',7,v)
def prop(pid,*v):return {'m_Id':pid,'m_CustomName':'','m_Line':-1,'m_Values':list(v)}
def rule(properties):
    i=len(sheet['m_Rules']);sheet['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':properties,'line':-1});return i
fill=[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131105,pct(100)),prop(131087,pct(100)),prop(262150,px(0)),prop(262151,px(0))]
fill_rule=rule(copy.deepcopy(fill))
image_rules={pid:rule(copy.deepcopy(fill)+[prop(458753,val('assets',6,{'m_FileID':0,'m_PathID':pid})),prop(262153,en('scale-to-fit'))]) for pid in range(-910000000000008,-910000000000018,-1)}
rid=max(refs)+1;eid=1903500000
def pair(nt,st,parent,name,ri):
    global rid,eid
    n,s=copy.deepcopy(nt),copy.deepcopy(st);n['rid'],s['rid']=rid,rid+1;rid+=2
    n['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=ri,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[],m_SkipClone=0)
    s['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
    eid+=1;refs[n['rid']],refs[s['rid']]=n,s;new.extend([n,s]);return n,s
def children(parent,ids):
    refs[parent]['data']['m_Children']=[{'rid':x} for x in ids]
    for x in ids:refs[x]['data']['m_Parent']={'rid':parent}
def string(s):
    b=s.encode();assert len(b)<128;return bytes([len(b)])+b
def args(bound,path):
    fields=[('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]',struct.pack('<i',5)),
        ('SI.VisualScripting.SingleVisualArg',struct.pack('<f',bound)),
        ('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\x01'+string(path))]
    b=bytearray([3])
    for cls,v in fields:
        x=string(cls)+v;b.extend(struct.pack('<i',len(x)));b.extend(x)
    return list(b)
conditions=[]
for label,key in specs:
    rows=ranges[label];group=node(names['ReportLeague'+key+'Scaled75'])
    value=node(names['ReportLeague'+key+'Value']);title=node(names['ReportLeague'+key+'Title'])
    switches=[];images=[]
    for i,row in enumerate(rows[1:]):
        parent=group['rid'] if i==0 else switches[-1][0]['rid']
        n,s=pair(switch_nt,switch_st,parent,f'ReportLeague{key}AtLeast{row["name"]}',fill_rule)
        vf=s['data']['Binding']['m_visualFunction'];vf['m_target']['m_guid']=FUNCTION_GUID
        vf['m_inputs']['m_variable']['m_argumentBytes']=args(row['min'],'SeasonStats.'+key)
        switches.append((n,s));conditions.append({'sd':s['rid'],'metric':label,'threshold':row['min']})
    for i,row in enumerate(rows):
        n,s=pair(ve_nt,ve_st,switches[min(i,8)][0]['rid'],f'ReportLeague{key}{row["name"]}',image_rules[row['pid']]);images.append(n['rid'])
    for i,(n,s) in enumerate(switches):children(n['rid'],[images[i],switches[i+1][0]['rid'] if i<8 else images[9]])
    children(group['rid'],[switches[0][0]['rid'],value['rid'],title['rid']]);changed.add(group['rid'])
doc['references']['RefIds'].extend(new)
for r in before_doc['references']['RefIds']:
    if r['rid'] not in removed|changed:assert refs[r['rid']]==r,r['rid']
assert sheet['m_Rules'][:len(before_sheet['m_Rules'])]==before_sheet['m_Rules']
objects[BANNER].save_typetree(doc);objects[STYLE].save_typetree(sheet);bundle.save_typetree(meta)
dest=OUT/'aa/StandaloneWindows64';dest.mkdir(parents=True,exist_ok=True)
(dest/GLOBAL).write_bytes(env.file.save(packer='lz4'))

# Append one catalog key; all existing keys and locations remain byte-identical.
catalog=catmod.Catalog(catalog_bytes)
template_loc=catalog.locations('f6f314e9db56227459137669d87c44e9')[0]
global_loc=catalog.locations(banner_key)[0]
new_catalog=catalog.add_key_location(FUNCTION_GUID,template_loc,global_loc)
assert new_catalog[:8]==catalog_bytes[:8] and new_catalog[12:len(catalog_bytes)]==catalog_bytes[12:]
(OUT/'aa/catalog.bin').write_bytes(new_catalog)
recat=catmod.Catalog(new_catalog)
assert recat.key_records[:-1]==catmod.Catalog(catalog_bytes).key_records
location=recat.location(recat.locations(FUNCTION_GUID)[0])
assert location['type'][1]=='SI.VisualScripting.VisualFunction'
assert location['dependencies']==recat.location(global_loc)['dependencies']
assert location['internal']==FUNCTION_GUID

_,check=load(dest/GLOBAL)
assert set(check)==set(objects)|{FUNCTION_PID}
assert check[FUNCTION_PID].read_typetree()==ft
assert check[BANNER].read_typetree()==doc
assert check[STYLE].read_typetree()==sheet
for pid,digest in original_hashes.items():
    if pid not in [BANNER,STYLE,bundle.path_id]:assert sha(check[pid].get_raw_data())==digest,pid
assert (AA/'StandaloneWindows64'/FUNCTIONS).read_bytes()==function_bytes
assert (AA/'catalog.bin').read_bytes()==catalog_bytes
seen=set()
def visit(r):
    assert r not in seen;seen.add(r)
    for c in refs[r].get('data',{}).get('m_Children',[]):
        assert refs[c['rid']]['data']['m_Parent']['rid']==r;visit(c['rid'])
visit(doc['m_VisualTree']['rid']);assert not seen&removed
assert all('Probe' not in r.get('data',{}).get('name','') for r in doc['references']['RefIds'])

# Check actual serialized Single thresholds and exclusive branch structure.
def decode_arg_bytes(a):
    raw=bytes(a);pos=1;out=[]
    for _ in range(raw[0]):
        length=struct.unpack_from('<i',raw,pos)[0];pos+=4;p=raw[pos:pos+length];pos+=length
        size=p[0];out.append((p[1:1+size].decode(),p[1+size:]))
    assert pos==len(raw);return out
for c in conditions:
    sd=refs[c['sd']]['data'];a=decode_arg_bytes(sd['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    assert a[1][0]=='SI.VisualScripting.SingleVisualArg'
    assert struct.unpack('<f',a[1][1])[0]==f32(c['threshold'])
def selected(label,value):
    rows=ranges[label];value=f32(value)
    i=0
    for j,row in enumerate(rows[1:],1):
        if value>=f32(row['min']):i=j
        else:break
    return rows[i]['name']
examples=[(specs[0][0],.02,'level001'),(specs[1][0],.07,'level003'),(specs[2][0],62.36,'level010'),(specs[3][0],.96,'level004')]
cases=0
for label,rows in ranges.items():
    for i,row in enumerate(rows):
        for value in [row['min'],row['max'],(row['min']+row['max'])/2]:
            assert selected(label,value)==row['name'];cases+=1
for label,value,result in examples:assert selected(label,value)==result
manifest={'function_guid':FUNCTION_GUID,'function_path_id':FUNCTION_PID,'function_nodes':8,'scale':.75,
    'ranges':ranges,'examples':examples,'boundary_checks':cases,'original_functions_unchanged_sha256':sha(function_bytes),
    'catalog_before_sha256':sha(catalog_bytes),'catalog_after_sha256':sha(new_catalog),'catalog_existing_keys_preserved':len(catalog.key_records),
    'global_before_sha256':sha((BASE/GLOBAL).read_bytes()),'global_after_sha256':sha((dest/GLOBAL).read_bytes()),
    'original_assets_unchanged':len(original_hashes)-3,'runtime_verified':False,'installed':False}
(OUT/'修改记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
backup=OUT/'回退/aa/StandaloneWindows64';backup.mkdir(parents=True,exist_ok=True)
shutil.copyfile(AA/'StandaloneWindows64'/GLOBAL,backup/GLOBAL)
shutil.copyfile(AA/'catalog.bin',OUT/'回退/aa/catalog.bin')
(OUT/'安装说明.txt').write_text('''独立小数选图75 v35（游戏内待验证）

本版新增独立的小数比较函数，沿用原生卡面的互斥 Switch 分支。
数值先 TryCastToFloat，再按表中小数边界比较；每项选一张图。
四项图文整体缩放75%，删除所有 i 检测标记。
没有修改 ui-visualfunctions_assets_all.bundle，继续使用 v34 恢复后的版本。
头像、卡面、左边信息、Actions及栏目185px高度保持现状。

安装：
1. 退出游戏。
2. 运行 安装.ps1；或者把 aa 文件夹里的两份文件按目录覆盖到：
   F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/
   catalog.bin 放在 aa 目录；global bundle 放在 aa/StandaloneWindows64 目录。
3. 两份文件必须一起安装，仅导入 JSON 或只替换 bundle 无法注册新函数。
4. 重启游戏查看同一名球员。截图中的0.02、0.07、62.36、0.96，
   应分别显示 level001、level003、level010、level004。

需要回退时：退出游戏，运行 回退.ps1，会恢复本次打包时的global和catalog。
游戏更新后不要覆盖旧catalog；需要针对更新后的目录重新生成此条函数记录。
已校验所有原目录记录、原有其他资源、函数序列化和分档边界；实际运行仍待验证。
''',encoding='utf-8-sig')
for rollback in [False,True]:
    script_name='回退.ps1' if rollback else '安装.ps1'
    relative='回退/aa' if rollback else 'aa'
    expected_catalog=manifest['catalog_after_sha256'] if rollback else manifest['catalog_before_sha256']
    expected_global=manifest['global_after_sha256'] if rollback else sha((backup/GLOBAL).read_bytes())
    recovery_relative='aa' if rollback else '回退/aa'
    ps=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager before replacing files.' }}
$targetAA = 'F:\\Steam\\steamapps\\common\\Project Taco\\fm_Data\\StreamingAssets\\aa'
$sourceAA = Join-Path $PSScriptRoot '{relative}'
$recoveryAA = Join-Path $PSScriptRoot '{recovery_relative}'
$catalogTarget = Join-Path $targetAA 'catalog.bin'
$globalTarget = Join-Path $targetAA 'StandaloneWindows64/{GLOBAL}'
if ((Get-FileHash -LiteralPath $catalogTarget -Algorithm SHA256).Hash.ToLower() -ne '{expected_catalog}') {{ throw 'Catalog changed. Do not overwrite a different game version.' }}
if ((Get-FileHash -LiteralPath $globalTarget -Algorithm SHA256).Hash.ToLower() -ne '{expected_global}') {{ throw 'Global bundle changed. Please check the installed version.' }}
if ((Get-FileHash -LiteralPath (Join-Path $targetAA 'StandaloneWindows64/{FUNCTIONS}') -Algorithm SHA256).Hash.ToLower() -ne '{sha(function_bytes)}') {{ throw 'The visual functions bundle does not match the v34 recovery version.' }}
try {{
    Copy-Item -LiteralPath (Join-Path $sourceAA 'StandaloneWindows64/{GLOBAL}') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $sourceAA 'catalog.bin') -Destination $catalogTarget -Force
}} catch {{
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'StandaloneWindows64/{GLOBAL}') -Destination $globalTarget -Force
    Copy-Item -LiteralPath (Join-Path $recoveryAA 'catalog.bin') -Destination $catalogTarget -Force
    throw
}}
Write-Host 'Complete. Start the game to verify.'
'''
    (OUT/script_name).write_text(ps,encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.rglob('*'):
        if p.is_file():z.write(p,p.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({k:manifest[k] for k in ['function_nodes','boundary_checks','catalog_existing_keys_preserved','original_assets_unchanged','runtime_verified']},ensure_ascii=True))
print(str(OUT.with_suffix('.zip')).encode('unicode_escape').decode())
