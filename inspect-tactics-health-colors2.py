from pathlib import Path
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','inspect-tactics-health-colors-');exec(s)
for ob in objs[W].values():
 if ob.type.name!='MonoBehaviour':continue
 raw=ob.get_raw_data()
 if not any(x in raw for x in [b'FatigueRawColour',b'CombinedConditionPercent',b'PitchFitnessPercent']):continue
 d=Doc(W,pid=ob.path_id);matches=[]
 for i,a in d.r.items():
  if 'm_Parent' not in a.get('data',{}):continue
  nm=d.data(i).get('name','')
  if nm.startswith(('FatigueRawColour','CombinedConditionPercent','CombinedConditionRing','CombinedSharpnessPercent','CombinedSharpnessRing','PitchFitnessPercent')):
   if nm.endswith(('0','100','None')):matches.append((i,nm))
 print(d.d['m_Name'],d.obj.path_id,matches[:12])
 if d.d['m_Name']=='TacticsConditionPercentageCell':
  for i,nm in matches:
   if nm in ['CombinedConditionRing100','CombinedConditionPercent100']:print(nm, d.s['m_Rules'][d.a(i)['m_RuleIndex']]['m_Properties'])

