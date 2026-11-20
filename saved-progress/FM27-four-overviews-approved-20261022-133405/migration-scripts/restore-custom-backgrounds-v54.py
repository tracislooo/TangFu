import copy,hashlib,json,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy

GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
N='ui-backgrounds_assets_common.bundle'
TARGET=GAME/N
ARCHIVE_SOURCE=R/'HIDEstats十张新版更新-V53'/N
OUT=R/'游戏更新后恢复243张图片-V54'
sha=lambda b:hashlib.sha256(b).hexdigest()
base=TARGET.read_bytes();previous=ARCHIVE_SOURCE.read_bytes()
assert sha(base)=='bd0b3ce77e5694bfad20e0a483380995a4df3121ebdd96970811f7fb8218aa3e'
assert sha(previous)=='d90e0dd98de8c85a5e2208a8a3a4ff82acef81b4e6a8d7c8ec79a93cda54e60c'
assert not OUT.exists(), 'Output folder already exists; do not overwrite a prior recovery package.'
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',GAME/'ui-visualfunctions_assets_all.bundle',GAME.parent/'catalog.bin']}

e=UnityPy.load(base);af=e.assets[0];objects={o.path_id:o for o in e.objects}
oldenv=UnityPy.load(previous);oldobjects={o.path_id:o for o in oldenv.objects}
custom=set(oldobjects)-set(objects)
assert len(custom)==243 and all(oldobjects[i].type.name=='Texture2D' for i in custom)
assert set(objects)<=set(oldobjects)
assert af.name==oldenv.assets[0].name=='CAB-999dbe4fa4e66f3eb4b5f53d4512b8b8'
native_hashes={i:sha(o.get_raw_data()) for i,o in objects.items()}
aux_hashes={name:sha(f.bytes) for name,f in e.file.files.items() if name!=af.name}
externals=[(x.path,x.guid,x.type) for x in af.externals]
bundle=next(o for o in objects.values() if o.type.name=='AssetBundle')
metadata=bundle.read_typetree();original_metadata=copy.deepcopy(metadata)
oldmeta=next(o for o in oldobjects.values() if o.type.name=='AssetBundle').read_typetree()
template=next(o for o in objects.values() if o.type.name=='Texture2D')
native_names={o.peek_name() for o in objects.values() if o.type.name=='Texture2D'}
native_keys={k for k,v in metadata['m_Container']}
names=[oldobjects[i].peek_name() for i in custom]
assert len(set(names))==len(names) and not(set(names)&native_names)
old_keys_by_id={}
for key,entry in oldmeta['m_Container']:
    ptr=entry['asset']
    if ptr['m_FileID']==0 and ptr['m_PathID'] in custom:
        old_keys_by_id.setdefault(ptr['m_PathID'],[]).append((key,entry))
records=[];new_keys=set();source_hashes={}
for index,pid in enumerate(sorted(custom,key=lambda i:oldobjects[i].peek_name().lower()),1):
    src=oldobjects[pid];tree=src.read_typetree()
    assert not tree['m_StreamData']['size'] and not tree['m_StreamData']['path']
    assert src.serialized_type.old_type_hash==template.serialized_type.old_type_hash
    assert pid not in af.objects
    reader=copy.copy(src);reader.assets_file=af;reader.path_id=pid
    reader.type_id=template.type_id;reader.serialized_type=template.serialized_type
    reader.data=None;reader._read_until=None;reader.set_raw_data(src.get_raw_data())
    af.objects[pid]=reader;source_hashes[pid]=sha(src.get_raw_data())
    entries=old_keys_by_id.get(pid,[])
    keys=[k for k,v in entries] or [tree['m_Name'].lower()]
    for key in keys:
        assert key not in native_keys and key not in new_keys, ('Container name collision',key)
        ptr={'m_FileID':0,'m_PathID':pid}
        metadata['m_Container'].append((key,{'preloadIndex':len(metadata['m_PreloadTable']),'preloadSize':1,'asset':copy.deepcopy(ptr)}))
        metadata['m_PreloadTable'].append(ptr);new_keys.add(key)
    records.append({'name':tree['m_Name'],'path_id':pid,'container_names':keys,
                    'size':[tree['m_Width'],tree['m_Height']],'texture_format_id':tree['m_TextureFormat'],
                    'mip_count':tree['m_MipCount'],'source_texture_sha256':source_hashes[pid],
                    'missing_source_container_completed':not bool(entries)})
    if index%50==0:print(f'Restored {index}/243 texture records',flush=True)

metadata['m_Container'].sort(key=lambda x:x[0])
bundle.save_typetree(metadata)
OUT.mkdir()
destination=OUT/N;destination.write_bytes(e.file.save(packer='lz4'))
print('Saved recovery bundle; checking all native and restored assets',flush=True)
check=UnityPy.load(str(destination));saved={o.path_id:o for o in check.objects};caf=check.assets[0]
assert set(saved)==set(objects)|custom
assert caf.name==af.name
assert [(x.path,x.guid,x.type) for x in caf.externals]==externals
for name,h in aux_hashes.items():assert sha(check.file.files[name].bytes)==h,('Native resource file changed',name)
for pid,h in native_hashes.items():
    if pid!=bundle.path_id:assert sha(saved[pid].get_raw_data())==h,('Native asset changed',pid)
assert saved[bundle.path_id].read_typetree()==metadata
containers=dict(metadata['m_Container'])
for key,entry in original_metadata['m_Container']:assert containers[key]==entry
assert metadata['m_PreloadTable'][:len(original_metadata['m_PreloadTable'])]==original_metadata['m_PreloadTable']
for key in original_metadata:
    if key not in ['m_Container','m_PreloadTable']:assert metadata[key]==original_metadata[key]
for index,record in enumerate(records,1):
    pid=record['path_id'];o=saved[pid]
    assert sha(o.get_raw_data())==source_hashes[pid],('Texture payload changed',pid)
    t=o.read_typetree();source_tree=oldobjects[pid].read_typetree();assert t==source_tree
    im=o.read().image.convert('RGBA')
    assert list(im.size)==record['size']
    record.update(decoded_ok=True,decoded_pixel_sha256=sha(im.tobytes()),decoded_alpha_range=list(im.getchannel('A').getextrema()),raw_texture_exact_match=True)
    for key in record['container_names']:
        entry=containers[key]
        assert entry['asset']=={'m_FileID':0,'m_PathID':pid}
        assert metadata['m_PreloadTable'][entry['preloadIndex']]==entry['asset'] and entry['preloadSize']==1
    if index%50==0:print(f'Validated {index}/243 decoded textures',flush=True)
assert TARGET.read_bytes()==base and ARCHIVE_SOURCE.read_bytes()==previous
observed_external_changes=[]
for p,h in protected.items():
    current=sha(p.read_bytes())
    if current!=h:observed_external_changes.append({'path':str(p),'before_sha256':h,'observed_after_sha256':current,'written_by_this_update':False})

(OUT/'回退').mkdir();(OUT/'回退'/N).write_bytes(base)
m={'version':54,'source_new_game_bundle':str(TARGET),'source_new_game_sha256':sha(base),
   'texture_source_bundle':str(ARCHIVE_SOURCE),'texture_source_bundle_sha256':sha(previous),
   'sha256':sha(destination.read_bytes()),'serialized_file':caf.name,'restored_texture_count':len(records),
   'textures':records,'new_native_asset_bytes_preserved':len(native_hashes)-1,
   'new_native_auxiliary_files_sha256':aux_hashes,'native_container_entries_preserved':len(original_metadata['m_Container']),
   'native_preload_table_preserved':True,'added_named_container_entries':len(new_keys),
   'all_source_texture_bytes_exact_match':True,'all_243_textures_decoded':True,
   'protected_files_sha256':{str(p):h for p,h in protected.items()},
   'observed_external_changes':observed_external_changes,
   'old_UI_or_catalog_migrated':False,'installed':False,'game_runtime_verified':False}
(OUT/'恢复与校验记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
mapping='名称\t原Path ID（保留）\t尺寸\t纹理格式ID\t包内资源名\n'+'\n'.join(f"{v['name']}\t{v['path_id']}\t{v['size'][0]}×{v['size'][1]}\t{v['texture_format_id']}\t{','.join(v['container_names'])}" for v in records)
(OUT/'243张图片资源ID对照.txt').write_text(mapping+'\n',encoding='utf-8-sig')
for back in [False,True]:
    src='回退/'+N if back else N;expected=m['sha256'] if back else m['source_new_game_sha256'];final=m['source_new_game_sha256'] if back else m['sha256']
    script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{TARGET}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
$sourceBundle = Join-Path $PSScriptRoot '{src}'
if ((Get-FileHash -LiteralPath $sourceBundle -Algorithm SHA256).Hash.ToLower() -ne '{final}') {{ throw 'Source bundle hash mismatch.' }}
Copy-Item -LiteralPath $sourceBundle -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{final}') {{ throw 'Installed bundle hash mismatch.' }}
Write-Host 'Complete.'
'''
    (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V54：以本次游戏更新后的backgrounds原包为基础，恢复V53中的243张自定义纹理。\n原图名称、Path ID、格式、尺寸、Alpha、mipmap和纹理设置完整保留，未对图片重新编码或压缩；包体使用LZ4重新封装。\n所有243张纹理原始字节与V53来源完全一致，全部已成功解码。\n新版65个原生资源的原始字节和原生.resS数据完整保留；原生目录、预加载和CAB不变，仅扩展自定义图片的资源目录与预加载。\n补齐PlayerTopBackground此前缺少的命名资源记录。\n范围包括101张FitnessPercentRing、25张CA、20张PA、10张HIDEstats、CAPAbg、四张90stats、70张属性徽章、10张等级图及两张PlayerTop图片。\n本次仅恢复backgrounds图片，不恢复旧版卡面、进度条、隐藏属性、体能环的界面关联；不修改gameworld、global、visualfunctions或catalog。\n游戏关闭后运行安装.ps1。回退.ps1恢复本次游戏更新后的原始背景包，不会恢复旧版V53整包。\n资源名、ID和格式请查看243张图片资源ID对照.txt。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'version':54,'restored':len(records),'native_asset_bytes_preserved':len(native_hashes)-1,
                  'native_auxiliary_files_preserved':len(aux_hashes),'added_named_entries':len(new_keys),
                  'all_texture_payloads_exact_match':True,'all_decoded':True,'sha256':m['sha256']},ensure_ascii=False))
