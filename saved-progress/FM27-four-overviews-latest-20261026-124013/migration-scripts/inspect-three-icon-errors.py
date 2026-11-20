from pathlib import Path
import json
p=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log')
seen=set()
for l in p.read_text(encoding='utf8',errors='replace').splitlines():
 if l.startswith('{'):
  try:
   j=json.loads(l);m=j.get('Message','')
   if j.get('LogLevel') in ['Critical','Error','Warning'] and m not in seen:
    seen.add(m);print(j.get('Timestamp'),m[:1200])
  except:pass
 elif any(s in l for s in ['NullReferenceException:','ArgumentException:','InvalidOperationException:','Assertion failed','Crash!!!','SIGSEGV','Access Violation','Stack overflow']):print(l[:1000])
