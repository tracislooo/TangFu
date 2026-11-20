exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-value-white-targets-'))
for bn,pid in [(G,-930000000001001),(G,-940000000021000),(W,-950000000000187),(W,-950000000000168)]:
 d=objs[bn][pid].read_typetree();rr=refs(d);print('DOC',pid,d['m_Name'],'USINGS',d.get('m_Usings'))
 if bn==G:
  for i,r in rr.items():
   v=r.get('data',{})
   if 'm_FullTypeName' not in v:continue
   s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});
   if i in [1018,1032,1035] or v['m_FullTypeName']=='SI.Bindable.SIText':print(i,v['m_FullTypeName'],v.get('m_TemplateAlias'),s.get('name'),s.get('TextBinding'))
 else:
  print('VALUES',[(i,rr[r['data']['m_SerializedData']['rid']]['data'].get('name')) for i,r in rr.items() if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText' and any(k in rr[r['data']['m_SerializedData']['rid']]['data'].get('name','') for k in ['Value','Number','Reputation'])][:25])
