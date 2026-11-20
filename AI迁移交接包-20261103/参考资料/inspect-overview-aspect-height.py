exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-overview-aspect-height-'))
for pid in [-930000000001001,-930000000001003,-940000000010000,-940000000012000]:
 doc=objs[W][pid].read_typetree();rr=refs(doc);sheet=objs[W][doc['inlineSheet']['m_PathID']].read_typetree();print('PAGE',pid)
 for i,r in rr.items():
  v=r.get('data',{});s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});name=s.get('name','');ix=v.get('m_RuleIndex',-1)
  if 'm_FullTypeName' not in v:continue
  entries={}
  for p in sheet['m_Rules'][ix]['m_Properties'] if ix>=0 else []:
   if p['m_Id'] in [131087,131096,131094,131093,131090,262150,262151]:
    val0=p['m_Values'][0];pool={2:'floats',3:'dimensions',7:'strings'}.get(val0['m_ValueType']);entries[p['m_Id']]=sheet[pool][val0['valueIndex']] if pool else val0
  minheight=entries.get(131096,{});height=entries.get(131087,{})
  if ('Scroll' in v['m_FullTypeName'] or (isinstance(minheight,dict) and minheight.get('value',0)>390) or (isinstance(height,dict) and height.get('value',0)>390) or (i in [1001,1002,1007,6320,6322])):print(i,name,v['m_FullTypeName'],entries)
