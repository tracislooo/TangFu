from pathlib import Path
s=Path('build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0].replace('NAMES=[W,G,M,F]','NAMES=[G]').replace('match-ui-avatars-layout-','inspect-referee-')
s=s.replace("if SKIN/n in before:assert before[SKIN/n]==before[GAME/n],('game/skin diverged',n)","pass").replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']","pass")
exec(s)
d=Doc(G,name='MatchViewer_12x4')
for i,a in d.r.items():
 if 'm_Parent' not in a.get('data',{}):continue
 if 'Highlight' in d.data(i).get('name','') and any(k in d.data(i).get('name','') for k in ['Header','Text','Icon']):
  print(i,json.dumps(a,ensure_ascii=False),json.dumps(d.data(i),ensure_ascii=False))
  ri=d.a(i).get('m_RuleIndex',-1)
  if ri>=0:print('STYLE',[(p['m_Id'],[d.s[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h for h in p['m_Values']]) for p in d.s['m_Rules'][ri]['m_Properties']])

