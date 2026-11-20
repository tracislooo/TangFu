import json
import re
import struct
from pathlib import Path
root = Path('G:/Doc/ChatGPT/New project')
report = json.loads((root / 'ca-binding-inspection-v28.json').read_text(encoding='utf-8'))
for item in report:
    exact = []
    for r in item['records']:
        s = json.dumps(r)
        paths = re.findall(r'"m_path": "([^"]+)"', s)
        if any('PlayerCurrentAbility' in p for p in paths):
            exact.append({'rid':r['rid'],'class':r['type']['class'],'paths':paths})
    if exact:
        print('EXACT', item['name'], item['pid'], json.dumps(exact))
    if item['name'] == 'report-player-banner-max':
        for r in item['records']:
            if r['type']['class'] == 'SIStyleSetter/UxmlSerializedData':
                d = r['data']
                f = d['BindFunction']
                b = bytes(f['m_inputs']['m_variable']['m_argumentBytes'])
                print('BANNER_SETTER',r['rid'],d['name'],f['m_target'],re.findall(rb'[a-zA-Z][a-zA-Z0-9_.:<>\- ]{3,}', b))
