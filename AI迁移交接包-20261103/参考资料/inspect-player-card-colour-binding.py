exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-player-card-colour-binding-'))
d=objs[G][-5643027006255053682].read_typetree();rr=refs(d);sheet=objs[G][d['inlineSheet']['m_PathID']].read_typetree()
for i in [1001,1012]:
 v=rr[i]['data'];s=rr[v['m_SerializedData']['rid']]['data'];print('NODE',i,json.dumps(s,ensure_ascii=False));print('CLASSES',v.get('m_Classes'));print('STYLE',sheet['m_Rules'][v['m_RuleIndex']] if v.get('m_RuleIndex',-1)>=0 else None)
