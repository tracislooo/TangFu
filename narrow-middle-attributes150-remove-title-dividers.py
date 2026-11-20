from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/('narrow-attributes150-remove-orphan-heading-dividers-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
for n in [W,G]:assert before[GAME/n]==before[SKIN/n]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env={n:UnityPy.load(before[GAME/n]) for n in [W,G]};objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()};hashes={n:{i:sha(o.get_raw_data()) for i,o in obs.items()} for n,obs in objs.items()};changed={W:{},G:{}};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3};newwidth=710
for pid in [-930000000001001,-930000000001003]:
 doc=objs[W][pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree();settingsid=rr[1002]['data']['m_SerializedData']['rid'];settings=rr[settingsid]['data']['Settings']['m_settings'];assert settings[2]['PredefinedSize']==860;settings[2].update(PredefinedSize=710.0,UsePredefinedOnly=1)
 override(rr[1009]['data'],[prop(131105,px(710)),prop(131097,px(710)),prop(131095,px(710)),prop(131082,px(710)),prop(131084,num(0)),prop(131085,num(0))])
 # Follow the actual ancestry, including the inner SIScrollView and the template with min-width=850.
 i=1040;ancestors=[]
 while i!=1009:
  ancestors.append(i);override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131084,num(1)),prop(131085,num(1)),prop(131074,en('stretch'))]);i=rr[i]['data']['m_Parent']['rid']
 for i,r in old.items():
  if i==settingsid:
   x=copy.deepcopy(rr[i]);x['data']['Settings']=r['data']['Settings'];assert x==r
  elif 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('binding modified',pid,i)
 validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);objs[W][sid].save_typetree(sheet);changed[W][pid]=doc;changed[W][sid]=sheet
# Both goalkeeper branches share this private attributes table.
tablepid=-930000000001003;doc=objs[G][tablepid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree();removed=[]
# Only dividers directly paired with hidden SIText headings are orphaned.
for r in list(rr.values()):
 a=r.get('data',{});ix=a.get('m_RuleIndex',-1)
 if a.get('m_FullTypeName')!='SI.Bindable.SIText' or ix<0:continue
 hidden=any(p['m_Id']==131081 and p['m_Values'][0]['m_ValueType']==7 and sheet['strings'][p['m_Values'][0]['valueIndex']]=='none' for p in sheet['m_Rules'][ix]['m_Properties'])
 if not hidden:continue
 siblings=rr[a['m_Parent']['rid']]['data']['m_Children'];at=siblings.index({'rid':r['rid']})
 for c in siblings[max(0,at-1):at+2]:
  target=rr[c['rid']]
  if target['data'].get('m_TemplateAlias')=='layout-divider-solid-horizontal':removed.append(c['rid'])
removed=sorted(set(removed));assert len(removed)==9,removed
removedrefs=[]
for i in removed:
 a=rr[i]['data'];rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});removedrefs += [i,a['m_SerializedData']['rid']]
for i in removedrefs:rr.pop(i)
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removedrefs]
columns=[1007,1008,1009,1011,1012,1013]
for i in [1001,1002,1004,1005]:override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131085,num(1))])
for j,i in enumerate(columns):
 override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131095,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131073,en('stretch')),prop(131091,px(0)),prop(131092,px(8 if j%3<2 else 0))])
for i,r in list(rr.items()):
 a=r.get('data',{})
 if 'm_Parent' not in a or i in [1000,1001,1002,1004,1005]+columns:continue
 typ=a.get('m_FullTypeName','')
 if typ=='UnityEngine.UIElements.VisualElement' and not a.get('m_Children'):continue
 if typ in ['UnityEngine.UIElements.VisualElement','SI.Bindable.SIVisible','SI.Bindable.BindableSwitchElement','SI.Bindable.StreamedObjectList']:
  override(a,[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131085,num(1)),prop(131074,en('stretch'))])
for i,r in old.items():
 if i in removedrefs:continue
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('table binding changed',i)
assert rr[1039]['data']['m_TemplateAlias']=='layout-divider-solid-horizontal'  # visible Set Pieces title keeps its own divider
validate_ui(doc,sheet);objs[G][tablepid].save_typetree(doc);objs[G][sid].save_typetree(sheet);changed[G][tablepid]=doc;changed[G][sid]=sheet
# A smaller column must also constrain its virtualised row, label and badge containers.
rowpid=-930000000001001;doc=objs[G][rowpid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[G][sid].read_typetree()
for i in [1001,1002,1004,1006]:override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131085,num(1)),prop(131074,en('stretch'))])
for i in [1008,1009]:
 override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131084,num(0)),prop(131085,num(1)),prop(131074,en('stretch')),prop(131091,px(0)),prop(131092,px(0)),prop(131099,px(8)),prop(131100,px(8))])
for i in [1011,1014]:override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
for i in [1012,1015]:override(rr[i]['data'],[prop(131105,px(48)),prop(131097,px(48)),prop(131095,px(48)),prop(131084,num(0)),prop(131085,num(0))])
for i in [1017,1023,1034]:override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131085,num(1))])
for i,r in old.items():
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('row binding changed',i)
validate_ui(doc,sheet);objs[G][rowpid].save_typetree(doc);objs[G][sid].save_typetree(sheet);changed[G][rowpid]=doc;changed[G][sid]=sheet
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
 check={x.path_id:x for x in UnityPy.load(b).objects};assert set(check)==set(hashes[n])
 for i,h in hashes[n].items():
  if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
 for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
 for pid in [-930000000001001,-930000000001003]:
  d=check[pid].read_typetree();validate_ui(d,check[d['inlineSheet']['m_PathID']].read_typetree())
 (OUT/n).write_bytes(b)
# Fixed badge width and shrinkable labels fit the narrowed equal columns without horizontal overflow.
column=(710-16)/3;assert column-16-48>0;assert abs((860-16)/3-column-50)<1e-6
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'old_center_width':860,'new_center_width':710,'reduction_px':150,'outer_and_inner_template_constraints_updated':True,'old_template_min_width_850_removed':True,'goalkeeper_and_outfielder_columns':'equal flex columns, min-width=0, shrink=1','row_width':'100%, min-width=0, padding instead of overflowing margins','badge_width':48,'nominal_attribute_column_width':column,'orphan_dividers_removed':removed,'visible_set_pieces_divider_preserved':True,'all_serialized_value_bindings_preserved':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared resources ready; exit game before install'
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
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'center_width':710,'reduced_by':150,'orphan_dividers_removed':len(removed),'both_player_types_adjusted':True},ensure_ascii=True))
