exec((__import__('pathlib').Path(__file__).resolve().parent/'inspect-database-views-current.py').read_text('utf8').split('for bn in')[0])
for bn in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(G/bn))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  raw=o.get_raw_data()
  if any(x in raw for x in [b'row.PropertyValue',b'row.Value',b'row.ptvl']):
   d=o.read_typetree(); print(d['m_Name'],sorted(set(re.findall(r'row\.[\w.]+',json.dumps(d)))))
