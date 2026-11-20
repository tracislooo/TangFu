exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
print('ROOT',json.dumps(rr[1006]['data'],ensure_ascii=False))
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
for o in ge.objects:
 if o.path_id==-4194025542157271532:
  t=o.read_typetree()
  for r in t.get('references',{}).get('RefIds',[]):
   if any(s in r['type']['class'] for s in ['Remapper/','ComponentElement/','PluginContext']):print(r['rid'],json.dumps(r['data'],ensure_ascii=False))
