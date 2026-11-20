from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'.codex-deps'))
import UnityPy
base=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for name in ['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle']:
 for o in UnityPy.load(str(base/name)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  for rule in d.get('m_Rules',[]):
   selectors=str(rule['m_ComplexSelectors'])
   if ('pitch-header' in selectors or 'TFPitchSwitches' in selectors) and any(p['m_Id']==458752 for p in rule['m_Properties']):print(name,o.path_id,d['m_Name'],selectors,rule['m_Properties'])
