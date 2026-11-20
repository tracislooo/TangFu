exec(open('inspect-player-grid-style-spacing.py',encoding='utf-8-sig').read().split('for bn in')[0])
for bn in ['ui-styles_assets_common.bundle','ui-styles_assets_default.bundle']:
 for o in UnityPy.load(str(base/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' not in d:continue
  for r in d['m_Rules']:
   for p in r['m_Properties']:
    ss=[d['strings'][v['valueIndex']] for v in p['m_Values'] if v['m_ValueType'] in [7,8]]
    if '--spacing-tiles' in ss or p.get('m_CustomName')=='--spacing-tiles':print(d.get('m_Name'),str(r.get('m_ComplexSelectors'))[:750],p)
