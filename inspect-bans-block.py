exec(open('inspect-request-overviews.py',encoding='utf-8-sig').read().split('for x in o.values():')[0])
for x in o.values():
 if x.type.name=='MonoBehaviour' and x.peek_name()=='PlayerReportBansBlock':
  d=x.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};print(x.path_id)
  for i,r in rr.items():
   a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print(i,sd.get('name'),a.get('m_FullTypeName'),a.get('m_Children'), {k:v for k,v in sd.items() if any(t in k for t in ['Scroll','Size','Height'])})
