from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('biography-titles-role-comparison-lower-bans-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))

auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def sd(i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(name):
 hits=[i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and sd(i).get('name')==name];assert len(hits)==1,(name,hits);return hits[0]
def move(i,parent):
 a=rr[i]['data'];rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});a['m_Parent']={'rid':parent};rr[parent]['data']['m_Children'].append({'rid':i})
def remove(i):
 a=rr[i]['data']
 for c in list(a.get('m_Children',[])):remove(c['rid'])
 rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i})
 for j in [i,a['m_SerializedData']['rid']]:rr.pop(j)
def add_pair(node,serial,parent,name):
 global next_rid,next_id
 a=copy.deepcopy(node);s=copy.deepcopy(serial);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_RuleIndex=-1,m_SerializedData={'rid':s['rid']},m_Classes=[],m_Properties=[])
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1);next_id+=1
 rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
# The selector exposes a content container for the existing overview-owned bans component.
# This keeps the player's original binding scope and avoids a Global -> GameWorld bundle dependency.
pid=-940000000005000;doc=objs[G][pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree();original=copy.deepcopy(rr)
move(2006,2002)
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
host=add_pair(rr[2000],rr[2001],2000,'OverviewBansContentHost')
override(rr[host]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131096,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131083,en('column')),prop(131073,en('stretch')),prop(131074,en('stretch')),prop(131093,px(8))])
doc['m_ContentContainerId']=rr[host]['data']['m_Id']
override(rr[1012]['data'],[prop(131084,num(3)),prop(131082,px(0)),prop(131096,px(0))])
override(rr[2006]['data'],[prop(131084,num(2)),prop(131082,px(0)),prop(131096,px(0)),prop(131093,px(8))])
assert rr[2002]['data']['m_Children']==[{'rid':1074},{'rid':1012},{'rid':2006}]
for i,r in original.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
validate_ui(doc,sheet);objs[G][pid].save_typetree(doc);objs[G][sid].save_typetree(sheet);changed[G][pid]=doc;changed[G][sid]=sheet
fr=refs(objs[W][-930000000001001].read_typetree());labelnode=copy.deepcopy(fr[1096]);labelserial=copy.deepcopy(fr[labelnode['data']['m_SerializedData']['rid']])
audits=[]
for pid in [-930000000001001,-930000000001003]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 blanknode=copy.deepcopy(rr[1011]);blankserial=copy.deepcopy(rr[blanknode['data']['m_SerializedData']['rid']])
 bans=named('OverviewTopRightBansScroll');move(bans,1007)
 sd(bans)['name']='OverviewPitchLowerBansScroll'
 override(rr[bans]['data'],[prop(131102,en('relative')),prop(131089,auto),prop(131103,auto),prop(131104,auto),prop(131080,auto),prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131073,en('stretch')),prop(131074,en('stretch'))])
 for c in rr[bans]['data']['m_Children']:override(rr[c['rid']]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131074,en('stretch'))])
 remove(named('OverviewFitnessBansDivider'))
 remove(named('OverviewMediaHandling'))
 col=named('OverviewBiographyMediaColumn');rows=[]
 for field,title in [('BiographyOverallCareerStats','职业生涯总结'),('BiographyCareerMilestones','生涯里程碑')]:
  value=named(field);ix=rr[col]['data']['m_Children'].index({'rid':value});row=add_pair(blanknode,blankserial,col,field+'Row');move(value,row)
  rr[col]['data']['m_Children'].remove({'rid':row});rr[col]['data']['m_Children'].insert(ix,{'rid':row})
  override(rr[row]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(20)),prop(131096,px(20)),prop(131083,en('row')),prop(131073,en('center')),prop(131084,num(0)),prop(131085,num(0)),prop(131090,px(4 if field=='BiographyOverallCareerStats' else 0))])
  label=add_pair(labelnode,labelserial,row,field+'Title');rr[row]['data']['m_Children']=[{'rid':label},{'rid':value}]
  rr[label]['data']['m_Classes']=['global-text-secondary','body-sm','content-no-wrap']
  data=sd(label);data.update(text=title,text_UxmlAttributeFlags=1,DebugDisplay=title,TextBinding_UxmlAttributeFlags=0)
  data['TextBinding']={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}}
  override(rr[label]['data'],[prop(131105,px(70)),prop(131097,px(70)),prop(131084,num(0)),prop(131085,num(0)),prop(65537,px(10)),prop(65546,en('middle-left'))])
  override(rr[value]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131090,px(0)),prop(65537,px(12)),prop(65546,en('middle-left'))]);rows.append(row)
 doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in rr]
 assert rr[1007]['data']['m_Children']==[{'rid':bans}]
 # All native data, including the bans table and biography values, keeps its previous bindings.
 for i,r in old.items():
  if i not in rr:continue
  if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
   if i==rr[bans]['data']['m_SerializedData']['rid']:
    a=copy.deepcopy(rr[i]);a['data']['name']=r['data']['name'];assert a==r
   else:assert rr[i]==r,('existing data binding changed',pid,i)
 validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);objs[W][sid].save_typetree(sheet);changed[W][pid]=doc;changed[W][sid]=sheet;audits.append({'page':pid,'bans_node':bans,'biography_title_rows':rows})
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={x.path_id:x for x in UnityPy.load(b).objects};assert set(check)==set(hashes[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'pages':audits,'biography_titles':['职业生涯总结','生涯里程碑'],'media_handling_removed_from_overview':True,'right_column_order':['phase buttons','roles','comparison'],'left_column_order':['landscape pitch','selected position','bans'],'bans_content_container_id':changed[G][-940000000005000]['m_ContentContainerId'],'native_player_bindings_preserved':True,'original_bans_area_blank':True,'center_attributes_width_retained':640,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():
 print(json.dumps({'prepared':True,'installed':False,'output':str(OUT),'waiting_for_game_exit':True},ensure_ascii=True));sys.exit(0)
try:
 for n,b in outputs.items():
  for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT)},ensure_ascii=True))

