from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest();BASE=R/'narrow-attributes150-remove-orphan-heading-dividers-20261021-044941'/'backup-game'
OUT=R/('coloured-goalkeeper-outfield-season-stats-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for n in [W,G] for p in [GAME/n,SKIN/n]}
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
src=ast.parse((R/'equal-role-comparison-biography-scout-icons.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'refs','sd','named','move','add_pair'}],type_ignores=[]),'tree helpers','exec'))
native=objs[W][-648337528654704265].read_typetree();nr=refs(native);native_names={r.get('data',{}).get('name'):r['data'] for r in nr.values() if r.get('data',{}).get('name')}
palette={'attack':(255,95,95),'passing':(80,180,255),'defence':(100,215,125),'other':(255,215,80)}
outfield=[('GamesWonAndPlayed','获胜/场次','MatchesWonText','other'),('PlayerOfTheMatchAwards','当场最佳','PotMAwText','other'),('Goals','进球','OutfielderStatsGoalsText','attack'),('ExpectedGoalsPer90','预期进球/90分钟','ExpectedGoalsPer90Text','attack'),('ShotsOnTargetPer90','射正/90分钟','ShotsOnTargetPer90Text','attack'),('ChancesCreated','创造机会','ChancesCreatedText','passing'),('ExpectedAssistsPer90','预期助攻/90分钟','ExpectedAssistsPer90Text','passing'),('KeyPasses','关键传球','KeyPassesText','passing'),('PassCompletedPer90','传球成功/90分钟','PassCompletedPer90Text','passing'),('KeyTackles','关键抢断','KeyTacklesText','defence'),('TacklesCompletedPer90','场均抢断成功次数','TacklesCompletedPer90Text','defence'),('KeyHeadersPer90','关键头球/90分钟','KeyHeadersPer90Text','defence')]
goalkeeper=[('GamesWonAndPlayed','获胜/场次','MatchesWonText','other'),('PlayerOfTheMatchAwards','当场最佳','PotMAwText','other'),('Clearances','解围','ClearancesText','defence'),('ExpectedGoalsPreventedPer90','预期阻止进球/90分钟','ExpectedGoalsPreventedPer90Text','defence'),('TotalSavesPer90','扑救/90分钟','TotalSavesPer90Text','defence'),('ConcededPer90','失球/90分钟','ConcededPer90Text','defence'),('PossessionWonPer90','赢得球权/90分钟','PossessionWonPer90Text','defence'),('PossessionLostPer90','丢失球权/90分钟','PossessionLostPer90Text','other'),('PassCompletedPer90','传球成功/90分钟','PassCompletedPer90Text','passing'),('PenaltiesFaced','点球失球/面对次数','PenaltiesFacedText','defence'),('MinutesPerGoalConceded','失球间隔(分钟)','MinutesPerGoalConcededText','defence'),('GoalMistakes','致命失误','GoalMistakesText','other')]
assert all(next(i for i,x in enumerate(outfield) if x[0]==field)==next(i for i,x in enumerate(goalkeeper) if x[0]==field) for field in ['GamesWonAndPlayed','PlayerOfTheMatchAwards','PassCompletedPer90'])
audits=[]
for pid in [-940000000007000,-940000000007002]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=objs[W][sid].read_typetree();compact=pid==-940000000007002
 next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 sample=named('SeasonStatCell_Goals');blank=copy.deepcopy(rr[sample]);blanksd=copy.deepcopy(rr[blank['data']['m_SerializedData']['rid']]);textnode=copy.deepcopy(rr[named('SeasonStatTitle_Goals')]);textsd=copy.deepcopy(rr[textnode['data']['m_SerializedData']['rid']]);valuenode=copy.deepcopy(rr[named('SeasonStatValue_Goals')]);valuesd=copy.deepcopy(rr[valuenode['data']['m_SerializedData']['rid']])
 # Reuse the progressive-pass slot for the native wins/appearances formatter.
 for prefix in ['SeasonStatCell_','SeasonStatTitle_','SeasonStatValue_']:
  i=named(prefix+'ProgressivePassesPer90');sd(i)['name']=prefix+'GamesWonAndPlayed'
 root=1041;rowids=[named('SeasonStatsRow'+str(i)) for i in range(1,5)];lineids=[named('SeasonStatsRowDivider'+str(i)) for i in range(1,5)]
 for j,(field,title,source,category) in enumerate(outfield):
  cell=named('SeasonStatCell_'+field);label=named('SeasonStatTitle_'+field);value=named('SeasonStatValue_'+field)
  sd(label).update(text=title,DebugDisplay=title,text_UxmlAttributeFlags=1)
  sd(value)['TextBinding']=copy.deepcopy(native_names[source]['TextBinding']);sd(value)['TextBinding_UxmlAttributeFlags']=native_names[source]['TextBinding_UxmlAttributeFlags']
  override(rr[value]['data'],[prop(65536,color(*palette[category]))]);rr[cell]['data']['m_Parent']={'rid':rowids[j//3]}
 for j,i in enumerate(rowids):rr[i]['data']['m_Children']=[{'rid':named('SeasonStatCell_'+x[0])} for x in outfield[j*3:j*3+3]]+[{'rid':lineids[j]}]
 switch_source=nr[1029];switch_sd=nr[switch_source['data']['m_SerializedData']['rid']]
 sw=add_pair(switch_source,switch_sd,root,'SeasonStatsIsGoalkeeperSwitch');sd(sw)['Binding']['m_direct']['Path']['m_path']='person.IsGoalkeeper'
 of=add_pair(blank,blanksd,sw,'SeasonStatsOutfielderPanel');gk=add_pair(blank,blanksd,sw,'SeasonStatsGoalkeeperPanel')
 for i in rowids:move(i,of)
 for i in [sw,of,gk]:
  override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131087,px(91 if compact else 126)),prop(131096,px(91 if compact else 126)),prop(131083,en('column')),prop(131073,en('stretch')),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0)),prop(262151,px(0))])
 # Preserve the league-aware native binding component as the first child.
 components=[c for c in rr[root]['data']['m_Children'] if rr[c['rid']]['data'].get('m_FullTypeName')=='SI.Bindable.BindingRemapperComponent'];assert len(components)==1;rr[root]['data']['m_Children']=components+[{'rid':sw}]
 gkrows=[]
 for j in range(4):
  row=add_pair(blank,blanksd,gk,'GoalkeeperStatsRow'+str(j+1));gkrows.append(row)
  override(rr[row]['data'],[prop(131102,en('relative')),prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(22 if compact else 30)),prop(131096,px(22 if compact else 30)),prop(131094,px(22 if compact else 30)),prop(131083,en('row')),prop(131073,en('stretch')),prop(131084,num(0)),prop(131085,num(0)),prop(131090,px((1 if compact else 2) if j<3 else 0))])
 for j,(field,title,source,category) in enumerate(goalkeeper):
  cell=add_pair(blank,blanksd,gkrows[j//3],'GoalkeeperStatCell_'+field)
  override(rr[cell]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131083,en('column')),prop(131073,en('stretch'))])
  label=add_pair(textnode,textsd,cell,'GoalkeeperStatTitle_'+field);sd(label).update(text=title,DebugDisplay=title,text_UxmlAttributeFlags=1)
  if field=='MinutesPerGoalConceded':sd(label).update(tooltip='平均每个失球的场上间隔时间（分钟）',tooltip_UxmlAttributeFlags=1)
  override(rr[label]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(10 if compact else 18)),prop(131096,px(10 if compact else 18)),prop(131094,px(10 if compact else 18)),prop(65537,px(9)),prop(65536,color(160,160,160)),prop(65546,en('middle-center')),prop(65552,en('nowrap' if compact else 'normal')),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0))])
  v=add_pair(valuenode,valuesd,cell,'GoalkeeperStatValue_'+field);sd(v)['TextBinding']=copy.deepcopy(native_names[source]['TextBinding']);sd(v)['TextBinding_UxmlAttributeFlags']=native_names[source]['TextBinding_UxmlAttributeFlags']
  override(rr[v]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(12)),prop(131096,px(12)),prop(131094,px(12)),prop(65537,px(12)),prop(65536,color(*palette[category])),prop(65546,en('middle-center')),prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0))])
  assert sd(v)['TextBinding']==native_names[source]['TextBinding']
 for j,row in enumerate(gkrows):
  l=add_pair(blank,blanksd,row,'GoalkeeperStatsRowDivider'+str(j+1));override(rr[l]['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131103,px(0)),prop(131080,px(0)),prop(131087,px(1)),prop(131096,px(1)),prop(131094,px(1)),prop(131084,num(0)),prop(131085,num(0)),prop(458752,color(135,140,145,160))])
 assert rr[sw]['data']['m_Children']==[{'rid':of},{'rid':gk}]
 for field,title,source,category in outfield:assert sd(named('SeasonStatValue_'+field))['TextBinding']==native_names[source]['TextBinding']
 # Context and all original separators survive the branch split unchanged.
 componentid=components[0]['rid'];assert rr[componentid]==old[componentid]
 parent_sd=rr[root]['data']['m_SerializedData']['rid'];assert rr[parent_sd]==old[parent_sd]
 validate_ui(doc,sheet);objs[W][pid].save_typetree(doc);objs[W][sid].save_typetree(sheet);changed[W][pid]=doc;changed[W][sid]=sheet;audits.append({'widget':pid,'switch':sw,'outfield':of,'goalkeeper':gk,'compact':compact})
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
 if i not in changed[W]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',i)
for i,d in changed[W].items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
(OUT/W).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'installed':False,'runtime_verified':False,'palette':palette,'outfielder_order':outfield,'goalkeeper_order':goalkeeper,'shared_fields_same_slots':True,'goalkeeper_selector':'native person.IsGoalkeeper false=outfield true=goalkeeper','native_league_context_unchanged':True,'native_formatters_preserved':True,'conceded_interval_unit':'native minutes; not divided by 90','widgets':audits,'after_sha256':sha(output)}
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
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'outfield_stats':12,'goalkeeper_stats':12,'colours':4},ensure_ascii=True))
