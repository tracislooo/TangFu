"""Copy the installed old left portrait page and its middle nonhidden info region."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, sys, zlib
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
for fn,names in [('build-fc-player-hover-layout.py',{'write','Styles'}),('add-two-portrait-hidden-overviews.py',{'refs','data','named','rid_links','owned_refs'}),('split-season-radar-two-charts.py',{'graph'}),('add-card-six-ratings.py',{'validate_ui'}),('verify-two-portrait-hidden-overviews.py',{'canonical'})]:
 t=ast.parse((R/fn).read_text('utf8'))
 exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),fn,'exec'))
TypeTreeHelper.write_value=write
s=(R/'sync-old-left-portrait-hidden-to-fc.py').read_text('utf8')
exec(s[s.index("source=(R/'add-approved"):s.index('spec=importlib')])
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
L='ui-tileslayouts_assets_all.bundle'
PAGE,SOURCE,DONOR=-940000000012000,-941100000001010,-930000000001003
KEY='d5277a1342b858ee8159a09846366205'
TITLE='左边大头像+无隐藏（旧版）'
TITLEKEY='OverviewLeftPortraitVariantTitle'
HOST=7857044477279960178
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
roots=[('game',Path(loc['bundle_root'])),('skin',Path(loc['skin_packages']))]
OUT=R/('old-left-portrait-nonhidden-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
protected={str(p):sha(p.read_bytes()) for _,root in roots for p in root.glob('*.bundle') if p.name!=W}
reserved={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
tx=[];checks=[]
def add_tx(tag,target,output,before):
 src=OUT/tag/target.name;backup=OUT/('backup-'+tag)/target.name
 src.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True)
 src.write_bytes(output);backup.write_bytes(before)
 tx.append(dict(target=str(target),source=str(src),backup=str(backup),before=sha(before),after=sha(output)))
def normalized(doc,sheet,node):
 temp=copy.deepcopy(doc);temp['m_VisualTree']={'rid':node};return canonical(temp,sheet)
for tag,root in roots:
 print('Preparing '+tag,flush=True)
 before=(root/W).read_bytes();env=UnityPy.load(before);oo={o.path_id:o for o in env.objects}
 baseline={i:sha(o.get_raw_data()) for i,o in oo.items()}
 original=oo[PAGE].read_typetree();sid=original['inlineSheet']['m_PathID']
 source=oo[SOURCE].read_typetree();ss=oo[source['inlineSheet']['m_PathID']].read_typetree()
 doc=copy.deepcopy(source);sheet=copy.deepcopy(ss)
 doc.update(m_Name=original['m_Name'],inlineSheet=copy.deepcopy(original['inlineSheet']))
 sheet['m_Name']=oo[sid].read_typetree()['m_Name']
 donor=oo[DONOR].read_typetree();ds=oo[donor['inlineSheet']['m_PathID']].read_typetree()
 # Rename only conflicting template aliases in the imported region.
 existing={u['alias']:u for u in doc['m_Usings']}
 renames={u['alias']:'LeftNonHidden_'+u['alias'] for u in donor['m_Usings'] if u['alias'] in existing and u!=existing[u['alias']]}
 def rename(v):
  if isinstance(v,list):return [rename(x) for x in v]
  if isinstance(v,dict):return {k:rename(x) for k,x in v.items()}
  return renames.get(v,v) if isinstance(v,str) else v
 donor=rename(donor)
 oldroot=named(doc,'InfoBlockFrame');newroot=named(donor,'InfoBlockFrame')
 detail=graft(doc,sheet,donor,ds,oldroot,newroot)
 rr=refs(doc)
 for i,v in refs(source).items():
  if i not in detail['removed'] and i!=detail['parent']:assert rr[i]==v,('Source layout changed outside requested region',i)
 assert normalized(doc,sheet,detail['root'])==normalized(donor,ds,newroot)
 # Entire retained portrait, feet, identity, attributes, pitch and career areas match the source.
 for name in ['ReportPortraitStatusColumn','OldLeftFCCompetitionAppearancesAndAbilityRadar','ThirdOverviewMiddleColumn']:
  assert normalized(doc,sheet,named(doc,name))==normalized(source,ss,named(source,name)),name
 assert not any('RightHidden' in data(rr,i).get('name','') for i in rr if rr[i].get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2)
 assert named(doc,'MiddleNonHiddenRecentForm') and named(doc,'MiddleNonHiddenSeasonRadarAndTwelveStats')
 graph(doc);validate_ui(doc,sheet)
 doc['m_ContentHash']=zlib.crc32(json.dumps([doc,sheet],ensure_ascii=False,sort_keys=True).encode('utf8'))&0x7fffffff
 # Change the selector title only; leave every other host property/binding unchanged.
 host=oo[HOST].read_typetree();oldhost=copy.deepcopy(host);title_updates=0
 def retitle(v):
  global title_updates
  if isinstance(v,list):
   for x in v:retitle(x)
  elif isinstance(v,dict):
   if v.get('m_name')==TITLEKEY:
    value=v['m_scopeValue'];value['m_serializedData']='String|'+TITLE+'|';title_updates+=1
   for k,x in list(v.items()):
    if isinstance(x,str) and '{'+TITLEKEY+'}{String|' in x:
     v[k],n=re.subn(r'\{'+TITLEKEY+r'\}\{String\|[^|]*\|\}',lambda m:'{'+TITLEKEY+'}{String|'+TITLE+'|}',x);title_updates+=n
    elif isinstance(x,(list,dict)):retitle(x)
 retitle(host);assert title_updates==2,title_updates
 host['m_ContentHash']=zlib.crc32(json.dumps(host,ensure_ascii=False,sort_keys=True).encode('utf8'))&0x7fffffff
 ab=next(o for o in oo.values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
 def entry(pid):return next((k,e) for k,e in meta['m_Container'] if e['asset']=={'m_FileID':0,'m_PathID':pid})
 key,e=entry(PAGE);assert key==KEY
 # Remove any obsolete competing registration for this exact selector GUID.
 meta['m_Container']=[(k,v) for k,v in meta['m_Container'] if k!=KEY or v['asset']=={'m_FileID':0,'m_PathID':PAGE}]
 assert [v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==KEY]==[PAGE]
 span=copy.deepcopy(meta['m_PreloadTable'][e['preloadIndex']:e['preloadIndex']+e['preloadSize']]);donorkeys=[]
 for pid in [SOURCE,DONOR]:
  k,en=entry(pid);donorkeys.append(k);td=oo[pid].read_typetree()
  for ptr in meta['m_PreloadTable'][en['preloadIndex']:en['preloadIndex']+en['preloadSize']]:
   ptr=copy.deepcopy(ptr)
   if ptr['m_FileID']==0:ptr['m_PathID']={pid:PAGE,td['inlineSheet']['m_PathID']:sid}.get(ptr['m_PathID'],ptr['m_PathID'])
   if ptr not in span:span.append(ptr)
 assert not any(p['m_PathID'] in reserved for p in span)
 e.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 cp=(root.parent if tag=='game' else root)/'catalog.bin';cb=cp.read_bytes();cat=cm.Catalog(cb)
 matches=[i for i in cat.locations(KEY) if cat.location(i)['type'][1].endswith('VisualTreeAsset')];assert len(matches)==1
 cl=matches[0];deps=list(cat.location(cl)['dependencies'])
 for k in donorkeys:
  dl=next(i for i in cat.locations(k) if cat.location(i)['type'][1].endswith('VisualTreeAsset'))
  deps=list(dict.fromkeys(deps+cat.location(dl)['dependencies']))
 assert cat.location(deps[0])['internal'].endswith(W) and cl in cat.locations('GameWorldVisualTreeAssetPreload')
 if deps!=cat.location(cl)['dependencies']:
  raw=b''.join(struct.pack('<I',i) for i in deps);off=cat.append(raw,True);struct.pack_into('<2I',cat.data,cl+12,off,zlib.crc32(raw))
 # Verify live aliases resolve through actual catalog entries and owning bundles.
 active={x.get('data',{}).get('m_TemplateAlias') for x in rr.values()}-{None,''};bundles={W:oo};resolved=0
 for u in doc['m_Usings']:
  if u['alias'] not in active or not u.get('path'):continue
  ml=[cat.location(i) for i in cat.locations(u['path']) if cat.location(i)['type'][1].endswith('VisualTreeAsset')];assert len(ml)==1,u
  owner=cat.location(ml[0]['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
  if owner not in bundles:bundles[owner]={o.path_id:o for o in UnityPy.load(str(root/owner)).objects}
  ob=bundles[owner];mt=next(o.read_typetree() for o in ob.values() if o.type.name=='AssetBundle')
  assert any('m_VisualTree' in ob[v['asset']['m_PathID']].read_typetree() for k,v in mt['m_Container'] if k==u['path']),u
  resolved+=1
 layouts={o.path_id:o for o in UnityPy.load(str(root/L)).objects}
 active_descriptions=[p['m_PathID'] for p in layouts[1332213496068314481].read_typetree()['m_gridElementDescriptions'] if p['m_FileID']==0 and layouts[p['m_PathID']].read_typetree().get('<ID>k__BackingField')=='PlayerOverviewLeftPortrait']
 assert len(active_descriptions)==1,active_descriptions
 desc=layouts[active_descriptions[0]].read_typetree()
 assert desc['<ID>k__BackingField']=='PlayerOverviewLeftPortrait' and desc['m_directTitlePath']['m_path']==TITLEKEY
 assert all(c['AssetRef']['m_AssetGUID']==KEY for c in desc['<Configurations>k__BackingField'])
 assert any(x['m_elementID']=='PlayerOverviewLeftPortrait' for x in layouts[3901662990989568885].read_typetree()['m_placementBindings'])
 changes={PAGE:doc,sid:sheet,HOST:host,ab.path_id:meta}
 for i,v in changes.items():oo[i].save_typetree(v)
 output=env.file.save(packer='lz4');co={o.path_id:o for o in UnityPy.load(output).objects};assert co.keys()==oo.keys()
 for i,h in baseline.items():
  if i not in changes:assert sha(co[i].get_raw_data())==h,('Unrelated object changed',i)
 for i,v in changes.items():assert co[i].read_typetree()==v,('Serialization mismatch',i)
 add_tx(tag,root/W,output,before)
 catout=bytes(cat.data);hp=cp.with_name('catalog.hash')
 if catout!=cb:
  add_tx(tag,cp,catout,cb);add_tx(tag,hp,hashlib.md5(catout).hexdigest().encode('ascii'),hp.read_bytes())
 else:protected[str(cp)]=sha(cb);protected[str(hp)]=sha(hp.read_bytes())
 checks.append(dict(target=tag,page=PAGE,source=SOURCE,region_donor=DONOR,title=TITLE,unique_guid=KEY,selector_description_set_composition_verified=True,layout_outside_region_matches_source=True,region_matches_middle_nonhidden=True,template_aliases_resolved=resolved,other_objects_byte_identical=True,serialization_readback=True,catalog_dependencies_preload_verified=True))
 print('Verified '+tag,flush=True)
# Correct only this entry's saved template reference, retaining the user's selection and positions.
cache=Path.home()/'AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large'
if cache.exists():
 cb=cache.read_bytes();layout=json.loads(cb);fixed=0
 for c in layout.get('m_gridComponents',[]):
  if c['m_elementID']=='PlayerOverviewLeftPortrait':
   for cfg in c['m_gridElementConfigs']:
    if cfg['AssetRef']['m_AssetGUID']!=KEY:cfg['AssetRef']['m_AssetGUID']=KEY;fixed+=1
 if fixed:add_tx('cache',cache,json.dumps(layout,ensure_ascii=False,separators=(',',':')).encode('utf8'),cb)
 else:protected[str(cache)]=sha(cb)
 checks.append(dict(target='saved-layout',binding_verified=True,corrected_references=fixed,selection_and_positions_preserved=True))
manifest=dict(installed=False,installed_verified=False,runtime_verified=False,title=TITLE,page=PAGE,guid=KEY,protected_sha256=protected,checks=checks)
for n,v in [('manifest.json',manifest),('transaction.json',tx),('verification-prepared.json',dict(passed=True,checks=checks,runtime_verified=False))]:(OUT/n).write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8').replace('assert p.resolve().parent in allowed','assert p.resolve().parent in allowed or p.resolve()==Path('+repr(str(cache))+').resolve()')
(OUT/'installer.py').write_text(installer,'utf8')
for mode,n in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/n).write_text("$ErrorActionPreference = 'Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf-8-sig')
(R/'old-left-portrait-nonhidden-prepared.json').write_text(json.dumps(dict(output=str(OUT))),'utf8')
print(OUT,flush=True)
