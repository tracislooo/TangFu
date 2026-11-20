exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','remove-player-top-backgrounds-'))
for bn in [W,G]:
 for pid,o in objs[bn].items():
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'references' not in d or 'inlineSheet' not in d:continue
  rr=refs(d);hits=[]
  for i,r in rr.items():
   v=r.get('data',{})
   if 'm_FullTypeName' in v:
    name=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name','')
    if any(s.lower() in name.lower() for s in ['PlayerTopBackground','BlueLight']):hits.append((i,name,v.get('m_Parent')))
  if hits:print(bn,pid,d.get('m_Name'),hits)
