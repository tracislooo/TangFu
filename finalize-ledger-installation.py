"""Record installed main resources and a verified new native baseline."""
from pathlib import Path
import json,hashlib,importlib.util,shutil,sys,zlib
sys.path.insert(0,'.codex-deps')
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
root=Path.cwd();out=Path(sys.argv[1]).resolve();read=lambda p:json.loads(p.read_text('utf8'));sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
m=read(out/'manifest.json');aa=Path(read(root/'current-game-location.json')['aa_root'])
inventory=read(root/'update-review-20261117.json')['all_native_files']
assert all(sha(aa/'StandaloneWindows64'/r['bundle'])==m['after_sha256'].get(r['bundle'],r['sha256']) for r in inventory),'Installed or protected bundle mismatch'
assert sha(aa/'catalog.bin')==m['catalog_after_sha256']
assert (aa/'catalog.hash').read_text().strip()==hashlib.md5((aa/'catalog.bin').read_bytes()).hexdigest()
ledger=Path(m['source_ledger']);lm=read(ledger/'manifest.json');lb={x['bundle']:x for x in read(ledger/'baseline-index.json')['bundles']}
mod={x['bundle']:x for x in lm['bundles'] if x['mode']=='current-game' and x['objects']}
base=out/'new-native-baseline';(base/'updated-native/aa/StandaloneWindows64').mkdir(parents=True,exist_ok=True)
sp=importlib.util.spec_from_file_location('c',root/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
catalog=cm.Catalog((out/'backup-game/catalog.bin').read_bytes())
options={}
for key,ls in catalog.keys():
    for loc, in catalog.array(ls,'I'):
        v=catalog.location(loc)
        if v['type'][1].endswith('IAssetBundleResource') and v['raw'][5]!=cm.NULL:
            _,p=catalog.unpack(v['raw'][5],'2I');options[v['internal'].replace('\\','/').split('/')[-1]]=catalog.unpack(p,'5I')
def crc(path):
    data=path.read_bytes();r=EndianBinaryReader(data);b=object.__new__(BundleFile)
    b.signature=r.read_string_to_null();b.version=r.read_u_int();b.version_player=r.read_string_to_null();b.version_engine=r.read_string_to_null()
    _,blocks=b.read_fs(r);return zlib.crc32(blocks.bytes)
native_inventory=[];provenance=[]
for row in inventory:
    name=row['bundle'];h=row['sha256'];source=aa/'StandaloneWindows64'/name
    if name in mod:
        before=out/'backup-game'/name
        if before.is_file():source=before
        assert sha(source)==h,name
        old=mod[name]
        if h==old['modified_sha256'] and h!=old['original_sha256']:
            source=ledger/lb[name]['materialized_native']
            assert sha(source)==old['original_sha256'],name
            assert options[name][2]==crc(source) and options[name][3]==source.stat().st_size,('Native baseline CRC/size not confirmed',name)
            h=sha(source);provenance.append(dict(bundle=name,source=str(source),confirmed_by='New official catalog CRC and size'))
        target=base/'updated-native/aa/StandaloneWindows64'/name
        shutil.copy2(source,target);assert sha(target)==h
    native_inventory.append(dict(name=name,sha256=h,bytes=source.stat().st_size))
for name in ['catalog.bin','catalog.hash']:shutil.copy2(out/'backup-game'/name,base/'updated-native/aa'/name)
settings=aa/'settings.json'
if settings.exists():shutil.copy2(settings,base/'updated-native/aa/settings.json')
(base/'updated-all-bundle-hashes.json').write_text(json.dumps(native_inventory,ensure_ascii=False,indent=2),'utf8')
(base/'provenance.json').write_text(json.dumps(provenance,ensure_ascii=False,indent=2),'utf8')
m.update(scope='Current-game complete bundle ledger 20261117, main only',installed_files_verified=True,all_537_bundles_verified=True,new_native_baseline=str(base))
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(root/'current-main-skin-install.json').write_text(json.dumps(dict(installation=str(out),manifest=str(out/'manifest.json'),mode='non-sidebar',source_ledger=str(ledger),verified=True),ensure_ascii=False,indent=2),'utf8')
statepath=root/'current-sidebar-version.json';state=read(statepath)
(out/'previous-sidebar-state.json').write_bytes(statepath.read_bytes());state.update(current_game_mode='non-sidebar',status='latest_ledger_migrated_20261117',current_non_sidebar_build=str(out))
statepath.write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
(root/'current-game-update-comparison.json').write_text(json.dumps(dict(archive=str(base),native_baseline_date='2026-11-17',report=str(out/'迁移说明.md'),scope='main only',installed=True,installation=str(out),installation_manifest=str(out/'manifest.json')),ensure_ascii=False,indent=2),'utf8')
print('Installed files and all 537 bundles verified. Updated native baseline saved separately.')
