from pathlib import Path
import sys,json
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
loc=json.loads((R/'current-game-location.json').read_text('utf-8-sig'));bn='ui-tileslayouts_assets_all.bundle'
for folder in [Path(loc['bundle_root']),Path(loc['skin_packages'])]:
 oo={o.path_id:o for o in UnityPy.load(str(folder/bn)).objects};print('TARGET',str(folder))
 for pid in [3901662990989568885,1332213496068314481]:
  d=oo[pid].read_typetree()
  if 'm_gridElementDescriptions' in d:
   rows=[]
   for p in d['m_gridElementDescriptions']:
    i=p['m_PathID'];name=oo[i].peek_name() if p['m_FileID']==0 and i in oo else ''
    if any(k in name.lower() for k in ['overviewtoggle','overviewthird','overviewfourth']):rows.append((i,name))
   print('TILESET',rows)
  for e in d.get('m_gridElements',[]):
   if any(k in e.get('m_elementID','') for k in ['Attributes','OverviewLeft']):print('ELEMENT',e['m_elementID'],e.get('m_configDescriptions'))
