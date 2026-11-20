"""Private seventh-page layout; native rows, comparison/contract fallback, no shared edits."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,zlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('add-left-test-overview.py',{'prune'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('radar_codec',R/'season-radar-builders.py');rb=importlib.util.module_from_spec(spec);spec.loader.exec_module(rb)
loc=json.loads((R/'current-game-location.json').read_text('utf8'));idxpath=R/'current-player-overview-test-variant.json';previous=json.loads(idxpath.read_text('utf8'));priorout=Path(previous['manifest']).parent;m=json.loads((priorout/'manifest.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';PAGE=-941100000001020;STYLE=PAGE-1
OUT=R/('test-overview-aligned-header-contract-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];audits=[]
targets=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for tag,root in targets for p in root.glob('*.bundle')if p.name!=W}
for tag,root in targets:
 for p in [(root.parent if tag=='game'else root)/'catalog.bin',(root.parent if tag=='game'else root)/'catalog.hash']:protected[str(p)]=sha(p.read_bytes())
for tag,root in targets:
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()};go={o.path_id:o for o in UnityPy.load(str(root/G)).objects}
 doc=obs[PAGE].read_typetree();original=copy.deepcopy(doc);sheet=obs[doc['inlineSheet']['m_PathID']].read_typetree();rr=refs(doc);st=Styles(sheet)
 auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
 def edit(i,ps,reset=False):
  unique={k:v for k,v in ps};st.edit(refs(doc)[i],[st.p(k,v)for k,v in unique.items()],reset)
 def box(i,w,h,grow=0,direction='column',reset=False):
  edit(i,[(131102,st.en('relative')),(131089,auto),(131103,auto),(131104,auto),(131080,auto),(131105,w),(131097,st.px(0)),(131095,none),(131087,h),(131096,st.px(0)),(131094,none),(131084,st.num(grow)),(131085,st.num(1)),(131082,st.px(0)if grow else auto),(131083,st.en(direction)),(131073,st.en('stretch')),(131074,st.en('stretch'))],reset)
 def absolute(i,x,y,w,h):
  box(i,w,st.px(h));edit(i,[(131102,st.en('absolute')),(131089,st.px(x)),(131104,st.px(y)),(131085,st.num(0))])
 def move(i,parent):
  r=refs(doc);r[r[i]['data']['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});r[i]['data']['m_Parent']={'rid':parent};r[parent]['data']['m_Children'].append({'rid':i})
 def proto(i):
  r=refs(doc);return copy.deepcopy(r[i]),copy.deepcopy(r[r[i]['data']['m_SerializedData']['rid']])
 plain=proto(1291);switchproto=proto(6310)
 def plainnode(parent,name):return add_node(doc,plain,parent,name)
 def gate(parent,name,binding):
  i=add_node(doc,switchproto,parent,name);r=refs(doc);sd=data(r,i);sd['Binding']=binding;sd['Binding_UxmlAttributeFlags']=1;sd['InvertDirectBinding']=0;sd['BindDirectAsMask']=0;box(i,st.pct(100),st.pct(100),1,reset=True);return i
 def direct(path):return dict(m_kind=1,m_direct=dict(Path=dict(m_path=path),Nullable=1),m_visualFunction=rb.function(''))
 # Remove the independent large club/flag column, keeping the identity footer intact.
 prune(doc,1163);rr=refs(doc)
 box(1291,st.px(0),st.px(250),1);edit(1291,[(131091,st.px(0)),(131092,st.px(8)),(131099,st.px(0)),(131100,st.px(0))])
 box(1297,st.pct(100),st.px(250));edit(1297,[(131091,st.px(0)),(131092,st.px(0)),(131099,st.px(0)),(131100,st.px(0))])
 # Shared vertical bands: heading 0..72; financial 72..99; personal 99..171;
 # national/club and scout/footer 172..240. All four statistics use these anchors.
 box(1171,st.pct(100),st.px(72));absolute(1199,0,72,st.pct(100),26)
 absolute(6274,0,98,st.pct(100),1);absolute(1184,0,99,st.pct(100),72)
 edit(6268,[(131104,st.px(23))]);edit(6270,[(131104,st.px(47))]);absolute(6272,0,171,st.pct(100),1);absolute(1295,0,172,st.pct(100),60)
 # Status markers and the complete quick-flick scope move together with events.
 absolute(6724,0,4,st.px(180),20);edit(6724,[(131089,auto),(131103,st.px(4)),(131088,st.en('flex-end'))])
 move(1707,6738);absolute(1707,0,28,st.px(28),54);edit(1707,[(131089,auto),(131103,st.px(4))])
 # Broader statistics column and a narrower native ability chart.
 box(1173,st.px(540),st.px(250));edit(1173,[(131082,st.px(540)),(131099,st.px(0)),(131100,st.px(0))])
 absolute(2242,0,0,st.px(320),250);edit(2242,[(131095,st.px(320))])
 absolute(2986,0,6,st.pct(100),42);absolute(6304,0,72,st.pct(100),99)
 edit(6304,[(131080,auto)]);absolute(1349,0,172,st.px(320),68)
 absolute(1026,332,0,st.px(200),242);box(1043,st.pct(100),st.px(242))
 data(refs(doc),1043).update(SpiderChartRadiusPercentage=30.,SpiderChartRadiusPercentage_UxmlAttributeFlags=1)
 # This page reuses its registered private stats slot, now containing native rows.
 stats=obs[-950000000000168].read_typetree();ss=obs[stats['inlineSheet']['m_PathID']].read_typetree();sst=Styles(ss);sr=refs(stats)
 for panel in ['SeasonStatsOutfielderPanel','SeasonStatsGoalkeeperPanel']:
  rowids=sr[named(stats,panel)]['data']['m_Children'];assert len(rowids)==4
  for c,height in zip(rowids,[27,24,24,24]):
   sst.edit(sr[c['rid']],[sst.p(131087,sst.px(height)),sst.p(131096,sst.px(height)),sst.p(131094,sst.px(height)),sst.p(131084,sst.num(0)),sst.p(131085,sst.num(0))])
 stats.update(m_Name='LeftTestAlignedNativeSeasonFourRows',inlineSheet=dict(m_FileID=0,m_PathID=-941100000001051));ss['m_Name']=stats['m_Name']+'Style'
 for u in doc['m_Usings']:
  if u['alias']=='OverviewNativeSeasonFourGauges':u.update(path=m['stats_guid'],asset=dict(m_FileID=0,m_PathID=-941100000001050))
 data(refs(doc),6304).update(template=dict(m_FileID=0,m_PathID=-941100000001050),template_UxmlAttributeFlags=1)
 # Native themed row background; remove every custom inline colour from the rows.
 rr=refs(doc);hidden=[]
 for i,r in rr.items():
  sd=rr.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if sd.get('name','').startswith('RightHiddenRow_'):
   hidden.append(i);r['data']['m_Classes']=list(dict.fromkeys(r['data']['m_Classes']+['attributes-row-number-key-no-border']))
   ri=r['data']['m_RuleIndex'];ps=[copy.deepcopy(p)for p in sheet['m_Rules'][ri]['m_Properties']if p['m_Id']!=458752]
   st.edit(r,ps,reset=True)
 assert len(hidden)==13
 # Bounded native lists, visible vertical scrollbars, wheel support from the list.
 for name in ['pros-list','const-list']:
  i=named(doc,name);sd=data(rr,i)
  sd.update(ClampSizeToPage=0,ClampSizeToPage_UxmlAttributeFlags=1,VerticalScrollerVisibility=1,VerticalScrollerVisibility_UxmlAttributeFlags=1)
  box(i,st.pct(100),st.px(0),1);edit(i,[(458768,st.en('hidden'))])
 # Native horizontal separator at the boundary of the stacked fallback modules.
 rr=refs(doc);sep=6318;native_sep=rr[6268]['data']['m_RuleIndex']
 rr[sep]['data']['m_RuleIndex']=native_sep;box(sep,st.pct(100),st.px(1));edit(sep,[(131096,st.px(1)),(131094,st.px(1)),(131085,st.num(0)),(131093,st.px(5)),(131090,st.px(5))])

 # Import a native template into the private page. All managed references,
 # component IDs, aliases, inline pools and cross-bundle PPtrs are remapped.
 af=obs[PAGE].assets_file
 stale_overrides=[]
 def import_template(source_obj,parent,prefix,overrides=None):
  nonlocal_marker=None
  source=copy.deepcopy(source_obj.read_typetree());source_rr=refs(source);sf=source_obj.assets_file
  source_objects={o.path_id:o for o in sf.objects.values()};source_sheet=source_objects[source['inlineSheet']['m_PathID']].read_typetree()
  if overrides:
   for ov in overrides:
    candidates=[i for i,r in source_rr.items()if r.get('data',{}).get('m_Id')==ov['m_ElementId']]
    if not candidates:
     # These old instance IDs also fail to resolve against the currently shared
     # native template. Preserve that template's effective bindings and events.
     stale_overrides.append(ov['m_ElementIdsPath']);continue
    assert len(candidates)==1,('Ambiguous selector override',ov['m_ElementIdsPath'])
    target=candidates[0];sdid=source_rr[target]['data']['m_SerializedData']['rid'];replace=copy.deepcopy(ov['_data']);replace['uxmlAssetId']=source_rr[target]['data']['m_Id'];source_rr[sdid]['data']=replace
  rootrid=source['m_VisualTree']['rid'];roots=source_rr[rootrid]['data']['m_Children'];assert len(roots)==1
  # Native references may include rid=-2 sentinel records, which are never cloned.
  imported=[r for r in source['references']['RefIds']if r['rid']!=rootrid and r.get('data')is not None]
  current=refs(doc);start=max(current)+1;ridmap={r['rid']:start+j for j,r in enumerate(imported)}
  uid=max(r.get('data',{}).get('m_Id',0)for r in current.values())+1
  idmap={r['data']['m_Id']:uid+j for j,r in enumerate(imported)if 'm_Id'in r['data']};assert max(idmap.values())<2147483647
  aliases={u['alias']:prefix+u['alias']for u in source['m_Usings']}
  def ptr(p):
   if p['m_PathID']==0:return
   fid=p['m_FileID']
   if sf is af:return
   if fid==0:extpath='archive:/'+sf.name+'/'+sf.name
   else:extpath=sf.externals[fid-1].path
   p['m_FileID']=next(j+1 for j,e in enumerate(af.externals)if e.path==extpath)
  for u in source['m_Usings']:
   u=copy.deepcopy(u);u['alias']=aliases[u['alias']];ptr(u['asset']);doc['m_Usings'].append(u)
  offsets={k:len(sheet[k])for k in set(poolmap.values())}
  for k in offsets:
   values=copy.deepcopy(source_sheet[k])
   if k=='assets':
    for p in values:ptr(p)
   sheet[k].extend(values)
  base=len(sheet['m_Rules'])
  for rule in copy.deepcopy(source_sheet['m_Rules']):
   for selector in rule['m_ComplexSelectors']:selector['ruleIndex']+=base
   for p in rule['m_Properties']:
    for h in p['m_Values']:
     if h['m_ValueType']in poolmap:h['valueIndex']+=offsets[poolmap[h['m_ValueType']]]
   sheet['m_Rules'].append(rule)
  def remap(v):
   if isinstance(v,dict):
    if set(v)=={'rid'}:
     if v['rid']in ridmap:v['rid']=ridmap[v['rid']]
    elif set(v)=={'m_FileID','m_PathID'}:ptr(v)
    else:
     for k,x in list(v.items()):
      if k in ['m_Id','m_ParentId','uxmlAssetId','m_ElementId']and x in idmap:v[k]=idmap[x]
      elif k=='m_ElementIdsPath':v[k]=[idmap.get(n,n)for n in x]
      elif k in ['m_TemplateAlias','templateId']and x in aliases:v[k]=aliases[x]
      else:remap(x)
   elif isinstance(v,list):
    for x in v:remap(x)
  known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)for t in af.ref_types}
  for t in sf.ref_types:
   key=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
   if key not in known:af.ref_types.append(copy.copy(t));known.add(key)
  for r in imported:
   oldrid=r['rid'];remap(r['data']);r['rid']=ridmap[oldrid]
   if r['data'].get('m_RuleIndex',-1)>=0:r['data']['m_RuleIndex']+=base
   doc['references']['RefIds'].append(r)
  r=refs(doc);top=ridmap[roots[0]['rid']];r[top]['data']['m_Parent']={'rid':parent};r[parent]['data']['m_Children'].append({'rid':top})
  return top,ridmap

 # Expand the selector privately, retaining exact existing serialized overrides.
 rr=refs(doc);instance=1007;oldinstance=copy.deepcopy(rr[instance]['data']);overrides=[]
 for ov in oldinstance['m_SerializedDataOverride']:
  ov=copy.deepcopy(ov);ov['_data']=copy.deepcopy(rr[ov['m_SerializedData']['rid']]['data']);overrides.append(ov)
 instance_parent=oldinstance['m_Parent']['rid'];host=plainnode(instance_parent,'TestPrivatePitchRolesHost')
 refs(doc)[host]['data']['m_RuleIndex']=oldinstance['m_RuleIndex']
 imported,im=import_template(go[-940000000005000],host,'TestSelector_',overrides)
 for child in list(oldinstance['m_Children']):move(child['rid'],im[2008])
 prune(doc,instance)
 box(host,st.pct(100),st.pct(100),1);box(imported,st.pct(100),st.pct(100),1)
 comparison=im[2006];r=refs(doc);comparison_parent=r[comparison]['data']['m_Parent']['rid']
 outer=gate(comparison_parent,'TestComparisonAllowed',direct('person.PositionalAbilitiesRolesVisible'))
 # First child false; second child true. Contract bindings inherit native player.
 c1,cm1=import_template(obs[-3986609065296841553],outer,'TestContractUnavailable_')
 inner=gate(outer,'TestComparisonHasRows',dict(m_kind=2,m_direct=dict(Path=dict(m_path=''),Nullable=0),m_visualFunction=rb.function('a4dffe7b331c90949b43d2d4e3155117',rb.path_arg('report.ScoutedSquadComparisonPlayers'))))
 c2,cm2=import_template(obs[-3986609065296841553],inner,'TestContractEmpty_')
 move(comparison,inner)
 for i in [outer,inner,c1,c2]:box(i,st.pct(100),st.px(0),1)
 # Fit the contract tile to the former comparison area, with native scrolling
 # and native no-contract branch retained.
 for mapping in [cm1,cm2]:
  for src in [1001,1002,1006]:box(mapping[src],st.pct(100),st.pct(100),1)
 graph(doc);validate_ui(doc,sheet);graph(stats);validate_ui(stats,ss)
 changes={PAGE:doc,-941100000001021:sheet,-941100000001050:stats,-941100000001051:ss}
 for pid,d in changes.items():obs[pid].save_typetree(d)
 output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(obs)
 for pid,h in baseline.items():
  if pid not in changes:assert sha(check[pid].get_raw_data())==h,('Unrelated object changed',tag,pid)
 for pid,d in changes.items():assert check[pid].read_typetree()==d,('Roundtrip',tag,pid)
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 audits.append(dict(target=tag,selector_map=im,contract_maps=[cm1,cm2],gates=[outer,inner],host=host,hidden_rows=hidden,changes=list(changes),original_comparison_binding='report.ScoutedSquadComparisonPlayers',row_heights=[27,24,24,24],preexisting_unresolved_override_paths=stale_overrides))
 print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Aligned identity/statistics rows, native backgrounds and scrollbars, scoped comparison contract fallback',protected_sha256=protected,audits=audits)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'aligned-header-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
