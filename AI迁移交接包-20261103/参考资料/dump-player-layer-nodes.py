import json
from pathlib import Path
P=Path('player-page-layer-inspection')
for n in ['PlayerReport','GameWorldBackground','ReportIconsBelowPlayerTopBackground','OverviewToggle_FullOverview']:
 t=json.loads((P/(n+'.json')).read_text('utf8'));s=json.loads((P/(n+'-style.json')).read_text('utf8'));rr={r['rid']:r for r in t['references']['RefIds']};print('\nTEMPLATE',n,'using',t.get('m_Usings',t.get('m_UsingEntries')))
 for r in rr.values():
  d=r.get('data',{});sd=rr.get(d.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if 'm_FullTypeName' not in d:continue
  z={'id':r['rid'],'parent':d.get('m_Parent'),'type':d['m_FullTypeName'],'name':sd.get('name'),'classes':d.get('m_Classes'),'rule':d.get('m_RuleIndex')}
  if n=='OverviewToggle_FullOverview' and not any(x in str(z).lower() for x in ['background','gradient','overlay','frame']):continue
  i=d.get('m_RuleIndex',-1)
  if i>=0:
   props=[]
   for p in s['m_Rules'][i]['m_Properties']:
    vals=[]
    for v in p['m_Values']:
     ty=v['m_ValueType'];idx=v['valueIndex'];a={2:'floats',3:'dimensions',4:'colors',5:'assets',7:'strings',8:'strings',11:'scalableImages'}.get(ty)
     vals.append([ty,s[a][idx] if a and a in s and idx<len(s[a]) else idx])
    props.append([p['m_Id'],p.get('m_CustomName'),vals])
   z['style']=props
  if any(x in d['m_FullTypeName'] for x in ['Gradient','Image']):z['serialized']=sd
  print(json.dumps(z,ensure_ascii=False))
