import copy,datetime,hashlib,importlib.util,json,re,struct,sys
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');WIN=G/'StandaloneWindows64'
O=R/'修复卡片模板目录缺失-V58-20261027';assert not (O/'修复记录.json').exists();O.mkdir(exist_ok=True);sha=lambda b:hashlib.sha256(b).hexdigest()
BN='ui-backgrounds_assets_common.bundle';WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
newbg=(R/'CA180新版替换并核对引用-V57-20261027'/BN).read_bytes()
snap={p:p.read_bytes() for p in [G/'catalog.bin',S/'catalog.bin',WIN/BN,S/BN,WIN/WN,WIN/GN,S/WN,S/GN]}
assert sha(newbg)=='77f568302b598735580f53a9583f498f9bc66517847857cb7a3db8671fdda481'
assert sha(snap[WIN/BN])==sha(snap[S/BN])=='fec2fad617543fa35e4983b89580c95247260d179deca73bd22b2689936dc52d'
assets={};records={}
for n in [WN,GN]:
 env=UnityPy.load(snap[WIN/n]);af=env.assets[0];assets[n]=af
 meta=next(o for o in env.objects if o.type.name=='AssetBundle').read_typetree()
 valid=[]
 for k,v in meta['m_Container']:
  if not re.fullmatch('[0-9a-f]{32}',k):continue
  p=v['asset'];obj=af.objects.get(p['m_PathID']) if p['m_FileID']==0 else None
  if not obj:continue
  t=obj.read_typetree() if obj.type.name=='MonoBehaviour' else {}
  if 'm_VisualElementAssets' in t or ('references' in t and 'inlineSheet' in t):valid.append((k,obj.path_id,obj.peek_name()))
 records[n]=valid
outputs={};reports=[]
for catalog_path in [G/'catalog.bin',S/'catalog.bin']:
 raw=snap[catalog_path];c=cm.Catalog(raw);originalkeys=c.keys();keyset={k for k,_ in originalkeys if isinstance(k,str)}
 locations={v for _,ptr in originalkeys for (v,) in c.array(ptr,'I')}
 def bundleloc(n):
  found=[loc for loc in locations if c.location(loc)['provider'].endswith('.AssetBundleProvider') and c.location(loc)['internal'].endswith('\\'+n)]
  assert len(found)==1;return found[0]
 bg=bundleloc(BN);world=bundleloc(WN);glob=bundleloc(GN);added=[]
 for n in [WN,GN]:
  valid=records[n];bnloc=bundleloc(n)
  candidates=[]
  for k,pid,name in valid:
   if k not in keyset:continue
   for loc in c.locations(k):
    d=c.location(loc)
    if d['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' and bnloc in d['dependencies']:candidates.append(loc)
   if candidates:break
  assert candidates
  template=candidates[0]
  for k,pid,name in valid:
   if k in keyset:continue
   c=cm.Catalog(c.add_key_location(k,template,template));keyset.add(k);added.append({'guid':k,'name':name,'bundle':n,'path_id':str(pid)})
 # Ensure addressable loads retain the external background dependency.
 locations={v for _,ptr in c.keys() for (v,) in c.array(ptr,'I')};arrays={};depfix=[]
 for loc in sorted(locations):
  fields=c.unpack(loc,'7I');deps=[x[0] for x in c.array(fields[3],'I')]
  if not ({world,glob}&set(deps)) or bg in deps:continue
  if fields[3] not in arrays:arrays[fields[3]]=c.append(struct.pack('<'+'I'*(len(deps)+1),*(deps+[bg])),True)
  struct.pack_into('<I',c.data,loc+12,arrays[fields[3]]);depfix.append(loc)
 out=bytes(c.data);cc=cm.Catalog(out)
 checkedkeys={key for key,_ in cc.keys() if isinstance(key,str)}
 for k,pid,name in records[WN]+records[GN]:assert k in checkedkeys
 # Original location properties and dependency ordering must survive.
 old=cm.Catalog(raw);oldlocs={v for _,ptr in old.keys() for (v,) in old.array(ptr,'I')}
 assert cc.keys()[:len(originalkeys)]==originalkeys
 for loc in oldlocs:
  a=old.location(loc);b=cc.location(loc)
  assert all(a[k]==b[k] for k in ['primary','internal','provider','type'])
  assert b['dependencies']==a['dependencies']+([bg] if loc in depfix else [])
 outputs[catalog_path]=out;reports.append({'target':str(catalog_path),'added_registrations':added,'background_dependency_locations_fixed':len(depfix),'old_records_preserved':True})
tag='64033a72b9925c8dad3b08826077c328'
c=cm.Catalog(outputs[G/'catalog.bin']);assert c.locations(tag)
for loc in c.locations(tag):assert world in c.location(loc)['dependencies'] and bg in c.location(loc)['dependencies']
outputs[WIN/BN]=newbg;outputs[S/BN]=newbg
items=[]
for i,(p,b) in enumerate(outputs.items()):
 tag=('game-' if p==G/'catalog.bin' or p.parent==WIN else 'skin-')+p.name
 (O/tag).write_bytes(b);backup=Path('回退')/tag;(O/backup).parent.mkdir(exist_ok=True);(O/backup).write_bytes(snap[p])
 items.append({'target':str(p),'source':tag,'backup':backup.as_posix(),'before_sha256':sha(snap[p]),'after_sha256':sha(b)})
logroot=Path.home()/'AppData/LocalLow/Sports Interactive/Football Manager 27';(O/'诊断日志').mkdir()
for n in ['Player.log','Player-prev.log']:
 if (logroot/n).exists():(O/'诊断日志'/n).write_bytes((logroot/n).read_bytes())
manifest={'version':58,'installed':False,'runtime_verified':False,'cause_evidence':'Player.log first failure: Failed to load VisualTreeAsset 64033a72b9925c8dad3b08826077c328; GUID absent from game catalog but present in current gameworld container and object table.','catalog_repairs':reports,'install_files':items,'ui_bundles_unchanged':{str(p):sha(b) for p,b in snap.items() if p.name in [WN,GN]},'active_images':173,'retired_70_ids_not_restored':True}
(O/'修复记录.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
rows='\n'.join("@{Target='"+x['target']+"';Source='"+x['source']+"';Before='"+x['before_sha256']+"';After='"+x['after_sha256']+"'}" for x in items)
script="""$ErrorActionPreference='Stop'
if(Get-Process -Name fm -ErrorAction SilentlyContinue){throw 'Exit Football Manager first.'}
$items=@(
"""+rows+"""
)
foreach($item in $items){if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.Before){throw 'Target version mismatch.'};if((Get-FileHash -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Package checksum mismatch.'}}
$written=@()
try{foreach($item in $items){$written+=@{Target=$item.Target;Bytes=[IO.File]::ReadAllBytes($item.Target)};Copy-Item -LiteralPath (Join-Path $PSScriptRoot $item.Source) -Destination $item.Target -Force;if((Get-FileHash -LiteralPath $item.Target -Algorithm SHA256).Hash.ToLower() -ne $item.After){throw 'Install verification failed.'}}}catch{foreach($entry in $written){[IO.File]::WriteAllBytes($entry.Target,$entry.Bytes)};throw}
Write-Output 'Complete.'
"""
(O/'安装.ps1').write_text(script,'utf-8-sig')
for p,b in snap.items():assert p.read_bytes()==b
print(json.dumps({'output':str(O),'catalog_repairs':[(r['target'],len(r['added_registrations']),r['background_dependency_locations_fixed']) for r in reports]},ensure_ascii=False),flush=True)
