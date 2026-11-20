from pathlib import Path
import sys,json,hashlib,importlib.util,struct,zlib,shutil
R=Path.cwd();G=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
O=next(p for p in sorted(R.glob('pinned-1-14-update-*'),reverse=True) if (p/'manifest.json').exists());m=json.loads((O/'manifest.json').read_text('utf8'));sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
for bn in ['ui-backgrounds_assets_common.bundle','ui-backgrounds_assets_.bundle']:
 if bn not in m['new_game_before_sha256']:m['new_game_before_sha256'][bn]=hashlib.sha256((G/bn).read_bytes()).hexdigest();shutil.copy2(G/bn,O/'backup-game'/bn)
 shutil.copy2(R/'prepare-current-backgrounds-1-14'/bn,O/bn);m['after_sha256'][bn]=hashlib.sha256((O/bn).read_bytes()).hexdigest()
c=cm.Catalog((O/'catalog.bin').read_bytes());old=cm.Catalog((S/'catalog.bin').read_bytes());oldkeys=dict(old.keys());keys=dict(c.keys())
def all_locations(cat):
 return {loc:cat.location(loc) for _,ls in cat.keys() for (loc,) in cat.array(ls,'I')}
locs=all_locations(c);oldlocs=all_locations(old)
def basename(s):return s.replace(chr(92),'/').split('/')[-1]
bl={basename(v['internal']):i for i,v in locs.items() if v['type'][1].endswith('IAssetBundleResource')}
patched=0
for key,ls in c.keys():
 if key not in oldkeys:continue
 for (loc,) in c.array(ls,'I'):
  v=c.location(loc)
  if v['type'][1].endswith('IAssetBundleResource') or not v['dependencies']:continue
  ov=next((old.location(i) for (i,) in old.array(oldkeys[key],'I') if old.location(i)['type']==v['type']),None)
  if not ov:continue
  required=[bl[basename(oldlocs[i]['internal'])] for i in ov['dependencies'] if basename(oldlocs[i]['internal']) in bl]
  deps=list(dict.fromkeys(v['dependencies']+required))
  if deps!=v['dependencies']:
   raw=list(c.unpack(loc,'7I'));bb=b''.join(struct.pack('<I',i) for i in deps);raw[3]=c.append(bb,True);raw[4]=zlib.crc32(bb);struct.pack_into('<7I',c.data,loc,*raw);patched+=1
payload=bytes(c.data);(O/'catalog.bin').write_bytes(payload);(O/'catalog.hash').write_text(hashlib.md5(payload).hexdigest(),'ascii');m['catalog_after_sha256']=hashlib.sha256(payload).hexdigest();m['extra_native_dependency_entries_restored']=patched;m['active_custom_texture_count']=180;m['background_registry_version']=73
(O/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'output':str(O),'native_catalog_entries_with_added_dependencies':patched}))

