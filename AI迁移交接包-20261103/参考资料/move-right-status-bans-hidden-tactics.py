from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,struct,importlib.util,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle';B='ui-backgrounds_assets_common.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
cache=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
OUT=R/('right-status-bans-hidden-tactics-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
before={p:p.read_bytes() for p in [GAME/W,SKIN/W,GAME/L,SKIN/L,cache]};assert before[GAME/W]==before[SKIN/W];assert before[GAME/L]==before[SKIN/L]
for p,b in before.items():
 tag='backup-cache' if p==cache else ('backup-game' if p.parent==GAME else 'backup-skin');folder=OUT/tag;folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/B,SKIN/B,GAME/G,SKIN/G,GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env=UnityPy.load(before[GAME/W]);objects={o.path_id:o for o in env.objects};oldhashes={i:sha(o.get_raw_data()) for i,o in objects.items()};af=env.assets[0]
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));helpers={'write','val','px','pct','en','num','prop','rule','override'};exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in helpers],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
full=objects[-930000000001001].read_typetree();fullrefs={r['rid']:r for r in full['references']['RefIds']};fullsheet=objects[full['inlineSheet']['m_PathID']].read_typetree()
tacticpid=4958372856258444847;tacticdoc=objects[tacticpid].read_typetree();metadata=next(o.read_typetree() for o in objects.values() if o.type.name=='AssetBundle')
tacticguid=next(k for k,v in metadata['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':tacticpid});tacticparams=next(r['data']['Parameters'] for r in tacticdoc['references']['RefIds'] if 'Parameters' in r.get('data',{}))
changed={};audits=[]
def sd(i):return rr.get(rr[i]['data']['m_SerializedData']['rid'],{}).get('data',{})
def named(name):
 matches=[r for r in rr.values() if 'm_SerializedData' in r.get('data',{}) and sd(r['rid']).get('name')==name];assert len(matches)==1,(name,len(matches));return matches[0]['rid']
def subtree(refs,i):
 out=[i]
 for c in refs[i]['data'].get('m_Children',[]):out+=subtree(refs,c['rid'])
 return out

def pair(nt,st,parent,name,properties):
 global next_rid,next_id
 a=copy.deepcopy(nt);s=copy.deepcopy(st);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=rule(properties),m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1);next_id+=1
 rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']

def blank(parent,name,properties):return pair(blanknode,blanksd,parent,name,properties)
def scroll(parent,name,properties):return pair(scrollnode,scrollsd,parent,name,properties)
def st(i,props):override(rr[i]['data'],props)
def move(i,parent):
 old=rr[i]['data']['m_Parent']['rid'];rr[old]['data']['m_Children'].remove({'rid':i});rr[parent]['data']['m_Children'].append({'rid':i});rr[i]['data']['m_Parent']={'rid':parent}

def clone_fitness(parent):
 global next_rid,next_id
 root=2986;nodes=subtree(fullrefs,root);ids=nodes+[fullrefs[i]['data']['m_SerializedData']['rid'] for i in nodes];mapping={i:next_rid+j for j,i in enumerate(ids)};next_rid+=len(ids)
 uidmap={fullrefs[i]['data']['m_Id']:next_id+j for j,i in enumerate(nodes)};next_id+=len(nodes)
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid'] in mapping:v['rid']=mapping[v['rid']]
   else:
    for k,x in v.items():
     if k in ['m_Id','m_ParentId','uxmlAssetId'] and isinstance(x,int) and x in uidmap:v[k]=uidmap[x]
     else:remap(x)
  elif isinstance(v,list):
   for x in v:remap(x)
 for i in ids:
  r=copy.deepcopy(fullrefs[i]);r['rid']=mapping[i];remap(r['data'])
  if i in nodes:
   if i==root:r['data']['m_Parent']={'rid':parent}
   ix=r['data'].get('m_RuleIndex',-1)
   if ix>=0:
    nr=copy.deepcopy(fullsheet['m_Rules'][ix])
    for p in nr['m_Properties']:
     for h in p['m_Values']:
      if h['m_ValueType']==1:continue
      pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(fullsheet[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
    r['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(nr)
  rr[r['rid']]=r;doc['references']['RefIds'].append(r)
 rr[parent]['data']['m_Children'].append({'rid':mapping[root]});return mapping[root]

for pid in [-930000000001001,-930000000001003]:
 doc=objects[pid].read_typetree();sheetid=doc['inlineSheet']['m_PathID'];sheet=objects[sheetid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr)
 next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 blanknode=copy.deepcopy(rr[1011]);blanksd=copy.deepcopy(rr[blanknode['data']['m_SerializedData']['rid']]);scrollnode=copy.deepcopy(rr[1703]);scrollsd=copy.deepcopy(rr[scrollnode['data']['m_SerializedData']['rid']]);scrollsd['data'].update(mode=0,mode_UxmlAttributeFlags=1,horizontalScrollerVisibility=2,horizontalScrollerVisibility_UxmlAttributeFlags=1,verticalScrollerVisibility=0,verticalScrollerVisibility_UxmlAttributeFlags=1)
 zero=[prop(262150,px(0)),prop(262151,px(0))];flow=zero+[prop(131102,en('relative')),prop(131083,en('column')),prop(131073,en('stretch')),prop(131088,en('flex-start')),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(0))]
 if pid==-930000000001001:
  panel=named('OverviewHiddenAttributesPanel');fitness=named('OverviewFitnessPercentRow');removed=[]
  for ch in list(rr[panel]['data']['m_Children']):
   if ch['rid']==fitness:continue
   ns=subtree(rr,ch['rid']);removed+=ns+[rr[i]['data']['m_SerializedData']['rid'] for i in ns]
  for i in removed:rr.pop(i)
  doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in set(removed)];rr[panel]['data']['m_Children']=[{'rid':fitness}];sd(panel)['name']='OverviewTopRightStatusPanel'
  height=220;width=210
 else:
  header=named('SimplePortraitHeader');st(header,[prop(131102,en('relative'))]);width=312;height=140
  panel=blank(header,'OverviewTopRightStatusPanel',zero+[prop(131102,en('absolute')),prop(131103,px(0)),prop(131104,px(0)),prop(131105,px(width)),prop(131087,px(height)),prop(131084,num(0)),prop(131085,num(0))])
  st(1711,[prop(131092,px(width+8))]);fitness=clone_fitness(panel)
 st(fitness,[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(0)),prop(131087,px(42)),prop(131096,px(42)),prop(131085,num(0))])
 bs=scroll(panel,'OverviewTopRightBansScroll',zero+[prop(131102,en('absolute')),prop(131089,px(0)),prop(131104,px(48)),prop(131105,px(width)),prop(131087,px(height-48)),prop(131096,px(0)),prop(131084,num(0)),prop(131085,num(1))])
 move(1035,bs);st(1035,[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,{'m_ValueType':1,'valueIndex':2}),prop(131085,num(0))])
 hidden=named('RightHiddenAttributesPanel');st(hidden,[prop(131093,px(0)),prop(131090,px(0))]);assert rr[1011]['data']['m_Children']==[{'rid':hidden}]
 # Bind the selected player explicitly, using the same native overview page inputs.
 params=rr[1015]['data']['Parameters']
 for p in tacticparams:
  if p['name'] in ['player','isonmainscreen'] and not any(x['name']==p['name'] for x in params):params.append(copy.deepcopy(p))
 alias='RightMiddleTacticalEffectiveness';doc['m_Usings'].append({'alias':alias,'path':tacticguid,'asset':{'m_FileID':0,'m_PathID':0}})
 nt=copy.deepcopy(rr[1035]);ts=copy.deepcopy(rr[nt['data']['m_SerializedData']['rid']]);nt['data'].update(m_TemplateAlias=alias,m_AttributeOverrides=[],m_SerializedDataOverride=[],m_SlotUsages=[]);ts['data'].update(templateId=alias,templateId_UxmlAttributeFlags=1,bindingPath='',bindingPath_UxmlAttributeFlags=0)
 tactical=pair(nt,ts,1011,'RightMiddleTacticalEffectiveness',flow+[prop(131105,pct(100)),prop(131087,px(160)),prop(131096,px(160)),prop(131093,px(12))])
 # Confirm all hidden values and all existing state-cell data bindings survived the move.
 for i,r in old.items():
  name=r.get('data',{}).get('name','')
  if name.startswith('OverviewFitness_') or name.startswith('RightHidden'):
   assert rr[i]==r,('state/hidden serialized binding changed',pid,i,name)
 assert len([r for r in rr.values() if r.get('data',{}).get('name','').startswith('RightHiddenRow_')])==13
 assert [len(rr[named('RightHiddenAttributesColumn'+str(i))]['data']['m_Children']) for i in [1,2,3]]==[5,4,4]
 assert len([r for r in rr.values() if r.get('data',{}).get('m_TemplateAlias')=='PlayerReportBansBlock'])==1
 assert rr[1011]['data']['m_Children']==[{'rid':hidden},{'rid':tactical}]
 validate_ui(doc,sheet);objects[pid].save_typetree(doc);objects[sheetid].save_typetree(sheet);changed[pid]=doc;changed[sheetid]=sheet
 audits.append({'page':pid,'top_status_panel':panel,'fitness_row':fitness,'bans_scroll':bs,'top_panel_height':height,'right_hidden_columns':[5,4,4],'native_tactical_guid':tacticguid,'tactical_inputs':['team','player','isonmainscreen']})

pagepid=7857044477279960178;page=objects[pagepid].read_typetree();bindings=next(r['data']['Bindings'] for r in page['references']['RefIds'] if 'Bindings' in r.get('data',{}));items=bindings['m_gridElementBindingData']
for desc in ['PlayerOverviewFull','PlayerOverviewSimple']:
 for mapping in ['player','isonmainscreen']:
  native=next(x for x in items if x['DescriptionAndMapping']['DescriptionName']=='TacticalEffectiveness' and x['DescriptionAndMapping']['MappingName']==mapping);new=copy.deepcopy(native);new['DescriptionAndMapping']['DescriptionName']=desc
  if new not in items:items.append(new)
objects[pagepid].save_typetree(page);changed[pagepid]=page

# Remove the previous bottom-right slot without shifting the other bottom cards.
def clean_layout(d):
 comps=d['m_gridComponents'];remove=[]
 for i,c in enumerate(comps):
  names=[c.get('m_elementID','')]+c.get('m_configDescriptionKeys',[])
  if 'TacticalEffectiveness' in names or (c.get('m_elementID')=='CareerStats' and c['m_location'].get('x')==16 and c['m_location'].get('y')==8):remove.append(i)
 removed=[comps[i]['m_elementID'] for i in remove];mapping={old:new for new,old in enumerate(i for i in range(len(comps)) if i not in remove)}
 d['m_gridComponents']=[c for i,c in enumerate(comps) if i not in remove]
 sl=d.get('m_optionalSlices',{});sl['m_instantiationOrder']=[mapping[i] for i in sl.get('m_instantiationOrder',[]) if i in mapping]
 d['m_placementBindings']=[b for b in d.get('m_placementBindings',[]) if b['m_elementID'] not in removed]
 return removed
le=UnityPy.load(before[GAME/L]);lo={o.path_id:o for o in le.objects};lh={i:sha(o.get_raw_data()) for i,o in lo.items()};layoutpid=3901662990989568885;layout=lo[layoutpid].read_typetree();removed_default=clean_layout(layout);assert removed_default==['CareerStats'];lo[layoutpid].save_typetree(layout)
saved_layout=json.loads(before[cache]);saved_original=copy.deepcopy(saved_layout);removed_cache=clean_layout(saved_layout);assert removed_cache==['TacticalEffectiveness'];assert len(saved_layout['m_gridComponents'])==len(saved_original['m_gridComponents'])-1
for c in saved_layout['m_gridComponents']:
 original=next(x for x in saved_original['m_gridComponents'] if x['m_elementID']==c['m_elementID']);assert c==original

outputs={W:env.file.save(packer='lz4'),L:le.file.save(packer='lz4')}
for n,b in outputs.items():
 reread={o.path_id:o for o in UnityPy.load(b).objects};hashes=oldhashes if n==W else lh;allowed=changed if n==W else {layoutpid:layout}
 assert set(reread)==set(hashes)
 for pid,h in hashes.items():
  if pid in allowed:assert reread[pid].read_typetree()==allowed[pid],('roundtrip mismatch',pid)
  else:assert sha(reread[pid].get_raw_data())==h,('unrelated object changed',pid)
 if n==W:
  for pid in [-930000000001001,-930000000001003]:
   d=reread[pid].read_typetree();validate_ui(d,reread[d['inlineSheet']['m_PathID']].read_typetree())
 (OUT/n).write_bytes(b)
# Confirm the native tactical asset resolves through the correct first bundle and preload label.
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm);cat=cm.Catalog((GAME.parent/'catalog.bin').read_bytes());loc=next(x for x in cat.locations(tacticguid) if cat.location(x)['type'][1].endswith('VisualTreeAsset'));assert cat.location(cat.location(loc)['dependencies'][0])['internal'].endswith(W);assert loc in cat.locations('GameWorldVisualTreeAssetPreload')
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():assert p.read_bytes()==b
report={'installed':False,'runtime_verified':False,'pages':audits,'removed_default_bottom_slot':removed_default,'removed_saved_bottom_slot':removed_cache,'other_saved_cards_unchanged':True,'original_background_and_catalog_preserved':True,'native_tactical_asset_preloaded':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'saved-layout.json').write_text(json.dumps(saved_layout,ensure_ascii=False,separators=(',',':')),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Game running; prepared files ready, install after game exits'
try:
 for n,b in outputs.items():
  for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
 cache.write_bytes((OUT/'saved-layout.json').read_bytes());assert json.loads(cache.read_bytes())==saved_layout
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');restore=['$ErrorActionPreference = "Stop"']
for p,b in before.items():
 tag='backup-cache' if p==cache else ('backup-game' if p.parent==GAME else 'backup-skin');restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'pages':2,'hidden_columns':[5,4,4],'native_tactical_guid':tacticguid,'other_bottom_cards_unchanged':True,'background_and_catalog_unchanged':True},ensure_ascii=True))

