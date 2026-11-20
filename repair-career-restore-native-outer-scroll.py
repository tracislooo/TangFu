"""Restore the proven native career block; put scrolling around it, not inside it."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value;poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links'}),('split-season-radar-two-charts.py',{'add_node','graph'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
index=R/'current-player-overview-test-variant.json';previous=json.loads(index.read_text('utf8'));BAD=Path(previous['manifest']).parent
assert BAD.name.startswith('approved-career-statistics-vertical-scroll-')
OUT=R/('career-native-restored-outer-scroll-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
tx=[];checks=[]
for tag,root in roots:
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 working={o.path_id:o for o in UnityPy.load(str(BAD/('backup-'+tag)/W)).objects};changes={};pages=[]
 # The native module itself was never changed. Confirm exact known-working bytes.
 native=oo[5779084658590882123].read_typetree();native_refs=refs(native)
 for pid in [5779084658590882123,native['inlineSheet']['m_PathID']]:
  assert working[pid].get_raw_data()==oo[pid].get_raw_data()
 assert data(native_refs,1006)['Binding']['m_kind']==2
 for pid in [-941100000001020,-941100000001060]:
  doc=oo[pid].read_typetree();rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
  old_doc=copy.deepcopy(doc);working_doc=working[pid].read_typetree();wr=refs(working_doc);working_sheet=working[sid].read_typetree()
  alias='ApprovedHeaderCareer_CareerStatsLargeTileTemplate';use=next(u for u in doc['m_Usings']if u['alias']==alias);native_use=next(u for u in working_doc['m_Usings']if u['alias']==alias)
  assert native_use['path']=='59857998b6983074b81d0423f446feca';use.clear();use.update(copy.deepcopy(native_use))
  instance=next(i for i,r in rr.items()if r.get('data',{}).get('m_TemplateAlias')==alias);parent=rr[instance]['data']['m_Parent']['rid']
  # Undo both zero-height/basis edits from the failed change, using the old indices.
  for node in [parent,instance]:
   oldrule=wr[node]['data']['m_RuleIndex']
   if oldrule>=0:assert sheet['m_Rules'][oldrule]==working_sheet['m_Rules'][oldrule]
   rr[node]['data']['m_RuleIndex']=oldrule
  prototype=(rr[5850],rr[rr[5850]['data']['m_SerializedData']['rid']])
  scroll=add_node(doc,prototype,parent,'ApprovedCareerNativeOuterScroll');rr=refs(doc)
  rr[parent]['data']['m_Children'].remove({'rid':instance});rr[scroll]['data']['m_Children']=[{'rid':instance}];rr[instance]['data']['m_Parent']={'rid':scroll}
  sd=data(rr,scroll)
  for key,value in {'mode':0,'horizontalScrollerVisibility':2,'verticalScrollerVisibility':1,'mouseWheelScrollSize':36.0}.items():sd[key]=value;sd[key+'_UxmlAttributeFlags']=1
  sd['showVertical_UxmlAttributeFlags']=0
  st.edit(rr[scroll],[st.p(131105,st.pct(100)),st.p(131097,st.px(0)),st.p(131095,st.pct(100)),st.p(131087,st.px(200)),st.p(131096,st.px(200)),st.p(131094,st.px(200)),st.p(131082,st.px(200)),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(458768,st.en('hidden'))],reset=True)
  # Natural content height retains the original native list's 176px measured size.
  auto={'m_ValueType':1,'valueIndex':2};none={'m_ValueType':1,'valueIndex':3}
  st.edit(rr[instance],[st.p(131105,st.pct(100)),st.p(131097,st.px(0)),st.p(131087,auto),st.p(131096,st.px(0)),st.p(131094,none),st.p(131082,auto),st.p(131084,st.num(0)),st.p(131085,st.num(0))],reset=True)
  for i,record in refs(old_doc).items():
   a,b=copy.deepcopy(record),copy.deepcopy(rr[i])
   for v in [a,b]:
    for key in ['m_Parent','m_Children','m_RuleIndex']:v.get('data',{}).pop(key,None)
   assert a==b,('Existing data or bindings changed',i)
  assert data(rr,instance)==data(wr,instance)
  assert next(u for u in doc['m_Usings']if u['alias']==alias)==native_use
  graph(doc);validate_ui(doc,sheet);changes.update({pid:doc,sid:sheet})
  pages.append(dict(page=pid,original_career_template_and_serialized_instance_exactly_restored=True,
    original_native_list_binding_and_row_template_untouched=True,outer_scroll_node=scroll,
    scroll_height=200,scroll_height_basis_nonzero=True,vertical_scrollbar=1,
    failed_private_career_asset_no_longer_used=True))
 for pid,value in changes.items():oo[pid].save_typetree(value)
 output=env.file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(output).objects};assert readback.keys()==oo.keys()
 for pid,h in hashes.items():
  if pid not in changes:assert sha(readback[pid].get_raw_data())==h
 for pid,value in changes.items():assert readback[pid].read_typetree()==value
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,pages=pages,working_donor=str(BAD/('backup-'+tag)/W),
  original_native_career_module_byte_identical_to_working_version=True,unrelated_objects_byte_identical=True))
 print('Verified '+tag+': known-working native career restored; only outer scroll added',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'));m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,previous_manifest=previous['manifest'],checks=checks,protected_sha256=protected,change='Restore the known-working native career module and container; add a separate 200px outer SIScrollView; do not modify the native data binding or list')
for n,v in [('manifest.json',m),('transaction.json',tx),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'career-native-outer-scroll-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
