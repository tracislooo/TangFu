from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,subprocess,struct
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/('identity-order-centered-status-hidden-gap3-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for p in [GAME/W,SKIN/W]};assert before[GAME/W]==before[SKIN/W]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir();(folder/W).write_bytes(b)
protected={p:sha(p.read_bytes()) for n in ['ui-backgrounds_assets_common.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle'] for p in [GAME/n,SKIN/n]};protected.update({p:sha(p.read_bytes()) for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']})
e=UnityPy.load(before[GAME/W]);o={x.path_id:x for x in e.objects};hashes={i:sha(x.get_raw_data()) for i,x in o.items()};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','color','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
changed={};audits=[]
def sd(i):return rr.get(rr[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(n):
 matches=[r['rid'] for r in rr.values() if 'm_Parent' in r.get('data',{}) and sd(r['rid']).get('name')==n];assert len(matches)==1,(n,matches);return matches[0]
def st(i,ps):override(rr[i]['data'],ps)
def move(i,parent):
 old=rr[i]['data']['m_Parent']['rid'];rr[old]['data']['m_Children'].remove({'rid':i});rr[parent]['data']['m_Children'].append({'rid':i});rr[i]['data']['m_Parent']={'rid':parent}
def blank(parent,n,ps):
 global next_rid,next_id
 a=copy.deepcopy(blanknode);s=copy.deepcopy(blanksd);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=rule(ps),m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 s['data'].update(uxmlAssetId=next_id,name=n,name_UxmlAttributeFlags=1);next_id+=1;rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
def value(i,pid):
 props=sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'];p=next(p for p in reversed(props) if p['m_Id']==pid);h=p['m_Values'][0];return ('keyword',h['valueIndex']) if h['m_ValueType']==1 else sheet[poolmap[h['m_ValueType']]][h['valueIndex']]
for pid in [-930000000001001,-930000000001003]:
 doc=o[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=o[sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 blanknode=copy.deepcopy(rr[1011]);blanksd=copy.deepcopy(rr[blanknode['data']['m_SerializedData']['rid']]);auto={'m_ValueType':1,'valueIndex':2};zero=[prop(262150,px(0)),prop(262151,px(0))]
 if pid==-930000000001001:
  # Name / position+age -> one financial row -> paired personal rows -> nation+club.
  info=named('OverviewAgentMediaColumn');move(1199,1297)
  st(1199,zero+[prop(131083,en('row')),prop(131073,en('center')),prop(131088,en('flex-start')),prop(131105,pct(100)),prop(131087,px(26)),prop(131096,px(26)),prop(131084,num(0)),prop(131085,num(0)),prop(131093,px(1)),prop(131090,px(1))])
  st(1214,[prop(131105,auto),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,px(24)),prop(131092,px(8))])
  st(1215,[prop(131105,auto),prop(131082,px(0)),prop(131084,num(2)),prop(131085,num(1)),prop(131087,px(24)),prop(131096,px(24))])
  st(1237,[prop(131083,en('row')),prop(131073,en('center')),prop(131105,pct(100)),prop(131087,px(24)),prop(131096,px(24)),prop(131085,num(0))])
  for i in [1260,1261]:st(i,[prop(131105,auto),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,px(24)),prop(131096,px(24)),prop(131092,px(6 if i==1260 else 0)),prop(131074,en('stretch'))])
  st(1184,zero+[prop(131102,en('relative')),prop(131083,en('row')),prop(131073,en('flex-start')),prop(131105,pct(100)),prop(131087,px(68)),prop(131096,px(68)),prop(131093,px(0)),prop(131090,px(0))])
  st(1031,[prop(131105,pct(33)),prop(131097,px(0)),prop(131087,px(68)),prop(131096,px(68)),prop(131092,px(10)),prop(131085,num(1))])
  for i in [1049,1050]:st(i,[prop(131090,px(4))])
  st(1051,[prop(131090,px(0))])
  st(info,[prop(131105,auto),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,px(68)),prop(131096,px(68)),prop(131092,px(0))])
  st(named('AgentVisible'),[prop(131087,px(20)),prop(131090,px(4))]);st(named('PlayerMediaVisible'),[prop(131087,px(44))]);st(named('MediaDescriptionFrame'),[prop(131090,px(4))]);st(named('InternationalMediaOpinionFrame'),[prop(131090,px(0))])
  # Thin full-width separators between all four personal-information groups.
  sepbase=zero+[prop(131087,px(1)),prop(131096,px(1)),prop(131084,num(0)),prop(131085,num(0)),prop(458752,color(135,140,145,160))]
  sep1=blank(1184,'OverviewPersonalRowsDivider1',sepbase+[prop(131102,en('absolute')),prop(131089,px(0)),prop(131103,px(0)),prop(131104,px(21))])
  sep2=blank(1184,'OverviewPersonalRowsDivider2',sepbase+[prop(131102,en('absolute')),prop(131089,px(0)),prop(131103,px(0)),prop(131104,px(45))])
  sep3=blank(1297,'OverviewPersonalNationDivider',sepbase+[prop(131102,en('relative')),prop(131105,pct(100)),prop(131093,px(1)),prop(131090,px(2))])
  contractsep=blank(1297,'OverviewFinancialPersonalDivider',sepbase+[prop(131102,en('relative')),prop(131105,pct(100)),prop(131093,px(1)),prop(131090,px(2))])
  rr[1297]['data']['m_Children']=[{'rid':1171},{'rid':1199},{'rid':contractsep},{'rid':1184},{'rid':sep3},{'rid':1295}]
  st(1297,[prop(131093,px(12)),prop(131090,px(-12))]);st(1295,[prop(131087,px(48)),prop(131096,px(48)),prop(131093,px(0)),prop(131090,px(0))])
  # Shared horizontal centre for scouting/ability widgets, rings, and bans.
  st(1349,[prop(131105,px(240)),prop(131097,px(240)),prop(131073,en('center')),prop(131090,px(4))])
  st(1186,[prop(131105,pct(100)),prop(131073,en('center')),prop(131088,en('center'))])
  st(1203,[prop(131105,auto),prop(131097,px(0)),prop(131074,en('center')),prop(131084,num(0)),prop(131085,num(1)),prop(131073,en('center')),prop(131088,en('center'))])
  st(2242,[prop(131074,en('flex-start')),prop(131105,px(240)),prop(131097,px(240)),prop(131091,px(0)),prop(131092,px(0))])
  # Increase the chart while keeping a concrete viewport within the 250px header.
  st(1026,[prop(131104,px(4)),prop(131087,px(242)),prop(131096,px(242)),prop(131094,px(242))]);st(1043,[prop(131087,px(242)),prop(131096,px(242)),prop(131094,px(242))]);sd(1043).update(SpiderChartRadiusPercentage=41.0,LabelDistanceFromChart=14.0)
  assert rr[1199]['data']['m_Parent']=={'rid':1297};assert rr[1237]['data']['m_Children']==[{'rid':1260},{'rid':1261}]
  assert [r['rid'] for r in rr[1184]['data']['m_Children'] if r['rid'] in [1031,info]]==[1031,info]
 # Centre the three rings inside the same width as their bans list.
 status=named('OverviewTopRightStatusPanel');fitness=named('OverviewFitnessPercentRow');bans=named('OverviewTopRightBansScroll');width=240 if pid==-930000000001001 else 312
 st(fitness,[prop(131089,px((width-210)/2)),prop(131105,px(210))]);st(bans,[prop(131089,px(0)),prop(131105,px(width))])
 # The bottom of the 19px bar is y=32+2+19=53. The 1px divider +2px margin make a 3px gap.
 summary=named('RightHiddenSummaryGraphic');barline=named('RightHidden_OverviewHiddenBarLine');sep=named('RightHiddenSummarySeparator');listing=named('RightHiddenAttributesList')
 st(summary,[prop(131087,px(53)),prop(131096,px(53)),prop(131090,px(0))]);st(barline,[prop(131087,px(21))]);st(sep,[prop(131093,px(0)),prop(131090,px(2)),prop(131087,px(1)),prop(131096,px(1))]);st(listing,[prop(131093,px(0))])
 assert sum(value(i,p)['value'] for i,p in [(sep,131093),(sep,131087),(sep,131090),(listing,131093)])==3
 assert value(fitness,131089)['value']+value(fitness,131105)['value']/2==value(bans,131105)['value']/2
 for i,r in old.items():
  if 'UxmlSerializedData' in r.get('type',{}).get('class','') and i not in [rr.get(1043,{}).get('data',{}).get('m_SerializedData',{}).get('rid')]:assert rr[i]==r,('serialized data/binding changed',pid,i)
 assert [len(rr[named('RightHiddenAttributesColumn'+str(i))]['data']['m_Children']) for i in [1,2,3]]==[5,4,4]
 validate_ui(doc,sheet);o[pid].save_typetree(doc);o[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet
 audits.append({'page':pid,'hidden_gap_px':3,'status_column_width':width,'rings_center_x':width/2,'bans_center_x':width/2,'bindings_unchanged':True})
output=e.file.save(packer='lz4');check={x.path_id:x for x in UnityPy.load(output).objects};assert set(check)==set(hashes)
for i,h in hashes.items():
 if i not in changed:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',i)
for i,d in changed.items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():assert p.read_bytes()==b
(OUT/W).write_bytes(output);report={'installed':False,'runtime_verified':False,'pages':audits,'left_section_order':['position_age','price_wage_playing_time_horizontal','height_agent','reputation_media_description','personality_media_opinion','national_team_club'],'personal_information_groups':4,'separators_between_personal_groups':3,'financial_row_height':26,'personal_rows_height':68,'nation_club_height':48,'radar':{'height':242,'top':4,'radius_percent':41,'label_distance':14},'after_sha256':sha(output)};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Game must exit before installing'
try:
 for p in before:p.write_bytes(output);assert p.read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'hidden_gap':3,'personal_groups':4,'financial_row':'horizontal','radar_height':242,'centered_status':True},ensure_ascii=True))

