from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps')
import UnityPy
p=Path(json.loads(Path('current-game-location.json').read_text('utf-8-sig'))['bundle_root'])
for bundle in ['ui-tablefactories_assets_all.bundle','ui-tableviews_assets_all.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 for o in UnityPy.load(str(p/bundle)).objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name() or ''
  if 'TacticTeamSelection' in n or 'Morale' in n or n in ['TacticsPositionDetailed','TacticsDetailedCardDetailsDesktop','TacticsDetailedCardDetailsTouch']:
   d=o.read_typetree()
   print(bundle.split('_')[0],o.path_id,n)
   if 'm_rowData' in d:print([(c['m_id'],c['m_defaultWidth'],c['m_minimumWidth'],c['m_uxmlRef']['m_AssetGUID']) for c in d['m_rowData'] if any(k in c['m_id'].lower() for k in ['morale','condition','fatigue','sharpness','role','pos','goal','assist','selection','ability','star'])])
   if 'm_tableView' in d:print([(c['m_columnID'],c['m_columnMetadata']['m_widthOverride']) for c in d['m_tableView']['m_tableConfig']])
   for r in d.get('references',{}).get('RefIds',[]):
    a=r.get('data',{})
    if 'm_Parent' in a and any('frame' in c.lower() or 'drag' in c.lower() or 'border' in c.lower() for c in a.get('m_Classes',[])):print(r['rid'],a.get('m_Classes'),a.get('m_Parent'))
   if 'Morale' in n and 'inlineSheet' in d: Path('probe-'+str(o.path_id)+'.json').write_text(json.dumps(d,ensure_ascii=False,indent=1),'utf8')
