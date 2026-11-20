import struct,re
from pathlib import Path
b=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes()
s=[struct.unpack_from('<III',b,8+i*12) for i in range(31)]
def name(i):
 p=s[2][0]+i;return b[p:b.index(0,p)].decode('utf8',errors='replace')
for i in range(s[19][2]):
 p=s[19][0]+i*76;n=name(struct.unpack_from('<I',b,p)[0]);ns=name(struct.unpack_from('<I',b,p+4)[0]);fs,ms=struct.unpack_from('<II',b,p+20);mc,pc,fc=struct.unpack_from('<HHH',b,p+52)
 methods=[]
 for j in range(ms,ms+mc):
  q=s[5][0]+j*(s[5][1]//s[5][2]);mn=name(struct.unpack_from('<I',b,q)[0])
  if any(x in mn.lower() for x in ['fatigue','sharpness','conditionpercentage','conditionpercent','conditionvalue','get_condition']):methods.append((j,mn))
 if methods and (ns.startswith(('SI.','FM.')) or 'Player' in n):print(i,ns+'.'+n,methods)
for i in range(s[0][2]-1):
 p,end=struct.unpack_from('<II',b,s[0][0]+i*4);t=b[s[1][0]+p:s[1][0]+end].decode('utf8',errors='replace')
 if len(t)<120 and any(x in t.lower() for x in ['fatigue','sharpness','conditionpercent']):print('LITERAL',i,repr(t))
