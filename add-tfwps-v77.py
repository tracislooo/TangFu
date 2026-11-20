import copy, datetime, hashlib, json, os, subprocess, sys, zipfile
from pathlib import Path
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from PIL import Image
from UnityPy.export.Texture2DConverter import image_to_texture2d
O=R/'TFWPS图片新增-20261105'; BN='ui-backgrounds_assets_common.bundle'
M=O/'manifest.json'; REG=R/'current-custom-textures.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
def dump(p,v):p.write_text(json.dumps(v,ensure_ascii=False,indent=2),'utf8')
def running():
 p=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 assert p.returncode in (0,1) and not p.stderr.strip(),p.stderr
 return bool(p.stdout.strip())
if '--install' in sys.argv or '--rollback' in sys.argv:
 m=json.loads(M.read_text('utf8'));back='--rollback' in sys.argv
 if running():print('GAME_RUNNING_PENDING_INSTALL');sys.exit(0)
 assert not m['installed'] if not back else m['installed']
 changes=[]
 for x in m['install_files']:
  p=Path(x['target']);assert 'Project Taco' not in str(p)
  old=p.read_bytes();assert sha(old)==x['after_sha256' if back else 'before_sha256'],str(p)+' version changed'
  payload=(O/x['backup' if back else 'source']).read_bytes()
  assert sha(payload)==x['before_sha256' if back else 'after_sha256']
  changes.append((p,old,payload))
 regold=REG.read_bytes();assert sha(regold)==m['registry_after_sha256' if back else 'registry_before_sha256']
 regnew=(O/('backup/current-custom-textures.json' if back else '更新后的有效图片恢复来源.json')).read_bytes()
 changes.append((REG,regold,regnew))
 if not back:
  for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h,'Other files changed: '+p
 try:
  for p,old,new in changes:
   tmp=p.with_name(p.name+'.tfwps.tmp');tmp.write_bytes(new);os.replace(tmp,p);assert p.read_bytes()==new
 except BaseException:
  for p,old,new in changes:p.write_bytes(old)
  raise
 m.update(installed=not back,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());dump(M,m)
 p=R/'AGENTS.md';s=p.read_text('utf8')
 if back:s+='\n- TFWPS 新增安装已回退，恢复来源以 current-custom-textures.json 为准。\n'
 else:
  s=s.replace('当前有效自定义图片为 180 张','当前有效自定义图片为 181 张')
  s+='\n- 2026-11-05 新增 TFWPS（-910000000000153）至 backgrounds，RGBA32 原尺寸无损像素；只入包，未设置界面关联。后续沿用名称及 ID；记录 TFWPS图片新增-20261105/manifest.json。\n'
 p.write_text(s,'utf8');print('ROLLED_BACK' if back else 'INSTALLED');sys.exit(0)
assert not O.exists()
loc=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(loc['bundle_root']);S=Path(loc['skin_packages']);AA=Path(loc['aa_root'])
regraw=REG.read_bytes();registry=json.loads(regraw)
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))
banned={int(t['path_id']) for t in reserved['reserved_textures']}|{-910000000000001,-910000000000002,-910000000000146}
banned_names={t['name'] for t in reserved['reserved_textures']}|{'PlayerTopBackground','PlayerTopBlueLight','TF patch'}
before={folder:(folder/BN).read_bytes() for folder in [G,S]};assert before[G]==before[S]
protected={p:sha(p.read_bytes()) for folder in [G,S] for p in folder.glob('ui-*.bundle') if p.name!=BN}
protected.update({p:sha(p.read_bytes()) for folder in [AA,S] for p in [folder/'catalog.bin',folder/'catalog.hash'] if p.exists()})
e=UnityPy.load(before[G]);a=e.assets[0];obs=a.objects;hashes={i:sha(o.get_raw_data()) for i,o in obs.items()}
ids={'TFWPS':-910000000000153}
assert banned.isdisjoint(obs) and banned.isdisjoint(ids.values())
assert not set(ids).intersection(t['name'] for t in registry['textures'])
assert not set(ids.values()).intersection(int(t['path_id']) for t in registry['textures'])
for n in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle']:
 other=UnityPy.load(str(G/n));assert all(set(ids.values()).isdisjoint(x.objects) for x in other.assets)
assert not any(o.peek_name() in set(ids)|banned_names for o in obs.values() if o.type.name=='Texture2D')
template=obs[-910000000000150]
bundle=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=bundle.read_typetree();oldmeta=copy.deepcopy(meta)
aux={k:sha(v.bytes) for k,v in e.file.files.items() if k!=a.name};records=[];desired={};images={};rawsources={}
sources={'TFWPS':Path('K:/桌面/27skin/PICTURE/TFWPS.png')}
for name,pid in ids.items():
 assert pid not in obs
 src=sources[name];raw=src.read_bytes();rawsources[name]=raw
 with Image.open(src) as im:image=im.convert('RGBA');source_format=im.format
 images[pid]=image
 obj=copy.copy(template);obj.assets_file=a;obj.path_id=pid;obj.data=None;obj._read_until=None;obj.set_raw_data(template.get_raw_data());obs[pid]=obj
 t=copy.deepcopy(template.read_typetree());pixels,fmt=image_to_texture2d(image,4,obj.platform,t['m_PlatformBlob']);assert int(fmt)==4
 t.update(m_Name=name,m_TextureFormat=4,m_Width=image.width,m_Height=image.height,m_CompleteImageSize=len(pixels),m_MipCount=1)
 t['image data']=pixels;t['m_StreamData']={'offset':0,'size':0,'path':''};obj.save_typetree(t);desired[pid]=t
 key=name.lower();assert key not in dict(meta['m_Container']);ptr={'m_FileID':0,'m_PathID':pid}
 meta['m_Container'].append((key,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':1,'asset':ptr}));meta['m_PreloadTable'].append(copy.deepcopy(ptr))
 records.append({'name':name,'path_id':str(pid),'size':list(image.size),'texture_format_id':4,'source_file':str(src),'source_sha256':sha(raw),'source_file_format':source_format,'m_FileID':0,'container_key':key,'bundle':BN,'cab':a.name})
meta['m_Container'].sort(key=lambda x:x[0]);bundle.save_typetree(meta);output=e.file.save(packer='lz4');saved=UnityPy.load(output);af=saved.assets[0]
assert af.name==a.name and set(af.objects)==set(hashes)|set(ids.values())
for i,h in hashes.items():
 if i!=bundle.path_id:assert sha(af.objects[i].get_raw_data())==h
for k,h in aux.items():assert sha(saved.file.files[k].bytes)==h
assert af.objects[bundle.path_id].read_typetree()==meta
assert dict(meta['m_Container']).items()>=dict(oldmeta['m_Container']).items()
assert meta['m_PreloadTable'][:len(oldmeta['m_PreloadTable'])]==oldmeta['m_PreloadTable']
assert banned.isdisjoint(af.objects) and all(p['m_PathID'] not in banned for p in meta['m_PreloadTable'])
assert all(v['asset']['m_PathID'] not in banned for k,v in meta['m_Container'])
for t in registry['textures']:
 obj=af.objects[int(t['path_id'])];assert obj.peek_name()==t['name'] and sha(obj.get_raw_data())==t['texture_sha256']
for rec in records:
 pid=int(rec['path_id']);obj=af.objects[pid];assert obj.read_typetree()==desired[pid]
 decoded=obj.read().image.convert('RGBA');assert decoded.size==images[pid].size and decoded.tobytes()==images[pid].tobytes()
 rec.update(lossless_rgba_match=True,decoded_pixel_sha256=sha(decoded.tobytes()),texture_sha256=sha(obj.get_raw_data()),decoded_alpha_range=list(decoded.getchannel('A').getextrema()))
O.mkdir();(O/BN).write_bytes(output);(O/'sources').mkdir();(O/'backup').mkdir();(O/'backup/current-custom-textures.json').write_bytes(regraw)
for rec in records:
 name=rec['name'];ext='.png' if rec['source_file_format']=='PNG' else '.jpg';p=O/'sources'/(name+ext);p.write_bytes(rawsources[name]);rec['archived_source']=str(p)
installs=[]
for folder,b in before.items():
 tag='game' if folder==G else 'skin';rel=Path('backup')/tag/BN;(O/rel).parent.mkdir(parents=True);(O/rel).write_bytes(b)
 installs.append({'target':str(folder/BN),'source':BN,'backup':rel.as_posix(),'before_sha256':sha(b),'after_sha256':sha(output)})
current=copy.deepcopy(registry);current.update(version=77,date='2026-11-05',authoritative_source_bundle=str(O/BN),source_bundle_sha256=sha(output),manifest=str(M),active_custom_texture_count=len(registry['textures'])+1)
for rec in records:current['textures'].append({k:rec[k] for k in ['name','path_id','texture_format_id','size','texture_sha256','decoded_alpha_range','archived_source']})
if 'restore_policy' in current:current['restore_policy']=str(current['restore_policy']).replace('180','181')
dump(O/'更新后的有效图片恢复来源.json',current)
m={'installed':False,'runtime_verified':False,'textures':records,'active_custom_texture_count':len(current['textures']),'all_existing_objects_preserved':len(hashes)-1,'existing_streams_preserved':True,'retired_ids_absent':True,'ui_associations_added':False,'install_files':installs,'registry_before_sha256':sha(regraw),'registry_after_sha256':sha((O/'更新后的有效图片恢复来源.json').read_bytes()),'protected_sha256':{str(p):h for p,h in protected.items()}}
dump(M,m)
for back in [False,True]:
 cmd='--rollback' if back else '--install'
 (O/('回退.ps1' if back else '安装.ps1')).write_text("$ErrorActionPreference='Stop'\n& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(Path(__file__).resolve())+"' "+cmd+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(O/'资源位置.md').write_text('| 名称 | Path ID | CAB | m_FileID | 目录键 |\n|---|---|---|---|---|\n'+''.join('| '+r['name']+' | '+r['path_id']+' | '+r['cab']+' | 0 | '+r['container_key']+' |\n' for r in records)+'\n所属包：'+BN+'。跨包 m_FileID 以引用包 externals 索引+1确定。新图保持原尺寸，RGBA32，解码像素完全一致；仅入包，未新增界面关联。游戏运行时保留待安装包，退出后运行安装.ps1。\n','utf8')
for p,h in protected.items():assert sha(p.read_bytes())==h
for folder,b in before.items():assert (folder/BN).read_bytes()==b
assert REG.read_bytes()==regraw
print(json.dumps({'prepared':True,'active':len(current['textures']),'textures':records},ensure_ascii=False))
