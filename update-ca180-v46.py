import copy,hashlib,json,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageChops,ImageStat
WIN=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
N='ui-backgrounds_assets_common.bundle';TARGET=WIN/N
INPUT=Path('C:/Users/traci/AppData/Local/Temp/codex-clipboard-57838e97-7091-44e4-8984-d940a205da61.png')
OUT=R/'CA180黑金卡面更新-V46';PID=-910000000000007
sha=lambda b:hashlib.sha256(b).hexdigest()
source=TARGET.read_bytes();png=INPUT.read_bytes()
assert sha(source)=='6ddf4680d9b6850dc59f43d2ba1f3ccbb35e0f8e3e922a3f7530a750839c007d'
protected={p:sha(p.read_bytes()) for p in [WIN/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',WIN.parent/'catalog.bin']}
e=UnityPy.load(str(TARGET));obs={o.path_id:o for o in e.objects}
hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
matches=[o for o in obs.values() if o.type.name=='Texture2D' and o.peek_name()=='CA180']
assert len(matches)==1 and matches[0].path_id==PID
obj=matches[0];old=obj.read_typetree()
assert old['m_TextureFormat']==12 and old['m_MipCount']==1
with Image.open(INPUT) as im:im.load();image=im.convert('RGBA')
pixels,fmt=image_to_texture2d(image,12,obj.platform,old['m_PlatformBlob'])
assert int(fmt)==12 and len(pixels)==((image.width+3)//4)*((image.height+3)//4)*16
data=copy.deepcopy(old);data.update(m_Width=image.width,m_Height=image.height,m_CompleteImageSize=len(pixels))
data['image data']=pixels;data['m_StreamData']={'offset':0,'size':0,'path':''}
obj.save_typetree(data);OUT.mkdir(exist_ok=True);dest=OUT/N;dest.write_bytes(e.file.save(packer='lz4'))
saved={o.path_id:o for o in UnityPy.load(str(dest)).objects};assert saved.keys()==obs.keys()
for i,h in hashes.items():
 if i!=PID:assert sha(saved[i].get_raw_data())==h,i
assert saved[PID].read_typetree()==data
decoded=saved[PID].read().image.convert('RGBA');assert decoded.size==image.size
rms=ImageStat.Stat(ImageChops.difference(decoded,image)).rms
assert rms[3]<20 and decoded.getchannel('A').getextrema()==image.getchannel('A').getextrema()
assert sum(rms)<sum(ImageStat.Stat(ImageChops.difference(decoded,image.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms)
decoded.save(OUT/'CA180包内解码预览.png');(OUT/'CA180源图.png').write_bytes(png)
assert TARGET.read_bytes()==source and INPUT.read_bytes()==png
for p,h in protected.items():assert sha(p.read_bytes())==h
(OUT/'回退').mkdir(exist_ok=True);(OUT/'回退'/N).write_bytes(source)
m={'version':46,'texture':'CA180','path_id':PID,'source_sha256':sha(source),'sha256':sha(dest.read_bytes()),
   'input_png':str(INPUT),'input_png_sha256':sha(png),'dimensions':list(image.size),'texture_format':'DXT5',
   'source_alpha_range':list(image.getchannel('A').getextrema()),'decoded_alpha_range':list(decoded.getchannel('A').getextrema()),
   'decoded_rgba_rms_error':[round(v,4) for v in rms],'other_resources_unchanged':len(hashes)-1,
   'protected_files':{str(p):h for p,h in protected.items()},'installed':False,'game_runtime_verified':False}
(OUT/'替换记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
for back in [False,True]:
 src='回退/'+N if back else N;expected=m['sha256'] if back else m['source_sha256'];final=m['source_sha256'] if back else m['sha256']
 script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{TARGET}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{final}') {{ throw 'Installed bundle hash mismatch.' }}
Write-Host 'Complete.'
'''
 (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V46：仅更新backgrounds包的CA180为本次最新附件黑金卡面。\n保留名称、Path ID -910000000000007、DXT5、mipmap及其他设置。按原图754×963和透明度导入，未裁剪或重绘图片。\n其余资源原始字节全部一致；其他四张CA卡面保留V45。global与catalog未修改。\n退出游戏后运行安装.ps1；回退.ps1恢复V45背景包。\n已重读成品核对尺寸、方向、透明度及其余资源哈希，游戏内显示待实测。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
 for f in OUT.rglob('*'):
  if f.is_file():z.write(f,f.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps(m,ensure_ascii=True))
