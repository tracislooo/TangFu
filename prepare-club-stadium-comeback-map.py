"""Read current FM database tables to recover club ID -> main-team stadium ID."""
from pathlib import Path
import sys,json,struct,re
R=Path(__file__).resolve().parent;A=R/'analysis/comeback-stadium-20261115';sys.path.insert(0,str(A/'deps'))
import zstandard
cfg=json.loads((R/'current-game-location.json').read_text('utf8'));D=Path(cfg['game_root'])/'shared/data/database/db/2700/2700_fm'
def tables(path,wanted):
 raw=path.read_bytes();off=[m.start() for m in re.finditer(re.escape(bytes.fromhex('28b52ffd')),raw)]+[len(raw)]
 def frame(i):return zstandard.ZstdDecompressor().decompressobj().decompress(raw[off[i]:off[i+1]])
 footer=frame(len(off)-2);p=0
 def string():
  nonlocal p
  n=struct.unpack_from('<I',footer,p)[0];p+=4;s=footer[p:p+n].decode();p+=n;return s
 assert string()==path.stem;n=struct.unpack_from('<I',footer,p)[0];p+=4;result={}
 for i in range(n):
  name=string();ext=string();vals=struct.unpack_from('<5Q',footer,p);p+=40
  if name in wanted:
   blob=frame(i);assert len(blob)==vals[2];result[name]=blob
 assert set(result)==set(wanted);return result
c=tables(D/'client_db.dat',{'table_3','table_21'});s=tables(D/'server_db.dat',{'table_24'})
d=c['table_3'];n=struct.unpack_from('<I',d,8)[0];p=13;clubs=[]
for i in range(n):
 start=p;p+=27;names=[]
 for _ in range(2):
  ln=struct.unpack_from('<I',d,p)[0];p+=4;assert ln<1000;names.append(d[p:p+ln].decode('utf8'));p+=ln
 endnames=p;candidates=[]
 for delta in range(3,min(60,len(d)-p-11)):
  ix,uid,uid2=struct.unpack_from('<III',d,p+delta)
  if ix==i and uid==uid2:candidates.append((delta,uid))
 assert len(candidates)==1,(i,candidates)
 delta,uid=candidates[0];p+=delta+12;clubs.append(dict(index=i,id=uid,names=names,start=start,endnames=endnames,end=p))
assert p==len(d)-9
t=s['table_24'];n=struct.unpack_from('<I',t,8)[0];p=13;teams=[]
for i in range(n):
 candidates=[];q=p
 while True:
  q=t.find(struct.pack('<I',i),q,min(len(t),p+50000))
  if q<0:break
  if q+12<len(t):
   a,b=struct.unpack_from('<II',t,q+4)
   if a==b and a>0 and a!=0xffffffff and t[q+12] in range(16):candidates.append((q,a))
  q+=1
 if i==0:
  assert (141,5) in candidates;candidates=[(141,5)]
 assert candidates,(i,p)
 q,uid=candidates[0];teams.append(dict(index=i,id=uid,start=p,end=q+12,stadium_index=struct.unpack_from('<I',t,p+17)[0],club_index=struct.unpack_from('<I',t,p+13)[0]));p=q+12
assert p==len(t)-9
st=c['table_21'];ns=struct.unpack_from('<I',st,8)[0];stadiums={i:struct.unpack_from('<I',st,12+38*i+31)[0] for i in range(ns)}
sample={x['id']:stadiums[x['stadium_index']] for x in teams if x['id'] in [602,676,680,1708]};assert sample=={602:5114336,676:676,680:680,1708:1040},sample
(A/'clubs-client.json').write_text(json.dumps(clubs,ensure_ascii=False),'utf8');(A/'teams-server.json').write_text(json.dumps(teams),'utf8')
(A/'client-frame-22.bin').write_bytes(st);(A/'server-frame-28.bin').write_bytes(t)
print(json.dumps(dict(clubs=len(clubs),teams=len(teams),stadiums=ns,samples=sample)))
