exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for o in objects.values():
 if o.type.name=='MonoBehaviour' and o.peek_name() in ['PlayerAttributesTooltipBlock','PlayerAttributesSmallBlock','PlayerAttributesStandardBlock','PlayerAttributesLargeBlock','PlayerAttributesCompactBlock','OverviewToggle_PortraitAttributes','PlayerReportHeader']:
  d=o.read_typetree();print(o.path_id,d['m_Name'],[(r['rid'],r['data'].get('BindingPaths')) for r in d.get('references',{}).get('RefIds',[]) if 'PluginContextMenuBindings/' in r['type']['class']])
