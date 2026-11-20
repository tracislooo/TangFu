"""Update native-format bundle request CRC/size metadata for installed skin content."""
from pathlib import Path
import sys,json,hashlib,importlib.util,struct,zlib
sys.path.insert(0,'.codex-deps')
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
out=Path(sys.argv[1]);m=json.loads((out/'manifest.json').read_text('utf8'))
game=Path(json.loads(Path('current-game-location.json').read_text('utf8'))['bundle_root'])
spec=importlib.util.spec_from_file_location('catalog','catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cat=cm.Catalog((out/'catalog.bin').read_bytes())
names=set(m['after_sha256'])|{'ui-fonts_assets_fmuniverse.bundle'}
def crc(data):
    reader=EndianBinaryReader(data);bundle=object.__new__(BundleFile)
    bundle.signature=reader.read_string_to_null();bundle.version=reader.read_u_int()
    bundle.version_player=reader.read_string_to_null();bundle.version_engine=reader.read_string_to_null()
    _,block=bundle.read_fs(reader)
    return zlib.crc32(block.bytes)
locations={loc:cat.location(loc) for _,ls in cat.keys() for loc, in cat.array(ls,'I')}
cache={};records=[]
for loc,v in locations.items():
    if not v['type'][1].endswith('IAssetBundleResource'):continue
    name=v['internal'].replace('\\','/').split('/')[-1]
    if name not in names:continue
    if name not in cache:
        p=out/name if (out/name).is_file() else game/name
        data=p.read_bytes();cache[name]=(crc(data),len(data),hashlib.sha256(data).hexdigest())
    checksum,size,digest=cache[name]
    extra=v['raw'][5];typ,payload=cat.unpack(extra,'2I');raw=list(cat.unpack(payload,'5I'))
    assert cat.typename(typ)[1].endswith('AssetBundleRequestOptions')
    original_crc,original_size=raw[2:4]
    raw[2],raw[3]=checksum,size
    new_payload=cat.append(struct.pack('<5I',*raw));new_extra=cat.append(struct.pack('<2I',typ,new_payload))
    location=list(v['raw']);location[5]=new_extra;struct.pack_into('<7I',cat.data,loc,*location)
    records.append(dict(bundle=name,crc=checksum,size=size,sha256=digest,previous_crc=original_crc,previous_size=original_size))
assert names==set(cache)
data=bytes(cat.data);(out/'catalog.bin').write_bytes(data);(out/'catalog.hash').write_text(hashlib.md5(data).hexdigest(),'ascii')
m['catalog_after_sha256']=hashlib.sha256(data).hexdigest();m['bundle_request_options_updated']=records
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
print('Bundle CRC and size metadata verified for',len(records),'bundles')
