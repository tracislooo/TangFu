exec(open('inspect-position-layout.py',encoding='utf-8-sig').read().split('for pid in')[0])
for o in oo.values():
 if o.type.name=='MonoBehaviour':
  name=o.peek_name()
  if name and ('Role' in name and ('Cell' in name or 'Rating' in name)):
   print(o.path_id,name)
