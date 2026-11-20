"""Name the approved portrait layout and clone it with the existing left FC card."""
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
SOURCE,DONOR=-941100000001020,-940000000010000
PAGE,STYLE,DESC=-941100000001060,-941100000001061,-941100000001062
SET_ID,COMPOSITION_ID,HOST_ID=1332213496068314481,3901662990989568885,7857044477279960178
IDENT='PlayerOverviewLeftFCHiddenApproved';TITLEKEY='OverviewLeftFCHiddenApprovedTitle'
TITLE='左边版FC卡面+隐藏';GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-approved-left-fc-hidden-overview-v1').hex
OUT=R/('approved-left-portrait-and-fc-hidden-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
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

def graft_fc(doc,sheet,donor,ds):
 rr,dr=refs(doc),refs(donor);oldroot=named(doc,'ReportPortraitStatusColumn');newroot=named(donor,'ReportPortraitStatusColumn')
 removed=owned_refs(rr,oldroot);imported=owned_refs(dr,newroot)
 parent=rr[oldroot]['data']['m_Parent']['rid'];slot=rr[parent]['data']['m_Children'].index({'rid':oldroot})
 oldrootrule=copy.deepcopy(sheet['m_Rules'][rr[oldroot]['data']['m_RuleIndex']]['m_Properties'])
 doc['references']['RefIds']=[r for r in doc['references']['RefIds']if r['rid']not in removed]
 kept=refs(doc);assert all(link not in removed for i,r in kept.items()if i!=parent for link in rid_links(r.get('data',{})))
 start=max(kept)+1;ridmap={i:start+j for j,i in enumerate(sorted(imported))}
 nodes=[i for i in imported if 'm_Id'in dr[i].get('data',{})]
 nextid=max(r.get('data',{}).get('m_Id',0)for r in kept.values())+1
 idmap={dr[i]['data']['m_Id']:nextid+j for j,i in enumerate(sorted(nodes))};assert max(idmap.values())<2147483647
 rulemap={}
 def remap(v):
  if isinstance(v,list):
   for x in v:remap(x)
  elif isinstance(v,dict):
   if set(v)=={'rid'}:
    if v['rid']in ridmap:v['rid']=ridmap[v['rid']]
   else:
    for k,x in list(v.items()):
     if k in ['m_Id','m_ParentId','uxmlAssetId','m_ElementId']and isinstance(x,int)and x in idmap:v[k]=idmap[x]
     elif k=='m_ElementIdsPath':v[k]=[idmap.get(n,n)for n in x]
     else:remap(x)
 for i in sorted(imported):
  item=copy.deepcopy(dr[i]);item['rid']=ridmap[i];remap(item['data']);d=item['data']
  if i==newroot:d['m_Parent']={'rid':parent}
  rule=d.get('m_RuleIndex',-1)
  if rule>=0:
   if rule not in rulemap:
    value=copy.deepcopy(ds['m_Rules'][rule])
    for prop in value['m_Properties']:
     for h in prop['m_Values']:
      pool=poolmap.get(h['m_ValueType'])
      if pool:sheet[pool].append(copy.deepcopy(ds[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
    rulemap[rule]=len(sheet['m_Rules']);sheet['m_Rules'].append(value)
   d['m_RuleIndex']=rulemap[rule]
  alias=d.get('m_TemplateAlias')
  if alias:
   use=next(u for u in donor['m_Usings']if u['alias']==alias);existing=next((u for u in doc['m_Usings']if u['alias']==alias),None)
   if existing:assert existing==use,('Alias conflict',alias)
   else:doc['m_Usings'].append(copy.deepcopy(use))
  doc['references']['RefIds'].append(item)
 kept[parent]['data']['m_Children'][slot]={'rid':ridmap[newroot]}
 result=refs(doc)
 for i in imported:
  expected=copy.deepcopy(dr[i]);expected['rid']=ridmap[i];remap(expected['data'])
  if i==newroot:expected['data']['m_Parent']={'rid':parent}
  if expected['data'].get('m_RuleIndex',-1)>=0:expected['data']['m_RuleIndex']=rulemap[expected['data']['m_RuleIndex']]
  assert result[ridmap[i]]==expected
 # Fit the complete original card uniformly into the existing 226x250 slot.
 # All inner card coordinates, templates, ratings and image functions stay intact.
 st=Styles(sheet);stage=ridmap[named(donor,'ReportPortraitLayerStage')];scale=226/286
 st.edit(result[ridmap[newroot]],oldrootrule,reset=True)
 st.edit(result[stage],[st.p(327681,st.num(scale),st.num(scale)),st.p(327682,st.pct(50),st.pct(0)),st.p(131093,st.px(struct.unpack('<f',struct.pack('<f',12+23*scale))[0]))])
 graph(doc);validate_ui(doc,sheet)
 return dict(root=ridmap[newroot],stage=stage,removed=removed,imported=imported,ridmap=ridmap,parent=parent,scale=scale)

for tag,base in [('game',GAME),('skin',SKIN)]:
 print('Preparing '+tag,flush=True)
 catpath=(base.parent if tag=='game'else base)/'catalog.bin';hashpath=catpath.with_name('catalog.hash')
 initial={n:(base/n).read_bytes()for n in [W,L]};catbefore=catpath.read_bytes();hashbefore=hashpath.read_bytes();cat=cm.Catalog(catbefore)
 env={n:UnityPy.load(b)for n,b in initial.items()};obs={n:{o.path_id:o for o in e.objects}for n,e in env.items()}
 hashes={n:{i:sha(o.get_raw_data())for i,o in oo.items()}for n,oo in obs.items()};modified={W:{},L:{}}
 assert PAGE not in obs[W]and STYLE not in obs[W]and DESC not in obs[L]
 source=obs[W][SOURCE].read_typetree();donor=obs[W][DONOR].read_typetree();doc=copy.deepcopy(source)
 sheet=obs[W][source['inlineSheet']['m_PathID']].read_typetree();ds=obs[W][donor['inlineSheet']['m_PathID']].read_typetree()
 detail=graft_fc(doc,sheet,donor,ds);nr=refs(doc);orr=refs(source)
 for i,value in orr.items():
  if i not in detail['removed']and i!=detail['parent']:assert nr[i]==value,('Outside portrait changed',i)
 # The entire old approved page and style remain byte-identical in the bundle.
 doc.update(m_Name='OverviewLeftFCHiddenApproved',inlineSheet={'m_FileID':0,'m_PathID':STYLE},m_ContentHash=struct.unpack('<i',struct.pack('<I',zlib.crc32(GUID.encode())))[0])
 sheet['m_Name']='OverviewLeftFCHiddenApprovedStyle'
 add(W,source['inlineSheet']['m_PathID'],STYLE,sheet);add(W,SOURCE,PAGE,doc)
 abobj=next(o for o in obs[W].values()if o.type.name=='AssetBundle');meta=abobj.read_typetree();oldmeta=copy.deepcopy(meta)
 donor_key,donor_entry=next((k,v)for k,v in oldmeta['m_Container']if v['asset']=={'m_FileID':0,'m_PathID':DONOR})
 extras=copy.deepcopy(oldmeta['m_PreloadTable'][donor_entry['preloadIndex']:donor_entry['preloadIndex']+donor_entry['preloadSize']])
 for ptr in extras:
  if ptr['m_FileID']==0:ptr['m_PathID']={DONOR:PAGE,donor['inlineSheet']['m_PathID']:STYLE}.get(ptr['m_PathID'],ptr['m_PathID'])
 source_key,span=register(SOURCE,PAGE,STYLE,GUID,extras)
 donor_loc=next(i for i in cat.locations(donor_key)if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
 cat,deps=catalog_add(cat,source_key,GUID,cat.location(donor_loc)['dependencies'])
 # Reused FC visual functions must resolve to an actual registered function.
 functions=set()
 def collect(v):
  if isinstance(v,list):
   for x in v:collect(x)
  elif isinstance(v,dict):
   if set(v)=={'m_guid'}and v['m_guid']:functions.add(v['m_guid'])
   for x in v.values():collect(x)
 for i in detail['imported']:collect(refs(donor)[i].get('data',{}))
 for key in functions:
  entries=[cat.location(i)for i in cat.locations(key)if cat.location(i)['type'][1].endswith('VisualFunction')]
  assert len(entries)==1,('FC function unregistered',key)
  assert entries[0]['dependencies']
 meta['m_Container'].sort(key=lambda x:x[0]);save(W,abobj.path_id,meta)
 desc=obs[L][-941100000001022].read_typetree();desc.update(m_Name='OverviewLeftFCHiddenApprovedDescription',m_translationType=2,m_directTitlePath={'m_path':TITLEKEY})
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
 titles={'OverviewLeftTestVariantTitle':'左边版大头像+隐藏','OverviewLeftPortraitHiddenVariantTitle':'左边版大头像+隐藏（旧版）','OverviewLeftFCVariantTitle':'左边版FC卡面+隐藏（旧版）'}
 for key,title in titles.items():
  variable=next(v for v in variables['ValueVariables']if v['m_name']==key)
  variable['m_scopeValue']['m_serializedData']='String|'+title+'|'
  pattern=r'(\{'+re.escape(key)+r'\}\{String\|)[^|]*(\|\})'
  textprop['value'],count=re.subn(pattern,lambda m:m[1]+title+m[2],textprop['value']);assert count==1
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
 audits.append(dict(target=tag,approved_page_and_style_byte_identical=True,non_portrait_regions_exact=True,
  fc_source=DONOR,fc_inner_data_and_bindings_exact_after_id_remap=True,fc_function_guids=sorted(functions),
  fc_uniform_scale=detail['scale'],avatar_slot=[226,250],layout_choices=8,layout_preload_spans_updated=preloads,
  previous_choices_and_placements_preserved=True,old_same_name_entries_retained_with_old_label=True))
 print('Verified '+tag+': approved portrait retained; FC-only clone; eight choices',flush=True)
if CACHE.exists():
 b=CACHE.read_bytes();c=json.loads(b);oldcache=copy.deepcopy(c);assert not any(p['m_elementID']==IDENT for p in c['m_placementBindings'])
 c['m_placementBindings'].append(copy.deepcopy(placement));assert c['m_gridComponents']==oldcache['m_gridComponents']
 assert c['m_placementBindings'][:-1]==oldcache['m_placementBindings']
 add_tx('cache',CACHE,json.dumps(c,ensure_ascii=False,separators=(',',':')).encode('utf8'),b)
for row in transaction:assert sha(Path(row['target']).read_bytes())==row['before']
for path,h in protected.items():assert sha(Path(path).read_bytes())==h
m=json.loads(Path(previous['manifest']).read_text('utf8'))
m.update(installed=False,installed_verified=False,runtime_verified=False,previous_manifest=previous['manifest'],
 approved=dict(page=SOURCE,title='左边版大头像+隐藏',ident='PlayerOverviewLeftTest'),
 fc=dict(page=PAGE,style=STYLE,description=DESC,guid=GUID,title=TITLE,ident=IDENT),
 audits=audits,catalog_audits=catalog_audits,protected_sha256=protected,
 saved_active_selection_and_positions_unchanged=True)
for name,value in [('manifest.json',m),('transaction.json',transaction),('previous-index.json',previous),('verification-prepared.json',dict(passed=True,audits=audits,catalog_audits=catalog_audits,runtime_verified=False))]:
 (OUT/name).write_text(json.dumps(value,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8');needle='for row in tx:\n';assert installer.count(needle)==1
installer=installer.replace(needle,'allowed.add(Path('+repr(str(CACHE.parent))+').resolve())\n'+needle)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'approved-left-fc-hidden-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8');print(OUT,flush=True)
