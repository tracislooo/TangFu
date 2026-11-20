from pathlib import Path
import sys, copy, ast, json, hashlib, datetime, subprocess, struct, zlib
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'

OUT=R/('overview-attributes-width640-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();before={p:p.read_bytes() for p in [GAME/W,SKIN/W]};assert before[GAME/W]==before[SKIN/W]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir();(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/G,SKIN/G,GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env=UnityPy.load(before[GAME/W]);objs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in objs.items()};changed={}
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
def properties(s,a):return {p['m_Id']:[s[poolmap[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in poolmap else v for v in p['m_Values']] for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties']}
for pid in [-930000000001001,-930000000001003]:
 doc=objs[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[sid].read_typetree();oldp=properties(sheet,rr[1009]['data']);assert oldp[131105][0]['value']==710
 override(rr[1009]['data'],[prop(131105,px(640)),prop(131097,px(640)),prop(131095,px(640)),prop(131082,px(640)),prop(131084,num(0)),prop(131085,num(0))])
 i=1040
 while i!=1009:
  p=properties(sheet,rr[i]['data']);assert p[131105][0]=={'unit':2,'value':100.0} and p[131097][0]['value']==0;i=rr[i]['data']['m_Parent']['rid']
 for i,r in rr.items():
  if i!=1009:assert r==old[i],('unrelated page element changed',i)
 validate_ui(doc,sheet);objs[pid].save_typetree(doc);objs[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet
# Both player branches fill their parent and divide the actual 640px width into three equal columns.
go={o.path_id:o for o in UnityPy.load(str(GAME/G)).objects};table=go[-930000000001003].read_typetree();tr={r['rid']:r for r in table['references']['RefIds']};ts=go[table['inlineSheet']['m_PathID']].read_typetree()
for i in [1001,1002,1004,1005]:assert properties(ts,tr[i]['data'])[131105][0]=={'unit':2,'value':100.0}
for i in [1007,1008,1009,1011,1012,1013]:
 p=properties(ts,tr[i]['data']);assert p[131084]==[1.0] and p[131082][0]['value']==0 and p[131097][0]['value']==0
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs)
for i,h in hashes.items():
 if i not in changed:assert sha(check[i].get_raw_data())==h
for i,d in changed.items():assert check[i].read_typetree()==d
for pid in [-930000000001001,-930000000001003]:
 d=check[pid].read_typetree();validate_ui(d,check[d['inlineSheet']['m_PathID']].read_typetree())
(OUT/W).write_bytes(output)
report={'installed':False,'runtime_verified':False,'old_width':710,'new_width':640,'nominal_each_attribute_column':(640-16)/3,'goalkeeper_and_outfielder_actual_table_width_verified':True,'both_overview_pages_updated':True,'equal_side_layout_preserved':True,'native_labels_left_values_right_preserved':True,'other_page_elements_and_global_components_unchanged':True,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared resources ready; exit game before install'
try:
 for p in before:p.write_bytes(output);assert sha(p.read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;report['installed_verified']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'width':640,'each_column':(640-16)/3,'goalkeeper_and_outfielder':True},ensure_ascii=True))
