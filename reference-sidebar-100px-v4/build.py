"""Reference-based public navigation sidebar. Writes only inside this folder."""
from pathlib import Path
import ast,copy,hashlib,importlib.util,json,shutil,struct,sys,uuid
OUT=Path(__file__).resolve().parent;R=OUT.parent;REF=Path('K:/桌面/Skin files')
location=json.loads((R/'current-game-location.json').read_text('utf8'));GAME=Path(location['bundle_root']);SKIN=Path(location['skin_packages'])
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for name,wanted in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-card-six-ratings.py',{'validate_ui'})]:
 a=ast.parse((R/name).read_text('utf8'));exec(compile(ast.Module(body=[n for n in a.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in wanted],type_ignores=[]),name,'exec'))
TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';D='ui-styles_assets_default.bundle'
sources={GAME/n:(GAME/n).read_bytes() for n in [W,G,D]}
protected={str(p):sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.iterdir() if p.is_file()}
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',R/'AGENTS.md',R/'current-game-location.json',R/'current-custom-textures.json',R/'reserved-texture-ids.json']:
 protected[str(p)]=sha(p.read_bytes())
reference_hashes={str(p):sha(p.read_bytes()) for p in REF.glob('*.bundle')}
envs={n:UnityPy.load(sources[GAME/n]) for n in [W,G,D]};objects={n:{o.path_id:o for o in e.objects} for n,e in envs.items()}
hashes={n:{pid:sha(o.get_raw_data()) for pid,o in oo.items()} for n,oo in objects.items()};expected={n:{} for n in envs}
def named(b,n):return next(o for o in objects[b].values() if o.type.name=='MonoBehaviour' and o.peek_name()==n)
def save(b,o,d):o.save_typetree(d);expected[b][o.path_id]=copy.deepcopy(d)
def clone(b,source,pid,d):
 assert pid not in objects[b]
 o=copy.copy(source);o.path_id=pid;o.data=None;o._read_until=None;o.assets_file.objects[pid]=o;objects[b][pid]=o;save(b,o,d);return o
def refs(d):return {x['rid']:x for x in d['references']['RefIds']}
def serial(rr,i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def closure(rr,root):
 seen=set()
 def walk(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    i=v['rid']
    if i in rr and i not in seen:seen.add(i);walk(rr[i].get('data',{}))
   else:
    for k,x in v.items():
     if k!='m_Parent':walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk({'rid':root});return seen

# Confirm the donor mechanism before adapting it. Never install its bundles wholesale.
re=UnityPy.load(str(REF/W));ro={o.path_id:o for o in re.objects}
rp=next(o.read_typetree() for o in re.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='PrimaryNavigationBar');rr=refs(rp)
donor=next(i for i in rr if serial(rr,i).get('name')=='FMETSideBar')
assert rr[donor]['data']['m_TemplateAlias']=='MenuBar' and rr[donor]['data']['m_Parent']['rid']==1002
ref_menu=next(o.read_typetree() for o in re.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='MenuBar')
assert any(x.get('data',{}).get('name')=='DirectLinks' for x in ref_menu['references']['RefIds'])

ROW=-980000000041001;ROWSTYLE=-980000000041002;SIDE=-980000000041003;SIDESTYLE=-980000000041004
retired={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}|{-910000000000001,-910000000000002,-910000000000146}
assert not ({ROW,ROWSTYLE,SIDE,SIDESTYLE}&retired)
ROWGUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/reference-sidebar-v4/bookmark-row').hex
SIDEGUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/reference-sidebar-v4/bookmark-sidebar').hex
rowobj=named(W,'BookmarkButton');row=rowobj.read_typetree();rr=refs(row);oldrowsid=row['inlineSheet']['m_PathID'];rowstyle=objects[W][oldrowsid].read_typetree();st=Styles(rowstyle)
row.update(m_Name='TFReferenceBookmarkRow',inlineSheet={'m_FileID':0,'m_PathID':ROWSTYLE});rowstyle['m_Name']='TFReferenceBookmarkRow_Style'
assert serial(rr,1016)['Binding']['m_direct']['Path']['m_path']=='gameworldsubtabsandbookmarks.AreBookmarkLabelsVisible'
serial(rr,1016)['Binding']['m_direct']['Path']['m_path']='const.true'
for i in [1001,1006,1009]:
 st.edit(rr[i],[st.p(131105,st.px(100)),st.p(131095,st.px(100)),st.p(131097,st.px(0)),st.p(131087,st.px(40)),st.p(131085,st.num(0)),st.p(131091,st.px(0)),st.p(131092,st.px(0))])
st.edit(rr[1009],[st.p(131099,st.px(4)),st.p(131100,st.px(4)),st.p(131088,st.en('flex-start'))])
st.edit(rr[1012],[st.p(131105,st.pct(100)),st.p(131097,st.px(0)),st.p(458768,st.en('hidden'))])
st.edit(rr[1016],[st.p(131084,st.num(1)),st.p(131085,st.num(1)),st.p(131097,st.px(0)),st.p(131095,st.px(68)),st.p(458768,st.en('hidden'))])
st.edit(rr[1022],[st.p(65537,st.px(11)),st.p(131105,st.pct(100)),st.p(196609,st.en('ellipsis')),st.p(65552,st.en('nowrap'))])
validate_ui(row,rowstyle);clone(W,rowobj,ROW,row);clone(W,objects[W][oldrowsid],ROWSTYLE,rowstyle)

# Keep the entire native bookmark block AND its required BindingExpect ancestor.
secobj=named(W,'SecondaryNavigationBar');side=secobj.read_typetree();sr=refs(side);sideorigstyle=objects[W][side['inlineSheet']['m_PathID']];sheet=sideorigstyle.read_typetree();st=Styles(sheet)
keep=closure(sr,1046)|{1000,1001,sr[1001]['data']['m_SerializedData']['rid']}
side['references']['RefIds']=[x for x in side['references']['RefIds'] if x['rid'] in keep];sr=refs(side)
sr[1001]['data']['m_Children']=[{'rid':1046}];sr[1046]['data']['m_Parent']={'rid':1001}
params=serial(sr,1001)['Parameters'];drag=next(p for p in params if p['name']=='bookmark-drag-key')
assert drag['defaultValue']['m_scopeValue']['m_serializedData']=='String|bookmark-reorder|'
side.update(m_Name='TFReferenceBookmarkSidebar',inlineSheet={'m_FileID':0,'m_PathID':SIDESTYLE});sheet['m_Name']='TFReferenceBookmarkSidebar_Style'
empty={'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
for i in [1046,1178]:serial(sr,i)['BindFunction']=copy.deepcopy(empty)
for i in [1001,1046,1071,1091,1129,1178]:
 sr[i]['data']['m_Classes']=[]
 st.edit(sr[i],[st.p(131083,st.en('column')),st.p(131105,st.px(100)),st.p(131097,st.px(0)),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131088,st.en('flex-start'))])
st.edit(sr[1072],[st.p(131081,st.en('none'))])
li=serial(sr,1229);li['Binding']={'m_kind':1,'m_direct':{'Path':{'m_path':'gameworldsubtabsandbookmarks.CurrentSelectedBookmarksList'},'Nullable':0},'m_visualFunction':copy.deepcopy(empty)}
li['RowTemplate']['m_AssetGUID']=ROWGUID
for k,v in {'Direction':0,'ScrollViewMode':0,'FixedElementSize':40.0,'DynamicElements':0,'HorizontalScrollerVisibility':2,'VerticalScrollerVisibility':0}.items():li[k]=v;li[k+'_UxmlAttributeFlags']=1
st.edit(sr[1229],[st.p(131105,st.px(100)),st.p(131087,st.px(560)),st.p(131085,st.num(0))])
sr[1073]['data']['m_Classes']=['ui-concepts-chevron-down_small','popupwidget-hover','bookmarks-button'];st.edit(sr[1073],[st.p(131105,st.px(100)),st.p(131087,st.px(32)),st.p(131088,st.en('center'))])
used={x.get('data',{}).get('m_TemplateAlias') for x in sr.values()}-{None,''};side['m_Usings']=[u for u in side['m_Usings'] if u['alias'] in used]
validate_ui(side,sheet);clone(W,secobj,SIDE,side);clone(W,sideorigstyle,SIDESTYLE,sheet)

# Follow the reference: a second navigation instance under the public MainNav.
primary=named(W,'PrimaryNavigationBar');pd=primary.read_typetree();pr=refs(pd)
td=named(W,'OverviewTitleBar').read_typetree();tr=refs(td);el=copy.deepcopy(tr[1006]);ser=copy.deepcopy(tr[el['data']['m_SerializedData']['rid']])
ei=max(pr)+1;si=ei+1;eid=1910314100;assert eid not in {x.get('data',{}).get('m_Id') for x in pr.values()}
el['rid']=ei;ser['rid']=si
el['data'].update(m_Id=eid,m_Parent={'rid':1002},m_Children=[],m_RuleIndex=-1,m_Classes=['tf-reference-sidebar'],m_SerializedData={'rid':si},m_TemplateAlias='TFReferenceSidebar',m_SerializedDataOverride=[],m_AttributeOverrides=[],m_SlotUsages=[])
ser['data'].update(uxmlAssetId=eid,name='TFReferenceSidebar',name_UxmlAttributeFlags=1,templateId='TFReferenceSidebar',templateId_UxmlAttributeFlags=1)
pd['references']['RefIds'].extend([el,ser]);pr[1002]['data']['m_Children'].append({'rid':ei});pd['m_Usings'].append({'alias':'TFReferenceSidebar','path':SIDEGUID,'asset':{'m_FileID':0,'m_PathID':0}})
pr[1006]['data']['m_Classes'].append('tf-reference-header-controls')
ps=objects[W][pd['inlineSheet']['m_PathID']].read_typetree();validate_ui(pd,ps);save(W,primary,pd)
# Like the donor, permit the sidebar to extend beyond the fixed-height title bar.
title=named(W,'OverviewTitleBar');td=title.read_typetree();tr=refs(td);tsid=td['inlineSheet']['m_PathID'];ts=objects[W][tsid].read_typetree();Styles(ts).edit(tr[1001],[Styles(ts).p(458768,Styles(ts).en('visible'))]);validate_ui(td,ts);save(W,title,td);save(W,objects[W][tsid],ts)

# Native boolean->USS binding changes one class on the common document container.
# This scopes the layout to a loaded management game, away from match viewing/flow.
def s7(s):
 b=s.encode('utf8');n=len(b);out=bytearray()
 while n>=128:out.append((n&127)|128);n>>=7
 return bytes(out)+bytes([n])+b
def visualargs(items):return bytes([len(items)])+b''.join(struct.pack('<I',len(x))+x for x in items)
def argstr(s):return s7('SI.VisualScripting.StringVisualArg')+b'\x01'+s7(s)
def argbool(b):return s7('SI.VisualScripting.BooleanVisualArg')+bytes([bool(b)])
conditions=[('app.GameStarted',False),('game.HumanInitialised',False),('game.IsViewingMatch',True),('game.IsDuringMatch',True)]
argsbody=s7('SI.VisualScripting.StructListVisualArg`1[SI.Bindable.BooleanArg]')+bytes([len(conditions)])+b''.join(b'\x01'+s7(path)+bytes([invert]) for path,invert in conditions)
enum=s7('SI.VisualScripting.EnumVisualArg`1[SI.VisualScripting.VisibleFunctions+LogicOperator]')+struct.pack('<i',0)
gatefunc={'m_target':{'m_guid':'678bbaf2a5da6f54ab4aa7b453f7d150'},'m_inputs':{'m_variable':{'m_argumentBytes':list(visualargs([argsbody,enum,argstr('tf-reference-sidebar-active'),argbool(True),argbool(False)]))}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}
main=named(G,'MainUIDocument');md=main.read_typetree();mr=refs(md);msid=md['inlineSheet']['m_PathID'];ms=objects[G][msid].read_typetree();mst=Styles(ms)
assert not mr[1000]['data']['m_Children']
native=refs(secobj.read_typetree());gate=copy.deepcopy(native[1046]);gateser=copy.deepcopy(native[gate['data']['m_SerializedData']['rid']]);gate['rid']=2000;gateser['rid']=2001
gate['data'].update(m_Id=1910314200,m_Parent={'rid':1000},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_SerializedData={'rid':2001})
gateser['data'].update(uxmlAssetId=1910314200,name='TFReferenceSidebarScope',name_UxmlAttributeFlags=1,BindFunction=gatefunc,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
mst.edit(gate,[mst.p(131102,mst.en('absolute')),mst.p(131105,mst.px(0)),mst.p(131087,mst.px(0))]);md['references']['RefIds'].extend([gate,gateser]);mr[1000]['data']['m_Children']=[{'rid':2000}]
validate_ui(md,ms);save(G,main,md);save(G,objects[G][msid],ms)

# Add only scoped rules; do not import the donor's page scale/inverse-match scale.
styleobj=named(D,'AlwaysAppliedStyleSheet');dd=styleobj.read_typetree();oldrulecount=len(dd['m_Rules']);st=Styles(dd)
active=[('tf-reference-sidebar-active',3)]
def rule(chain,props):
 i=len(dd['m_Rules']);sel=[{'m_Parts':[{'m_Value':n,'m_Type':t} for n,t in part],'m_PreviousRelationship':0 if j==0 else 2} for j,part in enumerate(chain)]
 specificity=1+sum(100 if t==6 else 10 for p in chain for _,t in p)
 dd['m_Rules'].append({'m_ComplexSelectors':[{'m_Specificity':specificity,'m_Selectors':sel,'ruleIndex':i}],'m_Properties':props,'line':-1})
rule([[('tf-reference-sidebar',3)]],[st.p(131081,st.en('none'))])
rule([active,[('tf-reference-sidebar',3)]],[st.p(131081,st.en('flex')),st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131104,st.px(0)),st.p(131105,st.px(100)),st.p(131087,st.px(3000)),st.p(131097,st.px(0)),st.p(131096,st.px(0)),st.p(458752,st.h(4,{'r':0.03125,'g':0.046875,'b':0.0625,'a':1.0}))])
for name in ['MenuBody','ReportBody','Report']:
 rule([active,[(name,6)]],[st.p(131089,st.px(100)),st.p(131103,st.px(0)),st.p(131105,{'m_ValueType':1,'valueIndex':3})])
rule([active,[('tf-reference-header-controls',3)]],[st.p(131099,st.px(100))])
rule([active,[('SecondaryNavigationBar',6)]],[st.p(131099,st.px(100))])
rule([active,[('SecondaryNavigationBar',6)],[('Bookmarks',6)]],[st.p(131081,st.en('none'))])
save(D,styleobj,dd)

# Register both actual VTA objects, their preload spans, and the preload label.
ab=next(o for o in objects[W].values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
for guid,pid,sid in [(ROWGUID,ROW,ROWSTYLE),(SIDEGUID,SIDE,SIDESTYLE)]:
 assert all(k!=guid for k,_ in meta['m_Container'])
 span=[{'m_FileID':0,'m_PathID':sid},{'m_FileID':0,'m_PathID':pid}]
 meta['m_Container'].append((guid,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':pid}}));meta['m_PreloadTable'].extend(span)
meta['m_Container'].sort(key=lambda x:x[0]);save(W,ab,meta)
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catbefore=(GAME.parent/'catalog.bin').read_bytes();cat=cm.Catalog(catbefore)
for guid,sourceguid in [(ROWGUID,'55c5e407237e29e43a7ee0feb446fea9'),(SIDEGUID,'f7baf58db4dbb2940be4a343961ba9ea')]:
 candidates=[x for x in cat.locations(sourceguid) if cat.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'];assert len(candidates)==1
 cat=cm.Catalog(cat.add_key_location(guid,candidates[0],candidates[0]))
labelindex=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GameWorldVisualTreeAssetPreload');keyobj,locset=cat.key_records[labelindex];locs=[x[0] for x in cat.array(locset,'I')]+cat.locations(ROWGUID)+cat.locations(SIDEGUID)
records=list(cat.key_records);records[labelindex]=(keyobj,cat.append(b''.join(struct.pack('<I',x) for x in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*x) for x in records),True));catout=bytes(cat.data)
for guid in [ROWGUID,SIDEGUID]:
 c=cm.Catalog(catout);ll=c.locations(guid)[0];assert ll in [x[0] for x in c.array(c.key_records[labelindex][1],'I')]
 assert c.location(c.location(ll)['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)

# Round-trip verification: all untouched objects must remain byte-identical.
outputs={};checks=[]
for n,e in envs.items():
 raw=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objects[n])
 for pid,o in saved.items():
  if pid in expected[n]:assert o.read_typetree()==expected[n][pid],(n,pid)
  else:assert sha(o.get_raw_data())==hashes[n][pid],(n,pid)
 outputs[GAME/n]=raw;checks.append({'bundle':n,'changed_objects':[{'path_id':pid,'name':d.get('m_Name')} for pid,d in expected[n].items()]})
outputs[GAME.parent/'catalog.bin']=catout;outputs[GAME.parent/'catalog.hash']=hashlib.md5(catout).hexdigest().encode('ascii')
assert all('Match' not in x['name'] for c in checks for x in c['changed_objects'] if x['name'])
for p,h in protected.items():assert sha(Path(p).read_bytes())==h,p
for p,h in reference_hashes.items():assert sha(Path(p).read_bytes())==h,p
(OUT/'packages').mkdir(exist_ok=True);(OUT/'backup-game').mkdir(exist_ok=True);tx=[]
for target,data in outputs.items():
 source=OUT/'packages'/target.name;backup=OUT/'backup-game'/target.name;source.write_bytes(data);before=target.read_bytes();backup.write_bytes(before)
 tx.append({'target':str(target),'source':str(source),'backup':str(backup),'before':sha(before),'after':sha(data)})
targets=set(outputs);installprotected={p:h for p,h in protected.items() if Path(p) not in targets}
record={'version':'Reference public navigation sidebar 100px V4','installed':False,'runtime_verified':False,'width_px':100,'row_height_px':40,'method':'Separate template instance under PrimaryNavigationBar/MainNav, matching FMETSideBar mounting','content':'Live native CurrentSelectedBookmarksList, preserving original click and selection events','native_context_preserved':'SecondaryNavigationBar BindingExpect including bookmark-drag-key default','preload_label':'GameWorldVisualTreeAssetPreload','row_guid':ROWGUID,'sidebar_guid':SIDEGUID,'new_ids':[ROW,ROWSTYLE,SIDE,SIDESTYLE],'page_templates_modified':False,'match_templates_modified':False,'settings_bundle_modified':False,'reference_page_scaling_imported':False,'reference_match_scaling_imported':False,'resolution_configuration_modified':False,'management_gate_conditions':conditions,'changed_bundles':checks,'reference_files':reference_hashes,'protected_sha256':installprotected,'source_preparation_hashes':protected,'known_limitations':['Not tested in game. Global scope binding and match-flow boolean coverage require runtime validation.','Sidebar background uses an absolute 3000px element as in the reference; the list viewport is 560px and scrolls. It does not resize the public layer or change page scale.']}
(OUT/'manifest.json').write_text(json.dumps(record,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');shutil.copyfile(R/'install-independent-resource-patch.py',OUT/'installer.py')
for name,flag in [('install',''),('restore',' --restore')]:
 (OUT/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed.' }\n",'utf-8-sig')
(OUT/'README.md').write_text('参考皮肤公共导航挂载方式的100px书签侧栏 V4\n\n参考：K:/桌面/Skin files。其PrimaryNavigationBar/MainNav增加FMETSideBar模板实例，内容来自MenuBar固定链接；本版沿用公共模板实例挂载方式，内容改为用户自己的原生书签列表，含文字、原生点击、选中和编辑入口。\n\n保留完整bookmark-drag-key上下文，新模板和书签行同时登记GUID与GameWorldVisualTreeAssetPreload标签。没有修改各页面模板，没有导入参考皮肤的整页缩放或比赛反向缩放，没有修改settings包、分辨率配置和原皮肤工程。\n\n此为独立待测试成品，尚未安装。install.ps1试装，退出游戏后restore.ps1回退。需要实际验证公共根绑定、连续书签跳转和赛前/赛中/赛后状态，不能将静态校验视为运行验证。\n','utf8')
print(json.dumps({'output':str(OUT),'installed':False,'native_bookmark_context_preserved':True,'preload_label_verified':True,'page_templates_modified':False,'match_templates_modified':False,'settings_modified':False,'runtime_verified':False},ensure_ascii=False))
