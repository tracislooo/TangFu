from pathlib import Path
import json,hashlib,subprocess
R=Path.cwd();GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');sha=lambda b:hashlib.sha256(b).hexdigest()
OUT=next(p for p in sorted(R.glob('pinned-1-11-update-*'),reverse=True) if (p/'verification.json').exists());m=json.loads((OUT/'manifest.json').read_text('utf8'));assert not m['installed']
pending=[]
for n,h in m['new_game_before_sha256'].items():assert sha((GAME/n).read_bytes())==h,(n,'game changed during preparation')
for n,h in m['source_skin_sha256'].items():assert sha((SKIN/n).read_bytes())==h,(n,'skin changed during preparation')
assert sha((GAME.parent/'catalog.bin').read_bytes())==m['catalog_before_sha256']
for n,h in m['after_sha256'].items():
 b=(OUT/n).read_bytes();assert sha(b)==h
 for folder in [GAME,SKIN]:pending.append((folder/n,b))
pending.extend([(GAME.parent/'catalog.bin',(OUT/'catalog.bin').read_bytes()),(GAME.parent/'catalog.hash',(OUT/'catalog.hash').read_bytes()),(SKIN/'catalog.bin',(OUT/'catalog.bin').read_bytes()),(SKIN/'catalog.hash',(OUT/'catalog.hash').read_bytes()),(SKIN/'ui-backgrounds_assets_common.bundle',(GAME/'ui-backgrounds_assets_common.bundle').read_bytes())])
original={p:p.read_bytes() if p.exists() else None for p,b in pending}
for p,b in original.items():
 if b is None:continue
 tag='backup-install-game' if p.parent in [GAME,GAME.parent] else 'backup-install-skin';dest=OUT/tag/p.name;dest.parent.mkdir(exist_ok=True)
 if dest.exists():assert dest.read_bytes()==b
 else:dest.write_bytes(b)
process=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True);assert not process.stdout.strip(),'Close running game before installation'
try:
 for p,b in pending:p.write_bytes(b);assert p.read_bytes()==b
 assert sha((GAME/'ui-backgrounds_assets_common.bundle').read_bytes())==m['background_bundle_unchanged_sha256']
except BaseException:
 for p,b in original.items():
  if b is not None:p.write_bytes(b)
  elif p.exists():p.unlink()
 raise
m['installed']=True;m['installed_paths']=[str(p) for p,b in pending];(OUT/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p,b in original.items():
 if b is not None:
  tag='backup-install-game' if p.parent in [GAME,GAME.parent] else 'backup-install-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name).replace("'","''")+"' -Destination '"+str(p).replace("'","''")+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');print(json.dumps({'installed':True,'output':str(OUT),'files_written':len(pending),'background_bundle_unchanged':True},ensure_ascii=True))
