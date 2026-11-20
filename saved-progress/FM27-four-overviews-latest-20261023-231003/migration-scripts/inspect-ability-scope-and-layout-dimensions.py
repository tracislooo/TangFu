exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for i in [1291,1297,1171,1295,1182,1180,1193,1349]:
 a=rr[i]['data'];print('FULL',i,a.get('m_Classes'))
 if a.get('m_RuleIndex',-1)>=0:print({p['m_Id']:[('kw',h['valueIndex']) if h['m_ValueType']==1 else sheet[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']] for p in sheet['m_Rules'][a['m_RuleIndex']]['m_Properties']})
for pid,ids in [(-547355884850947872,[1001,1002,1004,1006,1008,1009,1013,1018,1019]),(-7609784215942621793,[1001,1007,1012,1013])]:
 d=objects[pid].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']};ss=objects[d['inlineSheet']['m_PathID']].read_typetree();print('SOURCE',d['m_Name'],d['m_Usings'])
 for i in ids:
  a=sr[i]['data'];sd=sr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print('NODE',i,a.get('m_Classes'))
  if i in [1001,1002,1004,1006]:print({k:v for k,v in sd.items() if k in ['Parameters','Mappings','Binding','ClassSetters']})
  if a.get('m_RuleIndex',-1)>=0:print({p['m_Id']:[('kw',h['valueIndex']) if h['m_ValueType']==1 else ss[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']] for p in ss['m_Rules'][a['m_RuleIndex']]['m_Properties']})
