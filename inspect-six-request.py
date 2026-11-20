exec(open('inspect-request-overviews.py',encoding='utf-8-sig').read().split('for x in o.values():')[0])
for pid in [-930000000001001,-950000000000187,-941100000001000,-940000000010000,-940000000012000,-941100000001010]:
 d=o[pid].read_typetree();rr={r['rid']:r for r in d['references']['RefIds']};print('\nPAGE',pid,d['m_Name']);print('USINGS',[(u['alias'],u['path']) for u in d.get('m_Usings',[]) if any(k in u['alias'] for k in ['Season','Bans'])])
 for i,r in rr.items():
  a=r.get('data',{});s=rr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{});nm=s.get('name','')
  if any(k in nm for k in ['Bans','Season','Nation','Club']) or 'Scroll' in a.get('m_FullTypeName',''):
   print(i,nm,a.get('m_FullTypeName'),a.get('m_TemplateAlias'),a.get('m_Children'),{k:v for k,v in s.items() if any(t in k for t in ['Scroll','Mode','Direction','Binding']) and not isinstance(v,dict)})
