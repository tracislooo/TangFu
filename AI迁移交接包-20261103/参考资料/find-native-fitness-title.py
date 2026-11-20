exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
names=['PlayerFitnessTile_2x1','PlayerFitnessTile_2x2','PlayerFitnessTile_4x2','PlayerReportFitnessCard','PlayerConditionTooltipBlock']
for o in objects.values():
 if o.type.name=='MonoBehaviour' and o.peek_name() in names:
  d=o.read_typetree();sr={r['rid']:r for r in d.get('references',{}).get('RefIds',[])};print('\nASSET',o.path_id,d['m_Name'])
  for i,r in sr.items():
   a=r.get('data',{})
   if 'DebugDisplay' in a:print(i,a['DebugDisplay'])
  print('usings',d.get('m_Usings',[])[:3])
