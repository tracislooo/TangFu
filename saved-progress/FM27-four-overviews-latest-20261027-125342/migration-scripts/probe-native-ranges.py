exec(open('probe-action-native.py',encoding='utf-8-sig').read().split('for a,size')[0])
for term in [b'SIButton.cs',b'PluginContextMenuBindings.cs',b'ContextMenuDescriptionManipulator.cs']:
 starts=[];pos=base
 while True:
  pos=b.find(term,pos)
  if pos<0:break
  st=b.rfind(b'\0',base,pos)+1;starts.append(st-base);pos+=len(term)
 ranges=[]
 for idx in range(n):
  a,m,f,l,x=struct.unpack_from('<Q4I',b,24+idx*24)
  if f in starts and (not ranges or a-ranges[-1][1]>32):ranges.append([a,a,l])
  elif f in starts:ranges[-1][1]=a
 print(term,[(hex(a),hex(z),l) for a,z,l in ranges])
