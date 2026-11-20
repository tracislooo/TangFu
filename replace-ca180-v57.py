import copy,datetime,hashlib,json,struct,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageChops,ImageStat
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
N='ui-backgrounds_assets_common.bundle';PID=-910000000000007;SRC=Path('K:/桌面/27skin/PICTURE/CA180.png');OUT=R/'CA180新版替换并核对引用-V57-20261027'
assert not OUT.exists();sha=lambda b:hashlib.sha256(b).hexdigest()
before={p:(p/N).read_bytes() for p in [G,S]};assert before[G]==before[S]
protected={p:sha(p.read_bytes()) for p in [G.parent/'catalog.bin',G/'ui-visualfunctions_assets_all.bundle',G/'ui-tileslayouts_assets_all.bundle']}
for folder in [G,S]:
 for n in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:protected[folder/n]=sha((folder/n).read_bytes())
current=json.loads((R/'current-custom-textures.json').read_text('utf8'));reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'));retired={int(t['path_id']) for t in reserved['reserved_textures']}
e=UnityPy.load(before[G]);a=e.assets[0];obs=a.objects;hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
assert not (retired&set(obs));assert obs[PID].peek_name()=='CA180';assert all(int(t['path_id']) in obs for t in current['textures'])
aux={k:sha(v.bytes) for k,v in e.file.files.items() if k!=a.name}
png=SRC.read_bytes()
with Image.open(SRC) as im:image=im.convert('RGBA')
t=obs[PID].read_typetree();desired=copy.deepcopy(t);assert t['m_TextureFormat']==12 and t['m_MipCount']==1
pixels,fmt=image_to_texture2d(image,12,obs[PID].platform,t['m_PlatformBlob']);assert int(fmt)==12
desired.update(m_Width=image.width,m_Height=image.height,m_CompleteImageSize=len(pixels));desired['image data']=pixels;desired['m_StreamData']={'offset':0,'size':0,'path':''};obs[PID].save_typetree(desired)
data=e.file.save(packer='lz4');check=UnityPy.load(data);ca=check.assets[0];assert set(ca.objects)==set(hashes) and ca.name==a.name
for i,h in hashes.items():
 if i!=PID:assert sha(ca.objects[i].get_raw_data())==h
for k,h in aux.items():assert sha(check.file.files[k].bytes)==h
obj=ca.objects[PID];assert obj.read_typetree()==desired
decoded=obj.read().image.convert('RGBA');rms=ImageStat.Stat(ImageChops.difference(image,decoded)).rms
assert decoded.size==image.size and decoded.getchannel('A').getextrema()==image.getchannel('A').getextrema()
assert rms[3]<20 and sum(rms)<sum(ImageStat.Stat(ImageChops.difference(image.transpose(Image.Transpose.FLIP_TOP_BOTTOM),decoded)).rms)
texturehash=sha(obj.get_raw_data());links=[];needle=struct.pack('<q',PID)
for folder in [G,S]:
 for name in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
  p=folder/name;u=UnityPy.load(p.read_bytes(),data);af=next(x for x in u.assets if x.name!=a.name)
  external=[i+1 for i,x in enumerate(af.externals) if x.path==f'archive:/{a.name}/{a.name}']
  assert PID not in af.objects, 'Old local CA180 copy found'
  for o in af.objects.values():
   if needle not in o.get_raw_data():continue
   tree=o.read_typetree()
   def walk(v,path=''):
    if isinstance(v,dict):
     if v.get('m_PathID')==PID and 'm_FileID' in v:
      assert v['m_FileID'] in external
      resolved=PPtr(m_FileID=v['m_FileID'],m_PathID=PID,assetsfile=af).deref()
      assert resolved.assets_file.name==a.name and sha(resolved.get_raw_data())==texturehash
      links.append({'bundle':str(p),'object_path_id':str(o.path_id),'object_name':o.peek_name(),'field':path,'m_FileID':v['m_FileID'],'m_PathID':str(PID),'resolved_texture_sha256':texturehash})
     for k,x in v.items():walk(x,path+'/'+k)
    elif isinstance(v,(list,tuple)):
     for i,x in enumerate(v):walk(x,path+'/'+str(i))
   walk(tree)
assert len([x for x in links if Path(x['bundle']).parent==G])>=11
OUT.mkdir();(OUT/N).write_bytes(data);(OUT/'源PNG').mkdir();(OUT/'源PNG'/'CA180.png').write_bytes(png)
decoded.save(OUT/'CA180成品解码预览.png')
installs=[]
for folder,b in before.items():
 rel=Path('回退')/('game' if folder==G else 'skin')/N;(OUT/rel).parent.mkdir(parents=True,exist_ok=True);(OUT/rel).write_bytes(b)
 installs.append({'target':str(folder/N),'source':N,'backup':rel.as_posix(),'before_sha256':sha(b),'after_sha256':sha(data)})
manifest={'version':57,'date':'2026-10-27','installed':False,'game_runtime_verified':False,'source_png':str(SRC),'source_png_sha256':sha(png),'name':'CA180','path_id':str(PID),'size':list(image.size),'format':'DXT5','decoded_alpha_range':list(decoded.getchannel('A').getextrema()),'rgba_rms_error':rms,'texture_sha256':texturehash,'previous_texture_sha256':hashes[PID],'other_background_objects_unchanged':len(hashes)-1,'verified_references':links,'protected_sha256':{str(p):h for p,h in protected.items()},'install_files':installs,'active_custom_texture_count':173,'retired_ids_still_unoccupied':True}
(OUT/'替换及引用校验记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
for back in [False,True]:
 entries=[{'Target':x['target'],'Source':x['backup'] if back else N,'Before':x['after_sha256'] if back else x['before_sha256'],'After':x['before_sha256'] if back else x['after_sha256']} for x in installs]
 rows='\n'.join('@{'+ ';'.join(k+"='"+v+"'" for k,v in x.items())+'}' for x in entries)
 script="""$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
"""+rows+"""
)
foreach($item in $items){if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before){throw 'Target version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Source hash mismatch.'}}
$written=@()
try{foreach($item in $items){$written+=@{Target=$item.Target;Bytes=[IO.File]::ReadAllBytes($item.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force;if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Installed hash mismatch.'}}}catch{foreach($entry in $written){[IO.File]::WriteAllBytes($entry.Target,$entry.Bytes)};throw}
Write-Output 'Complete.'
"""
 (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,'utf-8-sig')
(OUT/'说明.txt').write_text('V57：只替换 CA180，原名称及 Path ID -910000000000007 保留。按源 PNG 尺寸及透明度导入，保持 DXT5 单级 mipmap；DXT5 有正常压缩误差。\n游戏及皮肤目录同步。所有现存 CA180 图片指针均逐一解析并核对成品纹理哈希，没有 gameworld/global 本地旧卡面副本。界面包、布局及其他图片保持不变。\n永久停用的70个 ID 仍未占用；有效自定义图片仍为173张。\n安装前关闭游戏；本目录含原包备份、安装回退脚本及引用校验。游戏内渲染待启动后确认。','utf-8-sig')
for p,h in protected.items():assert sha(p.read_bytes())==h
for folder,b in before.items():assert (folder/N).read_bytes()==b
assert sha(SRC.read_bytes())==sha(png)
print(json.dumps({'output':str(OUT),'texture_changed':texturehash!=hashes[PID],'reference_count_game_and_skin':len(links),'bundle_sha256':sha(data),'rgba_rms_error':rms},ensure_ascii=False),flush=True)
