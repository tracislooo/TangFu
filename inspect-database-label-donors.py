exec((__import__('pathlib').Path(__file__).resolve().parent/'inspect-database-views-current.py').read_text('utf8').split('for bn in')[0])
for bn,names in [('ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',['GenericDisplayValuePairDropdownRow','PlayerDatabaseMainContentBlock','PersonSearchMainContentBlock','PersonSearchMainContentBlock_MinRes']),('ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',['TacticsPositionCombined'])]:
 e=UnityPy.load(str(G/bn))
 for o in e.objects:
  if o.type.name!='MonoBehaviour' or o.peek_name() not in names:continue
  d=o.read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
  (out/(d['m_Name']+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
  for r in rr.values():
   a=r.get('data',{});sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   if d['m_Name']=='GenericDisplayValuePairDropdownRow' or sd.get('name')=='PitchFitnessAbove7' or a.get('m_TemplateAlias')=='TableViewDropdown':print(d['m_Name'],r['rid'],a,sd)
