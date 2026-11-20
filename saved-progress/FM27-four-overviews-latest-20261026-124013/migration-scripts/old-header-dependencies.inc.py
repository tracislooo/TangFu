import importlib.util, struct
spec=importlib.util.spec_from_file_location('catalog_migration',R/'catalog-binary-v35.py')
catmod=importlib.util.module_from_spec(spec);spec.loader.exec_module(catmod)
catalog_path=GAME.parent/'catalog.bin';catalog_before=catalog_path.read_bytes()
(OUT/'backup-game/catalog.bin').write_bytes(catalog_before)
catalog=catmod.Catalog(catalog_before)
catalog_keys={k for k,l in catalog.keys() if isinstance(k,str)}
old_file_names={next(iter(oo.values())).assets_file.name:n for n,oo in oldobs.items()}
dst_files={n:next(iter(oo.values())).assets_file for n,oo in obs.items()}
old_guid={}
for n,e in oldenv.items():
 for k,ptr in e.container.items():
  obj=oldobs[n].get(ptr.path_id)
  if obj is not None:
   old_guid.setdefault(k,[]).append((n,obj))
current_guid={}
for n,e in envs.items():
 for k,ptr in e.container.items():
  if ptr.path_id in obs[n]:current_guid.setdefault(k,[]).append(obs[n][ptr.path_id])
imported_ids={G:set(),W:set()};imported_docs={G:{},W:{}};clone_map={};next_pid=-920000000001000
functions_to_register={}

def external_id(srcaf,index,dstaf):
 ext=srcaf.externals[index-1]
 for j,target in enumerate(dstaf.externals):
  if target.path==ext.path:return j+1
 dstaf.externals.append(copy.copy(ext));return len(dstaf.externals)

def import_type(src,dstaf):
 st=src.serialized_type
 for j,t in enumerate(dstaf.types):
  if t.class_id==st.class_id and t.script_id==st.script_id and t.old_type_hash==st.old_type_hash:return j,t
 st=copy.copy(st)
 if st.script_type_index>=0:
  script=copy.copy(src.assets_file.script_types[st.script_type_index])
  if script.local_serialized_file_index:
   script.local_serialized_file_index=external_id(src.assets_file,script.local_serialized_file_index,dstaf)
  st.script_type_index=len(dstaf.script_types);dstaf.script_types.append(script)
 dstaf.types.append(st);return len(dstaf.types)-1,st

def merge_ref_types(srcaf,dstaf):
 known={(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName) for t in dstaf.ref_types}
 for t in srcaf.ref_types:
  k=(t.m_ClassName,t.m_NameSpace,t.m_AssemblyName)
  if k not in known:dstaf.ref_types.append(copy.copy(t));known.add(k)

def clone_object(srcn,pid,dstn):
 global next_pid
 key=(srcn,pid,dstn)
 if key in clone_map:return clone_map[key]
 src=oldobs[srcn][pid];dstaf=dst_files[dstn]
 use=pid
 if use in dstaf.objects:
  if dstaf.objects[use].get_raw_data()==src.get_raw_data():clone_map[key]=use;return use
  use=next_pid;next_pid-=1
 clone_map[key]=use
 d=copy.deepcopy(src.read_typetree())
 prepare(d,srcn,dstn)
 merge_ref_types(src.assets_file,dstaf)
 obj=copy.copy(src);obj.assets_file=dstaf;obj.path_id=use;obj.type_id,obj.serialized_type=import_type(src,dstaf)
 dstaf.objects[use]=obj;obs[dstn][use]=obj
 if src.type.name=='Texture2D':assert d['m_StreamData']['size']==0,'Unexpected streamed texture'
 obj.save_typetree(d);imported_ids[dstn].add(use);imported_docs[dstn][use]=d
 return use

def prepare(v,srcn,dstn):
 srcaf=next(iter(oldobs[srcn].values())).assets_file;dstaf=dst_files[dstn]
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
   pid=v['m_PathID'];index=v['m_FileID'];sn=srcn
   if index:
    ext=srcaf.externals[index-1].path
    sn=next((n for file,n in old_file_names.items() if file in ext),None)
   if sn is not None and pid in oldobs[sn]:
    v['m_PathID']=clone_object(sn,pid,dstn);v['m_FileID']=0
   elif index:v['m_FileID']=external_id(srcaf,index,dstaf)
   else:raise ValueError(('Unresolved source pointer',srcn,pid))
   return
  # Use a private direct template reference when the supplied template differs.
  if 'alias' in v and 'path' in v and 'asset' in v and not v['asset']['m_PathID']:
   key=v['path']
   if v['alias']!='report-player-banner-max':
    candidates=[(n,o) for n,o in old_guid.get(key,[]) if o.type.name=='MonoBehaviour' and 'm_VisualTree' in o.read_typetree()]
    if candidates:
     n,src=candidates[0]
     stock=next((o for o in current_guid.get(key,[]) if o.type.name=='MonoBehaviour' and o.peek_name()==src.peek_name()),None)
     if stock is None or stock.get_raw_data()!=src.get_raw_data():
      v['asset']={'m_FileID':0,'m_PathID':clone_object(n,src.path_id,dstn)}
   return
  guid=v.get('m_guid')
  if guid and guid not in catalog_keys:
   candidates=[(n,o) for n,o in old_guid.get(guid,[]) if o.type.name=='MonoBehaviour']
   if candidates:
    n,src=candidates[0]
    if src.peek_name() in ['ReportFiveAttributeSum','ReportMovementSumAsText']:
     functions_to_register[guid]=clone_object(n,src.path_id,G)
    else:raise ValueError(('Missing GUID dependency',guid,src.peek_name()))
  for a in v.values():prepare(a,srcn,dstn)
 elif isinstance(v,list):
  for a in v:prepare(a,srcn,dstn)

# Remove only the old duplicate action subtree, retaining all other legacy content.
br=refs(banner)
action=next(r for r in br.values() if br.get(r.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')=='FrameActions')
remove=set()
def remove_branch(i):
 remove.add(i);a=br[i]['data']
 if a.get('m_SerializedData',{}).get('rid',-2)!=-2:remove.add(a['m_SerializedData']['rid'])
 for c in a.get('m_Children',[]):remove_branch(c['rid'])
remove_branch(action['rid'])
br[action['data']['m_Parent']['rid']]['data']['m_Children'].remove({'rid':action['rid']})
banner['references']['RefIds']=[r for r in banner['references']['RefIds'] if r['rid'] not in remove]
old_max_rid=next(r['rid'] for r in refs(header).values() if r.get('data',{}).get('m_TemplateAlias')=='report-player-banner-max')
for d,ss,n in [(header,hs,W),(banner,bs,G)]:
 # The root script and inlineSheet are not imported; only clone content dependencies.
 prepare(d['references'],n,W);prepare(d['m_Usings'],n,W);prepare(ss['assets'],n,W)
 merge_ref_types(oldobs[n][5775949770471550939 if n==W else -4194025542157271532].assets_file,dst_files[W])

def register_functions():
 if not functions_to_register:return catalog_before
 bundle=next(o for o in obs[G].values() if o.type.name=='AssetBundle');meta=bundle.read_typetree()
 for guid,pid in functions_to_register.items():
  start=len(meta['m_PreloadTable']);tree=obs[G][pid].read_typetree()
  meta['m_PreloadTable'].extend([copy.deepcopy(tree['m_Script']),{'m_FileID':0,'m_PathID':pid}])
  meta['m_Container'].append((guid,{'preloadIndex':start,'preloadSize':2,'asset':{'m_FileID':0,'m_PathID':pid}}))
  native=next(loc for loc in catalog.locations('f6f314e9db56227459137669d87c44e9'))
  dep=catalog.locations('528775c3a6df3ee44a81b3d826326f09')[0]
  catalog.add_key_location(guid,native,dep)
 meta['m_Container'].sort(key=lambda kv:kv[0]);changed[G][bundle.path_id]=meta
 return bytes(catalog.data)
