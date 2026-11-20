exec(open('inspect-old-fc-request.py',encoding='utf-8-sig').read().split('for pid in')[0])
for pid,ids in [(-940000000010000,[1002,1102,6310,6330,6312,6322,1703,1011,6334,1173,1188,1205,1221]),(-941100000001020,[1011,5852,6298,8260,1349,1186,8274,8276,8277,8279,8283])]:
 d=o[pid].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};s=o[d['inlineSheet']['m_PathID']].read_typetree();print('PAGE',pid)
 for i in ids:
  a=rr[i]['data'];idx=a.get('m_RuleIndex',-1);ps=s['m_Rules'][idx]['m_Properties']if idx>=0 else [];print(i,[(p['m_Id'],[(h['m_ValueType'],s[{2:'floats',3:'dimensions',4:'colors',5:'strings',7:'strings'}.get(h['m_ValueType'],'strings')][h['valueIndex']]if h['m_ValueType']in [2,3,4,5,7]else h['valueIndex'])for h in p['m_Values']])for p in ps])
