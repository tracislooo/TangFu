from pathlib import Path
import sys
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
base=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for bn in ['ui-styles_assets_common.bundle','ui-styles_assets_default.bundle']:
 for o in UnityPy.load(str(base/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' not in d:continue
  for r in d['m_Rules']:
   sel=str(r.get('m_ComplexSelectors',[]))
   props=[p for p in r['m_Properties'] if any(x in p.get('m_CustomName','').lower() for x in ['grid','tile-gap'])]
   if props or ('grid' in sel.lower() and any(x in sel.lower() for x in ['layout','gap','tile'])):
    print(bn,o.path_id,d.get('m_Name'),sel[:190],props or r['m_Properties'])
