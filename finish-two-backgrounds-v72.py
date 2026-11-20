import copy,datetime,hashlib,json,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageChops,ImageStat
O=R/'TFWX及原生背景同名替换-V72-20261029';F=O/'图片及引用校验记录.json';m=json.loads(F.read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest()
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');N='ui-backgrounds_assets_.bundle'
if '--commit' in sys.argv:
 assert all(sha(Path(x['target']).read_bytes())==x['after_sha256'] for x in m['install_files'])
 assert all(sha(Path(p).read_bytes())==h for p,h in m['protected_sha256'].items())
 (R/'current-custom-textures.json').write_bytes((O/'更新后的有效图片恢复来源.json').read_bytes())
 m.update(installed=True,installed_hash_verified=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());F.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
 p=R/'AGENTS.md';s=p.read_text('utf8');s+='\n- V72 更新 TFWX，原ID不变；同名原生纹理 `fm27-background-texture`（`274891149646581386`，`ui-backgrounds_assets_.bundle`）改用对应PNG。后续更新按 current-custom-textures.json 的 native_individual_replacements 在新版原包上恢复该覆盖。\n';p.write_text(s,'utf8');print('V72 installed and registry updated.');sys.exit(0)
if '--package' in sys.argv:
 with zipfile.ZipFile(O.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for f in O.rglob('*'):
   if f.is_file():z.write(f,f.relative_to(O))
 with zipfile.ZipFile(O.with_suffix('.zip')) as z:assert z.testzip() is None
 print(json.dumps({'installed':m['installed'],'replaced':[t['name'] for t in m['textures']],'sizes':[t['size'] for t in m['textures']]}));sys.exit(0)
assert not any(x['name']=='fm27-background-texture' for x in m['textures'])
before={p/N:(p/N).read_bytes() for p in [G,S]};assert before[G/N]==before[S/N]
for p,b in before.items():assert sha(b)==m['protected_sha256'][str(p)]
e=UnityPy.load(before[G/N]);a=e.assets[0];obs=a.objects;matches=[o for o in obs.values() if o.type.name=='Texture2D' and o.peek_name()=='fm27-background-texture'];assert len(matches)==1
o=matches[0];pid=o.path_id;old=o.read_typetree();assert pid==274891149646581386
hashes={i:sha(v.get_raw_data()) for i,v in obs.items()};aux={k:sha(v.bytes) for k,v in e.file.files.items() if k!=a.name}
src=Path('K:/桌面/27skin/PICTURE/fm27-background-texture.png');png=src.read_bytes()
with Image.open(src) as im:image=im.convert('RGBA')
fmt=old['m_TextureFormat'] if image.getchannel('A').getextrema()==(255,255) else 4
pixels,actual=image_to_texture2d(image,fmt,o.platform,old['m_PlatformBlob']);assert int(actual)==fmt
t=copy.deepcopy(old);t.update(m_Width=image.width,m_Height=image.height,m_TextureFormat=fmt,m_CompleteImageSize=len(pixels),m_MipCount=1);t['image data']=pixels;t['m_StreamData']={'offset':0,'size':0,'path':''}
if 'm_StreamingMipmaps' in t:t['m_StreamingMipmaps']=False
o.save_typetree(t);data=e.file.save(packer='lz4');saved=UnityPy.load(data);sa=saved.assets[0];assert set(sa.objects)==set(hashes) and sa.name==a.name
for i,h in hashes.items():
 if i!=pid:assert sha(sa.objects[i].get_raw_data())==h
for k,h in aux.items():assert sha(saved.file.files[k].bytes)==h
assert sa.objects[pid].read_typetree()==t
decoded=sa.objects[pid].read().image.convert('RGBA');rms=ImageStat.Stat(ImageChops.difference(decoded,image)).rms
assert decoded.size==image.size and decoded.getchannel('A').getextrema()==image.getchannel('A').getextrema() and max(rms)<20
assert sum(rms)<sum(ImageStat.Stat(ImageChops.difference(decoded,image.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms)
rec={'name':old['m_Name'],'path_id':str(pid),'bundle':N,'size':list(image.size),'texture_format_id':fmt,'source_png':str(src),'source_png_sha256':sha(png),'texture_sha256':sha(sa.objects[pid].get_raw_data()),'decoded_alpha_range':list(decoded.getchannel('A').getextrema()),'rgba_rms_error':rms,'native_resource':True}
(O/N).write_bytes(data);(O/'源PNG'/src.name).write_bytes(png);decoded.thumbnail((836,470));decoded.save(O/'原生背景成品解码预览.png')
for p,b in before.items():
 tag='game' if p.parent==G else 'skin';rel=Path('回退')/tag/N;(O/rel).write_bytes(b);m['install_files'].append({'target':str(p),'source':N,'backup':rel.as_posix(),'before_sha256':sha(b),'after_sha256':sha(data)});del m['protected_sha256'][str(p)]
m['textures'].append(rec);m['native_other_objects_unchanged']=len(hashes)-1
current_path=O/'更新后的有效图片恢复来源.json';cur=json.loads(current_path.read_text('utf8'));cur.setdefault('native_individual_replacements',[])
cur['native_individual_replacements']=[x for x in cur['native_individual_replacements'] if not (x.get('bundle')==N and x.get('name')==rec['name'])]
cur['native_individual_replacements'].append(dict(rec,source_png=str(O/'源PNG'/src.name),authoritative_source_bundle=str(O/N),source_bundle_sha256=sha(data)))
current_path.write_text(json.dumps(cur,ensure_ascii=False,indent=2),'utf8');F.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(O/'回退'/'current-custom-textures.json').write_bytes((R/'current-custom-textures.json').read_bytes())
for back in [False,True]:
 rows='\n'.join("@{Target='"+x['target']+"';Source='"+(x['backup'] if back else x['source'])+"';Before='"+(x['after_sha256'] if back else x['before_sha256'])+"';After='"+(x['before_sha256'] if back else x['after_sha256'])+"'}" for x in m['install_files'])
 guards='' if back else '\n'.join("if((Get-FileHash -LiteralPath '"+p+"' -Algorithm SHA256).Hash.ToLower() -ne '"+h+"'){throw 'Related resource version changed.'}" for p,h in m['protected_sha256'].items())
 script="$ErrorActionPreference='Stop'\nif(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}\n"+guards+"\n$items=@(\n"+rows+"\n)\nforeach($x in $items){if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.Before){throw 'Version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Package hash mismatch.'}}\n$written=@()\ntry{foreach($x in $items){$written+=@{Target=$x.Target;Bytes=[IO.File]::ReadAllBytes($x.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Destination $x.Target -Force;if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Install checksum mismatch.'}}}catch{foreach($x in $written){[IO.File]::WriteAllBytes($x.Target,$x.Bytes)};throw}\n"
 if back:script+="Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination '"+str(R/'current-custom-textures.json')+"' -Force\n"
 else:script+="& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(Path(__file__).resolve())+"' --commit\nif($LASTEXITCODE -ne 0){throw 'Registry finalization failed.'}\n"
 (O/('回退.ps1' if back else '安装.ps1')).write_text(script,'utf-8-sig')
(O/'说明.txt').write_text('V72：同名替换 TFWX 与 fm27-background-texture，各自名称、Path ID、CAB、资源目录和预加载保持不变。\nTFWX 使用 RGBA32 无损纹理，像素与源 PNG 完全一致。原生 fm27-background-texture 保留兼容纹理格式、源PNG尺寸和透明度，使用单级mipmap，DXT存在正常压缩误差。\n分别更新 common 与 ui-backgrounds_assets_.bundle，同步游戏和皮肤目录；其他资源对象、原生资源流、界面布局、引用、公式、catalog及其他原生覆盖不变。\n自定义图片数量不变；恢复清单新增此次原生背景覆盖记录，保留原有覆盖列表。含原包备份、安装/回退脚本。游戏内显示待重启确认。','utf-8-sig')
assert sha(src.read_bytes())==sha(png)
for p,b in before.items():assert p.read_bytes()==b
for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h
print(json.dumps({'prepared':True,'native_name':rec['name'],'native_format':fmt,'size':rec['size'],'install_targets':len(m['install_files'])}))
