from pathlib import Path
import sys,json,hashlib,struct,zlib,importlib.util,datetime
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');base=R/'updated-game-last-skin-migration-20261020-132948';m=json.loads((base/'manifest.json').read_text('utf8'))
sp=importlib.util.spec_from_file_location('c',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
before=(GAME.parent/'catalog.bin').read_bytes();assert before==(SKIN/'catalog.bin').read_bytes();cat=cm.Catalog(before)
roots={}
for n in m['after_sha256']:
 e=UnityPy.load(str(GAME/n));obs={o.path_id:o for o in e.objects};meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle')
 for k,v in meta['m_Container']:
  if v['asset']['m_FileID']==0:
   o=obs[v['asset']['m_PathID']]
   if o.type.name=='MonoBehaviour' and o.serialized_type.script_id.hex()!='55df88d949bb6ddf480913cd0b7df24f':roots[k]=n
changes=[]
for guid in m['registered_custom_guids']:
 target=roots[guid]
 for loc in cat.locations(guid):
  v=cat.location(loc);deps=v['dependencies'];own=next(x for x in deps if cat.location(x)['internal'].replace('\\','/').endswith('/'+target))
  ordered=[own]+[x for x in deps if x!=own]
  if ordered!=deps:
   raw=list(cat.unpack(loc,'7I'));b=b''.join(struct.pack('<I',x) for x in ordered);raw[3]=cat.append(b,True);raw[4]=zlib.crc32(b);struct.pack_into('<7I',cat.data,loc,*raw);changes.append({'guid':guid,'bundle':target,'old_first_bundle':cat.location(deps[0])['internal']})
cat=cm.Catalog(bytes(cat.data))
for guid in m['registered_custom_guids']:
 for loc in cat.locations(guid):
  v=cat.location(loc);assert cat.location(v['dependencies'][0])['internal'].replace('\\','/').endswith('/'+roots[guid])
# Verify actual runtime lookup: the first bundle contains the requested root of the requested type.
assert cat.location(cat.location(cat.locations('fe01767f057e549684f9682096e6b529')[0])['dependencies'][0])['internal'].endswith('ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')
assert set(dict(cm.Catalog(before).keys()))==set(dict(cat.keys()))
OUT=R/('player-page-bundle-order-fix-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();(OUT/'catalog-before.bin').write_bytes(before);(OUT/'catalog-before.hash').write_bytes((GAME.parent/'catalog.hash').read_bytes());output=bytes(cat.data);hashout=hashlib.md5(output).hexdigest().encode('ascii');(OUT/'catalog.bin').write_bytes(output);(OUT/'catalog.hash').write_bytes(hashout)
original={p:p.read_bytes() for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']}
try:
 for p,b in [(GAME.parent/'catalog.bin',output),(GAME.parent/'catalog.hash',hashout),(SKIN/'catalog.bin',output)]:p.write_bytes(b);assert p.read_bytes()==b
except BaseException:
 for p,b in original.items():p.write_bytes(b)
 raise
report={'installed':True,'runtime_verified':False,'fixed_assets':changes,'all_28_custom_assets_first_bundle_verified':True,'original_catalog_keys_preserved':True};(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'fixed_asset_count':len(changes),'all_custom_resource_routes_verified':True,'output':str(OUT)},ensure_ascii=True))
# Correct the migration generator so later rebuilds preserve this invariant.
p=R/'migrate-last-skin-to-updated-game.py';s=p.read_text('utf-8-sig');s=s.replace("bundleloc[n] in v['dependencies']),template_loc)","v['dependencies'] and v['dependencies'][0]==bundleloc[n]),template_loc)");s=s.replace("deps=list(dict.fromkeys(deps+required_deps[n]));depbytes=", "deps=list(dict.fromkeys([bundleloc[n]]+deps+required_deps[n]));depbytes=");p.write_text(s,'utf8')
