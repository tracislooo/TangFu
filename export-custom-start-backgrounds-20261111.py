import copy, hashlib, json, sys
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image, ImageOps
sha=lambda b:hashlib.sha256(b).hexdigest()
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
BN='ui-backgrounds_assets_common.bundle'; PID=-910000000000145
base=Path(loc['bundle_root'])/BN; raw=base.read_bytes()
outroot=R/'exports/主页面背景定制-20261111'
assert not outroot.exists()
banned={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}|{-910000000000001,-910000000000002,-910000000000146}
reports=[]
for name,ext in [('朗尼克','jpg'),('王沐川','jpg'),('绿船','png')]:
 src=Path('K:/桌面/27skin/PICTURE/定制')/(name+'.'+ext)
 with Image.open(src) as img: im=ImageOps.exif_transpose(img).convert('RGBA')
 env=UnityPy.load(raw); a=env.assets[0]; obj=a.objects[PID]
 assert obj.peek_name()=='kunshan stadium'
 oldhash={i:sha(o.get_raw_data()) for i,o in a.objects.items() if i!=PID}
 t=copy.deepcopy(obj.read_typetree())
 pixels,fmt=image_to_texture2d(im,4,obj.platform,t['m_PlatformBlob'])
 assert int(fmt)==4
 t.update(m_TextureFormat=4,m_Width=im.width,m_Height=im.height,m_CompleteImageSize=len(pixels),m_MipCount=1)
 t['image data']=pixels; t['m_StreamData']={'offset':0,'size':0,'path':''}
 obj.save_typetree(t); data=env.file.save(packer='lz4')
 check=UnityPy.load(data); ca=check.assets[0]
 assert ca.name==a.name and set(ca.objects)==set(a.objects)
 assert all(sha(ca.objects[i].get_raw_data())==h for i,h in oldhash.items())
 assert ca.objects[PID].peek_name()=='kunshan stadium'
 assert ca.objects[PID].read().image.convert('RGBA').tobytes()==im.tobytes()
 assert banned.isdisjoint(ca.objects)
 meta=next(o.read_typetree() for o in ca.objects.values() if o.type.name=='AssetBundle')
 assert all(p['m_PathID'] not in banned for p in meta['m_PreloadTable'])
 assert all(v['asset']['m_PathID'] not in banned for k,v in meta['m_Container'])
 ent=dict(meta['m_Container'])['kunshan stadium']
 assert ent['asset']=={'m_FileID':0,'m_PathID':PID}
 for k,f in env.file.files.items():
  if k!=a.name: assert check.file.files[k].bytes==f.bytes
 folder=outroot/name;folder.mkdir(parents=True)
 dest=folder/BN;dest.write_bytes(data)
 assert sha(dest.read_bytes())==sha(data)
 reports.append(dict(name=name,file=str(dest),source=str(src),size=list(im.size),sha256=sha(data),source_sha256=sha(src.read_bytes()),other_objects_unchanged=True,lossless_pixels_verified=True))
 print(name,im.size,'VERIFIED',flush=True)
assert base.read_bytes()==raw
(outroot/'manifest.json').write_text(json.dumps(dict(base=str(base),base_sha256=sha(raw),texture='kunshan stadium',path_id=str(PID),installed=False,runtime_verified=False,variants=reports),ensure_ascii=False,indent=2),'utf8')
(outroot/'替换说明.txt').write_text('三份为互斥版本，每位用户只选自己文件夹内的 ui-backgrounds_assets_common.bundle。\n退出游戏，备份原文件，再覆盖至：\n'+str(base.parent)+'\n适用于当前已经关联 kunshan stadium 的唐夫皮肤。菜单文件无需更换。\n保留原图尺寸，游戏按现有等比裁切铺满规则显示。朗尼克原图为3:2，宽屏会裁切上下部分。\n本次未安装或修改本机游戏、主皮肤、资源索引；仅导出三份背景包。\n文件基于本次当前背景包，后续皮肤更新后应重新制作，避免覆盖新版其他纹理。\n','utf-8-sig')
print(str(outroot))
