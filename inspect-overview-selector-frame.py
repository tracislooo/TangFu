exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-overview-selector-frame-'))
pid=-940000000002000;doc=objs[G][pid].read_typetree();rr=refs(doc);sheet=objs[G][doc['inlineSheet']['m_PathID']].read_typetree()
print(doc['m_Name'])
for i in [1001,1002,1004,1006,1008,1010,1011,1015,1016,1020]:
 v=rr[i]['data'];s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});pp=[]
 for p in sheet['m_Rules'][v['m_RuleIndex']]['m_Properties'] if v.get('m_RuleIndex',-1)>=0 else []:
  if p['m_Id'] in [131087,131096,131094,131101,131098,131093,131090,131099,131100,131105]:
   q=p['m_Values'][0];pool={2:'floats',3:'dimensions',7:'strings'}.get(q['m_ValueType']);pp.append((p['m_Id'],sheet[pool][q['valueIndex']] if pool else q))
 print(i,s.get('name'),v.get('m_Classes'),pp)
