"""Export the live main skin, two complete editions, and three paired font packs."""
from pathlib import Path
import datetime,hashlib,importlib.util,json,struct,sys,zipfile,zlib
ROOT=Path.cwd();read=lambda p:json.loads(p.read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
sys.path.insert(0,str(ROOT/'.codex-deps'))
from UnityPy.files.BundleFile import BundleFile
from UnityPy.streams import EndianBinaryReader
spec=importlib.util.spec_from_file_location('catalog',ROOT/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
aa=Path(read(ROOT/'current-game-location.json')['aa_root'])
assert read(ROOT/'current-sidebar-version.json')['current_game_mode']=='non-sidebar'
delta=Path(sys.argv[1]).resolve();dm=read(delta/'manifest.json')
assert dm['sources_unchanged_verified']
for name,h in dm['source_sha256'].items():assert sha((aa/'StandaloneWindows64'/name).read_bytes())==h,name
assert sha((aa/'catalog.bin').read_bytes())==dm['catalog_source_sha256']
names=set(read(ROOT/'pinned-1-14-update-20261029-122441/manifest.json')['after_sha256'])
names.update(read(ROOT/'main-1-14-rebuild-20261102-101644/manifest.json')['after_sha256'])
base={'aa/StandaloneWindows64/'+n:(aa/'StandaloneWindows64'/n).read_bytes() for n in sorted(names)}
base.update({'aa/'+n:(aa/n).read_bytes() for n in ['catalog.bin','catalog.hash']})
original_hashes={p:sha(b) for p,b in base.items()}
assert base['aa/catalog.hash'].decode().strip()==hashlib.md5(base['aa/catalog.bin']).hexdigest()
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S')
OUT=ROOT/'exports'/('FM27-主皮肤及两套版本与三种字体-'+stamp);OUT.mkdir(parents=True)
crc_cache={}
def crc(data):
    key=sha(data)
    if key in crc_cache:return crc_cache[key]
    reader=EndianBinaryReader(data);bundle=object.__new__(BundleFile)
    bundle.signature=reader.read_string_to_null();bundle.version=reader.read_u_int()
    bundle.version_player=reader.read_string_to_null();bundle.version_engine=reader.read_string_to_null()
    _,blocks=bundle.read_fs(reader)
    crc_cache[key]=zlib.crc32(blocks.bytes)
    return crc_cache[key]

def paired_catalog(catalog,bundles):
    cat=cm.Catalog(catalog);found=set()
    locations={loc:cat.location(loc) for _,ls in cat.keys() for loc, in cat.array(ls,'I')}
    for loc,v in locations.items():
        if not v['type'][1].endswith('IAssetBundleResource'):continue
        name=v['internal'].replace('\\','/').split('/')[-1]
        if name not in bundles:continue
        data=bundles[name];typ,p=cat.unpack(v['raw'][5],'2I');request=list(cat.unpack(p,'5I'))
        request[2:4]=[crc(data),len(data)]
        extra=cat.append(struct.pack('<2I',typ,cat.append(struct.pack('<5I',*request))))
        record=list(v['raw']);record[5]=extra;struct.pack_into('<7I',cat.data,loc,*record);found.add(name)
    assert found==set(bundles)
    return bytes(cat.data)

external={}
cat=cm.Catalog(base['aa/catalog.bin'])
for key,ls in cat.keys():
    for loc, in cat.array(ls,'I'):
        v=cat.location(loc)
        if v['provider']=='SI.Core.LocalAssetProvider':external.setdefault(v['internal'],[]).append(str(key))
external_rows=[dict(path=p,keys=sorted(set(k)),exists=Path(p).is_file()) for p,k in external.items()]
assert all(r['exists'] for r in external_rows)
external_json=json.dumps(external_rows,ensure_ascii=False,indent=2).encode('utf8')
external_note='球场图库、地图等外置图片依然由当前catalog中的原路径读取。本次主文件包附外置资源路径清单。迁移至其他电脑需要另行迁移图片及适配路径。\n'

def save_archive(label,files,note,metadata=None,include_external=False):
    folder=OUT/label;folder.mkdir()
    rows=[]
    for relative,data in files.items():
        p=folder/relative;p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(data)
        rows.append(dict(path=relative,size=len(data),sha256=sha(data)))
    report=dict(files=rows,export_only=True,runtime_tested=False,source=str(aa),details=metadata or {})
    (folder/'文件校验.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
    (folder/'使用说明.txt').write_text(note,'utf-8-sig')
    if include_external:(folder/'外置图片依赖清单.json').write_bytes(external_json)
    dest=OUT/(label+'.zip')
    with zipfile.ZipFile(dest,'x',zipfile.ZIP_DEFLATED,compresslevel=6) as z:
        for p in folder.rglob('*'):
            if p.is_file():z.write(p,p.relative_to(folder))
    with zipfile.ZipFile(dest) as z:
        assert z.testzip() is None
        for row in rows:assert sha(z.read(row['path']))==row['sha256']
    print(json.dumps(dict(file=str(dest),size_mib=round(dest.stat().st_size/2**20,1),files=len(rows)),ensure_ascii=True),flush=True)
    return dict(zip=str(dest),folder=str(folder),files=len(rows),size_mib=round(dest.stat().st_size/2**20,1))

install='退出游戏并备份对应原文件，将所选版本内的aa文件夹合并覆盖至游戏fm_Data/StreamingAssets/。同一套catalog.bin、catalog.hash与资源包配套使用。\n本包对应本次当前游戏版本，游戏更新后须重新适配。文件已离线校验，游戏内效果尚未验证。\n'
results=[];editions={'当前主皮肤':base}
results.append(save_archive('当前主皮肤',base,'当前实际安装的主皮肤，16个游戏文件逐字节提取。\n'+install+external_note,dict(exact_live_snapshot=True),True))
for mode,title in [('portrait','大头像版完整主皮肤'),('fc','FC卡面版完整主皮肤')]:
    patch_report=next(r for r in dm['reports'] if r['edition']==mode)
    source=delta/('大头像版' if mode=='portrait' else 'FC卡面版')
    payloads=dict(base)
    for relative,h in patch_report['sha256'].items():
        data=(source/relative).read_bytes();assert sha(data)==h
        payloads[relative]=data
    bundles={p.split('/')[-1]:b for p,b in payloads.items() if p.endswith('.bundle')}
    catalog=paired_catalog(payloads['aa/catalog.bin'],bundles)
    payloads['aa/catalog.bin']=catalog;payloads['aa/catalog.hash']=hashlib.md5(catalog).hexdigest().encode('ascii')
    # Every bundle apart from the validated page/hover and layout deltas stays exact.
    changed_bundles={p for p in patch_report['sha256'] if p.endswith('.bundle')}
    assert all(data==base[p] for p,data in payloads.items() if p.endswith('.bundle') and p not in changed_bundles)
    short='大头像版' if mode=='portrait' else 'FC卡面版';editions[short]=payloads
    description='保留六种大头像概览，悬浮层使用320×500大头像。' if mode=='portrait' else '保留三种FC卡面概览，悬浮层使用FC卡面。'
    note=description+'\n本包为当前主皮肤基线制作的完整16文件版。\n'+install+external_note+'若旧球员概览布局仍显示，请在游戏内重置对应概览布局后选择版本。\n'
    results.append(save_archive(title,payloads,note,dict(edition=mode,choices=patch_report['choices'],changed_objects=patch_report['changed_objects']),True))

font_root=ROOT/'font-bundle-variants-20261118-020031'
font_results=[]
for name in ['FM圆体','UOS黑体M','霞鹭文楷']:
    font_dir=font_root/name;report=read(font_dir/'manifest.json');fonts={}
    for row in report['bundles']:
        rel='aa/StandaloneWindows64/'+row['name']
        assert original_hashes[rel]==row['before_sha256'],(name,'font source baseline changed')
        data=(font_dir/row['name']).read_bytes();assert sha(data)==row['after_sha256']
        fonts[row['name']]=data
    files={}
    for edition,payloads in editions.items():
        for n,data in fonts.items():files[edition+'/aa/StandaloneWindows64/'+n]=data
        catalog=paired_catalog(payloads['aa/catalog.bin'],fonts)
        files[edition+'/aa/catalog.bin']=catalog
        files[edition+'/aa/catalog.hash']=hashlib.md5(catalog).hexdigest().encode('ascii')
    note='字体 '+name+'\n\n先安装所选主皮肤，再打开本字体包中与之对应的“当前主皮肤”“大头像版”或“FC卡面版”目录，只复制其中一套aa。每套含两个字体bundle及配套catalog.bin、catalog.hash。\n'+install+'这些catalog只配套本次导出的三套主皮肤，后续修改或游戏更新后请重新导出，避免覆盖后续目录变化。\n'
    font_results.append(save_archive('字体-'+name,files,note,dict(font_family=report['font_family'],character_count=report['character_count'],editions=list(editions))))
for p,h in original_hashes.items():assert sha((aa/p[3:]).read_bytes())==h,('Live source changed',p)
summary=dict(main=results,fonts=font_results,game_files_unchanged_verified=True,edition_delta_source=str(delta),external_asset_count=len(external_rows))
(OUT/'导出总清单.json').write_text(json.dumps(summary,ensure_ascii=False,indent=2),'utf8')
(ROOT/'current-main-editions-export.json').write_text(json.dumps(dict(archive=str(OUT),manifest=str(OUT/'导出总清单.json'),verified=True),ensure_ascii=False,indent=2),'utf8')
print('COMPLETE',str(OUT),flush=True)
