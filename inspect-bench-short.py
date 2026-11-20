import json
from pathlib import Path
pm={2:'floats',3:'dimensions',4:'colors',7:'strings'}
for name in ['MatchManySubstitutesSmallCard','SquadOverviewPlayerBlockSmall','MatchManySubstitutesRegularCard','SquadOverview']:
 d=json.loads((Path('inspect-bench-current')/(name+'.json')).read_text('utf8'));t=d['tree'];st=d['style'];r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']}
 print(name)
 for i,a in r.items():
  if 'm_Parent' not in a:continue
  s=r.get(a.get('m_SerializedData',{}).get('rid'),{});typ=a.get('m_FullTypeName','')
  if name=='SquadOverview':
   if i not in [1009,1011,1012,1016,1021,1028,1029,1038,1041,1117,1119,1121,1123,1125,1127]:continue
  elif not (i in [1001,1002,1006,1008,1012,1015,1016,1019,1021,1022,1028,1043,1061,1062,1076,1083,1084] or typ.endswith('SIText') and 'MatchCondition' not in s.get('name','')):continue
  ps=st['m_Rules'][a['m_RuleIndex']]['m_Properties'] if a.get('m_RuleIndex',-1)>=0 else []
  decoded={p['m_Id']:[st[pm[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in pm else v for v in p['m_Values']] for p in ps}
  print(i,a['m_Parent']['rid'],typ,s.get('name'),str({k:v for k,v in s.items() if k in ['TextDataLink','TextBinding','FixedElementSize','Text','StringDataLink']}),a.get('m_TemplateAlias'),a.get('m_Classes'),decoded)
