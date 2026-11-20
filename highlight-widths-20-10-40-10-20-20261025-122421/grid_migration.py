import copy
MAPPING={(0, 2): (0, 4), (2, 1): (4, 2), (3, 8): (6, 8), (11, 1): (14, 2), (12, 2): (16, 4)}
def migrate_layout(document,forward=True,version=None,limits_from=None):
 result=copy.deepcopy(document);mapping=MAPPING if forward else {v:k for k,v in MAPPING.items()}
 destination=set(mapping.values())
 for b in result['m_gridComponents']:
  q=b['m_location'];key=(q['x'],q['width']);assert key in mapping or key in destination,('Unexpected slot',b['m_elementID'],key)
  x,w=mapping.get(key,key);q['x']=x;q['width']=w;b['m_minSize']['x']=w;b['m_maxSize']['x']=w
  for cfg in b['m_gridElementConfigs']:cfg['Size']['x']=w
 result['m_layoutMode']=0 if forward else 4
 if limits_from is not None:
  old={(b['m_location']['x'],b['m_location']['width'],b['m_location']['y']):b for b in limits_from['m_gridComponents']}
  for b in result['m_gridComponents']:
   q=b['m_location'];key=(q['x'],q['width'],q['y'])
   if key in old:b['m_minSize']=copy.deepcopy(old[key]['m_minSize']);b['m_maxSize']=copy.deepcopy(old[key]['m_maxSize'])
  result['m_layoutMode']=limits_from['m_layoutMode']
 if version is not None:result['m_compositionVersion']=version
 cells=set();width=20 if forward else 14
 for b in result['m_gridComponents']:
  q=b['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<width and 0<=y<8 and (x,y) not in cells
    cells.add((x,y))
 assert len(cells)==width*8
 return result
