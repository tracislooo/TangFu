"""200px six-axis radar inside the existing working native season context."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
def module(name,file):
 spec=importlib.util.spec_from_file_location(name,R/file);m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m);return m
rb=module('radar','season-radar-builders.py');cm=module('catalog','catalog-binary-v35.py')
loc=json.loads((R/'current-game-location.json').read_text('utf8'));index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'));manifest=json.loads(Path(previous['manifest']).read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
GROUPS=[dict(panel='SeasonStatsOutfielderPanel',fields=['ExpectedGoalsPer90','ShotsOnTargetPer90','ExpectedAssistsPer90','PassCompletedPer90','TacklesCompletedPer90','KeyHeadersPer90'],indices=[3,4,6,8,10,11],limits=[(0,1.2,False),(0,3,False),(0,.6,False),(0,100,False),(0,6,False),(0,6,False)]),dict(panel='SeasonStatsGoalkeeperPanel',fields=['ExpectedGoalsPreventedPer90','TotalSavesPer90','ConcededPer90','PossessionWonPer90','PossessionLostPer90','PassCompletedPer90'],indices=[3,4,5,6,7,8],limits=[(-2,2,False),(0,8,False),(0,3,True),(0,10,False),(0,15,True),(0,60,False)])]
OUT=R/('test-context-six-axis-radar200-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];audits=[]
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
for tag,root in roots:
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in obs.items()}
 page=obs[-941100000001020].read_typetree();ps=obs[-941100000001021].read_typetree();pst=Styles(ps);pr=refs(page)
 pst.edit(pr[1173],[pst.p(131105,pst.px(868)),pst.p(131082,pst.px(868))])
 stats=obs[-941100000001050].read_typetree();sheet=obs[-941100000001051].read_typetree();st=Styles(sheet);sr=refs(stats);original=copy.deepcopy(stats)
 assert sr[1041]['data']['m_FullTypeName']=='SI.UI.ComponentElement'
 assert [(p['from'],p['to']['m_path'])for p in sr[1598]['data']['Mappings']]==[('competition','person.Division'),('seasonStats','person.SeasonStats.SeasonStatsSelectedCompetitionsData')]
 donor={o.path_id:o for o in UnityPy.load(str(R/'season-six-values-one-radar-20261114-021409'/tag/W)).objects};dd=donor[-941100000001050].read_typetree();dr=refs(dd);ds=donor[-941100000001051].read_typetree()
 plain=(copy.deepcopy(sr[1046]),copy.deepcopy(sr[sr[1046]['data']['m_SerializedData']['rid']]))
 switch=(copy.deepcopy(pr[6310]),copy.deepcopy(pr[pr[6310]['data']['m_SerializedData']['rid']]))
 def box(i,width,height,grow=0,direction='column'):
  rr=refs(stats);st.edit(rr[i],[st.p(131102,st.en('relative')),st.p(131105,width),st.p(131097,st.px(0)),st.p(131095,{'m_ValueType':1,'valueIndex':3}),st.p(131087,height),st.p(131096,st.px(0)),st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131084,st.num(grow)),st.p(131085,st.num(1)),st.p(131082,st.px(0)if grow else {'m_ValueType':1,'valueIndex':2}),st.p(131083,st.en(direction)),st.p(131073,st.en('stretch'))],reset=True)
 contents=[c for c in sr[1041]['data']['m_Children']if c['rid']!=1597]
 column=add_node(stats,plain,1041,'WorkingNativeSeasonDataColumn');sr=refs(stats)
 for c in contents:
  sr[1041]['data']['m_Children'].remove(c);sr[column]['data']['m_Children'].append(c);sr[c['rid']]['data']['m_Parent']={'rid':column}
 box(1041,st.pct(100),st.px(249),direction='row');box(column,st.px(0),st.px(249),1)
 case=add_node(stats,switch,1041,'WorkingSeasonRadarGoalkeeperSwitch');sr=refs(stats);data(sr,case)['Binding']=dict(m_kind=1,m_direct=dict(Path=dict(m_path='person.IsGoalkeeper'),Nullable=0),m_visualFunction=rb.function(''));data(sr,case)['Binding_UxmlAttributeFlags']=1
 box(case,st.px(200),st.px(249));st.edit(sr[case],[st.p(131097,st.px(200)),st.p(131095,st.px(200)),st.p(131085,st.num(0)),st.p(131091,st.px(8))])
 def clone_subtree(source,parent):
  rr=refs(stats);owned=owned_refs(dr,source);selected=[r for r in dd['references']['RefIds']if r['rid']in owned];start=max(rr)+1;mapping={r['rid']:start+j for j,r in enumerate(selected)}
  uid=max(r.get('data',{}).get('m_Id',0)for r in rr.values())+1;idmap={r['data']['m_Id']:uid+j for j,r in enumerate(selected)if 'm_Id'in r.get('data',{})};assert max(idmap.values())<2147483647
  def remap(v):
   if isinstance(v,dict):
    if set(v)=={'rid'}:
     if v['rid']in mapping:v['rid']=mapping[v['rid']]
    else:
     for k,x in list(v.items()):
      if k in ['m_Id','uxmlAssetId','m_ParentId']and x in idmap:v[k]=idmap[x]
      else:remap(x)
   elif isinstance(v,list):
    for x in v:remap(x)
  for old in selected:
   r=copy.deepcopy(old);r['rid']=mapping[old['rid']];remap(r['data']);v=r.get('data',{});ix=v.get('m_RuleIndex',-1)
   if ix>=0:
    rule=copy.deepcopy(ds['m_Rules'][ix]);assert not rule['m_ComplexSelectors']
    for p in rule['m_Properties']:
     for h in p['m_Values']:
      if h['m_ValueType']in poolmap:
       pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ds[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
    v['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(rule)
   stats['references']['RefIds'].append(r)
  rr=refs(stats);rootrid=mapping[source];rr[rootrid]['data']['m_Parent']={'rid':parent};rr[parent]['data']['m_Children'].append({'rid':rootrid});return rootrid,mapping
 for group in GROUPS:
  dp=named(dd,group['panel']);source=next(c['rid']for c in dr[dp]['data']['m_Children']if data(dr,c['rid']).get('name')=='SeasonRadarNumericValues')
  branch,bmap=clone_subtree(source,case);sr=refs(stats);sd=data(sr,branch);assert len(sd['BindFunction'])==6
  # Negative xG-prevented stays negative on labels and increases monotonically.
  for j,(idx,limits,field)in enumerate(zip(group['indices'],group['limits'],group['fields'])):
   lo,hi,reverse=limits;prefix='seasonRadar'+str(idx)
   for v in sd['ValueVariables']:
    if v['m_name']==prefix+'Min':v['m_scopeValue']['m_serializedData']='Float|'+str(lo)+'|'
    if v['m_name']==prefix+'RangeMax':v['m_scopeValue']['m_serializedData']='Float|'+str(hi)+'|'
   sd['BindFunction'][j]=rb.function(manifest['function_guid'],rb.path_arg('SeasonStats.'+field),rb.path_arg(prefix+'RangeMax'),rb.float_arg(lo),rb.bool_arg(reverse),rb.path_arg(prefix+'Raw'),rb.path_arg(prefix+'Plot'),rb.path_arg(prefix+'Max'),rb.path_arg(prefix+'Valid'))
  for i in bmap.values():
   v=sr[i].get('data',{})
   if v.get('m_FullTypeName')=='FM.UI.FMSpiderChart':
    v['m_Classes']=['fmspiderchartmedium'];cd=data(sr,i);assert cd['SpiderChartVertices']==6;cd['SpiderChartRadiusPercentage']=24.;cd['LabelDistanceFromChart']=10.
  box(branch,st.pct(100),st.pct(100),1)
 # Preserve exactly the original component and the entire native statistic data.
 before_refs=refs(original);sr=refs(stats)
 for i,r in before_refs.items():
  if i==1041:continue
  expected=copy.deepcopy(r)
  if any(c['rid']==i for c in contents):expected['data']['m_Parent']={'rid':column}
  assert sr[i]==expected,('Native data/context changed',tag,i)
 label=obs[-941100000001052].read_typetree();ls=obs[-941100000001053].read_typetree();lst=Styles(ls)
 for r in refs(label).values():
  if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':lst.edit(r,[lst.p(65537,lst.px(8))])
 # Existing GUIDs, actual Global function and directory registrations must exist.
 go={o.path_id:o for o in UnityPy.load(str(root/G)).objects};assert go[-941100000001054].read_typetree()['m_Name']=='LeftTestSeasonRadarValues'
 cat=cm.Catalog(((root.parent if tag=='game'else root)/'catalog.bin').read_bytes())
 for key in [manifest['function_guid'],manifest['label_guid']]:assert cat.locations(key)
 graph(stats);validate_ui(stats,sheet);graph(page)
 changes={-941100000001020:page,-941100000001021:ps,-941100000001050:stats,-941100000001051:sheet,-941100000001053:ls}
 for i,d in changes.items():obs[i].save_typetree(d)
 output=env.file.save(packer='lz4');read={o.path_id:o for o in UnityPy.load(output).objects};assert read.keys()==obs.keys()
 for i,h in hashes.items():
  if i not in changes:assert sha(read[i].get_raw_data())==h
 for i,d in changes.items():assert read[i].read_typetree()==d
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before);tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 audits.append(dict(target=tag,radar_width=200,root=1041,column=column,case=case,groups=GROUPS,native_context_and_values_unchanged=True));print('Verified '+tag,flush=True)
manifest.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='200px six-axis radar sharing working native season context',protected_sha256=protected,radar_audits=audits)
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'context-radar-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
