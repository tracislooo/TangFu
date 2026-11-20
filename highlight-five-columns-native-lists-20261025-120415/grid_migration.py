import copy
OLD={(0,5):(0,2),(5,10):(3,8),(15,5):(12,2)}
ADDITIONS=[{'m_elementID': 'HighlightHomePlayerStatsColumn', 'm_configDescriptions': [{'m_FileID': 0, 'm_PathID': -981025000000300}], 'm_configDescriptionKeys': [], 'm_gridElementConfigs': [{'Description': {'m_FileID': 0, 'm_PathID': -981025000000300}, 'Size': {'x': 1, 'y': 8}, 'Asset': {'m_FileID': 0, 'm_PathID': 0}, 'AssetRef': {'m_AssetGUID': '5f58a08cb74054169e23929a94e26df7', 'm_SubObjectName': '', 'm_SubObjectType': ''}, 'Type': 0}], 'm_location': {'x': 2, 'y': 0, 'width': 1, 'height': 8}, 'm_minSize': {'x': 1, 'y': 8}, 'm_maxSize': {'x': 1, 'y': 8}, 'm_isLocked': 1, 'm_isDebug': 0, 'm_isDynamic': 0, 'm_features': 0, 'm_expandToContent': 0, 'm_takesFocus': 0, 'm_isOptional': 0, 'm_horizontalAlignment': 0, 'm_verticalAlignment': 0}, {'m_elementID': 'HighlightAwayPlayerStatsColumn', 'm_configDescriptions': [{'m_FileID': 0, 'm_PathID': -981025000000301}], 'm_configDescriptionKeys': [], 'm_gridElementConfigs': [{'Description': {'m_FileID': 0, 'm_PathID': -981025000000301}, 'Size': {'x': 1, 'y': 8}, 'Asset': {'m_FileID': 0, 'm_PathID': 0}, 'AssetRef': {'m_AssetGUID': '2cf183622d175b669d859a85c389bdf0', 'm_SubObjectName': '', 'm_SubObjectType': ''}, 'Type': 0}], 'm_location': {'x': 11, 'y': 0, 'width': 1, 'height': 8}, 'm_minSize': {'x': 1, 'y': 8}, 'm_maxSize': {'x': 1, 'y': 8}, 'm_isLocked': 1, 'm_isDebug': 0, 'm_isDynamic': 0, 'm_features': 0, 'm_expandToContent': 0, 'm_takesFocus': 0, 'm_isOptional': 0, 'm_horizontalAlignment': 0, 'm_verticalAlignment': 0}]
PRIVATE_IDS={b['m_elementID'] for b in ADDITIONS}
def migrate_layout(document,forward=True,version=None,limits_from=None,cache=False):
 result=copy.deepcopy(document);mapping=OLD if forward else {v:k for k,v in OLD.items()};destinations=set(mapping.values())
 original_blocks=[b for b in result['m_gridComponents'] if b['m_elementID'] not in PRIVATE_IDS]
 result['m_gridComponents']=original_blocks
 for block in original_blocks:
  loc=block['m_location'];key=(loc['x'],loc['width']);assert key in mapping or key in destinations,('Unexpected saved slot',block['m_elementID'],key)
  x,w=mapping.get(key,key);loc['x']=x;loc['width']=w;block['m_minSize']['x']=w;block['m_maxSize']['x']=w
  for cfg in block['m_gridElementConfigs']:cfg['Size']['x']=w
 if forward:
  for addition in ADDITIONS:
   b=copy.deepcopy(addition)
   if cache:
    b['m_configDescriptions']=[];b['m_configDescriptionKeys']=[b['m_elementID']];b['m_gridElementConfigs']=[]
   result['m_gridComponents'].append(b)
 if limits_from is not None:
  old={(b['m_location']['x'],b['m_location']['width'],b['m_location']['y']):b for b in limits_from['m_gridComponents']}
  for b in result['m_gridComponents']:
   key=(b['m_location']['x'],b['m_location']['width'],b['m_location']['y'])
   if key in old:b['m_minSize']=copy.deepcopy(old[key]['m_minSize']);b['m_maxSize']=copy.deepcopy(old[key]['m_maxSize'])
 if version is not None:result['m_compositionVersion']=version
 cells=set();width=14 if forward else 20
 for b in result['m_gridComponents']:
  q=b['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<width and 0<=y<8 and (x,y) not in cells,('Invalid grid',b['m_elementID'],x,y)
    cells.add((x,y))
 assert len(cells)==width*8
 return result
