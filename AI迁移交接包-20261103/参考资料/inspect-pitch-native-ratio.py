exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-pitch-native-ratio-'))
for pid in [-940000000005000,-940000000008000,-940000000010020]:
 doc=objs[G][pid].read_typetree();rr=refs(doc);sheet=objs[G][doc['inlineSheet']['m_PathID']].read_typetree();print('DOC',pid)
 for i,r in rr.items():
  v=r.get('data',{});s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=s.get('name','')
  if i not in [1010,1022,1023] and 'AspectRatio' not in v.get('m_FullTypeName','') and not any(k in name for k in ['PositionZones','SafeInset','PitchRatio']):continue
  print(i,v.get('m_FullTypeName'),name,'parent',v.get('m_Parent'), 'classes',v.get('m_Classes'))
  print('  DATA',{k:x for k,x in s.items() if any(z.lower() in k.lower() for z in ['aspect','ratio','fit','scale','width','height','sizing']) and not k.endswith('UxmlAttributeFlags')})
  ix=v.get('m_RuleIndex',-1)
  print('  STYLE',[(p['m_Id'],[(sheet[{2:'floats',3:'dimensions',7:'strings'}[q['m_ValueType']]][q['valueIndex']] if q['m_ValueType'] in [2,3,7] else q) for q in p['m_Values']]) for p in sheet['m_Rules'][ix]['m_Properties']] if ix>=0 else [])
