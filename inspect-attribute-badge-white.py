exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-attribute-badge-white-'))
for bn in [W,G]:
 ab=next(o for o in objs[bn].values() if o.type.name=='AssetBundle')
 for key,v in ab.read_typetree()['m_Container']:
  if key!='e61c9f83ee67aae4aadfec4ae509ae84':continue
  d=objs[bn][v['asset']['m_PathID']].read_typetree()
  if 'references' not in d:continue
  print('BADGE',bn,v['asset']['m_PathID'],d['m_Name']);rr=refs(d)
  for i,r in rr.items():
   a=r.get('data',{});s=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   if 'm_FullTypeName' in a:print(i,a['m_FullTypeName'],s.get('name'),a.get('m_Classes'),{k:v for k,v in s.items() if k in ['TextBinding','PrimaryColorDataLink','SecondaryColorDataLink']})
  print('usings',d.get('m_Usings'))
