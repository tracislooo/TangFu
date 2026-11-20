import copy,hashlib,json,struct,sys,zipfile
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa')
GLOBAL='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
FUNCTIONS='ui-visualfunctions_assets_all.bundle'
OUT=R/'速度爆发灵活总和-V36'
BANNER,STYLE=-4194025542157271532,8045407476604796436
SUM_GUID='a82e4cf3a34b1ae41b85cacd4f63208c'
DEST='ReportMovementSum'
PATHS=['person.AttributePace.PropertyValue','person.AttributeAcceleration.PropertyValue','person.AttributeAgility.PropertyValue']
sha=lambda b:hashlib.sha256(b).hexdigest()
source=AA/'StandaloneWindows64'/GLOBAL
source_bytes=source.read_bytes()
assert sha(source_bytes)=='f9937bd9da160f4b38896f216f1bd3ce91711127f7bd4af61f3eb80fc5169fa8'
function_hash=sha((AA/'StandaloneWindows64'/FUNCTIONS).read_bytes())
catalog_hash=sha((AA/'catalog.bin').read_bytes())

original_write=TypeTreeHelper.write_value
def write(v,node,writer,config):
    if node.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type!='ReferencedObjectData':original_write(v[child.m_Name],child,writer,config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):writer.align_stream()
        return
    return original_write(v,node,writer,config)
TypeTreeHelper.write_value=write

env=UnityPy.load(str(source));objects={o.path_id:o for o in env.objects}
hashes={pid:sha(o.get_raw_data()) for pid,o in objects.items()}
doc=objects[BANNER].read_typetree();sheet=objects[STYLE].read_typetree()
old_doc,old_sheet=copy.deepcopy(doc),copy.deepcopy(sheet)
refs={r['rid']:r for r in doc['references']['RefIds']}
search=next(x['tree'] for x in json.loads((R/'sum-ui-template-v36.json').read_text(encoding='utf-8')) if x['name']=='GlobalSearchCard')
srefs={r['rid']:r for r in search['references']['RefIds']}
setter_sd=srefs[1016]
setter_node=next(r for r in srefs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==1016)
native_sum=next(v for v in setter_sd['data']['BindFunction'] if v['m_target']['m_guid']==SUM_GUID)
integer=json.loads((R/'native-integer-text-template-v36.json').read_text(encoding='utf-8'))
assert refs[1013]['data']['m_Children']==[{'rid':1028}]
assert next(r for r in refs.values() if r['type']['class']=='BindingExpect/UxmlSerializedData')['data']['Parameters'][0]['name']=='person'

def string(s):
    b=s.encode();assert len(b)<128;return bytes([len(b)])+b
def read_string(b,p=0):
    n=shift=0
    while True:
        v=b[p];p+=1;n|=(v&127)<<shift
        if v<128:break
        shift+=7
    return b[p:p+n].decode(),p+n
def decode(a):
    b=bytes(a);p=1;out=[]
    for _ in range(b[0]):
        n=struct.unpack_from('<i',b,p)[0];p+=4;payload=b[p:p+n];p+=n;c,j=read_string(payload);out.append((c,payload[j:]))
    assert p==len(b);return out
def encode(a):
    b=bytearray([len(a)])
    for c,v in a:
        p=string(c)+v;b.extend(struct.pack('<i',len(p)));b.extend(p)
    return list(b)
original_args=decode(native_sum['m_inputs']['m_variable']['m_argumentBytes'])
assert [c for c,v in original_args]==['SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BindingPath]','SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]']
sum_fn=copy.deepcopy(native_sum)
sum_fn['m_inputs']['m_variable']['m_argumentBytes']=encode([
    (original_args[0][0],bytes([3])+b''.join(b'\x01'+string(p) for p in PATHS)),
    (original_args[1][0],b'\x01'+string(DEST))])

def val(pool,typ,v):
    if v not in sheet[pool]:sheet[pool].append(v)
    return {'m_ValueType':typ,'valueIndex':sheet[pool].index(v)}
def px(v):return val('dimensions',3,{'unit':1,'value':float(v)})
def pct(v):return val('dimensions',3,{'unit':2,'value':float(v)})
def enum(v):return val('strings',7,v)
def num(v):return val('floats',2,float(v))
def p(pid,*values):return {'m_Id':pid,'m_CustomName':'','m_Line':-1,'m_Values':list(values)}
def rule(props):
    i=len(sheet['m_Rules']);sheet['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':props,'line':-1});return i
setter_rule=rule([p(131084,num(1)),p(131085,num(1)),p(131082,px(0)),p(131097,px(0)),
    p(131087,pct(100)),p(131074,enum('stretch')),p(131083,enum('column')),p(131088,enum('center')),
    p(262150,px(0)),p(131092,px(12)),p(262151,px(0))])
text_rule=rule([p(131105,pct(100)),p(131087,pct(100)),p(131097,px(0)),p(131084,num(1)),
    p(65537,px(26)),p(65546,enum('middle-center')),p(65552,enum('nowrap')),
    p(65536,val('colors',4,{'r':1.0,'g':1.0,'b':1.0,'a':1.0})),p(262150,px(0)),p(262151,px(0))])
new=[];rid=max(refs)+1;eid=1903600000
def pair(nt,st,parent,name,index):
    global rid,eid
    n,s=copy.deepcopy(nt),copy.deepcopy(st);n['rid'],s['rid']=rid,rid+1;rid+=2
    n['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=index,
        m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[],m_SkipClone=0)
    s['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
    eid+=1;refs[n['rid']],refs[s['rid']]=n,s;new.extend([n,s]);return n,s
setter,sd=pair(setter_node,setter_sd,1013,'ReportMovementSumSetter',setter_rule)
sd['data'].update(ValueVariables=[{'m_name':DEST,'m_scopeValue':{'m_serializedData':'Int|0|'}}],ReferenceVariables=[],
    ValueVariables_UxmlAttributeFlags=1,ReferenceVariables_UxmlAttributeFlags=0,BindFunction=[sum_fn],BindFunction_UxmlAttributeFlags=1)
text,tsd=pair(integer['node'],integer['sd'],setter['rid'],'ReportMovementSumValue',text_rule)
tsd['data']['DebugDisplay']='--'
vf=tsd['data']['TextBinding']['m_visualFunction']
assert vf['m_target']['m_guid']=='f97abdf5a74842647ba921d183f4a3eb'
a=decode(vf['m_inputs']['m_variable']['m_argumentBytes'])
payload=a[1][1];assert payload[:2]==b'\x01\x01'
_,end=read_string(payload,2)
a[1]=(a[1][0],b'\x01\x01'+string(DEST)+payload[end:])
vf['m_inputs']['m_variable']['m_argumentBytes']=encode(a)
setter['data']['m_Children']=[{'rid':text['rid']}]
refs[1013]['data']['m_Children']=[{'rid':setter['rid']},{'rid':1028}]
doc['references']['RefIds'].extend(new)
known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in objects[BANNER].assets_file.ref_types}
assert all((r['type']['class'],r['type']['ns'],r['type']['asm']) in known for r in new)
for r in old_doc['references']['RefIds']:
    if r['rid']!=1013:assert refs[r['rid']]==r,r['rid']
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])]==old_sheet['m_Rules']
objects[BANNER].save_typetree(doc);objects[STYLE].save_typetree(sheet)
OUT.mkdir(exist_ok=True);dest=OUT/GLOBAL;dest.write_bytes(env.file.save(packer='lz4'))
saved={o.path_id:o for o in UnityPy.load(str(dest)).objects}
assert saved[BANNER].read_typetree()==doc and saved[STYLE].read_typetree()==sheet
assert set(saved)==set(objects)
for pid,digest in hashes.items():
    if pid not in [BANNER,STYLE]:assert sha(saved[pid].get_raw_data())==digest,pid
seen=set()
def visit(r):
    assert r not in seen;seen.add(r)
    for c in refs[r].get('data',{}).get('m_Children',[]):
        assert refs[c['rid']]['data']['m_Parent']['rid']==r;visit(c['rid'])
visit(doc['m_VisualTree']['rid']);assert setter['rid'] in seen and text['rid'] in seen
a=decode(sd['data']['BindFunction'][0]['m_inputs']['m_variable']['m_argumentBytes'])
assert a[0][1][0]==3
pos=1;paths=[]
for _ in range(3):
    assert a[0][1][pos]==1;pos+=1;path,pos=read_string(a[0][1],pos);paths.append(path)
assert pos==len(a[0][1]) and paths==PATHS
assert read_string(a[1][1],1)[0]==DEST
assert sd['data']['ValueVariables'][0]['m_name']==DEST
ta=decode(tsd['data']['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
assert read_string(ta[0][1],5)[0]=='[%number#1]'
assert read_string(ta[1][1],2)[0]==DEST
assert sha((AA/'StandaloneWindows64'/FUNCTIONS).read_bytes())==function_hash
assert sha((AA/'catalog.bin').read_bytes())==catalog_hash
assert source.read_bytes()==source_bytes

(OUT/'report-player-banner-max.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),encoding='utf-8')
(OUT/'inlineStyle-report-player-banner-max.json').write_text(json.dumps(sheet,ensure_ascii=False,indent=2),encoding='utf-8')
notes='''速度、爆发力、灵活总和 V36

基于已回退的V30。
在报告头最右侧底部、Actions按钮左边显示一个实时整数。
取数：
person.AttributePace.PropertyValue
person.AttributeAcceleration.PropertyValue
person.AttributeAgility.PropertyValue

调用原生 BindMultipleIntArgsAsSumToDestination，结果写入局部 Int 变量 ReportMovementSum。
再用原生整数文本格式显示结果。没有把截图数字写死。
截图球员为12+13+13，预期显示38。

安装：退出游戏，替换同名global bundle至：
F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/
只需替换这一份bundle，不需要替换visualfunctions、catalog、backgrounds、gameworld。
若通过Skin Builder导入JSON，包内两份JSON需一起导入，然后重新打包global。
本次仅改report-max的树与内联样式；栏目185px、四项统计、头像卡面及Actions按钮原有样式保留。
若要回退，使用V30的global bundle。

已检查原生求和参数、整数显示格式、局部变量、父子结构和其余资源字节。
游戏当前运行中，所以没有覆盖安装文件；实际显示仍待重启游戏验证。
'''
(OUT/'安装说明.txt').write_text(notes,encoding='utf-8-sig')
manifest={'baseline':'V30','source_sha256':sha(source_bytes),'output_sha256':sha(dest.read_bytes()),
    'paths':PATHS,'destination_scope_variable':DEST,'sum_function_guid':SUM_GUID,
    'native_sum_template':'GlobalSearchCard.SearchBindingsSetter','native_integer_text_template':integer['source_name'],
    'position':'Actions frame, before existing Actions button','font_size_px':26,'header_height_px':185,
    'expected_screenshot_value':38,'changed_existing_record_ids':[1013],
    'changed_asset_ids':[BANNER,STYLE],'untouched_asset_byte_checks':len(hashes)-2,
    'visualfunctions_unchanged_sha256':function_hash,'catalog_unchanged_sha256':catalog_hash,
    'game_runtime_verified':False,'installed':False}
(OUT/'修改记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():z.write(p,p.name)
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'zip':str(OUT.with_suffix('.zip')),'expected_value':38,'unchanged_assets':len(hashes)-2,'game_runtime_verified':False},ensure_ascii=True))
