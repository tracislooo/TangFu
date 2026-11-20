from pathlib import Path
s=Path('fix-tactical-hollow-ring-ten-bars.py').read_text('utf-8-sig');head=s.split('outputs={};checks=[]')[0].replace("'tactical-hollow-ring-ten-bars-'","'tactical-horizontal-visible-'")
body=r'''
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
'''
Path('fix-tactical-horizontal-visible.py').write_text(head+body+s[s.index('for p,b in before.items():assert'):],'utf8')
