exec(open('inspect-position-blocks.py',encoding='utf8').read().split('for i in range(s[19][2]):')[0])
for i in range(s[19][2]):
 p=s[19][0]+i*76;n=name(struct.unpack_from('<I',b,p)[0]);ns=name(struct.unpack_from('<I',b,p+4)[0]);fs,ms=struct.unpack_from('<II',b,p+20);mc,pc,fc=struct.unpack_from('<HHH',b,p+52)
 if n in ['StylePropertyId']:
  fields=[(name(struct.unpack_from('<I',b,s[11][0]+j*10)[0]),j) for j in range(fs,fs+fc)]
  if n=='StylePropertyId':
   defaults={struct.unpack_from('<I',b,s[7][0]+j*10)[0]:struct.unpack_from('<I',b,s[7][0]+j*10+6)[0] for j in range(s[7][2])}
   print(ns,n,[(fn,idx,defaults.get(idx),b[s[8][0]+defaults[idx]:s[8][0]+defaults[idx]+4].hex() if idx in defaults else '') for fn,idx in fields if any(x in fn for x in ['Border','Visibility','Opacity'])])
