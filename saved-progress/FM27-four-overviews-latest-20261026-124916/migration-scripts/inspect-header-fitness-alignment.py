exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
doc=objects[5775949770471550939].read_typetree();rr={r['rid']:r for r in doc['references']['RefIds']};sheet=objects[doc['inlineSheet']['m_PathID']].read_typetree()
m={int(k):v for k,v in json.loads((R/'header-six-native-fitness-metrics-20261018-013417/manifest.json').read_text())['new_node_mapping'].items()}
for i in [1029,1056,1109,1110,1116,1192,1134]:
 a=rr[m[i]]['data'];print(i,'class',a['m_Classes'])
 for p in sheet['m_Rules'][a['m_RuleIndex']]['m_Properties']:
  print(p['m_Id'],[('kw',h['valueIndex']) if h['m_ValueType']==1 else sheet[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']])
