import struct,re,json
from pathlib import Path
R=Path(__file__).resolve().parent
b=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes();s=[struct.unpack_from('<III',b,8+i*12) for i in range(31)]
def name(i):
 p=s[2][0]+i
 return b[p:b.index(0,p)].decode('utf8',errors='replace')
lines=[]
for i in range(s[19][2]):
 p=s[19][0]+i*76;n=name(struct.unpack_from('<I',b,p)[0]);ns=name(struct.unpack_from('<I',b,p+4)[0])
 if not re.search('TableView|TranslationID|TranslationDatabase|ChoiceDisplay|ChoiceList',n):continue
 fs,ms=struct.unpack_from('<II',b,p+20);mc,pc,fc=struct.unpack_from('<HHH',b,p+52)
 fields=[]
 for j in range(fs,fs+fc):
  fn,ft,token=struct.unpack_from('<IHI',b,s[11][0]+j*10);fields.append(name(fn))
 stride=s[5][1]//s[5][2];methods=[]
 for j in range(ms,ms+mc):
  q=s[5][0]+j*stride;methods.append((name(struct.unpack_from('<I',b,q)[0]),j,b[q:q+stride].hex()))
 lines.append({'name':ns+'.'+n,'fields':fields,'methods':methods})
(R/'table-choice-metadata.json').write_text(json.dumps(lines,ensure_ascii=False,indent=2),'utf8');print([(x['name'],x['fields']) for x in lines])
