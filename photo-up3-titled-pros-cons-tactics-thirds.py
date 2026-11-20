from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('photo-up3-titled-pros-cons-tactics-thirds-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))

src=ast.parse((R/'equal-role-comparison-biography-scout-icons.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'refs','sd','named','add_pair'}],type_ignores=[]),'tree helpers','exec'))
auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
ROW=-940000000006000;MODULE=-940000000006002;MODULE_KEY='fdc9e9e0d3085013a4ff4b5618c500a3'
native_role=objs[G][-4928795461599700197].read_typetree();nrr=refs(native_role)
native_row=objs[G][-294675314297081795].read_typetree();nrow=refs(native_row)
native_module=objs[G][7391060340652509499].read_typetree();nm=refs(native_module)
def serial(rr0,i):return rr0[rr0[i]['data']['m_SerializedData']['rid']]
def save(n,pid,doc,sid,sheet):
 validate_ui(doc,sheet);objs[n][pid].save_typetree(doc);objs[n][sid].save_typetree(sheet);changed[n][pid]=doc;changed[n][sid]=sheet
# The previously isolated 20px icon row gains the native popup tooltip, rather than inline text.
doc=objs[G][ROW].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
tooltip=add_pair(nrr[1034],serial(nrr,1034),1006,'OverviewProConIconTooltip')
text=add_pair(nrow[1009],serial(nrow,1009),tooltip,'OverviewProConIconDescription')
rr[text]['data']['m_Classes']=['body-md','global-text-primary']
override(rr[text]['data'],[prop(131097,px(0)),prop(131095,px(280)),prop(65552,en('normal')),prop(262150,px(0))])
assert sd(text)['TextBinding']['m_direct']['Path']['m_path']=='binding.ProConsLongString'
for i,r in old.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
save(G,ROW,doc,sid,sheet)
# Two equal icon columns with the scouting report's original translated headings and thumb symbols.
doc=objs[G][MODULE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
def clone_heading(i,parent):
 name=serial(nm,i)['data'].get('name','')
 new=add_pair(nm[i],serial(nm,i),parent,'OverviewScout_'+name)
 rr[new]['data']['m_Classes']=copy.deepcopy(nm[i]['data'].get('m_Classes',[]))
 for c in nm[i]['data'].get('m_Children',[]):clone_heading(c['rid'],new)
 return new
pros_head=clone_heading(1007,1004);cons_head=clone_heading(1010,1005)
rr[1004]['data']['m_Children']=[{'rid':pros_head},{'rid':1008}];rr[1005]['data']['m_Children']=[{'rid':cons_head},{'rid':1011}]
for i in [1001,1002]:override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131073,en('stretch')),prop(262150,px(0)),prop(262151,px(0))])
override(rr[1002]['data'],[prop(131083,en('row'))])
for i in [1004,1005]:override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131083,en('column')),prop(131073,en('stretch')),prop(262150,px(0)),prop(131099,px(4)),prop(131100,px(4))])
for i in [pros_head,cons_head]:
 rr[i]['data']['m_Classes']=['row-direction-normal','align-items-center']
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(26)),prop(131096,px(26)),prop(131094,px(26)),prop(131084,num(0)),prop(131085,num(0)),prop(131090,px(4)),prop(262151,px(0))])
for i in [1008,1011]:
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,px(42)),prop(131096,px(42)),prop(131094,px(42)),prop(131084,num(0)),prop(131085,num(1))])
 for k,v in {'Direction':1,'ScrollViewMode':1,'HorizontalScrollerVisibility':0,'VerticalScrollerVisibility':2,'DynamicElements':0,'FixedElementSize':24.0}.items():sd(i)[k]=v;sd(i)[k+'_UxmlAttributeFlags']=1
 for k in ['Binding','RowTemplate','RowParamName']:assert sd(i)[k]==old[old[i]['data']['m_SerializedData']['rid']]['data'][k]
save(G,MODULE,doc,sid,sheet)
full=objs[W][-930000000001001].read_typetree();fr=refs(full);mapper=copy.deepcopy(fr[1119]);mapper_sd=copy.deepcopy(serial(fr,1119));audits=[]
for pid in [-930000000001001,-930000000001003]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 if pid==-930000000001001:
  photo=1285;assert sd(photo)['name']=='PersonPictureFrame'
  oldtop=next(p for p in sheet['m_Rules'][rr[photo]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==131104)['m_Values'][0];assert sheet['dimensions'][oldtop['valueIndex']]['value']==34
  override(rr[photo]['data'],[prop(131104,px(31))])
 row=named('OverviewProsConsTacticsEqualRow');left=named('OverviewEmptyLeftHalf');tactic=named('RightMiddleTacticalEffectiveness');leftsd=rr[left]['data']['m_SerializedData']['rid']
 # Reuse the empty area as the player's scouting-report mapping scope.
 replacement=copy.deepcopy(mapper_sd);replacement['rid']=leftsd;replacement['data'].update(uxmlAssetId=rr[left]['data']['m_Id'],name='OverviewProsConsReportMapping',name_UxmlAttributeFlags=1,Mappings=[{'m_serialisedType':0,'from':'report','to':{'m_path':'Person.PlayerReportForContextTeam'},'type':{'id':1315196500}}],Mappings_UxmlAttributeFlags=1)
 rr[leftsd].clear();rr[leftsd].update(replacement);rr[left]['data']['m_FullTypeName']='SI.Bindable.BindingRemapper'
 for i,grow in [(left,2),(tactic,1)]:override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(grow)),prop(131085,num(1)),prop(131091,px(0)),prop(131092,px(0)),prop(131073,en('stretch')),prop(131074,en('stretch'))])
 node=copy.deepcopy(rr[tactic]);nodesd=copy.deepcopy(serial(rr,tactic));inst=add_pair(node,nodesd,left,'OverviewTitledProsConsIcons')
 rr[inst]['data'].update(m_TemplateAlias='OverviewTitledProsConsIcons',m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[])
 sd(inst).update(templateId='OverviewTitledProsConsIcons',templateId_UxmlAttributeFlags=1)
 override(rr[inst]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131084,num(1)),prop(131085,num(1)),prop(131074,en('stretch'))])
 doc['m_Usings'].append({'alias':'OverviewTitledProsConsIcons','path':MODULE_KEY,'asset':{'m_FileID':0,'m_PathID':0}})
 assert rr[row]['data']['m_Children']==[{'rid':left},{'rid':tactic}]
 for i,r in old.items():
  if 'UxmlSerializedData' in r.get('type',{}).get('class','') and i!=leftsd:assert rr[i]==r,('existing binding changed',pid,i)
 save(W,pid,doc,sid,sheet);audits.append({'page':pid,'report_mapping':left,'tactics':tactic,'icons':inst,'pros_cons_ratio':2,'tactics_ratio':1})
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'photo_only_top_before':34,'photo_only_top_after':31,'three_equal_columns':['scouting pros','scouting cons','tactical effectiveness'],'scouting_module_existing_guid':MODULE_KEY,'original_scouting_headings_and_thumb_icons':True,'icon_size':20,'icon_cell_width':24,'overflow':'native horizontal scroll','tooltip_path':'binding.ProConsLongString','stats_colours_rows_bindings_unchanged':True,'pages':audits,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'output':str(OUT),'waiting_for_game_exit':True},ensure_ascii=True));sys.exit(0)
try:
 for n,b in outputs.items():
  for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'photo_top':31,'columns':3,'tooltip':True},ensure_ascii=True))

