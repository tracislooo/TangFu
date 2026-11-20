from pathlib import Path
import sys,copy,ast,json,hashlib,datetime,struct,uuid,zlib,importlib.util,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';B='ui-backgrounds_assets_common.bundle';L='ui-tileslayouts_assets_all.bundle'
OUT=R/('personal-info-radar-fullwidth-hidden-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
paths=[GAME/W,SKIN/W,GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin'];before={p:p.read_bytes() for p in paths};assert before[GAME/W]==before[SKIN/W]
for p,b in before.items():
 tag='backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin';folder=OUT/tag;folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(b)
protected={p:sha(p.read_bytes()) for n in [G,B,L] for p in [GAME/n,SKIN/n]};e=UnityPy.load(before[GAME/W]);o={x.path_id:x for x in e.objects};af=e.assets[0];hashes={i:sha(x.get_raw_data()) for i,x in o.items()};oldwrite=TypeTreeHelper.write_value
source=ast.parse((R/'redesign-card-top-info-foot.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name in {'write','val','px','pct','en','num','color','prop','rule','override'}],type_ignores=[]),'helpers','exec'));TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'};source=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in source.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
personalpid=-1336215414551004732;personal=o[personalpid].read_typetree();sr={r['rid']:r for r in personal['references']['RefIds']};ss=o[personal['inlineSheet']['m_PathID']].read_typetree();changed={};audit=[]
def sn(i):return sr.get(sr[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','')
def sd(i):return rr.get(rr[i]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})
def named(n):
 hits=[r['rid'] for r in rr.values() if 'm_Parent' in r.get('data',{}) and sd(r['rid']).get('name')==n];assert len(hits)==1,(n,hits);return hits[0]
def st(i,ps):override(rr[i]['data'],ps)
def subtree(rs,i):
 result=[i]
 for c in rs[i]['data'].get('m_Children',[]):result+=subtree(rs,c['rid'])
 return result

def pair(nt,ts,parent,name,ps):
 global next_rid,next_id
 a=copy.deepcopy(nt);s=copy.deepcopy(ts);a['rid']=next_rid;s['rid']=next_rid+1;next_rid+=2
 a['data'].update(m_Id=next_id,m_Parent={'rid':parent},m_Children=[],m_SerializedData={'rid':s['rid']},m_RuleIndex=rule(ps),m_Classes=[],m_Properties=[],m_Stylesheets=[],m_StylesheetPaths=[])
 s['data'].update(uxmlAssetId=next_id,name=name,name_UxmlAttributeFlags=1);next_id+=1
 rr[a['rid']]=a;rr[s['rid']]=s;doc['references']['RefIds'] += [a,s];rr[parent]['data']['m_Children'].append({'rid':a['rid']});return a['rid']
def blank(parent,name,ps):return pair(blanknode,blanksd,parent,name,ps)
def move(i,parent):
 old=rr[i]['data']['m_Parent']['rid'];rr[old]['data']['m_Children'].remove({'rid':i});rr[parent]['data']['m_Children'].append({'rid':i});rr[i]['data']['m_Parent']={'rid':parent}

def clone_person(root,parent):
 global next_rid,next_id
 nodes=subtree(sr,root);ids=nodes+[sr[i]['data']['m_SerializedData']['rid'] for i in nodes if sr[i]['data'].get('m_SerializedData',{}).get('rid',-2)>=0]
 mapping={i:next_rid+j for j,i in enumerate(ids)};next_rid+=len(ids);uids={sr[i]['data']['m_Id']:next_id+j for j,i in enumerate(nodes)};next_id+=len(nodes)
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid'] in mapping:v['rid']=mapping[v['rid']]
   else:
    for k,x in v.items():
     if k in ['m_Id','m_ParentId','uxmlAssetId'] and isinstance(x,int) and x in uids:v[k]=uids[x]
     else:remap(x)
  elif isinstance(v,list):
   for x in v:remap(x)
 for i in ids:
  r=copy.deepcopy(sr[i]);r['rid']=mapping[i];remap(r['data'])
  if i in nodes:
   if i==root:r['data']['m_Parent']={'rid':parent}
   ix=r['data'].get('m_RuleIndex',-1)
   if ix>=0:
    nr=copy.deepcopy(ss['m_Rules'][ix])
    for p in nr['m_Properties']:
     for h in p['m_Values']:
      if h['m_ValueType']==1:continue
      pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
    r['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(nr)
  rr[r['rid']]=r;doc['references']['RefIds'].append(r)
 rr[parent]['data']['m_Children'].append({'rid':mapping[root]});return mapping
# A local bans component removes the title without changing the native lower cards.
banspid=-3667015745575234167;bans=o[banspid].read_typetree();br={r['rid']:r for r in bans['references']['RefIds']};newbans=copy.deepcopy(bans);newbr={r['rid']:r for r in newbans['references']['RefIds']};remove=subtree(br,1002);remove+= [br[i]['data']['m_SerializedData']['rid'] for i in remove];newbr[1001]['data']['m_Children'].remove({'rid':1002});newbans['references']['RefIds']=[r for r in newbans['references']['RefIds'] if r['rid'] not in remove]
newpid=-940000000004000;assert newpid not in o;key=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-overview-bans-content-without-title').hex;newbans['m_Name']='OverviewBansWithoutTitle';newbans['m_ContentHash']=struct.unpack('<i',struct.pack('<I',zlib.crc32(key.encode())))[0];validate_ui(newbans,o[newbans['inlineSheet']['m_PathID']].read_typetree());obj=copy.copy(o[banspid]);obj.path_id=newpid;af.objects[newpid]=obj;obj.save_typetree(newbans);changed[newpid]=newbans
for pid in [-930000000001001,-930000000001003]:
 doc=o[pid].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};old=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=o[sid].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
 blanknode=copy.deepcopy(rr[1011]);blanksd=copy.deepcopy(rr[blanknode['data']['m_SerializedData']['rid']]);auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3};zero=[prop(262150,px(0)),prop(262151,px(0))];flow=zero+[prop(131102,en('relative')),prop(131083,en('column')),prop(131073,en('stretch')),prop(131084,num(0)),prop(131085,num(0)),prop(131097,px(0))]
 for u in doc['m_Usings']:
  if u['alias']=='PlayerReportBansBlock':u['path']=key;u['asset']={'m_FileID':0,'m_PathID':0}
 # A three-row column immediately to the right of the existing personal details.
 if pid==-930000000001001:
  info=blank(1184,'OverviewAgentMediaColumn',flow+[prop(131105,px(200)),prop(131082,px(200)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,px(60)),prop(131096,px(60)),prop(131092,px(8))]);rr[1184]['data']['m_Children'].remove({'rid':info});index=rr[1184]['data']['m_Children'].index({'rid':1031});rr[1184]['data']['m_Children'].insert(index+1,{'rid':info})
  st(1031,[prop(131105,px(126)),prop(131097,px(126)),prop(131092,px(8))])
  # Fill all remaining horizontal room to the right of the fitness/bans column.
  move(1026,1173);st(1173,[prop(131102,en('relative'))]);st(1026,[prop(131102,en('absolute')),prop(131089,px(252)),prop(131103,px(0)),prop(131104,px(0)),prop(131075,px(0)),prop(131105,auto),prop(131097,px(0)),prop(131095,none),prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(131073,en('stretch')),prop(131088,en('center'))])
  st(1043,[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,none),prop(131087,pct(100)),prop(131096,px(0)),prop(131094,none),prop(131091,px(0)),prop(131092,px(0)),prop(131084,num(1)),prop(131085,num(1))]);sd(1043).update(SpiderChartRadiusPercentage=38.0,SpiderChartRadiusPercentage_UxmlAttributeFlags=1,LabelDistanceFromChart=24.0,LabelDistanceFromChart_UxmlAttributeFlags=1)
 else:
  header=named('SimplePortraitHeader');info=blank(header,'OverviewAgentMediaColumn',flow+[prop(131105,px(240)),prop(131095,px(240)),prop(131085,num(1)),prop(131087,px(60)),prop(131096,px(60)),prop(131091,px(12))]);rr[header]['data']['m_Children'].remove({'rid':info});rr[header]['data']['m_Children'].insert(1,{'rid':info})
 maps=[clone_person(root,info) for root in [1060,1061]]
 for mapping in maps:
  for oldid,newid in mapping.items():
   if 'm_Parent' not in sr[oldid].get('data',{}):continue
   nm=sn(oldid)
   if nm=='AgentVisible':st(newid,flow+[prop(131087,px(20))])
   elif nm=='PlayerMediaVisible':st(newid,flow+[prop(131087,px(40))])
   elif nm in ['AgentFrame','MediaDescriptionFrame','InternationalMediaOpinionFrame']:st(newid,zero+[prop(131083,en('row')),prop(131073,en('center')),prop(131105,pct(100)),prop(131087,px(20)),prop(131096,px(20)),prop(131084,num(0)),prop(131085,num(0))])
   else:
    a=rr[newid]['data'];data=sd(newid)
    if 'TextBinding' in data or nm=='AgentNullSwitch':
     title=nm in ['AgentFrameText','MediaDescriptionFrameText','InternationalMediaOpinionFrameText']
     st(newid,zero+[prop(131097,px(0)),prop(131087,px(20)),prop(131090,px(0)),prop(131093,px(0)),prop(131085,num(1)),prop(65537,px(11)),prop(65552,en('nowrap'))]+([prop(131105,px(64)),prop(131084,num(0)),prop(131092,px(4))] if title else [prop(131105,auto),prop(131084,num(1))]))
     if 'displayTooltipWhenElided' in data:data['displayTooltipWhenElided']=True;data['displayTooltipWhenElided_UxmlAttributeFlags']=1
 # Expand the top summary across the full width using proportional CA/PA/reputation groups.
 summary=named('RightHiddenSummaryGraphic');line=named('RightHidden_OverviewHiddenSummaryLine');barline=named('RightHidden_OverviewHiddenBarLine');st(summary,[prop(131105,pct(100)),prop(131087,px(64)),prop(131096,px(64))]);st(line,[prop(131102,en('relative')),prop(131089,auto),prop(131104,auto),prop(131105,pct(100)),prop(131087,px(30)),prop(131083,en('row')),prop(131073,en('center'))])
 for prefix in ['CA','PA']:
  group=blank(line,'RightHidden'+prefix+'FullWidthGroup',zero+[prop(131102,en('relative')),prop(131105,auto),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131097,px(0)),prop(131087,px(30))])
  dot=named('RightHidden_Overview'+prefix+'WhiteDot');number=named('RightHidden_Overview'+prefix+'NativeNumberAvailable');move(dot,group);move(number,group)
  st(dot,[prop(131089,px(0)),prop(131104,px(8)),prop(131105,px(14)),prop(131087,px(14)),prop(262147,px(7))]);arrow=named('RightHidden_Overview'+prefix+'DirectionArrow');st(arrow,[prop(131105,px(14)),prop(131087,px(14)),prop(65537,px(12))]);st(number,[prop(131089,px(18)),prop(131103,px(0)),prop(131105,auto),prop(131087,px(30))])
  for suffix in ['Missing','Value']:st(named('RightHidden_Overview'+prefix+'NativeNumber'+suffix),[prop(131105,pct(100)),prop(131087,px(30)),prop(65537,px(22))])
 rep=named('RightHidden_OverviewCurrentReputationCompactGroup');move(rep,line);st(rep,zero+[prop(131102,en('relative')),prop(131089,auto),prop(131104,auto),prop(131105,auto),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131097,px(0)),prop(131087,px(30)),prop(131083,en('row')),prop(131073,en('center')),prop(131088,en('flex-end'))])
 for n,size in [('RightHidden_OverviewCurrentReputationTitle',10),('RightHidden_OverviewCurrentReputationMissing',12),('RightHidden_OverviewCurrentReputationValue',12)]:st(named(n),[prop(65537,px(size))])
 st(named('RightHidden_OverviewCurrentReputationAvailable'),[prop(131105,px(40))]);st(barline,[prop(131105,pct(100)),prop(131104,px(32)),prop(131087,px(26))]);st(named('RightHidden_OverviewHiddenNativeTitle'),[prop(65537,px(10)),prop(131105,px(32))])
 bar=named('RightHidden_OverviewCAPALayeredBar')
 for i in subtree(rr,bar):
  ix=rr[i]['data'].get('m_RuleIndex',-1)
  if ix<0:continue
  ps=[]
  for p in sheet['m_Rules'][ix]['m_Properties']:
   if p['m_Id'] in [131105,131097,131095]:
    h=p['m_Values'][0]
    if h['m_ValueType']==3 and sheet['dimensions'][h['valueIndex']]['value'] in [166,178]:ps.append(prop(p['m_Id'],pct(100)))
  if ps:st(i,ps)
 st(bar,[prop(131089,px(36)),prop(131103,px(0)),prop(131105,auto),prop(131097,px(0))])
 labels=[r['rid'] for r in rr.values() if 'm_Parent' in r.get('data',{}) and sd(r['rid']).get('name','').startswith('RightHiddenLabel_')];assert len(labels)==13
 for i in labels:st(i,[prop(65537,px(11))])
 panel=named('RightHiddenAttributesPanel');listing=named('RightHiddenAttributesList');lineprops=zero+[prop(131102,en('relative')),prop(131105,pct(100)),prop(131087,px(1)),prop(131096,px(1)),prop(131084,num(0)),prop(131085,num(0)),prop(458752,color(135,140,145,160)),prop(131093,px(6)),prop(131090,px(6))]
 sep1=blank(panel,'RightHiddenSummarySeparator',lineprops);sep2=blank(panel,'RightHiddenAttributesSeparator',lineprops);rr[panel]['data']['m_Children']=[{'rid':summary},{'rid':sep1},{'rid':listing},{'rid':sep2}]
 # Explicit group order: CA, PA, then reputation; hidden legacy captions remain non-rendering.
 groups=[named('RightHiddenCAFullWidthGroup'),named('RightHiddenPAFullWidthGroup'),rep];oldcaps=[c for c in rr[line]['data']['m_Children'] if c['rid'] not in groups];rr[line]['data']['m_Children']=oldcaps+[{'rid':i} for i in groups]
 validate_ui(doc,sheet);o[pid].save_typetree(doc);o[sid].save_typetree(sheet);changed[pid]=doc;changed[sid]=sheet
 audit.append({'page':pid,'personal_info_column':'right of existing details, three rows','summary_width':'100%','hidden_label_font':11,'horizontal_separators':2,'radar_uses_remaining_width':pid==-930000000001001})
# Complete the requested move by removing the original two visibility blocks (three rows).
for root in [1060,1061]:
 parent=sr[root]['data']['m_Parent']['rid'];sr[parent]['data']['m_Children'].remove({'rid':root})
removed=subtree(sr,1060)+subtree(sr,1061);removed+= [sr[i]['data']['m_SerializedData']['rid'] for i in removed if sr[i]['data'].get('m_SerializedData',{}).get('rid',-2)>=0];personal['references']['RefIds']=[r for r in personal['references']['RefIds'] if r['rid'] not in removed];validate_ui(personal,ss);o[personalpid].save_typetree(personal);changed[personalpid]=personal
# Add the local titleless bans variant to the correct catalog and preload label.
metaobj=next(x for x in o.values() if x.type.name=='AssetBundle');meta=metaobj.read_typetree();ix=len(meta['m_PreloadTable']);meta['m_PreloadTable'] += [copy.deepcopy(newbans['m_Script']),copy.deepcopy(newbans['inlineSheet']),{'m_FileID':0,'m_PathID':newpid}];meta['m_Container'].append((key,{'preloadIndex':ix,'preloadSize':3,'asset':{'m_FileID':0,'m_PathID':newpid}}));meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta);changed[metaobj.path_id]=meta
sp=importlib.util.spec_from_file_location('c',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm);cat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=next(x for x in cat.locations('72b2a804423579143940e7fc9b38914d') if cat.location(x)['type'][1].endswith('VisualTreeAsset'));cat=cm.Catalog(cat.add_key_location(key,loc,loc));newloc=cat.locations(key)[0];assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(W)
idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)=='GameWorldVisualTreeAssetPreload');ko,ls=cat.key_records[idx];locs=[x[0] for x in cat.array(ls,'I')]+[newloc];newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[idx]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);catout=bytes(cat.data)
output=e.file.save(packer='lz4');check={x.path_id:x for x in UnityPy.load(output).objects};assert set(check)==set(hashes)|{newpid}
for i,h in hashes.items():
 if i not in changed:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',i)
for i,d in changed.items():assert check[i].read_typetree()==d,('roundtrip mismatch',i,d.get('m_Name'))
for i in [-930000000001001,-930000000001003,personalpid,newpid]:
 d=check[i].read_typetree();validate_ui(d,check[d['inlineSheet']['m_PathID']].read_typetree())
(OUT/W).write_bytes(output);(OUT/'catalog.bin').write_bytes(catout);(OUT/'catalog.hash').write_bytes(hashlib.md5(catout).hexdigest().encode());report={'installed':False,'runtime_verified':False,'pages':audit,'agent_media_source_rows_removed':True,'bans_title_removed_locally':True,'background_bundle_unchanged':True,'after_sha256':sha(output)};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not proc.stdout.strip(),'Game must exit before install'
try:
 for p,b in [(GAME/W,output),(SKIN/W,output),(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',(OUT/'catalog.hash').read_bytes())]:p.write_bytes(b);assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():p.write_bytes(b)
 raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');restore=['$ErrorActionPreference = "Stop"']
for p in before:
 tag='backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'pages':2,'identity_added_rows':3,'hidden_separators':2,'bans_title_removed':True},ensure_ascii=True))
