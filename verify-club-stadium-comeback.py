"""Independent check of the prepared/installed native lookup and preserved UI objects."""
from pathlib import Path
import sys,json,hashlib,struct,importlib.util
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
spec=importlib.util.spec_from_file_location('cm',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
O=Path(sys.argv[1]);installed='--installed' in sys.argv
sha=lambda b:hashlib.sha256(b).hexdigest();tx=json.loads((O/'transaction.json').read_text('utf8'));mapping=json.loads((O/'photo-mapping.json').read_text('utf8'));m=json.loads((O/'manifest.json').read_text('utf8'))
for tag in ['game','skin']:
 rows=[x for x in tx if ('backup-'+tag) in str(x['backup'])];wr=next(x for x in rows if x['target'].endswith('.bundle'));cr=next(x for x in rows if x['target'].endswith('catalog.bin'));hr=next(x for x in rows if x['target'].endswith('catalog.hash'))
 get=lambda x:Path(x['target'] if installed else x['source']).read_bytes()
 before={o.path_id:o for o in UnityPy.load(Path(wr['backup']).read_bytes()).objects};after={o.path_id:o for o in UnityPy.load(get(wr)).objects};assert set(before)==set(after)
 changed=[i for i in before if before[i].get_raw_data()!=after[i].get_raw_data()];assert changed==[-991100000000030],changed
 d=after[changed[0]].read_typetree();old=before[changed[0]].read_typetree();a=next(r['data'] for r in d['references']['RefIds'] if r.get('data',{}).get('name')=='ClubOverviewStadiumPackPhoto');oa=next(r['data'] for r in old['references']['RefIds'] if r.get('data',{}).get('name')=='ClubOverviewStadiumPackPhoto')
 for k in ['Binding','Binding_UxmlAttributeFlags','ScaleMode','ScaleMode_UxmlAttributeFlags','KeepImageWhileLoading','KeepImageWhileLoading_UxmlAttributeFlags']:oa[k]=a[k]
 assert old==d,'Unexpected UI change'
 vf=a['Binding']['m_visualFunction'];assert vf['m_target']['m_guid']=='7a35874b5cb0acb4d846df3f46c3a872';b=bytes(vf['m_inputs']['m_variable']['m_argumentBytes']);assert b[0]==6;p=1;args=[]
 for i in range(6):
  n=struct.unpack_from('<I',b,p)[0];p+=4;args.append(b[p:p+n]);p+=n
 assert p==len(b) and args[0].endswith(b'\x01\x15club.MainTeam.KitHome') and args[4].endswith(struct.pack('<I',7)) and args[5].endswith(b'\x01\x0bfmetstadium')
 cb=get(cr);cat=cm.Catalog(cb);keys=dict(cat.keys());bc=cm.Catalog(Path(cr['backup']).read_bytes());assert cat.key_records[:len(bc.key_records)]==bc.key_records;assert get(hr).decode()==hashlib.md5(cb).hexdigest()
 for x in mapping:
  loc=cat.location(cat.array(keys[x['key']],'I')[0][0]);assert loc['provider']=='SI.Core.LocalAssetProvider' and loc['type'][1]=='UnityEngine.Texture2D' and Path(loc['internal']).resolve()==Path(x['image']).resolve() and Path(x['image']).is_file()
 for row in rows:assert sha(get(row))==row['after']
for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h
print(json.dumps(dict(verified=True,installed=installed,files=len(tx),photo_clubs=len(mapping),photo_stadiums=len(set(x['image'] for x in mapping)),unrelated_objects_byte_identical=True,runtime_verified=False)))
