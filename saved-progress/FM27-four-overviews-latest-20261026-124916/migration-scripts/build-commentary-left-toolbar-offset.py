from pathlib import Path
import json
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','commentary-left-toolbar-minus20-').replace('NAMES=[W,G,M,F]','NAMES=[M]')
exec(compile(boot,'backup-current-match-resource','exec'))
audits=[]
for name in ['MatchCommentaryBar','SquadOverview']:
 d=Doc(M,name=name);old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
 if name=='MatchCommentaryBar':
  assert d.data(1006)['name']=='CommentaryBar'
  assert d.a(1008)['m_FullTypeName']=='SI.Bindable.SIText'
  d.st(1006,[(131073,d.enum('stretch'))])
  d.st(1008,[(65546,d.enum('middle-left')),(131074,d.enum('stretch'))])
  allowed={1006,1008}
 else:
  host=d.named('MatchBottomTacticalToolbar')
  rules=d.s['m_Rules'][d.a(host)['m_RuleIndex']]['m_Properties']
  for key in [131089,131103]:
   p=next(p for p in rules if p['m_Id']==key)
   assert [d.s['dimensions'][h['valueIndex']] for h in p['m_Values']]==[{'unit':1,'value':0.0}]
  d.st(host,[(131089,d.px(-20)),(131103,d.px(20))])
  allowed={host}
 for rid,record in oldr.items():
  if rid not in allowed:assert d.r[rid]==record,('Unrelated node changed',name,rid)
  else:
   expected=copy.deepcopy(record);expected['data']['m_RuleIndex']=d.a(rid)['m_RuleIndex']
   assert d.r[rid]==expected,('Binding or structure changed',name,rid)
 for k,v in olds.items():
  if isinstance(v,list):assert d.s[k][:len(v)]==v
  else:assert d.s[k]==v
 assert set(d.r)==set(oldr)
 d.save();audits.append({'template':name,'modified_style_nodes':sorted(allowed),'all_bindings_structure_classes_unchanged':True})
data=env[M].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
assert set(saved)==set(objs[M])
for pid,h in hashes[M].items():
 if pid not in changes[M]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,tree in changes[M].items():assert saved[pid].read_typetree()==tree,('Serialization mismatch',pid)
for d in documents:validate_ui(saved[d.obj.path_id].read_typetree(),saved[d.sid].read_typetree())
(OUT/M).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
report={'commentary_alignment':'middle-left','existing_commentary_padding_size_color_preserved':True,'toolbar_translation_px':-20,'toolbar_offsets_px':{'left':-20,'right':20},'toolbar_width_height_buttons_substitutes_unchanged':True,'audits':audits,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{M:{str(pid):tree.get('m_Name','') for pid,tree in changes[M].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{M:sha(data)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[M],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-match-ui-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
watcher=(R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_text('utf8').replace("'G:/Doc/ChatGPT/New project/install-match-ui-patch.py'","(Join-Path $PSScriptRoot 'installer.py')")
(OUT/'install-after-game-exits.ps1').write_text(watcher,'utf8')
(OUT/'修改说明.md').write_text('MatchCommentaryBar：文字纵向居中、水平左对齐，保留现有文字内边距、字号、颜色以及解说条背景和尺寸。SquadOverview/MatchBottomTacticalToolbar：left= -20px、right=20px，整体左移20px，宽度及高度不变。按钮、菜单、球员与替补区域、Highlight内容和全部绑定结构均不变。已通过序列化回读及无关对象一致性检查；尚未在游戏中验证显示或点击。restore.ps1仅回退本次修改。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'serialization_roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
