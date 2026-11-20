from pathlib import Path
import sys,json,copy,hashlib
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
R=Path.cwd();G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');O=R/'prepare-current-backgrounds-1-14';O.mkdir(exist_ok=True)
r=json.loads((R/'current-custom-textures.json').read_text('utf8'));retired=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']+r['removed_textures'];ids={int(t['path_id']) for t in retired};names={t['name'].lower() for t in retired}
source=UnityPy.load(r['authoritative_source_bundle']);so={o.path_id:o for o in source.objects};assert hashlib.sha256(Path(r['authoritative_source_bundle']).read_bytes()).hexdigest()==r['source_bundle_sha256']
for bn in ['ui-backgrounds_assets_common.bundle','ui-backgrounds_assets_.bundle']:
 e=UnityPy.load(str(G/bn));af=e.assets[0];objs={o.path_id:o for o in e.objects};before={i:hashlib.sha256(o.get_raw_data()).hexdigest() for i,o in objs.items()};changed=set();expected={};metaobj=next(o for o in objs.values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree()
 def put(src,pid,name=None):
  if pid in objs:o=objs[pid];d=src.read_typetree();d['m_Name']=name or o.peek_name();o.save_typetree(d)
  else:
   template=next(o for o in objs.values() if o.type.name=='Texture2D');o=copy.copy(template);o.path_id=pid;o.data=None;o._read_until=None;af.objects[pid]=o;objs[pid]=o;o.save_typetree(src.read_typetree())
  expected[pid]=d if pid in before else src.read_typetree();changed.add(pid)
 if 'common' in bn:
  for t in r['textures']+[{'name':o.peek_name(),'path_id':str(o.path_id)} for o in so.values() if o.type.name=='Texture2D' and o.peek_name().startswith('FM27StatusRing')]:
   pid=int(t['path_id']);assert pid not in ids;assert so[pid].peek_name()==t['name'];put(so[pid],pid)
   ptr={'m_FileID':0,'m_PathID':pid}
   if not any(v['asset']==ptr for k,v in meta['m_Container']):meta['m_Container'].append((t['name'].lower(),{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':1,'asset':ptr}));meta['m_PreloadTable'].append(ptr)
 targets=[t for t in r['native_background_overrides']['textures'] if t['bundle']==bn]
 restored=[];missing=[]
 for t in targets:
  hits=[o for o in objs.values() if o.type.name=='Texture2D' and o.peek_name()==t['actual_name']]
  if not hits:missing.append(t['actual_name']);continue
  assert len(hits)==1;o=hits[0];put(so[-910000000000149],o.path_id,o.peek_name());restored.append(o.peek_name())
 for t in r.get('native_individual_replacements',[]):
  if t['bundle']!=bn:continue
  hits=[o for o in objs.values() if o.type.name=='Texture2D' and o.peek_name()==t['name']]
  if hits:
   se=UnityPy.load(t['authoritative_source_bundle']);src=next(o for o in se.objects if o.path_id==int(t['path_id']));put(src,hits[0].path_id,hits[0].peek_name());restored.append(t['name'])
 assert ids.isdisjoint(objs)
 assert all(p['m_PathID'] not in ids for p in meta['m_PreloadTable'])
 assert all(k.lower() not in names and v['asset']['m_PathID'] not in ids for k,v in meta['m_Container'])
 meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta);changed.add(metaobj.path_id)
 b=e.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(b).objects}
 for i,h in before.items():
  if i not in changed:assert hashlib.sha256(check[i].get_raw_data()).hexdigest()==h
 for i in changed:
  assert check[i].read_typetree()==(meta if i==metaobj.path_id else expected[i]),i
 (O/bn).write_bytes(b);print(bn,'custom',180 if 'common' in bn else 0,'native_overrides',len(restored),'missing',missing)
