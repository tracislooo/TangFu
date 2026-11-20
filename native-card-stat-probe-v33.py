import copy
import hashlib
import json
import shutil
import struct
import sys
import zipfile
from pathlib import Path

ROOT=Path('G:/Doc/ChatGPT/New project')
sys.path.insert(0,str(ROOT/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
BASE=ROOT/'联赛四项等级图片数值标题-v31'
OUT=ROOT/'原生卡面写法检测75-v33'
GLOBAL='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
FUNCTIONS='ui-visualfunctions_assets_all.bundle'
ORIGINAL_FUNCTIONS=Path('G:/Doc/skins/27_01')/FUNCTIONS
BANNER,STYLE=-4194025542157271532,8045407476604796436

original_write=TypeTreeHelper.write_value
def write(value,node,writer,config):
    if node.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(value,config.assetsfile) is None:
        for child in node.m_Children:
            if child.m_Type!='ReferencedObjectData':original_write(value[child.m_Name],child,writer,config)
        if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):writer.align_stream()
        return
    return original_write(value,node,writer,config)
TypeTreeHelper.write_value=write
def sha(data):return hashlib.sha256(data).hexdigest()
env=UnityPy.load(str(BASE/GLOBAL));objects={o.path_id:o for o in env.objects}
hashes={pid:sha(o.get_raw_data()) for pid,o in objects.items()}
doc=objects[BANNER].read_typetree();sheet=objects[STYLE].read_typetree()
old_doc,old_sheet=copy.deepcopy(doc),copy.deepcopy(sheet)
refs={r['rid']:r for r in doc['references']['RefIds']}
names={r.get('data',{}).get('name'):r for r in refs.values() if r.get('data',{}).get('name')}
def node(sd):return next(r for r in refs.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==sd['rid'])
switch_sd=names['ReportCAAbove119Switch'];switch_node=node(switch_sd)
assert switch_sd['data']['AlwaysInstantiate']==0
assert switch_sd['data']['Binding']['m_visualFunction']['m_target']['m_guid']=='f6f314e9db56227459137669d87c44e9'
specs=[('ExpectedGoalsPer90','SeasonStats.ExpectedGoalsPer90'),('ExpectedAssistsPer90','SeasonStats.ExpectedAssistsPer90'),
       ('PassCompletedPer90','SeasonStats.PassCompletedPer90'),('TacklesCompletedPer90','SeasonStats.TacklesCompletedPer90')]
removed=set()
def remove(rid):
    removed.add(rid);removed.add(refs[rid]['data']['m_SerializedData']['rid'])
    for c in refs[rid]['data']['m_Children']:remove(c['rid'])
for key,path in specs:remove(node(names['ReportLeague'+key+'ImageStack'])['rid'])
assert len(removed)==248
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
def val(pool,typ,v):
    if v not in sheet[pool]:sheet[pool].append(v)
    return {'m_ValueType':typ,'valueIndex':sheet[pool].index(v)}
def px(v):return val('dimensions',3,{'unit':1,'value':float(v)})
def pct(v):return val('dimensions',3,{'unit':2,'value':float(v)})
def en(v):return val('strings',7,v)
def p(pid,*v):return {'m_Id':pid,'m_CustomName':'','m_Line':-1,'m_Values':list(v)}
def rule(properties):
    i=len(sheet['m_Rules']);sheet['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':properties,'line':-1});return i
full=[p(131102,en('absolute')),p(131089,px(0)),p(131104,px(0)),p(131105,pct(100)),p(131087,pct(100)),p(262150,px(0)),p(262151,px(0))]
full_rule=rule(copy.deepcopy(full))
scale_rule=rule(copy.deepcopy(full)+[p(327681,val('floats',2,.75),val('floats',2,.75))])
image_rule=rule(copy.deepcopy(full)+[p(458753,val('assets',6,{'m_FileID':0,'m_PathID':-910000000000008})),p(262153,en('scale-to-fit'))])
probe_rule=rule([p(131102,en('absolute')),p(131089,px(0)),p(131104,px(0)),p(131105,pct(100)),
    p(131087,px(14)),p(65537,px(12)),p(65546,en('upper-left')),p(65552,en('nowrap')),
    p(65536,val('colors',4,{'r':1.0,'g':1.0,'b':1.0,'a':1.0})),p(262150,px(0)),p(262151,px(0))])
new=[];rid=max(refs)+1;eid=1901300000
def pair(nt,st,parent,name,ri):
    global rid,eid
    n,s=copy.deepcopy(nt),copy.deepcopy(st);n['rid'],s['rid']=rid,rid+1;rid+=2
    n['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=ri,
        m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[],m_SkipClone=0)
    s['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
    eid+=1;refs[n['rid']],refs[s['rid']]=n,s;new.extend([n,s]);return n,s
def children(parent,ids):
    refs[parent]['data']['m_Children']=[{'rid':x} for x in ids]
    for x in ids:refs[x]['data']['m_Parent']={'rid':parent}
def strbytes(s):
    b=s.encode();assert len(b)<128;return bytes([len(b)])+b
def switch_args(threshold,path):
    a=[('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.GeneralVisualFunction+ComparisonOperator]',struct.pack('<i',4)),
       ('SI.VisualScripting.Int32VisualArg',struct.pack('<i',threshold)),
       ('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]',b'\x01'+strbytes(path))]
    b=bytearray([3])
    for cls,v in a:
        data=strbytes(cls)+v;b.extend(struct.pack('<i',len(data)));b.extend(data)
    return list(b)
thresholds=[0,1,4,9,49,99,999,9999]
labels=['i<=0','i=1','i=2-4','i=5-9','i=10-49','i=50-99','i=100-999','i=1000-9999','i>=10000']
changed=set()
for key,path in specs:
    cell=node(names['ReportLeague'+key+'Cell']);title=node(names['ReportLeague'+key+'Title']);value=node(names['ReportLeague'+key+'Value'])
    group,_=pair(refs[1140],refs[1141],cell['rid'],'ReportLeague'+key+'Scaled75',scale_rule)
    image,_=pair(refs[1140],refs[1141],group['rid'],'ReportLeague'+key+'ProbeNeutralImage',image_rule)
    switches=[]
    for i,bound in enumerate(thresholds):
        parent=group['rid'] if i==0 else switches[-1][0]['rid']
        n,s=pair(switch_node,switch_sd,parent,f'ReportLeague{key}IntegerProbe{bound}',probe_rule)
        s['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=switch_args(bound,path)
        switches.append((n,s))
    texts=[]
    for i,label in enumerate(labels):
        ts=names['ReportLeague'+key+'Value'];tn=node(ts)
        n,s=pair(tn,ts,switches[min(i,7)][0]['rid'],f'ReportLeague{key}IntegerProbeLabel{i}',probe_rule)
        s['data'].update(text=label,text_UxmlAttributeFlags=1,DebugDisplay=label,
            TextBinding_UxmlAttributeFlags=0,BindTextFunction_UxmlAttributeFlags=0)
        empty={'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
        s['data']['TextBinding']={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':copy.deepcopy(empty)}
        s['data']['BindTextFunction']=copy.deepcopy(empty);texts.append(n['rid'])
    for i,(n,s) in enumerate(switches):children(n['rid'],[texts[i],switches[i+1][0]['rid'] if i<7 else texts[8]])
    children(group['rid'],[image['rid'],value['rid'],title['rid'],switches[0][0]['rid']])
    children(cell['rid'],[group['rid']]);changed.update([cell['rid'],value['rid'],title['rid']])
doc['references']['RefIds'].extend(new)
for r in old_doc['references']['RefIds']:
    if r['rid'] not in removed and r['rid'] not in changed:assert refs[r['rid']]==r
assert sheet['m_Rules'][:len(old_sheet['m_Rules'])]==old_sheet['m_Rules']
objects[BANNER].save_typetree(doc);objects[STYLE].save_typetree(sheet)
OUT.mkdir(exist_ok=True);(OUT/GLOBAL).write_bytes(env.file.save(packer='lz4'))
shutil.copyfile(ORIGINAL_FUNCTIONS,OUT/FUNCTIONS)
check={o.path_id:o for o in UnityPy.load(str(OUT/GLOBAL)).objects}
assert check[BANNER].read_typetree()==doc and check[STYLE].read_typetree()==sheet
for pid,digest in hashes.items():
    if pid not in [BANNER,STYLE]:assert sha(check[pid].get_raw_data())==digest
assert (OUT/FUNCTIONS).read_bytes()==ORIGINAL_FUNCTIONS.read_bytes()
rs={r['rid']:r for r in doc['references']['RefIds']};seen=set()
def visit(r):
    assert r not in seen;seen.add(r)
    for c in rs[r].get('data',{}).get('m_Children',[]):
        assert rs[c['rid']]['data']['m_Parent']['rid']==r;visit(c['rid'])
visit(doc['m_VisualTree']['rid']);assert not seen&removed
(OUT/'安装说明.txt').write_text('''原生卡面写法检测75 v33（检测版，尚未完成最终图片分档）

包内visualfunctions是G:/Doc/skins/27_01的原版文件，未做任何改写。
游戏安装目录已恢复此原版函数包，并临时恢复到v30的正常四项统计界面。

检测版global只调用头像卡面同一个原生BindIntComparisonToSwitch，不新增或修改函数。
四项图文整体75%，每项只有一张中性level001图片，不会叠放十张。
数值和标题原有的联赛绑定保留。图片旁新增i标记代表该数值经原生整数函数读取后的区间。

请退出游戏，安装检测版global，打开一名预期进球/90非零的球员，
告诉我四项数值和对应i标记（例如0.27，i<=0）。
此检测用来确认统计值内部是否已经缩放成整数，随后才能正确复用卡面的互斥图片分支。
检测版的level001是刻意固定的，不代表最终图片选择结果。
整个栏目仍185px，Actions和头像卡面没有改动。
''',encoding='utf-8-sig')
manifest={'original_functions_sha256':sha((OUT/FUNCTIONS).read_bytes()),'scale':.75,'probe_thresholds':thresholds,
    'probe_labels':labels,'native_function_guid':'f6f314e9db56227459137669d87c44e9','game_runtime_verified':False,
    'final_image_mapping_complete':False,'global_sha256':sha((OUT/GLOBAL).read_bytes())}
(OUT/'修改记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf-8')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for p in OUT.iterdir():z.write(p,p.name)
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'output':str(OUT.with_suffix('.zip')),'original_function_hash':manifest['original_functions_sha256']},ensure_ascii=True))
