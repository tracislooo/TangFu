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
source=(R/'sync-middle-portrait-hidden-to-fc.py').read_text('utf8')
exec(source[source.index("source=(R/'add-approved"):source.index('spec=importlib')])
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';PAGE=-930000000001003
loc=json.loads((R/'current-game-location.json').read_text('utf8'));roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('middle-nonhidden-recent-form-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);rr=refs(doc)
 def delete(node):
  rr=refs(doc);parent=rr[node]['data']['m_Parent']['rid'];rr[parent]['data']['m_Children'].remove({'rid':node});gone=owned_refs(rr,node);doc['references']['RefIds']=[x for x in doc['references']['RefIds']if x['rid']not in gone]
 FORM=4708141797674504207
 donor=copy.deepcopy(oo[FORM].read_typetree());ds=oo[donor['inlineSheet']['m_PathID']].read_typetree();dr=refs(donor)
 # Keep native binding expect and content, omit the background-bearing tile wrapper.
 keep=owned_refs(dr,1004)|{1000,1001,dr[1001]['data']['m_SerializedData']['rid']}
 donor['references']['RefIds']=[x for x in donor['references']['RefIds']if x['rid']in keep or x['rid']==-2]
 dr=refs(donor);dr[1001]['data']['m_Children']=[{'rid':1004}];dr[1004]['data']['m_Parent']={'rid':1001}
 dst=Styles(ds)
 def fill(i):
  dst.edit(dr[i],[dst.p(131105,dst.pct(100)),dst.p(131087,dst.pct(100)),dst.p(131097,dst.px(0)),dst.p(131096,dst.px(0)),dst.p(131095,{'m_ValueType':1,'valueIndex':3}),dst.p(131094,{'m_ValueType':1,'valueIndex':3}),dst.p(131082,dst.px(0)),dst.p(131084,dst.num(1)),dst.p(131085,dst.num(1))])
 fill(1004);fill(1008)
 # A static module heading replaces the omitted native tile header.
 proto=(copy.deepcopy(dr[1025]),copy.deepcopy(dr[dr[1025]['data']['m_SerializedData']['rid']]))
 heading=add_node(donor,proto,1001,'MiddleRecentFormTitle');dr=refs(donor);hd=data(dr,heading)
 for key,v in list(hd.items()):
  if isinstance(v,dict)and 'm_kind'in v:v['m_kind']=0
 hd.update(text='近期表现',text_UxmlAttributeFlags=1,tooltip='',tooltip_UxmlAttributeFlags=1)
 dr[heading]['data']['m_Classes']=[]
 dst.edit(dr[heading],[dst.p(131105,dst.pct(100)),dst.p(131087,dst.px(22)),dst.p(131096,dst.px(22)),dst.p(131094,dst.px(22)),dst.p(131084,dst.num(0)),dst.p(131085,dst.num(0)),dst.p(65537,dst.px(12)),dst.p(65546,dst.en('middle-left'))],reset=True)
 dr[1001]['data']['m_Children']=[{'rid':heading},{'rid':1004}]
 # Remove any background decoration from the private copy only.
 for i,v in dr.items():
  x=v.get('data',{})
  if 'm_Classes'in x:x['m_Classes']=[c for c in x['m_Classes']if not c.startswith('tf27-module-bg-') and c not in ['frame-generic-with-padding','tile-content']]
  if v['type']['class']in ['VisualElementAsset','TemplateAsset']:
   dst.edit(v,[dst.p(458752,dst.h(4,dict(r=0.,g=0.,b=0.,a=0.)))])
 oldpanel=named(doc,'SeasonStatsGoalkeeperPanel');sw=rr[oldpanel]['data']['m_Parent']['rid'];oldtable=rr[sw]['data']['m_Parent']['rid']
 detail=graft(doc,sheet,donor,ds,oldtable,1001);rr=refs(doc);st=Styles(sheet);newroot=detail['root'];data(rr,newroot)['name']='MiddleNonHiddenRecentForm'
 st.edit(rr[newroot],[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131104,st.pct(50)),st.p(131105,st.pct(100)),st.p(131087,st.pct(50)),st.p(131096,st.px(0)),st.p(131097,st.px(0)),st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131082,{'m_ValueType':1,'valueIndex':2}),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131083,st.en('column')),st.p(131099,st.px(6)),st.p(131100,st.px(6)),st.p(131101,st.px(4))],reset=True)
 assert named(doc,'NonHiddenRadarDataHorizontalDivider') and named(doc,'NonHiddenStatsProsConsVerticalDivider')
 assert not any('StatCell_'in data(rr,i).get('name','')for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2)
 graph(doc);validate_ui(doc,sheet);doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
 ab=next(o for o in oo.values()if o.type.name=='AssetBundle');meta=ab.read_typetree();assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='76cd79feada45acebc482721c1b688da']==[PAGE]
 # Transfer the native form dependencies and actual preload references.
 key,entry=next((k,e)for k,e in meta['m_Container']if e['asset']['m_PathID']==PAGE)
 fkey,fe=next((k,e)for k,e in meta['m_Container']if e['asset']['m_PathID']==FORM)
 span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
 for ptr in meta['m_PreloadTable'][fe['preloadIndex']:fe['preloadIndex']+fe['preloadSize']]:
  if ptr not in span:span.append(copy.deepcopy(ptr))
 entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 import importlib.util
 sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
 cp=(root.parent if tag=='game'else root)/'catalog.bin';cb=cp.read_bytes();cat=cm.Catalog(cb)
 cl=next(i for i in cat.locations(key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'));fl=next(i for i in cat.locations(fkey)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 deps=list(dict.fromkeys(cat.location(cl)['dependencies']+cat.location(fl)['dependencies']))
 if deps!=cat.location(cl)['dependencies']:
  raw=b''.join(struct.pack('<I',i)for i in deps);offset=cat.append(raw,True);struct.pack_into('<2I',cat.data,cl+12,offset,zlib.crc32(raw))
 assert cat.location(deps[0])['internal'].endswith(W) and cl in cat.locations('GameWorldVisualTreeAssetPreload')
 co=bytes(cat.data)
 if co!=cb:
  for target,value in [(cp,co),(cp.with_name('catalog.hash'),hashlib.md5(co).hexdigest().encode())]:
   protected.pop(str(target));src=OUT/tag/target.name;backup=OUT/('backup-'+tag)/target.name;src.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True);src.write_bytes(value);backup.write_bytes(target.read_bytes());tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(backup.read_bytes()),after=sha(value)))
 changes={PAGE:doc,sid:sheet,ab.path_id:meta}
 for i,v in changes.items():oo[i].save_typetree(v)
 output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
 for i,h in hashes.items():
  if i not in changes:assert sha(new[i].get_raw_data())==h
 for i,v in changes.items():assert new[i].read_typetree()==v,('Serialization mismatch',i)
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True);src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,native_form_tile=FORM,native_graph_and_position_branches_preserved=True,native_background_wrapper_removed=True,old_statistics_removed=True,horizontal_vertical_lines_preserved=True,catalog_preload_dependencies_verified=True,other_objects_byte_identical=True,unique_guid=True))
 print('Verified '+tag,flush=True)
for n,v in [('manifest.json',dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)),('transaction.json',tx)]: (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]: (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-nonhidden-recent-form-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
