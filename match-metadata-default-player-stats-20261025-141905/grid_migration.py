import copy
TARGETS={0:'PlayerStatsHomeTeam',15:'PlayerStatsAwayTeam'}
FIELDS=['m_elementID','m_configDescriptions','m_configDescriptionKeys','m_gridElementConfigs']
def migrate_layout(document,forward=True,version=None,limits_from=None):
 result=copy.deepcopy(document)
 for block in result['m_gridComponents']:
  q=block['m_location']
  if q['y']!=4 or q['x'] not in TARGETS:continue
  assert q['width']==5 and q['height']==4
  if forward:
   block['m_elementID']=TARGETS[q['x']]
   block['m_configDescriptions']=[];block['m_configDescriptionKeys']=[TARGETS[q['x']]];block['m_gridElementConfigs']=[]
  else:
   assert limits_from is not None,'Original saved choices are required for restore'
   old=next(b for b in limits_from['m_gridComponents'] if b['m_location']==q)
   for field in FIELDS:block[field]=copy.deepcopy(old[field])
 if version is not None:result['m_compositionVersion']=version
 return result
