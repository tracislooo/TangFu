from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('restore-working-league-season-stats-context-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{x.path_id:x for x in e.objects} for n,e in env.items()};hashes={n:{i:sha(x.get_raw_data()) for i,x in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))


import struct

for p in [GAME/G,SKIN/G]:protected[p]=sha(p.read_bytes())
def refs(d):return {r['rid']:r for r in d['references']['RefIds']}
coach=objs[W][-6136493093000647937].read_typetree();cr=refs(coach)
source_node=copy.deepcopy(cr[1109]);source_component_sd=copy.deepcopy(cr[1157]);source_parent_sd=copy.deepcopy(cr[1113])
assert cr[1078]['data']['m_FullTypeName']=='SI.UI.ComponentElement'
assert source_node['data']['m_FullTypeName']=='SI.Bindable.BindingRemapperComponent'
assert [(m['from'],m['to']['m_path']) for m in source_component_sd['data']['Mappings']]==[('competition','Player.Division'),('seasonStats','Player.SeasonStats.SeasonStatsSelectedCompetitionsData')]
audits=[]
for pid in [-940000000007000,-940000000007002]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);original=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree();root=rr[1041]['data'];oldsd=root['m_SerializedData']['rid']
 assert root['m_FullTypeName']=='SI.Bindable.BindingRemapper'
 rid=max(rr)+1;csid=rid+1;ident=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 component=copy.deepcopy(source_node);component['rid']=rid;component['data'].update(m_Id=ident,m_Parent={'rid':1041},m_ParentId=root['m_Id'])
 component['data']['m_Properties']=[{'name':'mappings','value':'competition:person.Division:comp,seasonStats:person.SeasonStats.SeasonStatsSelectedCompetitionsData:seasonstatsselectedcompetitions'}]
 cs=copy.deepcopy(source_component_sd);cs['rid']=csid;cs['data']['uxmlAssetId']=ident
 for mp in cs['data']['Mappings']:mp['to']['m_path']='person.'+mp['to']['m_path'].removeprefix('Player.')
 ps=copy.deepcopy(source_parent_sd);ps['rid']=oldsd;ps['data'].update(uxmlAssetId=root['m_Id'],name='OverviewLeagueSeasonStatsNativeComponent',name_UxmlAttributeFlags=1,m_components=[{'rid':csid}],m_components_UxmlAttributeFlags=1)
 rr[oldsd].clear();rr[oldsd].update(ps);root['m_FullTypeName']='SI.UI.ComponentElement';root['m_Children'].insert(0,{'rid':rid})
 doc['references']['RefIds'].extend([component,cs]);rr[rid]=component;rr[csid]=cs
 for i,r in original.items():
  if i not in [1041,oldsd]:assert rr[i]==r,('existing number/formatter/line changed',i)
 assert len([r for r in rr.values() if r.get('data',{}).get('name','').startswith('SeasonStatValue_')])==12
 assert len([r for r in rr.values() if r.get('data',{}).get('name','').startswith('SeasonStatsRowDivider')])==4
 validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);changed[W][pid]=doc
 audits.append({'widget':pid,'root_component':1041,'native_remapper_node':rid,'native_remapper_sd':csid,'mappings':cs['data']['Mappings']})
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
 if i not in changed[W]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
for i,d in changed[W].items():
 assert check[i].read_typetree()==d;validate_ui(d,check[d['inlineSheet']['m_PathID']].read_typetree())
(OUT/W).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'working_reference':'add-league-stats-v30.py native CoachReportBlock league statistics component','native_coach_component_source':-6136493093000647937,'competition_context_restored':'person.Division','statistics_context':'person.SeasonStats.SeasonStatsSelectedCompetitionsData','native_component_type':'SI.UI.ComponentElement + SI.Bindable.BindingRemapperComponent','twelve_text_bindings_and_native_number_formatters_unchanged':True,'four_row_dividers_unchanged':True,'layout_unchanged':True,'widgets':audits,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared files ready; game must exit before install'
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
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'old_native_league_component_restored':True},ensure_ascii=True))

