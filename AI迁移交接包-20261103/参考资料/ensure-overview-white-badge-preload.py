from pathlib import Path
import json,struct,hashlib,uuid,importlib.util,datetime
R=Path.cwd();loc=json.loads((R/'current-game-location.json').read_text('utf-8-sig'));spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);key=uuid.uuid5(uuid.NAMESPACE_URL,'FM27OverviewWhiteAttributeBadge').hex
OUT=R/('overview-white-badge-preload-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir();records=[]
for tag,folder in [('game',Path(loc['aa_root'])),('skin',Path(loc['skin_packages']))]:
 p=folder/'catalog.bin';raw=p.read_bytes();hashraw=(folder/'catalog.hash').read_bytes();backup=OUT/tag;backup.mkdir();(backup/'catalog.bin').write_bytes(raw);(backup/'catalog.hash').write_bytes(hashraw);c=cm.Catalog(raw);nl=c.locations(key)[0];idx=next(i for i,(k,ptr) in enumerate(c.key_records) if c.object(k)=='GlobalVisualTreeAssetPreload');ko,ptr=c.key_records[idx];old=[x[0] for x in c.array(ptr,'I')]
 if nl not in old:
  newset=c.append(b''.join(struct.pack('<I',x) for x in old+[nl]),True);rs=list(c.key_records);rs[idx]=(ko,newset);newtable=c.append(b''.join(struct.pack('<2I',*r) for r in rs),True);struct.pack_into('<I',c.data,8,newtable)
 out=bytes(c.data);assert p.read_bytes()==raw;p.write_bytes(out);(folder/'catalog.hash').write_bytes(hashlib.md5(out).hexdigest().encode('ascii'));cc=cm.Catalog(p.read_bytes());assert nl in cc.locations('GlobalVisualTreeAssetPreload');records.append({'target':str(folder),'registered':True,'old_location_count':len(old),'new_location_count':len(cc.locations('GlobalVisualTreeAssetPreload'))})
(OUT/'manifest.json').write_text(json.dumps({'installed':True,'runtime_verified':False,'guid':key,'changes':records},indent=2),'utf8');print(OUT)
