exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-first-background-'))
for pid in [-930000000001001,-910000000000201]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);print('DOC',pid,doc.get('m_Name'),'USINGS',doc.get('m_Usings'))
 for i,r in rr.items():
  v=r.get('data',{})
  if 'm_FullTypeName' not in v:continue
  s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});n=s.get('name','')
  if 'Gradient' in v['m_FullTypeName'] or any(x in n for x in ['Layer','Background','gradient','colour','color']):print(i,v['m_FullTypeName'],n,'parent',v.get('m_Parent'),'children',v.get('m_Children'), 'alias',v.get('m_TemplateAlias'))
