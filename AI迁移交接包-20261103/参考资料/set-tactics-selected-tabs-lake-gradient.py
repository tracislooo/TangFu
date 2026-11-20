from pathlib import Path
import subprocess,re
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactics-selected-tabs-lake-gradient-').replace('hours=-4','hours=-7')
exec(compile(s,'backup-current-non-sidebar','exec'))
parsed=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'styles','exec'))
for file,names in [('unify-lake-blue-controls.py',{'append_rule','color'}),('fix-primary-navigation-grey-lake-blue.py',{'selector'})]:
 parsed=ast.parse((R/file).read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='f32' for t in n.targets)],type_ignores=[]),file,'exec'))
S='ui-styles_assets_default.bundle';outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 donor=Doc(W,name='TacticalPlannerTeamShapePitchHeader')
 for name,buttons in [('TacticalPlannerTeamShapePitchHeader',[1023,1025,1027,1045]),('TacticalPlannerTeamInstructionsPitchHeader',[1013,1014])]:
  d=Doc(W,name=name)
  for button in buttons:
   existing=[c['rid'] for c in d.a(button)['m_Children'] if d.a(c['rid']).get('m_FullTypeName')=='SI.Bindable.SIGradient']
   grad=existing[0] if existing else d.add(donor,1061,button,'TacticsLakeBlueSelectedGradient')
   d.a(grad)['m_Classes']=['tf-tactics-selected-gradient'];d.move(grad,button,0)
   d.st(grad,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.px(0)),(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(458767,d.num(0))])
   d.st(grad,[(-1,d.val(4,color('35C6E8')))])
   rule=d.s['m_Rules'][d.a(grad)['m_RuleIndex']];rule['m_Properties'][-1]['m_CustomName']='--start-colour'
   # Separate custom properties share m_Id=-1, so append the second manually.
   rule['m_Properties'].append({'m_Id':-1,'m_CustomName':'--end-colour','m_Line':-1,'m_Values':[d.val(4,color('078BC4'))]})
   # Opacity is selected via stylesheet; an inline zero would override it.
   rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id']!=458767]
  d.save()
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,d in changes[W].items():assert saved[pid].read_typetree()==d
 outputs[folder/W]=data
 path=folder/S;before[path]=path.read_bytes();protected.pop(path,None)
 (OUT/('backup-'+tag)/S).write_bytes(before[path])
 e=UnityPy.load(before[path]);oo={o.path_id:o for o in e.objects};changed={}
 for o in oo.values():
  if o.type.name!='MonoBehaviour' or o.peek_name() not in ['AlwaysAppliedStyleSheet','FigmaGeneratedStyles']:continue
  sh=o.read_typetree()
  append_rule(sh,['.tf-tactics-selected-gradient'],[(458767,0.)])
  append_rule(sh,['.tactics-collapsable-pitch-header-button-group .buttongroup__button--active .tf-tactics-selected-gradient','#TFPitchSwitches .buttongroup__button--active .tf-tactics-selected-gradient'],[(458767,1.)])
  o.save_typetree(sh);changed[o.path_id]=sh
 assert len(changed)==2
 data=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 for pid,o in saved.items():
  if pid in changed:assert o.read_typetree()==changed[pid]
  else:assert o.get_raw_data()==oo[pid].get_raw_data()
 outputs[path]=data
 checks.append({'target':str(folder),'buttons':6,'gradient':['#35C6E8','#078BC4'],'native_gradient':True,'selected_only':True,'roundtrip':True})
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';(OUT/('output-'+tag)).mkdir(exist_ok=True);(OUT/('output-'+tag)/p.name).write_bytes(b)
G=W
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
tail=tail.replace("OUT/('backup-'+tag)/G","OUT/('backup-'+tag)/p.name").replace("OUT/('output-'+tag)/G","OUT/('output-'+tag)/p.name")
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('战术球场模式按钮选中时使用原生SIGradient，湖水蓝#35C6E8至#078BC4，覆盖合并/持球/无球/都包括及球队指令持球/无球。梯度装饰忽略鼠标并置于文本下，复用原选中class，不新增图片或GUID。基于当前非侧栏版分别迁移游戏/皮肤。资源回读通过，游戏内视觉待验收。','utf8')"+tail[end:]
exec(compile(tail,'verify-and-install','exec'))
