import copy, hashlib, json, sys, zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageChops,ImageDraw,ImageStat

N='ui-backgrounds_assets_common.bundle'
WIN=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SOURCE=WIN/N
INPUT=Path('K:/桌面/27skin/FcCard/新建文件夹')
OUT=R/'五张CA卡面同名更新-V45'
NAMES=['CA000','CA120','CA140','CA160','CA180']
sha=lambda b:hashlib.sha256(b).hexdigest()
source=SOURCE.read_bytes()
assert sha(source)=='69fb429f92f600ddfdf640db8c3c20d253f56a16db451312566371f326c27991'
global_path=WIN/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
global_hash=sha(global_path.read_bytes())
catalog=WIN.parent/'catalog.bin';catalog_hash=sha(catalog.read_bytes())
env=UnityPy.load(str(SOURCE));obs={o.path_id:o for o in env.objects}
hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
records=[];desired={};images={};previews={};input_hashes={}
for index,name in enumerate(NAMES,3):
    matches=[o for o in obs.values() if o.type.name=='Texture2D' and o.peek_name()==name]
    assert len(matches)==1
    obj=matches[0];pid=obj.path_id;assert pid==-910000000000000-index
    old=obj.read_typetree();assert old['m_TextureFormat']==12 and old['m_MipCount']==1
    path=INPUT/(name+'.png');input_hashes[path]=sha(path.read_bytes())
    with Image.open(path) as im:im.load();image=im.convert('RGBA')
    pixels,fmt=image_to_texture2d(image,12,obj.platform,old['m_PlatformBlob'])
    assert int(fmt)==12 and len(pixels)==((image.width+3)//4)*((image.height+3)//4)*16
    data=copy.deepcopy(old)
    data.update(m_Width=image.width,m_Height=image.height,m_CompleteImageSize=len(pixels))
    data['image data']=pixels;data['m_StreamData']={'offset':0,'size':0,'path':''}
    for k in old:
        if k not in ['m_Width','m_Height','m_CompleteImageSize','image data','m_StreamData']:
            assert data[k]==old[k]
    obj.save_typetree(data);desired[pid]=data;images[pid]=image
    records.append({'name':name,'path_id':pid,'old_size':[old['m_Width'],old['m_Height']],
        'new_size':list(image.size),'format':'DXT5','format_id':12,'source_png':str(path),
        'source_png_sha256':input_hashes[path],'source_alpha_range':list(image.getchannel('A').getextrema())})

OUT.mkdir(exist_ok=True);dest=OUT/N;dest.write_bytes(env.file.save(packer='lz4'))
checked={o.path_id:o for o in UnityPy.load(str(dest)).objects}
assert checked.keys()==obs.keys()
for pid,h in hashes.items():
    if pid not in desired:assert sha(checked[pid].get_raw_data())==h,pid
for rec in records:
    pid=rec['path_id'];assert checked[pid].read_typetree()==desired[pid]
    original=images[pid];decoded=checked[pid].read().image.convert('RGBA')
    assert decoded.size==original.size
    rms=ImageStat.Stat(ImageChops.difference(decoded,original)).rms
    flipped=ImageStat.Stat(ImageChops.difference(decoded,original.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms
    assert sum(rms)<sum(flipped) and rms[3]<20
    assert decoded.getchannel('A').getextrema()==(0,255)
    rec.update(decoded_alpha_range=list(decoded.getchannel('A').getextrema()),decoded_rgba_rms_error=[round(x,4) for x in rms])
    previews[rec['name']]=decoded
assert SOURCE.read_bytes()==source
assert sha(global_path.read_bytes())==global_hash and sha(catalog.read_bytes())==catalog_hash
for path,h in input_hashes.items():assert sha(path.read_bytes())==h

preview=Image.new('RGB',(1200,350),'#343434');draw=ImageDraw.Draw(preview)
for index,name in enumerate(NAMES):
    tile=Image.new('RGBA',(220,300));painter=ImageDraw.Draw(tile)
    for y in range(0,300,12):
        for x in range(0,220,12):
            color='#d6d6d6' if (x//12+y//12)%2==0 else '#a7a7a7'
            painter.rectangle((x,y,x+11,y+11),fill=color)
    im=previews[name].copy();im.thumbnail((220,300));tile.alpha_composite(im,((220-im.width)//2,(300-im.height)//2))
    x=10+index*240;preview.paste(tile.convert('RGB'),(x,40));draw.text((x,12),name+' / 754x963',fill='white')
preview.save(OUT/'包内五张CA卡面解码预览.png')
(OUT/'回退').mkdir(exist_ok=True);(OUT/'回退'/N).write_bytes(source)
m={'version':45,'source_bundle':str(SOURCE),'source_sha256':sha(source),'sha256':sha(dest.read_bytes()),
   'replaced_texture_count':5,'textures':records,'other_resources_unchanged':len(hashes)-5,
   'resource_names_and_ids_preserved':True,'global_unchanged_sha256':global_hash,
   'catalog_unchanged_sha256':catalog_hash,'installed':False,'game_runtime_verified':False}
(OUT/'替换记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
for back in [False,True]:
    src='回退/'+N if back else N;expected=m['sha256'] if back else m['source_sha256']
    final=m['source_sha256'] if back else m['sha256']
    script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{SOURCE}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{final}') {{ throw 'Installed bundle hash mismatch.' }}
Write-Host 'Complete.'
'''
    (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V45：使用本次五张PNG更新backgrounds bundle中的同名CA000、CA120、CA140、CA160、CA180。\n原资源名称及Path ID -910000000000003至-910000000000007保留，无需改已有引用。\n图片按754×963原尺寸和Alpha导入，DXT5、单级mipmap及其余设置保留；DXT5存在正常压缩误差。\n仅替换背景包这五张纹理，其他图片、AssetBundle目录和预加载数据逐一核对原始字节不变。\n当前global bundle中没有这五个同名纹理，因此未改global；界面逻辑、布局和catalog保持不变。\n预览来自成品bundle解码，棋盘底仅用于显示透明区域。源PNG保留。\n退出游戏后运行安装.ps1；回退.ps1恢复更新前的背景包。游戏内显示待实测。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'sha256':m['sha256'],'count':5,'dimensions':[754,963],'other_resources_unchanged':m['other_resources_unchanged'],'global_unchanged':True}))
