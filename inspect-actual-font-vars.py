exec(open('inspect-font.py',encoding='utf-8-sig').read().split('for ob in e2.objects:')[0])
for ob in e2.objects:
 if ob.type.name!='MonoBehaviour':continue
 d=ob.read_typetree()
 if 'm_Rules' not in d:continue
 print('SHEET',ob.path_id,d.get('m_Name'))
 for rule in d['m_Rules']:
  for pr in rule['m_Properties']:
   if pr.get('m_CustomName') and any(x in pr['m_CustomName'] for x in ['font','text','body']):
    print(pr['m_CustomName'],[(v['m_ValueType'],d.get({2:'floats',3:'dimensions',5:'strings',7:'strings',8:'strings'}.get(v['m_ValueType'],''),[])[v['valueIndex']] if v['m_ValueType'] in [2,3,5,7,8] else v) for v in pr['m_Values']])
