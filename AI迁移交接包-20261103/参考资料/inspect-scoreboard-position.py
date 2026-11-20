from pathlib import Path
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('NAMES=[W]','NAMES=[M]').replace('inspect-fitness-backdrop-','inspect-scoreboard-position-');exec(s)
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[M]=UnityPy.load(before[folder/M]);objs[M]={o.path_id:o for o in env[M].objects}
 d=Doc(M,name='OverviewHeader');i=1034
 print(tag)
 while i in d.r and i!=1000:
  print(i,d.a(i).get('m_Classes'),d.a(i).get('m_Parent'))
  ri=d.a(i).get('m_RuleIndex',-1)
  if ri>=0:
   print([(p['m_Id'],[d.s[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h for h in p['m_Values']]) for p in d.s['m_Rules'][ri]['m_Properties']])
  i=d.a(i)['m_Parent']['rid']
