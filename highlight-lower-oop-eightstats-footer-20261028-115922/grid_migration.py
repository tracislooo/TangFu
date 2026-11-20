import copy
VERSIONS={'MatchExperienceHumanGridComposition-Large': {'before': 7, 'after': 8}, 'MatchExperienceHumanGridComposition-Large-NoLeague': {'before': 7, 'after': 8}, 'MatchExperienceGridComposition-Large': {'before': 7, 'after': 8}, 'MatchExperienceGridComposition-Large-NoLeague': {'before': 7, 'after': 8}}
IDS={'PlayerStatsHomeTeam': 'HighlightHomeEightStatsAndOOP', 'PlayerStatsAwayTeam': 'HighlightAwayEightStatsAndOOP'}
def migrate_layout(document,forward=True,version=None,limits_from=None):
 if not forward:
  assert limits_from is not None
  return copy.deepcopy(limits_from)
 result=copy.deepcopy(document)
 for a in result['m_gridComponents']:
  if a['m_elementID'] in IDS:
   a['m_elementID']=IDS[a['m_elementID']];a['m_configDescriptionKeys']=[a['m_elementID']];a['m_configDescriptions']=[];a['m_gridElementConfigs']=[]
 for a in result.get('m_placementBindings',[]):
  if a['m_elementID'] in IDS:a['m_elementID']=IDS[a['m_elementID']]
 result['m_compositionVersion']=version
 return result
