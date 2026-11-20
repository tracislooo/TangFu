from pathlib import Path
import subprocess
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactical-percent-gauges-').replace('hours=-4','hours=-7')
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
outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 d=Doc(W,name='TacticalEffectivenessGauge');old=copy.deepcopy(d.d)
 single=fmtbinding(d,1031,'[%number#2]%');rang=fmtbinding(d,1031,'[%number#1]%–[%number#2]%')
 d.move(1021,1010,1)
 for i,b,w in [(1030,single,39),(1031,rang,78)]:
  d.data(i).update(TextBinding=b,TextBinding_UxmlAttributeFlags=1);textstyle(d,i,11,w,24);d.st(i,[(131090,d.px(5))])
 for i in [1023,1024,1026,1027]:assert d.r[i]==refs(old)[i] and d.data(i)==sd(refs(old),i)
 d.save();checks.append({'target':tag,'template':d.d['m_Name'],'native_steppers_unchanged':True})
 d=Doc(W,name='TacticalEffectivenessPercentageGauge');old=copy.deepcopy(d.d)
 single=fmtbinding(d,1019,'[%number#2]%');rang=fmtbinding(d,1019,'[%number#1]%–[%number#2]%')
 # Native data and colour functions stay intact; only ring geometry and label presentation change.
 for i in [1017,1021,1022]:
  a=args(d.data(i)['RadialGaugeInitFunc']['m_inputs']['m_variable']['m_argumentBytes']);assert struct.unpack('<i',a[2][-4:])[0]==10;a[2]=a[2][:-4]+struct.pack('<i',0);d.data(i)['RadialGaugeInitFunc']['m_inputs']['m_variable']['m_argumentBytes']=pack(a)
  d.a(i)['m_Classes']=[c for c in d.a(i)['m_Classes'] if c not in ['width-height-16px','sisegemntedradialgauge-tactical-effectiveness']]
  d.size(i,30,30);d.st(i,[(-1,d.num(2))]);d.s['m_Rules'][d.a(i)['m_RuleIndex']]['m_Properties'][-1]['m_CustomName']='--track-width'
  assert d.data(i)['BindFunction']==sd(refs(old),i)['BindFunction']
 d.size(1007,30,30);d.size(1010,30,30)
 d.move(1015,1007);d.data(1015).update(TextBinding=single,TextBinding_UxmlAttributeFlags=1);textstyle(d,1015,8,30,30);d.st(1015,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.px(0))])
 # Ranged scouting values remain ranges instead of falsely displaying one exact value.
 d.move(1019,1005);d.data(1019).update(TextBinding=rang,TextBinding_UxmlAttributeFlags=1);textstyle(d,1019,10,78,30)
 d.st(1004,[(131073,d.enum('center'))]);d.st(1005,[(131073,d.enum('center'))]);d.save();checks.append({'target':tag,'template':d.d['m_Name'],'ring_size':30,'track_width':2,'native_colour_and_value_binding_preserved':True})
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
