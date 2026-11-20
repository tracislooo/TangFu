from pathlib import Path
exec(Path('inspect-tactics-v8.py').read_text('utf8').split('for pid in [312759')[0])
dump(-970000000005000)
for folder in [GAME]:
 e=UnityPy.load(str(folder/'ui-styles_assets_default.bundle'))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  for rule in d.get('m_Rules',[]):
   sels=str(rule['m_ComplexSelectors'])
   if any(k in sels for k in ['frame-tactics-nav-menu','tactics-nav-primary-actions-property-1-base','tactics-nav-secondary-actions-property-1-team-shape','tactics-subs-block']):
    print('RULE',d['m_Name'],sels,[(p['m_Id'],[(d[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h) for h in p['m_Values']]) for p in rule['m_Properties']])
