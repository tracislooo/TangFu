from pathlib import Path
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','inspect-star-outline-');exec(s)
for name in ['TacticsPositionCombined','TacticsDetailedCardDetailsDesktop','TacticsDetailedCardDetailsTouch']:
 d=Doc(W,name=name)
 for i,a in d.r.items():
  if 'm_Parent' not in a.get('data',{}):continue
  typ=a.get('data',{}).get('m_FullTypeName','')
  if 'Star' in typ or d.data(i).get('name','').endswith('FitnessTrack') or 'FitnessFill68' in d.data(i).get('name',''):
   print(name,i,typ,d.data(i))
   print('RULE',d.s['m_Rules'][d.a(i)['m_RuleIndex']] if d.a(i).get('m_RuleIndex',-1)>=0 else None)
 print('USINGS', [u for u in d.d['m_Usings'] if 'star' in u['alias'].lower()])

