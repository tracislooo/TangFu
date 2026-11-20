import sys,json,re,hashlib,datetime,importlib.util,subprocess
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');GAME=AA/'StandaloneWindows64';SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';BN='ui-backgrounds_assets_common.bundle'
sha=lambda b:hashlib.sha256(b).hexdigest()
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S');OUT=R/('repair-fc-rating-functions-catalog-'+stamp);OUT.mkdir()
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures'];reserved_ids={int(x['path_id']) for x in reserved};reserved_names={x['name'].lower() for x in reserved}
protected={p:sha(p.read_bytes()) for f in [GAME,SKIN] for p in [f/GN,f/WN,f/BN,f/'ui-tileslayouts_assets_all.bundle']}
# Explicitly verify the retired objects are absent; no image bundle is repacked.
be=UnityPy.load(str(GAME/BN));bo={o.path_id:o for o in be.objects};bm=next(o.read_typetree() for o in be.objects if o.type.name=='AssetBundle')
assert reserved_ids.isdisjoint(bo)
for o in be.objects:
 if o.type.name=='Texture2D':assert o.peek_name().lower() not in reserved_names
for key,entry in bm['m_Container']:assert key.lower() not in reserved_names and entry['asset']['m_PathID'] not in reserved_ids
assert all(p['m_PathID'] not in reserved_ids for p in bm['m_PreloadTable'])
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'));assert len(registry['textures'])==173
for t in registry['textures']:assert int(t['path_id']) in bo and bo[int(t['path_id'])].peek_name()==t['name']
e=UnityPy.load(str(GAME/GN));obs={o.path_id:o for o in e.objects};meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle');functions=[];vta=[]
for key,entry in meta['m_Container']:
 if not re.fullmatch('[0-9a-f]{32}',key) or entry['asset']['m_FileID']!=0:continue
 o=obs.get(entry['asset']['m_PathID'])
 if not o or o.type.name!='MonoBehaviour':continue
 d=o.read_typetree()
 if 'm_nodes' in d:functions.append({'guid':key,'path_id':str(o.path_id),'name':d['m_Name']})
 elif 'inlineSheet' in d:vta.append(key)
assert len(functions)==15 and sum(x['name'].startswith('OverviewCard') and x['name'].endswith('Rating') for x in functions)==11
before={p:p.read_bytes() if p.exists() else None for f in [AA,SKIN] for p in [f/'catalog.bin',f/'catalog.hash']};outputs={};audits=[]
for f in [AA,SKIN]:
 path=f/'catalog.bin';raw=before[path];c=cm.Catalog(raw);old=c.keys();keys={k for k,_ in old if isinstance(k,str)};alllocs={loc for _,ptr in old for (loc,) in c.array(ptr,'I')}
 gloc=next(loc for loc in alllocs if c.location(loc)['provider'].endswith('.AssetBundleProvider') and c.location(loc)['internal'].endswith('\\'+GN))
 nativevf=next(loc for loc in alllocs if c.location(loc)['type'][1]=='SI.VisualScripting.VisualFunction' and c.location(loc)['provider'].endswith('.BundledAssetProvider'))
 dependency_template=next(loc for key in vta if key in keys for loc in c.locations(key) if c.location(loc)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' and c.location(loc)['dependencies'] and c.location(loc)['dependencies'][0]==gloc)
 added=[]
 for row in functions:
  key=row['guid']
  if key not in keys:c=cm.Catalog(c.add_key_location(key,nativevf,dependency_template));keys.add(key);added.append(row)
  locs=c.locations(key);assert locs
  for loc in locs:
   v=c.location(loc);assert v['internal']==key and v['type'][1]=='SI.VisualScripting.VisualFunction' and v['provider'].endswith('.BundledAssetProvider') and v['dependencies'][0]==gloc,(key,v)
 out=bytes(c.data);cc=cm.Catalog(out);assert cc.keys()[:len(old)]==old
 oldc=cm.Catalog(raw)
 for loc in alllocs:assert cc.unpack(loc,'7I')==oldc.unpack(loc,'7I'),('existing catalog entry changed',loc)
 outputs[path]=out;outputs[f/'catalog.hash']=hashlib.md5(out).hexdigest().encode('ascii');audits.append({'target':str(path),'added':added,'all_15_function_registrations_valid':True,'old_locations_unchanged':True})
# Check actual UI references to these functions, including full pages and hovering cards.
usages=[]
for bn in [GN,WN]:
 en=e if bn==GN else UnityPy.load(str(GAME/bn))
 for o in en.objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'inlineSheet' not in d:continue
  targets=set()
  def visit(v):
   if isinstance(v,dict):
    if 'm_target' in v and isinstance(v['m_target'],dict):
     key=v['m_target'].get('m_guid')
     if key in {f['guid'] for f in functions}:targets.add(key)
    for x in v.values():visit(x)
   elif isinstance(v,list):
    for x in v:visit(x)
  visit(d)
  if targets:usages.append({'bundle':bn,'name':d['m_Name'],'path_id':str(o.path_id),'functions':sorted(targets)})
assert any('Overview' in x['name'] for x in usages)
for tag,f in [('game',AA),('skin',SKIN)]:
 for name in ['catalog.bin','catalog.hash']:
  (OUT/tag).mkdir(exist_ok=True);(OUT/tag/name).write_bytes(outputs[f/name])
  if before[f/name] is not None:(OUT/('backup-'+tag)).mkdir(exist_ok=True);(OUT/('backup-'+tag)/name).write_bytes(before[f/name])
logroot=Path.home()/'AppData/LocalLow/Sports Interactive/Football Manager 27'
if (logroot/'Player.log').exists():__import__('shutil').copy2(logroot/'Player.log',OUT/'Player-before.log')
report={'installed':False,'runtime_verified':False,'cause':'custom VisualFunction objects exist in global bundle but all 15 registrations missing from game catalog; Player.log reports six outfield and five goalkeeper rating loads returning NULL','catalog_repairs':audits,'verified_function_objects':functions,'verified_ui_usages':usages,'ratings_formulas_unchanged':True,'bundle_files_unchanged':protected,'reserved_70_absent':True,'active_173_verified':True,'after_sha256':{str(p):sha(b) for p,b in outputs.items()}}
report['bundle_files_unchanged']={str(p):h for p,h in protected.items()}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert (p.read_bytes() if p.exists() else None)==b
for p,h in protected.items():assert sha(p.read_bytes())==h
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
for p,b in before.items():
 if b is not None:restore.append("Copy-Item -LiteralPath '"+str(OUT/('backup-game' if p.parent==AA else 'backup-skin')/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
 for p,b in outputs.items():p.write_bytes(b);assert p.read_bytes()==b
 for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
 for p,b in before.items():
  if b is not None:p.write_bytes(b)
 raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');print(json.dumps({'installed':True,'output':str(OUT),'game_registrations_added':len(audits[0]['added']),'card_rating_functions':11,'ui_assets_checked':len(usages),'images_unchanged':True}))
