from pathlib import Path
import subprocess,re
s=Path('inspect-fitness-backdrop.py').read_text('utf-8-sig').split('for name in [')[0].replace('inspect-fitness-backdrop-','tactics-role-phase-backgrounds-').replace('hours=-4','hours=-7')
exec(compile(s,'latest-separate-game-skin-backups','exec'))
for file,names in [('combine-tactics-condition-sharpness.py',{'decode','encode'}),('unify-lake-blue-controls.py',{'append_rule','color'}),('fix-primary-navigation-grey-lake-blue.py',{'selector'})]:
 parsed=ast.parse((R/file).read_text('utf-8-sig'));exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.FunctionDef) and n.name in names or isinstance(n,ast.Assign) and any(isinstance(t,ast.Name) and t.id=='f32' for t in n.targets)],type_ignores=[]),file,'exec'))
parsed=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in parsed.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'styles','exec'))
S='ui-styles_assets_default.bundle';outputs={};checks=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 env[W]=UnityPy.load(before[folder/W]);objs[W]={o.path_id:o for o in env[W].objects};changes[W]={};hashes[W]={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
 d=Doc(W,name='TacticsPositionCombined');original=copy.deepcopy(d.d)
 for node,hexcolor in [(1105,'123F32'),(1107,'651D35')]:d.st(node,[(458752,d.val(4,color(hexcolor)))])
 rr=refs(original)
 for i,a in rr.items():
  b=copy.deepcopy(d.r[i]);a=copy.deepcopy(a)
  if i in [1105,1107]:a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
  assert a==b
 d.save()
 # Use the game's proven Boolean -> class function. Its parent receives the
 # class; all native role scopes, tooltip and click handlers remain intact.
 proto=Doc(W,name='TacticalPlannerCollapsablePitchesSingle')
 d=Doc(W,name='TacticsDetailedCardPositionButton');old=copy.deepcopy(d.d);parent=1002;button=1004
 wrapper=d.add(proto,1005,parent,'TacticsRoleCurrentPhaseColour')
 fn=d.data(wrapper)['BindFunction'];args=decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
 assert len(args)==5 and args[0].endswith(b'config.UseFMCTactics')
 for index,oldtext,newtext in [(0,'config.UseFMCTactics','position.IsInPossession'),(1,'tf-tactics-pitch-black-dark-header','tf-role-in-possession'),(2,'tf-tactics-pitch-black','tf-role-out-possession')]:
  b=oldtext.encode();n=newtext.encode();assert args[index].endswith(bytes([len(b)])+b);args[index][-len(b)-1:]=bytes([len(n)])+n
 assert args[3][-1]==0 and args[4][-1]==1
 fn['m_inputs']['m_variable']['m_argumentBytes']=encode(args)
 d.move(button,wrapper)
 d.st(wrapper,[(131105,d.pct(100)),(131087,d.px(12)),(131097,d.px(0)),(131096,d.px(0)),(131085,d.num(0))])
 d.st(button,[(458752,d.val(4,{'r':0.,'g':0.,'b':0.,'a':0.}))])
 rr=refs(old)
 for i,a in rr.items():
  b=copy.deepcopy(d.r[i]);a=copy.deepcopy(a)
  if i==parent:a['data']['m_Children']=b['data']['m_Children']
  if i==button:
   a['data']['m_Parent']=b['data']['m_Parent'];a['data']['m_RuleIndex']=b['data']['m_RuleIndex']
  assert a==b,('original role binding or event changed',i)
 d.save()
 data=env[W].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert saved.keys()==objs[W].keys()
 for pid,h in hashes[W].items():
  if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h
 for pid,t in changes[W].items():assert saved[pid].read_typetree()==t
 outputs[folder/W]=data
 path=folder/S;before[path]=path.read_bytes();protected.pop(path,None);(OUT/('backup-'+tag)/S).write_bytes(before[path])
 e=UnityPy.load(before[path]);oo={o.path_id:o for o in e.objects};hh={i:sha(o.get_raw_data()) for i,o in oo.items()};edited={}
 for o in oo.values():
  if o.type.name!='MonoBehaviour' or o.peek_name() not in ['AlwaysAppliedStyleSheet','FigmaGeneratedStyles']:continue
  sh=o.read_typetree()
  for cls,h in [('tf-role-in-possession','123F32'),('tf-role-out-possession','651D35')]:
   append_rule(sh,['.'+cls+'.'+cls+'.'+cls],[(458752,color(h))])
  o.save_typetree(sh);edited[o.path_id]=sh
 assert len(edited)==2
 data=e.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 for pid,o in saved.items():
  if pid in edited:assert o.read_typetree()==edited[pid]
  else:assert sha(o.get_raw_data())==hh[pid]
 outputs[path]=data;checks.append({'target':tag,'combined_in_possession':'#123F32','combined_out_possession':'#651D35','detailed_live_phase':'position.IsInPossession','native_role_events_and_binding_scopes_preserved':True,'roundtrip':True})
for p,b in outputs.items():
 tag='game' if p.parent==GAME else 'skin';(OUT/('output-'+tag)).mkdir(exist_ok=True);(OUT/('output-'+tag)/p.name).write_bytes(b)
G=W
tail=Path('fix-highlight-stadium-center-referee-right.py').read_text('utf8').split("for p,b in before.items():\n if p.name.startswith('catalog.')")[1]
tail="for p,b in before.items():\n if p.name.startswith('catalog.')"+tail
tail=tail.replace("OUT/('backup-'+tag)/G","OUT/('backup-'+tag)/p.name").replace("OUT/('output-'+tag)/G","OUT/('output-'+tag)/p.name")
start=tail.index("(OUT/'修改说明.md').write_text(");end=tail.index('\nprint(',start)
tail=tail[:start]+"(OUT/'修改说明.md').write_text('球员卡位置按钮：有球墨绿#123F32，无球酒红#651D35。Combined原有两个RoleButton分别设置；Detailed专用位置模板加入原生Boolean样式setter读取position.IsInPossession，为父级添加相应私有类，按钮透明透出父底。原roledata上下文、点击、提示与数据保持。普通/触控Detailed共用此私有模板。游戏和独立皮肤分别迁移，原始无关对象及序列化回读校验通过，游戏内实际显色待验收。','utf8')"+tail[end:]
exec(compile(tail,'verify-backup-install','exec'))
