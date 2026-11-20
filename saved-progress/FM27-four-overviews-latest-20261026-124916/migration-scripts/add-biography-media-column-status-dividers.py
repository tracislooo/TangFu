from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,struct,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=R/('biography-media-third-column-status-dividers-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();before={p:p.read_bytes() for p in [GAME/W,SKIN/W]};assert before[GAME/W]==before[SKIN/W]
for p,b in before.items():
 folder=OUT/('backup-game' if p.parent==GAME else 'backup-skin');folder.mkdir();(folder/W).write_bytes(b)
protected={p:sha(p.read_bytes()) for n in ['ui-backgrounds_assets_common.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-tileslayouts_assets_all.bundle'] for p in [GAME/n,SKIN/n]};protected.update({p:sha(p.read_bytes()) for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']})
e=UnityPy.load(before[GAME/W]);o={x.path_id:x for x in e.objects};hashes={i:sha(x.get_raw_data()) for i,x in o.items()};oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','color','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
full=o[-930000000001001].read_typetree();fr={r['rid']:r for r in full['references']['RefIds']};tn=copy.deepcopy(fr[1097]);ts=copy.deepcopy(fr[tn['data']['m_SerializedData']['rid']])
bio=o[-2572099601129076466].read_typetree();br={r['rid']:r for r in bio['references']['RefIds']};personal=o[-1336215414551004732].read_typetree();pr={r['rid']:r for r in personal['references']['RefIds']};media=next(r['data'] for r in pr.values() if r.get('data',{}).get('name')=='PersonMediaHandlingText')
fields=[('BiographyOverallCareerStats','生涯总统计',br[1103]['data'],'Person.BiographyCareerStatsString'),('BiographyCareerMilestones','生涯里程碑',br[1098]['data'],'Person.BiographyMilestonesString'),('OverviewMediaHandling','媒体处理',media,'Person.MediaHandling')]
for n,t,s,p in fields:assert s['TextBinding']['m_direct']['Path']['m_path']==p
changed={};audits=[]
def sd(i):return rr.get(rr[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(n):
 matches=[r['rid'] for r in rr.values() if 'm_Parent' in r.get('data',{}) and sd(r['rid']).get('name')==n];assert len(matches)==1,(n,matches);return matches[0]
def st(i,ps):override(rr[i]['data'],ps)
def pair(nt,ntsd,parent,n,ps):
 global next_rid,next_id
 a=copy.deepcopy(nt);s=copy.deepcopy(ntsd);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=rule(ps),m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 s['data'].update(uxmlAssetId=next_id,name=n,name_UxmlAttributeFlags=1);next_id+=1;rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
def blank(parent,n,ps):return pair(blanknode,blanksd,parent,n,ps)
for pid in [-930000000001001,-930000000001003]:
 doc=o[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=o[sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 blanknode=copy.deepcopy(rr[1011]);blanksd=copy.deepcopy(rr[blanknode['data']['m_SerializedData']['rid']]);zero=[prop(262150,px(0)),prop(262151,px(0))];auto={'m_ValueType':1,'valueIndex':2}
 if pid==-930000000001001:
  parent=1184;col=blank(parent,'OverviewBiographyMediaColumn',zero+[prop(131102,en('relative')),prop(131083,en('column')),prop(131105,pct(25)),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(1)),prop(131087,px(68)),prop(131096,px(68)),prop(131099,px(6))]);gap=4
  st(named('OverviewAgentMediaColumn'),[prop(131092,px(6))])
 else:
  parent=named('SimplePortraitHeader');col=blank(parent,'OverviewBiographyMediaColumn',zero+[prop(131102,en('relative')),prop(131083,en('column')),prop(131105,px(200)),prop(131095,px(200)),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(1)),prop(131087,px(60)),prop(131096,px(60)),prop(131091,px(8))]);gap=0
  rr[parent]['data']['m_Children'].remove({'rid':col});where=rr[parent]['data']['m_Children'].index({'rid':named('OverviewAgentMediaColumn')});rr[parent]['data']['m_Children'].insert(where+1,{'rid':col})
 values=[]
 for j,(n,title,source,path) in enumerate(fields):
  node=pair(tn,ts,col,n,zero+[prop(131102,en('relative')),prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(20)),prop(131096,px(20)),prop(131084,num(0)),prop(131085,num(0)),prop(131090,px(gap if j<2 else 0)),prop(65546,en('middle-left')),prop(65552,en('nowrap'))]);rr[node]['data']['m_Classes']=copy.deepcopy(tn['data']['m_Classes'])+['content-ellipsis'];data=sd(node)
  data['TextBinding']=copy.deepcopy(source['TextBinding']);data['TextBinding_UxmlAttributeFlags']=source.get('TextBinding_UxmlAttributeFlags',1);data.update(text='--',text_UxmlAttributeFlags=1,DebugDisplay='',tooltip=title,tooltip_UxmlAttributeFlags=1,displayTooltipWhenElided=True,displayTooltipWhenElided_UxmlAttributeFlags=1)
  for k in ['enableRichText','enableRichText_UxmlAttributeFlags']:
   if k in source:data[k]=copy.deepcopy(source[k])
  assert data['TextBinding']==source['TextBinding'];values.append({'name':n,'path':path,'node':node})
 # Horizontal rules separate the report, condition row, and bans; all share the column width.
 linebase=zero+[prop(131087,px(1)),prop(131096,px(1)),prop(131084,num(0)),prop(131085,num(0)),prop(458752,color(135,140,145,160))]
 status=named('OverviewTopRightStatusPanel');inner=blank(status,'OverviewFitnessBansDivider',linebase+[prop(131102,en('absolute')),prop(131089,px(0)),prop(131103,px(0)),prop(131104,px(44))])
 if pid==-930000000001001:
  scoutsep=blank(1349,'OverviewScoutFitnessDivider',linebase+[prop(131102,en('relative')),prop(131105,pct(100)),prop(131093,px(3)),prop(131090,px(0))])
  vertical=blank(1173,'OverviewStatusRadarDivider',zero+[prop(131102,en('absolute')),prop(131089,px(246)),prop(131104,px(4)),prop(131105,px(1)),prop(131087,px(242)),prop(131084,num(0)),prop(131085,num(0)),prop(458752,color(135,140,145,160))])
  assert 240<246<252 and 4+242<=250
 for i,r in old.items():
  if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('existing data/binding changed',pid,i)
 assert len(rr[col]['data']['m_Children'])==3
 assert [len(rr[named('RightHiddenAttributesColumn'+str(i))]['data']['m_Children']) for i in [1,2,3]]==[5,4,4]
 validate_ui(doc,sheet);o[pid].save_typetree(doc);o[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet;audits.append({'page':pid,'new_column':col,'values':values,'row_height':20,'row_pitch':20+gap,'status_dividers':2 if pid==-930000000001001 else 1,'radar_vertical_divider':pid==-930000000001001})
output=e.file.save(packer='lz4');check={x.path_id:x for x in UnityPy.load(output).objects};assert set(check)==set(hashes)
for i,h in hashes.items():
 if i not in changed:assert sha(check[i].get_raw_data())==h,('unrelated asset modified',i)
for i,d in changed.items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
(OUT/W).write_bytes(output);report={'installed':False,'runtime_verified':False,'pages':audits,'native_biography_and_personal_sources_unchanged':True,'existing_overview_bindings_preserved':True,'catalog_and_background_unchanged':True,'after_sha256':sha(output)};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Prepared files ready; game must exit before install'
try:
 for p in before:p.write_bytes(output);assert p.read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/W)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'third_column_fields':3,'horizontal_and_vertical_dividers_added':True,'native_sources_preserved':True},ensure_ascii=True))
