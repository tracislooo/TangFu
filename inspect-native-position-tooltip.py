exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-native-position-tooltip-'))
for bn,pid in [(W,4269476442492208794),(G,-940000000018000)]:
 d=objs[bn][pid].read_typetree();rr=refs(d);print('DOC',pid,d['m_Name'],d.get('m_Usings'))
 for i,r in rr.items():
  v=r.get('data',{})
  if 'm_FullTypeName' not in v:continue
  if bn==G and 'PositionZone_GK' not in str(rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{})) and 'Tooltip' not in v['m_FullTypeName']:continue
  s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print('NODE',i,v['m_FullTypeName'],s.get('name'),'parent',v.get('m_Parent'),'children',v.get('m_Children'));print(json.dumps({k:x for k,x in s.items() if k not in ['Events'] and not k.endswith('UxmlAttributeFlags')},ensure_ascii=False)[:3500])
