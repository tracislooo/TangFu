from pathlib import Path
import subprocess
s=Path('inspect-scoreboard-position.py').read_text('utf-8-sig').split('for folder,tag in [')[0].replace('inspect-scoreboard-position-','match-scoreboard-left-').replace('hours=-4','hours=-7')
exec(compile(s,'backup-current-independent-branches','exec'))
outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[M]=UnityPy.load(before[folder/M]);objs[M]={o.path_id:o for o in env[M].objects};changes[M]={};hashes[M]={i:sha(o.get_raw_data()) for i,o in objs[M].items()}
 d=Doc(M,name='OverviewHeader');old=copy.deepcopy(d.d);rr=refs(old)
 assert 'centre-avoid-centred' in d.a(1034)['m_Classes']
 d.a(1034)['m_Classes']=[c for c in d.a(1034)['m_Classes'] if c!='centre-avoid-centred']
 d.st(1034,[(131102,d.enum('absolute')),(131089,d.px(0)),(131103,{'m_ValueType':1,'valueIndex':3}),(131104,d.px(-4)),(131074,d.enum('flex-start')),(131084,d.num(0)),(131085,d.num(0))])
 for i,a in rr.items():
  a=copy.deepcopy(a);b=copy.deepcopy(d.r[i])
  if i==1034:
   a['data']['m_Classes']=b['data']['m_Classes'];a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
  assert a==b,('unrelated control, binding or hierarchy changed',tag,i)
 d.save();data=env[M].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[M].keys()
 for pid,h in hashes[M].items():
  if pid not in changes[M]:assert sha(saved[pid].get_raw_data())==h
 for pid,t in changes[M].items():assert saved[pid].read_typetree()==t
 outputs[folder/M]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/M).write_bytes(data)
 checks.append({'target':str(folder/M),'template':'OverviewHeader','scoreboard_node':1034,'left':0,'top':-4,'position':'absolute','centering_class_removed':True,'other_controls_and_native_bindings_unchanged':True,'roundtrip':True})
G=M
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('仅将OverviewHeader节点1034记分牌从centre-avoid-centred布局改为父级左对齐，absolute/left0/top-4，取消右侧约束。保留全部赛事记分牌数据、尺寸、模板ID及其他控件。游戏侧栏分支与独立皮肤分别在当前资源上修改，不覆盖侧栏补偿。回读与无关对象核验通过，游戏内实际位置待用户确认。','utf8')"+tail[end:]
exec(compile(tail,'verify-backup-install','exec'))
