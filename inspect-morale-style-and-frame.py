exec(open('inspect-tactical-table-modes-current.py',encoding='utf-8-sig').read().split('for bundle in [')[0])
for sn in ['default','common']:
 e=UnityPy.load(str(p/f'ui-styles_assets_{sn}.bundle'))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  for rule in d.get('m_Rules',[]):
   for sel in rule['m_ComplexSelectors']:
    names=[a['m_Value'] for st in sel['m_Selectors'] for a in st['m_Parts']]
    if any(n in ['layout-tile-interaction_border_tactics','tactics-position__draggable','fm-star-rating-star','fm-star-rating-star-no-margin','scaling-icons-form-morale-1-size-small-16px','scaling-icons-form-morale-20-size-small-16px'] for n in names):
     pools={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
     print(sn,d['m_Name'],names,[(x['m_Id'],[d[pools[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pools else h for h in x['m_Values']]) for x in rule['m_Properties'] if x['m_Id'] in [131105,131092,131087,458752,458753,196610,458767,262146,262148]])
