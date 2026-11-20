import copy
NATIVE='9a03c4e43edfd284fb46d9f17bc197da';AWAY='bab6a500d7a65266a5162c218a2ddf6e'
def migrate_layout(document,forward=True,version=None,limits_from=None):
 result=copy.deepcopy(document)
 for block in result['m_gridComponents']:
  q=block['m_location']
  if q['x'] not in [0,15]:continue
  assert q['width']==5
  top=q['y']==0
  if forward:
   assert (q['y'],q['height']) in [(0,6),(6,2),(0,4),(4,4)]
   q['y']=0 if top else 4;q['height']=4
  else:
   assert (q['y'],q['height']) in [(0,4),(4,4)]
   q['y']=0 if top else 6;q['height']=6 if top else 2
  for key in ['m_minSize','m_maxSize']:block[key]['y']=q['height']
  for cfg in block['m_gridElementConfigs']:
   cfg['Size']['y']=q['height']
   if block['m_elementID']=='AwayTeamFormationAdaptive':
    old,new=(NATIVE,AWAY) if forward else (AWAY,NATIVE)
    if cfg['AssetRef']['m_AssetGUID']==old:cfg['AssetRef']['m_AssetGUID']=new
 if limits_from is not None:
  for block in result['m_gridComponents']:
   q=block['m_location']
   prior=[b for b in limits_from['m_gridComponents'] if b['m_location']==q and b['m_elementID']==block['m_elementID']]
   if len(prior)==1:
    for key in ['m_minSize','m_maxSize']:block[key]=copy.deepcopy(prior[0][key])
 if version is not None:result['m_compositionVersion']=version
 cells=set()
 for block in result['m_gridComponents']:
  q=block['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<20 and 0<=y<8 and (x,y) not in cells
    cells.add((x,y))
 assert len(cells)==160
 return result
