exec(open('inspect-tactical-table-modes-current.py',encoding='utf-8-sig').read().split('for bundle in [')[0])
from collections import Counter
from glob import glob
e=UnityPy.load(str(p/'ui-icons_assets_1x.bundle'),str(p/'ui-iconspriteatlases_assets_1x.bundle'))
o=next(x for x in e.objects if x.path_id==-5959038453500707990)
print(Counter((r,g,b) for r,g,b,a in o.read().image.convert('RGBA').getdata() if a>200).most_common(6))
for file in p.glob('ui-styles_assets_1x.bundle'):
 for ob in UnityPy.load(str(file)).objects:
  if ob.type.name!='MonoBehaviour':continue
  s=ob.read_typetree()
  for rule in s.get('m_Rules',[]):
   if any(t['m_Value']=='ability-max-potential-level-fullfilled-youth-false' for l in rule['m_ComplexSelectors'] for b in l['m_Selectors'] for t in b['m_Parts']):
    print('star',[(a['m_Id'],[s['dimensions'][h['valueIndex']] for h in a['m_Values'] if h['m_ValueType']==3]) for a in rule['m_Properties']])
