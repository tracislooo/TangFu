exec(open('inspect-position-layout.py',encoding='utf-8-sig').read().split('for pid in')[0])
for pid in [-940000000005000,-940000000008000,-940000000010020]:
 d=oo[pid].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};print('DOC',pid)
 for i in [1030,1069,1070,1071,1072]:
  if i in rr: print(i,rr[i]['data'])
 for r in rr.values():
  v=r.get('data',{})
  if any('RowTemplate' in k for k in v):print('LIST',v)
