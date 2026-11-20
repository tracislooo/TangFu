exec(open('inspect-tactics-tab-color.py',encoding='utf-8-sig').read().split('for name in [')[0])
for bundle in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle']:
 for o in UnityPy.load(str(base/bundle)).objects:
  if o.type.name!='MonoBehaviour':continue
  nm=o.peek_name() or ''
  if 'PitchHeader' not in nm and 'CollapsablePitch' not in nm and 'ButtonGroup' not in nm:continue
  d=o.read_typetree();r={a['rid']:a for a in d.get('references',{}).get('RefIds',[])}
  for i,a in r.items():
   if a.get('data',{}).get('m_FullTypeName')=='SI.Bindable.ButtonGroup':
    print(bundle,nm,i,a['data']['m_Children'],r[a['data']['m_SerializedData']['rid']]['data'])
