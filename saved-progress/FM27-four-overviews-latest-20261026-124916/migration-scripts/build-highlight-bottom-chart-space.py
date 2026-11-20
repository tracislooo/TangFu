from pathlib import Path
import json
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-bottom-chart-space-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-installed-resources','exec'))
d=Doc(G,pid=-7710242645031577538)
old=copy.deepcopy(d.d);oldr=refs(old);olds=copy.deepcopy(d.s)
allowed=set();class_changes=set()
AUTO={'m_ValueType':1,'valueIndex':2}
def style(i,props):
 d.st(i,props);allowed.add(i)
def spacing(i):
 style(i,[(p,d.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])
def grow(i):
 style(i,[(131087,d.px(0)),(131082,d.px(0)),(131096,d.px(0)),(131097,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131074,d.enum('stretch'))])
def transparent(i):
 style(i,[(458752,d.val(4,{'r':0.,'g':0.,'b':0.,'a':0.})),(458753,{'m_ValueType':1,'valueIndex':3})])
modules=json.loads((R/'highlight-4x4-75-dividers-transparent-20261024-141806/verification.json').read_text('utf8'))['module_style']
for module in modules:
 title=module['title'];frame=d.a(d.a(title)['m_Parent']['rid'])['m_Parent']['rid'];scroller=d.a(title)['m_Parent']['rid']
 assert d.data(frame)['name']=='title area frame'
 parent=d.a(frame)['m_Parent']['rid']
 # Clear padding along only this module's enclosing chain, not its labels or data.
 i=parent
 while i!=d.a(module['wrapper'])['m_Parent']['rid']:
  spacing(i);i=d.a(i)['m_Parent']['rid']
 for i in [frame,scroller,title]:
  spacing(i)
  style(i,[(131087,d.px(16)),(131082,d.px(16)),(131096,d.px(16)),(131094,d.px(16)),(131085,d.num(0))])
 style(frame,[(131084,d.num(0)),(131073,d.enum('center')),(131088,d.enum('center'))])
 style(title,[(65537,d.px(12)),(65546,d.enum('middle-center'))])
 content=next(c['rid'] for c in d.a(parent)['m_Children'] if d.a(c['rid']).get('m_TemplateAlias')=='states-templates-tile-content')
 spacing(content);grow(content)
 # Every ancestor between plot and content yields spare height to the chart.
 i=module['plot']
 while i!=content:
  spacing(i);grow(i);i=d.a(i)['m_Parent']['rid']
 style(module['plot'],[(131105,d.pct(100))])

# Action-zone shading is on an inner wrapper in both native switch branches.
for i in [3204,3197]:
 assert 'graph_datavis_accent_background' in d.a(i)['m_Classes']
 d.a(i)['m_Classes']=[c for c in d.a(i)['m_Classes'] if c!='graph_datavis_accent_background']
 class_changes.add(i);transparent(i);spacing(i);grow(i)
for i in [3189,3193,3201,3206]:spacing(i);grow(i)
style(3206,[(131105,d.pct(100))])
# Direction captions stay at their native font size and content height.
for i in [3210,3212]:
 spacing(i)
 style(i,[(131087,AUTO),(131082,AUTO),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131074,d.enum('center'))])
for i in [3144,3150,3284,3289]:spacing(i)

for rid,record in oldr.items():
 if rid not in allowed and rid not in class_changes:assert d.r[rid]==record,('Unrelated node changed',rid)
 else:
  expected=copy.deepcopy(record)
  if rid in allowed:expected['data']['m_RuleIndex']=d.r[rid]['data']['m_RuleIndex']
  if rid in class_changes:expected['data']['m_Classes']=d.r[rid]['data']['m_Classes']
  assert d.r[rid]==expected,('Unexpected binding/structure change',rid)
for k,v in olds.items():
 if isinstance(v,list):assert d.s[k][:len(v)]==v
 else:assert d.s[k]==v
assert set(d.r)==set(oldr)
d.save()
output=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[G])
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(check[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,expected in changes[G].items():assert check[pid].read_typetree()==expected,('Serialization mismatch',pid)
validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
(OUT/G).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
report={'title_font_px':12,'title_height_px':16,'title_top_spacing_px':0,'activity_inner_backdrops_transparent':[3204,3197],'activity_graph':'flexible remaining height, full available width; native aspect and painting retained','other_text_and_all_bindings_unchanged':True,'structure_and_unrelated_objects_unchanged':True,'modified_style_nodes':sorted(allowed),'removed_background_class_nodes':sorted(class_changes),'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v.get('m_Name','AssetBundle') for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-match-ui-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
watcher=(R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_text('utf8').replace("'G:/Doc/ChatGPT/New project/install-match-ui-patch.py'","(Join-Path $PSScriptRoot 'installer.py')")
(OUT/'install-after-game-exits.ps1').write_text(watcher,'utf8')
(OUT/'修改说明.md').write_text('仅修改当前 MatchViewer_12x4 内三个下方私有模块。标题12px、行高16px，清除顶部留白；绘图区使用释放的空间。活动区域有/无数据两分支的内衬背景透明，清除球场外围多余间距。方向说明和其他文字字号、球场绘制参数、实时绑定、所有外层布局与数据比较区均保持原样。序列化回读和无关节点/资产一致性通过；未进行游戏内渲染验证。restore.ps1 回退本次修改。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'title_px':12,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
