exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-player-team-colour-overlay-'))
for bn in [W,G]:
 for pid,o in objs[bn].items():
  if o.type.name!='MonoBehaviour':continue
  name=o.peek_name()
  if not name or not any(k in name.lower() for k in ['playersite','personsite','playerprofile','gameworldbackground','basesite','basebackground','tooltab','personbackground']):continue
  doc=o.read_typetree()
  if 'references' not in doc:continue
  rr=refs(doc);print('DOC',bn,pid,name)
  for i,r in rr.items():
   v=r.get('data',{})
   if 'm_FullTypeName' not in v:continue
   s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});n=s.get('name','')
   if 'Gradient' in v['m_FullTypeName'] or any(k in n.lower() for k in ['background','colour','color','gradient']):print(i,v['m_FullTypeName'],n,'parent',v.get('m_Parent'),json.dumps({k:x for k,x in s.items() if any(t in k for t in ['Binding','Color','Colour','DataLink']) and not k.endswith('UxmlAttributeFlags')},ensure_ascii=False)[:650])
