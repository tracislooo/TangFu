from pathlib import Path
import sys,json,hashlib,shutil,datetime
R=Path(__file__).parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01')
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
O=R/'saved-progress'/('FM27-four-overviews-latest-'+stamp);O.mkdir(parents=True)
sha=lambda p:hashlib.sha256(p.read_bytes()).hexdigest()
shutil.copytree(S,O/'skin-tf27-01')
shutil.copy2(R/'FM27-最新版恢复说明.md',O/'RESTORE-NOTES.md')
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
for prefix in ['restore-approved-four-overviews-20261022-134518','fourth-transfer-fallback-radar250-20261022-140238','fourth-bans-tactics-radar-pros-rows-20261022-141739','fourth-native-tactics-wrapped-centered-pros-20261022-142532','first-native-pros-cons-text-transfer-fallback-20261022-221154','first-contained-scroll-transparent-fallback-20261022-223125','copy-first-region-second-fourth-bans-radar200-20261022-224531','four-status-rings-native-translations-20261022-230957','direct-four-condition-sharpness-percent-20261023-055814']:
 p=R/prefix/'manifest.json'
 if p.exists():shutil.copy2(p,O/'change-records'/(prefix+'.json'))
shutil.copytree(R/'outputs/fm27-resource-inventory-20261023',O/'resource-inventory',ignore=shutil.ignore_patterns('node_modules','*.png','*.mjs','*.py','*.ndjson'))
(O/'component-typetrees').mkdir();exported=[]
for name in bundle_names[:3]:
 env=UnityPy.load(str(G/name));obs={o.path_id:o for o in env.objects}
 ids={int(r[1]) for r in data['ui']+data['styles'] if r[4]==name}
 for pid in sorted(ids):
  obj=obs[pid];tree=obj.read_typetree();filename=name+'__'+str(pid)+'.json'
  (O/'component-typetrees'/filename).write_text(json.dumps(tree,ensure_ascii=False,indent=2,default=lambda v:list(v) if isinstance(v,(bytes,bytearray)) else str(v)),'utf8')
  exported.append({'bundle':name,'path_id':str(pid),'name':tree.get('m_Name',''),'file':filename})
# Fingerprint every archived file, then verify that copying preserved the current installations.
files=[{'path':str(p.relative_to(O)),'size':p.stat().st_size,'sha256':sha(p)} for p in O.rglob('*') if p.is_file()]
for c in checks:assert sha(G/c['bundle'])==c['game_sha256'];assert sha(O/'game-resources'/c['bundle'])==c['game_sha256']
manifest={'created_local':datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).isoformat(),'snapshot_kind':'latest requested implementation; supersedes 2026-10-22 approved snapshot','game_files_modified':False,'runtime_verified':False,'last_change':'Condition/Sharpness UI 1=1%,100=100%; all four versions','game_comparison':checks,'exported_components':exported,'files':files}
(O/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(R/'LATEST-FM27-PROGRESS.txt').write_text(str(O)+'\n'+str(O/'RESTORE-NOTES.md')+'\n','utf8')
print(json.dumps({'snapshot':str(O),'files':len(files),'components':len(exported),'bundles':len(bundle_names),'bytes':sum(f['size'] for f in files),'all_ui_game_skin_equal':all(c['same'] for c in checks[:4])},ensure_ascii=False))
