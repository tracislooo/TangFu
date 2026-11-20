import copy
OLD='9a03c4e43edfd284fb46d9f17bc197da';NEW='8354dc9fb4635507a461287242ebd435'
def migrate_layout(document,forward=True,**kwargs):
 result=copy.deepcopy(document);source,target=(OLD,NEW) if forward else (NEW,OLD)
 for block in result['m_gridComponents']:
  if block['m_elementID']!='HomeTeamFormationAdaptive':continue
  for cfg in block['m_gridElementConfigs']:
   if cfg['AssetRef']['m_AssetGUID']==source:cfg['AssetRef']['m_AssetGUID']=target
 return result
