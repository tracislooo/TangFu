exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
e=UnityPy.load(str(GAME/'ui-tileslayouts_assets_all.bundle'))
for o in e.objects:
 if o.type.name=='MonoBehaviour' and 'PlayerReportOverviewComposition' in o.peek_name():
  d=o.read_typetree();print('ASSET',o.path_id,d['m_Name'],{k:v for k,v in d.items() if k not in ['m_gridComponents','m_GameObject','m_Script']})
  for c in d.get('m_gridComponents',[]):print(c['m_elementID'],'location',c['m_location'],'min',c['m_minSize'],'max',c['m_maxSize'],'configs',[(x.get('Size'),x.get('AssetRef')) for x in c['m_gridElementConfigs']])
