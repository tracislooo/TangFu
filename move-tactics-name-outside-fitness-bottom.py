from pathlib import Path
import subprocess
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactics-name-outside-fitness-bottom-').replace('hours=-4','hours=-7')
exec(compile(s,'backup-current','exec'))
outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 for name,node in [('TacticsPositionCombined',1037),('TacticsPositionDetailed',None),('TacticsDetailedCardDetailsDesktop',1016),('TacticsDetailedCardDetailsTouch',1061)]:
  d=Doc(W,name=name);old=copy.deepcopy(d.d);allowed=set();bars=0
  def val(i,k):
   p=next(p for p in d.s['m_Rules'][d.a(i)['m_RuleIndex']]['m_Properties'] if p['m_Id']==k)
   h=p['m_Values'][0];return d.s[poolmap[h['m_ValueType']]][h['valueIndex']]
  if node is not None:
   assert val(node,131104)['value']==60,(name,'unexpected name baseline')
   d.st(node,[(131104,d.px(73))]);allowed.add(node)
  for i,a in list(d.r.items()):
   if 'm_Parent' not in a.get('data',{}):continue
   nm=d.data(i).get('name','')
   if 'CardFitnessFill' in nm or nm.endswith('CardFitnessTrack'):
    assert val(i,131104)['value']==57
    d.st(i,[(131104,d.px(68))]);allowed.add(i);bars+=1
  if name in ['TacticsPositionCombined','TacticsPositionDetailed']:assert bars>=103
  for i,a in refs(old).items():
   b=copy.deepcopy(d.r[i]);a=copy.deepcopy(a)
   if i in allowed:a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
   assert a==b,('unexpected control or binding change',name,i)
  d.save();checks.append({'target':tag,'template':name,'name_top':73 if node else None,'bar_top':68 if bars else None,'bar_nodes':bars,'bindings_preserved':True})
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 outputs[folder/W]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/W).write_bytes(data)
G=W
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('战术Combined及Detailed桌面/触控姓名区域y60→73，框底y71以下留2px；体能轨道与全部百分比填充y57→68，高3px，贴框底且位于姓名上方。仅改现有样式top，保留字号、宽度、三栏缩放、头像、百分比文字和全部绑定。游戏与独立皮肤分别增量修改，回读及其他对象字节校验通过，游戏内显示未验证。','utf8')"+tail[end:]
# Validate all rollback targets before restoring any file.
needle="for p in outputs:\n tag='game' if p.parent==GAME else 'skin'\n install.append"
replacement="for p in outputs:\n restore.append(\"if ((Get-FileHash -LiteralPath '\"+str(p)+\"').Hash.ToLower() -ne '\"+sha(outputs[p])+\"') { throw 'Target changed after this patch; merge rollback required.' }\")\n"+needle
assert needle in tail;tail=tail.replace(needle,replacement)
exec(compile(tail,'verify-install','exec'))
(R/'current-tactics-card-layout.json').write_text(json.dumps({'patch':str(OUT),'installed':manifest['installed'],'runtime_verified':False,'name_top':73,'fitness_top':68,'manifest':str(OUT/'manifest.json')},ensure_ascii=False,indent=2),'utf8')
