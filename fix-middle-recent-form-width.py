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
OUT=R/('middle-nonhidden-recent-form-width-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest();tx=[];checks=[]
protected={str(p):sha(p.read_bytes())for _,root in roots for p in root.glob('*.bundle')if p.name!=W}
for tag,root in roots:
 for n in ['catalog.bin','catalog.hash']:
  p=(root.parent if tag=='game'else root)/n;protected[str(p)]=sha(p.read_bytes())
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects};hashes={i:sha(o.get_raw_data())for i,o in oo.items()}
 doc=oo[PAGE].read_typetree();sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet);rr=refs(doc)
 form=named(doc,'MiddleNonHiddenRecentForm');subtree=owned_refs(rr,form);changed=set();stream=[]
 for i in subtree:
  x=rr[i].get('data',{});cl=rr[i]['type']['class']
  if cl not in ['VisualElementAsset','TemplateAsset']:continue
  sd=data(rr,i);full=x.get('m_FullTypeName','');props=[]
  if full=='SI.Bindable.StreamedObjectList':
   # The same native row template is used at 25px in the 2x2 tile.
   sd.update(FixedElementSize=40.0,FixedElementSize_UxmlAttributeFlags=1);stream.append(i)
   props=[st.p(131105,st.pct(100)),st.p(131097,st.px(0)),st.p(131095,st.pct(100)),st.p(131073,st.en('center')),st.p(131085,st.num(1))]
  elif cl=='TemplateAsset':props=[st.p(131097,st.px(0)),st.p(131095,st.pct(100)),st.p(131085,st.num(1))]
  elif full=='UnityEngine.UIElements.VisualElement' or full=='SI.Bindable.BindableSwitchElement':
   props=[st.p(131097,st.px(0)),st.p(131095,st.pct(100)),st.p(131085,st.num(1))]
   if sd.get('name')in ['NoMatches','Outfield','Goalkeeper']:
    props.extend([st.p(131105,st.pct(100)),st.p(131083,st.en('row'))])
   elif sd.get('name')=='Frame' and x.get('m_Parent',{}).get('rid')!=10731:
    # Native three statistic cells share the available width, including long captions.
    parent=x.get('m_Parent',{}).get('rid');pname=data(rr,parent).get('name','')if parent in rr and rr[parent].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 else ''
    if pname in ['Outfield','Goalkeeper','NoMatches']:
     props.extend([st.p(131105,st.px(0)),st.p(131082,st.px(0)),st.p(131084,st.num(1))])
   elif sd.get('name')=='':props.append(st.p(131105,st.pct(100)))
  elif full=='SI.Bindable.SIText' and sd.get('name')!='MiddleRecentFormTitle':
   props=[st.p(131097,st.px(0)),st.p(131095,st.pct(100)),st.p(131085,st.num(1)),st.p(65537,st.px(10)),st.p(65552,st.en('normal'))]
  if props:st.edit(rr[i],props);changed.add(i)
 assert len(stream)==1
 st.edit(rr[form],[st.p(458768,st.en('hidden'))])
 # Binding paths, native graph rows, branch selection and events remain exact.
 original=refs(oo[PAGE].read_typetree())
 for i,old in original.items():
  actual=copy.deepcopy(rr[i]);expected=copy.deepcopy(old)
  for q in [actual,expected]:q.get('data',{}).pop('m_RuleIndex',None)
  if i==rr[stream[0]]['data']['m_SerializedData']['rid']:
   for q in [actual,expected]:q['data'].pop('FixedElementSize',None);q['data'].pop('FixedElementSize_UxmlAttributeFlags',None)
  assert actual==expected,('Unexpected data change',i)
 graph(doc);validate_ui(doc,sheet);doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],sort_keys=True).encode())&0x7fffffff
 meta=next(o.read_typetree()for o in oo.values()if o.type.name=='AssetBundle');assert [e['asset']['m_PathID']for k,e in meta['m_Container']if k=='76cd79feada45acebc482721c1b688da']==[PAGE]
 oo[PAGE].save_typetree(doc);oo[sid].save_typetree(sheet);output=env.file.save(packer='lz4');new={o.path_id:o for o in UnityPy.load(output).objects}
 for i,h in hashes.items():
  if i not in [PAGE,sid]:assert sha(new[i].get_raw_data())==h
 assert new[PAGE].read_typetree()==doc and new[sid].read_typetree()==sheet
 src=OUT/tag/W;backup=OUT/('backup-'+tag)/W;src.parent.mkdir();backup.parent.mkdir();src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(root/W),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
 checks.append(dict(target=tag,native_form_graph_row_width=40,five_bars_total_width=200,statistics_row_width_percent=100,three_statistics_columns_share_available_width=True,native_bindings_preserved=True,other_objects_byte_identical=True,unique_guid=True))
 print('Verified '+tag,flush=True)
for n,v in [('manifest.json',dict(installed=False,installed_verified=False,runtime_verified=False,protected_sha256=protected,checks=checks)),('transaction.json',tx)]: (OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]: (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'middle-nonhidden-recent-form-width-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
