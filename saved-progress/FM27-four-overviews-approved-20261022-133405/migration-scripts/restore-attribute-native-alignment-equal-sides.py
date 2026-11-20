from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('restore-native-attribute-alignment-equal-sides-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3};audits=[]
for pid in [-930000000001001,-930000000001003]:
 doc=objs[W][pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree();settingsid=rr[1002]['data']['m_SerializedData']['rid'];settings=rr[settingsid]['data']['Settings']['m_settings'];assert settings[2]['PredefinedSize']==710
 settings[0].update(PredefinedSize=380.0,Margin=0.0,Priority=0,UsePredefinedOnly=0);settings[4]=copy.deepcopy(settings[0]);settings[2]['UsePredefinedOnly']=1
 for i in [1007,1703]:override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131091,px(0)),prop(131092,px(0))])
 override(rr[1011]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131074,en('stretch'))])
 for i,r in old.items():
  if i==settingsid:
   a=copy.deepcopy(rr[i]);a['data']['Settings']=r['data']['Settings'];assert a==r
  elif 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('world binding changed',pid,i)
 assert settings[0]==settings[4];validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);objs[W][sid].save_typetree(sheet);changed[W][pid]=doc;changed[W][sid]=sheet;audits.append({'page':pid,'center_width':710,'equal_side_predefined_sizes':[380,380],'equal_side_flex':[1,1],'equal_side_basis':[0,0]})
baseline={x.path_id:x for x in UnityPy.load(str(BASE/G)).objects};removed=[1035,1043,1047,1055,1059,1082,1092,1096,1100]
# Restore the original table internals, retaining only responsive container constraints.
pid=-930000000001003;doc=baseline[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};current={r['rid']:r for r in objs[G][pid].read_typetree()['references']['RefIds']};sid=doc['inlineSheet']['m_PathID'];sheet=baseline[sid].read_typetree();removedrefs=[]
for i in removed:
 a=rr[i]['data'];assert a['m_TemplateAlias']=='layout-divider-solid-horizontal';rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});removedrefs += [i,a['m_SerializedData']['rid']]
for i in removedrefs:rr.pop(i)
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removedrefs]
for i in [1001,1002,1004,1005]:override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131085,num(1))])
for j,i in enumerate([1007,1008,1009,1011,1012,1013]):override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131073,en('stretch')),prop(131091,px(0)),prop(131092,px(8 if j%3<2 else 0))])
for i,r in rr.items():
 if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.StreamedObjectList':override(r['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131074,en('stretch'))])
for i,r in rr.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert r==current[i],('table value binding changed',i)
validate_ui(doc,sheet);objs[G][pid].save_typetree(doc);objs[G][sid].save_typetree(sheet);changed[G][pid]=doc;changed[G][sid]=sheet
# Use native spacing, labels and badges; row edges stretch, while its contents remain left/right aligned.
pid=-930000000001001;doc=baseline[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};current={r['rid']:r for r in objs[G][pid].read_typetree()['references']['RefIds']};sid=doc['inlineSheet']['m_PathID'];sheet=baseline[sid].read_typetree()
for i in [1001,1002,1004,1006]:override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131085,num(1)),prop(131074,en('stretch'))])
for i in [1008,1009]:override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131095,pct(100)),prop(131084,num(0)),prop(131085,num(1)),prop(131074,en('stretch')),prop(131088,en('space-between'))])
for i in [1011,1014]:override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(1))])
for i in [1017,1034]:override(rr[i]['data'],[prop(65546,en('middle-left'))])
for i,r in rr.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert r==current[i],('row value binding changed',i)
base_row={r['rid']:r for r in baseline[pid].read_typetree()['references']['RefIds']}
for i in [1012,1015,1020,1021,1025,1026,1032,1038]:assert rr[i]==base_row[i],('native right value block changed',i)
validate_ui(doc,sheet);objs[G][pid].save_typetree(doc);objs[G][sid].save_typetree(sheet);changed[G][pid]=doc;changed[G][sid]=sheet
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={x.path_id:x for x in UnityPy.load(b).objects};assert set(check)==set(hashes[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 for pid in [-930000000001001,-930000000001003]:
  d=check[pid].read_typetree();validate_ui(d,check[d['inlineSheet']['m_PathID']].read_typetree())
 (OUT/n).write_bytes(b)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'pages':audits,'center_width_retained':710,'attribute_name_alignment':'left','attribute_value_alignment':'right using native space-between rows and unchanged value containers','native_rating_row_layout_restored':True,'orphan_title_lines_still_removed':9,'all_value_bindings_preserved':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared files ready; game must exit before install'
try:
 for n,b in outputs.items():
  for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'center_width':710,'equal_sides':True,'native_attribute_alignment_restored':True},ensure_ascii=True))
