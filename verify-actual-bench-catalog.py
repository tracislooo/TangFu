from pathlib import Path
import importlib.util,json,sys
spec=importlib.util.spec_from_file_location('catalog','catalog-binary-v35.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
paths=[Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/catalog.bin'),Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/catalog.bin')]
for p in paths:
 c=m.Catalog(p.read_bytes());guid='d8b28e612b34531ba0f09ff5a425e022';loc=next(x for x in c.locations(guid) if c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset');l=c.location(loc);assert 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle' in c.location(l['dependencies'][0])['internal'];idx=next(i for i,(k,_) in enumerate(c.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=c.key_records[idx];assert loc in [v[0] for v in c.array(ls,'I')];print(p.parent,'compact card catalog/preload OK')
