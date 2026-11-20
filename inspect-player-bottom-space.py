exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-player-bottom-space-'))
d=objs[W][7857044477279960178].read_typetree();rr=refs(d);sheet=objs[W][d['inlineSheet']['m_PathID']].read_typetree()
for i,r in rr.items():
 v=r.get('data',{});ix=v.get('m_RuleIndex',-1)
 if 'm_FullTypeName' not in v:continue
 s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 print(i,v['m_FullTypeName'],s.get('name'),v.get('m_Parent'),v.get('m_Classes'))
 print('  Padding', {k:s[k] for k in s if any(t in k for t in ['Padding','Scroll','Margin'])})
 for p in sheet['m_Rules'][ix]['m_Properties'] if ix>=0 else []:
  if p['m_Id'] in [131090,131093,131098,131101,262150,262151]:
   print('  Style',p['m_Id'],[sheet[{2:'floats',3:'dimensions',7:'strings'}[q['m_ValueType']]][q['valueIndex']] if q['m_ValueType'] in [2,3,7] else q for q in p['m_Values']])
