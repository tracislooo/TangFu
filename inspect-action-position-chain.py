exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
i=1103
while i in rr:
 r=rr[i];d=r['data'];sd=rr.get(d.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
 print(i,d.get('m_FullTypeName'),sd.get('name'),'parent',d.get('m_Parent'),'pick',sd.get('pickingMode'),'pickflag',sd.get('pickingMode_UxmlAttributeFlags'))
 ix=d.get('m_RuleIndex',-1)
 if ix>=0:
  result={}
  for pr in sheet['m_Rules'][ix]['m_Properties']:
   if pr['m_Id'] in [131102,131089,131103,131104,131105,131087,458768,327681,327682]:
    result[pr['m_Id']]=[('keyword',h['valueIndex']) if h['m_ValueType']==1 else sheet[poolmap[h['m_ValueType']]][h['valueIndex']] for h in pr['m_Values']]
  print(result)
 i=d.get('m_Parent',{}).get('rid')
