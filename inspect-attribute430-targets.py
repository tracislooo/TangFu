exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-attribute430-targets-'))
for pid in [-930000000001001,-930000000001003,-940000000010000,-940000000012000]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);print(pid)
 for i,r in rr.items():
  v=r.get('data',{});s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=s.get('name','')
  if i in [1002,1009,1025] or 'AttributesNoScroll' in name:print(i,name,v.get('m_FullTypeName'))
