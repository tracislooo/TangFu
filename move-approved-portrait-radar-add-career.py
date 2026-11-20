"""Portrait layout only: career statistics in the header, radar in transfer slot."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,sys,uuid,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links'}),('split-season-radar-two-charts.py',{'add_node','graph'}),('add-card-six-ratings.py',{'validate_ui'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
PAGE,STYLE=-941100000001020,-941100000001021
RADAR,RADARSTYLE=-941100000001080,-941100000001081
GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-approved-left-portrait-lower-season-radar-v1').hex
CAREER=-8751479712270500017
OUT=R/('approved-portrait-career-header-radar-transfer-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));GAME,SKIN=Path(loc['bundle_root']),Path(loc['skin_packages'])
previous=json.loads((R/'current-player-overview-test-variant.json').read_text('utf8'))
reserved={int(x['path_id'])for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
transaction=[];catalog_audits=[];checks=[]
protected={str(p):sha(p.read_bytes())for base in [GAME,SKIN]for p in base.glob('*.bundle')if p.name!=W}
t=ast.parse((R/'add-left-test-overview.py').read_text('utf8'));wanted={'save','add','add_tx','register','catalog_add'}
exec(compile(ast.Module(body=[n for n in ast.walk(t)if isinstance(n,ast.FunctionDef)and n.name in wanted],type_ignores=[]),'register','exec'))
t=ast.parse((R/'implement-test-overview-aligned-header.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in ast.walk(t)if isinstance(n,ast.FunctionDef)and n.name=='import_template'],type_ignores=[]),'native-import','exec'))
for tag,base in [('game',GAME),('skin',SKIN)]:
 print('Preparing '+tag,flush=True)
 before=(base/W).read_bytes();env={W:UnityPy.load(before)};obs={W:{o.path_id:o for o in env[W].objects}};oo=obs[W]
 baseline={i:sha(o.get_raw_data())for i,o in oo.items()};modified={W:{}}
 assert RADAR not in oo and RADARSTYLE not in oo
 catpath=(base.parent if tag=='game'else base)/'catalog.bin';hashpath=catpath.with_name('catalog.hash');catbefore=catpath.read_bytes();hashbefore=hashpath.read_bytes();cat=cm.Catalog(catbefore)
 abobj=next(o for o in oo.values()if o.type.name=='AssetBundle');meta=abobj.read_typetree();oldmeta=copy.deepcopy(meta)
 # A private presentation copy protects the FC version's shared radar and data.
 radar=oo[-941100000001050].read_typetree();original_radar=copy.deepcopy(radar)
 rs=oo[-941100000001051].read_typetree();rst=Styles(rs);rr=refs(radar)
 def edit_r(node,values):
  rule=rr[node]['data']['m_RuleIndex'];assert [i for i,r in rr.items()if r.get('data',{}).get('m_RuleIndex')==rule]==[node]
  keys={p['m_Id']for p in values};p=rs['m_Rules'][rule]['m_Properties'];rs['m_Rules'][rule]['m_Properties']=[v for v in p if v['m_Id']not in keys]+values
 def r(node,values):edit_r(node,[rst.p(k,v)for k,v in values])
 case=named(radar,'WorkingSeasonRadarGoalkeeperSwitch')
 for node in [1041,case]:
  r(node,[(131105,rst.pct(100)),(131097,rst.px(0)),(131095,rst.pct(100)),(131087,rst.px(200)),(131096,rst.px(200)),(131094,rst.px(200))])
 captions=[]
 for branch in rr[case]['data']['m_Children']:
  overlay=next(c['rid']for c in rr[branch['rid']]['data']['m_Children']if data(rr,c['rid']).get('name')=='SeasonRadarDirectAxisLabels')
  r(overlay,[(131105,rst.pct(100)),(131097,rst.px(0)),(131095,rst.pct(100)),(131087,rst.px(200)),(131096,rst.px(200)),(131094,rst.px(200))])
  boxes=[(25,2,50),(65,38,35),(65,134,35),(25,170,50),(0,134,35),(0,38,35)]
  for child,(x,y,w)in zip(rr[overlay]['data']['m_Children'],boxes):
   r(child['rid'],[(131089,rst.pct(x)),(131104,rst.px(y)),(131105,rst.pct(w))]);captions.append(dict(node=child['rid'],left_percent=x,top=y,width_percent=w))
 assert radar==original_radar # all native contexts, formulas and six-axis data intact
 radar.update(m_Name='ApprovedPortraitLowerSeasonRadar',inlineSheet={'m_FileID':0,'m_PathID':RADARSTYLE},m_ContentHash=struct.unpack('<i',struct.pack('<I',zlib.crc32(GUID.encode())))[0]);rs['m_Name']='ApprovedPortraitLowerSeasonRadarStyle'
 add(W,-941100000001051,RADARSTYLE,rs);add(W,-941100000001050,RADAR,radar)
 radar_source_key,radar_span=register(-941100000001050,RADAR,RADARSTYLE,GUID)
 cat,radar_deps=catalog_add(cat,radar_source_key,GUID)
 doc=oo[PAGE].read_typetree();old_doc=copy.deepcopy(doc);sheet=oo[STYLE].read_typetree();st=Styles(sheet);pr=refs(doc)
 def pe(node,values):st.edit(refs(doc)[node],[st.p(k,v)for k,v in values])
 # Move the existing instance; retain the old transfer node as hidden content.
 assert pr[6304]['data']['m_Parent']=={'rid':2242}
 pr[2242]['data']['m_Children'].remove({'rid':6304})
 pr[6312]['data']['m_Children'].insert(0,{'rid':6304});pr[6304]['data']['m_Parent']={'rid':6312}
 pe(6314,[(131081,st.en('none'))])
 pe(6304,[(131105,st.pct(100)),(131097,st.px(0)),(131095,st.pct(100)),(131087,st.px(200)),(131096,st.px(200)),(131094,st.px(200)),(131082,st.px(200)),(131084,st.num(0)),(131085,st.num(0))])
 pr=refs(doc);data(pr,6304)['template']={'m_FileID':0,'m_PathID':RADAR}
 alias=pr[6304]['data']['m_TemplateAlias'];use=next(u for u in doc['m_Usings']if u['alias']==alias);use.update(path=GUID,asset={'m_FileID':0,'m_PathID':RADAR})
 # Reuse the entire native career module with the same player context as a tile.
 prototype=(pr[6312],pr[pr[6312]['data']['m_SerializedData']['rid']])
 career_context=add_node(doc,prototype,2242,'ApprovedHeaderCareerPlayerContext');pr=refs(doc)
 assert data(pr,career_context)['Mappings']==[{'m_serialisedType':0,'from':'player','to':{'m_path':'person'},'type':{'id':1145176065}}]
 pe(career_context,[(131105,st.pct(100)),(131097,st.px(0)),(131087,st.pct(100)),(131096,st.px(0)),(131082,st.px(0)),(131084,st.num(1)),(131085,st.num(1)),(131083,st.en('column'))])
 af=oo[PAGE].assets_file;stale_overrides=[]
 career_root,career_map=import_template(oo[CAREER],career_context,'ApprovedHeaderCareer_')
 pe(career_root,[(131105,st.pct(100)),(131097,st.px(0)),(131087,st.pct(100)),(131096,st.px(0)),(131082,st.px(0)),(131084,st.num(1)),(131085,st.num(1))])
 transparent='de14e90fe14655249deefc697f132781'
 assert cat.locations(transparent)
 changed_frame=0
 for u in doc['m_Usings']:
  if u['alias'].startswith('ApprovedHeaderCareer_')and u['path']=='f677caec43d6c1342b1bba39c5ae2c5f':u['path']=transparent;changed_frame+=1
 assert changed_frame==1
 # Extend only this page's preload and dependency closure for the added modules.
 page_key,page_entry=next((k,v)for k,v in meta['m_Container']if v['asset']=={'m_FileID':0,'m_PathID':PAGE})
 career_key,career_entry=next((k,v)for k,v in oldmeta['m_Container']if v['asset']=={'m_FileID':0,'m_PathID':CAREER})
 career_span=oldmeta['m_PreloadTable'][career_entry['preloadIndex']:career_entry['preloadIndex']+career_entry['preloadSize']]
 page_span=copy.deepcopy(meta['m_PreloadTable'][page_entry['preloadIndex']:page_entry['preloadIndex']+page_entry['preloadSize']])
 for ptr in list(radar_span)+list(career_span):
  if ptr not in page_span:page_span.append(copy.deepcopy(ptr))
 assert not any(p['m_PathID']in reserved for p in page_span)
 page_entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(page_span));meta['m_PreloadTable'].extend(page_span)
 page_loc=next(i for i in cat.locations(page_key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 career_loc=next(i for i in cat.locations(career_key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 deps=list(dict.fromkeys(cat.location(page_loc)['dependencies']+radar_deps+cat.location(career_loc)['dependencies']))
 assert cat.location(deps[0])['internal'].endswith(W)
 depbytes=b''.join(struct.pack('<I',i)for i in deps);dep_offset=cat.append(depbytes,True);struct.pack_into('<2I',cat.data,page_loc+12,dep_offset,zlib.crc32(depbytes));cat=cm.Catalog(bytes(cat.data))
 assert cat.location(page_loc)['dependencies']==deps
 meta['m_Container'].sort(key=lambda x:x[0]);save(W,abobj.path_id,meta)
 graph(doc);validate_ui(doc,sheet);validate_ui(radar,rs)
 # Every old serialized binding survives, except the relocated template pointer.
 before_refs=refs(old_doc);after_refs=refs(doc);template_sd=before_refs[6304]['data']['m_SerializedData']['rid']
 for i,old in before_refs.items():
  if 'm_Parent'in old.get('data',{}):
   a=copy.deepcopy(old);b=copy.deepcopy(after_refs[i])
   for v in [a,b]:
    for key in ['m_Parent','m_Children','m_RuleIndex']:v['data'].pop(key,None)
   assert a==b,('Existing node changed',i)
  elif i==template_sd:
   expected=copy.deepcopy(old);expected['data']['template']={'m_FileID':0,'m_PathID':RADAR};assert after_refs[i]==expected
  else:assert after_refs[i]==old,('Existing data binding changed',i)
 assert after_refs[6312]['data']['m_Children']==[{'rid':6304},{'rid':6314},{'rid':6318},{'rid':6316}]
 save(W,PAGE,doc);save(W,STYLE,sheet)
 output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==oo.keys()
 for i,h in baseline.items():
  if i not in modified[W]:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',i)
 for i,value in modified[W].items():assert check[i].read_typetree()==value
 # In particular, the FC layout and its shared header radar are untouched.
 for i in [-941100000001060,-941100000001061,-941100000001050,-941100000001051]:assert sha(check[i].get_raw_data())==baseline[i]
 add_tx(tag,base/W,output,before);catout=bytes(cat.data);add_tx(tag,catpath,catout,catbefore);add_tx(tag,hashpath,hashlib.md5(catout).hexdigest().encode('ascii'),hashbefore)
 checks.append(dict(target=tag,portrait_page_only=True,old_radar_instance_moved_without_rebuilding=True,
  lower_radar=RADAR,lower_radar_height=200,lower_radar_labels=captions,season_context_and_all_formulas_unchanged=True,
  original_transfer_module_hidden_and_retained=True,favoured_people_and_pros_cons_retained=True,
  native_career_source=CAREER,native_career_root=career_root,native_career_context=career_context,
  native_career_controls=career_map,career_player_maps_to_person=True,transparent_career_frame=True,
  new_radar_catalog_preload_verified=True,portrait_page_preload_and_dependency_closure_updated=True,
  fc_page_and_shared_header_radar_byte_identical=True,selector_and_saved_layouts_untouched=True,
  unrelated_objects_byte_identical=True))
 print('Verified '+tag+': portrait career header and lower fallback radar; FC layout unchanged',flush=True)
m=json.loads(Path(previous['manifest']).read_text('utf8'));m.update(installed=False,installed_verified=False,runtime_verified=False,restored=False,previous_manifest=previous['manifest'],checks=checks,catalog_audits=catalog_audits,protected_sha256=protected,change='Approved portrait page only: move season radar into transfer fallback, retain favoured/pros-cons, native career statistics in old radar slot',portrait_lower_radar=dict(page=RADAR,style=RADARSTYLE,guid=GUID))
for name,value in [('manifest.json',m),('transaction.json',transaction),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,checks=checks,catalog_audits=catalog_audits,runtime_verified=False))]:(OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'portrait-career-radar-transfer-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
