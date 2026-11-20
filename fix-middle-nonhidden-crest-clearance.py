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
OUT=R/('middle-nonhidden-crest-clearance-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);rr=refs(doc)
 crest=named(doc,'ClubImage');setter=rr[crest]['data']['m_Parent']['rid'];holder=rr[setter]['data']['m_Parent']['rid']
 layer=rr[holder]['data']['m_Parent']['rid'];stage=rr[layer]['data']['m_Parent']['rid'];column=rr[stage]['data']['m_Parent']['rid']
 def px(i,key):
  p=next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties']if p['m_Id']==key)
  v=p['m_Values'][0];assert v['m_ValueType']==3
  dim=sheet['dimensions'][v['valueIndex']];assert dim['unit']==1;return dim['value']
 column_width=px(column,131105);stage_width=px(stage,131105);layer_left=px(layer,131089)
 children=rr[layer]['data']['m_Children'];assert children[-1]['rid']==holder and len(children)==2
 flag_width=px(children[0]['rid'],131105);crest_width=px(holder,131105);margin=px(holder,131091)
 previous=px(holder,131089);base=(column_width-stage_width)/2+layer_left+flag_width+margin
 newleft=column_width-10-crest_width-base
 st.edit(rr[holder],[st.p(131089,st.px(newleft))])
 assert base+newleft+crest_width==column_width-10
 oldrr=refs(oo[PAGE].read_typetree())
 for i,old in oldrr.items():
  expected=copy.deepcopy(old)
  if i==holder:expected['data']['m_RuleIndex']=rr[i]['data']['m_RuleIndex']
  assert expected==rr[i],('Unexpected change',i)
 graph(doc);validate_ui(doc,sheet);doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
 meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle');assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='76cd79feada45acebc482721c1b688da']==[PAGE]
 oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet);output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
 for i,h in hashes.items():
  if i not in [PAGE,sid]:assert sha(new[i].get_raw_data())==h
 assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,crest_relative_left_before=previous,crest_relative_left_after=newleft,portrait_column_width=column_width,crest_right_edge=column_width-10,career_clearance_px=10,crest_size_unchanged=True,all_other_nodes_and_bindings_exact=True,other_objects_byte_identical=True,unique_guid=True))
 print('Verified '+tag,flush=True)
for n,v in [('manifest.json',dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)),('transaction.json',tx)]: (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]: (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-nonhidden-crest-clearance-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
