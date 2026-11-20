exec(open('inspect-player-grid-style-spacing.py',encoding='utf-8-sig').read().split('for bn in')[0])
for bn in ['ui-styles_assets_common.bundle','ui-styles_assets_default.bundle']:
 for o in UnityPy.load(str(base/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' not in d:continue
  for r in d['m_Rules']:
   sels=str(r.get('m_ComplexSelectors',[]))
   if 'grid' not in sels.lower() and not any('grid' in p.get('m_CustomName','').lower() for p in r['m_Properties']):continue
   if not any(x in sels.lower() for x in ['scalable','grid-layout','tile','grid-element']) and not any('grid' in p.get('m_CustomName','').lower() for p in r['m_Properties']):continue
   print(d.get('m_Name'),sels)
   for p in r['m_Properties']:
    vals=[]
    for v in p['m_Values']:
     pool={2:'floats',3:'dimensions',7:'strings',8:'strings'}.get(v['m_ValueType']);vals.append(d[pool][v['valueIndex']] if pool else v)
    print(p['m_Id'],p['m_CustomName'],vals)
