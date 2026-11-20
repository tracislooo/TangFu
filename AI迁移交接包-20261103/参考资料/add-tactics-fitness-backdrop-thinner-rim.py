from pathlib import Path
import subprocess
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split("for name in [")[0]
s=s.replace('inspect-fitness-backdrop-','tactics-fitness-backdrop-thinner-rim-').replace('hours=-4','hours=-6')
exec(compile(s,'boot','exec'))
G=W;outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[G]=UnityPy.load(before[folder/G]);objs[G]={o.path_id:o for o in env[G].objects};changes[G]={}
 hashes[G]={i:sha(o.get_raw_data()) for i,o in objs[G].items()}
 for name in ['TacticsPositionCombined','TacticsPositionDetailed']:
  d=Doc(G,name=name);old=copy.deepcopy(d.d);r0=refs(old)
  gate=d.named('PitchFitnessPlayerVisible');frame=d.named('TacticsPlayerPortraitFrame')
  border=next(i for i,a in d.r.items() if 'm_Parent' in a.get('data',{}) and d.data(i).get('name','').endswith('CardNativePositionBackground'))
  donor=d if name.endswith('Combined') else Doc(G,name='TacticsDetailedCardPositionButton')
  btn=1105 if donor is d else 1004
  h=next(p for p in donor.s['m_Rules'][donor.a(btn)['m_RuleIndex']]['m_Properties'] if p['m_Id']==458752)['m_Values'][0]
  color=copy.deepcopy(donor.s['colors'][h['valueIndex']])
  original_children=copy.deepcopy(d.a(gate)['m_Children'])
  plate=d.add(d,frame,gate,'PitchFitnessPercentageBackdrop')
  d.a(gate)['m_Children']=[{'rid':plate}]+original_children
  d.size(plate,28,12)
  d.st(plate,[(131102,d.enum('absolute')),(131089,d.px(-8)),(131104,d.px(36 if name.endswith('Detailed') else 35)),(458752,d.val(4,color)),(262147,d.px(0))])
  d.size(border,73,73)
  d.st(border,[(131089,d.px(1)),(131104,d.px(1)),(262147,d.px(5))])
  # Bindings and every pre-existing node are intact except the gate child list
  # and bottom layer geometry. No changes to percentage state trees or bars.
  for i,a in r0.items():
   b=copy.deepcopy(d.r[i]);a=copy.deepcopy(a)
   if i==border:a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
   if i==gate:a['data']['m_Children']=b['data']['m_Children']
   assert a==b,('unrelated node changed',name,i)
  d.save();checks.append({'target':str(folder/G),'template':name,'fitness_backdrop':[28,12],'backdrop_rgba':color,'bottom_layer':[1,1,73,73],'native_bindings_and_fitness_tree_unchanged':True})
 data=env[G].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[G].keys()
 for pid,h in hashes[G].items():
  if pid not in changes[G]:assert sha(saved[pid].get_raw_data())==h
 for pid,tree in changes[G].items():assert saved[pid].read_typetree()==tree
 outputs[folder/G]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/G).write_bytes(data)
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
tail=tail.replace('Highlight中间信息行调整为温度—球场—主裁判；球场在该信息行中间50%区域，裁判右侧25%区域。裁判姓名使用原生MatchdayInfo_4x4的match.MatchReferee.Name直接文本绑定，关闭内嵌链接、富文本和上下文菜单。游戏/皮肤分别在各自现有Global包上修改，保留差异。未启动游戏，游戏内姓名与布局需实际验收。','Combined和Detailed体能文字下新增28×12px底，颜色逐组件复制位置按钮实际RGBA。背景位于原有球员显隐门控内且忽略鼠标；原体能决策树和进度条不变。最底层位置色板从75×75缩至73×73，x1/y1/圆角5，头像与其他内容尺寸不变，露出色边由4px变约3px。游戏和皮肤分别修改；资源回读和无关对象校验通过，游戏内效果待验收。')
exec(compile(tail,'backup-verify-install','exec'))
