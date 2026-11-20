from pathlib import Path
import sys,copy,json,hashlib,datetime,importlib.util,re,struct,zlib,ast
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle';B='ui-backgrounds_assets_common.bundle';F='ui-visualfunctions_assets_all.bundle'
M='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
T='ui-tablefactories_assets_all.bundle'
I='ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle';V='ui-tableviews_assets_all.bundle';S='ui-styles_assets_default.bundle';C='ui-styles_assets_common.bundle';D='ui-visualtreeassets_assets_fantasydraftvisualtreeassetpreload.bundle'
NAMES=[W,G,L,M,T,I,V,S,C,D];sha=lambda b:hashlib.sha256(b).hexdigest()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
OUT=R/('main-1-14-rebuild-'+stamp);OUT.mkdir();(OUT/'backup-game').mkdir();(OUT/'backup-skin').mkdir()
gamebefore={n:(GAME/n).read_bytes() for n in NAMES+[B]};skinbefore={n:(SKIN/n).read_bytes() for n in NAMES+[B,'catalog.bin'] if (SKIN/n).exists()}
source_paths={n:SKIN/n for n in NAMES+[B] if (SKIN/n).exists()}
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'))
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
catbefore=(GAME.parent/'catalog.bin').read_bytes();hashpath=GAME.parent/'catalog.hash';hashbefore=hashpath.read_bytes() if hashpath.exists() else None
for n,b in gamebefore.items():(OUT/'backup-game'/n).write_bytes(b)
(OUT/'backup-game/catalog.bin').write_bytes(catbefore)
if hashbefore is not None:(OUT/'backup-game/catalog.hash').write_bytes(hashbefore)
for n,b in skinbefore.items():(OUT/'backup-skin'/n).write_bytes(b)
cachepath=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
cachebefore=cachepath.read_bytes() if cachepath.exists() else None
if cachebefore is not None:(OUT/'backup-custom-layout.json').write_bytes(cachebefore)
newenv={n:UnityPy.load(b) for n,b in gamebefore.items()};oldenv={n:UnityPy.load(b) for n,b in skinbefore.items() if n.endswith('.bundle')}
newenv[B]=UnityPy.load(str(R/'prepare-current-backgrounds-1-14'/B))
newenv[F]=UnityPy.load(str(GAME/F))
no={n:{o.path_id:o for o in e.objects} for n,e in newenv.items()};oo={n:{o.path_id:o for o in e.objects} for n,e in oldenv.items()}
nh={n:{i:sha(o.get_raw_data()) for i,o in obs.items()} for n,obs in no.items() if n in NAMES}
schema_defaults_added=[];schema_fields_removed=[]
def schema_default(node):
 if node.m_Type=="string":return ""
 if node.m_Type=="bool":return False
 if node.m_Children and node.m_Children[0].m_Type=="Array":return []
 if node.m_Children:return {c.m_Name:schema_default(c) for c in node.m_Children}
 return 0
oldwrite=TypeTreeHelper.write_value
def write(v,node,writer,config):
 if isinstance(v,dict) and node.m_Type!="ReferencedObject":
  for child in node.m_Children:
   if child.m_Name not in v and child.m_Type!='ManagedReferencesRegistry':
    v[child.m_Name]=schema_default(child);schema_defaults_added.append((node.m_Type,child.m_Name))
 if node.m_Type=='ReferencedObject' and TypeTreeHelper.get_ref_type_node(v,config.assetsfile) is None:
  for child in node.m_Children:
   if child.m_Type!='ReferencedObjectData':oldwrite(v[child.m_Name],child,writer,config)
  if TypeTreeHelper.metaflag_is_aligned(node.m_MetaFlag):writer.align_stream()
  return
 return oldwrite(v,node,writer,config)
TypeTreeHelper.write_value=write
spec=importlib.util.spec_from_file_location('migration_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
oldcat=cm.Catalog(skinbefore['catalog.bin']);catalog=cm.Catalog(catbefore);newcatkeys=dict(catalog.keys());oldcatkeys=dict(oldcat.keys())
def metadatas(obs):
 return {n:next(o for o in items.values() if o.type.name=='AssetBundle').read_typetree() for n,items in obs.items()}
nm=metadatas(no);om=metadatas(oo)
def index(obs,meta):
 out={}
 for n,m in meta.items():
  for k,v in m['m_Container']:
   if v['asset']['m_FileID']==0:
    obj=obs[n][v['asset']['m_PathID']]
    if obj.type.name=='MonoBehaviour' and obj.serialized_type.script_id.hex()=='55df88d949bb6ddf480913cd0b7df24f':continue
    out[k]=(n,v['asset']['m_PathID'])
 return out
ni=index(no,nm);oi=index(oo,om)
oldafs={a.name.lower():a for e in oldenv.values() for a in e.assets};newafs={a.name.lower():a for e in newenv.values() for a in e.assets}
bundle_by_cab={a.name.lower():n for n,e in newenv.items() for a in e.assets}
objcache={}
def tree(which,n,pid):
 key=(which,n,pid)
 if key not in objcache:objcache[key]=(oo if which=='old' else no)[n][pid].read_typetree()
 return objcache[key]
def canon(af,ptr):
 if not ptr['m_PathID']:return None
 fid=ptr['m_FileID']
 return ((af.name if fid==0 else af.externals[fid-1].name).lower(),ptr['m_PathID'])
def external_index(af,cab):
 if cab==af.name.lower():return 0
 found=next((i+1 for i,e in enumerate(af.externals) if e.name.lower()==cab),None)
 if found is not None:return found
 assert cab in newafs or any(e.name.lower()==cab for src in oldafs.values() for e in src.externals),cab
 source=next((e for src in list(newafs.values())+list(oldafs.values()) for e in src.externals if e.name.lower()==cab),None)
 if source is None:
  source=copy.copy(af.externals[0]);source.guid=bytes(16);source.type=0;source.path=f'archive:/{newafs[cab].name}/{newafs[cab].name}'
 af.externals.append(copy.copy(source));return len(af.externals)
def pointer(af,target):
 if target is None:return {'m_FileID':0,'m_PathID':0}
 return {'m_FileID':external_index(af,target[0]),'m_PathID':target[1]}
semantic={};stages={};source_dest={};source_guid={}
def oldkey(n,pid):return (oo[n][pid].assets_file.name.lower(),pid)
def newkey(n,pid):return (no[n][pid].assets_file.name.lower(),pid)
# GUIDs, not the old path IDs, identify rebuilt native objects. Inline style IDs changed too.
for guid,src in oi.items():
 if guid not in ni:continue
 dst=ni[guid];semantic[oldkey(*src)]=newkey(*dst)
 if oo[src[0]][src[1]].type.name=='MonoBehaviour' and no[dst[0]][dst[1]].type.name=='MonoBehaviour':
  a=tree('old',*src);b=tree('new',*dst)
  if 'inlineSheet' in a and 'inlineSheet' in b:semantic[canon(oo[src[0]][src[1]].assets_file,a['inlineSheet'])]=canon(no[dst[0]][dst[1]].assets_file,b['inlineSheet'])
for guid,src in oi.items():source_guid.setdefault(src,guid)
bgname={o.peek_name():newkey(B,pid) for pid,o in no[B].items() if o.type.name=='Texture2D'}
for n,items in oo.items():
 for pid,o in items.items():
  if o.type.name=='Texture2D' and o.peek_name() in bgname:semantic[oldkey(n,pid)]=bgname[o.peek_name()]
# Old World copies of Global templates are rebound to the new native template identity.
for pid,o in oo[W].items():
 if oldkey(W,pid) not in semantic and pid in oo[G] and o.type==oo[G][pid].type:
  gkey=oldkey(G,pid)
  if gkey in semantic and o.peek_name()==oo[G][pid].peek_name():semantic[oldkey(W,pid)]=semantic[gkey]
fresh=-950000000000000
def allocate(n,preferred):
 global fresh
 if preferred not in no[n] and (n,preferred) not in stages:return preferred
 while fresh in no[n] or (n,fresh) in stages:fresh-=1
 result=fresh;fresh-=1;return result
def stage(n,pid,replace_native=False):
 src=(n,pid)
 if src in source_dest:return source_dest[src]
 obj=oo[n][pid];data=tree('old',n,pid)
 if obj.type.name=='Texture2D':
  assert obj.peek_name() in bgname,('custom image missing from backgrounds',obj.peek_name());return (B,bgname[obj.peek_name()][1])
 existing=semantic.get(oldkey(n,pid)) if replace_native else None
 if existing is not None:
  dst=(bundle_by_cab[existing[0]],existing[1])
 else:dst=(n,allocate(n,pid))
 source_dest[src]=dst;semantic[oldkey(n,pid)]=(newenv[dst[0]].assets[0].name.lower(),dst[1]);stages[dst]=src
 if 'inlineSheet' in data and data['inlineSheet']['m_FileID']==0 and data['inlineSheet']['m_PathID']:
  stage(n,data['inlineSheet']['m_PathID'],replace_native)
 return dst
def iscustom(pid):return -999000000000000<pid<=-910000000000000
for n in NAMES:
 for pid,o in oo[n].items():
  if iscustom(pid) and o.type.name=='MonoBehaviour':stage(n,pid)
# Gather actual historical edited object identities; use final sources, never historical values.
seed_ids={n:set() for n in NAMES}
def same_edit(a,b):
 if isinstance(a,dict) and isinstance(b,dict):return all(same_edit(v,b[k]) for k,v in a.items() if k in b and k not in ['m_Script','m_ContentHash'])
 if isinstance(a,list) and isinstance(b,list):return len(a)==len(b) and all(same_edit(x,y) for x,y in zip(a,b))
 return a==b
for bn in NAMES:
 baseline=R/'pinned-1-14-update-20261029-122441/backup-game'/bn
 if not baseline.exists():continue
 base={o.path_id:o for o in UnityPy.load(str(baseline)).objects}
 for pid,obj in oo[bn].items():
  if obj.type.name!='MonoBehaviour':continue
  if pid not in base or not same_edit(obj.read_typetree(),base[pid].read_typetree()):seed_ids[bn].add(pid)
required_names={'IGEEditDetailsBlock','MainMenu','AlwaysAppliedStyleSheet','PrimaryNavigationBar','MarketingBannerTile_8x2','GameWorld','GameWorldBackground','Bookmarks','PrimaryNavigationBar','SecondaryNavigationBar','HistoryButtons','TopBar'}
for bn,items in oo.items():
 if bn not in seed_ids:continue
 for pid,obj in items.items():
  if obj.peek_name() in required_names:seed_ids[bn].add(pid)
# Shared stylesheet GUIDs may appear in more than one bundle. Keep their local identity.
for bn in [S,C]:
 for pid,obj in oo[bn].items():
  if pid in no[bn] and obj.peek_name()==no[bn][pid].peek_name():semantic[oldkey(bn,pid)]=newkey(bn,pid)
for mp in [R/'sidebar-approved-rebased-20261101-121312/manifest.json',R/'sidebar-below-navigation-20261102-084638/manifest.json',R/'sidebar-borderless-20261102-090802/manifest.json']:
 if not mp.exists():continue
 rec=json.loads(mp.read_text('utf8'))
 for audit in rec.get('bundle_audits',[]):
  bn=audit.get('bundle')
  if bn in seed_ids:
   for item in audit.get('changed_objects',[]):
    if isinstance(item,dict) and 'path_id' in item:seed_ids[bn].add(int(item['path_id']))
# Early customized player templates and selector layouts predate manifest conventions.
native_world=[-6400646727147995419,-3862538512510687317,168226888031714516,5938222404796150770,7199728689344018492,5775949770471550939]
seed_ids[W].update(native_world);seed_ids[G].add(-4194025542157271532)
seed_ids[L].update([1332213496068314481,3901662990989568885])
for bn,ids in seed_ids.items():
 for pid in ids:
  if pid not in oo[bn] or oo[bn][pid].type.name!='MonoBehaviour':continue
  data=tree('old',bn,pid)
  if oldkey(bn,pid) in semantic:stage(bn,pid,True)
  elif iscustom(pid):stage(bn,pid)
# A few early custom picture templates were imported directly rather than registered in a container.
direct_alias_guids={}
for n,items in oo.items():
 if n not in NAMES:continue
 for pid,obj in items.items():
  if obj.type.name!='MonoBehaviour' or not iscustom(pid):continue
  for u in tree('old',n,pid).get('m_Usings',[]):
   p=u.get('asset',{});guid=u.get('path','')
   if guid and guid not in oi and guid not in newcatkeys and p.get('m_PathID'):
    target=canon(obj.assets_file,p);source_bundle=next((bn for bn,e in oldenv.items() if any(a.name.lower()==target[0] for a in e.assets)),None)
    if source_bundle in NAMES and target[1] in oo[source_bundle]:
     src=(source_bundle,target[1]);oi[guid]=src;direct_alias_guids.setdefault(src,[]).append(guid)

def guid_refs(v):
 if isinstance(v,dict):
  if 'm_AssetGUID' in v and v['m_AssetGUID']:yield v['m_AssetGUID']
  if 'm_Usings' in v:
   for u in v['m_Usings']:
    if u['path']:yield u['path']
  if 'm_target' in v and v['m_target'].get('m_guid'):yield v['m_target']['m_guid']
  for x in v.values():yield from guid_refs(x)
 elif isinstance(v,list):
  for x in v:yield from guid_refs(x)
# Retain compatibility resources only when a restored component actually needs a removed native GUID.
missing_guids=[]
while True:
 added=0
 for dst,src in list(stages.items()):
  for guid in set(guid_refs(tree('old',*src))):
   if guid in newcatkeys or guid in ni:continue
   if guid in oi:
    ref=oi[guid]
    if ref[0] in NAMES and ref not in source_dest:stage(*ref);added+=1
   elif guid not in missing_guids:missing_guids.append(guid)
 if not added:break
assert not missing_guids,('unresolved GUID dependencies',missing_guids)

# Build native MonoScript mappings using the current build's serialized type IDs.
type_templates={}
for n,items in no.items():
 for obj in items.values():
  if obj.serialized_type is not None:type_templates.setdefault((obj.class_id,obj.serialized_type.script_id),obj)
script_map={};reference_defaults={}
for n,items in oo.items():
 for obj in items.values():
  if obj.type.name!='MonoBehaviour':continue
  key=(obj.class_id,obj.serialized_type.script_id);template=type_templates.get(key)
  if template is None:continue
  od=obj.read_typetree();nd=template.read_typetree()
  if od.get('m_Script',{}).get('m_PathID') and nd.get('m_Script',{}).get('m_PathID'):script_map[canon(obj.assets_file,od['m_Script'])]=canon(template.assets_file,nd['m_Script'])
for n,items in no.items():
 for obj in items.values():
  if obj.type.name!="MonoBehaviour":continue
  data=obj.read_typetree()
  for ref in data.get("references",{}).get("RefIds",[]):
   typ=ref.get("type",{});key=(typ.get("class"),typ.get("ns"),typ.get("asm"))
   if ref.get("data"):reference_defaults.setdefault(key,(copy.deepcopy(ref["data"]),obj.assets_file))

def fill_new_fields(value,defaults,default_af,dstaf):
 if isinstance(value,dict) and isinstance(defaults,dict):
  for k,d in defaults.items():
   if k not in value:
    value[k]=copy_current(d,default_af,dstaf);schema_defaults_added.append(("native-default",k))
   else:fill_new_fields(value[k],d,default_af,dstaf)

def copy_current(value,srcaf,dstaf):
 if isinstance(value,dict):
  if set(value)=={"m_FileID","m_PathID"}:return pointer(dstaf,canon(srcaf,value))
  return {k:copy_current(v,srcaf,dstaf) for k,v in value.items()}
 if isinstance(value,list):return [copy_current(v,srcaf,dstaf) for v in value]
 return copy.deepcopy(value)

def resolve(srcaf,ptr):
 key=canon(srcaf,ptr)
 if key is None:return None
 if key in semantic:return semantic[key]
 if key in script_map:return script_map[key]
 if key[0] not in oldafs:return key  # Unchanged engine/icon resources from other bundles.
 if key[0] in newafs and key[1] in newafs[key[0]].objects:
  oldobj=oldafs[key[0]].objects.get(key[1]);newobj=newafs[key[0]].objects[key[1]]
  if oldobj and oldobj.type==newobj.type and oldobj.peek_name()==newobj.peek_name():return key
 if key[0] in newafs and key[1] in oldafs[key[0]].objects:
  oldobj=oldafs[key[0]].objects[key[1]];name=oldobj.peek_name()
  matches=[o for o in newafs[key[0]].objects.values() if name and o.type==oldobj.type and o.peek_name()==name]
  if len(matches)==1:
   result=(key[0],matches[0].path_id);semantic[key]=result;return result
 raise AssertionError(('unresolved rebuilt object',key,oldafs[key[0]].objects[key[1]].peek_name() if key[1] in oldafs[key[0]].objects else 'missing'))
pointer_count=[0];background_refs=[0]
def remap_data(v,srcaf,dstaf):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'}:
   target=resolve(srcaf,v);result=pointer(dstaf,target);pointer_count[0]+=int(bool(v['m_PathID']));background_refs[0]+=int(target is not None and target[0]==newenv[B].assets[0].name.lower());return result
  out={}
  for k,x in v.items():
   if k=='m_Script':continue
   if k=='m_Usings':
    out[k]=[]
    for u in x:
     nu=copy.deepcopy(u);p=u.get('asset',{})
     # Preserve intentional custom template overrides; native imports resolve through the new GUID.
     if p.get('m_PathID') and not iscustom(p['m_PathID']):nu['asset']={'m_FileID':0,'m_PathID':0}
     elif p:nu['asset']=remap_data(p,srcaf,dstaf)
     out[k].append(nu)
   else:out[k]=remap_data(x,srcaf,dstaf)
  return out
 if isinstance(v,list):return [remap_data(x,srcaf,dstaf) for x in v]
 return copy.deepcopy(v)
def type_for(dstaf,template):
 key=(template.class_id,template.serialized_type.script_id)
 found=next(((i,t) for i,t in enumerate(dstaf.types) if (t.class_id,t.script_id)==key),None)
 if found:return found
 st=copy.copy(template.serialized_type)
 if st.script_type_index>=0:
  script=copy.copy(template.assets_file.script_types[st.script_type_index]);p={'m_FileID':script.local_serialized_file_index,'m_PathID':script.local_identifier_in_file}
  target=canon(template.assets_file,p);converted=pointer(dstaf,target)
  script.local_serialized_file_index=converted['m_FileID'];script.local_identifier_in_file=converted['m_PathID'];st.script_type_index=len(dstaf.script_types);dstaf.script_types.append(script)
 index=len(dstaf.types);dstaf.types.append(st);return index,st
def merge_ref_types(dstaf):
 keys={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in dstaf.ref_types}
 for af in list(newafs.values())+list(oldafs.values()):
  for typ in af.ref_types:
   key=(typ.m_ClassName,typ.m_NameSpace,typ.m_AssemblyName)
   if key not in keys:dstaf.ref_types.append(copy.copy(typ));keys.add(key)
for n in NAMES:merge_ref_types(newenv[n].assets[0])
expected={n:{} for n in NAMES};stage_audit=[]
for dst,src in list(stages.items()):
 n,pid=dst;sn,spid=src;source=oo[sn][spid];data=tree('old',sn,spid);af=newenv[n].assets[0]
 template=type_templates[(source.class_id,source.serialized_type.script_id)];tid,st=type_for(af,template)
 if sn==L and spid==1332213496068314481:
  converted=copy_current(tree('new',n,pid),no[n][pid].assets_file,af)
  for p in data['m_gridElementDescriptions']:
   if iscustom(p['m_PathID']):converted['m_gridElementDescriptions'].append(remap_data(p,source.assets_file,af))
 else:converted=remap_data(data,source.assets_file,af)
 if data.get('m_Name')=='ContractNegotiationToolTemplate' and pid in no[n]:
  native_refs={r['rid']:r for r in tree('new',n,pid)['references']['RefIds']}
  for row in converted['references']['RefIds']:
   nr=native_refs.get(row['rid'])
   if nr and nr['type']==row['type']:
    for field in ['m_Id','uxmlAssetId']:
     if field in row.get('data',{}) and field in nr.get('data',{}):row['data'][field]=nr['data'][field]

 nd=template.read_typetree()
 if 'm_Script' in nd:converted['m_Script']=pointer(af,canon(template.assets_file,nd['m_Script']))
 # Supply only newly added top-level serialized fields from the current build.
 for k,v in nd.items():
  if k not in converted:converted[k]=copy.deepcopy(v)
 for ref in converted.get('references',{}).get('RefIds',[]):
  typ=ref.get('type',{});key=(typ.get('class'),typ.get('ns'),typ.get('asm'))
  if key in reference_defaults and 'data' in ref:
   defaults,default_af=reference_defaults[key];fill_new_fields(ref['data'],defaults,default_af,af)
   for obsolete in set(ref['data'])-set(defaults):
    schema_fields_removed.append((str(key),obsolete));ref['data'].pop(obsolete)
 obj=copy.copy(template);obj.path_id=pid;obj.assets_file=af;obj.type_id=tid;obj.serialized_type=st;obj.data=None;obj._read_until=None
 af.objects[pid]=obj;no[n][pid]=obj
 obj.save_typetree(converted);reread=converted;expected[n][pid]=copy.deepcopy(reread)
 assert reread.get('m_Name','')==data.get('m_Name',''),(n,pid,data.get('m_Name'),reread.get('m_Name'))
 stage_audit.append({'bundle':n,'id':pid,'source_bundle':sn,'source_id':spid,'name':data.get('m_Name'),'replaces_native':pid in nh[n]})

for pid in native_world:assert source_dest[(W,pid)][1] in nh[source_dest[(W,pid)][0]],('native override not mapped',pid)
assert source_dest[(G,-4194025542157271532)][1] in nh[G]

# Merge just the extra overview-description bindings into the new PlayerReport page.
oldpage=(W,7857044477279960178);pagekey=resolve(oo[W][oldpage[1]].assets_file,{'m_FileID':0,'m_PathID':oldpage[1]});newpage=(bundle_by_cab[pagekey[0]],pagekey[1])
np=copy.deepcopy(expected[newpage[0]].get(newpage[1],tree('new',*newpage)));op=tree('old',*oldpage)
oldgrid=next(r['data']['Bindings'] for r in op['references']['RefIds'] if 'Bindings' in r.get('data',{}) and r['data']['Bindings'].get('m_gridCompositionSet',{}).get('m_PathID')==1615455816372668659)
newgrid=next(r['data']['Bindings'] for r in np['references']['RefIds'] if 'Bindings' in r.get('data',{}) and 'm_gridElementBindingData' in r['data']['Bindings'])
def descriptions(v):
 if isinstance(v,dict):
  if 'DescriptionName' in v:yield v['DescriptionName']
  for x in v.values():yield from descriptions(x)
 elif isinstance(v,list):
  for x in v:yield from descriptions(x)
binding_adds=0
for k,items in oldgrid.items():
 if not isinstance(items,list):continue
 if k=='m_nameBindings':
  newgrid.setdefault(k,[])
  for item in items:
   if item.get('name')=='person' and not any(v.get('name')=='person' for v in newgrid[k]):newgrid[k].append(copy.deepcopy(item))
  continue
 for item in items:
  if set(descriptions(item))&{'PlayerOverviewFull','PlayerOverviewSimple'}:
   newgrid.setdefault(k,[])
   if item not in newgrid[k]:newgrid[k].append(copy.deepcopy(item));binding_adds+=1
assert binding_adds>=0
no[newpage[0]][newpage[1]].save_typetree(np);expected[newpage[0]][newpage[1]]=np

# Rebuild only the migrated container entries and preload spans in each new bundle.
registered={}
for n in NAMES:
 af=newenv[n].assets[0];meta=copy.deepcopy(nm[n]);containers=list(meta['m_Container'])
 for dst,src in stages.items():
  if dst[0]!=n:continue
  pid=dst[1];d=expected[n][pid]
  if 'm_Rules' in d:continue
  keys=[k for k,v in om[src[0]]['m_Container'] if v['asset']=={'m_FileID':0,'m_PathID':src[1]}]+direct_alias_guids.get(src,[])
  for guid in keys:
   if re.fullmatch('[a-fA-F0-9]{32}',guid):registered[guid]=(n,pid)
   span=[]
   def pointers(v):
    if isinstance(v,dict):
     if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
      if v not in span:span.append(copy.deepcopy(v))
     else:
      for x in v.values():pointers(x)
    elif isinstance(v,list):
     for x in v:pointers(x)
   pointers(d)
   root={'m_FileID':0,'m_PathID':pid}
   if root not in span:span.append(root)
   containers=[(k,v) for k,v in containers if not (k==guid and v['asset']==root)]
   containers.append((guid,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':root}));meta['m_PreloadTable'].extend(span)
 for ext in af.externals:
  cab=ext.name.lower()
  if cab in bundle_by_cab and cab!=af.name.lower() and cab not in meta['m_Dependencies']:meta['m_Dependencies'].append(cab)
 meta['m_Container']=sorted(containers,key=lambda x:x[0]);meta['m_Dependencies']=sorted(set(meta['m_Dependencies']))
 ab=next(o for o in no[n].values() if o.type.name=='AssetBundle');ab.save_typetree(meta);expected[n][ab.path_id]=meta;nm[n]=meta

# Re-register custom GUIDs against the current catalog's providers and bundle dependency locations.
all_locations={}
for key,locset in catalog.keys():
 for (loc,) in catalog.array(locset,'I'):all_locations[loc]=catalog.location(loc)
bundleloc={}
for loc,v in all_locations.items():
 if v['type'][1].endswith('IAssetBundleResource') and v['internal']:
  for n in NAMES+[B,F]:
   if v['internal'].replace('\\','/').endswith('/'+n):bundleloc[n]=loc
assert set(NAMES+[B,F])<=set(bundleloc)
def add_dependencies(loc,extras):
 raw=list(catalog.unpack(loc,'7I'));existing=[v[0] for v in catalog.array(raw[3],'I')]
 combined=existing+[x for x in extras if x not in existing]
 if combined!=existing:
  raw[3]=catalog.append(b''.join(struct.pack('<I',x) for x in combined),True)
  raw[4]=zlib.crc32(b''.join(struct.pack('<I',x) for x in combined));struct.pack_into('<7I',catalog.data,loc,*raw)
# Addressables stores flattened bundle dependencies on asset locations.
# Bundle-resource locations intentionally remain dependency-free to avoid CAB cycles.
required_deps={}
for n in NAMES:
 required_deps[n]=[bundleloc[n]]+[bundleloc[bundle_by_cab[cab]] for cab in nm[n]['m_Dependencies'] if cab in bundle_by_cab and bundle_by_cab[cab] in bundleloc and bundle_by_cab[cab]!=n]
for loc,v in all_locations.items():
 if v['type'][1].endswith('IAssetBundleResource'):continue
 extras=[]
 for n in NAMES:
  if bundleloc[n] in v['dependencies']:extras.extend(required_deps[n])
 if extras:add_dependencies(loc,extras)
catalog=cm.Catalog(bytes(catalog.data))
native_keys=dict(catalog.keys());new_custom=[]
for guid,(n,pid) in registered.items():
 if guid in native_keys:continue
 oldloc=oldcat.location(oldcat.array(oldcatkeys[guid],'I')[0][0]) if guid in oldcatkeys else None
 typename=oldloc['type'][1] if oldloc else ('UnityEngine.UIElements.VisualTreeAsset' if 'm_VisualTree' in expected[n][pid] else 'SI.VisualScripting.VisualFunction')
 template_loc=next(loc for loc,v in all_locations.items() if v['type'][1]==typename)
 # A synthetic dependency source points to this bundle; its recursive deps were updated above.
 base=next((loc for loc,v in all_locations.items() if v['type'][1]==typename and v['dependencies'] and v['dependencies'][0]==bundleloc[n]),template_loc)
 raw=list(catalog.unpack(base,'7I'));deps=[v[0] for v in catalog.array(raw[3],'I')]
 deps=list(dict.fromkeys([bundleloc[n]]+deps+required_deps[n]));depbytes=b''.join(struct.pack('<I',x) for x in deps)
 raw[3]=catalog.append(depbytes,True);raw[4]=zlib.crc32(depbytes);dep_loc=catalog.append(struct.pack('<7I',*raw))
 catalog=cm.Catalog(catalog.add_key_location(guid,template_loc,dep_loc));new_custom.append(guid)
# Add restored VTAs to the corresponding native preload labels, retaining their existing members.
label_changes={}
for n,label in [(W,'GameWorldVisualTreeAssetPreload'),(G,'GlobalVisualTreeAssetPreload'),(M,'MatchVisualTreeAssetPreload'),(I,'IntroVisualTreeAssetPreload'),(D,'FantasyDraftVisualTreeAssetPreload')]:
 keyidx=next((i for i,(k,l) in enumerate(catalog.key_records) if catalog.object(k)==label),None)
 
 if keyidx is None:continue
 keyobj,locset=catalog.key_records[keyidx];locs=[v[0] for v in catalog.array(locset,'I')];extra=[]
 for guid,(bn,pid) in registered.items():
  if bn==n and 'm_VisualTree' in expected[bn][pid]:
   target=catalog.locations(guid)[0]
   if target not in locs:extra.append(target)
 if extra:
  locs+=extra;newset=catalog.append(b''.join(struct.pack('<I',p) for p in locs),True);records=list(catalog.key_records);records[keyidx]=(keyobj,newset);table=catalog.append(b''.join(struct.pack('<2I',*r) for r in records),True);struct.pack_into('<I',catalog.data,8,table);catalog=cm.Catalog(bytes(catalog.data))
 label_changes[label]=len(extra)
catout=bytes(catalog.data);outputs={n:e.file.save(packer='lz4') for n,e in newenv.items() if n in NAMES}
for n,b in outputs.items():
 check={o.path_id:o for o in UnityPy.load(b).objects}
 assert set(check)==set(no[n])
 for pid,h in nh[n].items():
  if pid not in expected[n]:assert sha(check[pid].get_raw_data())==h,('updated native asset changed unexpectedly',n,pid)
 for pid,d in expected[n].items():
  actual=check[pid].read_typetree()
  if actual!=d:
   differences=[]
   def diff(a,b,path=''):
    if len(differences)>=12:return
    if isinstance(a,dict) and isinstance(b,dict):
     for k in set(a)|set(b):
      if k not in a or k not in b:differences.append((path+'.'+k,'missing-key',k in a,k in b))
      else:diff(a[k],b[k],path+'.'+k)
    elif isinstance(a,list) and isinstance(b,list):
     if len(a)!=len(b):differences.append((path,'length',len(a),len(b)))
     for i,(x,y) in enumerate(zip(a,b)):diff(x,y,path+'['+str(i)+']')
    elif a!=b:differences.append((path,a,b))
   diff(actual,d);raise AssertionError(('roundtrip mismatch',n,pid,d.get('m_Name'),differences))
for n,b in outputs.items():(OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout);hashout=hashlib.md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'schema_fields_added':sorted(set(schema_defaults_added)),'schema_fields_removed':sorted(set(schema_fields_removed)),'output':str(OUT),'stage_assets':stage_audit,'native_page_binding_additions':binding_adds,'registered_custom_guids':new_custom,'preload_labels':label_changes,'all_images_reference_current_backgrounds':True,'background_pointer_references':background_refs[0],'remapped_object_references':pointer_count[0],'background_bundle_unchanged_sha256':sha(gamebefore[B]),'all_other_updated_native_assets_preserved':True,'source_skin_sha256':{n:sha((SKIN/n).read_bytes()) for n in skinbefore if (SKIN/n).exists()},'source_paths':{n:str(p) for n,p in source_paths.items()},'new_game_before_sha256':{n:sha(b) for n,b in gamebefore.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'catalog_before_sha256':sha(catbefore),'catalog_after_sha256':sha(catout),'changed_native_counts':{n:sum(i in nh[n] for i in expected[n]) for n in NAMES},'added_counts':{n:sum(i not in nh[n] for i in expected[n]) for n in NAMES}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'added_counts':report['added_counts'],'changed_native_counts':report['changed_native_counts'],'registered_guids':len(new_custom),'background_references':background_refs[0]},ensure_ascii=True))




