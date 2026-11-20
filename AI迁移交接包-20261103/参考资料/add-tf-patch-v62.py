import copy,datetime,hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
from UnityPy.export.Texture2DConverter import image_to_texture2d
from PIL import Image,ImageChops,ImageStat,ImageDraw
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');G=AA/'StandaloneWindows64';S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
BN='ui-backgrounds_assets_common.bundle';WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
O=R/'TF-patch图片新增-V62-20261028';assert not O.exists();sha=lambda b:hashlib.sha256(b).hexdigest()
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'));reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'));banned={int(t['path_id']) for t in reserved['reserved_textures']}
before={folder:(folder/BN).read_bytes() for folder in [G,S]};assert before[G]==before[S]
protected={p:sha(p.read_bytes()) for folder in [G,S] for p in [folder/WN,folder/GN,folder/'ui-visualfunctions_assets_all.bundle',folder/'ui-tileslayouts_assets_all.bundle'] if p.exists()}
protected.update({p:sha(p.read_bytes()) for folder in [G,S] for p in folder.glob('*.bundle') if p.name!=BN})
protected.update({p:sha(p.read_bytes()) for folder in [AA,S] for p in [folder/'catalog.bin',folder/'catalog.hash'] if p.exists()})
e=UnityPy.load(before[G]);a=e.assets[0];obs=a.objects;hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};assert banned.isdisjoint(obs)
ids={'TF patch':-910000000000146}
all_ids=set(obs)
for n in [WN,GN]:all_ids.update(UnityPy.load(str(G/n)).assets[0].objects)
assert ids['TF patch'] not in all_ids and ids['TF patch'] not in banned
assert not any(o.type.name=='Texture2D' and o.peek_name()=='TF patch' for o in obs.values())
template=obs[-910000000000005];bundle=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=bundle.read_typetree();oldmeta=copy.deepcopy(meta)
aux={k:sha(v.bytes) for k,v in e.file.files.items() if k!=a.name};desired={};records=[];sources={};source_images={}
for name in ['TF patch']:
 pid=ids[name];src=Path('K:/桌面/27skin/PICTURE')/(name+'.png');raw=src.read_bytes();sources[src]=sha(raw)
 with Image.open(src) as im:image=im.convert('RGBA')
 added=pid not in obs
 if added:
  obj=copy.copy(template);obj.assets_file=a;obj.path_id=pid;obj.data=None;obj._read_until=None;obj.set_raw_data(template.get_raw_data());obs[pid]=obj
 else:obj=obs[pid];assert obj.peek_name()==name
 t=copy.deepcopy(template.read_typetree()) if added else obj.read_typetree()
 pixels,fmt=image_to_texture2d(image,12,obj.platform,t['m_PlatformBlob']);assert int(fmt)==12
 t.update(m_Name=name,m_Width=image.width,m_Height=image.height,m_CompleteImageSize=len(pixels));t['image data']=pixels;t['m_StreamData']={'offset':0,'size':0,'path':''};assert t['m_MipCount']==1
 obj.save_typetree(t);desired[pid]=t;source_images[pid]=image
 if added:
  key=name.lower();assert key not in dict(meta['m_Container']);ptr={'m_FileID':0,'m_PathID':pid};meta['m_Container'].append((key,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':1,'asset':ptr}));meta['m_PreloadTable'].append(copy.deepcopy(ptr))
 records.append({'name':name,'path_id':str(pid),'added':added,'size':list(image.size),'source_png':str(src),'source_png_sha256':sha(raw),'texture_format_id':12})
meta['m_Container'].sort(key=lambda x:x[0]);bundle.save_typetree(meta)
output=e.file.save(packer='lz4');saved=UnityPy.load(output);af=saved.assets[0]
assert af.name==a.name and set(af.objects)==set(hashes)|set(ids.values())
for i,h in hashes.items():
 if i not in desired and i!=bundle.path_id:assert sha(af.objects[i].get_raw_data())==h
for k,h in aux.items():assert sha(saved.file.files[k].bytes)==h
assert dict(meta['m_Container']).items()>=dict(oldmeta['m_Container']).items()
assert meta['m_PreloadTable'][:len(oldmeta['m_PreloadTable'])]==oldmeta['m_PreloadTable']
assert banned.isdisjoint(af.objects) and all(p['m_PathID'] not in banned for p in meta['m_PreloadTable'])
for key,entry in meta['m_Container']:assert entry['asset']['m_PathID'] not in banned
for rec in records:
 pid=int(rec['path_id']);obj=af.objects[pid];assert obj.read_typetree()==desired[pid]
 decoded=obj.read().image.convert('RGBA');im=source_images[pid];rms=ImageStat.Stat(ImageChops.difference(decoded,im)).rms
 assert decoded.size==im.size and decoded.getchannel('A').getextrema()==im.getchannel('A').getextrema() and rms[3]<20
 assert sum(rms)<sum(ImageStat.Stat(ImageChops.difference(decoded,im.transpose(Image.Transpose.FLIP_TOP_BOTTOM))).rms)
 rec.update(texture_sha256=sha(obj.get_raw_data()),decoded_alpha_range=list(decoded.getchannel('A').getextrema()),rgba_rms_error=rms)
# Verify current card PPtrs and all custom VTA/VF catalog registrations in both catalogs.
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
audits=[];links=[];worlds={}
reference_ids={int(t['path_id']) for t in registry['textures'] if t['name'] in ['CA000','CA120','CA140','CA150','CA160','CA170','CA180']}
for n in [WN,GN]:
 en=UnityPy.load((G/n).read_bytes(),output);wa=next(x for x in en.assets if x.name!=af.name);worlds[n]=wa
 bgids=[i+1 for i,x in enumerate(wa.externals) if x.path==f'archive:/{af.name}/{af.name}'];assert len(bgids)==1
 for obj in wa.objects.values():
  if obj.type.name=='Texture2D':assert obj.peek_name() not in ['CA000','CA120','CA140','CA150','CA160','CA170','CA180']
  if not any(struct.pack('<q',i) in obj.get_raw_data() for i in reference_ids):continue
  try:t=obj.read_typetree()
  except Exception:continue
  def visit(v,path=''):
   if isinstance(v,dict):
    if v.get('m_PathID') in reference_ids and 'm_FileID' in v:
     assert v['m_FileID']==bgids[0];resolved=PPtr(m_FileID=v['m_FileID'],m_PathID=v['m_PathID'],assetsfile=wa).deref();assert sha(resolved.get_raw_data())==sha(af.objects[v['m_PathID']].get_raw_data());links.append({'bundle':n,'object_id':str(obj.path_id),'field':path,'m_FileID':v['m_FileID'],'m_PathID':str(v['m_PathID'])})
    for k,x in v.items():visit(x,path+'/'+k)
   elif isinstance(v,(list,tuple)):
    for i,x in enumerate(v):visit(x,path+'/'+str(i))
  visit(t)
for folder in [AA,S]:
 c=cm.Catalog((folder/'catalog.bin').read_bytes());keys={k:ptr for k,ptr in c.keys() if isinstance(k,str)};locs={loc for ptr in keys.values() for (loc,) in c.array(ptr,'I')}
 def bl(n):return next(loc for loc in locs if c.location(loc)['provider'].endswith('.AssetBundleProvider') and c.location(loc)['internal'].endswith('\\'+n))
 bg=bl(BN);checked=[]
 for n,wa in worlds.items():
  own=bl(n);bm=next(o.read_typetree() for o in wa.objects.values() if o.type.name=='AssetBundle')
  for key,entry in bm['m_Container']:
   if not re.fullmatch('[0-9a-f]{32}',key) or entry['asset']['m_FileID']!=0:continue
   obj=wa.objects.get(entry['asset']['m_PathID'])
   if not obj or not (-1000000000000000 < obj.path_id < -900000000000000) or obj.type.name!='MonoBehaviour':continue
   tree=obj.read_typetree();typ='SI.VisualScripting.VisualFunction' if 'm_nodes' in tree else ('UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in tree else None)
   if not typ:continue
   assert key in keys,('Missing catalog key',key,obj.peek_name())
   for (loc,) in c.array(keys[key],'I'):
    val=c.location(loc);assert val['type'][1]==typ and val['dependencies'][0]==own and bg in val['dependencies'],(key,val)
   checked.append({'guid':key,'name':obj.peek_name(),'resource_type':typ,'bundle':n,'path_id':str(obj.path_id)})
 audits.append({'catalog':str(folder/'catalog.bin'),'custom_resources_checked':checked,'catalog_unchanged_sha256':sha((folder/'catalog.bin').read_bytes())})
assert len(links)>=55
O.mkdir();(O/BN).write_bytes(output);(O/'源PNG').mkdir()
for p,h in sources.items():assert sha(p.read_bytes())==h;(O/'源PNG'/p.name).write_bytes(p.read_bytes())
installs=[]
for folder,b in before.items():
 tag='game' if folder==G else 'skin';rel=Path('回退')/tag/BN;(O/rel).parent.mkdir(parents=True,exist_ok=True);(O/rel).write_bytes(b);installs.append({'target':str(folder/BN),'source':BN,'backup':rel.as_posix(),'before_sha256':sha(b),'after_sha256':sha(output)})
current=copy.deepcopy(registry);current.update(version=62,date='2026-10-28',authoritative_source_bundle=str(O/BN),source_bundle_sha256=sha(output),manifest=str(O/'图片及引用校验记录.json'),active_custom_texture_count=177)
byname={t['name']:t for t in current['textures']}
for rec in records:
 row=byname.get(rec['name'])
 if row is None:row={};current['textures'].append(row)
 row.update({k:rec[k] for k in ['name','path_id','texture_format_id','size','texture_sha256','decoded_alpha_range']})
assert len(current['textures'])==177
(O/'当前177张有效图片恢复来源.json').write_text(json.dumps(current,ensure_ascii=False,indent=2),'utf8');(O/'永久保留禁止复用ID.json').write_bytes((R/'reserved-texture-ids.json').read_bytes())
m={'version':62,'installed':False,'runtime_verified':False,'textures':records,'active_custom_texture_count':177,'retired_70_ids_absent':True,'verified_existing_ui_references':links,'catalog_audits':audits,'install_files':installs,'protected_sha256':{str(p):h for p,h in protected.items()},'new_cards_auto_switch_added':False}
(O/'图片及引用校验记录.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
for back in [False,True]:
 rows='\n'.join("@{Target='"+x['target']+"';Source='"+(x['backup'] if back else BN)+"';Before='"+(x['after_sha256'] if back else x['before_sha256'])+"';After='"+(x['before_sha256'] if back else x['after_sha256'])+"'}" for x in installs)
 script="$ErrorActionPreference='Stop'\nif(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}\n$items=@(\n"+rows+"\n)\nforeach($x in $items){if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.Before){throw 'Version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Package hash mismatch.'}}\n$written=@()\ntry{foreach($x in $items){$written+=@{Target=$x.Target;Bytes=[IO.File]::ReadAllBytes($x.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $x.Source) -Destination $x.Target -Force;if((Get-FileHash -LiteralPath $x.Target -Algorithm SHA256).Hash.ToLower() -ne $x.After){throw 'Install checksum mismatch.'}}}catch{foreach($x in $written){[IO.File]::WriteAllBytes($x.Target,$x.Bytes)};throw}\nWrite-Output 'Complete.'\n"
 (O/('回退.ps1' if back else '安装.ps1')).write_text(script,'utf-8-sig')
preview=Image.new('RGB',(420,290),'#343434');d=ImageDraw.Draw(preview)
for i,rec in enumerate(records):
 im=af.objects[int(rec['path_id'])].read().image.convert('RGBA');im.thumbnail((185,245));tile=Image.new('RGBA',(185,245),'#b0b0b0');tile.alpha_composite(im,((185-im.width)//2,(245-im.height)//2));preview.paste(tile.convert('RGB'),(8+200*i,32));d.text((8+200*i,10),rec['name'],fill='white')
preview.save(O/'新增球场图包内解码预览.png')
for p,h in protected.items():assert sha(p.read_bytes())==h
for folder,b in before.items():assert (folder/BN).read_bytes()==b
print(json.dumps({'output':str(O),'replaced':0,'added':1,'active':177,'ui_references_checked':len(links),'catalog_custom_resources_checked':[len(x['custom_resources_checked']) for x in audits]},ensure_ascii=False),flush=True)
