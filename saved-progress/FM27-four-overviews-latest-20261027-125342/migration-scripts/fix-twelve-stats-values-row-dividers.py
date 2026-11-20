from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('fix-twelve-stats-values-row-dividers-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))


import struct

for p in [GAME/G,SKIN/G]:protected[p]=sha(p.read_bytes())
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='color'],type_ignores=[]),'color','exec'))
src=ast.parse((R/'equal-role-comparison-biography-scout-icons.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'refs','sd','named','move','remove','add_pair'}],type_ignores=[]),'tree helpers','exec'))
audit=[]
for pid in [-940000000007000,-940000000007002]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree()
 switches=[i for i,r in rr.items() if 'm_Parent' in r.get('data',{}) and sd(i).get('name','').startswith('SeasonStatAvailable_')];assert len(switches)==12
 direct_values=[]
 for switch in switches:
  field=sd(switch)['name'].removeprefix('SeasonStatAvailable_');v=named('SeasonStatValue_'+field);cell=rr[switch]['data']['m_Parent']['rid'];move(v,cell);remove(switch);direct_values.append(v)
  # Native SIText receives the original integer binding or native decimal formatter directly.
  assert rr[rr[v]['data']['m_SerializedData']['rid']]==old[old[v]['data']['m_SerializedData']['rid']]
 doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in rr]
 next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 sample=named('SeasonStatCell_Goals');node=copy.deepcopy(rr[sample]);serial=copy.deepcopy(rr[node['data']['m_SerializedData']['rid']]);lines=[]
 for j in range(4):
  row=named('SeasonStatsRow'+str(j+1));override(rr[row]['data'],[prop(131102,en('relative'))]);line=add_pair(node,serial,row,'SeasonStatsRowDivider'+str(j+1));lines.append(line)
  override(rr[line]['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131103,px(0)),prop(131080,px(0)),prop(131087,px(1)),prop(131096,px(1)),prop(131094,px(1)),prop(131084,num(0)),prop(131085,num(0)),prop(458752,color(135,140,145,160)),prop(262150,px(0)),prop(262151,px(0))])
 doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] in rr]
 assert not any(r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.BindableSwitchElement' for r in rr.values())
 assert len(direct_values)==12 and len(lines)==4
 validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);objs[W][sid].save_typetree(sheet);changed[W][pid]=doc;changed[W][sid]=sheet;audit.append({'widget':pid,'direct_value_nodes':direct_values,'divider_nodes':lines})
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
 if i not in changed[W]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',i)
for i,d in changed[W].items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
for a in audit:
 d=check[a['widget']].read_typetree();validate_ui(d,check[d['inlineSheet']['m_PathID']].read_typetree())
(OUT/W).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'numeric_reference_switches_removed':24,'native_numeric_text_bindings_and_formatters_preserved':True,'direct_display_values_per_widget':12,'bottom_dividers_per_widget':4,'layout_and_header_heights_preserved':True,'widgets':audit,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared resources ready; game must exit before install'
try:
 for folder in [GAME,SKIN]:(folder/W).write_bytes(output);assert sha((folder/W).read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'direct_values':12,'row_lines':4},ensure_ascii=True))
