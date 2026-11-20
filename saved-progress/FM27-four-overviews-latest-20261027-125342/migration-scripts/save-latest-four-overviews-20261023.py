from pathlib import Path
import sys,json,hashlib,shutil,datetime
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01')
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
O=R/'saved-progress'/('FM27-four-overviews-latest-'+stamp);O.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copytree(S,O/'skin-tf27-01')
shutil.copy2(R/'FM27-最新版恢复说明.md',O/'RESTORE-NOTES.md')
for document in ['球员位置模块统一恢复顺序.md','球员弹窗最终版本说明.md','球员弹窗最终版本资源快照.json','AGENTS.md','reserved-texture-ids.json','current-custom-textures.json']:
 shutil.copy2(R/document,O/document)
data=json.loads((R/'outputs/fm27-resource-inventory-20261023/inventory.json').read_text('utf8'))
bundle_names=[r[0] for r in data['bundles']];(O/'game-resources').mkdir();checks=[]
for name in bundle_names:
 p=G/name;shutil.copy2(p,O/'game-resources'/name)
 skin=S/'packages'/name;checks.append({'bundle':name,'game_sha256':sha(p),'skin_sha256':sha(skin) if skin.exists() else None,'same':skin.exists() and sha(p)==sha(skin)})
for n in ['catalog.bin','catalog.hash']:
 if (G.parent/n).exists():shutil.copy2(G.parent/n,O/'game-resources'/n)
layout=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
if layout.exists():(O/'saved-layout').mkdir();shutil.copy2(layout,O/'saved-layout'/layout.name)
(O/'migration-scripts').mkdir()
for p in R.iterdir():
 if p.is_file() and p.suffix.lower() in ['.py','.ps1']:shutil.copy2(p,O/'migration-scripts'/p.name)
(O/'change-records').mkdir()
for folder,filename in [('seven-ca-range-switch-20261027-125118','manifest.json'),('repair-fc-rating-functions-catalog-20261027-051559','manifest.json'),('七张CA更新及新增150和170-V59-20261027','图片及引用校验记录.json')]:
 shutil.copy2(R/folder/filename,O/'change-records'/(folder+'.json'))
for prefix in ['restore-approved-four-overviews-20261022-134518','fourth-transfer-fallback-radar250-20261022-140238','fourth-bans-tactics-radar-pros-rows-20261022-141739','fourth-native-tactics-wrapped-centered-pros-20261022-142532','first-native-pros-cons-text-transfer-fallback-20261022-221154','first-contained-scroll-transparent-fallback-20261022-223125','copy-first-region-second-fourth-bans-radar200-20261022-224531','four-status-rings-native-translations-20261022-230957','direct-four-condition-sharpness-percent-20261023-055814','overview-position-rectangle-zones-20261026-123653','fix-overview-position-zones-fit-pitch-20261026-124834']:
 p=R/prefix/'manifest.json'
 if p.exists():shutil.copy2(p,O/'change-records'/(prefix+'.json'))
shutil.copytree(R/'outputs/fm27-resource-inventory-20261023',O/'resource-inventory',ignore=shutil.ignore_patterns('node_modules','*.png','*.mjs','*.py','*.ndjson'))
(O/'component-typetrees').mkdir();exported=[]
for name in bundle_names[:3]:
 env=UnityPy.load(str(G/name));obs={o.path_id:o for o in env.objects}
 ids={int(r[1]) for r in data['ui']+data['styles'] if r[4]==name}
 if name=='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle':ids.update([-940000000018000,-940000000018001])
 for pid in sorted(ids):
  obj=obs[pid];tree=obj.read_typetree();filename=name+'__'+str(pid)+'.json'
  (O/'component-typetrees'/filename).write_text(json.dumps(tree,ensure_ascii=False,indent=2,default=lambda v:list(v) if isinstance(v,(bytes,bytearray)) else str(v)),'utf8')
  exported.append({'bundle':name,'path_id':str(pid),'name':tree.get('m_Name',''),'file':filename})
# Fingerprint every archived file, then verify that copying preserved the current installations.
files=[{'path':str(p.relative_to(O)),'size':p.stat().st_size,'sha256':sha(p)} for p in O.rglob('*') if p.is_file()]
for c in checks:assert sha(G/c['bundle'])==c['game_sha256'];assert sha(O/'game-resources'/c['bundle'])==c['game_sha256']
manifest={'created_local':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat(),'snapshot_kind':'current files; historical snapshots remain references only','game_files_modified':False,'runtime_verified':False,'last_change':'V59 existing seven CA textures installed with user-defined CA ranges; 175 active images and 70 permanently retired IDs. Preserve current black pitch and 40% position fills; overview versions 3 and 4 share one pitch module','ca_range_restore_record':'seven-ca-range-switch-20261027-125118/manifest.json','position_restore_guide':'球员位置模块统一恢复顺序.md','position_restore_rule':'Follow P00-P08 once per unique shared resource; do not replay historical scripts by date','game_comparison':checks,'exported_components':exported,'files':files}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(R/'LATEST-FM27-PROGRESS.txt').write_text(str(O)+'\n'+str(O/'RESTORE-NOTES.md')+'\n','utf8')
print(json.dumps({'snapshot':str(O),'files':len(files),'components':len(exported),'bundles':len(bundle_names),'bytes':sum(f['size'] for f in files),'all_ui_game_skin_equal':all(c['same'] for c in checks[:4])},ensure_ascii=False))
