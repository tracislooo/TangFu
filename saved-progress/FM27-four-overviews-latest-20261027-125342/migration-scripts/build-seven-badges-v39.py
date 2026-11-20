import copy,json,sys,struct,uuid,hashlib,importlib.util,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');N='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';OUT=R/'七项属性徽章-V39';B=-4194025542157271532;S=8045407476604796436;FP=-910000000000303;FG='d25e07441190434f86b42ec2ec560039'
sha=lambda b:hashlib.sha256(b).hexdigest();source=(AA/'StandaloneWindows64'/N).read_bytes();catalog=(AA/'catalog.bin').read_bytes()
assert sha(source)=='c32aa52889f5585f6a3db3e365e48e4b507bcdae5538b82f71727219b330e56e'
oldwrite=TypeTreeHelper.write_value
def write(v,n,w,c):
 if n.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,c.assetsfile) is None:
  for ch in n.m_Children:
   if ch.m_Type!='ReferencedObjectData':oldwrite(v[ch.m_Name],ch,w,c)
  if TypeTreeHelper.metaflag_is_aligned(n.m_MetaFlag):w.align_stream()
  return
 return oldwrite(v,n,w,c)
TypeTreeHelper.write_value=write
e=UnityPy.load(str(AA/'StandaloneWindows64'/N));obs={o.path_id:o for o in e.objects};af=obs[B].assets_file;hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
fenv=UnityPy.load(str(AA/'StandaloneWindows64/ui-visualfunctions_assets_all.bundle'));native=next(o for o in fenv.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='BindMultipleIntArgsAsSumToDestination');nt=native.read_typetree()
templates=json.loads((R/'movement-sum-node-templates-v37.json').read_text())
for r in nt['references']['RefIds']:templates[r['type']['class']]=r
# Function: cast five attributes, sum, publish one local int used by text and image switches.
tree=copy.deepcopy(obs[-910000000000302].read_typetree());tree.update(m_Name='ReportFiveAttributeSum',m_name='ReportFiveAttributeSum',m_description='Five integer attribute values to a local sum; -1 if any unavailable.',m_inputs=[],m_outputs=[],m_variables=[],m_nodes=[])
def guid():return {'m_idBytes':list(uuid.uuid4().bytes_le)}
root=guid();tree['m_id']=root
for name,template in [('BindingBag',nt['m_inputs'][0]),('Target',nt['m_inputs'][1])]+[(f'Attribute{i}',nt['m_inputs'][3]) for i in range(5)]+[('Destination',nt['m_inputs'][3])]:
 p=copy.deepcopy(template);p.update(m_name=name,m_id=guid(),m_parentID=copy.deepcopy(root));tree['m_inputs'].append(p)
fr=[]
def clone(cls,name):
 r=copy.deepcopy(templates[cls]);r['rid']=190390000000000000+len(fr);d=r['data'];d.update(m_name=name,m_id=guid(),m_parentID=copy.deepcopy(root))
 def reset(v):
  if isinstance(v,dict):
   for k,x in v.items():
    if k=='m_id' and isinstance(x,dict) and 'm_idBytes' in x:v[k]=guid()
    elif k in ['m_sourceID','m_destinationID']:v[k]={'m_idBytes':[0]*16}
    else:reset(x)
  elif isinstance(v,list):
   for x in v:reset(x)
 for k,v in d.items():
  if k not in ['m_id','m_parentID']:reset(v)
 fr.append(r);return d
entry=clone('EntryNode','Entry');entry['m_dataSockets']=[{'m_id':guid(),'m_name':p['m_name'],'m_dataID':copy.deepcopy(p['m_id'])} for p in tree['m_inputs']];ports={p['m_name']:p['m_id'] for p in entry['m_dataSockets']}
bind=clone('BindNode','Read Five Attribute Values');bind['m_bindingBagDataInputSocket']['m_sourceID']=ports['BindingBag'];bind['m_componentDataInputSocket']['m_sourceID']=ports['Target']
di0=copy.deepcopy(bind['m_dynamicDataInputSockets'][0]);do0=copy.deepcopy(bind['m_outputAsyncExecSocket']['m_dataOutputSockets'][0]);bind['m_dynamicDataInputSockets']=[];bind['m_outputAsyncExecSocket']['m_dataOutputSockets']=[]
# Use a single BindingPath native template (the sum template is StructList).
b0=json.loads((R/'movement-sum-node-templates-v37.json').read_text())['BindNode']['data'];di0=copy.deepcopy(b0['m_dynamicDataInputSockets'][0]);do0=copy.deepcopy(b0['m_outputAsyncExecSocket']['m_dataOutputSockets'][0])
for p in tree['m_inputs'][2:7]:
 di,do=copy.deepcopy(di0),copy.deepcopy(do0);di.update(m_id=guid(),m_name=p['m_name'],m_sourceID=ports[p['m_name']],m_dataID=p['m_id']);do.update(m_id=guid(),m_name=p['m_name'],m_dataID=p['m_id']);bind['m_dynamicDataInputSockets'].append(di);bind['m_outputAsyncExecSocket']['m_dataOutputSockets'].append(do)
casts=[clone('TypedValueVisualFunctionLibrary_TryCastToInt',f'Cast {i}') for i in range(5)]
for c,o in zip(casts,bind['m_outputAsyncExecSocket']['m_dataOutputSockets']):c['m_dataInValue']['m_sourceID']=o['m_id']
adds=[];ands=[]
for i in range(4):
 d=clone('GeneralVisualFunction_Add_int_int_int',f'Sum {i}');d['m_dataInA']['m_sourceID']=casts[0]['m_dataOutIntValue']['m_id'] if i==0 else adds[-1]['m_dataOutInt32']['m_id'];d['m_dataInB']['m_sourceID']=casts[i+1]['m_dataOutIntValue']['m_id'];adds.append(d)
 a=clone('GeneralVisualFunction_AND',f'Validate {i}');a['m_dataInA']['m_sourceID']=casts[0]['m_dataOutBoolean']['m_id'] if i==0 else ands[-1]['m_dataOutBoolean']['m_id'];a['m_dataInB']['m_sourceID']=casts[i+1]['m_dataOutBoolean']['m_id'];ands.append(a)
branch=clone('GeneralVisualFunction_Branch','All Valid');branch['m_dataInCondition']['m_sourceID']=ands[-1]['m_dataOutBoolean']['m_id']
conv=clone('TypedValueVisualFunctionLibrary_IntToTypedValue','Sum Value');conv['m_dataInValue']['m_sourceID']=adds[-1]['m_dataOutInt32']['m_id']
failconv=clone('TypedValueVisualFunctionLibrary_IntToTypedValue','Missing Value');failconv['m_dataInValue']['m_defaultSocketValue']['m_value']=-1
success=clone('VisualFunctionLibrary_SetBinding','Publish Sum');failure=clone('VisualFunctionLibrary_SetBinding','Publish Missing')
for d,v in [(success,conv),(failure,failconv)]:
 d['m_dataInTarget']['m_sourceID']=ports['Target'];d['m_dataInDest']['m_sourceID']=ports['Destination'];d['m_dataInValue']['m_sourceID']=v['m_dataOutTypedValue']['m_id']
def link(a,k,b,q='m_execInExecInput'):a[k]['m_destinationID']=b[q]['m_id']
link(entry,'m_outputExecSocket',bind,'m_inputExecSocket');link(bind,'m_outputAsyncExecSocket',casts[0])
chain=casts+ands+[branch]
for a,b in zip(chain,chain[1:]):link(a,'m_execOutExecOutput',b)
link(branch,'m_execOutTrue',success);link(branch,'m_execOutFalse',failure)
tree['m_nodes']=[{'rid':r['rid']} for r in fr];tree['references']={'version':2,'RefIds':fr}
known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in af.ref_types};needed={(r['type']['class'],r['type']['ns'],r['type']['asm']) for r in fr}
for t in native.assets_file.ref_types:
 k=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
 if k in needed and k not in known:af.ref_types.append(copy.copy(t));known.add(k)
assert needed<=known
fo=copy.copy(obs[-910000000000302]);fo.path_id=FP;af.objects[FP]=fo;fo.save_typetree(tree)
bundle=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=bundle.read_typetree();bannerkey=next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==B);start=len(meta['m_PreloadTable']);meta['m_PreloadTable'].extend([copy.deepcopy(tree['m_Script']),{'m_FileID':0,'m_PathID':FP}]);meta['m_Container'].append((FG,{'preloadIndex':start,'preloadSize':2,'asset':{'m_FileID':0,'m_PathID':FP}}));meta['m_Container'].sort(key=lambda x:x[0])
doc=obs[B].read_typetree();sheet=obs[S].read_typetree();old_doc=copy.deepcopy(doc);old_sheet=copy.deepcopy(sheet);refs={r['rid']:r for r in doc['references']['RefIds']}
def string(s):
 b=s.encode();assert len(b)<128;return bytes([len(b)])+b
def encode(args):
 b=bytearray([len(args)])
 for c,v in args:
  p=string(c)+v;b.extend(struct.pack('<i',len(p)));b.extend(p)
 return list(b)
def decode(a):
 b=bytes(a);p=1;out=[]
 for _ in range(b[0]):
  n=struct.unpack_from('<i',b,p)[0];p+=4;z=b[p:p+n];p+=n;length=z[0];out.append((z[1:1+length].decode(),z[1+length:]))
 assert p==len(b);return out
BC='SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]'
def vf(g,args):return {'m_target':{'m_guid':g},'m_inputs':{'m_variable':{'m_argumentBytes':encode(args)}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
def val(pool,typ,v):
 if v not in sheet[pool]:sheet[pool].append(v)
 return {'m_ValueType':typ,'valueIndex':sheet[pool].index(v)}
def px(v):return val('dimensions',3,{'unit':1,'value':float(v)})
def pct(v):return val('dimensions',3,{'unit':2,'value':float(v)})
def en(v):return val('strings',7,v)
def num(v):return val('floats',2,float(v))
def prop(k,*v):return {'m_Id':k,'m_CustomName':'','m_Line':-1,'m_Values':list(v)}
def rule(ps):
 i=len(sheet['m_Rules']);sheet['m_Rules'].append({'m_ComplexSelectors':[],'m_Properties':ps,'line':-1});return i
zero=[prop(262150,px(0)),prop(262151,px(0))]
full=[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131105,pct(100)),prop(131087,pct(100))]+zero
rowrule=rule([prop(131084,num(1)),prop(131085,num(1)),prop(131082,px(0)),prop(131097,px(0)),prop(131087,px(44)),prop(131083,en('row')),prop(131073,en('flex-end')),prop(131088,en('space-between')),prop(131092,px(8))]+zero)
cellrule=rule([prop(131084,num(1)),prop(131085,num(1)),prop(131082,px(0)),prop(131097,px(0)),prop(131087,px(60)),prop(131091,px(1)),prop(131092,px(1))]+zero)
switchrule=rule(full)
# label overlay sits in the existing image's plaque.
plaque=rule([prop(131102,en('absolute')),prop(131089,pct(10)),prop(131104,pct(72)),prop(131105,pct(80)),prop(131087,pct(18)),prop(131083,en('row')),prop(131073,en('center'))]+zero)
def txtrule(width,size,color):return rule([prop(131105,pct(width)),prop(131087,pct(100)),prop(131097,px(0)),prop(65537,px(size)),prop(65546,en('middle-center')),prop(65552,en('nowrap')),prop(65536,val('colors',4,dict(zip(['r','g','b','a'],color))))]+zero)
labelrule=txtrule(63,9,(1,1,1,1));valuerule=txtrule(37,11,(1,.4375,.4375,1))
integer=json.loads((R/'native-integer-text-template-v36.json').read_text());search=next(x['tree'] for x in json.loads((R/'sum-ui-template-v36.json').read_text()) if x['name']=='GlobalSearchCard');sr={r['rid']:r for r in search['references']['RefIds']};settersd=sr[1016];setternode=next(r for r in sr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==1016)
new=[];rid=max(refs)+1;eid=1903900000
def pair(nt,st,parent,name,ri):
 global rid,eid
 n,s=copy.deepcopy(nt),copy.deepcopy(st);n['rid'],s['rid']=rid,rid+1;rid+=2;n['data'].update(m_Id=eid,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=ri,m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[],m_SkipClone=0);s['data'].update(uxmlAssetId=eid,name=name,name_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);eid+=1;refs[n['rid']]=n;refs[s['rid']]=s;new.extend([n,s]);return n,s
def child(parent,node):refs[parent]['data']['m_Children'].append({'rid':node['rid']})
rows=[('进攻','ATT',38,['Passing','Dribbling','Finishing','FirstTouch','Movement']),('防守','DEF',48,['Tackling','Marking','Heading','Positioning','Anticipation']),('技术','TCN',28,['Technique','Passing','FirstTouch','Vision','Crossing']),('精神','SPT',18,['Concentration','Decisions','Leadership','Determination','Bravery']),('身体','SPD',78,['Acceleration','Pace','Agility','Balance','Strength']),('定位球','KIK',68,['PenaltyTaking','Corners','LongThrows','FreeKicks','LongShots']),('合作','FED',58,['WorkRate','Teamwork','Leadership','Professionalism','Sportsmanship'])]
refs[1214]['data']['m_RuleIndex']=rowrule;refs[1214]['data']['m_Children']=[];refs[1215]['data']['name']='ReportSevenAttributeBadges'
# Native card embeds image textures in global; do the same for new icons.
bg=UnityPy.load(str(AA/'StandaloneWindows64/ui-backgrounds_assets_common.bundle'));bo={o.path_id:o for o in bg.objects};imgtemplate=obs[-910000000000003]
for pid in range(-910000000000087,-910000000000017):
 assert pid not in obs;src=bo[pid];o=copy.copy(src);o.assets_file=af;o.type_id=imgtemplate.type_id;o.serialized_type=imgtemplate.serialized_type;af.objects[pid]=o
 # The source texture data is inline; verify no uncarried streamed resource.
 t=src.read_typetree();assert not t.get('m_StreamData',{}).get('size',0);o.save_typetree(t)
badge_colors={'ATT':(1,.4375,.4375,1),'DEF':(.25,.75,1,1),'TCN':(1,.8125,.25,1),'SPT':(.875,.375,1,1),'SPD':(.25,1,.75,1),'KIK':(.25,.9375,1,1),'FED':(1,1,1,1)}
checks=[]
for title,code,start,attrs in rows:
 paths=['person.attribute'+a.lower()+'.AttributeMinValue' for a in attrs];dest='Report'+code+'Total'
 cell,sd=pair(setternode,settersd,1214,'Report'+code+'Badge',cellrule);child(1214,cell);sd['data'].update(ValueVariables=[{'m_name':dest,'m_scopeValue':{'m_serializedData':'Int|-1|'}}],ReferenceVariables=[],ValueVariables_UxmlAttributeFlags=1,ReferenceVariables_UxmlAttributeFlags=0,BindFunction=[vf(FG,[(BC,b'\x01'+string(p)) for p in paths+[dest]])],BindFunction_UxmlAttributeFlags=1)
 # Nine nested binary switches: child0 <= upper bound, child1 remaining tiers.
 parent=cell['rid']
 for tier in range(10):
  if tier<9:
   sw,ss=pair(refs[1166],refs[1167],parent,f'{code}Above{(tier+1)*10}',switchrule);child(parent,sw)
   a=decode(ss['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);a[1]=(a[1][0],struct.pack('<i',(tier+1)*10));a[2]=(BC,b'\x01'+string(dest));ss['data']['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(a);parent=sw['rid']
  pid=-910000000000000-start-tier;asset=val('assets',6,{'m_FileID':0,'m_PathID':pid});ir=rule(full+[prop(458753,asset),prop(262153,en('scale-to-fit'))]);im,ims=pair(refs[1174],refs[1175],parent,f'{code}{tier+1:02}',ir);child(parent,im)
  # next switch will be second child of this switch; final tier is its second image.
 plate,ps=pair(refs[1174],refs[1175],cell['rid'],code+'Plaque',plaque);child(cell['rid'],plate)
 lab,ls=pair(integer['node'],integer['sd'],plate['rid'],code+'Title',labelrule);child(plate['rid'],lab);ls['data']['TextBinding']['m_kind']=0;ls['data']['TextBinding']['m_visualFunction']=vf('',[]);ls['data'].update(text=title,text_UxmlAttributeFlags=1,DebugDisplay=title)
 numel,ns=pair(integer['node'],integer['sd'],plate['rid'],code+'Total',txtrule(37,11,badge_colors[code]));child(plate['rid'],numel);a=decode(ns['data']['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);payload=a[1][1];length=payload[2];a[1]=(a[1][0],b'\x01\x01'+string(dest)+payload[3+length:]);ns['data']['TextBinding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(a);ns['data']['DebugDisplay']='--'
 checks.append({'title':title,'code':code,'paths':paths,'sum':dest,'images':[(-910000000000000-start-i) for i in range(10)]})
# Remove obsolete movement text reference pair.
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in [1216,1217]]+new
obs[B].save_typetree(doc);obs[S].save_typetree(sheet);bundle.save_typetree(meta)
OUT.mkdir(exist_ok=True);destdir=OUT/'aa/StandaloneWindows64';destdir.mkdir(parents=True,exist_ok=True);(destdir/N).write_bytes(e.file.save(packer='lz4'))
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(catalog);newcat=cat.add_key_location(FG,cat.locations('a82e4cf3a34b1ae41b85cacd4f63208c')[0],cat.locations(bannerkey)[0]);(OUT/'aa/catalog.bin').write_bytes(newcat)
# Reload data, verify unrelated assets and nested image cardinality.
saved={o.path_id:o for o in UnityPy.load(str(destdir/N)).objects};assert saved[B].read_typetree()==doc;assert saved[S].read_typetree()==sheet;assert saved[FP].read_typetree()==tree
for i,h in hashes.items():
 if i not in [B,S,bundle.path_id]:assert sha(saved[i].get_raw_data())==h,i
rr={r['rid']:r for r in doc['references']['RefIds']};seen=set()
def visit(i):
 assert i not in seen;seen.add(i)
 for c in rr[i].get('data',{}).get('m_Children',[]):assert rr[c['rid']]['data']['m_Parent']['rid']==i;visit(c['rid'])
visit(doc['m_VisualTree']['rid'])
for r in new:
 if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement':assert len(r['data']['m_Children'])==2
for v in range(0,101):assert sum(1 for i in range(10) if (i==0 or v>i*10) and (i==9 or v<=(i+1)*10))==1
backup=OUT/'回退/aa/StandaloneWindows64';backup.mkdir(parents=True,exist_ok=True);(backup/N).write_bytes(source);(OUT/'回退/aa/catalog.bin').write_bytes(catalog)
m={'version':39,'categories':checks,'source_global':sha(source),'global':sha((destdir/N).read_bytes()),'source_catalog':sha(catalog),'catalog':sha(newcat),'function_guid':FG,'height':60,'tier_bounds':'0-10,11-20,...,91-100','game_runtime_verified':False,'installed':False};(OUT/'修改记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
for rollback in [False,True]:
 folder='回退/aa' if rollback else 'aa';back='aa' if rollback else '回退/aa';gh=m['global'] if rollback else m['source_global'];ch=m['catalog'] if rollback else m['source_catalog']
 script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetAA = '{AA}'
$targetBundle = Join-Path $targetAA 'StandaloneWindows64/{N}'
$targetCatalog = Join-Path $targetAA 'catalog.bin'
if ((Get-FileHash -LiteralPath $targetBundle).Hash.ToLower() -ne '{gh}') {{ throw 'Global version mismatch.' }}
if ((Get-FileHash -LiteralPath $targetCatalog).Hash.ToLower() -ne '{ch}') {{ throw 'Catalog version mismatch.' }}
try {{
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{folder}/StandaloneWindows64/{N}') -Destination $targetBundle -Force
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{folder}/catalog.bin') -Destination $targetCatalog -Force
}} catch {{
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{back}/StandaloneWindows64/{N}') -Destination $targetBundle -Force
 Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{back}/catalog.bin') -Destination $targetCatalog -Force
 throw
}}
Write-Host 'Complete.'
'''
 (OUT/('回退.ps1' if rollback else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V39 七项属性徽章。每项五属性求和，使用 AttributeMinValue（范围属性取下限）。\n顺序：进攻、防守、技术、精神、身体、定位球、合作。\n档位：0-10第1张、11-20第2张，依此类推，91-100第10张。\n字体中文，图片与数值共用同一个局部总和。徽章高60px，均分Actions左侧空间。\n复制了游戏当前backgrounds内70张纹理到global，保持原纹理内容与ID，不依赖导入JSON。\n退出游戏后运行安装.ps1；回退.ps1恢复V38。\n原visualfunctions及背景包不修改，catalog新增私有函数索引。游戏实测待验证。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for p in OUT.rglob('*'):
  if p.is_file():z.write(p,p.relative_to(OUT))
print(json.dumps({'global':m['global'],'catalog':m['catalog'],'new_refs':len(new),'function_nodes':len(fr),'unrelated_assets_verified':len(hashes)-3}))

