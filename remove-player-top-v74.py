import copy,datetime,hashlib,importlib.util,json,os,re,struct,subprocess,sys,zipfile
from pathlib import Path
R=Path(__file__).resolve().parent;O=R/'移除PlayerTop两张图片-V74-20261030';M=O/'删除及引用校验记录.json'
sha=lambda b:hashlib.sha256(b).hexdigest()
if '--package' in sys.argv:
 with zipfile.ZipFile(O.with_suffix('.zip'),'w',zipfile.ZIP_DEFLATED) as z:
  for f in O.rglob('*'):
   if f.is_file():z.write(f,f.relative_to(O))
 with zipfile.ZipFile(O.with_suffix('.zip')) as z:assert z.testzip() is None
 print('Backup package verified.');sys.exit(0)
if '--install' in sys.argv:
 m=json.loads(M.read_text('utf8'));assert not m['installed']
 proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
 if proc.stdout.strip():print('Game running: package prepared, installation pending.');sys.exit(0)
 loc=json.loads((R/'current-game-location.json').read_text('utf8'));game=Path(loc['bundle_root']).resolve();skin=Path(loc['skin_packages']).resolve()
 assert sha((R/'current-custom-textures.json').read_bytes())==m['before_registry_sha256']
 old={};desired={}
 for x in m['install_files']:
  p=Path(x['target']);assert p.parent.resolve() in [game,skin] and 'Project Taco' not in str(p)
  old[p]=p.read_bytes();assert sha(old[p])==x['before_sha256'];desired[p]=(O/x['source']).read_bytes();assert sha(desired[p])==x['after_sha256']
 for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h
 try:
  for p,b in desired.items():
   tmp=p.with_name(p.name+'.v74.tmp');tmp.write_bytes(b);os.replace(tmp,p);assert sha(p.read_bytes())==sha(b)
  for p,h in m['protected_sha256'].items():assert sha(Path(p).read_bytes())==h
 except BaseException:
  for p,b in old.items():p.write_bytes(b)
  raise
 (R/'current-custom-textures.json').write_bytes((O/'更新后的有效图片恢复来源.json').read_bytes())
 p=R/'AGENTS.md';s=p.read_text('utf8').replace('当前有效自定义图片为 180 张','当前有效自定义图片为 178 张')
 s+='\n- V74（2026-10-30）删除 PlayerTopBackground（-910000000000001）和 PlayerTopBlueLight（-910000000000002），清理纹理、目录/预加载及现有图片引用；后续恢复不得重新导入，其他卡面和布局保留。\n';p.write_text(s,'utf8')
 m.update(installed=True,installed_hash_verified=True,installed_at_utc=datetime.datetime.now(datetime.timezone.utc).isoformat());M.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'removed':m['removed'],'cleared_references_per_directory':m['cleared_references_per_directory'],'active_custom_images':m['active_custom_texture_count']}));sys.exit(0)
sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
assert not O.exists();loc=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(loc['bundle_root']);S=Path(loc['skin_packages']);AA=Path(loc['aa_root'])
assert 'Football Manager 27' in str(G) and 'Project Taco' not in str(G)
BN='ui-backgrounds_assets_common.bundle';WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
targets={-910000000000001:'PlayerTopBackground',-910000000000002:'PlayerTopBlueLight'}
regbytes=(R/'current-custom-textures.json').read_bytes();registry=json.loads(regbytes);banned={int(t['path_id']) for t in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
before={f/n:(f/n).read_bytes() for f in [G,S] for n in [BN,WN]};assert before[G/BN]==before[S/BN] and before[G/WN]==before[S/WN]
protected={p:sha(p.read_bytes()) for f in [G,S] for p in f.glob('*.bundle') if p.name not in [BN,WN]}
protected.update({p:sha(p.read_bytes()) for f in [AA,S] for p in [f/'catalog.bin',f/'catalog.hash'] if p.exists()})
e=UnityPy.load(before[G/BN]);a=e.assets[0];obs=a.objects;hashes={i:sha(o.get_raw_data()) for i,o in obs.items()};assert not(banned&set(obs))
for i,n in targets.items():assert obs[i].type.name=='Texture2D' and obs[i].peek_name()==n
aux={k:sha(v.bytes) for k,v in e.file.files.items() if k!=a.name};bundle=next(o for o in obs.values() if o.type.name=='AssetBundle');meta=bundle.read_typetree();old=copy.deepcopy(meta)
deleted=lambda p:isinstance(p,dict) and p.get('m_FileID')==0 and p.get('m_PathID') in targets
pre=old['m_PreloadTable'];keep=[not deleted(p) for p in pre];prefix=[0]
for v in keep:prefix.append(prefix[-1]+int(v))
meta['m_Container']=[(k,v) for k,v in meta['m_Container'] if not deleted(v['asset'])]
def remap(v):
 if isinstance(v,dict):
  if 'preloadIndex' in v and 'preloadSize' in v:
   start,size=v['preloadIndex'],v['preloadSize'];assert 0<=start<=start+size<=len(pre);v['preloadIndex']=prefix[start];v['preloadSize']=prefix[start+size]-prefix[start]
  for x in v.values():remap(x)
 elif isinstance(v,(list,tuple)):
  for x in v:remap(x)
remap(meta);meta['m_PreloadTable']=[p for p,k in zip(pre,keep) if k];assert len(old['m_Container'])-len(meta['m_Container'])==2 and len(pre)-len(meta['m_PreloadTable'])==2
bundle.save_typetree(meta)
for i in targets:del obs[i]
we=UnityPy.load(before[G/WN]);wa=we.assets[0];wh={i:sha(o.get_raw_data()) for i,o in wa.objects.items()};bgids={i+1 for i,x in enumerate(wa.externals) if x.path==f'archive:/{a.name}/{a.name}'};assert bgids
changes={};needles=[struct.pack('<q',i) for i in targets]
def clear(v):
 count=0
 if isinstance(v,dict):
  if v.get('m_PathID') in targets and v.get('m_FileID') in bgids:v.update(m_FileID=0,m_PathID=0);count+=1
  for x in v.values():count+=clear(x)
 elif isinstance(v,(list,tuple)):
  for x in v:count+=clear(x)
 return count
for i,o in wa.objects.items():
 if not any(n in o.get_raw_data() for n in needles):continue
 t=o.read_typetree();expected=copy.deepcopy(t);count=clear(t)
 if not count:continue
 assert o.type.name=='MonoBehaviour' and 'assets' in t
 for p in expected['assets']:
  if p.get('m_PathID') in targets and p.get('m_FileID') in bgids:p.update(m_FileID=0,m_PathID=0)
 assert t==expected,'Unexpected non-image layout change';o.save_typetree(t);changes[i]={'name':o.peek_name(),'cleared':count,'after':t}
assert sum(x['cleared'] for x in changes.values())==11
outputs={BN:e.file.save(packer='lz4'),WN:we.file.save(packer='lz4')}
be=UnityPy.load(outputs[BN]);sa=be.assets[0];sw=UnityPy.load(outputs[WN]).assets[0]
assert set(sa.objects)==set(hashes)-set(targets) and set(sw.objects)==set(wh)
for i,h in hashes.items():
 if i not in targets and i!=bundle.path_id:assert sha(sa.objects[i].get_raw_data())==h
for k,h in aux.items():assert sha(be.file.files[k].bytes)==h
for i,h in wh.items():
 if i not in changes:assert sha(sw.objects[i].get_raw_data())==h
 else:assert sw.objects[i].read_typetree()==changes[i]['after']
assert sa.objects[bundle.path_id].read_typetree()==meta
entries=dict(meta['m_Container'])
for k,v in old['m_Container']:
 if deleted(v['asset']):continue
 nv=entries[k];assert meta['m_PreloadTable'][nv['preloadIndex']:nv['preloadIndex']+nv['preloadSize']]==[p for p in pre[v['preloadIndex']:v['preloadIndex']+v['preloadSize']] if not deleted(p)]
for o in sw.objects.values():
 if any(n in o.get_raw_data() for n in needles):assert clear(o.read_typetree())==0
# Catalog registrations and exact owner-first dependencies remain valid.
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm);audits=[]
for folder,catdir in [(G,AA),(S,S)]:
 c=cm.Catalog((catdir/'catalog.bin').read_bytes());keys={k:p for k,p in c.keys() if isinstance(k,str)};locations={q for p in keys.values() for (q,) in c.array(p,'I')}
 def bl(n):return next(q for q in locations if c.location(q)['provider'].endswith('.AssetBundleProvider') and c.location(q)['internal'].endswith('\\'+n))
 bg=bl(BN);count=0
 for n in [WN,GN]:
  f=sw if n==WN else UnityPy.load(str(folder/n)).assets[0];owner=bl(n);bm=next(o.read_typetree() for o in f.objects.values() if o.type.name=='AssetBundle')
  for k,v in bm['m_Container']:
   if not re.fullmatch('[0-9a-f]{32}',k) or v['asset']['m_FileID']!=0:continue
   obj=f.objects.get(v['asset']['m_PathID'])
   if not obj or not(-1000000000000000<obj.path_id<-900000000000000) or obj.type.name!='MonoBehaviour':continue
   t=obj.read_typetree();typ='SI.VisualScripting.VisualFunction' if 'm_nodes' in t else ('UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in t else None)
   if not typ:continue
   assert k in keys
   for (q,) in c.array(keys[k],'I'):
    v=c.location(q);assert v['type'][1]==typ and v['dependencies'][0]==owner and bg in v['dependencies']
   count+=1
 audits.append({'catalog':str(catdir/'catalog.bin'),'custom_vta_vf_checked':count})
assert not (set(sa.objects)&(banned|set(targets)|{-910000000000146}))
for p in meta['m_PreloadTable']:assert p['m_PathID'] not in banned|set(targets)
current=copy.deepcopy(registry);current['textures']=[t for t in current['textures'] if int(t['path_id']) not in targets];assert len(current['textures'])==len(registry['textures'])-2
for t in current['textures']:assert sha(sa.objects[int(t['path_id'])].get_raw_data())==t['texture_sha256']
current.update(version=74,date='2026-10-30',authoritative_source_bundle=str(O/BN),source_bundle_sha256=sha(outputs[BN]),manifest=str(M),active_custom_texture_count=len(current['textures']))
current['restore_policy']=f"以当前来源清单迁移{len(current['textures'])}张有效自定义纹理；排除70个永久禁用ID、已删除TF patch及PlayerTopBackground/PlayerTopBlueLight，保留所有原生背景覆盖及界面关联规则。"
for i,n in targets.items():current.setdefault('removed_textures',[]).append({'name':n,'path_id':str(i),'removed_on':'2026-10-30','restore':False})
O.mkdir();installs=[]
for n,b in outputs.items():(O/n).write_bytes(b)
for p,b in before.items():
 tag='game' if p.parent==G else 'skin';rel=Path('回退')/tag/p.name;(O/rel).parent.mkdir(parents=True,exist_ok=True);(O/rel).write_bytes(b);installs.append({'target':str(p),'source':p.name,'backup':rel.as_posix(),'before_sha256':sha(b),'after_sha256':sha(outputs[p.name])})
(O/'回退'/'current-custom-textures.json').write_bytes(regbytes);(O/'更新后的有效图片恢复来源.json').write_text(json.dumps(current,ensure_ascii=False,indent=2),'utf8')
m={'version':74,'installed':False,'runtime_verified':False,'removed':[{'name':n,'path_id':str(i)} for i,n in targets.items()],'cleared_references_per_directory':11,'changed_styles':[{'path_id':str(i),'name':x['name'],'cleared':x['cleared']} for i,x in changes.items()],'active_custom_texture_count':len(current['textures']),'catalog_audits':audits,'install_files':installs,'protected_sha256':{str(p):h for p,h in protected.items()},'before_registry_sha256':sha(regbytes),'native_background_overrides_preserved':True,'layout_and_template_objects_unchanged':True}
M.write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(O/'安装.ps1').write_text("$ErrorActionPreference='Stop'\n& 'C:/Users/traci/.cache/codex-runtimes/codex-primary-runtime/dependencies/python/python.exe' '"+str(Path(__file__).resolve())+"' --install\nif($LASTEXITCODE -ne 0){throw 'Install failed.'}\n",'utf-8-sig')
lines=["$ErrorActionPreference='Stop'","if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}"]
for x in installs:lines.append("if((Get-FileHash -LiteralPath '"+x['target']+"' -Algorithm SHA256).Hash.ToLower() -ne '"+x['after_sha256']+"'){throw 'Rollback target version mismatch.'}")
for x in installs:lines.append("Copy-Item -LiteralPath (Join-Path $PSScriptRoot '"+x['backup']+"') -Destination '"+x['target']+"' -Force")
lines.append("Copy-Item -LiteralPath (Join-Path $PSScriptRoot '回退/current-custom-textures.json') -Destination '"+str(R/'current-custom-textures.json')+"' -Force")
(O/'回退.ps1').write_text('\n'.join(lines),'utf-8-sig')
(O/'说明.txt').write_text('V74：删除PlayerTopBackground、PlayerTopBlueLight及其目录/预加载记录，11个残留图片样式引用清空。游戏和皮肤目录同步。\n仅变更背景包及gameworld样式assets图片指针，其他对象、布局、绑定、合同模板控件ID、评分函数、catalog和原生背景覆盖保持不变。\n当前有效图片178张，70个永久禁用ID仍未占用。已删TF patch不恢复。恢复清单排除本次删除的两张图片。\n安装前退出游戏，运行安装.ps1。保留原包及恢复清单备份，回退.ps1用于故障回退。目标仅为Football Manager 27新目录及皮肤目录。未启动游戏或操作桌面验证。','utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
print(json.dumps({'prepared':True,'removed':list(targets.values()),'references_cleared':11,'active_after_install':len(current['textures']),'catalog_audits':audits}))
