"""Clone the current approved left portrait page without altering its contents."""
from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,re,struct,sys,uuid,zlib
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('add-card-six-ratings.py',{'validate_ui'}),('split-season-radar-two-charts.py',{'graph'})]:
 t=ast.parse((R/fn).read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef))and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle'
SOURCE=-941100000001020
PAGE,STYLE,DESC=-941100000001100,-941100000001101,-941100000001102
SET_ID,COMPOSITION_ID,HOST_ID=1332213496068314481,3901662990989568885,7857044477279960178
IDENT='PlayerOverviewLeftPortraitNonhiddenApproved';TITLEKEY='OverviewLeftPortraitNonhiddenApprovedTitle'
TITLE='左边版大头像+无隐藏';GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-approved-left-portrait-nonhidden-overview-v1').hex
OUT=R/('approved-left-portrait-nonhidden-clone-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(loc['bundle_root']),Path(loc['skin_packages'])
CACHE=Path.home()/'AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large'
previous=json.loads((R/'current-player-overview-test-variant.json').read_text('utf8'))
reserved={int(x['path_id'])for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
assert not reserved.intersection([PAGE,STYLE,DESC])
transaction=[];audits=[];catalog_audits=[]
protected={str(p):sha(p.read_bytes())for base in [GAME,SKIN]for p in base.glob('*.bundle')if p.name not in [W,L]}
# Reuse the repository's guarded registration and transaction helpers.
t=ast.parse((R/'add-left-test-overview.py').read_text('utf8'))
helpers={'add_tx','save','add','register','catalog_add'}
exec(compile(ast.Module(body=[n for n in ast.walk(t)if isinstance(n,ast.FunctionDef)and n.name in helpers],type_ignores=[]),'registration-helpers','exec'))

for tag,base in [('game',GAME),('skin',SKIN)]:
 print('Preparing '+tag,flush=True)
 catpath=(base.parent if tag=='game'else base)/'catalog.bin';hashpath=catpath.with_name('catalog.hash')
 initial={n:(base/n).read_bytes()for n in [W,L]};catbefore=catpath.read_bytes();hashbefore=hashpath.read_bytes();cat=cm.Catalog(catbefore)
 env={n:UnityPy.load(b)for n,b in initial.items()};obs={n:{o.path_id:o for o in e.objects}for n,e in env.items()}
 hashes={n:{i:sha(o.get_raw_data())for i,o in oo.items()}for n,oo in obs.items()};modified={W:{},L:{}}
 assert PAGE not in obs[W]and STYLE not in obs[W]and DESC not in obs[L]
 source=obs[W][SOURCE].read_typetree();doc=copy.deepcopy(source)
 source_style=source['inlineSheet']['m_PathID'];sheet=obs[W][source_style].read_typetree()
 original_sheet=copy.deepcopy(sheet)
 doc.update(m_Name='OverviewLeftPortraitNonhiddenApproved',inlineSheet={'m_FileID':0,'m_PathID':STYLE},m_ContentHash=struct.unpack('<i',struct.pack('<I',zlib.crc32(GUID.encode())))[0])
 sheet['m_Name']='OverviewLeftPortraitNonhiddenApprovedStyle'
 assert {k:v for k,v in doc.items()if k not in ['m_Name','inlineSheet','m_ContentHash']}=={k:v for k,v in source.items()if k not in ['m_Name','inlineSheet','m_ContentHash']}
 assert {k:v for k,v in sheet.items()if k!='m_Name'}=={k:v for k,v in original_sheet.items()if k!='m_Name'}
 validate_ui(doc,sheet);graph(doc)
 add(W,source_style,STYLE,sheet);add(W,SOURCE,PAGE,doc)
 abobj=next(o for o in obs[W].values()if o.type.name=='AssetBundle');meta=abobj.read_typetree();oldmeta=copy.deepcopy(meta)
 assert GUID not in {key for key,_ in cat.keys()}
 source_key,span=register(SOURCE,PAGE,STYLE,GUID)
 cat,deps=catalog_add(cat,source_key,GUID)
 meta['m_Container'].sort(key=lambda x:x[0]);save(W,abobj.path_id,meta)
 desc=obs[L][-941100000001022].read_typetree();desc.update(m_Name='OverviewLeftPortraitNonhiddenApprovedDescription',m_translationType=2,m_directTitlePath={'m_path':TITLEKEY})
 desc['<Name>k__BackingField']=desc['<ID>k__BackingField']=IDENT
 for cfg in desc['<Configurations>k__BackingField']:cfg['Description']={'m_FileID':0,'m_PathID':DESC};cfg['AssetRef']['m_AssetGUID']=GUID
 add(L,-941100000001022,DESC,desc)
 ts=obs[L][SET_ID].read_typetree();oldset=copy.deepcopy(ts);ts['m_gridElementDescriptions'].append({'m_FileID':0,'m_PathID':DESC});save(L,SET_ID,ts)
 composition=obs[L][COMPOSITION_ID].read_typetree();oldcomp=copy.deepcopy(composition)
 placement=dict(m_elementID=IDENT,m_optionalConditions=[],m_optionalConfigConditions=[]);composition['m_placementBindings'].append(copy.deepcopy(placement));save(L,COMPOSITION_ID,composition)
 assert composition['m_placementBindings'][:-1]==oldcomp['m_placementBindings']
 la=next(o for o in obs[L].values()if o.type.name=='AssetBundle');lm=la.read_typetree();preloads=0
 for _,entry in lm['m_Container']:
  span2=copy.deepcopy(lm['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
  if any(p['m_FileID']==0 and p['m_PathID']in [SET_ID,COMPOSITION_ID]for p in span2):
   span2.append({'m_FileID':0,'m_PathID':DESC});entry['preloadIndex']=len(lm['m_PreloadTable']);entry['preloadSize']=len(span2);lm['m_PreloadTable'].extend(span2);preloads+=1
 assert preloads>=3;save(L,la.path_id,lm)
 host=obs[W][HOST_ID].read_typetree();hr=refs(host)
 variables=next(r['data']for r in hr.values()if r.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
 props=next(r['data']['m_Properties']for r in hr.values()if r.get('data',{}).get('m_Id')==variables['uxmlAssetId']);textprop=next(p for p in props if p['name']=='value-vars')
 assert not any(v['m_name']==TITLEKEY or v.get('m_scopeValue',{}).get('m_serializedData')=='String|'+TITLE+'|' for v in variables['ValueVariables'])
 variables['ValueVariables'].append(dict(m_name=TITLEKEY,m_scopeValue={'m_serializedData':'String|'+TITLE+'|'}))
 textprop['value']+=',{'+TITLEKEY+'}{String|'+TITLE+'|}'
 grid=next(r['data']['Bindings']for r in hr.values()if r.get('data',{}).get('Bindings',{}).get('m_gridCompositionSet',{}).get('m_PathID')==1615455816372668659)
 oldgrid=copy.deepcopy(grid);grid['m_nameBindings'].append(dict(name=TITLEKEY,path={'m_path':TITLEKEY},method=0))
 mappings=copy.deepcopy([m for m in grid['m_gridElementBindingData']if m['DescriptionAndMapping']['DescriptionName']=='PlayerOverviewLeftTest'and m['DescriptionAndMapping']['MappingName']!='OverviewLeftTestVariantTitle'])
 assert {'person','player','team','isonmainscreen'}<={m['DescriptionAndMapping']['MappingName']for m in mappings}
 for mapping in mappings:mapping['DescriptionAndMapping']['DescriptionName']=IDENT
 mappings.append(dict(DescriptionAndMapping=dict(DescriptionName=IDENT,MappingName=TITLEKEY,MappingReferenceID=0),BindingPath={'m_path':''},IsDynamic=0));grid['m_gridElementBindingData'].extend(mappings)
 assert grid['m_gridElementBindingData'][:-len(mappings)]==oldgrid['m_gridElementBindingData'];save(W,HOST_ID,host)
 for n,e in env.items():
  output=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==obs[n].keys()
  for pid,h in hashes[n].items():
   if pid not in modified[n]:assert sha(check[pid].get_raw_data())==h,('Unrelated change',tag,n,pid)
  for pid,value in modified[n].items():assert check[pid].read_typetree()==value
  add_tx(tag,base/n,output,initial[n])
 oldcat=cm.Catalog(catbefore);assert len(cat.key_records)==len(oldcat.key_records)+1
 current_keys=set(cat.keys())
 for key,locations in oldcat.keys():
  if key=='GameWorldVisualTreeAssetPreload':assert cat.locations(key)[:-1]==oldcat.locations(key)
  else:assert (key,locations)in current_keys
 catout=bytes(cat.data);add_tx(tag,catpath,catout,catbefore);add_tx(tag,hashpath,hashlib.md5(catout).hexdigest().encode('ascii'),hashbefore)
 audits.append(dict(target=tag,source_page=SOURCE,source_page_and_style_byte_identical=True,cloned_contents_and_bindings_exact=True,private_style=True,previous_choices_and_placements_preserved=True,layout_preload_spans_updated=preloads))
 print('Verified '+tag+': exact portrait clone; existing choices preserved',flush=True)
if CACHE.exists():
 b=CACHE.read_bytes();c=json.loads(b);oldcache=copy.deepcopy(c);assert not any(p['m_elementID']==IDENT for p in c['m_placementBindings'])
 c['m_placementBindings'].append(copy.deepcopy(placement));assert c['m_gridComponents']==oldcache['m_gridComponents']
 assert c['m_placementBindings'][:-1]==oldcache['m_placementBindings']
 add_tx('cache',CACHE,json.dumps(c,ensure_ascii=False,separators=(',',':')).encode('utf8'),b)
for row in transaction:assert sha(Path(row['target']).read_bytes())==row['before']
for path,h in protected.items():assert sha(Path(path).read_bytes())==h
m=dict(installed=False,installed_verified=False,runtime_verified=False,previous_manifest=previous['manifest'],
 version=dict(page=PAGE,style=STYLE,description=DESC,guid=GUID,title=TITLE,ident=IDENT,source_page=SOURCE),
 audits=audits,catalog_audits=catalog_audits,protected_sha256=protected,
 clone_contents_unchanged=True,all_unrelated_bundle_objects_byte_identical=True,saved_active_selection_and_positions_unchanged=True)
for name,value in [('manifest.json',m),('transaction.json',transaction),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,audits=audits,catalog_audits=catalog_audits,runtime_verified=False))]:
 (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8');needle='for row in tx:\n';assert installer.count(needle)==1
installer=installer.replace(needle,'allowed.add(Path('+repr(str(CACHE.parent))+').resolve())\n'+needle)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'approved-left-portrait-nonhidden-clone-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
