exec(open('inspect-tactical-table-modes-current.py',encoding='utf-8-sig').read().split('for bundle in [')[0])
w='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
oo={o.path_id:o for o in UnityPy.load(str(p/w)).objects}
meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
keys=['049d18b3b3058354f81f0ab6e30f3b1c','51e2481822451a041b89d2b2d814c8cc','db62e5def695f584480f6071eba32320','f1935ffe2854de64d878ec4e5b5c82bd','bf7d796066412f347ab90d29414bc453','f736b22c080436d41abc8af203d87789']
for key,v in meta['m_Container']:
 if key not in keys:continue
 o=oo[v['asset']['m_PathID']];d=o.read_typetree();print(key,d['m_Name'])
 if 'inlineSheet' not in d:continue
 s=oo[d['inlineSheet']['m_PathID']].read_typetree()
 for a in d['references']['RefIds']:
  n=a.get('data',{});idx=n.get('m_RuleIndex',-1)
  if idx<0:continue
  rule=s['m_Rules'][idx]
  vals=[(p['m_Id'],[s['dimensions'][h['valueIndex']] if h['m_ValueType']==3 else s['floats'][h['valueIndex']] if h['m_ValueType']==2 else h for h in p['m_Values']]) for p in rule['m_Properties'] if p['m_Id'] in [131105,131097,131095,327681]]
  if vals:print(a['rid'],n['m_FullTypeName'],vals)
