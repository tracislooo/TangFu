exec(open('inspect-tactical-table-modes-current.py',encoding='utf-8-sig').read().split('for bundle in [')[0])
for name in ['ui-datacollections_assets_all.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-tablefactories_assets_all.bundle']:
 oo={o.path_id:o for o in UnityPy.load(str(p/name)).objects}
 for o in oo.values():
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name() or ''
  if n=='MoraleDataCollection':
   d=o.read_typetree()
   for r in d['references']['RefIds']:
    a=r.get('data',{})
    if r['rid'] in [c['rid'] for c in d['m_columns']]:print(r)
  if n=='TacticsPositionDetailed':
   d=o.read_typetree();rs={r['rid']:r for r in d['references']['RefIds']}
   for i in [1008,1010,1012,1015,1016,1019,1020,1023,1030,1031,1033]:
    a=rs.get(i,{}).get('data',{});b=rs.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
    print(i,a.get('m_FullTypeName'),a.get('m_Classes'),a.get('m_Children'),b.get('name'),b.get('Binding',{}).get('m_direct'))
  if n in ['TacticTeamSelectionTableFactory','InMatchTacticsFitnessFactory','TacticTeamSelectionTableFactoryInMatch']:
   d=o.read_typetree()
   print(n,o.path_id,[(c['m_id'],c['m_valueBindings'],c['m_sortBinding']) for c in d['m_rowData'] if c['m_id'] in ['morale','morale-icon-only','condition','tactics-fatigue-value']])
