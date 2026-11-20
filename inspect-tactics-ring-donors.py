exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
B='ui-backgrounds_assets_common.bundle';bg=UnityPy.load(str(p.parent/B));bo={o.path_id:o for o in bg.objects}
t={o.peek_name():o.path_id for o in bo.values() if o.type.name=='Texture2D' and o.peek_name().startswith('FM27StatusRingCW')};print('RINGS',len(t),[(n,t.get(n)) for n in ['FM27StatusRingCW000','FM27StatusRingCW050','FM27StatusRingCW100']]);print('BUNDLE',bg.assets[0].name)
cell=obs[-970000000001000];d=cell.read_typetree();r={x['rid']:x for x in d['references']['RefIds']};print('STYLE',d['inlineSheet']);print('EXTERNALS',[(i+1,e.name) for i,e in enumerate(cell.assets_file.externals) if e.name.lower()==bg.assets[0].name.lower()]);print('CELLLEAVES',[(i,a['data'].get('name'),a['data'].get('text')) for i,a in r.items() if a.get('data',{}).get('name','').startswith('TacticsConditionPercent')][:4])
for o in UnityPy.load(str(p.parent/'ui-tableviews_assets_all.bundle')).objects:
 if o.type.name=='MonoBehaviour' and o.peek_name().startswith('TacticTeamSelection') and 'InMatch' not in o.peek_name():
  for c in o.read_typetree().get('m_tableView',{}).get('m_tableConfig',[]):
   if c['m_columnID']=='condition':print(o.peek_name(),c['m_columnMetadata']['m_widthOverride'],c['m_columnMetadata']['m_minWidthOverride'])
# existing private-cell preload pointers
meta=next(o for o in obs.values() if o.type.name=='AssetBundle').read_typetree();entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==-970000000001000);print('PRELOAD',meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
