import json,re
from pathlib import Path
for f in ['probe--1956312186672579198.json','probe-2951970324711735998.json']:
 d=json.loads(Path(f).read_text('utf8'))
 for r in d['references']['RefIds']:
  a=r.get('data',{})
  for k in ['BindFunction','Binding','TextBinding','ImageBinding']:
   if k not in a:continue
   def scan(x):
    if isinstance(x,dict):
     for k,v in x.items():
      if k=='m_argumentBytes' and v: print(re.findall(rb'[ -~]{4,}',bytes(v)))
      else:scan(v)
    elif isinstance(x,list):
     for y in x:scan(y)
   print(f,r['rid'],k);scan(a[k])

