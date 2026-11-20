from pathlib import Path
import subprocess,re
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactics-five-stop-fatigue-percent-').replace('hours=-4','hours=-7')
exec(compile(s,'backup-latest-game-and-skin','exec'))
outputs={};checks=[]
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
stops=['43D65A','3498FF','F2D63C','F39A32','E84848']
rgb=[tuple(int(h[i:i+2],16)/255 for i in [0,2,4]) for h in stops]
def gradient(t):
 t=max(0.,min(1.,t))*4;i=min(3,int(t));a=t-i
 return dict(zip(['r','g','b','a'],[f32(rgb[i][k]*(1-a)+rgb[i+1][k]*a) for k in range(3)]+[1.]))
def fatigue(v):return gradient(abs(v)/500)
def percent(v):return gradient((100-v)/100)
for v in [0,1,44,125,250,375,499,500,501,1000]:assert fatigue(v)==fatigue(-v)
assert fatigue(-500)==fatigue(500)==fatigue(1000)==gradient(1)
assert fatigue(0)==percent(100)==gradient(0)
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()};expected_colors={}
 targets=[o.path_id for o in objs[W].values() if o.type.name=='MonoBehaviour' and any(x in o.get_raw_data() for x in [b'FatigueRawColour',b'CombinedConditionPercent',b'PitchFitnessPercent'])]
 assert len(targets)>=6
 for pid in targets:
  d=Doc(W,pid=pid);old=copy.deepcopy(d.d);rr=refs(old);allowed=set();counts={'fatigue':0,'percentage':0,'bar':0}
  for i,a in list(d.r.items()):
   if 'm_Parent' not in a.get('data',{}):continue
   name=d.data(i).get('name','');color=None;prop=65536
   m=re.fullmatch(r'FatigueRawColour(-?\d+)',name)
   if m:color=fatigue(int(m[1]));counts['fatigue']+=1
   else:
    m=re.fullmatch(r'(?:Combined(?:Condition|Sharpness)Percent|PitchFitnessPercent)(\d+)',name)
    if m:color=percent(int(m[1]));counts['percentage']+=1
    else:
     m=re.fullmatch(r'(?:Combined|Detailed)CardFitnessFill(\d+)',name)
     if m:color=percent(int(m[1]));prop=458752;counts['bar']+=1
   if color is None:continue
   d.st(i,[(prop,d.val(4,color))]);allowed.add(i);expected_colors[(pid,i,prop)]=color
  assert allowed
  for i,a in rr.items():
   a=copy.deepcopy(a);b=copy.deepcopy(d.r[i])
   if i in allowed:a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
   assert a==b,('binding, data or geometry changed',pid,i)
  d.save();checks.append({'target':tag,'template':d.d['m_Name'],'pid':pid,'counts':counts,'all_bindings_geometry_and_missing_values_preserved':True})
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 loaded={}
 for (pid,i,prop),color in expected_colors.items():
  if pid not in loaded:
   d=saved[pid].read_typetree();loaded[pid]=(refs(d),saved[d['inlineSheet']['m_PathID']].read_typetree())
  r,sh=loaded[pid];rule=sh['m_Rules'][r[i]['data']['m_RuleIndex']];h=next(p for p in rule['m_Properties'] if p['m_Id']==prop)['m_Values'][0]
  assert sh['colors'][h['valueIndex']]==color
 outputs[folder/W]=data;(OUT/('output-'+tag)).mkdir();(OUT/('output-'+tag)/W).write_bytes(data)
G=W
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('疲劳数字按abs(v)/500：0绿色、125蓝色、250黄色、375橙色、500及更大红色；负值完全对称，-500红色，范围外饱和。体能/比赛状态百分比数字与球场体能横条按100绿、75蓝、50黄、25橙、0红连续线性渐变；保留原始值、决策树、缺失灰色、布局及排序。覆盖普通及比赛共用的两份疲劳/百分比模板和两种球场卡片；不改背景图片、原生圆环纹理或界面底色。逐项回读颜色、原绑定和无关对象核验通过，游戏内视觉待验收。','utf8')"+tail[end:]
exec(compile(tail,'verify-backup-install','exec'))
