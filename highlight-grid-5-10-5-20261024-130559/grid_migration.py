"""Change only the three horizontal slot widths of an existing match composition."""
import copy

OLD={(0,6):(0,5),(6,8):(5,10),(14,6):(15,5)}

def migrate_layout(document,forward=True,version=None,limits_from=None):
 result=copy.deepcopy(document)
 mapping=OLD if forward else {value:key for key,value in OLD.items()}
 destinations=set(mapping.values())
 for block in result['m_gridComponents']:
  loc=block['m_location'];key=(loc['x'],loc['width'])
  assert key in mapping or key in destinations,('Unexpected horizontal slot; refusing to reset it',block['m_elementID'],key)
  target=mapping.get(key,key)
  loc['x'],loc['width']=target
  block['m_minSize']['x']=target[1];block['m_maxSize']['x']=target[1]
  for config in block['m_gridElementConfigs']:config['Size']['x']=target[1]
 if limits_from is not None:
  original_limits={(b['m_location']['x'],b['m_location']['width'],b['m_location']['y']):(b['m_minSize']['x'],b['m_maxSize']['x']) for b in limits_from['m_gridComponents']}
  for block in result['m_gridComponents']:
   loc=block['m_location'];key=(loc['x'],loc['width'],loc['y'])
   if key in original_limits:block['m_minSize']['x'],block['m_maxSize']['x']=original_limits[key]
 if version is not None:result['m_compositionVersion']=version
 cells={}
 for block in result['m_gridComponents']:
  loc=block['m_location']
  for x in range(loc['x'],loc['x']+loc['width']):
   for y in range(loc['y'],loc['y']+loc['height']):
    assert 0<=x<20 and 0<=y<8
    assert (x,y) not in cells,('Grid overlap',block['m_elementID'],cells.get((x,y)))
    cells[x,y]=block['m_elementID']
 assert len(cells)==160,('Unexpected gaps',len(cells))
 for old,new in zip(document['m_gridComponents'],result['m_gridComponents']):
  normalized=copy.deepcopy(new)
  normalized['m_location']=copy.deepcopy(old['m_location'])
  normalized['m_minSize']=copy.deepcopy(old['m_minSize'])
  normalized['m_maxSize']=copy.deepcopy(old['m_maxSize'])
  for previous,current in zip(old['m_gridElementConfigs'],normalized['m_gridElementConfigs']):current['Size']=copy.deepcopy(previous['Size'])
  assert normalized==old,'Selected module or other configuration changed'
 return result
