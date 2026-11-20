from pathlib import Path
s=Path('build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0].replace('NAMES=[W,G,M,F]','NAMES=[W]').replace('match-ui-avatars-layout-','inspect-fitness-backdrop-').replace("if SKIN/n in before:assert before[SKIN/n]==before[GAME/n],('game/skin diverged',n)","pass").replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']","pass")
exec(s)
for name in ['TacticsPositionCombined','TacticsPositionDetailed','TacticsDetailedCardPositionButton']:
 d=Doc(W,name=name)
 for i,a in d.r.items():
  if 'm_Parent' not in a.get('data',{}):continue
  nm=d.data(i).get('name','')
  if ('NativePositionBackground' in nm or nm in ['PitchFitnessPlayerVisible','PitchFitnessPercent68'] or (name.endswith('Button')) or (name.endswith('Combined') and i in [1035,1105])):
   print(name,i,nm,a['data'].get('m_Parent'))
   ri=d.a(i).get('m_RuleIndex',-1)
   if ri>=0:print([(p['m_Id'],[d.s[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h for h in p['m_Values']]) for p in d.s['m_Rules'][ri]['m_Properties']])
