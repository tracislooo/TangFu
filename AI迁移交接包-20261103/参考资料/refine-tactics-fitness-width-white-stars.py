from pathlib import Path
import subprocess
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactics-fitness67-backdrop24-white-stars-').replace('hours=-4','hours=-7')
exec(compile(s,'current-branch-backups','exec'))
S='ui-styles_assets_default.bundle';outputs={};checks=[]
def f32(v):return struct.unpack('<f',struct.pack('<f',v))[0]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 for name in ['TacticsPositionCombined','TacticsPositionDetailed']:
  d=Doc(W,name=name);old=copy.deepcopy(d.d);r0=refs(old);allowed=set();fills=0;tracks=0;plates=0
  for i,a in list(d.r.items()):
   if 'm_Parent' not in a.get('data',{}):continue
   nm=d.data(i).get('name','')
   if nm.endswith('CardFitnessTrack'):
    d.st(i,[(131089,d.px(4)),(131105,d.px(67))]);tracks+=1
   elif 'CardFitnessFill' in nm:
    suffix=nm.split('CardFitnessFill',1)[1];pct=0 if suffix=='None' else int(suffix)
    parent=d.a(i)['m_Parent']['rid']
    # Percentage leaves are shifted left 12px; offset their fill back to x4.
    x=16 if d.data(parent).get('name','').startswith('PitchFitnessPercent') else 4
    d.st(i,[(131089,d.px(x)),(131105,d.px(f32(pct*.67)))]);fills+=1
   elif nm=='PitchFitnessPercentageBackdrop':
    d.st(i,[(131105,d.px(24)),(131097,d.px(24)),(131095,d.px(24))]);plates+=1
   else:continue
   allowed.add(i)
  assert tracks>=1 and fills>=102 and plates==1
  for i,a in r0.items():
   b=copy.deepcopy(d.r[i]);a=copy.deepcopy(a)
   if i in allowed:a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
   assert a==b,('unrelated binding or node changed',name,i)
  d.save();checks.append({'target':tag,'template':name,'bar_width':67,'bar_x':4,'backdrop_width':24,'fills':fills,'tracks':tracks,'all_bindings_preserved':True})
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 outputs[folder/W]=data
 path=folder/S;before[path]=path.read_bytes();protected.pop(path,None);(OUT/('backup-'+tag)/S).write_bytes(before[path])
 e=UnityPy.load(before[path]);oo={o.path_id:o for o in e.objects};hh={i:sha(o.get_raw_data()) for i,o in oo.items()};edited={};rules=0
 for o in oo.values():
  if o.type.name!='MonoBehaviour':continue
  d=o.read_typetree();hits=0
  for rule in d.get('m_Rules',[]):
   if not any(p['m_Value']=='tf-tactics-star-outline' for sel in rule['m_ComplexSelectors'] for s in sel['m_Selectors'] for p in s['m_Parts']):continue
   for prop in rule['m_Properties']:
    if prop['m_Id'] in [196610,65536]:
     d['colors'].append({'r':1.,'g':1.,'b':1.,'a':1.});prop['m_Values']=[{'m_ValueType':4,'valueIndex':len(d['colors'])-1}]
   hits+=1
  if hits:o.save_typetree(d);edited[o.path_id]=d;rules+=hits
 assert len(edited)==2 and rules==2
 data=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 for pid,o in saved.items():
  if pid in edited:assert o.read_typetree()==edited[pid]
  else:assert sha(o.get_raw_data())==hh[pid]
 outputs[path]=data
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';(OUT/('output-'+tag)).mkdir(exist_ok=True);(OUT/('output-'+tag)/p.name).write_bytes(b)
G=W
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
tail=tail.replace("OUT/('backup-'+tag)/G","OUT/('backup-'+tag)/p.name").replace("OUT/('output-'+tag)/G","OUT/('output-'+tag)/p.name")
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('Combined和Detailed体能轨道宽67px/x4，与头像对齐；所有百分比填充按67px重新计算并补偿文字父级偏移，y57保持紧贴姓名。百分比黑底28→24px适配100%。仅战术专用星形描边样式改为纯白。游戏侧栏分支和原皮肤分别处理；保留绑定、图片和目录，资源回读与无关对象校验通过，游戏内视觉待验收。','utf8')"+tail[end:]
exec(compile(tail,'verify-backup-install','exec'))
