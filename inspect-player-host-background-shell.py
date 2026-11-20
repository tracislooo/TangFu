exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-player-host-background-shell-'))
for bn in [W,G]:
 ab=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
 for key,entry in meta['m_Container']:
  if key!='c560d7c346514c04f9c84c4b55b94bb4':continue
  d=objs[bn][entry['asset']['m_PathID']].read_typetree();
  if 'references' not in d:continue
  print('DOC',bn,entry['asset']['m_PathID'],d['m_Name']);rr=refs(d)
  for i,r in rr.items():
   v=r.get('data',{})
   if 'm_FullTypeName' in v:
    s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print(i,v.get('m_FullTypeName'),s.get('name'),v.get('m_TemplateAlias'))
    if any(k in v.get('m_FullTypeName','') for k in ['Gradient','Background','StyleSetter']):print(s)
  print('USINGS',d.get('m_Usings'))
d=objs[W][-716828569427839901].read_typetree();rr=refs(d);print('GAMEBG')
for i,r in rr.items():
 v=r.get('data',{})
 if 'm_FullTypeName' in v:print(i,v.get('m_FullTypeName'),rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{}))

