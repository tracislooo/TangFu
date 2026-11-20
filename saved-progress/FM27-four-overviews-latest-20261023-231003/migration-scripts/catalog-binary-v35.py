import struct
from pathlib import Path

NULL = 0xffffffff
class Catalog:
    def __init__(self, data):
        self.data = bytearray(data)
        self.header = self.unpack(0, '8I')
        self.key_records = self.array(self.header[2], '2I')
        self.string_cache = {}
    def unpack(self, offset, fmt):
        return struct.unpack_from('<'+fmt, self.data, offset)
    def array(self, offset, fmt):
        if offset == NULL:return []
        size = self.unpack(offset-4,'I')[0]
        stride = struct.calcsize('<'+fmt)
        assert size % stride == 0 and offset+size <= len(self.data)
        return [self.unpack(p,fmt) for p in range(offset,offset+size,stride)]
    def string(self, offset, sep=''):
        if offset == NULL:return None
        key = (offset,sep)
        if key in self.string_cache:return self.string_cache[key]
        if sep and offset & 0x40000000:
            chunks=[];n=offset
            while n != NULL:
                st,n=self.unpack(n & 0x3fffffff,'2I')
                chunks.append(self.string(st))
            result=sep.join(reversed(chunks))
        else:
            p=offset & 0x3fffffff;size=self.unpack(p-4,'I')[0]
            assert p+size <= len(self.data)
            result=self.data[p:p+size].decode('utf-16le' if offset & 0x80000000 else 'ascii')
        self.string_cache[key]=result
        return result
    def typename(self, offset):
        a,c=self.unpack(offset,'2I')
        return self.string(a,'.'),self.string(c,'.')
    def object(self, offset):
        if offset == NULL:return None
        t,p=self.unpack(offset,'2I');assembly,cls=self.typename(t)
        if cls == 'System.String':
            s,sep=self.unpack(p,'IH');return self.string(s,chr(sep) if sep else '')
        if cls == 'System.Int32':return self.unpack(p,'i')[0]
        return ('opaque',offset,cls)
    def keys(self):
        return [(self.object(k),loc) for k,loc in self.key_records]
    def locations(self,key):
        matches=[l for k,l in self.keys() if k==key]
        assert len(matches)==1,(key,len(matches))
        return [p[0] for p in self.array(matches[0],'I')]
    def location(self,offset):
        a,i,p,d,h,e,t=self.unpack(offset,'7I')
        return {'offset':offset,'primary':self.string(a,'/'),'internal':self.string(i,'/'),
            'provider':self.string(p,'.'),'dependencies':[v[0] for v in self.array(d,'I')],
            'type':self.typename(t),'raw':(a,i,p,d,h,e,t)}
    def append(self, data, array=False):
        if array:self.data.extend(struct.pack('<I',len(data)))
        p=len(self.data);self.data.extend(data);return p
    def add_string(self,s):return self.append(s.encode('ascii'),True)
    def add_key_location(self,key,template_location,dependency_location):
        assert all(k!=key for k,l in self.keys())
        raw=list(self.unpack(template_location,'7I'))
        raw[0]=raw[1]=self.add_string(key)
        dep=self.unpack(dependency_location,'7I')
        raw[3],raw[4]=dep[3],dep[4]
        loc=self.append(struct.pack('<7I',*raw))
        # Reuse the catalog's System.String type descriptor.
        st=next(self.unpack(k,'2I')[0] for k,l in self.key_records if isinstance(self.object(k),str))
        remap=self.append(struct.pack('<IHH',raw[0],0,0))
        keyobj=self.append(struct.pack('<2I',st,remap))
        locset=self.append(struct.pack('<I',loc),True)
        records=self.key_records+[(keyobj,locset)]
        offset=self.append(b''.join(struct.pack('<2I',*r) for r in records),True)
        struct.pack_into('<I',self.data,8,offset)
        return bytes(self.data)

if __name__=='__main__':
    import json
    p=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/catalog.bin')
    c=Catalog(p.read_bytes());keys=c.keys()
    print('header',c.header,'keys',len(keys))
    for target in ['f6f314e9db56227459137669d87c44e9']:
        for loc in c.locations(target):print(json.dumps(c.location(loc)))
    found=[]
    for k,l in keys:
        if isinstance(k,str) and ('report-player-banner-max' in k.lower()):
            found.append((k,[c.location(p[0]) for p in c.array(l,'I')]))
    print(json.dumps(found))
