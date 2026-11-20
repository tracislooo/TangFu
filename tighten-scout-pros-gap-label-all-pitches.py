"""Content-sized scout headers; six position captions across all eight layouts."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links'}),('split-season-radar-two-charts.py',{'add_node','graph'}),('add-card-six-ratings.py',{'validate_ui'}),('verify-two-portrait-hidden-overviews.py',{'canonical'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
OUT=R/('scout-pros-gap-all-position-captions-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
previous=json.loads((R/'current-player-overview-test-variant.json').read_text('utf8'))
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name not in [W,G]}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
pages=[-930000000001001,-930000000001003,-940000000010000,-940000000012000,-941100000001000,-941100000001010,-941100000001020,-941100000001060]
selectors=[-940000000005000,-940000000008000,-940000000010020]
labels=['GK','D','DM','M','AM','ST'];tx=[];checks=[]
def add_tx(tag,target,output,before):
 src,backup=OUT/tag/target.name,OUT/('backup-'+tag)/target.name;src.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True);src.write_bytes(output);backup.write_bytes(before);tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
for tag,root in roots:
 print('Preparing '+tag,flush=True)
 before={n:(root/n).read_bytes()for n in [W,G]};env={n:UnityPy.load(b)for n,b in before.items()};obs={n:{o.path_id:o for o in e.objects}for n,e in env.items()}
 baseline={n:{i:sha(o.get_raw_data())for i,o in oo.items()}for n,oo in obs.items()};changes={W:{},G:{}}
 # The accepted FC labels provide the exact static-text prototype.
 fc=obs[W][-941100000001060].read_typetree();fr=refs(fc);protoid=named(fc,'TestPitchGroup_GK');prototype=(fr[protoid],fr[fr[protoid]['data']['m_SerializedData']['rid']])
 assert data(fr,protoid)['TextBinding']['m_kind']==0
 gap_nodes=[]
 for pid in [-941100000001020,-941100000001060]:
  doc=obs[W][pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=obs[W][sid].read_typetree();old=copy.deepcopy(sheet);st=Styles(sheet)
  bridge=named(doc,'ScoutHeaderPreservedContext');header=named(doc,'ReportOriginalManagementModulesColumn');changed=set()
  auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
  for node in [bridge,header]:
   rule=rr[node]['data']['m_RuleIndex'];assert [i for i,r in rr.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[node]
   values=[st.p(131087,auto),st.p(131096,st.px(0)),st.p(131094,none),st.p(131082,auto),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131090,st.px(0))]
   keys={p['m_Id']for p in values};props=sheet['m_Rules'][rule]['m_Properties'];sheet['m_Rules'][rule]['m_Properties']=[p for p in props if p['m_Id']not in keys]+values;changed.add(rule)
  for i,rule in enumerate(old['m_Rules']):
   if i not in changed:assert sheet['m_Rules'][i]==rule
  assert len(sheet['m_Rules'])==len(old['m_Rules']);validate_ui(doc,sheet)
  changes[W][sid]=sheet;gap_nodes.append(dict(page=pid,header=header,context=bridge,height='auto',bottom_margin=0))
 # These three shared modules are used by the six older overview choices.
 # Their existing GUIDs, object IDs, control IDs and binding overrides are kept.
 global_checks=[]
 for pid in selectors:
  doc=obs[G][pid].read_typetree();old_doc=copy.deepcopy(doc);rr=refs(doc);oldrr=copy.deepcopy(rr);sid=doc['inlineSheet']['m_PathID'];sheet=obs[G][sid].read_typetree();st=Styles(sheet)
  if pid==-940000000010020:
   parent=named(doc,'ThirdOverviewPortraitPitchRatio');inset=named(doc,'ThirdOverviewPitchSafeInset')
   # Match the actual scaled pitch width, reserving a caption band above it.
   rule=rr[inset]['data']['m_RuleIndex'];assert [i for i,r in rr.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[inset]
   ps=sheet['m_Rules'][rule]['m_Properties'];sheet['m_Rules'][rule]['m_Properties']=[p for p in ps if p['m_Id']!=131104]+[st.p(131104,st.px(20))]
   top=-20;bottom=None
  else:
   parent=named(doc,'top-section-frame');rule=rr[parent]['data']['m_RuleIndex'];assert [i for i,r in rr.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[parent]
   ps=sheet['m_Rules'][rule]['m_Properties'];sheet['m_Rules'][rule]['m_Properties']=[p for p in ps if p['m_Id']!=131102]+[st.p(131102,st.en('relative'))]
   top=None;bottom=0
  added=[]
  for column,text in enumerate(labels):
   node=add_node(doc,prototype,parent,'OverviewPitchGroup_'+text);rr=refs(doc);sd=data(rr,node);sd.update(text=text,text_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1)
   width=struct.unpack('<f',struct.pack('<f',100/6))[0];left=struct.unpack('<f',struct.pack('<f',column*100/6))[0]
   values=[st.p(131102,st.en('absolute')),st.p(131089,st.pct(left)),st.p(131105,st.pct(width)),st.p(131087,st.px(18)),st.p(131096,st.px(18)),st.p(131094,st.px(18)),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(65537,st.px(11)),st.p(65546,st.en('middle-center')),st.p(65552,st.en('nowrap'))]
   values.append(st.p(131104,st.px(top))if top is not None else st.p(131080,st.px(bottom)))
   st.edit(rr[node],values,reset=True);added.append(dict(text=text,node=node,left_percent=left))
  rr=refs(doc)
  for i,record in oldrr.items():
   if i==parent:
    expected=copy.deepcopy(record);expected['data']['m_Children'] += [{'rid':x['node']}for x in added];assert rr[i]==expected
   else:assert rr[i]==record,('Original control or binding changed',pid,i)
  assert doc['m_Usings']==old_doc['m_Usings'];graph(doc);validate_ui(doc,sheet)
  changes[G].update({pid:doc,sid:sheet});global_checks.append(dict(selector=pid,caption_parent=parent,added=added,all_existing_controls_and_bindings_preserved=True))
 # Prove every active dropdown version obtains exactly one six-label row.
 gm=next(o.read_typetree()for o in obs[G].values()if o.type.name=='AssetBundle')
 guid_to_pid={k:e['asset']['m_PathID']for k,e in gm['m_Container']if e['asset']['m_FileID']==0 and e['asset']['m_PathID']in selectors}
 page_checks=[]
 for pid in pages:
  doc=obs[W][pid].read_typetree();rr=refs(doc)
  local=[i for i,r in rr.items()if r.get('data',{}).get('name','').startswith('TestPitchGroup_')]
  if local:
   assert len(local)==6;assert {r['data']['text']for i,r in rr.items()if r.get('data',{}).get('name','').startswith('TestPitchGroup_')}==set(labels)
   selected=None
  else:
   uses=[u for u in doc['m_Usings']if u['path']in guid_to_pid and any(r.get('data',{}).get('m_TemplateAlias')==u['alias']for r in rr.values())];assert len(uses)==1
   selected=guid_to_pid[uses[0]['path']];gr=refs(changes[G][selected]);assert sum(r.get('data',{}).get('name','').startswith('OverviewPitchGroup_')for r in gr.values())==6
  page_checks.append(dict(page=pid,shared_selector=selected,labels=labels))
 for n in [W,G]:
  for i,value in changes[n].items():obs[n][i].save_typetree(value)
  output=env[n].file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(output).objects};assert readback.keys()==obs[n].keys()
  for i,h in baseline[n].items():
   if i not in changes[n]:assert sha(readback[i].get_raw_data())==h,('Unrelated object changed',n,i)
  for i,value in changes[n].items():assert readback[i].read_typetree()==value
  add_tx(tag,root/n,output,before[n])
 checks.append(dict(target=tag,scout_headers_content_sized=gap_nodes,new_labels_in_shared_selectors=global_checks,
  all_eight_dropdown_versions_covered=page_checks,
  new_fc_and_portrait_existing_caption_rows_unchanged=True,
  scout_and_pros_cons_bindings_byte_identical=True,all_pitch_position_data_bindings_unchanged=True,
  object_ids_guid_catalog_and_preload_unchanged=True,unrelated_objects_byte_identical=True))
 print('Verified '+tag+': compact report headers; all eight overview choices have GK/D/DM/M/AM/ST',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'));m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,previous_manifest=previous['manifest'],checks=checks,protected_sha256=protected,change='Remove fixed scout-header reserve above pros/cons in both current variants; add matching position captions to the three modules used by all six older variants')
for name,value in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'scout-gap-all-pitch-captions-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
