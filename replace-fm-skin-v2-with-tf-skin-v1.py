"""Use the existing TF skin V1 pixels under the native fm-skin-v2 identity."""
from pathlib import Path
import copy,datetime,json,sys
R=Path(__file__).resolve().parent
# Current bundles, latest registry, retired textures and both catalogs are audited.
# Execute definitions/audit only, not the historical hover patch or its installer.
code=(R/'fix-primary-navigation-hover-brightness.py').read_text('utf8').split('payloads={};changes={}')[0]
code=code.replace("S='ui-styles_assets_default.bundle';BG=", "S='ui-backgrounds_assets_common.bundle';BG=")
exec(compile(code,'<current-background-and-catalog-audit>','exec'))
TARGET=-8106300765064621370;SOURCE=-910000000000149
assert TARGET not in banned and SOURCE not in banned
assert before[GAME/S]==before[SKIN/S]
assert sha(before[GAME/S])==registry['source_bundle_sha256'],'Latest source registry must match installed background bundle'
e=UnityPy.load(before[GAME/S]);a=e.assets[0];oo=a.objects
assert oo[TARGET].type.name==oo[SOURCE].type.name=='Texture2D'
assert oo[TARGET].peek_name()=='fm-skin-v2' and oo[SOURCE].peek_name()=='TF skin V1'
hashes={pid:sha(ob.get_raw_data()) for pid,ob in oo.items()}
aux={k:sha(v.bytes) for k,v in e.file.files.items() if k!=a.name}
original=oo[TARGET].read_typetree();src=oo[SOURCE].read_typetree()
replacement=copy.deepcopy(src);replacement['m_Name']=original['m_Name']
assert replacement['m_StreamData']=={'offset':0,'size':0,'path':''}
assert src['m_Width']==2668 and src['m_Height']==1500
# The native background is a texture, not an atlas sprite with an old fixed rect.
for ob in oo.values():
 if ob.type.name=='Sprite':
  sprite=ob.read_typetree()
  assert sprite.get('m_RD',{}).get('texture',{}).get('m_PathID')!=TARGET,'Native Sprite rect requires separate migration'
oo[TARGET].save_typetree(replacement)
payload=e.file.save(packer='lz4');saved=UnityPy.load(payload);sa=saved.assets[0];so=sa.objects
assert sa.name==a.name and set(so)==set(hashes)
for pid,ob in so.items():
 if pid==TARGET:assert ob.read_typetree()==replacement
 else:assert sha(ob.get_raw_data())==hashes[pid],('Unrelated background resource changed',pid)
for k,h in aux.items():assert sha(saved.file.files[k].bytes)==h,('Native stream changed',k)
out_image=so[TARGET].read().image.convert('RGBA');source_image=so[SOURCE].read().image.convert('RGBA')
assert out_image.size==source_image.size and out_image.tobytes()==source_image.tobytes()
assert so[TARGET].read_typetree()['image data']==src['image data']
for t in registry['textures']:
 ob=so[int(t['path_id'])];assert ob.peek_name()==t['name'] and sha(ob.get_raw_data())==t['texture_sha256'],t['name']
meta=next(ob.read_typetree() for ob in so.values() if ob.type.name=='AssetBundle')
assert banned.isdisjoint(so)
assert all(v['asset']['m_PathID'] not in banned and k.lower() not in bnames for k,v in meta['m_Container'])
assert all(v['m_PathID'] not in banned for v in meta['m_PreloadTable'])
target_keys=[k for k,v in meta['m_Container'] if v['asset']['m_FileID']==0 and v['asset']['m_PathID']==TARGET]
assert target_keys

stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('fm-skin-v2-to-TF-skin-V1-'+stamp);out.mkdir()
regpath=R/'current-custom-textures.json';instructions=R/'AGENTS.md'
before[regpath]=regpath.read_bytes();before[instructions]=instructions.read_bytes()
updated=copy.deepcopy(registry)
updated.update(version=registry['version']+1,date='2026-10-29',authoritative_source_bundle=str(out/'game'/BG),
 source_bundle_sha256=sha(payload),manifest=str(out/'manifest.json'))
updated['native_background_override']={'name':'fm-skin-v2','path_id':str(TARGET),'source_texture':'TF skin V1',
 'source_path_id':str(SOURCE),'native_texture_sha256':sha(so[TARGET].get_raw_data()),'source_texture_sha256':hashes[SOURCE],
 'size':[src['m_Width'],src['m_Height']],'encoded_pixels_copied_without_recompression':True,'container_and_preload_unchanged':True}
note='\n- fm-skin-v2 默认背景已改用 `TF skin V1` 的现有图像数据；原生名称 `fm-skin-v2` 及 Path ID `-8106300765064621370` 保持不变，源纹理 `TF skin V1`（`-910000000000149`）原样保留。更新后在新版原生背景包上重做该替换，不能仅迁移自定义纹理而遗漏此原生背景覆盖。\n'
updated_instructions=instructions.read_text('utf8')
updated_instructions=updated_instructions.replace('- V66 新增纹理 `TF skin V1`，Path ID `-910000000000149`，须沿用；本次仅加入 backgrounds，未设置界面关联。',
 '- V66 新增纹理 `TF skin V1`，Path ID `-910000000000149`，须沿用；现已用于替换原生 `fm-skin-v2` 的图像数据，源纹理本身保持原样。')+note
outputs={GAME/BG:payload,SKIN/BG:payload,regpath:json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8'),instructions:updated_instructions.encode('utf8')}
for p in [regpath,instructions]:protected.pop(str(p),None)
for p,b in before.items():assert p.read_bytes()==b,p
for p,h in protected.items():assert sha(Path(p).read_bytes())==h,p
sources={};backups={}
for path,raw in outputs.items():
 tag='game' if path.parent==GAME else 'skin' if path.parent==SKIN else 'workspace'
 (out/tag).mkdir(exist_ok=True);(out/('backup-'+tag)).mkdir(exist_ok=True)
 source=out/tag/path.name;source.write_bytes(raw);backup=out/('backup-'+tag)/path.name;backup.write_bytes(before[path])
 sources[str(path)]=str(source);backups[str(path)]=str(backup)
out_image.save(out/'fm-skin-v2-replaced-preview.png')
verification={'source':'TF skin V1','source_path_id':str(SOURCE),'target':'fm-skin-v2','target_path_id':str(TARGET),
 'size':list(out_image.size),'texture_format':src['m_TextureFormat'],'encoded_data_byte_identical_to_source':True,
 'decoded_pixels_identical_to_source':True,'custom_texture_count':len(registry['textures']),
 'all_current_custom_textures_unchanged':True,'unrelated_background_objects_unchanged':len(hashes)-1,
 'container_preload_and_native_streams_unchanged':True,'native_container_keys':target_keys,
 'reserved_70_absent':True,'removed_TF_patch_absent':-910000000000146 not in so,
 'catalog_audits':audits,'runtime_verified':False}
assert verification['removed_TF_patch_absent']
m={'installed':False,'runtime_verified':False,'before_sha256':{str(p):sha(before[p]) for p in outputs},
 'after_sha256':{str(p):sha(raw) for p,raw in outputs.items()},'protected_sha256':protected,'verification':verification}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(out/'verification.json').write_text(json.dumps(verification,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'workspace':str(R),
 'sources':sources,'before':backups},ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-primary-navigation-patch.py').read_text('utf8')
old='[Path(tx[\'game\']).resolve(),Path(tx[\'skin\']).resolve()]'
assert old in installer
installer=installer.replace(old,'[Path(tx[\'game\']).resolve(),Path(tx[\'skin\']).resolve(),Path(tx[\'workspace\']).resolve()]')
(out/'installer.py').write_text(installer,'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(out/'说明.md').write_text('将原生 fm-skin-v2（-8106300765064621370）的图像内容替换为已存在的 TF skin V1（-910000000000149）。直接复制已打包的 DXT5 编码数据，保留2668×1500原尺寸，不重压缩、不裁切；保留原生纹理名称、Path ID、目录和预加载记录，因此原有 fm-skin-v2 引用自动获得新图。\n源 TF skin V1 对象及其他所有自定义图片、原生对象和资源流不变，不新增纹理对象或重新分配 ID。背景包游戏/皮肤同步安装；同步更新 current-custom-textures.json 的恢复来源以及 AGENTS.md 的背景覆盖记录。\n只影响原来使用 fm-skin-v2 的背景，不强制覆盖赛事专用背景或3D场景；不替换 background-base-layer。\n退出游戏后 install.ps1 安装；restore.ps1 在哈希匹配时回退本次背景、清单和说明规则。文件校验通过；游戏内显示需启动确认。','utf8')
print(json.dumps({'prepared':True,'output':str(out),'size':list(out_image.size),'custom_textures_unchanged':len(registry['textures']),
 'native_target_keys':target_keys,'catalog_audits':audits,'runtime_verified':False},ensure_ascii=False),flush=True)
