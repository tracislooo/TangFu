exec(open('inspect-tactical-percent.py',encoding='utf-8-sig').read().split('for bn in')[0])
e=UnityPy.load(str(p/'ui-styles_assets_default.bundle'))
for o in e.objects:
 if o.type.name!='MonoBehaviour':continue
 d=o.read_typetree()
 for rule in d.get('m_Rules',[]):
  if 'border-radius' in str(rule.get('m_ComplexSelectors',[])).lower():
   print(o.peek_name(),rule['m_ComplexSelectors'],[(x['m_Id'],x.get('m_CustomName'),[(h['m_ValueType'],d.get({2:'floats',3:'dimensions',4:'colors',7:'strings'}.get(h['m_ValueType'],''),[])[h['valueIndex']] if h['m_ValueType'] in [2,3,4,7] else h) for h in x['m_Values']]) for x in rule['m_Properties']])

