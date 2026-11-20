import json
from pathlib import Path
d=json.loads(Path('inspect-old-fc--941100000001020.json').read_text('utf8'));rr={r['rid']:r for r in d['references']['RefIds']}
for i in [8274,8276,8277,8279,8283,8260]:
 a=rr[i]['data'];print(i,a);s=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print('SD',str(s)[-3000:])
