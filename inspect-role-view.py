exec(open('inspect-position-layout.py',encoding='utf-8-sig').read().split('for pid in')[0])
b=p.parent
for n,key in [('ui-tableviews_assets_all.bundle','cc14c4f1722a75c4c9267bf074000f3f')]:
 e2=UnityPy.load(str(b/n))
 for f in e2.files.values():
  pass
 for o in e2.objects:
  if o.type.name=='AssetBundle':
   for c in o.read_typetree()['m_Container']:
    if c[0]==key:
     pid=c[1]['asset']['m_PathID'];obs={x.path_id:x for x in e2.objects};print(json.dumps(obs[pid].read_typetree(),ensure_ascii=False))
