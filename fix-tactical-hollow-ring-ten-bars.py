from pathlib import Path
import subprocess
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactical-hollow-ring-ten-bars-').replace('hours=-4','hours=-7')
exec(compile(s,'helpers','exec'))
def args(raw):
 b=bytes(raw);p=1;out=[]
 for _ in range(b[0]):
  z=struct.unpack_from('<I',b,p)[0];p+=4;out.append(b[p:p+z]);p+=z
 assert p==len(b);return out
def pack(a):return list(bytes([len(a)])+b''.join(struct.pack('<I',len(x))+x for x in a))
def fmtbinding(d,source,fmt):
 b=copy.deepcopy(d.data(source)['TextBinding']);a=args(b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);old=b'[%number#1] - [%number#2]';new=fmt.encode();assert bytes([len(old)])+old in a[0];a[0]=a[0].replace(bytes([len(old)])+old,bytes([len(new)])+new);b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=pack(a);return b
def textstyle(d,i,size,w,h):
 d.a(i)['m_Classes']=['content-no-wrap'];d.size(i,w,h);d.st(i,[(65537,d.px(size)),(65546,d.enum('middle-center')),(65536,d.val(4,{'r':1.,'g':1.,'b':1.,'a':1.})),(131090,d.px(0)),(131093,d.px(0))])

def replacearg(raw,old,new):
 a=args(raw);o=old.encode();n=new.encode();return pack([x.replace(bytes([len(o)])+o,bytes([len(n)])+n) for x in a])
def rounded(d,i,w,h):
 d.size(i,w,h);d.st(i,[(k,d.px(1.5)) for k in [458764,458765,458759,458760]])

outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 d=Doc(W,name='TacticalEffectivenessGauge');host=d.named('TacticalSegmentedProgress');steps=[c['rid'] for c in d.a(host)['m_Children']];assert len(steps)==20
 removed=set()
 def remove(i):
  for c in d.a(i).get('m_Children',[]):remove(c['rid'])
  removed.add(i);sr=d.a(i).get('m_SerializedData',{}).get('rid',-2)
  if sr!=-2:removed.add(sr)
 for i in steps[10:]:remove(i)
 d.a(host)['m_Children']=[{'rid':i} for i in steps[:10]];d.d['references']['RefIds']=[x for x in d.d['references']['RefIds'] if x['rid'] not in removed]
 for i in removed:d.r.pop(i)
 for j,i in enumerate(steps[:10]):
  d.size(i,8,14)
  b=d.data(i)['Binding']['m_visualFunction']['m_inputs']['m_variable'];a=args(b['m_argumentBytes']);a[1]=a[1][:-4]+struct.pack('<i',(j+1)*10-1);b['m_argumentBytes']=pack(a)
  for c in d.a(i)['m_Children']:rounded(d,c['rid'],6,14)
 # Fit the text to its contents and eliminate trailing button padding and flexible width.
 for i in [1001,1002,1006,1010,1021]:
  d.a(i)['m_Classes']=[c for c in d.a(i).get('m_Classes',[]) if c!='flex-grow-class']
  d.st(i,[(131084,d.num(0)),(131085,d.num(0)),(131105,d.enum('auto')),(131097,d.px(0)),(131095,d.enum('none')),(131093,d.px(0)),(131101,d.px(0)),(131088,d.enum('flex-start'))])
 for i in [1030,1031]:
  d.st(i,[(131105,d.enum('auto')),(131097,d.px(0)),(131095,d.enum('none')),(131093,d.px(0)),(131101,d.px(0)),(65546,d.enum('middle-left'))])
 d.save();checks.append({'target':tag,'segments':10,'thresholds':list(range(10,101,10)),'text_width':'auto','native_colours_unchanged':True})
 d=Doc(W,name='TacticalEffectivenessPercentageGauge')
 for i in [1017,1021,1022]:
  before_bind=copy.deepcopy(d.data(i)['BindFunction']);b=d.data(i)['RadialGaugeInitFunc']['m_inputs']['m_variable'];a=args(b['m_argumentBytes']);assert struct.unpack('<i',a[2][-4:])[0]==8;a[2]=a[2][:-4]+struct.pack('<i',0);b['m_argumentBytes']=pack(a)
  assert d.data(i)['BindFunction']==before_bind
 d.save();checks.append({'target':tag,'ring':'native unsegmented hollow track','size':24,'track_width':3})
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 outputs[folder/W]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/W).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b,('Concurrent change',p)
for p,h in protected.items():assert sha(p.read_bytes())==h
protected.update({p:sha(b) for p,b in before.items() if p not in outputs})
tx=[]
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';tx.append({'target':str(p),'backup':str(OUT/('backup-'+tag)/p.name),'source':str(OUT/('output-'+tag)/p.name),'before':sha(before[p]),'after':sha(b)})
manifest={'installed':False,'runtime_verified':False,'checks':checks,'protected_sha256':{str(p):h for p,h in protected.items()},'scope':'Tactical effectiveness circular percentage rings and percentages to the right of horizontal gauges'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
for name,flag in [('install.ps1',''),('restore.ps1',' --restore')]:
 (OUT/name).write_text("& '"+str(PYTHON)+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+flag+'\n','utf8')
print(OUT,flush=True)
res=subprocess.run([str(PYTHON),str(R/'install-independent-resource-patch.py'),str(OUT)],capture_output=True,text=True);print(res.stdout,res.stderr);assert res.returncode==0
(R/'current-tactical-percent-gauges.json').write_text(json.dumps({'patch':str(OUT),'installed':True,'runtime_verified':False,'manifest':str(OUT/'manifest.json')},ensure_ascii=False,indent=2),'utf8')


