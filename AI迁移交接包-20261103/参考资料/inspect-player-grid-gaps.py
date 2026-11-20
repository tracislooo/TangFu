exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-player-grid-gaps-'))
doc=objs[W][7857044477279960178].read_typetree();print(doc['m_Usings'])
rr=refs(doc)
for i,r in rr.items():
 v=r.get('data',{});typ=v.get('m_FullTypeName','')
 if typ or 'Grid' in str(r.get('type',{})):
  s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(i,typ,s.get('name'),v.get('m_TemplateAlias'),{k:x for k,x in s.items() if any(y in k.lower() for y in ['gap','grid','layout','composition'])})
