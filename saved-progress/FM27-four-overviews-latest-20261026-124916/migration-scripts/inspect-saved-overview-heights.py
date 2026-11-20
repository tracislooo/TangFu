from pathlib import Path
import json
p=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
print('EXISTS',p.exists())
if p.exists():
 d=json.loads(p.read_text(encoding='utf-8-sig'));print('KEYS',list(d))
 for c in d['m_gridComponents']:print(c['m_elementID'],c['m_location'],c['m_minSize'],c['m_maxSize'],[(x.get('Size'),x.get('AssetRef',{}).get('m_AssetGUID')) for x in c['m_gridElementConfigs']])
