import json
from pathlib import Path
for n in ['TacticalEffectivenessGauge','TacticalEffectivenessPercentageGauge','TacticalEffectivenessKeyFactorRow']:
 d=json.loads(Path('inspect-'+n+'.json').read_text('utf8'));r={x['rid']:x for x in d['references']['RefIds']};print('\n',n)
 for i,x in r.items():
  a=x.get('data',{})
  if 'm_Parent' not in a:continue
  s=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(i,a['m_Parent'],a.get('m_FullTypeName'),a.get('m_TemplateAlias'),s.get('name'),a.get('m_Classes'))
  for k,v in s.items():
   if isinstance(v,dict) and ('m_kind' in v or 'm_target' in v):print(k,str(v).split('m_argumentBytes')[0],''.join(chr(z) if 32<=z<127 else '.' for z in (v.get('m_visualFunction',v).get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[]))))
