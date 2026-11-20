exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for o in objects.values():
 if o.type.name=='MonoBehaviour' and b'Overall Happiness' in o.get_raw_data():
  d=o.read_typetree();sr={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
  for i,r in sr.items():
   if r.get('data',{}).get('DebugDisplay')=='Overall Happiness':
    n=next((n for n in sr.values() if n.get('data',{}).get('m_SerializedData',{}).get('rid')==i),None)
    print(o.path_id,d.get('m_Name'),i,'node',n['rid'] if n else None)
