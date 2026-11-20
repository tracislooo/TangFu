from pathlib import Path
import sys, copy, ast, json, hashlib, datetime, subprocess, struct, zlib
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
PID=-940000000005000;SID=-940000000005001;KEY='1d1704ae44cb5b7ba38367bc28362460'
OUT=R/('overview-pitch-comparison-half-layout-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
before={p:(p.read_bytes()) for p in [GAME/G,SKIN/G]}
assert before[GAME/G]==before[SKIN/G]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir();(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/W,SKIN/W,GAME/'ui-backgrounds_assets_common.bundle',SKIN/'ui-backgrounds_assets_common.bundle',GAME/'ui-tileslayouts_assets_all.bundle',SKIN/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
env=UnityPy.load(before[GAME/G]);objs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data()) for i,o in objs.items()}
oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
doc=objs[PID].read_typetree();sheet=objs[SID].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};original=copy.deepcopy(rr)
native=objs[-4928795461599700197].read_typetree();nr={r['rid']:r for r in native['references']['RefIds']}
assert doc['inlineSheet']['m_PathID']==SID and rr[1007]['data']['m_Children']==[{'rid':2000},{'rid':2002},{'rid':2004}]
auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
def sd(i):return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
def move(i,parent):
 a=rr[i]['data'];rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});a['m_Parent']={'rid':parent};rr[parent]['data']['m_Children'].append({'rid':i})
removed=[]
def remove_subtree(i):
 a=rr[i]['data']
 for c in list(a.get('m_Children',[])):remove_subtree(c['rid'])
 rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i})
 removed.append(i)
 sid=a.get('m_SerializedData',{}).get('rid')
 if sid is not None:removed.append(sid);rr.pop(sid)
 rr.pop(i)
# Left column stacks pitch and comparison; right column retains its phase buttons and roles.
move(2006,2000)
remove_subtree(2004)
# Replace toggle-driven visibility with an ordinary frame, retaining its child setter and table.
serialid=rr[2006]['data']['m_SerializedData']['rid'];replacement=copy.deepcopy(rr[2001]);replacement['rid']=serialid
replacement['data'].update(uxmlAssetId=rr[2006]['data']['m_Id'],name='OverviewAlwaysVisibleComparisonContent',name_UxmlAttributeFlags=1)
rr[serialid].clear();rr[serialid].update(replacement);rr[2006]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
sd(2000)['name']='OverviewHorizontalPitchAndComparisonColumn'
rr[1018]['data']['ValueVariables']=[v for v in rr[1018]['data']['ValueVariables'] if v['m_name']!='showTeamCompareTable']
for p in rr[1006]['data']['m_Properties']:
 if p['name']=='value-vars':p['value']=p['value'].replace('{showTeamCompareTable}{Bool|1|}','')
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
doc['m_Name']='OverviewHorizontalPitchComparisonHalfLayout';sheet['m_Name']=doc['m_Name']+'_Style'
doc['m_ContentHash']=struct.unpack('<i',struct.pack('<I',zlib.crc32(b'fm27-overview-horizontal-pitch-comparison-half-layout')))[0]
for i in [2000,2002]:
 override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131092,px(8 if i==2000 else 0))])
# Restore both native landscape geometry and its native image binding. The aspect ratio is 200:140.
rr[1022]['data']['m_Classes']=copy.deepcopy(nr[1022]['data']['m_Classes'])
rr[1023]['data']['m_Classes']=copy.deepcopy(nr[1023]['data']['m_Classes'])
override(rr[1010]['data'],[prop(131101,pct(70)),prop(131087,px(0)),prop(131096,px(0)),prop(131094,none),prop(131090,px(8))])
for i in [1022,1023]:
 override(rr[i]['data'],[prop(131081,en('flex')),prop(131102,en('absolute')),prop(131089,px(0)),prop(131103,px(0)),prop(131104,px(0)),prop(131080,px(0)),prop(131105,auto),prop(131087,auto),prop(131097,px(0)),prop(131095,none),prop(131096,px(0)),prop(131094,none),prop(262150,px(0)),prop(262151,px(0))])
sd(1023).update(Orientation=1,Orientation_UxmlAttributeFlags=1)
override(rr[2006]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131096,px(0)),prop(131083,en('column')),prop(131073,en('stretch')),prop(131074,en('stretch')),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131093,px(8))])
# Give the selected-position caption its native centered alignment below the pitch.
override(rr[1038]['data'],[prop(65546,en('middle-center'))])
assert 'showTeamCompareTable' not in json.dumps(doc)
assert rr[1007]['data']['m_Children']==[{'rid':2000},{'rid':2002}]
assert rr[2000]['data']['m_Children']==[{'rid':1009},{'rid':1010},{'rid':1011},{'rid':2006}]
assert rr[2002]['data']['m_Children']==[{'rid':1074},{'rid':1012}]
assert rr[2006]['data']['m_Children']==[{'rid':1064}]
for i,r in original.items():
 if i in removed or i in [1018,serialid]:continue
 if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
  if i==rr[1023]['data']['m_SerializedData']['rid']:
   restored=copy.deepcopy(rr[i]);restored['data']['Orientation']=r['data']['Orientation'];assert restored==r
  elif i==rr[1038]['data']['m_SerializedData']['rid'] or i==2001:continue
  else:assert rr[i]==r,('unrelated behavior changed',i)
validate_ui(doc,sheet);objs[PID].save_typetree(doc);objs[SID].save_typetree(sheet)
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs)
for i,h in hashes.items():
 if i not in [PID,SID]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
assert check[PID].read_typetree()==doc and check[SID].read_typetree()==sheet
validate_ui(check[PID].read_typetree(),check[SID].read_typetree())
# Both installed overview pages already resolve to this private template; no catalog changes are needed.
world={o.path_id:o for o in UnityPy.load(str(GAME/W)).objects}
for pagepid in [-930000000001001,-930000000001003]:
 page=world[pagepid].read_typetree();assert next(u for u in page['m_Usings'] if u['alias']=='role_selector-large')['path']==KEY
(OUT/G).write_bytes(output)
report={'installed':False,'runtime_verified':False,'private_guid':KEY,'left_right_ratio':[50,50],'gap_px':8,'pitch_aspect_ratio':[200,140],'pitch_orientation':'native landscape 1','comparison_button_removed':True,'comparison_visibility_switch_removed':True,'data_and_input_bindings_preserved':True,'both_overviews_use_same_private_selector':True,'unrelated_objects_verified_unchanged':True,'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared files ready; exit game before install'
try:
 for p in before:p.write_bytes(output);assert sha(p.read_bytes())==sha(output)
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
print(json.dumps({'installed':True,'output':str(OUT),'ratio':[50,50],'comparison_direct':True,'pitch':'landscape'},ensure_ascii=True))
