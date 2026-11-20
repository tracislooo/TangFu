from pathlib import Path
import sys,json,hashlib,ast,importlib.util,re
from collections import Counter
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
GAME=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
OUT=next(p for p in sorted(R.glob('pinned-1-14-update-*'),reverse=True) if (p/'manifest.json').exists())
m=json.loads((OUT/'manifest.json').read_text('utf8'));names=list(m['after_sha256']);env={n:UnityPy.load(str(OUT/n)) for n in names}
bg='ui-backgrounds_assets_common.bundle';env[bg]=UnityPy.load(str(OUT/bg));afs={a.name.lower():a for e in env.values() for a in e.assets};objects={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
src=ast.parse((R/'add-card-six-ratings.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='validate_ui'],type_ignores=[]),'validator','exec'))
checks=[];pointers_checked=0
for n in names:
 before=UnityPy.load(str(OUT/'backup-game'/n));bm=next(o.read_typetree() for o in before.objects if o.type.name=='AssetBundle');am=next(o.read_typetree() for o in env[n].objects if o.type.name=='AssetBundle')
 pairs=lambda meta:Counter((k,v['asset']['m_FileID'],v['asset']['m_PathID']) for k,v in meta['m_Container'])
 assert not (pairs(bm)-pairs(am)),('native container entries lost',n,pairs(bm)-pairs(am))
for item in m['stage_assets']:
 if item['source_id'] in [-6400646727147995419,-3862538512510687317,168226888031714516,5938222404796150770,7199728689344018492,5775949770471550939,-4194025542157271532]:assert item['replaces_native'],item
for item in m['stage_assets']:
 n=item['bundle'];o=objects[n][item['id']];d=o.read_typetree()
 def walk(v):
  global pointers_checked
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID']:
    fid=v['m_FileID'];cab=(o.assets_file.name if not fid else o.assets_file.externals[fid-1].name).lower()
    if cab in afs:assert v['m_PathID'] in afs[cab].objects,(d.get('m_Name'),cab,v)
    pointers_checked+=1
   for x in v.values():walk(x)
  elif isinstance(v,list):
   for x in v:walk(x)
 walk(d)
 if 'm_VisualTree' in d and d['inlineSheet']['m_PathID']:
  p=d['inlineSheet'];a=o.assets_file if not p['m_FileID'] else afs[o.assets_file.externals[p['m_FileID']-1].name.lower()]
  validate_ui(d,a.objects[p['m_PathID']].read_typetree())
  checks.append(d['m_Name'])

spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog((OUT/'catalog.bin').read_bytes());old=cm.Catalog((OUT/'backup-game/catalog.bin').read_bytes());assert set(dict(old.keys()))<=set(dict(cat.keys()))
locations={}
for k,ls in cat.keys():
 for (loc,) in cat.array(ls,'I'):locations[loc]=cat.location(loc)
seen=set();active=set()
def visit(loc):
 if loc in seen:return
 assert loc not in active,('catalog dependency cycle',cat.location(loc)['internal']);active.add(loc)
 for dep in cat.location(loc)['dependencies']:visit(dep)
 active.remove(loc);seen.add(loc)
for loc in locations:visit(loc)
for guid in m['registered_custom_guids']:assert len(cat.locations(guid))==1
keys=set(dict(cat.keys()))
def guids(v):
 if isinstance(v,dict):
  if v.get('m_AssetGUID'):yield v['m_AssetGUID']
  if v.get('m_target',{}).get('m_guid'):yield v['m_target']['m_guid']
  for u in v.get('m_Usings',[]):
   if u.get('path'):yield u['path']
  for x in v.values():yield from guids(x)
 elif isinstance(v,list):
  for x in v:yield from guids(x)
for item in m['stage_assets']:
 d=objects[item['bundle']][item['id']].read_typetree()
 for guid in guids(d):assert guid in keys,('missing asset GUID',d.get('m_Name'),guid)

audit={'valid_tree_count':len(checks),'checked_object_pointers':pointers_checked,'catalog_dependency_cycles':False,'original_catalog_keys_preserved':True,'all_original_container_entries_preserved':True,'all_template_guids_resolved':True,'runtime_verified':False}
(OUT/'verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),'utf8');print(json.dumps(audit))

registry=json.loads((R/'current-custom-textures.json').read_text('utf8'));retired=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];reserved_ids={int(x['path_id']) for x in retired};reserved_names={x['name'].lower() for x in retired}
for bn,items in objects.items():
 assert reserved_ids.isdisjoint(items),(bn,'retired ID occupied')
 meta=next(o.read_typetree() for o in items.values() if o.type.name=='AssetBundle')
 assert all(p['m_PathID'] not in reserved_ids for p in meta['m_PreloadTable'])
 assert all(k.lower() not in reserved_names and v['asset']['m_PathID'] not in reserved_ids for k,v in meta['m_Container'])
reserved_ids.add(-910000000000146)
for t in registry['textures']:
 o=objects[bg][int(t['path_id'])];assert o.peek_name()==t['name'];assert hashlib.sha256(o.get_raw_data()).hexdigest()==t['texture_sha256']
vtas=0;functions=0;catalog_checked=[]
for bn,items in objects.items():
 if bn==bg:continue
 meta=next(o.read_typetree() for o in items.values() if o.type.name=='AssetBundle')
 for key,v in meta['m_Container']:
  pid=v['asset']['m_PathID']
  if not re.fullmatch('[0-9a-f]{32}',key) or v['asset']['m_FileID'] or pid not in items:continue
  o=items[pid]
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree();typ='SI.VisualScripting.VisualFunction' if 'm_nodes' in d else 'UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in d else None
  if not typ or not (-999000000000000<pid<=-910000000000000):continue
  assert key in keys,('custom GUID missing',bn,d.get('m_Name'),key)
  for loc in cat.locations(key):
   entry=cat.location(loc);assert entry['type'][1]==typ,(key,entry['type'],typ)
   assert entry['dependencies'] and cat.location(entry['dependencies'][0])['internal'].replace('\\','/').endswith('/'+bn),(key,'wrong first bundle',entry)
   assert any(cat.location(dep)['internal'].replace('\\','/').endswith('/'+bg) for dep in entry['dependencies']),(key,'background dependency missing')
  vtas+=int(typ.endswith('VisualTreeAsset'));functions+=int(typ.endswith('VisualFunction'));catalog_checked.append({'guid':key,'name':d.get('m_Name'),'bundle':bn,'path_id':pid,'type':typ})
assert functions>=15
assert '64033a72b9925c8dad3b08826077c328' in keys
audit.update(active_textures=len(registry['textures']),retired70_absent=True,custom_vta_registrations=vtas,custom_function_registrations=functions,custom_catalog_types_and_bundle_dependencies_verified=True)
(OUT/'verification.json').write_text(json.dumps(audit,ensure_ascii=False,indent=2),'utf8');(OUT/'catalog-resources-verified.json').write_text(json.dumps(catalog_checked,ensure_ascii=False,indent=2),'utf8');print(json.dumps(audit))
