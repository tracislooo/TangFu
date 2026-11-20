import struct,json
from pathlib import Path
b=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes()
s=[struct.unpack_from('<III',b,8+i*12) for i in range(31)]
out=[]
for i in range(s[0][2]-1):
    p,end=struct.unpack_from('<II',b,s[0][0]+i*4)
    size=end-p
    text=b[s[1][0]+p:s[1][0]+p+size].decode('utf-8',errors='replace')
    if len(text)<250 and any(x in text for x in ['Passing','Acceleration','PlayerCurrentAbility','PlayerAttribute','AttributesTechnical','AttributesPhysical','GoalkeepingRating','Average','SumInt']):out.append((i,text))
print(json.dumps(out,ensure_ascii=True))
def name(i):
    p=s[2][0]+i;return b[p:b.index(0,p)].decode('utf-8',errors='replace')
types=[]
for i in range(s[19][2]):
    p=s[19][0]+i*76;n=name(struct.unpack_from('<I',b,p)[0]);ns=name(struct.unpack_from('<I',b,p+4)[0])
    if n in ['PlayerProperty','PlayerAttributes','ViewableAttribute','AttributeHolder','PlayerAttributesAttribute','PlayerAttribute'] or any(x in n for x in ['AttributeBinding','PlayerProperty']):
        fs=struct.unpack_from('<I',b,p+20)[0];fc=struct.unpack_from('<H',b,p+56)[0];fields=[]
        for j in range(fs,fs+fc):
            fn,ft,token=struct.unpack_from('<IHI',b,s[11][0]+j*10);fields.append((name(fn),ft))
        types.append((ns+'.'+n,fields))
print(json.dumps(types))
