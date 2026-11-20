exec((__import__('pathlib').Path(__file__).resolve().parent/'inspect-database-views-current.py').read_text('utf8').split('for bn in')[0])
v=UnityPy.load(str(G/'ui-tableviews_assets_all.bundle'));meta=next(o.read_typetree() for o in v.objects if o.type.name=='AssetBundle')
keys=[k for k,x in meta['m_Container'] if x['asset']['m_PathID']==-6760049043920748617];print('keys',keys)
for bn in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(G/bn))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  raw=o.get_raw_data()
  if any(k.encode() in raw for k in keys) or (b'TableView' in raw and b'Dropdown' in raw and b'inlineSheet' not in raw):
   d=o.read_typetree();n=d['m_Name'];print(bn,n,o.path_id)
   (out/(n+'.json')).write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8')
