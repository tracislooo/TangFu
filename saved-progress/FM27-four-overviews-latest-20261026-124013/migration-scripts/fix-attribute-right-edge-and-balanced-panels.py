from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('fix-attribute-right-edge-and-balanced-panels-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))

auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
def horizontal_fill(a):
 override(a,[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131074,en('stretch')),prop(131073,en('stretch'))])
def save_document(n,pid,doc,sid):
 validate_ui(doc,sheet);objs[n][pid].save_typetree(doc);objs[n][sid].save_typetree(sheet);changed[n][pid]=doc;changed[n][sid]=sheet
for pid in [-930000000001001,-930000000001003]:
 doc=objs[W][pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree()
 # A plain flex row has no geometry callback that can reassign its children's widths or visibility.
 body=rr[1002]['data'];serialid=body['m_SerializedData']['rid'];sample=rr[rr[1009]['data']['m_SerializedData']['rid']]
 replacement=copy.deepcopy(sample);replacement['rid']=serialid
 for key in replacement['data']:
  if key in rr[serialid]['data']:replacement['data'][key]=copy.deepcopy(rr[serialid]['data'][key])
 replacement['data']['uxmlAssetId']=body['m_Id'];replacement['data']['name']='OverviewBalancedThreePanels';replacement['data']['name_UxmlAttributeFlags']=1
 rr[serialid].clear();rr[serialid].update(replacement);body['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
 override(body,[prop(131083,en('row')),prop(131073,en('stretch')),prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100))])
 for i in [1007,1703]:
  override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131091,px(0)),prop(131092,px(0)),prop(131074,en('stretch')),prop(131073,en('stretch'))])
 for i in [1008,1010]:
  override(rr[i]['data'],[prop(131105,px(1)),prop(131097,px(1)),prop(131095,px(1)),prop(131082,px(1)),prop(131084,num(0)),prop(131085,num(0)),prop(131091,px(12)),prop(131092,px(12)),prop(131074,en('stretch'))])
 # A ScrollView viewport must stretch; align-items:start shrinks its internal viewport to content.
 rr[1703]['data']['m_Classes']=[c for c in rr[1703]['data']['m_Classes'] if c!='align-items-start']
 override(rr[1011]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131095,pct(100)),prop(131073,en('stretch')),prop(131074,en('stretch')),prop(131084,num(0)),prop(131085,num(0))])
 # Also stretch the middle scroll viewport, keeping the existing 710px center constraints.
 i=1040
 while i!=1009:
  horizontal_fill(rr[i]['data']);i=rr[i]['data']['m_Parent']['rid']
 for i,r in old.items():
  if i!=serialid and 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('world binding changed',pid,i)
 save_document(W,pid,doc,sid)
# Keep table columns equal and stretch only the list ancestors, not labels or value groups.
pid=-930000000001003;doc=objs[G][pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree()
for i in [1004,1005]:override(rr[i]['data'],[prop(131083,en('row')),prop(131073,en('stretch'))])
for i in [1015,1016,1018,1020,1025,1027,1029,1062,1063]:horizontal_fill(rr[i]['data'])
# The rating rows use the same two-edge arrangement, with native text and bindings.
for i in [1021,1030,1050,1065,1083,1101]:horizontal_fill(rr[i]['data'])
for i in [1105,1115]:
 override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131083,en('row')),prop(131074,en('stretch')),prop(131088,en('space-between'))])
for i,r in old.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
save_document(G,pid,doc,sid)
pid=-930000000001001;doc=objs[G][pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree()
for i in [1001,1002,1004,1006]:
 horizontal_fill(rr[i]['data']);override(rr[i]['data'],[prop(131083,en('column')),prop(131084,num(1))])
for i in [1008,1009]:
 # Explicit full-width rows plus padding avoid auto-width, shrink-to-content rows and overflowing margins.
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131083,en('row')),prop(131073,en('center')),prop(131074,en('stretch')),prop(131088,en('space-between')),prop(131084,num(1)),prop(131085,num(0)),prop(131091,px(0)),prop(131092,px(0)),prop(131099,px(12)),prop(131100,px(12))])
for i in [1011,1014]:
 override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131073,en('stretch'))])
for i in [1012,1015]:
 override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131083,en('row')),prop(131073,en('center')),prop(131088,en('flex-end'))])
for i in [1017,1034]:override(rr[i]['data'],[prop(65546,en('middle-left'))])
for i,r in old.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('row binding changed',i)
save_document(G,pid,doc,sid)
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={x.path_id:x for x in UnityPy.load(b).objects};assert set(check)==set(hashes[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 for pid in [-930000000001001,-930000000001003]:
  d=check[pid].read_typetree();validate_ui(d,check[d['inlineSheet']['m_PathID']].read_typetree())
 (OUT/n).write_bytes(b)
# Layout budget at common panel widths: equal side regions and fixed-size central columns.
geometry=[]
for width in [1280,1440,1660,1920]:
 side=(width-710-2*25)/2;center_x=side+25;assert side>=260 and center_x+355==width/2
 col=(710-16)/3;assert col-24-48>150
 geometry.append({'panel_width':width,'left':side,'center':710,'right':side,'center_midpoint':center_x+355})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'center_width':710,'side_width_rule':'(available width - 710 - 50) / 2','native_expandable_width_overrides_removed':True,'scroll_viewports_stretch':True,'row_width':'100% with 12px inset at each edge','label_flex_grow':1,'value_flex_grow':0,'value_justify_content':'flex-end','all_data_bindings_preserved':True,'geometry_checks':geometry,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared files ready; game must exit before install'
try:
 for n,b in outputs.items():
  for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'geometry':geometry},ensure_ascii=True))
