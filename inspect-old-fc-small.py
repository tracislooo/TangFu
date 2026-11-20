exec(open('inspect-old-fc-focused.py',encoding='utf-8-sig').read().split('for pid in')[0])
for pid, roots in [(-940000000010000,[1002,1703,1173,1188,1205,2242]),(-941100000001020,[1011,8274])]:
 d=json.loads(Path('inspect-old-fc-'+str(pid)+'.json').read_text('utf8'));rr={r['rid']:r for r in d['references']['RefIds']}
 def w(i,dep=0):
  a=rr[i]['data'];sd=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});print(' '*dep,i,sd.get('name'),a.get('m_FullTypeName'),a.get('m_TemplateAlias'), 'components',sd.get('m_components'))
  if dep<4:
   for c in a.get('m_Children',[]):w(c['rid'],dep+1)
 for i in roots:w(i)
