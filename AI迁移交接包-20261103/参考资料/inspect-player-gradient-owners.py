exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-player-gradient-owners-'))
for bn in [W,G]:
 for pid,o in objs[bn].items():
  if o.type.name!='MonoBehaviour':continue
  doc=o.read_typetree()
  if 'references' not in doc:continue
  rr=refs(doc)
  hits=[]
  for i,r in rr.items():
   v=r.get('data',{});t=v.get('m_FullTypeName','');s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});n=s.get('name','')
   if t=='SI.Bindable.SIGradient' and (any(k in doc.get('m_Name','').lower() for k in ['player','person','profile','background','site','tool']) or any(k in n.lower() for k in ['background','colour','color'])):hits.append((i,n,v.get('m_Parent'),s))
  if hits:
   print('DOC',bn,pid,doc['m_Name'])
   for i,n,p,s in hits:print(i,n,p,{k:v for k,v in s.items() if k not in ['bindings'] and not k.endswith('UxmlAttributeFlags') and k not in ['dataSourcePathString','dataSourceTypeString','dataSourceUnityObject']})
