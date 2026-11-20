import copy,hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');G=AA/'StandaloneWindows64';S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
BN='ui-backgrounds_assets_common.bundle';WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
PID=-910000000000146;NAME='TF patch';O=R/'删除TF-patch原图-V65-20261028';assert not O.exists();sha=lambda b:hashlib.sha256(b).hexdigest()
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'));banned={int(t['path_id']) for t in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
before={G/BN:(G/BN).read_bytes(),S/BN:(S/BN).read_bytes()};assert before[G/BN]==before[S/BN]
protected={p:sha(p.read_bytes()) for folder in [G,S] for p in folder.glob('*.bundle') if p.name!=BN}
protected.update({p:sha(p.read_bytes()) for folder in [AA,S] for p in [folder/'catalog.bin',folder/'catalog.hash'] if p.exists()})
e=UnityPy.load(before[G/BN]);a=e.assets[0];obs=a.objects;hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};assert obs[PID].peek_name()==NAME and PID not in banned
assert not (banned&set(obs));aux={k:sha(v.bytes) for k,v in e.file.files.items() if k!=a.name}
bundle=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=bundle.read_typetree();old=copy.deepcopy(meta)
is_deleted=lambda p:isinstance(p,dict) and p.get('m_FileID')==0 and p.get('m_PathID')==PID
pre=old['m_PreloadTable'];keep=[not is_deleted(p) for p in pre];prefix=[0]
for k in keep:prefix.append(prefix[-1]+int(k))
meta['m_Container']=[(key,entry) for key,entry in meta['m_Container'] if not is_deleted(entry['asset'])]
def remap(v):
 if isinstance(v,dict):
  if 'preloadIndex' in v and 'preloadSize' in v:
   start,size=v['preloadIndex'],v['preloadSize'];assert 0<=start<=start+size<=len(pre);v['preloadIndex']=prefix[start];v['preloadSize']=prefix[start+size]-prefix[start]
  for x in v.values():remap(x)
 elif isinstance(v,(list,tuple)):
  for x in v:remap(x)
remap(meta);meta['m_PreloadTable']=[p for p,k in zip(pre,keep) if k]
assert len(old['m_Container'])-len(meta['m_Container'])==1 and len(pre)-len(meta['m_PreloadTable'])==1
bundle.save_typetree(meta);del obs[PID]
# Removing the named original must not silently alter its independently used derivative.
assert any(o.type.name=='Texture2D' and o.peek_name()=='TF patch aligned' for o in obs.values())
needle=struct.pack('<q',PID);external_refs=[];loaded={}
for folder in [G,S]:
 for n in [WN,GN]:
  en=UnityPy.load(str(folder/n));wa=en.assets[0];loaded[(folder,n)]=wa
  bgids={i+1 for i,x in enumerate(wa.externals) if x.path==f'archive:/{a.name}/{a.name}'}
  for obj in wa.objects.values():
   if needle not in obj.get_raw_data():continue
   t=obj.read_typetree()
   def walk(v,path=''):
    if isinstance(v,dict):
     if v.get('m_PathID')==PID and v.get('m_FileID') in bgids:external_refs.append({'bundle':str(folder/n),'object_id':str(obj.path_id),'field':path})
     for k,x in v.items():walk(x,path+'/'+k)
    elif isinstance(v,(list,tuple)):
     for i,x in enumerate(v):walk(x,path+'/'+str(i))
   walk(t)
assert not external_refs, ('Original TF patch is referenced; clean references before removal',external_refs)
data=e.file.save(packer='lz4');saved=UnityPy.load(data);sa=saved.assets[0]
assert set(sa.objects)==set(hashes)-{PID} and sa.name==a.name
for i,h in hashes.items():
 if i not in [PID,bundle.path_id]:assert sha(sa.objects[i].get_raw_data())==h
for k,h in aux.items():assert sha(saved.file.files[k].bytes)==h
assert sa.objects[bundle.path_id].read_typetree()==meta
assert not (banned&set(sa.objects)) and all(p['m_PathID'] not in banned|{PID} for p in meta['m_PreloadTable'])
assert all(v['asset']['m_PathID'] not in banned|{PID} for k,v in meta['m_Container'])
# Verify the remaining directory spans preserve their exact dependency contents.
entries=dict(meta['m_Container'])
for key,v in old['m_Container']:
 if is_deleted(v['asset']):continue
 nv=entries[key];span=pre[v['preloadIndex']:v['preloadIndex']+v['preloadSize']]
 assert meta['m_PreloadTable'][nv['preloadIndex']:nv['preloadIndex']+nv['preloadSize']]==[p for p in span if not is_deleted(p)]
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);audits=[]
for folder,catdir in [(G,AA),(S,S)]:
 c=cm.Catalog((catdir/'catalog.bin').read_bytes());keys={k:p for k,p in c.keys() if isinstance(k,str)};locations={loc for p in keys.values() for (loc,) in c.array(p,'I')}
 def bl(n):return next(loc for loc in locations if c.location(loc)['provider'].endswith('.AssetBundleProvider') and c.location(loc)['internal'].endswith('\\'+n))
 bg=bl(BN);count=0
 for n in [WN,GN]:
  wa=loaded[(folder,n)];own=bl(n);bm=next(o.read_typetree() for o in wa.objects.values() if o.type.name=='AssetBundle')
  for key,entry in bm['m_Container']:
   if not re.fullmatch('[0-9a-f]{32}',key) or entry['asset']['m_FileID']!=0:continue
   obj=wa.objects.get(entry['asset']['m_PathID'])
   if not obj or not(-1000000000000000<obj.path_id<-900000000000000) or obj.type.name!='MonoBehaviour':continue
   t=obj.read_typetree();typ='SI.VisualScripting.VisualFunction' if 'm_nodes' in t else ('UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in t else None)
   if not typ:continue
   assert key in keys
   for (loc,) in c.array(keys[key],'I'):
    val=c.location(loc);assert val['type'][1]==typ and val['dependencies'][0]==own and bg in val['dependencies']
   count+=1
 audits.append({'catalog':str(catdir/'catalog.bin'),'custom_vta_vf_checked':count})
current=copy.deepcopy(registry);current['textures']=[t for t in current['textures'] if t['name']!=NAME and int(t['path_id'])!=PID];assert len(current['textures'])==len(registry['textures'])-1
current.update(version=65,date='2026-10-28',authoritative_source_bundle=str(O/BN),source_bundle_sha256=sha(data),manifest=str(O/'删除及校验记录.json'),active_custom_texture_count=len(current['textures']))
current.setdefault('removed_textures',[]).append({'name':NAME,'path_id':str(PID),'removed_on':'2026-10-28','restore':False})
O.mkdir();(O/BN).write_bytes(data);(O/'更新后的有效图片恢复来源.json').write_text(json.dumps(current,ensure_ascii=False,indent=2),'utf8')
(O/'回退').mkdir();(O/'回退'/'current-custom-textures.json').write_bytes((R/'current-custom-textures.json').read_bytes())
installs=[]
for p,b in before.items():
 tag='game' if p.parent==G else 'skin';rel=Path('回退')/tag/BN;(O/rel).parent.mkdir();(O/rel).write_bytes(b);installs.append({'target':str(p),'source':BN,'backup':rel.as_posix(),'before_sha256':sha(b),'after_sha256':sha(data)})
m={'version':65,'installed':False,'runtime_verified':False,'removed_name':NAME,'removed_path_id':str(PID),'active_custom_texture_count':len(current['textures']),'derivative_TF_patch_aligned_preserved':True,'external_original_references':external_refs,'catalog_audits':audits,'other_objects_preserved':len(hashes)-2,'install_files':installs,'protected_sha256':{str(p):h for p,h in protected.items()}}
(O/'删除及校验记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
for rollback in [False,True]:
 rows='\n'.join("@{Target='"+x['target']+"';Source='"+(x['backup'] if rollback else BN)+"';Before='"+(x['after_sha256'] if rollback else x['before_sha256'])+"';After='"+(x['before_sha256'] if rollback else x['after_sha256'])+"'}" for x in installs)
 script="$ErrorActionPreference='Stop'\nif(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}\n$items=@(\n"+rows+"\n)\nforeach($x in $items){if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.Before){throw 'Target version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Package hash mismatch.'}}\n$written=@()\ntry{foreach($x in $items){$written+=@{Target=$x.Target;Bytes=[IO.File]::ReadAllBytes($x.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Destination $x.Target -Force;if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Install checksum mismatch.'}}}catch{foreach($x in $written){[IO.File]::WriteAllBytes($x.Target,$x.Bytes)};throw}\n"
 if not rollback:script+="& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(R/'finish-remove-tf-v65.py')+"' --commit\nif($LASTEXITCODE -ne 0){throw 'Registry update failed.'}\n"
 else:script+="Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination '"+str(R/'current-custom-textures.json')+"' -Force\n"
 (O/('回退.ps1' if rollback else '安装.ps1')).write_text(script,"utf-8-sig")
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
print(json.dumps({'prepared':True,'removed':NAME,'active_after_install':len(current['textures']),'derivative_preserved':True,'catalog_audits':audits},ensure_ascii=False),flush=True)
