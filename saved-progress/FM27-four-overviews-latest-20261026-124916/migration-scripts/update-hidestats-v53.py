import copy,hashlib,json,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageDraw

N='ui-backgrounds_assets_common.bundle'
SOURCE=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')/N
INPUT=Path('K:/桌面/27skin/capa')
OUT=R/'HIDEstats十张新版更新-V53'
names=[f'HIDEstats{i:02d}' for i in range(1,11)]
sha=lambda b:hashlib.sha256(b).hexdigest()
source=SOURCE.read_bytes()
assert sha(source)=='c0704d073155911b7ad7221e0660438638446fbc2dd6a2c1bbd3c95a81bf42e7'
e=UnityPy.load(source);obs={o.path_id:o for o in e.objects}
hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
original_cab=e.assets[0].name
original_externals=[(x.path,x.guid,x.type) for x in e.assets[0].externals]
records=[];desired={};images={};inputs={}
for index,name in enumerate(names,126):
    matches=[o for o in obs.values() if o.type.name=='Texture2D' and o.peek_name()==name]
    assert len(matches)==1
    o=matches[0];pid=o.path_id;assert pid==-910000000000000-index
    old=o.read_typetree();assert old['m_TextureFormat']==4 and old['m_MipCount']==1
    p=INPUT/(name+'.png');png=p.read_bytes();inputs[p]=sha(png)
    with Image.open(p) as im:im.load();image=im.convert('RGBA')
    pixels,fmt=image_to_texture2d(image,4,o.platform,old['m_PlatformBlob'])
    assert int(fmt)==4 and len(pixels)==image.width*image.height*4
    data=copy.deepcopy(old)
    data.update(m_Width=image.width,m_Height=image.height,m_CompleteImageSize=len(pixels))
    data['image data']=pixels;data['m_StreamData']={'offset':0,'size':0,'path':''}
    o.save_typetree(data);desired[pid]=data;images[pid]=image
    records.append({'name':name,'path_id':pid,'size':list(image.size),'format':'RGBA32','format_id':4,
                    'source_png':str(p),'source_png_sha256':sha(png),'source_alpha_range':list(image.getchannel('A').getextrema())})
OUT.mkdir(exist_ok=True);dest=OUT/N;dest.write_bytes(e.file.save(packer='lz4'))
check=UnityPy.load(str(dest));saved={o.path_id:o for o in check.objects}
assert set(saved)==set(obs)
assert check.assets[0].name==original_cab
assert [(x.path,x.guid,x.type) for x in check.assets[0].externals]==original_externals
for pid,h in hashes.items():
    if pid not in desired:assert sha(saved[pid].get_raw_data())==h,pid
decoded={}
for rec in records:
    pid=rec['path_id'];assert saved[pid].read_typetree()==desired[pid]
    image=saved[pid].read().image.convert('RGBA')
    assert image.size==images[pid].size and image.tobytes()==images[pid].tobytes()
    rec.update(decoded_pixels_exact_match=True,decoded_alpha_range=list(image.getchannel('A').getextrema()))
    decoded[rec['name']]=image
assert SOURCE.read_bytes()==source
for p,h in inputs.items():assert sha(p.read_bytes())==h

preview=Image.new('RGB',(1000,160),'#30343a');draw=ImageDraw.Draw(preview)
for i,name in enumerate(names):
    tile=Image.new('RGBA',(80,100));td=ImageDraw.Draw(tile)
    for yy in range(0,100,10):
        for xx in range(0,80,10):td.rectangle((xx,yy,xx+9,yy+9),fill='#bdbdbd' if (xx//10+yy//10)%2 else '#858585')
    im=decoded[name].resize((20,80),Image.Resampling.NEAREST)
    tile.alpha_composite(im,(30,10));preview.paste(tile.convert('RGB'),(10+i*100,35));draw.text((10+i*100,12),name,fill='white')
preview.save(OUT/'十张新版包内解码预览.png')
(OUT/'回退').mkdir(exist_ok=True);(OUT/'回退'/N).write_bytes(source)
m={'version':53,'source_bundle':str(SOURCE),'source_sha256':sha(source),'sha256':sha(dest.read_bytes()),
   'changed_texture_count':10,'textures':records,'all_decoded_pixels_exact_match':True,
   'other_asset_bytes_unchanged':len(hashes)-10,'container_and_preload_bytes_unchanged':True,
   'resource_names_ids_cab_and_externals_preserved':True,'installed':False,'game_runtime_verified':False}
(OUT/'替换与校验记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
mapping='名称\t原Path ID（保留）\t尺寸\t格式\n'+'\n'.join(f"{r['name']}\t{r['path_id']}\t{r['size'][0]}×{r['size'][1]}\tRGBA32" for r in records)
(OUT/'资源ID对照.txt').write_text(mapping+'\n',encoding='utf-8-sig')
for back in [False,True]:
    src='回退/'+N if back else N;old=m['sha256'] if back else m['source_sha256'];new=m['source_sha256'] if back else m['sha256']
    script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{SOURCE}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{old}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{new}') {{ throw 'Installed bundle hash mismatch.' }}
Write-Host 'Complete.'
'''
    (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V53：按名称替换当前backgrounds中的HIDEstats01～HIDEstats10，共10张。\n使用本次新版PNG的5×20原尺寸和Alpha，RGBA32无损格式；保存后解码全部像素与原PNG逐字节一致。\n原名称、Path ID -910000000000126至-910000000000135、CAB、纹理采样设置、容器及预加载均保持不变，已有图片引用继续适用。\n当前backgrounds中的其余全部资源原始字节保持不变，包括CA/PA标记、CAPAbg、五张卡面及其他图片。\n只更新backgrounds，未复制图片至gameworld，未修改界面逻辑、布局或catalog。\n退出游戏后运行安装.ps1；回退.ps1恢复本次替换前的背景包。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'version':53,'sha256':m['sha256'],'replaced':10,'other_assets_unchanged':m['other_asset_bytes_unchanged'],'all_pixels_exact_match':True},ensure_ascii=False))
