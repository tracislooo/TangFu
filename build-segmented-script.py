from pathlib import Path
src=Path('apply-tactical-percent-gauges.py').read_text('utf-8-sig')
head=src.split('outputs={};checks=[]')[0].replace("'tactical-percent-gauges-'","'tactical-segmented-gauges-'")
body=r'''
def replacearg(raw,old,new):
 a=args(raw);o=old.encode();n=new.encode();return pack([x.replace(bytes([len(o)])+o,bytes([len(n)])+n) for x in a])
def rounded(d,i,w,h):
 d.size(i,w,h);d.st(i,[(k,d.px(1.5)) for k in [458756,458757,458758,458759]])
outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 donor=Doc(W,pid=-930000000001001);factor=Doc(W,name='TacticalEffectivenessKeyFactorRow');rad=Doc(W,name='TacticalEffectivenessPercentageGauge')
 d=Doc(W,name='TacticalEffectivenessGauge');old=copy.deepcopy(d.d)
 host=d.add(rad,1004,1010,'TacticalSegmentedProgress');d.move(host,1010,0);d.size(host,80,16);d.st(host,[(131083,d.enum('row')),(131073,d.enum('center'))]);d.st(1012,[(131081,d.enum('none'))])
 for j in range(20):
  sw=d.add(donor,1303,host,'TacticalProgressStep'+str(j+1));d.size(sw,4,14)
  b=d.data(sw)['Binding'];a=args(b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);a[1]=a[1][:-4]+struct.pack('<i',(j+1)*5-1);b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=replacearg(pack(a),'person.PlayerCurrentAbility','MaxValue')
  empty=d.add(rad,1007,sw,'Unfilled'+str(j));rounded(d,empty,3,14);d.st(empty,[(458752,d.val(4,{'r':.27,'g':.30,'b':.32,'a':.5}))])
  filled=d.add(factor,1009,sw,'Filled'+str(j));rounded(d,filled,3,14)
  bf=d.data(filled)['BindFunction'];raw=bf['m_inputs']['m_variable']['m_argumentBytes'];raw=replacearg(raw,'57d2af85cf685c14bb872f944a729be1','2867ea5d15b7baf42b73bb5f481e2d3f');raw=replacearg(raw,'IconDataSet','StyleClass');raw=replacearg(raw,'factor.type','MaxValue');bf['m_inputs']['m_variable']['m_argumentBytes']=raw
  assert len(d.a(sw)['m_Children'])==2
 for i in [1023,1024,1026,1027]:assert d.data(i)==sd(refs(old),i)
 d.save();checks.append({'target':tag,'template':d.d['m_Name'],'segments':20,'native_colour_collection':'2867ea5d15b7baf42b73bb5f481e2d3f','native_values_preserved':True})
 d=rad;old=copy.deepcopy(d.d)
 for i in [1017,1021,1022]:
  a=args(d.data(i)['RadialGaugeInitFunc']['m_inputs']['m_variable']['m_argumentBytes']);assert struct.unpack('<i',a[2][-4:])[0]==0;a[2]=a[2][:-4]+struct.pack('<i',8);d.data(i)['RadialGaugeInitFunc']['m_inputs']['m_variable']['m_argumentBytes']=pack(a)
  d.size(i,24,24);d.st(i,[(-1,d.num(3))]);d.s['m_Rules'][d.a(i)['m_RuleIndex']]['m_Properties'][-1]['m_CustomName']='--track-width'
  assert d.data(i)['BindFunction']==sd(refs(old),i)['BindFunction']
 for i in [1007,1010]:d.size(i,24,24)
 b=d.data(1015)['TextBinding'];b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=replacearg(b['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'],'[%number#2]%','[%number#2]')
 textstyle(d,1015,9,24,12);d.st(1015,[(131104,d.px(3))])
 percent=d.add(d,1015,1007,'TacticalRingPercentSign');d.data(percent).update(TextBinding={'m_kind':0,'m_direct':{'Path':{'m_path':''},'Nullable':0},'m_visualFunction':{'m_target':{'m_guid':''},'m_inputs':{'m_variable':{'m_argumentBytes':[]}},'m_outputs':{'m_variable':{'m_argumentBytes':[]}}}},text='%',text_UxmlAttributeFlags=1,TextBinding_UxmlAttributeFlags=0)
 textstyle(d,percent,6,24,7);d.st(percent,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.px(14))]);d.size(1019,78,24)
 d.save();checks.append({'target':tag,'template':d.d['m_Name'],'ring_size':24,'segments':8,'native_colour_and_value_binding_preserved':True})
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 outputs[folder/W]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/W).write_bytes(data)
'''
tail=src[src.index('for p,b in before.items():assert'):]
Path('refine-tactical-segmented-gauges.py').write_text(head+body+tail,'utf8')
