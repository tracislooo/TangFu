from pathlib import Path
import json,hashlib
folders=[Path('game-retired-image-cleanup-20261111-195101'),Path('game-retired-image-cleanup-20261111-195226')]
ms=[json.loads((p/'manifest.json').read_text('utf8')) for p in folders]
changed={m['target'] for m in ms}
sha=lambda p:hashlib.sha256(Path(p).read_bytes()).hexdigest()
assert all(sha(m['target'])==m['after'] for m in ms)
assert all(sha(p)==h for p,h in ms[0]['protected_files'].items() if p not in changed)
report={'installed':True,'transactions':[str(p.resolve()) for p in folders],'files':[m['target'] for m in ms],'invalid_image_values':1277,'retired_selectors':3,'retired_empty_nodes':19,'other_bundles_catalog_unchanged':True,'runtime_tested':False}
(folders[0]/'combined-manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
lines=["$ErrorActionPreference='Stop'"]
for m in ms:lines.append("if ((Get-FileHash -LiteralPath '"+m['target']+"').Hash.ToLower() -ne '"+m['after']+"') { throw 'Later changes detected' }")
for p in reversed(folders):lines.append("& '"+str((p/'restore.ps1').resolve())+"'")
(folders[0]/'restore-all.ps1').write_text('\n'.join(lines),'utf-8-sig')
print(json.dumps(report))
