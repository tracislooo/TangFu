exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for pid in [FULL,-930000000001003]:
 d=objects[pid].read_typetree();sr={r['rid']:r for r in d['references']['RefIds']};ss=objects[d['inlineSheet']['m_PathID']].read_typetree();print('TREE',d['m_Name'])
 for i,r in sr.items():
  a=r.get('data',{});sd=sr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if a.get('m_Parent',{}).get('rid') in [1000,1705] or sd.get('name') in ['FullOverviewFrame','FrameActions'] or i in [1001,1002]:
   print(i,a.get('m_FullTypeName'),sd.get('name'),a.get('m_Classes'))
   ix=a.get('m_RuleIndex',-1)
   if ix>=0:
    print({p['m_Id']:[('kw',h['valueIndex']) if h['m_ValueType']==1 else ss[poolmap[h['m_ValueType']]][h['valueIndex']] for h in p['m_Values']] for p in ss['m_Rules'][ix]['m_Properties'] if p['m_Id'] in [131087,131096,131094,131084,131085,458768,131082]})
