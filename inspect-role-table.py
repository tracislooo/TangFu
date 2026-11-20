exec(open('inspect-position-layout.py',encoding='utf-8-sig').read().split('for pid in')[0])
d=oo[-940000000008000].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
for i,r in rr.items():
 v=r.get('data',{})
 if 'StreamedTable' in v.get('m_FullTypeName',''):
  print(i,json.dumps(rr[v['m_SerializedData']['rid']]['data'],ensure_ascii=False))
