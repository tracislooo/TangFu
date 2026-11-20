exec(open('inspect-tactical-table-modes-current.py',encoding='utf-8-sig').read().split('for bundle in [')[0])
for fp in [p/'ui-styles_assets_1x.bundle',p/'ui-styles_assets_default.bundle']:
 for o in UnityPy.load(str(fp)).objects:
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  for rule in d.get('m_Rules',[]):
   ns={a['m_Value'] for sel in rule['m_ComplexSelectors'] for st in sel['m_Selectors'] for a in st['m_Parts']}
   if 'scaling-icons-form-morale-1-size-small-16px' in ns:
    h=next(x for x in rule['m_Properties'] if x['m_Id']==458753)['m_Values'][0];ptr=d['assets'][h['valueIndex']];print(ptr,o.assets_file.externals[ptr['m_FileID']-1].name)
   if 'frame-330-tactics-visualiser-player-indicator' in ns:print(ns,[x['m_Id'] for x in rule['m_Properties']])
