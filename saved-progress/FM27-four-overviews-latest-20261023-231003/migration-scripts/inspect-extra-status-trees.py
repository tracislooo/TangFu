exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for pid in [1504705285788836261,3052255369264346086,3508926604620743622,1835999027414418521,5108509966786251923]:
 d=objects[pid].read_typetree();r={x['rid']:x for x in d['references']['RefIds']};print('\nASSET',pid,d['m_Name'])
 def walk(i,dep=0):
  a=r[i].get('data',{});s=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  if pid!=5108509966786251923 or i in [1042,1043,1088,1156,1217,1218]:print(' '*dep,i,a.get('m_FullTypeName'),a.get('m_TemplateAlias',''),s.get('name',''),s.get('DebugDisplay',''),s.get('bindingPath',''))
  for c in a.get('m_Children',[]):walk(c['rid'],dep+1)
 walk(d['m_VisualTree']['rid'])
