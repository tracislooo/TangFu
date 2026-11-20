from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
base=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for n in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']:
 oo={o.path_id:o for o in UnityPy.load(str(base/n)).objects};print('BUNDLE',n)
 for pid,o in oo.items():
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name() or ''
  if any(k.lower() in name.lower() for k in ['PositionAbilityWith','PositionSelector','RoleSelector']):print(pid,name)
