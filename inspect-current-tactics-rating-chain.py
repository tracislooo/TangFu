from pathlib import Path
s=Path('fix-tactics-card-frame-and-star-visibility.py').read_text('utf8').split('for folder, tag in ')[0]
exec(s)
for name in ['TacticsPositionCombined','TacticsDetailedCardDetailsDesktop']:
 doc=Doc(W,name=name); print(name)
 node=doc.named('DirectTacticsRatingEquals7')
 while node!=-2 and node in doc.r:
  a=doc.a(node); ri=a.get('m_RuleIndex',-1)
  print(node,doc.data(node).get('name'), [(p['m_Id'],[doc.s[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h for h in p['m_Values']]) for p in doc.s['m_Rules'][ri]['m_Properties']] if ri>=0 else [])
  node=a.get('m_Parent',{}).get('rid',-2)
