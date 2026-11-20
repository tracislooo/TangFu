import copy
OLD='6a4b032b28fee7b47941ca946d06eafb';NEW='0d00ff6203195093b948b74cbaffede8'
def migrate_layout(document,forward=True,version=None,**kwargs):
 result=copy.deepcopy(document);old,new=(OLD,NEW) if forward else (NEW,OLD)
 for block in result['m_gridComponents']:
  if block['m_elementID'] not in ['PlayerStatsHomeTeam','PlayerStatsAwayTeam']:continue
  for cfg in block['m_gridElementConfigs']:
   if cfg['AssetRef']['m_AssetGUID']==old:cfg['AssetRef']['m_AssetGUID']=new
 if version is not None:result['m_compositionVersion']=version
 return result
