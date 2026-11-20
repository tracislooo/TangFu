from pathlib import Path
import sys,json,re
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(cfg['bundle_root'])
out=R/'database-views-research';out.mkdir(exist_ok=True)
for bn in ['ui-tableviews_assets_all.bundle','ui-tablefactories_assets_all.bundle']:
 e=UnityPy.load(str(G/bn));summary=[]
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name()
  if ('tableviews' in bn and re.search('Search|Shortlist',n)) or n=='PlayerTableFactory':
   d=o.read_typetree();(out/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
   summary.append({'name':n,'pid':o.path_id,'columns':[c['m_columnID'] for c in d.get('m_tableView',{}).get('m_tableConfig',[])], 'settings':d.get('m_tableViewSettings')})
 print(json.dumps(summary,ensure_ascii=False))
