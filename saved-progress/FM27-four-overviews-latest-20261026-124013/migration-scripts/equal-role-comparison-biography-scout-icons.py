from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('equal-role-comparison-biography-scout-icons-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))


import uuid, importlib.util, struct

for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:
 before[p]=p.read_bytes();protected.pop(p,None)
 folder=OUT/('backup-skin' if p.parent==SKIN else 'backup-game');(folder/p.name).write_bytes(before[p])
auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
def sd(i):return rr.get(rr[i].get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(name):
 h=[i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and sd(i).get('name')==name];assert len(h)==1,(name,h);return h[0]
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
def fill(i,grow=0):override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131096,px(0)),prop(131084,num(grow)),prop(131085,num(1)),prop(131073,en('stretch')),prop(131074,en('stretch'))])
def save(n,pid,doc,sid,sheet):
 doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in rr];validate_ui(doc,sheet);objs[n][pid].save_typetree(doc);objs[n][sid].save_typetree(sheet);changed[n][pid]=doc;changed[n][sid]=sheet
# An equal split includes the phase buttons in the top half.
pid=-940000000005000;doc=objs[G][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
top=add_pair(rr[2000],rr[2001],2002,'OverviewPhaseRolesTopHalf');move(1074,top);move(1012,top);rr[2002]['data']['m_Children']=[{'rid':top},{'rid':2006}]
for i in [top,2006]:
 fill(i,1);override(rr[i]['data'],[prop(131082,px(0)),prop(131083,en('column')),prop(131093,px(0)),prop(131090,px(0)),prop(131101,px(0)),prop(131098,px(0))])
override(rr[top]['data'],[prop(131090,px(8))]);override(rr[1012]['data'],[prop(131084,num(1))])
for i,r in old.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
save(G,pid,doc,sid,sheet)
# Private native icon row and native pros/cons list, preserving the game's icon lookup and colours.
clones=[]
def clone(sourcepid,pid,sid,label,sourceguid):
 source=objs[G][sourcepid];d=source.read_typetree();ssource=d['inlineSheet']['m_PathID'];s=objs[G][ssource].read_typetree();d['m_Name']=label;s['m_Name']=label+'_Style';d['inlineSheet']={'m_FileID':0,'m_PathID':sid}
 for newid,srcid,data in [(pid,sourcepid,d),(sid,ssource,s)]:
  assert newid not in objs[G];o=copy.copy(objs[G][srcid]);o.path_id=newid;o.assets_file.objects[newid]=o;objs[G][newid]=o
 key=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-overview/'+label).hex;clones.append({'source':sourcepid,'source_style':ssource,'source_guid':sourceguid,'pid':pid,'style':sid,'guid':key});return d,s,key
doc,sheet,rowkey=clone(-294675314297081795,-940000000006000,-940000000006001,'OverviewScoutedProConIconOnly','d6b5a3f852c7d8b40892e4489465bbc4');rr=refs(doc);original_icon=copy.deepcopy(sd(1008));remove(1009)
for i in [1001,1002,1004,1006]:
 rr[i]['data']['m_Classes']=[];override(rr[i]['data'],[prop(131105,px(24)),prop(131097,px(24)),prop(131095,px(24)),prop(131087,px(24)),prop(131096,px(24)),prop(131094,px(24)),prop(131084,num(0)),prop(131085,num(0)),prop(131073,en('center')),prop(131088,en('center')),prop(262150,px(0)),prop(262151,px(0))])
override(rr[1008]['data'],[prop(131105,px(20)),prop(131087,px(20)),prop(131097,px(20)),prop(131096,px(20)),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0))]);assert sd(1008)==original_icon
save(G,-940000000006000,doc,-940000000006001,sheet)
doc,sheet,modulekey=clone(7391060340652509499,-940000000006002,-940000000006003,'OverviewScoutedProsConsIconsOnly','9924b510914c26d45a48ea396a2feb29');rr=refs(doc);remove(1007);remove(1010)
for i in [1001,1002,1004,1005]:
 rr[i]['data']['m_Classes']=[];fill(i);override(rr[i]['data'],[prop(131083,en('column')),prop(262150,px(0)),prop(262151,px(0))])
override(rr[1004]['data'],[prop(131090,px(8))])
for i in [1008,1011]:
 fill(i);override(rr[i]['data'],[prop(131087,px(42)),prop(131096,px(42)),prop(131094,px(42))])
 data=sd(i);data['RowTemplate']['m_AssetGUID']=rowkey
 for key,value in {'Direction':1,'ScrollViewMode':1,'HorizontalScrollerVisibility':0,'VerticalScrollerVisibility':2,'DynamicElements':0,'FixedElementSize':24.0}.items():data[key]=value;data[key+'_UxmlAttributeFlags']=1
save(G,-940000000006002,doc,-940000000006003,sheet)
full=objs[W][-930000000001001].read_typetree();fr=refs(full);fs=objs[W][full['inlineSheet']['m_PathID']].read_typetree();aLabel=copy.deepcopy(fr[1096]['data']);aValue=copy.deepcopy(fr[1097]['data'])
def textmatch(target,source):
 oldprops=copy.deepcopy(sheet['m_Rules'][target['m_RuleIndex']]['m_Properties']) if target['m_RuleIndex']>=0 else []
 srcprops=copy.deepcopy(fs['m_Rules'][source['m_RuleIndex']]['m_Properties']) if source['m_RuleIndex']>=0 else []
 target['m_RuleIndex']=rule([p for p in oldprops if not 65536<=p['m_Id']<=65560])
 # Shared font classes match the preceding columns; their colours remain theme-aware.
 target['m_Classes']=[c for c in source['m_Classes'] if not c.startswith('margin-')]+['content-no-wrap','content-ellipsis']
 override(target,[prop(65546,en('middle-left'))])
audits=[]
for pid in [-930000000001001,-930000000001003]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 blank=copy.deepcopy(rr[1011]);blanksd=copy.deepcopy(rr[blank['data']['m_SerializedData']['rid']])
 col=named('OverviewBiographyMediaColumn');override(rr[col]['data'],[prop(131102,en('relative')),prop(131089,px(-20))])
 for field in ['BiographyOverallCareerStats','BiographyCareerMilestones']:
  label=named(field+'Title');value=named(field);textmatch(rr[label]['data'],aLabel);textmatch(rr[value]['data'],aValue)
  override(rr[label]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(0)),prop(131092,px(4))])
 tactic=named('RightMiddleTacticalEffectiveness');parent=rr[tactic]['data']['m_Parent']['rid'];row=add_pair(blank,blanksd,parent,'OverviewProsConsTacticsEqualRow');move(tactic,row)
 override(rr[row]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131083,en('row')),prop(131073,en('stretch')),prop(131087,px(160)),prop(131096,px(160)),prop(131084,num(0)),prop(131085,num(0)),prop(131093,px(12))])
 # Map the exact report type expected by the native scouting module.
 remapnode=copy.deepcopy(rr[1119] if 1119 in rr and rr[1119]['data'].get('m_FullTypeName')=='SI.Bindable.BindingRemapper' else fr[1119])
 remapserial=copy.deepcopy(fr[fr[1119]['data']['m_SerializedData']['rid']])
 left=add_pair(remapnode,remapserial,row,'OverviewScoutedProsConsReportMapping');sd(left)['Mappings']=[{'m_serialisedType':0,'from':'report','to':{'m_path':'Person.PlayerReportForContextTeam'},'type':{'id':1315196500}}];sd(left)['Mappings_UxmlAttributeFlags']=1
 rr[row]['data']['m_Children']=[{'rid':left},{'rid':tactic}]
 for i in [left,tactic]:override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,pct(100)),prop(131096,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(131073,en('stretch'))])
 templ=copy.deepcopy(rr[tactic]);templs=copy.deepcopy(rr[templ['data']['m_SerializedData']['rid']]);icons=add_pair(templ,templs,left,'OverviewScoutedProsConsIcons')
 rr[icons]['data'].update(m_TemplateAlias='OverviewScoutedProsConsIcons',m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[]);sd(icons).update(templateId='OverviewScoutedProsConsIcons',templateId_UxmlAttributeFlags=1)
 fill(icons,1);doc['m_Usings'].append({'alias':'OverviewScoutedProsConsIcons','path':modulekey,'asset':{'m_FileID':0,'m_PathID':0}})
 for i,r in old.items():
  if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('existing binding changed',pid,i)
 save(W,pid,doc,sid,sheet);audits.append({'page':pid,'lower_row':row,'scouting_left':left,'tactical_right':tactic})
# Register private clones with the same owning bundle and native preload dependencies.
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin'])
ab=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=ab.read_typetree();newlocs=[]
for c in clones:
 sourceentry=next(v for k,v in meta['m_Container'] if k==c['source_guid'] and v['asset']['m_PathID']==c['source']);span=copy.deepcopy(meta['m_PreloadTable'][sourceentry['preloadIndex']:sourceentry['preloadIndex']+sourceentry['preloadSize']])
 for ptr in span:
  if ptr['m_FileID']==0 and ptr['m_PathID'] in [c['source'],c['source_style']]:ptr['m_PathID']={c['source']:c['pid'],c['source_style']:c['style']}[ptr['m_PathID']]
 for ptr in [{'m_FileID':0,'m_PathID':c['style']},{'m_FileID':0,'m_PathID':c['pid']}]:
  if ptr not in span:span.append(ptr)
 meta['m_Container'].append((c['guid'],{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':c['pid']}}));meta['m_PreloadTable'].extend(span)
 loc=next(x for x in cat.locations(c['source_guid']) if cat.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');cat=cm.Catalog(cat.add_key_location(c['guid'],loc,loc));newloc=cat.locations(c['guid'])[0];newlocs.append(newloc);assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(G)
meta['m_Container'].sort(key=lambda kv:kv[0]);ab.save_typetree(meta);changed[G][ab.path_id]=meta
ix=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[ix];locs=[x[0] for x in cat.array(ls,'I')]+newlocs
newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[ix]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);catout=bytes(cat.data)
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 (OUT/n).write_bytes(b)
hashout=hashlib.md5(catout).hexdigest().encode('ascii');(OUT/'catalog.bin').write_bytes(catout);(OUT/'catalog.hash').write_bytes(hashout)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'role_comparison_equal_halves':True,'phase_buttons_included_in_top_half':True,'biography_column_shift_px':-20,'biography_styles_match_preceding_columns':True,'lower_scout_tactics_equal_halves':True,'native_scouting_report_pros_cons_icons_only':True,'native_icon_binding_preserved':True,'pages':audits,'private_templates':clones,'center_attribute_width_preserved':640,'after_sha256':{**{n:sha(b) for n,b in outputs.items()},'catalog.bin':sha(catout),'catalog.hash':sha(hashout)}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared files ready; game must exit before install'
try:
 for n,b in outputs.items():
  for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
 for p,b in [(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout)]:p.write_bytes(b);assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'scout_icons':modulekey,'vertical_split':[50,50],'horizontal_split':[50,50]},ensure_ascii=True))
