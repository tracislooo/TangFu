import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
G=Path(json.loads(Path('current-game-location.json').read_text())['bundle_root'])
for bn in ['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle']:
 for o in UnityPy.load(str(G/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' not in d:continue
  for i,r in enumerate(d['m_Rules']):
   txt=json.dumps(r.get('m_ComplexSelectors',[]))
   if any(k in txt for k in ['tabgroup__tab-settings--active','buttons-toggle-active','unity-dragger','slider__thumb','responsibilities-primary','buttongroup__button--active']):
    print(bn,d['m_Name'],i,json.dumps(r,ensure_ascii=False))
