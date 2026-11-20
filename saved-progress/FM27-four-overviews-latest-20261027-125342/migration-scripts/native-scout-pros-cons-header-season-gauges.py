from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('native-scout-pros-cons-header-season-gauges-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))


import uuid, importlib.util, struct

for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:
 protected.pop(p,None);before[p]=p.read_bytes();(OUT/('backup-skin' if p.parent==SKIN else 'backup-game')/p.name).write_bytes(before[p])
for p in [GAME/G,SKIN/G]:protected[p]=sha(p.read_bytes())
auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def sd(i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(n):
 h=[i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and sd(i).get('name')==n];assert len(h)==1,(n,h);return h[0]
sourcepid=-648337528654704265;pid=-940000000007000;sid=-940000000007001
doc=objs[W][sourcepid].read_typetree();original=copy.deepcopy(doc);rr=refs(doc);original_rr=copy.deepcopy(rr);source_sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][source_sid].read_typetree()
sourcekey=next(k for k,v in env[W].container.items() if v.path_id==sourcepid)
key=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-overview-native-season-four-gauges').hex
doc['m_Name']='OverviewNativeSeasonFourGauges';sheet['m_Name']=doc['m_Name']+'_Style';doc['inlineSheet']={'m_FileID':0,'m_PathID':sid}
# Keep the native SeasonStats remapper and the four exact screenshot subtrees.
cards=[1126,1085,1088,1146];rr[1000]['data']['m_Children']=[{'rid':1041}];rr[1041]['data']['m_Parent']={'rid':1000};rr[1041]['data']['m_Children']=[]
mapping=sd(1041);assert mapping['Mappings'][0]['from']=='SeasonStats';mapping['Mappings'][0]['to']['m_path']='person.SeasonStats.SeasonStatsSelectedCompetitionsData'
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
def row(name):
 global next_rid,next_id
 a=copy.deepcopy(rr[1126]);s=copy.deepcopy(rr[a['data']['m_SerializedData']['rid']]);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':1041},m_Children=[],m_RuleIndex=-1,m_Classes=[],m_SerializedData={'rid':s['rid']})
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1);next_id+=1;rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[1041]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
rows=[row('OverviewGoalsChancesCreatedRow'),row('OverviewKeyPassesTacklesRow')]
for j,i in enumerate(cards):rr[i]['data']['m_Parent']={'rid':rows[j//2]};rr[rows[j//2]]['data']['m_Children'].append({'rid':i})
keep=set()
def collect(i):
 if i in keep:return
 keep.add(i);a=rr[i].get('data',{});serial=a.get('m_SerializedData',{}).get('rid')
 if serial in rr:keep.add(serial)
 for c in a.get('m_Children',[]):collect(c['rid'])
collect(1000);rr={i:r for i,r in rr.items() if i in keep};doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in keep]
override(rr[1041]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,px(124)),prop(131096,px(124)),prop(131083,en('column')),prop(131073,en('stretch')),prop(262150,px(0)),prop(262151,px(0))])
for j,i in enumerate(rows):override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(60)),prop(131096,px(60)),prop(131094,px(60)),prop(131083,en('row')),prop(131073,en('stretch')),prop(131084,num(0)),prop(131085,num(0)),prop(131090,px(4 if j==0 else 0))])
for j,i in enumerate(cards):override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,px(60)),prop(131096,px(60)),prop(131094,px(60)),prop(131092,px(8 if j%2==0 else 0)),prop(131073,en('stretch')),prop(131088,en('flex-start'))])
for i,r in rr.items():
 a=r.get('data',{});typ=a.get('m_FullTypeName','')
 if i in cards+rows+[1000,1041] or not typ:continue
 override(a,[prop(131097,px(0)),prop(131096,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(131101,px(0)),prop(131098,px(0))])
 if typ=='SI.Bindable.SIText':override(a,[prop(65537,px(9)),prop(131085,num(1))])
 elif typ=='UnityEngine.UIElements.VisualElement' and a.get('m_Children'):
  override(a,[prop(131085,num(1))])
  if 'column-direction-normal' in a.get('m_Classes',[]):override(a,[prop(131105,pct(100)),prop(131073,en('stretch'))])
titles=[1284,1214,1227,1337];values=[1360,1312,1326,1403];icons=[1359,1311,1325,1402];gauges=[1417,1388,1434,1440];gaugeframes=[1362,1314,1396,1405];counts=[1446,1431,1453,1456]
for i in titles:override(rr[i]['data'],[prop(131087,px(12)),prop(131096,px(12)),prop(131094,px(12))])
for i in values:
 override(rr[i]['data'],[prop(65537,px(16)),prop(131087,px(22)),prop(131096,px(22))]);par=rr[i]['data']['m_Parent']['rid'];override(rr[par]['data'],[prop(131087,px(22)),prop(131096,px(22)),prop(131094,px(22))])
for i in icons:override(rr[i]['data'],[prop(131105,px(18)),prop(131097,px(18)),prop(131087,px(18)),prop(131096,px(18)),prop(131092,px(4)),prop(131084,num(0)),prop(131085,num(0))])
for i in gauges+gaugeframes:override(rr[i]['data'],[prop(131105,px(24)),prop(131097,px(24)),prop(131087,px(24)),prop(131096,px(24)),prop(131094,px(24)),prop(131084,num(0)),prop(131085,num(0))])
for i in gaugeframes:override(rr[i]['data'],[prop(131092,px(4))])
for i in counts:override(rr[i]['data'],[prop(65537,px(7))])
for i,r in rr.items():
 if i in original_rr and 'UxmlSerializedData' in r.get('type',{}).get('class','') and i!=rr[1041]['data']['m_SerializedData']['rid']:assert r==original_rr[i],('native stat/radial binding changed',i)
validate_ui(doc,sheet)
for newpid,srcpid,data in [(pid,sourcepid,doc),(sid,source_sid,sheet)]:
 assert newpid not in objs[W];o=copy.copy(objs[W][srcpid]);o.path_id=newpid;o.assets_file.objects[newpid]=o;objs[W][newpid]=o;o.save_typetree(data);changed[W][newpid]=data
audits=[]
for pagepid in [-930000000001001,-930000000001003]:
 doc=objs[W][pagepid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);pagesid=doc['inlineSheet']['m_PathID'];sheet=objs[W][pagesid].read_typetree()
 u=next(u for u in doc['m_Usings'] if u['alias']=='OverviewScoutedProsConsIcons');u['path']='9924b510914c26d45a48ea396a2feb29'
 pros=named('OverviewScoutedProsConsIcons');override(rr[pros]['data'],[prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131084,num(1)),prop(131085,num(1))])
 lower=named('OverviewProsConsTacticsEqualRow');override(rr[lower]['data'],[prop(131087,auto),prop(131096,px(160)),prop(131094,none)])
 # Insert the native season graphics in the area vacated by top-right bans.
 status=named('OverviewTopRightStatusPanel');sample=copy.deepcopy(rr[named('RightMiddleTacticalEffectiveness')]);serial=copy.deepcopy(rr[sample['data']['m_SerializedData']['rid']]);rid=max(rr)+1;serialid=rid+1;ident=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 sample['rid']=rid;sample['data'].update(m_Id=ident,m_Parent={'rid':status},m_Children=[],m_SerializedData={'rid':serialid},m_RuleIndex=-1,m_TemplateAlias='OverviewNativeSeasonFourGauges',m_Classes=[],m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[])
 serial['rid']=serialid;serial['data'].update(uxmlAssetId=ident,name='OverviewTopSeasonFourGauges',name_UxmlAttributeFlags=1,templateId='OverviewNativeSeasonFourGauges',templateId_UxmlAttributeFlags=1)
 rr[rid]=sample;rr[serialid]=serial;doc['references']['RefIds'] += [sample,serial];rr[status]['data']['m_Children'].append({'rid':rid});doc['m_Usings'].append({'alias':'OverviewNativeSeasonFourGauges','path':key,'asset':{'m_FileID':0,'m_PathID':0}})
 width=240 if pagepid==-930000000001001 else 312
 override(sample['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(48)),prop(131105,px(width)),prop(131097,px(0)),prop(131087,px(124)),prop(131096,px(124)),prop(131084,num(0)),prop(131085,num(0))])
 for i,r in old.items():
  if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
 validate_ui(doc,sheet);objs[W][pagepid].save_typetree(doc);objs[W][pagesid].save_typetree(sheet);changed[W][pagepid]=doc;changed[W][pagesid]=sheet;audits.append({'page':pagepid,'stats_node':rid,'width':width})
# The private widget loads from GameWorld, using the native Season Stats dependencies.
ab=next(o for o in objs[W].values() if o.type.name=='AssetBundle');meta=ab.read_typetree();entry=next(v for k,v in meta['m_Container'] if k==sourcekey and v['asset']['m_PathID']==sourcepid);span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for ptr in span:
 if ptr['m_FileID']==0 and ptr['m_PathID'] in [sourcepid,source_sid]:ptr['m_PathID']={sourcepid:pid,source_sid:sid}[ptr['m_PathID']]
for ptr in [{'m_FileID':0,'m_PathID':pid},{'m_FileID':0,'m_PathID':sid}]:
 if ptr not in span:span.append(ptr)
meta['m_Container'].append((key,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':pid}}));meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda kv:kv[0]);ab.save_typetree(meta);changed[W][ab.path_id]=meta
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=next(x for x in cat.locations(sourcekey) if cat.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');cat=cm.Catalog(cat.add_key_location(key,loc,loc));newloc=cat.locations(key)[0];assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(W)
ix=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)=='GameWorldVisualTreeAssetPreload');ko,ls=cat.key_records[ix];locs=[x[0] for x in cat.array(ls,'I')]+[newloc];newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[ix]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);catout=bytes(cat.data)
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
 if i not in changed[W]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
for i,d in changed[W].items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
(OUT/W).write_bytes(output);(OUT/'catalog.bin').write_bytes(catout);hashout=hashlib.md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'native_scouting_pros_cons_module':'9924b510914c26d45a48ea396a2feb29','season_stats_source':sourcekey,'season_stats_private_guid':key,'season_stats_private_pid':pid,'native_stat_and_gauge_bindings_preserved':True,'season_data_path':'person.SeasonStats.SeasonStatsSelectedCompetitionsData','cards':['Goals / shots on target','Chances created / crosses completed','Key passes / pass completion','Key tackles / tackles won'],'pages':audits,'center_attribute_width_preserved':640,'global_bundle_unchanged':True,'after_sha256':{W:sha(output),'catalog.bin':sha(catout),'catalog.hash':sha(hashout)}}
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
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'native_pros_cons':True,'season_four_gauges':key},ensure_ascii=True))
