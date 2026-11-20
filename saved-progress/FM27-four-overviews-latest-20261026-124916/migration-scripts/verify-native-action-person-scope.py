exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
p=next(R.glob('Action移入属性区-*/backup/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
e=UnityPy.load(str(p));o=next(o for o in e.objects if o.path_id==-4194025542157271532);t=o.read_typetree()
for r in t['references']['RefIds']:
 if 'PluginContextMenuBindings/' in r['type']['class']:print('ORIGINAL',r['data']['BindingPaths'],r['data']['MouseButton'])
print('CURRENT',rr[1109]['data']['BindingPaths'])
for i,r in rr.items():
 d=r.get('data',{})
 for m in d.get('Mappings',[]):
  if m.get('from') in ['Person','person','player','overviewactionperson']:print(i,m)
