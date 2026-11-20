exec(open('inspect-tactical-table-modes-current.py',encoding='utf-8-sig').read().split('for bundle in [')[0])
for fp in p.glob('ui-styles*.bundle'):
 e=UnityPy.load(str(fp))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  for rule in d.get('m_Rules',[]):
   for sel in rule['m_ComplexSelectors']:
    names=[a['m_Value'] for st in sel['m_Selectors'] for a in st['m_Parts']]
    if any(n in ['scaling-icons-form-morale-1-size-small-16px','scaling-icons-form-morale-10-size-small-16px','scaling-icons-form-morale-20-size-small-16px'] or 'drag' in n.lower() and ('tactic' in n.lower() or 'dragging' in n.lower()) for n in names):
     print(fp.name,d['m_Name'],names,[(x['m_Id'],x['m_Values']) for x in rule['m_Properties']])
