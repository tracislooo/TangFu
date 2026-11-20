"""Private full-career list with visible vertical scrolling in both new layouts."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,uuid,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links'}),('split-season-radar-two-charts.py',{'graph'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
SOURCE=5779084658590882123;PAGE,STYLE=-941100000001090,-941100000001091
GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-approved-career-statistics-full-scroll-v1').hex
TARGETS=[-941100000001020,-941100000001060]
OUT=R/('approved-career-statistics-vertical-scroll-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME,SKIN=Path(loc['bundle_root']),Path(loc['skin_packages'])
previous=json.loads((R/'current-player-overview-test-variant.json').read_text('utf8'))
reserved={int(x['path_id'])for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
transaction=[];catalog_audits=[];checks=[]
protected={str(p):sha(p.read_bytes())for base in [GAME,SKIN]for p in base.glob('*.bundle')if p.name!=W}
t=ast.parse((R/'add-left-test-overview.py').read_text('utf8'));helpers={'save','add','add_tx','register','catalog_add'}
exec(compile(ast.Module(body=[n for n in ast.walk(t)if isinstance(n,ast.FunctionDef)and n.name in helpers],type_ignores=[]),'register-helpers','exec'))
for tag,base in [('game',GAME),('skin',SKIN)]:
 print('Preparing '+tag,flush=True)
 before=(base/W).read_bytes();env={W:UnityPy.load(before)};obs={W:{o.path_id:o for o in env[W].objects}};oo=obs[W];hashes={i:sha(o.get_raw_data())for i,o in oo.items()};modified={W:{}}
 assert PAGE not in oo and STYLE not in oo
 catpath=(base.parent if tag=='game'else base)/'catalog.bin';hashpath=catpath.with_name('catalog.hash');catbefore=catpath.read_bytes();hashbefore=hashpath.read_bytes();cat=cm.Catalog(catbefore)
 abobj=next(o for o in oo.values()if o.type.name=='AssetBundle');meta=abobj.read_typetree();oldmeta=copy.deepcopy(meta)
 doc=oo[SOURCE].read_typetree();original=copy.deepcopy(doc);rr=refs(doc);sid=doc['inlineSheet']['m_PathID'];sheet=oo[sid].read_typetree();st=Styles(sheet)
 list_node=1006;sd=data(rr,list_node);old_binding=copy.deepcopy(sd['Binding'])
 assert bytes(old_binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']).endswith(b'Player.CareerStatsPerSeasonLeagueOnly')
 # Preserve the native full data source instead of its tile-only first-five slice.
 sd['Binding']['m_kind']=1;sd['Binding']['m_direct']={'Path':{'m_path':'Player.CareerStatsPerSeasonLeagueOnly'},'Nullable':0}
 fields={'VerticalScrollerVisibility':1,'HorizontalScrollerVisibility':2,'ScrollViewMode':0,'ClampSizeToPage':0,'Truncate':0,'MouseWheelScrollSize':36.0}
 for key,value in fields.items():sd[key]=value;sd[key+'_UxmlAttributeFlags']=1
 for node in [1001,1002,list_node]:
  st.edit(rr[node],[st.p(131105,st.pct(100)),st.p(131097,st.px(0)),st.p(131095,st.pct(100)),st.p(131087,st.px(0)),st.p(131096,st.px(0)),st.p(131094,{'m_ValueType':1,'valueIndex':3}),st.p(131082,st.px(0)),st.p(131084,st.num(1)),st.p(131085,st.num(1)),st.p(131083,st.en('column')),st.p(458768,st.en('hidden'))])
 oldrr=refs(original);list_sd=rr[list_node]['data']['m_SerializedData']['rid']
 for i,ref in oldrr.items():
  if i==list_sd:
   expected=copy.deepcopy(ref);expected['data']['Binding']['m_kind']=1;expected['data']['Binding']['m_direct']={'Path':{'m_path':'Player.CareerStatsPerSeasonLeagueOnly'},'Nullable':0}
   for key,value in fields.items():expected['data'][key]=value;expected['data'][key+'_UxmlAttributeFlags']=1
   assert rr[i]==expected
  else:
   a,b=copy.deepcopy(ref),copy.deepcopy(rr[i]);a.get('data',{}).pop('m_RuleIndex',None);b.get('data',{}).pop('m_RuleIndex',None);assert a==b
 assert sd['FixedElementSize']==36. and sd['DynamicElements']==0
 assert sd['RowTemplate']==data(oldrr,list_node)['RowTemplate']
 doc.update(m_Name='ApprovedFullCareerStatisticsScroll',inlineSheet={'m_FileID':0,'m_PathID':STYLE},m_ContentHash=struct.unpack('<i',struct.pack('<I',zlib.crc32(GUID.encode())))[0]);sheet['m_Name']='ApprovedFullCareerStatisticsScrollStyle'
 graph(doc);validate_ui(doc,sheet);add(W,sid,STYLE,sheet);add(W,SOURCE,PAGE,doc)
 source_key,span=register(SOURCE,PAGE,STYLE,GUID);cat,deps=catalog_add(cat,source_key,GUID)
 page_checks=[]
 for target in TARGETS:
  page=oo[target].read_typetree();old_page=copy.deepcopy(page);pr=refs(page);psid=page['inlineSheet']['m_PathID'];ps=oo[psid].read_typetree();pst=Styles(ps)
  alias='ApprovedHeaderCareer_CareerStatsLargeTileTemplate';use=next(u for u in page['m_Usings']if u['alias']==alias)
  assert use['path']=='59857998b6983074b81d0423f446feca';use['path']=GUID
  instance=next(i for i,r in pr.items()if r.get('data',{}).get('m_TemplateAlias')==alias)
  parent=pr[instance]['data']['m_Parent']['rid']
  for node in [parent,instance]:
   pst.edit(pr[node],[pst.p(131105,pst.pct(100)),pst.p(131097,pst.px(0)),pst.p(131087,pst.px(0)),pst.p(131096,pst.px(0)),pst.p(131094,{'m_ValueType':1,'valueIndex':3}),pst.p(131082,pst.px(0)),pst.p(131084,pst.num(1)),pst.p(131085,pst.num(1)),pst.p(131083,pst.en('column')),pst.p(458768,pst.en('hidden'))])
  for i,ref in refs(old_page).items():
   a,b=copy.deepcopy(ref),copy.deepcopy(pr[i]);a.get('data',{}).pop('m_RuleIndex',None);b.get('data',{}).pop('m_RuleIndex',None);assert a==b,('Existing data binding changed',target,i)
  page_key,entry=next((k,e)for k,e in meta['m_Container']if e['asset']=={'m_FileID':0,'m_PathID':target})
  preload=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
  for ptr in span:
   if ptr not in preload:preload.append(copy.deepcopy(ptr))
  assert not any(p['m_PathID']in reserved for p in preload)
  entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(preload));meta['m_PreloadTable'].extend(preload)
  location=next(i for i in cat.locations(page_key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
  olddeps=cat.location(location)['dependencies'];combined=list(dict.fromkeys(olddeps+deps));assert cat.location(combined[0])['internal'].endswith(W)
  if combined!=olddeps:
   raw=b''.join(struct.pack('<I',i)for i in combined);offset=cat.append(raw,True);struct.pack_into('<2I',cat.data,location+12,offset,zlib.crc32(raw));cat=cm.Catalog(bytes(cat.data))
  graph(page);validate_ui(page,ps);save(W,target,page);save(W,psid,ps)
  page_checks.append(dict(page=target,career_instance=instance,scroll_viewport_bounded_to_remaining_height=True))
 meta['m_Container'].sort(key=lambda x:x[0]);save(W,abobj.path_id,meta)
 output=env[W].file.save(packer='lz4');readback={o.path_id:o for o in UnityPy.load(output).objects};assert readback.keys()==oo.keys()
 for i,h in hashes.items():
  if i not in modified[W]:assert sha(readback[i].get_raw_data())==h,('Unrelated object changed',i)
 for i,value in modified[W].items():assert readback[i].read_typetree()==value
 add_tx(tag,base/W,output,before);catout=bytes(cat.data);add_tx(tag,catpath,catout,catbefore);add_tx(tag,hashpath,hashlib.md5(catout).hexdigest().encode('ascii'),hashbefore)
 checks.append(dict(target=tag,pages=page_checks,vertical_scrollbar_visibility=1,horizontal_scrollbar_visibility=2,
  native_summary_and_career_row_templates_preserved=True,native_fixed_row_height=36,
  career_data_source='Player.CareerStatsPerSeasonLeagueOnly',removed_native_five_season_slice=True,
  full_data_list_scrolls_with_mouse_wheel=True,other_six_variants_and_original_career_module_unchanged=True,
  new_asset_and_page_preloads_verified=True,unrelated_objects_byte_identical=True))
 print('Verified '+tag+': two career viewports with full season list and visible vertical scrollbar',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'));m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,previous_manifest=previous['manifest'],protected_sha256=protected,checks=checks,catalog_audits=catalog_audits,change='Visible vertical career scrollbars in the two new variants; preserve totals and native rows; expose the complete existing career-season data source',career_scroll_asset=dict(page=PAGE,style=STYLE,guid=GUID))
for name,value in [('manifest.json',m),('transaction.json',transaction),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,catalog_audits=catalog_audits,runtime_verified=False))]:(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'approved-career-scroll-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
