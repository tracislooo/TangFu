import sys
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy

root = Path('F:/Steam/steamapps/common/Football Manager 26/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for filename in ['ui-styles_assets_default.bundle', 'ui-styles_assets_1x.bundle',
                 'ui-styles_assets_2x.bundle', 'ui-styles_assets_4x.bundle', 'ui-styles_assets_common.bundle']:
    env = UnityPy.load(str(root / filename))
    for o in env.objects:
        if o.type.name != 'MonoBehaviour':
            continue
        try:
            d = o.read_typetree()
        except Exception:
            continue
        if 'm_Rules' not in d:
            continue
        for selector in d.get('m_ComplexSelectors', []):
                i = selector['ruleIndex']
                rule = d['m_Rules'][i]
                content = str(selector)
                if 'report-player-full-header-max' in content or 'report-player-banner-max' in content:
                    values = []
                    for p in rule['m_Properties']:
                        if p.get('m_Name') in ['height','min-height','max-height','opacity','padding','padding-top','padding-bottom']:
                            vv=[]
                            for v in p['m_Values']:
                                key={2:'floats',3:'dimensions',4:'colors',6:'assets',7:'strings'}.get(v['m_ValueType'])
                                vv.append(d[key][v['valueIndex']] if key else v)
                            values.append((p['m_Name'], vv))
                    print(filename,o.path_id,d['m_Name'],'rule',i,'selector',selector,'values',values)
