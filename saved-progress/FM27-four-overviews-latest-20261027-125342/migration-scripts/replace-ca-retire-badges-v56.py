import copy,hashlib,json,re,struct,sys,zipfile,datetime
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageChops,ImageStat
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
BN='ui-backgrounds_assets_common.bundle';WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
OUT=R/'五张CA替换并永久停用70张徽章-V56-20261027'
assert not (OUT/'替换删除及引用校验记录.json').exists(), 'Existing completed output must not be overwritten'
sha=lambda b:hashlib.sha256(b).hexdigest()
snapshot=json.loads((R/'probe-ca-cleanup-v56.json').read_text('utf8'))
before={Path(x['path']):Path(x['path']).read_bytes() for x in snapshot}
assert all(sha(before[Path(x['path'])])==x['hash'] for x in snapshot)
assert before[GAME/BN]==before[SKIN/BN] and before[GAME/WN]==before[SKIN/WN]
protected={p:sha(p.read_bytes()) for p in [GAME.parent/'catalog.bin',GAME/'ui-visualfunctions_assets_all.bundle',GAME/'ui-tileslayouts_assets_all.bundle']}
protected.update({p:sha(b) for p,b in before.items() if p.name not in [BN,WN]})
prior=json.loads((R/'游戏更新后恢复243张图片-V54'/'恢复与校验记录.json').read_text('utf8'))
retired={t['path_id']:t['name'] for t in prior['textures'] if re.fullmatch(r'(ATT|DEF|FED|KIK|SPD|SPT|TCN)\d+',t['name'])}
assert len(retired)==70
cards={n:-910000000000003-i for i,n in enumerate(['CA000','CA120','CA140','CA160','CA180'])}
be=UnityPy.load(before[GAME/BN]);ba=be.assets[0];bo=ba.objects
original_hashes={i:sha(o.get_raw_data()) for i,o in bo.items()}
aux={k:sha(v.bytes) for k,v in be.file.files.items() if k!=ba.name}
assert all(bo[i].peek_name()==n for i,n in retired.items())
oldtextures={o.path_id:o.peek_name() for o in bo.values() if o.type.name=='Texture2D'}
OUT.mkdir(exist_ok=True);(OUT/'源PNG').mkdir(exist_ok=True)
replacements=[];desired={}
for name,pid in cards.items():
 obj=bo[pid];assert obj.peek_name()==name
 src=Path('K:/桌面/27skin/PICTURE')/(name+'.png');raw=src.read_bytes()
 with Image.open(src) as im:image=im.convert('RGBA')
 t=obj.read_typetree();old=copy.deepcopy(t)
 pixels,fmt=image_to_texture2d(image,t['m_TextureFormat'],obj.platform,t['m_PlatformBlob'])
 assert int(fmt)==t['m_TextureFormat']==12 and t['m_MipCount']==1
 t.update(m_Width=image.width,m_Height=image.height,m_CompleteImageSize=len(pixels))
 t['image data']=pixels;t['m_StreamData']={'offset':0,'size':0,'path':''};obj.save_typetree(t)
 desired[pid]=copy.deepcopy(t)
 (OUT/'源PNG'/src.name).write_bytes(raw)
 replacements.append({'name':name,'path_id':str(pid),'source_png':str(src),'source_png_sha256':sha(raw),'size':list(image.size),'texture_format_id':12})
 print('Replaced',name,flush=True)
bundle=next(o for o in bo.values() if o.type.name=='AssetBundle');bm=bundle.read_typetree();oldbm=copy.deepcopy(bm)
def is_retired(p):return isinstance(p,dict) and p.get('m_FileID')==0 and p.get('m_PathID') in retired
oldpre=bm['m_PreloadTable'];keep=[not is_retired(p) for p in oldpre];prefix=[0]
for k in keep:prefix.append(prefix[-1]+int(k))
bm['m_Container']=[(k,e) for k,e in bm['m_Container'] if not is_retired(e['asset'])]
def fix_span(v):
 if isinstance(v,dict):
  if 'preloadIndex' in v and 'preloadSize' in v:
   start,size=v['preloadIndex'],v['preloadSize'];assert 0<=start<=start+size<=len(oldpre)
   v['preloadIndex']=prefix[start];v['preloadSize']=prefix[start+size]-prefix[start]
  for x in v.values():fix_span(x)
 elif isinstance(v,(list,tuple)):
  for x in v:fix_span(x)
fix_span(bm);bm['m_PreloadTable']=[p for p,k in zip(oldpre,keep) if k]
bundle.save_typetree(bm)
for pid in retired:del bo[pid]
assert len(oldbm['m_Container'])-len(bm['m_Container'])==70
assert len(oldpre)-len(bm['m_PreloadTable'])==70
world=UnityPy.load(before[GAME/WN]);wa=world.assets[0];wo=wa.objects
bgpath=f'archive:/{ba.name}/{ba.name}';fileid=[i+1 for i,e in enumerate(wa.externals) if e.path==bgpath]
assert len(fileid)==1;fileid=fileid[0]
world_hashes={i:sha(o.get_raw_data()) for i,o in wo.items()}
styles=[];links=[]
def rewrite(v,path='',matches=None):
 count=0
 if isinstance(v,dict):
  if 'm_PathID' in v and 'm_FileID' in v:
   if v['m_PathID'] in retired and v['m_FileID']==fileid:
    v.update(m_FileID=0,m_PathID=0);count+=1
   elif v['m_PathID'] in cards.values() and v['m_FileID'] in [fileid,0]:
    assert v['m_FileID']==fileid,'Unexpected local card texture fallback'
    if matches is not None:matches.append({'path':path,'m_FileID':fileid,'m_PathID':str(v['m_PathID'])})
  for k,x in v.items():count+=rewrite(x,path+'/'+k,matches)
 elif isinstance(v,(list,tuple)):
  for i,x in enumerate(v):count+=rewrite(x,path+'/'+str(i),matches)
 return count
needles=[struct.pack('<q',i) for i in list(retired)+list(cards.values())]
for pid,o in list(wo.items()):
 if not any(n in o.get_raw_data() for n in needles):continue
 t=o.read_typetree();old=copy.deepcopy(t);matches=[];count=rewrite(t,matches=matches)
 if count:
  assert o.type.name=='MonoBehaviour' and 'assets' in t
  expected=copy.deepcopy(old)
  for ptr in expected['assets']:
   if ptr.get('m_FileID')==fileid and ptr.get('m_PathID') in retired:ptr.update(m_FileID=0,m_PathID=0)
  assert t==expected,'Change outside stylesheet assets'
  o.save_typetree(t);styles.append({'path_id':str(pid),'name':o.peek_name(),'cleared_image_references':count})
 if matches:links.append({'style_path_id':str(pid),'style_name':o.peek_name(),'links':matches})
assert sum(x['cleared_image_references'] for x in styles)==700
assert sum(len(x['links']) for x in links)==55
outputs={BN:be.file.save(packer='lz4'),WN:world.file.save(packer='lz4')}
for n,b in outputs.items():(OUT/n).write_bytes(b)
check=UnityPy.load(outputs[BN],outputs[WN]);sba=next(a for a in check.assets if a.name==ba.name);swa=next(a for a in check.assets if a.name==wa.name)
assert set(sba.objects)==set(original_hashes)-set(retired) and set(swa.objects)==set(world_hashes)
changed_bg=set(cards.values())|{bundle.path_id};changed_world={int(x['path_id']) for x in styles}
for i,h in original_hashes.items():
 if i not in retired and i not in changed_bg:assert sha(sba.objects[i].get_raw_data())==h
for i,h in world_hashes.items():
 if i not in changed_world:assert sha(swa.objects[i].get_raw_data())==h
# Check native resource streams independently of serialization.
saved_bg_env=UnityPy.load(outputs[BN])
for k,h in aux.items():assert sha(saved_bg_env.file.files[k].bytes)==h
for n,pid in cards.items():
 assert sba.objects[pid].read_typetree()==desired[pid]
 sba.objects[pid].read().image.load()
 assert pid not in swa.objects
 rec=next(r for r in replacements if r['name']==n)
 with Image.open(rec['source_png']) as im:image=im.convert('RGBA')
 decoded=sba.objects[pid].read().image.convert('RGBA');rms=ImageStat.Stat(ImageChops.difference(decoded,image)).rms
 assert decoded.size==image.size and decoded.getchannel('A').getextrema()==image.getchannel('A').getextrema()
 assert rms[3]<20 and sum(rms)<sum(ImageStat.Stat(ImageChops.difference(decoded,image.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms)
 rec.update(texture_sha256=sha(sba.objects[pid].get_raw_data()),changed_from_previous=sha(sba.objects[pid].get_raw_data())!=original_hashes[pid],decoded_alpha_range=list(decoded.getchannel('A').getextrema()),rgba_rms_error=rms)
for row in links:
 t=swa.objects[int(row['style_path_id'])].read_typetree()
 for link in row['links']:
  v=t
  for part in link['path'].strip('/').split('/'):v=v[int(part)] if isinstance(v,list) else v[part]
  assert v=={'m_FileID':fileid,'m_PathID':int(link['m_PathID'])}
  from UnityPy.classes import PPtr
  resolved=PPtr(m_FileID=v['m_FileID'],m_PathID=v['m_PathID'],assetsfile=swa).deref()
  assert resolved.assets_file.name==ba.name and sha(resolved.get_raw_data())==sha(sba.objects[v['m_PathID']].get_raw_data())
for o in swa.objects.values():
 if any(struct.pack('<q',i) in o.get_raw_data() for i in retired):
  t=o.read_typetree();assert rewrite(copy.deepcopy(t))==0
assert not any(o.type.name=='Texture2D' and re.fullmatch(r'(ATT|DEF|FED|KIK|SPD|SPT|TCN)\d+',o.peek_name()) for o in sba.objects.values())
active=[];prior_by_id={t['path_id']:t for t in prior['textures']}
for pid,name in oldtextures.items():
 if pid not in prior_by_id or pid in retired:continue
 o=sba.objects[pid];t=o.read_typetree();im=o.read().image.convert('RGBA');im.load()
 active.append({'name':name,'path_id':str(pid),'texture_format_id':t['m_TextureFormat'],'size':[t['m_Width'],t['m_Height']],'texture_sha256':sha(o.get_raw_data()),'decoded_alpha_range':list(im.getchannel('A').getextrema())})
assert len(active)==173
installs=[]
for p,b in before.items():
 if p.name not in outputs:continue
 tag='game' if p.parent==GAME else 'skin';rel=Path('回退')/tag/p.name;(OUT/rel).parent.mkdir(parents=True,exist_ok=True);(OUT/rel).write_bytes(b)
 installs.append({'target':str(p),'source':p.name,'backup':rel.as_posix(),'before_sha256':sha(b),'after_sha256':sha(outputs[p.name])})
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
registry={'updated':'2026-10-27','policy':'永久停用，不允许占用、复用、恢复或分配给其他资源；不创建占位对象。','reserved_textures':[{'name':n,'path_id':str(i),'status':'retired_permanently'} for i,n in sorted(retired.items(),key=lambda x:x[1])]}
(R/'reserved-texture-ids.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),'utf8');(OUT/'永久保留禁止复用ID.json').write_text(json.dumps(registry,ensure_ascii=False,indent=2),'utf8')
manifest={'version':56,'date':'2026-10-27','installed':False,'game_runtime_verified':False,'replaced_textures':replacements,'retired_texture_count':70,'reserved_registry':str(R/'reserved-texture-ids.json'),'active_custom_texture_count':173,'active_textures':active,'verified_ca_ui_links':links,'cleared_retired_image_references':styles,'native_resource_streams_preserved':aux,'unrelated_background_objects_preserved':len(original_hashes)-len(retired)-len(changed_bg),'unrelated_world_objects_preserved':len(world_hashes)-len(changed_world),'install_files':installs,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'替换删除及引用校验记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'当前173张图片ID对照.txt').write_text('名称\tPath ID（文本）\t纹理对象SHA256\n'+'\n'.join(f"{t['name']}\t{t['path_id']}\t{t['texture_sha256']}" for t in active),'utf-8-sig')
for rollback in [False,True]:
 entries=[{'target':x['target'],'source':x['backup'] if rollback else x['source'],'before':x['after_sha256'] if rollback else x['before_sha256'],'after':x['before_sha256'] if rollback else x['after_sha256']} for x in installs]
 rows='\n'.join("@{Target='"+x['target']+"';Source='"+x['source']+"';Before='"+x['before']+"';After='"+x['after']+"'}" for x in entries)
 script="""$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
"""+rows+"""
)
foreach($item in $items){
 if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before){throw ('Target version mismatch: '+$item.Target)}
 if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Package hash mismatch.'}
}
$written=@()
try{
 foreach($item in $items){$written+=@{Target=$item.Target;Bytes=[IO.File]::ReadAllBytes($item.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force;if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Installed hash mismatch.'}}
}catch{foreach($entry in $written){[IO.File]::WriteAllBytes($entry.Target,$entry.Bytes)};throw}
Write-Output 'Complete.'
"""
 (OUT/('回退.ps1' if rollback else '安装.ps1')).write_text(script,'utf-8-sig')
(OUT/'说明.txt').write_text('V56：替换 CA000、CA120、CA140、CA160、CA180，保留同名及原 Path ID；DXT5 保持原设置，存在正常压缩误差。\n删除 ATT/DEF/FED/KIK/SPD/SPT/TCN 各10张，共70张纹理及目录/预加载记录，700个旧样式引用清空。\n这70个名称和 Path ID 永久停用，不创建占位对象，不允许分配或重新恢复。当前有效自定义图片数为173，不再是243。\n55个卡面样式引用逐一验证直接解析到 backgrounds 中的新图，gameworld 没有旧卡面副本。\n同步更新游戏目录和皮肤工作目录的 backgrounds、gameworld。其余布局、绑定、global、catalog、visualfunctions 和 tileslayouts 保持不变。\n退出游戏后运行安装.ps1。回退.ps1只用于故障回退，含删除前原包；不可作为下次更新的图片来源。\n下次更新以本目录 backgrounds 和当前173张图片清单为准，结合永久保留禁止复用ID.json，不可再次从V53/V54/V55无筛选恢复243张。\n游戏内实际渲染待启动后确认。','utf-8-sig')
print(json.dumps({'output':str(OUT),'active':len(active),'removed':len(retired),'cleared_ui_refs':700,'verified_ca_refs':55,'sizes':{n:len(b) for n,b in outputs.items()}},ensure_ascii=False),flush=True)
