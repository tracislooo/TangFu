import json
from pathlib import Path
p=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log')
seen={}
for l in p.read_text(encoding='utf8',errors='replace').splitlines():
 if l.startswith('{'):
  try:
   j=json.loads(l);m=j.get('Message','');seen[m]=j.get('Timestamp')
  except:pass
for m,t in seen.items():
 if any(s in m.lower() for s in ['preload','context','menu','binding','exception','failed']):print(t,m[:1400])
