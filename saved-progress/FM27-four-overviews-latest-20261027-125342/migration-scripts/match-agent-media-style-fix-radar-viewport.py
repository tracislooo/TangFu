from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();OUT=R/('match-personal-info-style-fix-radar-box-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
before={p:p.read_bytes() for p in [GAME/W,SKIN/W]};assert before[GAME/W]==before[SKIN/W]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir();(folder/W).write_bytes(b)
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-backgrounds_assets_common.bundle',GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',GAME/'ui-tileslayouts_assets_all.bundle',GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
e=UnityPy.load(before[GAME/W]);o={x.path_id:x for x in e.objects};hashes={i:sha(x.get_raw_data()) for i,x in o.items()};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
source=o[-930000000001001].read_typetree();sr={r['rid']:r for r in source['references']['RefIds']};ss=o[source['inlineSheet']['m_PathID']].read_typetree();changed={};audits=[]
def copy_rule(r):
 ix=r['data'].get('m_RuleIndex',-1)
 if ix<0:return -1
 p=copy.deepcopy(ss['m_Rules'][ix])
 for pr in p['m_Properties']:
  for h in pr['m_Values']:
   if h['m_ValueType']==1:continue
   pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
 sheet['m_Rules'].append(p);return len(sheet['m_Rules'])-1
for pid in [-930000000001001,-930000000001003]:
 doc=o[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=o[sid].read_typetree()
 def sd(i):return rr.get(rr[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 def named(n):
  matches=[r['rid'] for r in rr.values() if 'm_Parent' in r.get('data',{}) and sd(r['rid']).get('name')==n];assert len(matches)==1,(n,matches);return matches[0]
 def st(i,p):override(rr[i]['data'],p)
 auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3};zero=[prop(262150,px(0)),prop(262151,px(0))]
 # Copy the actual adjacent row and text styling instead of approximating its font.
 for n in ['AgentFrame','MediaDescriptionFrame','InternationalMediaOpinionFrame']:
  i=named(n);rr[i]['data']['m_Classes']=copy.deepcopy(sr[1087]['data']['m_Classes']);rr[i]['data']['m_RuleIndex']=copy_rule(sr[1087]);st(i,[prop(131088,en('flex-start')),prop(131105,pct(100)),prop(131090,px(0)),prop(131093,px(0))])
 for n in ['AgentFrameText','MediaDescriptionFrameText','InternationalMediaOpinionFrameText']:
  i=named(n);rr[i]['data']['m_Classes']=copy.deepcopy(sr[1096]['data']['m_Classes']);rr[i]['data']['m_RuleIndex']=copy_rule(sr[1096]);st(i,[prop(131105,auto),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(0)),prop(65546,en('middle-left')),prop(65552,en('nowrap'))])
 for n in ['PersonAgentText','PersonNoAgentText','PersonMediaDescriptionText','PersonInternationalMediaOpinionText']:
  i=named(n);rr[i]['data']['m_Classes']=copy.deepcopy(sr[1097]['data']['m_Classes']);rr[i]['data']['m_RuleIndex']=copy_rule(sr[1097]);st(i,zero+[prop(131105,auto),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(1)),prop(65546,en('middle-left')),prop(65552,en('nowrap'))])
 gate=named('AgentNullSwitch');st(gate,zero+[prop(131105,auto),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(1)),prop(131088,en('flex-start')),prop(65537,{'m_ValueType':1,'valueIndex':0})])
 # The renderer collapsed the percentage height: provide a concrete viewport at every level.
 if pid==-930000000001001:
  st(1173,[prop(131102,en('relative')),prop(131087,px(250)),prop(131096,px(250)),prop(131094,px(250))])
  st(1026,[prop(131102,en('absolute')),prop(131089,px(252)),prop(131103,px(0)),prop(131104,px(8)),prop(131075,auto),prop(131105,auto),prop(131097,px(0)),prop(131095,none),prop(131087,px(234)),prop(131096,px(234)),prop(131094,px(234)),prop(131084,num(0)),prop(131085,num(0)),prop(131073,en('stretch')),prop(131088,en('center')),prop(458768,en('visible'))])
  st(1043,[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,none),prop(131087,px(234)),prop(131096,px(234)),prop(131094,px(234)),prop(131091,px(0)),prop(131092,px(0)),prop(131084,num(0)),prop(131085,num(0)),prop(131074,en('stretch')),prop(458768,en('visible'))]);sd(1043).update(SpiderChartRadiusPercentage=38.0,LabelDistanceFromChart=20.0)
 for i,r in old.items():assert rr[i].get('data',{}).get('TextBinding')==r.get('data',{}).get('TextBinding'),('value/translation binding changed',pid,i)
 for n in ['AgentFrameText','MediaDescriptionFrameText','InternationalMediaOpinionFrameText']:assert rr[named(n)]['data']['m_Classes']==sr[1096]['data']['m_Classes']
 for n in ['PersonAgentText','PersonMediaDescriptionText','PersonInternationalMediaOpinionText']:assert rr[named(n)]['data']['m_Classes']==sr[1097]['data']['m_Classes']
 validate_ui(doc,sheet);o[pid].save_typetree(doc);o[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet;audits.append({'page':pid,'rows_match_native_personality_style':True,'left_aligned_values':True,'row_background_removed':True,'bindings_preserved':True})
output=e.file.save(packer='lz4');check={x.path_id:x for x in UnityPy.load(output).objects};assert set(check)==set(hashes)
for i,h in hashes.items():
 if i not in changed:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',i)
for i,d in changed.items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():assert p.read_bytes()==b
(OUT/W).write_bytes(output);report={'installed':False,'runtime_verified':False,'pages':audits,'radar_viewport':{'left':252,'right':0,'top':8,'height':234,'child_height':234,'header_height':250,'radius_percent':38,'label_distance':20},'after_sha256':sha(output)};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Game must exit before installation'
try:
 for p in before:p.write_bytes(output);assert p.read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'matched_personal_info_style':True,'radar_explicit_height':234,'catalog_and_background_unchanged':True},ensure_ascii=True))
