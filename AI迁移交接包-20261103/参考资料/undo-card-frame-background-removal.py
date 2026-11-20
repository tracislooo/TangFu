from pathlib import Path
import hashlib,json,importlib.util,uuid,datetime,subprocess
R=Path.cwd();S=R/'player-report-remove-card-frame-background-20261101-142650';loc=json.loads((R/'current-game-location.json').read_text('utf-8-sig'));GAME=Path(loc['bundle_root']);SKIN=Path(loc['skin_packages']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';sha=lambda b:hashlib.sha256(b).hexdigest()
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);KEY=uuid.uuid5(uuid.NAMESPACE_URL,'FM27PlayerReportShellWithoutCardFrameBackground').hex;SOURCEKEY='c560d7c346514c04f9c84c4b55b94bb4'
outputs={};current={}
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for bn in [W,G]:
  p=folder/bn;b=p.read_bytes();assert b==(S/('prepared-'+tag)/bn).read_bytes(),('File changed after installation; stop full rollback',str(p));current[p]=b;outputs[p]=(S/('backup-'+tag)/bn).read_bytes()
 catfolder=GAME.parent if tag=='game' else SKIN;raw=(S/('backup-'+tag)/'catalog.bin').read_bytes();c=cm.Catalog(raw);source=next(x for x in c.locations(SOURCEKEY) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');expected=c.add_key_location(KEY,source,source)
 for name in ['catalog.bin','catalog.hash']:
  p=catfolder/name;b=p.read_bytes();assert b==(expected if name=='catalog.bin' else hashlib.md5(expected).hexdigest().encode('ascii')),('Catalog changed after installation',str(p));current[p]=b;outputs[p]=(S/('backup-'+tag)/name).read_bytes()
assert not subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True).stdout.strip(),'Exit game first'
OUT=R/('undo-card-frame-background-removal-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));OUT.mkdir()
for p,b in current.items():
 tag='game' if p.parent in [GAME,GAME.parent] else 'skin';f=OUT/('backup-'+tag);f.mkdir(exist_ok=True);(f/p.name).write_bytes(b)
try:
 for p,b in outputs.items():p.write_bytes(b);assert sha(p.read_bytes())==sha(b)
except BaseException:
 for p,b in current.items():p.write_bytes(b)
 raise
(OUT/'manifest.json').write_text(json.dumps({'installed':True,'reverted_only':str(S),'files_verified':len(outputs),'original_game_and_skin_restored':True,'runtime_verified':False},indent=2),'utf8')
print(json.dumps({'reverted':True,'files_verified':len(outputs),'record':str(OUT)}))
