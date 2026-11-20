from pathlib import Path
s=Path('refine-tactical-segmented-gauges.py').read_text('utf-8-sig');head=s.split('outputs={};checks=[]')[0].replace("'tactical-segmented-gauges-'","'tactical-hollow-ring-ten-bars-'")
body=r'''
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
'''
Path('fix-tactical-hollow-ring-ten-bars.py').write_text(head+body+s[s.index('for p,b in before.items():assert'):],'utf8')
