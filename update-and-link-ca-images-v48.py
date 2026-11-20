import copy,hashlib,json,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageChops,ImageDraw,ImageStat

GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
BN='ui-backgrounds_assets_common.bundle'
WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
INPUT=Path('K:/桌面/27skin/FcCard/新建文件夹')
OUT=R/'五张CA新版替换并关联游戏卡面-V48'
FULL=-930000000001001
names=['CA000','CA120','CA140','CA160','CA180']
ids={n:-910000000000003-i for i,n in enumerate(names)}
sha=lambda b:hashlib.sha256(b).hexdigest()
before={GAME/BN:(GAME/BN).read_bytes(),GAME/WN:(GAME/WN).read_bytes(),SKIN/WN:(SKIN/WN).read_bytes()}
assert sha(before[GAME/BN])=='4a6ac770b50b6c6e08021a00799d5aec5ebc58b6b7a01e12a0d72e95cc0c2aac'
assert sha(before[GAME/WN])=='1426c06d078c165c6cc928e85c9f4c56cfb551883b061991aaca6a48a23451b5'
assert before[GAME/WN]==before[SKIN/WN]
protected={p:sha(p.read_bytes()) for p in [GAME/GN,SKIN/GN,GAME.parent/'catalog.bin',GAME/'ui-visualfunctions_assets_all.bundle',GAME/'ui-tileslayouts_assets_all.bundle']}
be=UnityPy.load(before[GAME/BN]);bo={o.path_id:o for o in be.objects}
we=UnityPy.load(before[GAME/WN]);wo={o.path_id:o for o in we.objects}
bh={i:sha(o.get_raw_data()) for i,o in bo.items()};wh={i:sha(o.get_raw_data()) for i,o in wo.items()}
doc=wo[FULL].read_typetree();style_id=doc['inlineSheet']['m_PathID'];sheet=wo[style_id].read_typetree()
rr={r['rid']:r for r in doc['references']['RefIds']}
links=[]
for name,pid in ids.items():
    sd=next(r for r in rr.values() if r.get('data',{}).get('name')=='ReportCACardImage'+name)
    node=next(r for r in rr.values() if r.get('data',{}).get('m_SerializedData',{}).get('rid')==sd['rid'])
    ps=sheet['m_Rules'][node['data']['m_RuleIndex']]['m_Properties']
    ptrs=[sheet['assets'][v['valueIndex']] for p in ps if p['m_Id']==458753 for v in p['m_Values'] if v['m_ValueType']==6]
    assert ptrs==[{'m_FileID':0,'m_PathID':pid}]
    links.append({'name':name,'node_name':sd['data']['name'],'serialized_data_rid':sd['rid'],'texture_reference':ptrs[0]})

OUT.mkdir(exist_ok=True);records=[];desired={};previews={};inputs={}
for name,pid in ids.items():
    src=INPUT/(name+'.png');png=src.read_bytes();inputs[src]=sha(png)
    with Image.open(src) as im:im.load();image=im.convert('RGBA')
    old=bo[pid].read_typetree();world_old=wo[pid].read_typetree()
    assert bo[pid].type.name==wo[pid].type.name=='Texture2D'
    assert old['m_Name']==world_old['m_Name']==name
    assert old['m_TextureFormat']==12 and old['m_MipCount']==1
    assert set(old)==set(world_old)
    pixels,fmt=image_to_texture2d(image,12,bo[pid].platform,old['m_PlatformBlob'])
    assert int(fmt)==12 and len(pixels)==((image.width+3)//4)*((image.height+3)//4)*16
    data=copy.deepcopy(old);data.update(m_Width=image.width,m_Height=image.height,m_CompleteImageSize=len(pixels))
    data['image data']=pixels;data['m_StreamData']={'offset':0,'size':0,'path':''}
    bo[pid].save_typetree(data);wo[pid].save_typetree(data);desired[pid]=data
    records.append({'name':name,'path_id':pid,'size':list(image.size),'source_png':str(src),'source_png_sha256':inputs[src],
        'format':'DXT5','source_alpha_range':list(image.getchannel('A').getextrema())})
    previews[name]=image
    (OUT/'源图').mkdir(exist_ok=True);(OUT/'源图'/(name+'.png')).write_bytes(png)

outputs={BN:be.file.save(packer='lz4'),WN:we.file.save(packer='lz4')}
for n,b in outputs.items():(OUT/n).write_bytes(b)
saved_bg={o.path_id:o for o in UnityPy.load(outputs[BN]).objects}
saved_world={o.path_id:o for o in UnityPy.load(outputs[WN]).objects}
for saved,original,hashes in [(saved_bg,bo,bh),(saved_world,wo,wh)]:
    assert set(saved)==set(original)
    for pid,h in hashes.items():
        if pid not in desired:assert sha(saved[pid].get_raw_data())==h,(pid,'Unrelated asset changed')
for rec in records:
    name,pid=rec['name'],rec['path_id'];original=previews[name]
    assert saved_bg[pid].read_typetree()==saved_world[pid].read_typetree()==desired[pid]
    assert saved_bg[pid].get_raw_data()==saved_world[pid].get_raw_data()
    decoded=saved_bg[pid].read().image.convert('RGBA')
    assert decoded.size==original.size
    rms=ImageStat.Stat(ImageChops.difference(decoded,original)).rms
    assert rms[3]<20 and decoded.getchannel('A').getextrema()==original.getchannel('A').getextrema()
    assert sum(rms)<sum(ImageStat.Stat(ImageChops.difference(decoded,original.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms)
    rec.update(texture_sha256=sha(saved_bg[pid].get_raw_data()),decoded_alpha_range=list(decoded.getchannel('A').getextrema()),decoded_rgba_rms_error=[round(v,4) for v in rms])
    assert saved_world[pid].read().image.tobytes()==decoded.tobytes()
    previews[name]=decoded
assert saved_world[FULL].get_raw_data()==wo[FULL].get_raw_data()
assert saved_world[style_id].get_raw_data()==wo[style_id].get_raw_data()
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,h in inputs.items():assert sha(p.read_bytes())==h

preview=Image.new('RGB',(1200,350),'#343434');draw=ImageDraw.Draw(preview)
for i,name in enumerate(names):
    tile=Image.new('RGBA',(220,300));td=ImageDraw.Draw(tile)
    for y in range(0,300,12):
        for x in range(0,220,12):td.rectangle((x,y,x+11,y+11),fill='#d6d6d6' if (x//12+y//12)%2==0 else '#a7a7a7')
    im=previews[name].copy();im.thumbnail((220,300));tile.alpha_composite(im,((220-im.width)//2,(300-im.height)//2))
    preview.paste(tile.convert('RGB'),(10+i*240,40));draw.text((10+i*240,12),name,fill='white')
preview.save(OUT/'背景与游戏卡面共用新版图片解码预览.png')
install=[]
for p,b in before.items():
    tag='skin' if p.parent==SKIN else 'game';backup=Path('回退')/tag/p.name
    (OUT/backup).parent.mkdir(parents=True,exist_ok=True);(OUT/backup).write_bytes(b)
    install.append({'target':str(p),'source':p.name,'backup':backup.as_posix(),'before_sha256':sha(b),'after_sha256':sha(outputs[p.name])})
m={'version':48,'installed':False,'game_runtime_verified':False,'textures':records,'verified_ui_links':links,
   'background_other_assets_unchanged':len(bh)-5,'gameworld_other_assets_unchanged':len(wh)-5,
   'layout_bindings_tier_switches_preserved':True,'background_and_gameworld_texture_bytes_identical':True,
   'install_files':install,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'替换关联记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
for back in [False,True]:
    rows=[]
    for item in install:
        src=item['backup'] if back else item['source'];backup=item['source'] if back else item['backup']
        old=item['after_sha256'] if back else item['before_sha256'];new=item['before_sha256'] if back else item['after_sha256']
        rows.append("    @{ Target = '"+item['target']+"'; Source = '"+src+"'; Backup = '"+backup+"'; Before = '"+old+"'; After = '"+new+"' }")
    script="""$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }
$files = @(
"""+',\n'.join(rows)+"""
)
foreach ($item in $files) {
    if ((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before) { throw ('Bundle version mismatch: ' + $item.Target) }
    if ((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After) { throw 'Source bundle hash mismatch.' }
}
try {
    foreach ($item in $files) {
        Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force
        if ((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After) { throw 'Installed bundle hash mismatch.' }
    }
} catch {
    foreach ($item in $files) { Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Backup) -Destination $item.Target -Force }
    throw
}
Write-Host 'Complete.'
"""
    (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V48：按名称更新最新五张CA000、CA120、CA140、CA160、CA180。\n同步backgrounds与现有gameworld内同名纹理，二者纹理字节完全一致。\n已核对OverviewToggle_FullOverview现有五张卡面图片引用：FileID 0，Path ID -910000000000003至-910000000000007，继续沿用原能力分档切换。\n本次仅改五张纹理，现有卡面、资料栏、数值公式、能力切换、布局、字体与交互引用原始字节均不变。\n图片使用原尺寸754×963及Alpha；包含原图已有的左侧暗色区域，未重新绘制。DXT5存在正常压缩误差。\n安装同时更新游戏backgrounds、游戏gameworld及皮肤工程packages中gameworld。\n退出游戏后运行安装.ps1；回退.ps1同时恢复上述三个文件。已解码和核对资源引用，游戏内显示待实测。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'version':48,'background_sha256':sha(outputs[BN]),'gameworld_sha256':sha(outputs[WN]),'ui_links_verified':len(links),'unchanged_background_assets':len(bh)-5,'unchanged_gameworld_assets':len(wh)-5},ensure_ascii=False))
