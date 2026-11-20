exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-native-dot-size-'))
d=objs[W][4269476442492208794].read_typetree();rr=refs(d);s=objs[W][d['inlineSheet']['m_PathID']].read_typetree()
for i in [1001,1002,1004,1006,1008,1010]:
 a=rr[i]['data'];print(i,[(p['m_Id'],[(s[{2:'floats',3:'dimensions',7:'strings'}[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in [2,3,7] else v) for v in p['m_Values']]) for p in s['m_Rules'][a['m_RuleIndex']]['m_Properties']] if a['m_RuleIndex']>=0 else [])
