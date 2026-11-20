"""Refine the installed nonhidden middle portrait page incrementally."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph','add_node'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-930000000001003
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('middle-nonhidden-stats-width-fix-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);rr=refs(doc)
 # Native cells retain flex-basis:0. With grow:0 this collapses both columns.
 changes=[]
 for name in ['SeasonStatsGoalkeeperPanel','SeasonStatsOutfielderPanel']:
  panel=named(doc,name)
  st.edit(rr[panel],[st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131085,st.num(1)),st.p(131096,st.px(0))])
  rows=rr[panel]['data']['m_Children'];assert len(rows)==3
  for rowptr in rows:
   row=rowptr['rid']
   st.edit(rr[row],[st.p(131105,st.pct(100)),st.p(131082,st.px(0)),st.p(131084,st.num(1)),st.p(131085,st.num(1)),st.p(131087,{'m_ValueType':1,'valueIndex':2}),st.p(131096,st.px(40)),st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131090,st.px(0))])
   cells=[c['rid']for c in rr[row]['data']['m_Children']if 'Cell_'in data(rr,c['rid']).get('name','')]
   assert len(cells)==2
   for cell in cells:
    st.edit(rr[cell],[st.p(131082,st.pct(50)),st.p(131105,st.pct(50)),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131097,st.px(0)),st.p(131095,st.pct(50)),st.p(131087,st.pct(100)),st.p(131096,st.px(0))])
    changes.append(cell)
 assert len(changes)==12
 # All data, component registrations, node ordering, separators and portrait stay exact.
 olddoc=oo[PAGE].read_typetree();oldrr=refs(olddoc)
 for i,old in oldrr.items():
  actual=copy.deepcopy(rr[i]);expected=copy.deepcopy(old)
  actual.get('data',{}).pop('m_RuleIndex',None);expected.get('data',{}).pop('m_RuleIndex',None)
  assert actual==expected,('Non-style change',i)
 graph(doc);validate_ui(doc,sheet);doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
 meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle');assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='76cd79feada45acebc482721c1b688da']==[PAGE]
 oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet);output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
 for i,h in hashes.items():
  if i not in [PAGE,sid]:assert sha(new[i].get_raw_data())==h
 assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,both_branches=True,two_equal_columns=True,cell_flex_basis_percent=50,cell_shrink=0,three_rows_share_available_height=True,data_and_separators_exact=True,portrait_exact=True,other_objects_byte_identical=True,unique_guid=True))
 print('Verified '+tag,flush=True)
for n,v in [('manifest.json',dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)),('transaction.json',tx)]: (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]: (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-nonhidden-stats-width-fix-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
