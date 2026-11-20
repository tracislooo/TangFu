exec(open('inspect-position-layout.py',encoding='utf-8-sig').read().split('for pid in')[0])
for n in ['ui-tablefactories_assets_all.bundle']:
 e2=UnityPy.load(str(p.parent/n));obs={x.path_id:x for x in e2.objects}
 for o in e2.objects:
  if o.type.name=='AssetBundle':
   for key,c in o.read_typetree()['m_Container']:
    if key=='494078080b489c44fae783144f43505c':
     d=obs[c['asset']['m_PathID']].read_typetree();Path('role-factory.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),'utf8');print(json.dumps(d,ensure_ascii=False)[:11000])
