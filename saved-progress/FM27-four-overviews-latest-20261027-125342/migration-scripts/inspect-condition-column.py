import json
from pathlib import Path
d=json.loads(Path('inspect-PlayerTableFactory.json').read_text())
def walk(v,path=''):
 if isinstance(v,dict):
  if any(isinstance(x,str) and x in ['condition','condition-icon','condition-in-match'] for x in v.values()):print(path,json.dumps(v)[:7000])
  for k,x in v.items():walk(x,path+'/'+k)
 elif isinstance(v,list):
  for i,x in enumerate(v):walk(x,path+'/'+str(i))
walk(d)
for f in Path('.').glob('inspect-TacticTeamSelection*.json'):
 d=json.loads(f.read_text());cols=d.get('m_tableView',{}).get('m_tableConfig',[]);a=[x['m_columnID'] for x in cols if 'condition' in x['m_columnID']]
 if a:print(f.stem,a)
