exec(open('fix-overview-position-title-role-fit.py',encoding='utf-8-sig').read().split('newassets=[]')[0].replace('overview-position-headings-role-fit-','inspect-bound-page-gradients-'))
for bn in [W,G]:
 for pid,o in objs[bn].items():
  if o.type.name!='MonoBehaviour':continue
  doc=o.read_typetree()
  if 'references' not in doc:continue
  rr=refs(doc)
  for i,r in rr.items():
   v=r.get('data',{})
   if v.get('m_FullTypeName')!='SI.Bindable.SIGradient':continue
   s=rr.get(v.get('m_SerializedData',{}).get('rid'),{}).get('data',{});fn=s.get('BindGradientFunc',{});key=fn.get('m_target',{}).get('m_guid')
   if not key:continue
   args=bytes(fn['m_inputs']['m_variable']['m_argumentBytes']);readable=''.join(chr(c) if 32<=c<127 else ' ' for c in args)
   if any(k in doc['m_Name'].lower() for k in ['player','person','profile','background','site','tooltab']):print(bn[:19],pid,doc['m_Name'],i,s.get('name'),key,readable[-160:])
