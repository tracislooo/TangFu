from pathlib import Path
import sys,json,hashlib,struct,importlib.util
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cat=cm.Catalog((out/'catalog.bin').read_bytes());keys=dict(cat.keys());original=cm.Catalog((out/'backup-game/catalog.bin').read_bytes())
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
records=list(cat.key_records);labeladd={}
for label,bundle in [('GameWorldVisualTreeAssetPreload',W),('GlobalVisualTreeAssetPreload',G)]:
 idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==label);ko,ptr=records[idx]
 new=[cat.array(keys[c['guid']],'I')[0][0] for c in m['clones'] if c['bundle']==bundle and c['kind']=='template']
 old=[x[0] for x in cat.array(ptr,'I')];records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in old+new),True));labeladd[label]=new
struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True))
data=bytes(cat.data);cat=cm.Catalog(data);keys=dict(cat.keys())
for key,ptr in original.keys():
 old=[x[0] for x in original.array(ptr,'I')];actual=[x[0] for x in cat.array(keys[key],'I')]
 assert actual==old+labeladd.get(key,[])
 for loc in old:assert cat.location(loc)==original.location(loc)

loaded={};audits=[];seen=set();game=Path(tx['game'])
def load(bundle):
 if bundle not in loaded:
  path=out/bundle if (out/bundle).exists() else game/bundle
  e=UnityPy.load(str(path));oo={o.path_id:o for o in e.objects};mt=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
  idx={}
  for g,v in mt['m_Container']:
   ob=oo.get(v['asset']['m_PathID']) if v['asset']['m_FileID']==0 else None
   if ob and ob.type.name=='MonoBehaviour':
    d=ob.read_typetree()
    if 'inlineSheet' in d or 'm_nodes' in d:idx[g]=(ob,d)
  loaded[bundle]=(oo,idx)
 return loaded[bundle]
def resource_refs(v):
 ret=set()
 if isinstance(v,dict):
  for k,x in v.items():
   if k in ['m_guid','m_AssetGUID','path'] and isinstance(x,str) and len(x)==32 and all(c in '0123456789abcdef' for c in x):ret.add(x)
   else:ret.update(resource_refs(x))
 elif isinstance(v,(list,tuple)):
  for x in v:ret.update(resource_refs(x))
 return ret
def audit(g):
 if g in seen:return
 seen.add(g);assert g in keys,('GUID missing',g)
 locs=[cat.location(v[0]) for v in cat.array(keys[g],'I')]
 typed=[q for q in locs if q['type'][1] in ['UnityEngine.UIElements.VisualTreeAsset','SI.VisualScripting.VisualFunction']]
 if not typed:return
 q=typed[0];assert q['dependencies']
 bundle=cat.location(q['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
 oo,idx=load(bundle);assert g in idx,('Typed GUID absent from owning bundle',g,bundle)
 ob,d=idx[g];kind='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in d else 'SI.VisualScripting.VisualFunction'
 assert all(q['type'][1]==kind for q in typed)
 for q in typed:assert cat.location(q['dependencies'][0])['internal'].replace('\\','/').endswith('/'+bundle)
 if 'inlineSheet' in d and d['inlineSheet']['m_PathID']:
  assert d['inlineSheet']['m_FileID']==0 and d['inlineSheet']['m_PathID'] in oo,(g,d['m_Name'],d['inlineSheet'],bundle)
 audits.append({'guid':g,'name':d['m_Name'],'kind':kind,'bundle':bundle,'pid':ob.path_id})
 for child in resource_refs(d):audit(child)
for c in m['clones']:audit(c['guid'])
sha=lambda b:hashlib.sha256(b).hexdigest()
(out/'catalog.bin').write_bytes(data);(out/'catalog.hash').write_bytes(hashlib.md5(data).hexdigest().encode('ascii'))
for p,source in tx['sources'].items():m['after_sha256'][p]=sha(Path(source).read_bytes())
m.update(existing_catalog_asset_locations_unchanged=True,preload_additions={k:len(v) for k,v in labeladd.items()},catalog_templates_and_functions_verified=len(audits));m.pop('existing_catalog_locations_unchanged',None)
(out/'catalog-audits.json').write_text(json.dumps(audits,ensure_ascii=False,indent=2),'utf8')
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'output':str(out),'preload_additions':m['preload_additions'],'templates_functions_verified':len(audits)}),flush=True)
