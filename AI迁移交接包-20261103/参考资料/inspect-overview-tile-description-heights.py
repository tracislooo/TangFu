exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
e=UnityPy.load(str(GAME/'ui-tileslayouts_assets_all.bundle'));oo={o.path_id:o for o in e.objects};co=oo[3901662990989568885].read_typetree()
for c in co['m_gridComponents']:
 for cfg in c['m_gridElementConfigs']:
  p=cfg['Description'];print(c['m_elementID'],p)
  if p['m_FileID']==0:
   d=oo[p['m_PathID']].read_typetree();print(d.get('m_Name'),d.get('<Configurations>k__BackingField'))
