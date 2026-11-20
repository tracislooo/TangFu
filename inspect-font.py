exec(open('inspect-request-overviews.py',encoding='utf-8-sig').read().split('for x in o.values():')[0])
e2=UnityPy.load(str(p.parent/'ui-styles_assets_default.bundle'))
for ob in e2.objects:
 if ob.type.name!='MonoBehaviour':continue
 d=ob.read_typetree()
 if 'm_Rules' not in d:continue
 for rule in d['m_Rules']:
  if any(part['m_Value'] in ['body-sm','body-md','body-md-strong','text-cell-medium-strong'] for c in rule['m_ComplexSelectors'] for s in c['m_Selectors'] for part in s['m_Parts']):
   print([(part['m_Value']) for c in rule['m_ComplexSelectors'] for s in c['m_Selectors'] for part in s['m_Parts']],[(pr['m_Id'],[d.get({2:'floats',3:'dimensions',5:'strings',7:'strings'}.get(v['m_ValueType'],''),[])[v['valueIndex']] if v['m_ValueType'] in [2,3,5,7] else v for v in pr['m_Values']]) for pr in rule['m_Properties'] if pr['m_Id']==65537])
d=o[-950000000000162].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']}
for i,r in rr.items():
 a=r.get('data',{});si=a.get('m_SerializedData',{}).get('rid');sd=rr.get(si,{}).get('data',{});cur=i
 for z in range(15):
  if cur==1297:
   if a.get('m_FullTypeName') in ['SI.Bindable.SIText','UnityEngine.UIElements.TemplateContainer']:print(i,a.get('m_FullTypeName'),sd.get('name'),a.get('m_TemplateAlias'),a.get('m_Classes'))
   break
  cur=rr.get(cur,{}).get('data',{}).get('m_Parent',{}).get('rid')
