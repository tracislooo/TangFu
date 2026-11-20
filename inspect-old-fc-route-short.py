exec(open('inspect-old-fc-binding-route.py',encoding='utf-8-sig').read().split('for f in')[0])
spec=importlib.util.spec_from_file_location('cat',r/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm);cat=cm.Catalog((root.parent/'catalog.bin').read_bytes())
for key in ['1f6ebbeeaeba50cbbb57ef2d123b47dc','e898cf8de19d543984f58379abb35340']:
 print('CAT',key,[(i,cat.location(i))for i in cat.locations(key)])
e=UnityPy.load(str(root/L));oo={o.path_id:o for o in e.objects}
for pid in [-950000000000230,-940000000010030,3901662990989568885]:
 d=oo[pid].read_typetree();print('DESC',pid,json.dumps(d,ensure_ascii=False)if pid!=3901662990989568885 else json.dumps([x for x in d['m_gridComponents']if 'Overview' in x['m_elementID']or x['m_elementID']=='PlayerAttributesBlock']))
