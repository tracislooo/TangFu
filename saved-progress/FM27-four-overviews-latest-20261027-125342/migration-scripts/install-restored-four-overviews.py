from pathlib import Path
import json,hashlib,subprocess
R=Path.cwd();GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=next(p for p in sorted(R.glob('restore-approved-four-overviews-*'),reverse=True) if (p/'verification.json').exists());m=json.loads((OUT/'manifest.json').read_text('utf8'));assert not m['installed']
for n,h in m['new_game_before_sha256'].items():assert sha((GAME/n).read_bytes())==h,('game changed during preparation',n)
for n,h in m['source_skin_sha256'].items():assert sha((SKIN/n).read_bytes())==h,('skin changed during preparation',n)
assert sha((GAME.parent/'catalog.bin').read_bytes())==m['catalog_before_sha256']
pending=[]
for n,h in m['after_sha256'].items():
 b=(OUT/n).read_bytes();assert sha(b)==h
 for folder in [GAME,SKIN]:pending.append((folder/n,b))
for p,b in [(GAME.parent/'catalog.bin',(OUT/'catalog.bin').read_bytes()),(GAME.parent/'catalog.hash',(OUT/'catalog.hash').read_bytes()),(SKIN/'catalog.bin',(OUT/'catalog.bin').read_bytes()),(SKIN/'catalog.hash',(OUT/'catalog.hash').read_bytes()),(SKIN/'ui-backgrounds_assets_common.bundle',(GAME/'ui-backgrounds_assets_common.bundle').read_bytes())]:pending.append((p,b))
cache=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
if cache.exists():
 current=cache.read_bytes();assert current==(OUT/'backup-custom-layout.json').read_bytes(),'saved layout changed during preparation'
 data=json.loads(current);saved=json.loads((Path(m['approved_snapshot'])/'saved-layout'/cache.name).read_bytes())
 for binding in saved['m_placementBindings']:
  if binding not in data['m_placementBindings']:data['m_placementBindings'].append(binding)
 if data!=json.loads(current):pending.append((cache,json.dumps(data,ensure_ascii=False,separators=(',',':')).encode('utf8')))
original={p:p.read_bytes() if p.exists() else None for p,b in pending}
for p,b in original.items():
 if b is None:continue
 tag='backup-cache' if p==cache else 'backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin';dest=OUT/tag/p.name;dest.parent.mkdir(exist_ok=True)
 if dest.exists():assert dest.read_bytes()==b
 else:dest.write_bytes(b)
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));raise SystemExit(0)
try:
 for p,b in pending:p.write_bytes(b);assert p.read_bytes()==b
 assert sha((GAME/'ui-backgrounds_assets_common.bundle').read_bytes())==m['background_bundle_unchanged_sha256']
except BaseException:
 for p,b in original.items():
  if b is not None:p.write_bytes(b)
  elif p.exists():p.unlink()
 raise
restore=['$ErrorActionPreference = "Stop"']
for p,b in original.items():
 if b is not None:
  tag='backup-cache' if p==cache else 'backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin'
  restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name).replace("'","''")+"' -Destination '"+str(p).replace("'","''")+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
m.update(installed=True,installed_verified=True,installed_paths=[str(p) for p,b in pending],native_background_untouched=True,existing_custom_fonts_preserved=True)
(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
(R/'LATEST-FM27-RESTORE.txt').write_text(str(OUT.resolve())+'\n','utf8')
print(json.dumps({'installed':True,'output':str(OUT),'files_synced':len(pending),'versions':4,'background_preserved':True,'fonts_preserved':True}))
