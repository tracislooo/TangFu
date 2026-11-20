import sys
import json
import re
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy
root = Path('G:/Doc/ChatGPT/New project')
env = UnityPy.load('F:/Steam/steamapps/common/Football Manager 26/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualfunctions_assets_all.bundle')
results = []
for o in env.objects:
    if o.type.name != 'MonoBehaviour':
        continue
    d = o.read_typetree()
    name = d.get('m_Name','')
    if re.search(r'display|style|switch|compar|greater|less|image|texture|condition|range', name, re.I):
        results.append({'pid':o.path_id,'tree':d})
        print('FUNCTION', o.path_id, name, 'keys', list(d))
(root / 'native-visual-functions-v28.json').write_text(json.dumps(results,ensure_ascii=False,indent=2),encoding='utf-8')
for o in env.objects:
    if o.type.name == 'AssetBundle':
        d = o.read_typetree()
        for key, value in d['m_Container']:
            if key in ['d47d9f6bfe419344692270d5af16c5ef','ccad53b4192c2ed41ad18bae0726dbe4']:
                print('TARGET_METADATA', key, value)
