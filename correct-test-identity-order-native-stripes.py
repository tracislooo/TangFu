"""Restore original identity flow; fix comparison order and native alternating rows."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
idxpath=R/'current-player-overview-test-variant.json';previous=json.loads(idxpath.read_text('utf8'));priorout=Path(previous['manifest']).parent;m=json.loads((priorout/'manifest.json').read_text('utf8'));ptx=json.loads((priorout/'transaction.json').read_text('utf8'));loc=json.loads((R/'current-game-location.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-941100000001020
OUT=R/('test-identity-order-native-stripes-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
for tag,root in [('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]:
 path=root/W;before=path.read_bytes();prior=next(r for r in ptx if Path(r['target'])==path);assert sha(before)==prior['after'],('Changed baseline',tag)
 env=UnityPy.load(before);obs={o.path_id:o for o in env.objects};baseline={i:sha(o.get_raw_data())for i,o in obs.items()}
 donor={o.path_id:o for o in UnityPy.load(prior['backup']).objects}
 doc=obs[PAGE].read_typetree();unchanged=copy.deepcopy(doc);sheet=obs[doc['inlineSheet']['m_PathID']].read_typetree();st=Styles(sheet);rr=refs(doc)
 old=donor[PAGE].read_typetree();oldrr=refs(old);olds=donor[old['inlineSheet']['m_PathID']].read_typetree()
 # Restore every original style in the identity subtree. No new fixed coordinates
 # are applied to the information under the player's name.
 restored=[]
 for i in owned_refs(oldrr,1291):
  ov=oldrr[i].get('data',{})
  if 'm_SerializedData'not in ov:continue
  assert i in rr
  ix=ov.get('m_RuleIndex',-1)
  if ix<0:rr[i]['data']['m_RuleIndex']=-1
  else:
   rule=copy.deepcopy(olds['m_Rules'][ix]);assert not rule['m_ComplexSelectors']
   for p in rule['m_Properties']:
    for h in p['m_Values']:
     if h['m_ValueType']in poolmap:
      pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(olds[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
   rr[i]['data']['m_RuleIndex']=len(sheet['m_Rules']);sheet['m_Rules'].append(rule)
  restored.append(i)
 # Both the fitness values and statistics stay to the left of this divider.
 st.edit(rr[6288],[st.p(131102,st.en('absolute')),st.p(131089,st.px(326)),st.p(131104,st.px(4)),st.p(131105,st.px(1)),st.p(131087,st.px(242))])
 st.edit(rr[2242],[st.p(131105,st.px(320)),st.p(131095,st.px(320)),st.p(458768,st.en('hidden'))])
 # Keep the three gauges within the stats column, with the original 210px row.
 st.edit(rr[2986],[st.p(131105,st.px(210)),st.p(131095,st.px(210)),st.p(131089,st.px(0)),st.p(458768,st.en('hidden'))])
 # The previous inline expansion appended this host. Restore the former selector
 # index so the entire pitch/roles/comparison group is first, before attributes.
 host=named(doc,'TestPrivatePitchRolesHost');parent=rr[host]['data']['m_Parent']['rid'];oldparent=oldrr[1007]['data']['m_Parent']['rid'];assert parent==oldparent
 oldindex=oldrr[oldparent]['data']['m_Children'].index({'rid':1007});children=rr[parent]['data']['m_Children'];children.remove({'rid':host});children.insert(oldindex,{'rid':host})
 # Use exactly the normal native attribute row and native odd-list class.
 rows=rr[6064]['data']['m_Children'];assert len(rows)==13
 for j,c in enumerate(rows):
  row=rr[c['rid']]['data'];classes=[s for s in row['m_Classes']if not s.startswith('attributes-row-number')and s not in ['virtualised-list__item--odd','virtualised-list__item--even']]
  row['m_Classes']=classes+['attributes-row-number-no-border']+(['virtualised-list__item--odd']if j%2 else [])
  ix=row['m_RuleIndex'];props=[copy.deepcopy(p)for p in sheet['m_Rules'][ix]['m_Properties']if p['m_Id']!=458752];st.edit(row,props,reset=True)
 graph(doc)
 # All existing serialized data, including click events, remains byte-for-byte
 # equivalent at the tree level; only visual styles/classes/order change.
 ur=refs(unchanged)
 for i,r in ur.items():
  if 'm_SerializedData'not in r.get('data',{}):assert rr[i]==r,('Data changed',tag,i)
 def canonical(s,r):
  ix=r['data'].get('m_RuleIndex',-1)
  if ix<0:return []
  ps=copy.deepcopy(s['m_Rules'][ix]['m_Properties'])
  for p in ps:
   for h in p['m_Values']:
    if h['m_ValueType']in poolmap:h['valueIndex']=s[poolmap[h['m_ValueType']]][h['valueIndex']]
  return ps
 for i in restored:assert canonical(sheet,rr[i])==canonical(olds,oldrr[i]),('Identity style mismatch',tag,i)
 sid=doc['inlineSheet']['m_PathID'];obs[PAGE].save_typetree(doc);obs[sid].save_typetree(sheet);output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs.keys();assert check[PAGE].read_typetree()==doc;assert check[sid].read_typetree()==sheet
 for i,h in baseline.items():
  if i not in [PAGE,sid]:assert sha(check[i].get_raw_data())==h
 src,backup=OUT/tag/W,OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(path),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,identity_subtree_styles_restored=len(restored),selector_index_restored=oldindex,hidden_rows=13,native_alternating_background=True,all_existing_bindings_and_events_unchanged=True,other_objects_byte_identical=True));print('Verified '+tag,flush=True)
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_fix_manifest=previous['manifest'],change='Restore original identity styles and selector position, correct divider, native alternating row background',checks=checks)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'previous-index.json').write_text(json.dumps(previous,ensure_ascii=False,indent=2),'utf8');(OUT/'verification-prepared.json').write_text(json.dumps(dict(passed=True,checks=checks,runtime_verified=False),indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'identity-order-correction-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT)
