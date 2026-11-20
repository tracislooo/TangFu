from pathlib import Path
import importlib.util
spec=importlib.util.spec_from_file_location('catalog','catalog-binary-v35.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
for p in [Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/catalog.bin'),Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/catalog.bin')]:
 c=m.Catalog(p.read_bytes())
 for card,source in [('6ed5dfdc99cd53b282b9e69d836f8941','b1f80633e62ce0e43b18cbe67256ad14'),('d8b28e612b34531ba0f09ff5a425e022','eb433e33a56539049910c63aabdec0d2')]:
  def get(g):return c.location(next(x for x in c.locations(g) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'))
  loc=get(card);deps={c.location(x)['internal'] for x in loc['dependencies']};expected={c.location(x)['internal'] for x in get(source)['dependencies']};print(p.parent,card,'missing deps',expected-deps);assert not expected-deps
 print('all source dependencies present')
