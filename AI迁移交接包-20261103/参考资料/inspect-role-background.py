from pathlib import Path
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','inspect-role-background-');exec(s)
for name in ['TacticsPositionCombined','TacticsDetailedCardDetailsDesktop','TacticsDetailedCardDetailsTouch']:
 d=Doc(W,name=name)
 for i,a in d.r.items():
  if 'm_Parent' not in a.get('data',{}):continue
  if (name=='TacticsPositionCombined' and i in [1055,1057,1075,1078,1092,1094,1105,1107]) or d.data(i).get('name','')=='DetailedCurrentPhasePositionContext':
   print(name,i,d.a(i).get('m_Classes'),d.data(i))
