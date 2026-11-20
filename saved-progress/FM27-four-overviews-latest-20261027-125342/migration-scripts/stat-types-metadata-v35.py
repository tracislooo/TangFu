import struct
from pathlib import Path
b=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes()
s=[struct.unpack_from('<III',b,8+i*12) for i in range(31)]
def name(i):
    p=s[2][0]+i
    return b[p:b.index(0,p)].decode('utf-8',errors='replace')
print('methods section',s[5], 'stride',s[5][1]/s[5][2])
for i in range(s[19][2]):
    p=s[19][0]+i*76
    n=name(struct.unpack_from('<I',b,p)[0]);ns=name(struct.unpack_from('<I',b,p+4)[0])
    fs,ms=struct.unpack_from('<II',b,p+20)
    mc,pc,fc=struct.unpack_from('<HHH',b,p+52)
    if (ns.startswith('SI.') and any(x in n.lower() for x in ['booleanarg','visible','remap','calc','expression','multiply','doublevisualarg','floatvisualarg'])):
        fields=[]
        for j in range(fs,fs+fc):
            fn,ft,token=struct.unpack_from('<IHI',b,s[11][0]+j*10)
            fields.append((name(fn),ft))
        stride=int(s[5][1]/s[5][2]);methods=[]
        for j in range(ms,ms+mc):
            q=s[5][0]+j*stride
            mn=name(struct.unpack_from('<I',b,q)[0])
            if any(x in mn for x in ['Expected','PassCompletedPer90','TacklesCompletedPer90']):
                methods.append((mn, b[q:q+stride].hex()))
        if fields or methods:
            print(ns+'.'+n, 'fields',fields, 'methods',methods)
