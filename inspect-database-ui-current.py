exec((__import__('pathlib').Path(__file__).resolve().parent/'inspect-database-views-current.py').read_text('utf8').split("for bn in")[0])
for base,tag in [(G,'game'),(Path(cfg['skin_packages']),'skin')]:
 e=UnityPy.load(str(base/'ui-tableviews_assets_all.bundle'))
 for o in e.objects:
  if o.type.name=='MonoBehaviour' and o.peek_name() in ['PlayerSearchResultsViewCollection','SearchResultsTableOverview']:
   d=o.read_typetree(); print(tag,o.peek_name(),o.path_id,[(x.get('name'),x.get('DisplayValue')) for x in d.get('m_tableViewSettings',[])])
e=UnityPy.load(str(G/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'))
for o in e.objects:
 if o.type.name!='MonoBehaviour':continue
 n=o.peek_name()
 if re.search('PlayerSearch|TableView.*(Dropdown|Selector)|Table.*View.*(Options|Menu)|SearchResults',n):
  print(n,o.path_id)
  d=o.read_typetree();(out/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
