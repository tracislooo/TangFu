from pathlib import Path
import json,hashlib,datetime
R=Path.cwd();WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
base=R/'touch-bar-dynamics-happiness-condition-20261018-235513';report=json.loads((base/'manifest.json').read_text(encoding='utf8'))
folders=[Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64'),Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')]
sha=lambda b:hashlib.sha256(b).hexdigest()
backup=(base/'backup-game'/WN).read_bytes();assert sha(backup)==report['before_sha256'][str(folders[0]/WN)]
stamp=datetime.datetime.now().strftime('%Y%m%d-%H%M%S');out=R/('rollback-crashed-four-statuses-'+stamp);out.mkdir()
manifest={'restored_sha256':sha(backup),'source':str(base/'backup-game'/WN),'files':{}}
for tag,folder in zip(['game','skin'],folders):
 current=(folder/WN).read_bytes();(out/('crashed-'+tag+'.bundle')).write_bytes(current)
 manifest['files'][str(folder/WN)]=sha(current)
for folder in folders:(folder/WN).write_bytes(backup);assert (folder/WN).read_bytes()==backup
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'rollback_complete':True,'backup':str(out),'restored_sha256':sha(backup)},ensure_ascii=False))
