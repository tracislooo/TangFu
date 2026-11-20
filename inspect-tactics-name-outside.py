from pathlib import Path
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0]
exec(s)
for name in ['TacticsPositionCombined','TacticsPositionDetailed']:
 d=Doc(W,name=name)
 for i,a in d.r.items():
  if 'm_Parent' not in a.get('data',{}):continue
  nm=d.data(i).get('name','')
  if 'Name' in nm or 'NativePositionBackground' in nm or 'FitnessTrack' in nm or i in [1035,1002,1003]:
   ri=d.a(i).get('m_RuleIndex',-1)
   print(name,i,nm,'parent',d.a(i)['m_Parent'], 'alias',d.a(i).get('m_TemplateAlias'))
   if ri>=0:print([(p['m_Id'],[d.s[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h for h in p['m_Values']]) for p in d.s['m_Rules'][ri]['m_Properties']])
