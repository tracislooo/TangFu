exec(open('inspect-position-layout.py',encoding='utf-8-sig').read().split('for pid in')[0])
for o in oo.values():
 if o.type.name=='AssetBundle':
  for k,c in o.read_typetree()['m_Container']:
   if k in ['275b95704dc858346bf8acb33d0dd6ac','03295969b1254e08a596d5041b535b6b']:
    d=oo[c['asset']['m_PathID']].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};print('CELL',k,d['m_Name'])
    for i,r in rr.items():
     v=r.get('data',{})
     if 'm_FullTypeName' in v: print(i,v['m_FullTypeName'],v.get('m_Classes'),rr.get(v['m_SerializedData']['rid'],{}).get('data',{}).get('name'))
