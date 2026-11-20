exec((__import__('pathlib').Path(__file__).resolve().parent/'inspect-database-views-current.py').read_text('utf8').split('for bn in')[0])
e=UnityPy.load(str(G/'ui-tableviews_assets_all.bundle'));oo={o.path_id:o for o in e.objects};mt=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle');pid=next(v['asset']['m_PathID'] for k,v in mt['m_Container'] if k=='e0d306fce00cf5d4a99961b2d568206b')
collection=oo[pid].read_typetree();print(collection['m_Name'],pid)
ids={pid}
def pointers(x):
 if isinstance(x,dict):
  if x.get('m_FileID')==0 and x.get('m_PathID') in oo:ids.add(x['m_PathID'])
  for v in x.values():pointers(v)
 elif isinstance(x,list):
  for v in x:pointers(v)
pointers(collection)
for pid in ids:
 d=oo[pid].read_typetree();(out/(d['m_Name']+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
 if 'm_tableView' in d:print(d['m_Name'],pid,[c['m_columnID'] for c in d['m_tableView']['m_tableConfig']])
print(json.dumps(collection['m_tableViewSettings'],ensure_ascii=False))
