exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
for o in UnityPy.load(str(p.parent/'ui-tablefactories_assets_all.bundle')).objects:
 if o.type.name!='MonoBehaviour':continue
 d=o.read_typetree()
 for c in d.get('m_rowData',[]):
  if c.get('m_id')=='condition':print(d['m_Name'],o.path_id,json.dumps(c))
