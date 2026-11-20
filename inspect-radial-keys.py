exec(open('inspect-tactical-percent.py',encoding='utf-8-sig').read().split('for bn in')[0])
e=UnityPy.load(str(p/'ui-styles_assets_default.bundle'))
for o in e.objects:
 if o.type.name=='AssetBundle':continue
 d=o.read_typetree()
 print(o.type.name,list(d)[:15]);
 if 'm_ComplexSelectors' not in d:continue
 print(o.peek_name(),d['m_ComplexSelectors'][:1]);print([x for rule in d['m_Rules'] for x in rule['m_Properties'] if 'radial' in str(x).lower() or 'gauge' in str(x).lower()][:20])

