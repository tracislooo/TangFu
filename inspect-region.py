exec(open('inspect-request-overviews.py',encoding='utf-8-sig').read().split('for x in o.values():')[0])
d=o[-950000000000162].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
for i,r in rr.items():
 a=r.get('data',{});si=a.get('m_SerializedData',{}).get('rid');sd=rr.get(si,{}).get('data',{});nm=sd.get('name','')
 if i in [1066,1067,1069,1070,1096,1097,6236,6238,6239,6248,6249,6251,6252,6278,6280,6292,6296] or 'Identity' in nm:
  chain=[];cur=i
  for z in range(7):
   a1=rr.get(cur,{}).get('data',{});s1=rr.get(a1.get('m_SerializedData',{}).get('rid'),{}).get('data',{});chain.append((cur,s1.get('name'),a1.get('m_TemplateAlias'),a1.get('m_Classes')));cur=a1.get('m_Parent',{}).get('rid')
  print(chain)
print('stat objects',[(x.path_id,x.peek_name()) for x in o.values() if x.type.name=='MonoBehaviour' and 'Twelve' in (x.peek_name() or '')])
