from pathlib import Path
import subprocess
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactical-horizontal-visible-').replace('hours=-4','hours=-7')
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
base=R/'tactical-hollow-ring-ten-bars-20261108-140206'
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 d=Doc(W,name='TacticalEffectivenessGauge');original=copy.deepcopy(d.d)
 be=UnityPy.load(str(base/('backup-'+tag)/W));bo={o.path_id:o for o in be.objects};bd=bo[d.obj.path_id].read_typetree();br=refs(bd);bs=bo[bd['inlineSheet']['m_PathID']].read_typetree()
 for i in [1001,1002,1006,1010,1021,1030,1031]:
  d.a(i)['m_Classes']=copy.deepcopy(br[i]['data']['m_Classes']);ri=br[i]['data']['m_RuleIndex']
  if ri<0:d.a(i)['m_RuleIndex']=-1;continue
  rule=copy.deepcopy(bs['m_Rules'][ri])
  for prop in rule['m_Properties']:
   for ix,h in enumerate(prop['m_Values']):
    if h['m_ValueType'] in poolmap:prop['m_Values'][ix]=d.val(h['m_ValueType'],copy.deepcopy(bs[poolmap[h['m_ValueType']]][h['valueIndex']]))
  d.s['m_Rules'].append(rule);d.a(i)['m_RuleIndex']=len(d.s['m_Rules'])-1
 # Preserve native ancestor sizing; the visible contents alone define the compact button width.
 d.a(1010)['m_Classes']=[c for c in d.a(1010)['m_Classes'] if c!='flex-grow-class']
 d.st(1010,[(131084,d.num(0)),(131085,d.num(0)),(131097,d.px(112)),(131101,d.px(0)),(131093,d.px(0))])
 d.size(1030,27,24);d.st(1030,[(65546,d.enum('middle-right')),(131090,d.px(4)),(131093,d.px(0))])
 d.size(1031,78,24);d.st(1031,[(65546,d.enum('middle-right')),(131090,d.px(4)),(131093,d.px(0))])
 host=d.named('TacticalSegmentedProgress');d.size(host,80,16);assert len(d.a(host)['m_Children'])==10
 for i,a in refs(original).items():
  if 'm_Parent' in a.get('data',{}):assert d.data(i)==sd(refs(original),i),('binding changed',i)
 d.save();checks.append({'target':tag,'native_ancestor_layout_restored':True,'segments':10,'all_serialized_bindings_unchanged':True,'text_width':27})
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


