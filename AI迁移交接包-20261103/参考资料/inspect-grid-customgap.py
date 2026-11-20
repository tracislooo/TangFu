exec(open('inspect-player-grid-style-spacing.py',encoding='utf-8-sig').read().split('for bn in')[0])
for bn in ['ui-styles_assets_common.bundle','ui-styles_assets_default.bundle']:
 for o in UnityPy.load(str(base/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' not in d:continue
  for r in d['m_Rules']:
   for p in r['m_Properties']:
    if 'grid' in p.get('m_CustomName','').lower():print(p['m_CustomName'],p['m_Values'])
  print('STRINGS',d.get('m_Name'),[s for s in d.get('strings',[]) if ('grid' in s.lower() or 'tile' in s.lower()) and any(x in s.lower() for x in ['gap','spacing','padding'])][:25])
