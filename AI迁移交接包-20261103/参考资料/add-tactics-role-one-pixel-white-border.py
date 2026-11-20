from pathlib import Path
import subprocess
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactics-role-white-border1-').replace('hours=-4','hours=-7')
exec(compile(s,'backup-current-game-skin','exec'))
outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 for name,nodes in [('TacticsPositionCombined',[1105,1107]),('TacticsDetailedCardPositionButton',[1004])]:
  d=Doc(W,name=name);old=copy.deepcopy(d.d)
  for node in nodes:
   props=[(k,d.px(1)) for k in [131076,131077,131078,131079]]+[(k,d.val(4,{'r':1.,'g':1.,'b':1.,'a':1.})) for k in [458758,458761,458762,458763]]
   d.st(node,props)
  for i,a in refs(old).items():
   b=copy.deepcopy(d.r[i]);a=copy.deepcopy(a)
   if i in nodes:a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
   assert a==b,('unrelated control or binding changed',i)
  d.save();checks.append({'target':tag,'template':name,'buttons':nodes,'white_border_width':1,'all_other_geometry_colors_and_bindings_preserved':True})
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 outputs[folder/W]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/W).write_bytes(data)
G=W
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('Combined两组位置按钮及Detailed普通/触控共用私有位置按钮增加四边1px纯白描边，保留有球墨绿/无球酒红背景及原点击、提示、绑定、尺寸。资源回读和无关对象检查通过；游戏运行时只准备补丁，退出后执行install.ps1。','utf8')"+tail[end:]
exec(compile(tail,'verify-backup-install','exec'))
