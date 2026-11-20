from pathlib import Path
source=Path('trial-tactics-combined-layered-card.py').read_text('utf8')
exec(compile(source.split('# Keep the pitch anchor / footprint')[0].replace('tactics-combined-layered-card-trial-','inspect-tactics-v8-'),'boot','exec'))
def dump(pid):
 d=objs[pid].read_typetree();r=refs(d);s=objs[d['inlineSheet']['m_PathID']].read_typetree()
 print('\nTEMPLATE',pid,d['m_Name'])
 for i,a in r.items():
  z=a.get('data',{})
  if 'm_FullTypeName' not in z:continue
  sd=r.get(z.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  rule=s['m_Rules'][z['m_RuleIndex']]['m_Properties'] if z.get('m_RuleIndex',-1)>=0 else []
  vals={p['m_Id']:[s[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h for h in p['m_Values']] for p in rule}
  if pid in [3127595210179668386,-8273082868742719783] and not any(w in str([sd.get('name'),z.get('m_Classes'),z['m_FullTypeName']]) for w in ['Star','star','Ability','ability','Frame']):continue
  print(i,z['m_FullTypeName'],sd.get('name'),z.get('m_Classes'),z.get('m_Parent'),json.dumps(vals,ensure_ascii=False))

for pid in [-970000000009000,-970000000010000,-966834888143150418,-8736816170277224605,7377640792410373437,-2969502280056045063]:dump(pid)

