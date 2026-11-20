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
OUT=R/('middle-nonhidden-career-scroll-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);rr=refs(doc)
 # Use a private inline career template so scrolling never changes other pages.
 native=oo[5779084658590882123].read_typetree();ns=oo[native['inlineSheet']['m_PathID']].read_typetree()
 for u in native['m_Usings']:
  existing=next((a for a in doc['m_Usings']if a['alias']==u['alias']),None)
  if existing and existing!=u:
   oldalias=u['alias'];newalias='NonHiddenCareerScroll_'+oldalias;u['alias']=newalias
   for ref in native['references']['RefIds']:
    x=ref.get('data',{})
    if x.get('m_TemplateAlias')==oldalias:x['m_TemplateAlias']=newalias
    if x.get('templateId')==oldalias:x['templateId']=newalias
 detail=graft(doc,sheet,native,ns,named(doc,'CareerStatsLargeTileTemplate'),1001);rr=refs(doc);st=Styles(sheet)
 for i in detail['ridmap'].values():
  if rr[i].get('data',{}).get('m_FullTypeName')=='SI.Bindable.StreamedObjectList':
   sd=data(rr,i)
   for k,v in [('VerticalScrollerVisibility',1),('HorizontalScrollerVisibility',2),('ScrollViewMode',0)]:sd[k]=v;sd[k+'_UxmlAttributeFlags']=1
 # A bounded scroll viewport ends 20px before the old right edge.
 parent=named(doc,'OverviewTopRightStatusPanel');content=named(doc,'ApprovedHeaderCareerPlayerContext')
 proto=(copy.deepcopy(rr[5850]),copy.deepcopy(rr[rr[5850]['data']['m_SerializedData']['rid']]))
 scroll=add_node(doc,proto,parent,'MiddleNonHiddenCareerVerticalScroll');rr=refs(doc)
 rr[parent]['data']['m_Children'].remove({'rid':content});rr[scroll]['data']['m_Children']=[{'rid':content}];rr[content]['data']['m_Parent']={'rid':scroll}
 sd=data(rr,scroll)
 for k,v in [('verticalScrollerVisibility',1),('horizontalScrollerVisibility',2),('mode',0),('showVertical',1),('showHorizontal',0)]:sd[k]=v;sd[k+'_UxmlAttributeFlags']=1
 st.edit(rr[scroll],[st.p(131102,st.en('absolute')),st.p(131089,st.px(0)),st.p(131103,st.px(20)),st.p(131104,st.px(0)),st.p(131080,st.px(0)),st.p(131105,{'m_ValueType':1,'valueIndex':2}),st.p(131087,{'m_ValueType':1,'valueIndex':2}),st.p(131096,st.px(0)),st.p(131097,st.px(0)),st.p(131084,st.num(0)),st.p(131085,st.num(1))],reset=True)
 for i in [content,9457,9458]:
  rr[i]['data']['m_Classes']=[c for c in rr[i]['data']['m_Classes']if c not in ['height-100-percent','flex-grow-class']]
  st.edit(rr[i],[st.p(131087,{'m_ValueType':1,'valueIndex':2}),st.p(131096,st.px(300)),st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131082,{'m_ValueType':1,'valueIndex':2}),st.p(131084,st.num(0)),st.p(131085,st.num(0)),st.p(131105,st.pct(100)),st.p(131097,st.px(0))])
 # Move only the crest 20px to the right from its currently installed position.
 crest=named(doc,'ClubImage');holder=rr[rr[crest]['data']['m_Parent']['rid']]['data']['m_Parent']['rid']
 rule=sheet['m_Rules'][rr[holder]['data']['m_RuleIndex']];v=next(p for p in rule['m_Properties']if p['m_Id']==131089)['m_Values'][0];previous=sheet['dimensions'][v['valueIndex']]['value'];st.edit(rr[holder],[st.p(131089,st.px(previous+20))])
 graph(doc);validate_ui(doc,sheet);doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
 meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle');assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='76cd79feada45acebc482721c1b688da']==[PAGE]
 oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet);output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
 for i,h in hashes.items():
  if i not in [PAGE,sid]:assert sha(new[i].get_raw_data())==h
 assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,career_outer_vertical_scrollbar_visible=True,native_career_list_scrollbar_visible=True,career_right_edge_inset_px=20,crest_move_right_px=20,crest_left_before=previous,crest_left_after=previous+20,other_objects_byte_identical=True,unique_guid=True))
 print('Verified '+tag,flush=True)
for n,v in [('manifest.json',dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)),('transaction.json',tx)]: (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]: (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-nonhidden-career-scroll-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
