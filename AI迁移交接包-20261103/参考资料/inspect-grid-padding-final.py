exec(open('inspect-player-grid-style-spacing.py',encoding='utf-8-sig').read().split('for bn in')[0])
for bn in ['ui-styles_assets_common.bundle','ui-styles_assets_default.bundle']:
 for o in UnityPy.load(str(base/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_Rules' not in d:continue
  for r in d['m_Rules']:
   matches=[s for s in r.get('m_ComplexSelectors',[]) if any('grid' in part['m_Value'].lower() and any(k in part['m_Value'].lower() for k in ['layout','element','content']) for se in s['m_Selectors'] for part in se['m_Parts'])]
   pp=[p for p in r['m_Properties'] if p['m_Id'] in [131090,131093,131098,131101,262151,262150]]
   if matches and pp:print(d.get('m_Name'),str(matches)[:430],[(p['m_Id'],p['m_Values']) for p in pp])
