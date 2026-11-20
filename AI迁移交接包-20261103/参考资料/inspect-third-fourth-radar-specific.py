exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-third-fourth-radar-height-'))
for pid in [-940000000010000,-940000000012000]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);sheet=objs[W][doc['inlineSheet']['m_PathID']].read_typetree();print('PAGE',pid)
 for i,r in rr.items():
  v=r.get('data',{})
  if 'm_FullTypeName' not in v:continue
  s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=s.get('name','')
  if i in [6298,6228,1026,1043] or i in [rr[j]['data']['m_Parent']['rid'] for j in [6298]]:
   props=sheet['m_Rules'][v['m_RuleIndex']]['m_Properties'] if v['m_RuleIndex']>=0 else []
   fmt=[]
   for p0 in props:
    if p0['m_Id'] in [131087,131094,131096,131084,131085,131105]:
     vals=[]
     for q in p0['m_Values']:
      pool={2:'floats',3:'dimensions',7:'strings'}.get(q['m_ValueType']);vals.append(sheet[pool][q['valueIndex']] if pool else q)
     fmt.append((p0['m_Id'],vals))
   print(i,name,'parent',v['m_Parent'],'children',v.get('m_Children'),fmt)

