from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('rotate-biography-remove-pros-twelve-stats-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))


import struct, uuid, importlib.util

for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:
 protected.pop(p,None);before[p]=p.read_bytes();(OUT/('backup-skin' if p.parent==SKIN else 'backup-game')/p.name).write_bytes(before[p])
for p in [GAME/G,SKIN/G]:protected[p]=sha(p.read_bytes())
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='color'],type_ignores=[]),'color','exec'))
src=ast.parse((R/'equal-role-comparison-biography-scout-icons.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'refs','sd','named','move','remove','add_pair','fill'}],type_ignores=[]),'tree helpers','exec'))
auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
native=objs[W][-648337528654704265].read_typetree();nr=refs(native)
def native_sd(i):return nr[nr[i]['data']['m_SerializedData']['rid']]['data']
native_names={r.get('data',{}).get('name'):r for r in nr.values() if r.get('data',{}).get('name')}
stats=[('进球','OutfielderStatsGoalsText','Goals'),('创造机会','ChancesCreatedText','ChancesCreated'),('当场最佳','PotMAwText','PlayerOfTheMatchAwards'),('预期进球/90分钟','ExpectedGoalsPer90Text','ExpectedGoalsPer90'),('射正/90分钟','ShotsOnTargetPer90Text','ShotsOnTargetPer90'),('预期助攻/90分钟','ExpectedAssistsPer90Text','ExpectedAssistsPer90'),('关键传球','KeyPassesText','KeyPasses'),('推进型传球/90分钟','ProgressivePassesPer90Text','ProgressivePassesPer90'),('传球成功/90分钟','PassCompletedPer90Text','PassCompletedPer90'),('关键抢断','KeyTacklesText','KeyTackles'),('场均抢断成功次数','TacklesCompletedPer90Text','TacklesCompletedPer90'),('关键头球/90分钟','KeyHeadersPer90Text','KeyHeadersPer90')]
PID=-940000000007000;SID=-940000000007001;COMPACT=-940000000007002;COMPACT_STYLE=-940000000007003
FULL_KEY='8510b34993845aedbfedc0e105597c4e';COMPACT_KEY=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-overview-season-twelve-stats-portrait-header-compact').hex
doc=copy.deepcopy(native);rr=refs(doc);sheet=objs[W][native['inlineSheet']['m_PathID']].read_typetree()
doc['m_Name']='OverviewSeasonTwelveStats';sheet['m_Name']=doc['m_Name']+'_Style';doc['inlineSheet']={'m_FileID':0,'m_PathID':SID}
rr[1000]['data']['m_Children']=[{'rid':1041}];rr[1041]['data']['m_Parent']={'rid':1000};rr[1041]['data']['m_Children']=[];sd(1041)['Mappings'][0]['to']['m_path']='person.SeasonStats.SeasonStatsSelectedCompetitionsData'
base_node=copy.deepcopy(nr[1126]);base_sd=copy.deepcopy(nr[base_node['data']['m_SerializedData']['rid']]);text_node=copy.deepcopy(nr[1284]);text_sd=copy.deepcopy(nr[text_node['data']['m_SerializedData']['rid']]);switch_node=copy.deepcopy(nr[1008]);switch_sd=copy.deepcopy(nr[switch_node['data']['m_SerializedData']['rid']])
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
rows=[];titles=[];value_nodes=[];cells=[];checks=[]
empty_binding={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}}
def static_text(i,text):
 d=sd(i);d.update(text=text,text_UxmlAttributeFlags=1,DebugDisplay=text,TextBinding=copy.deepcopy(empty_binding),TextBinding_UxmlAttributeFlags=0)
for j in range(4):
 i=add_pair(base_node,base_sd,1041,'SeasonStatsRow'+str(j+1));rows.append(i)
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(30)),prop(131096,px(30)),prop(131094,px(30)),prop(131083,en('row')),prop(131073,en('stretch')),prop(131084,num(0)),prop(131085,num(0)),prop(131090,px(2 if j<3 else 0))])
for j,(title,native_name,field) in enumerate(stats):
 cell=add_pair(base_node,base_sd,rows[j//3],'SeasonStatCell_'+field);cells.append(cell)
 override(rr[cell]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131083,en('column')),prop(131073,en('stretch')),prop(131087,px(30)),prop(131096,px(30)),prop(131094,px(30))])
 t=add_pair(text_node,text_sd,cell,'SeasonStatTitle_'+field);static_text(t,title);titles.append(t)
 override(rr[t]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(18)),prop(131096,px(18)),prop(131094,px(18)),prop(65537,px(9)),prop(65536,color(160,160,160)),prop(65546,en('middle-center')),prop(65552,en('normal')),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0))])
 sw=add_pair(switch_node,switch_sd,cell,'SeasonStatAvailable_'+field);checks.append(sw)
 bind=sd(sw)['Binding'];args=bind['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'];oldpath=b'SelectedComp';assert bytes(args).endswith(bytes([len(oldpath)])+oldpath)
 path=('SeasonStats.'+field).encode();bind['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=args[:-len(oldpath)-1]+[len(path)]+list(path)
 override(rr[sw]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(12)),prop(131096,px(12)),prop(131094,px(12)),prop(131084,num(0)),prop(131085,num(0))])
 source_sd=copy.deepcopy(native_names[native_name]);source_node=next(r for r in nr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==source_sd['rid'])
 v=add_pair(source_node,source_sd,sw,'SeasonStatValue_'+field);value_nodes.append(v);sd(v).update(text='--',text_UxmlAttributeFlags=1)
 missing=add_pair(text_node,text_sd,sw,'SeasonStatMissing_'+field);static_text(missing,'--')
 for i in [v,missing]:
  rr[i]['data']['m_Classes']=['content-no-wrap'];override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(12)),prop(131096,px(12)),prop(131094,px(12)),prop(65537,px(12)),prop(65536,color(255,255,255)),prop(65546,en('middle-center')),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0))])
 assert sd(v)['TextBinding']==source_sd['data']['TextBinding'],field
# Discard the native competition table and all four previous graphic groups.
keep=set()
def collect(i):
 if i in keep:return
 keep.add(i);a=rr[i].get('data',{});s=a.get('m_SerializedData',{}).get('rid')
 if s in rr:keep.add(s)
 for c in a.get('m_Children',[]):collect(c['rid'])
collect(1000);rr={i:r for i,r in rr.items() if i in keep};doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in keep]
override(rr[1041]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(126)),prop(131096,px(126)),prop(131083,en('column')),prop(131073,en('stretch')),prop(262150,px(0)),prop(262151,px(0))])
validate_ui(doc,sheet);objs[W][PID].save_typetree(doc);objs[W][SID].save_typetree(sheet);changed[W][PID]=doc;changed[W][SID]=sheet
compact_doc=copy.deepcopy(doc);compact_sheet=copy.deepcopy(sheet);compact_doc['m_Name']='OverviewSeasonTwelveStatsCompact';compact_doc['inlineSheet']['m_PathID']=COMPACT_STYLE;compact_sheet['m_Name']=compact_doc['m_Name']+'_Style';rr=refs(compact_doc);sheet=compact_sheet
for i in rows+cells:override(rr[i]['data'],[prop(131087,px(22)),prop(131096,px(22)),prop(131094,px(22))])
for i in rows:override(rr[i]['data'],[prop(131090,px(1 if i!=rows[-1] else 0))])
for i in titles:override(rr[i]['data'],[prop(131087,px(10)),prop(131096,px(10)),prop(131094,px(10)),prop(65552,en('nowrap'))])
override(rr[1041]['data'],[prop(131087,px(91)),prop(131096,px(91))]);validate_ui(compact_doc,sheet)
for newpid,sourcepid,data in [(COMPACT,PID,compact_doc),(COMPACT_STYLE,SID,compact_sheet)]:
 assert newpid not in objs[W];o=copy.copy(objs[W][sourcepid]);o.path_id=newpid;o.assets_file.objects[newpid]=o;objs[W][newpid]=o;o.save_typetree(data);changed[W][newpid]=data
audits=[]
payload=['text','text_UxmlAttributeFlags','DebugDisplay','DebugDisplay_UxmlAttributeFlags','TextBinding','TextBinding_UxmlAttributeFlags','enableRichText','enableRichText_UxmlAttributeFlags']
for pagepid in [-930000000001001,-930000000001003]:
 doc=objs[W][pagepid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);pagesid=doc['inlineSheet']['m_PathID'];sheet=objs[W][pagesid].read_typetree()
 if pagepid==-930000000001001:
  # Rotate payloads inside the three existing slots, retaining each slot's own typography and geometry.
  for triplet in [(1097,named('BiographyOverallCareerStats'),named('BiographyCareerMilestones')),(1096,named('BiographyOverallCareerStatsTitle'),named('BiographyCareerMilestonesTitle'))]:
   snapshots=[copy.deepcopy(sd(i)) for i in triplet]
   for target,source in [(triplet[0],snapshots[2]),(triplet[1],snapshots[0]),(triplet[2],snapshots[1])]:
    data=sd(target)
    for k in payload:
     if k in source:data[k]=copy.deepcopy(source[k])
 remove(named('OverviewScoutedProsConsReportMapping'))
 row=named('OverviewProsConsTacticsEqualRow');tactic=named('RightMiddleTacticalEffectiveness');next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 blank=copy.deepcopy(rr[1011]);blank_sd=copy.deepcopy(rr[blank['data']['m_SerializedData']['rid']]);spacer=add_pair(blank,blank_sd,row,'OverviewEmptyLeftHalf');rr[row]['data']['m_Children']=[{'rid':spacer},{'rid':tactic}]
 override(rr[spacer]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))]);override(rr[row]['data'],[prop(131087,px(160)),prop(131096,px(160))])
 doc['m_Usings']=[u for u in doc['m_Usings'] if u['alias']!='OverviewScoutedProsConsIcons']
 stats_node=named('OverviewTopSeasonFourGauges');sd(stats_node)['name']='OverviewTopSeasonTwelveStats';override(rr[stats_node]['data'],[prop(131087,px(126 if pagepid==-930000000001001 else 91)),prop(131096,px(126 if pagepid==-930000000001001 else 91))])
 if pagepid==-930000000001003:next(u for u in doc['m_Usings'] if u['alias']=='OverviewNativeSeasonFourGauges')['path']=COMPACT_KEY
 doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in rr];validate_ui(doc,sheet);objs[W][pagepid].save_typetree(doc);objs[W][pagesid].save_typetree(sheet);changed[W][pagepid]=doc;changed[W][pagesid]=sheet;audits.append({'page':pagepid,'stats':stats_node,'left_empty':spacer,'tactics_right':tactic})
# Register the compact variant without changing ownership of the existing widget.
ab=next(o for o in objs[W].values() if o.type.name=='AssetBundle');meta=ab.read_typetree();sourceentry=next(v for k,v in meta['m_Container'] if k==FULL_KEY and v['asset']['m_PathID']==PID);span=copy.deepcopy(meta['m_PreloadTable'][sourceentry['preloadIndex']:sourceentry['preloadIndex']+sourceentry['preloadSize']])
for p in span:
 if p['m_FileID']==0 and p['m_PathID'] in [PID,SID]:p['m_PathID']={PID:COMPACT,SID:COMPACT_STYLE}[p['m_PathID']]
meta['m_Container'].append((COMPACT_KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':COMPACT}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda kv:kv[0]);ab.save_typetree(meta);changed[W][ab.path_id]=meta
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=cat.locations(FULL_KEY)[0];cat=cm.Catalog(cat.add_key_location(COMPACT_KEY,loc,loc));newloc=cat.locations(COMPACT_KEY)[0];assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(W)
ix=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)=='GameWorldVisualTreeAssetPreload');ko,ls=cat.key_records[ix];locs=[x[0] for x in cat.array(ls,'I')]+[newloc];newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[ix]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);catout=bytes(cat.data)
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
 if i not in changed[W]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
for i,d in changed[W].items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
(OUT/W).write_bytes(output);(OUT/'catalog.bin').write_bytes(catout);hashout=hashlib.md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'identity_rotation':'old personality -> milestones; old career summary -> personality; old milestones -> career summary','pros_cons_removed':True,'tactics_right_half_left_blank':True,'stats':stats,'full_stats_height':126,'portrait_stats_height':91,'title_size':9,'number_size':12,'missing':'native BindingTargetExists/IsNullReference switch -> --; zero remains a valid number','compact_guid':COMPACT_KEY,'pages':audits,'native_number_formatters_preserved':True,'center_width_preserved':640,'after_sha256':{W:sha(output),'catalog.bin':sha(catout),'catalog.hash':sha(hashout)}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared files ready; exit game before install'
try:
 for folder in [GAME,SKIN]:(folder/W).write_bytes(output);assert (folder/W).read_bytes()==output
 for p,b in [(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout)]:p.write_bytes(b);assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'stats_count':12,'layout':[4,3]},ensure_ascii=True))
