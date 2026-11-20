exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-overview-external-gaps-'))
for pid in [-930000000001001,-940000000010000,7857044477279960178]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);sheet=objs[W][doc['inlineSheet']['m_PathID']].read_typetree();print('PAGE',pid)
 def dump(i,dep=0):
  v=rr[i]['data'];s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});ix=v.get('m_RuleIndex',-1);props=[]
  for p in sheet['m_Rules'][ix]['m_Properties'] if ix>=0 else []:
   if p['m_Id'] in [131093,131090,262150,262151,131100,131103,131087,131096,262152,262153]:
    vals=[]
    for q in p['m_Values']:
     pool={2:'floats',3:'dimensions',7:'strings'}.get(q['m_ValueType']);vals.append(sheet[pool][q['valueIndex']] if pool else q)
    props.append((p['m_Id'],vals))
  print(' '*dep,i,s.get('name',''),v.get('m_FullTypeName'),v.get('m_Classes'),props)
  if dep<3:
   for c in v.get('m_Children',[]):
    if 'm_FullTypeName' in rr[c['rid']].get('data',{}):dump(c['rid'],dep+1)
 dump(1000)
