import copy,hashlib,json,sys,zipfile
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageDraw

GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
N='ui-backgrounds_assets_common.bundle';SOURCE=GAME/N
INPUT=Path('K:/桌面/27skin/capa')
OUT=R/'backgrounds新增44张CAPA与隐藏属性图-V51'
NAMES=[f'PA{i:02d}' for i in range(1,21)]+[f'CA{i:02d}' for i in range(8,21)]+['CAPAbg']+[f'HIDEstats{i:02d}' for i in range(1,11)]
sha=lambda b:hashlib.sha256(b).hexdigest()
source=SOURCE.read_bytes()
assert sha(source)=='c2941b12696bbc8ff4048c2b0c39dde242c8f168428d70f4c8b42e15d1bd0a90'
protected={p:sha(p.read_bytes()) for p in [GAME/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',GAME/'ui-visualfunctions_assets_all.bundle',GAME.parent/'catalog.bin']}
env=UnityPy.load(source);objects={o.path_id:o for o in env.objects}
hashes={i:sha(o.get_raw_data()) for i,o in objects.items()}
template=objects[-910000000000001];af=template.assets_file;td=template.read_typetree()
assert td['m_MipCount']==1 and not td['m_PlatformBlob']
externals=[(x.path,x.guid,x.type) for x in af.externals]
bundle=next(o for o in objects.values() if o.type.name=='AssetBundle')
meta=bundle.read_typetree();oldmeta=copy.deepcopy(meta)
existing_names={o.peek_name() for o in objects.values() if o.type.name=='Texture2D'}
existing_keys={k for k,v in meta['m_Container']}
assert len(NAMES)==44 and not(existing_names&set(NAMES))
assert not(existing_keys&{n.lower() for n in NAMES})
desired={};images={};records=[];input_hashes={}
custom=[pid for pid,o in objects.items() if o.type.name=='Texture2D' and -910000000010000<pid<=-910000000000000]
next_id=min(custom)-1
for name in NAMES:
    path=INPUT/(name+'.png');png=path.read_bytes();input_hashes[path]=sha(png)
    with Image.open(path) as im:im.load();image=im.convert('RGBA')
    pixels,fmt=image_to_texture2d(image,4,template.platform,td['m_PlatformBlob'])
    assert int(fmt)==4 and len(pixels)==image.width*image.height*4
    pid=next_id;next_id-=1;assert pid not in af.objects
    data=copy.deepcopy(td)
    data.update(m_Name=name,m_Width=image.width,m_Height=image.height,m_TextureFormat=4,
                m_CompleteImageSize=len(pixels),m_IsAlphaChannelOptional=False)
    data['image data']=pixels;data['m_StreamData']={'offset':0,'size':0,'path':''}
    obj=copy.copy(template);obj.path_id=pid;obj.data=None;obj._read_until=None
    obj.save_typetree(data);af.objects[pid]=obj
    ptr={'m_FileID':0,'m_PathID':pid}
    meta['m_Container'].append((name.lower(),{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':1,'asset':copy.deepcopy(ptr)}))
    meta['m_PreloadTable'].append(ptr)
    desired[pid]=data;images[pid]=image
    records.append({'name':name,'path_id':pid,'container_name':name.lower(),'size':list(image.size),
                    'format':'RGBA32','format_id':4,'source_png_sha256':input_hashes[path],
                    'source_alpha_range':list(image.getchannel('A').getextrema())})
meta['m_Container'].sort(key=lambda x:x[0]);bundle.save_typetree(meta)
OUT.mkdir(exist_ok=True);dest=OUT/N;dest.write_bytes(env.file.save(packer='lz4'))
saved_env=UnityPy.load(str(dest));saved={o.path_id:o for o in saved_env.objects}
assert set(saved)==set(objects)|set(desired)
for pid,h in hashes.items():
    if pid!=bundle.path_id:assert sha(saved[pid].get_raw_data())==h,pid
assert saved[bundle.path_id].read_typetree()==meta
assert dict(meta['m_Container'])|dict(oldmeta['m_Container'])==dict(meta['m_Container'])
assert meta['m_PreloadTable'][:len(oldmeta['m_PreloadTable'])]==oldmeta['m_PreloadTable']
assert [(x.path,x.guid,x.type) for x in saved_env.assets[0].externals]==externals
assert saved_env.assets[0].name==af.name
decoded={};containers=dict(meta['m_Container'])
for rec in records:
    pid=rec['path_id'];assert saved[pid].read_typetree()==desired[pid]
    image=saved[pid].read().image.convert('RGBA')
    assert image.size==images[pid].size and image.tobytes()==images[pid].tobytes(),rec['name']
    info=containers[rec['container_name']]
    assert info['asset']=={'m_FileID':0,'m_PathID':pid}
    assert meta['m_PreloadTable'][info['preloadIndex']]==info['asset'] and info['preloadSize']==1
    rec.update(decoded_alpha_range=list(image.getchannel('A').getextrema()),decoded_pixels_exact_match=True)
    decoded[rec['name']]=image
for p,h in input_hashes.items():assert sha(p.read_bytes())==h,p
assert SOURCE.read_bytes()==source
for p,h in protected.items():assert sha(p.read_bytes())==h,p

# Display the exact decoded pixels on a checkerboard, enlarged only for the overview.
preview=Image.new('RGB',(980,850),'#30343a');draw=ImageDraw.Draw(preview)
for i,rec in enumerate(records):
    x=12+(i%4)*244;y=12+(i//4)*76
    tile=Image.new('RGBA',(220,48));paint=ImageDraw.Draw(tile)
    for yy in range(0,48,8):
        for xx in range(0,220,8):paint.rectangle((xx,yy,xx+7,yy+7),fill='#bdbdbd' if (xx//8+yy//8)%2 else '#858585')
    im=decoded[rec['name']]
    if im.width==5:im=im.resize((10,40),Image.Resampling.NEAREST)
    tile.alpha_composite(im,((220-im.width)//2,(48-im.height)//2))
    preview.paste(tile.convert('RGB'),(x,y+20));draw.text((x,y),f"{rec['name']}  {rec['size'][0]}x{rec['size'][1]}",fill='white')
preview.save(OUT/'44张包内纹理解码预览.png')
(OUT/'回退').mkdir(exist_ok=True);(OUT/'回退'/N).write_bytes(source)
m={'version':51,'source_bundle':str(SOURCE),'source_sha256':sha(source),'sha256':sha(dest.read_bytes()),
   'serialized_file':af.name,'added_texture_count':44,'textures':records,
   'existing_asset_bytes_preserved':len(hashes)-1,'existing_container_entries_preserved':len(oldmeta['m_Container']),
   'existing_preload_table_preserved':True,'all_new_decoded_pixels_exact_match':True,
   'protected_sha256':{str(p):h for p,h in protected.items()},'installed':False,'game_runtime_verified':False}
(OUT/'资源ID与校验记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),encoding='utf8')
mapping='名称\tPath ID\t尺寸\t纹理格式\t包内资源名\n'+'\n'.join(f"{r['name']}\t{r['path_id']}\t{r['size'][0]}×{r['size'][1]}\tRGBA32\t{r['container_name']}" for r in records)
(OUT/'资源ID对照.txt').write_text(mapping+'\n',encoding='utf-8-sig')
for back in [False,True]:
    src='回退/'+N if back else N;expected=m['sha256'] if back else m['source_sha256'];final=m['source_sha256'] if back else m['sha256']
    script=f'''$ErrorActionPreference = 'Stop'
if (Get-Process -Name fm -ErrorAction SilentlyContinue) {{ throw 'Exit Football Manager first.' }}
$targetBundle = '{SOURCE}'
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{expected}') {{ throw 'Bundle version mismatch.' }}
Copy-Item -LiteralPath (Join-Path $PSScriptRoot '{src}') -Destination $targetBundle -Force
if ((Get-FileHash -LiteralPath $targetBundle -Algorithm SHA256).Hash.ToLower() -ne '{final}') {{ throw 'Installed bundle hash mismatch.' }}
Write-Host 'Complete.'
'''
    (OUT/('回退.ps1' if back else '安装.ps1')).write_text(script,encoding='utf-8-sig')
(OUT/'说明.txt').write_text('V51：仅向backgrounds包新增本次指定的44张图片。\nPA01～PA20共20张、CA08～CA20共13张、CAPAbg共1张、HIDEstats01～HIDEstats10共10张。\nCA01～CA07不在本次附件清单内，未导入。\n保留原图名称、原尺寸和Alpha；采用RGBA32无损格式、单级mipmap，全部成品解码像素与原PNG逐字节一致。\n新Path ID -910000000000092至-910000000000135；各项对应关系见资源ID对照.txt。\n全部登记AssetBundle资源名称及预加载信息。\n保留已有所有纹理与ID、CAB名称、原容器及预加载；gameworld、global、visualfunctions和catalog均未修改。\n本次加入图片资源，未自行增加界面组件或数据绑定。需要使用时按对照表引用backgrounds中的图片。\n退出游戏后运行安装.ps1；回退.ps1恢复本次更新前的backgrounds。',encoding='utf-8-sig')
with zipfile.ZipFile(OUT.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
    for f in OUT.rglob('*'):
        if f.is_file():z.write(f,f.relative_to(OUT))
with zipfile.ZipFile(OUT.with_suffix('.zip')) as z:assert z.testzip() is None
print(json.dumps({'version':51,'sha256':m['sha256'],'added':44,'id_first':records[0]['path_id'],'id_last':records[-1]['path_id'],'existing_assets_preserved':len(hashes)-1,'decoded_pixels_exact_match':True},ensure_ascii=False))
