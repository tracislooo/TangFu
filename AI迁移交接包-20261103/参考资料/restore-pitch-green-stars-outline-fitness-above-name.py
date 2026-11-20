from pathlib import Path
import subprocess,re
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactics-green-star-outline-fitness-above-name-').replace('hours=-4','hours=-7')
exec(compile(s,'backup-current-separate-branches','exec'))
for file,names in [('unify-lake-blue-controls.py',{'append_rule','color'}),('fix-primary-navigation-grey-lake-blue.py',{'selector'})]:
 parsed=ast.parse((R/file).read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='f32' for t in n.targets)],type_ignores=[]),file,'exec'))
parsed=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'styles','exec'))
S='ui-styles_assets_default.bundle';outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 for name in ['TacticsPositionCombined','TacticsPositionDetailed']:
  d=Doc(W,name=name);old=copy.deepcopy(d.d);count=0
  for i,a in list(d.r.items()):
   if 'm_Parent' not in a.get('data',{}):continue
   nm=d.data(i).get('name','')
   if 'CardFitnessFill' in nm or nm.endswith('CardFitnessTrack'):
    d.st(i,[(131104,d.px(57))]);count+=1
  assert count>=103
  d.save();checks.append({'target':tag,'template':name,'fitness_bar_y':57,'bar_bottom_equals_name_top':60,'progress_nodes':count})
 for name in ['TacticsPositionCombined','TacticsDetailedCardDetailsDesktop','TacticsDetailedCardDetailsTouch']:
  obj=find(W,name);doc=changes[W].get(obj.path_id)
  sheet=changes[W].get(doc['inlineSheet']['m_PathID']) if doc else None
  d=Doc(W,name=name,tree=doc,style=sheet)
  leaves=[i for i,a in d.r.items() if a.get('data',{}).get('m_FullTypeName')=='FM.UI.FMStarRatingTemp' or a.get('data',{}).get('m_TemplateAlias')=='stats-star-ratings']
  assert leaves
  for leaf in leaves:
   parent=d.a(leaf)['m_Parent']['rid'];original_rule=d.a(leaf)['m_RuleIndex']
   props=copy.deepcopy(d.s['m_Rules'][original_rule]['m_Properties']) if original_rule>=0 else []
   def pxval(key):
    p=next((p for p in props if p['m_Id']==key),None)
    if not p:return 0
    h=p['m_Values'][0]
    return d.s['dimensions'][h['valueIndex']]['value'] if h['m_ValueType']==3 else 0
   x,y=pxval(131089),pxval(131104)
   for n,(dx,dy) in enumerate([(-.6,0),(.6,0),(0,-.6),(0,.6),(-.45,-.45),(.45,-.45),(-.45,.45),(.45,.45)]):
    shadow=d.add(d,leaf,parent,'TacticsStarOutline'+str(leaf)+'_'+str(n));d.a(shadow)['m_RuleIndex']=original_rule
    d.a(shadow)['m_Classes']=copy.deepcopy(d.a(leaf).get('m_Classes',[]))+['tf-tactics-star-outline']
    d.st(shadow,[(131102,d.enum('absolute')),(131089,d.px(x+dx)),(131104,d.px(y+dy)),(458768,d.enum('visible'))])
    d.move(shadow,parent,d.a(parent)['m_Children'].index({'rid':leaf}))
  for dim in d.s['dimensions']:dim['value']=f32(dim['value'])
  d.save();checks.append({'target':tag,'template':name,'native_rating_outlines':len(leaves),'outline_uses_same_live_bindings':True})
 for name in ['TacticalPlannerCollapsablePitchesSingle','TacticalPlannerPhasesPitches']:
  d=Doc(W,name=name);n=0
  for i,a in list(d.r.items()):
   if any(k in a.get('data',{}).get('m_FullTypeName','') for k in ['FMTacticsPanel','FMTacticsWithAnalysis','FMTacticsWithPhases']):
    ri=d.a(i)['m_RuleIndex'];rule=copy.deepcopy(d.s['m_Rules'][ri]);rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id'] not in [458752,458753]]
    rule['m_ComplexSelectors']=[];d.s['m_Rules'].append(rule);d.a(i)['m_RuleIndex']=len(d.s['m_Rules'])-1;n+=1
  assert n==(5 if 'Single' in name else 1)
  d.save();checks.append({'target':tag,'template':name,'native_grass_background_restored':n})
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,doc in changes[W].items():assert saved[pid].read_typetree()==doc
 outputs[folder/W]=data
 path=folder/S;before[path]=path.read_bytes();protected.pop(path,None);(OUT/('backup-'+tag)/S).write_bytes(before[path])
 e=UnityPy.load(before[path]);oo={o.path_id:o for o in e.objects};hh={i:sha(o.get_raw_data()) for i,o in oo.items()};edited={}
 for o in oo.values():
  if o.type.name!='MonoBehaviour' or o.peek_name() not in ['AlwaysAppliedStyleSheet','FigmaGeneratedStyles']:continue
  sh=o.read_typetree()
  root='.tf-tactics-star-outline.tf-tactics-star-outline.tf-tactics-star-outline.tf-tactics-star-outline'
  append_rule(sh,[root,root+' *'],[(196610,color('101010')),(65536,color('101010'))])
  o.save_typetree(sh);edited[o.path_id]=sh
 assert len(edited)==2
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
tail=tail[:start]+"(OUT/'修改说明.md').write_text('六个战术球场渲染器移除透明/图片行内覆盖，恢复原生草坪底色类；上下工具栏底色保持当前。Combined/Detailed体能横条y78改y57，3px高，紧贴y60姓名上沿，所有重复状态填充与轨道同步。Combined与Detailed普通/触控星级以同绑定原生星级绘制偏移黑色底层作为星形细描边，透明背景，不生成图片/GUID。游戏侧栏分支与独立皮肤分别迁移，原始资源对象逐项校验，无关对象字节不变。游戏内视觉和交互待验收。','utf8')"+tail[end:]
exec(compile(tail,'verify-backup-install','exec'))
