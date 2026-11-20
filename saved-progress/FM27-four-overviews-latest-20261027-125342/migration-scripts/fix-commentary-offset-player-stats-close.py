from pathlib import Path
import json,ast
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','commentary-right20-player-stats-close-').replace('NAMES=[W,G,M,F]','NAMES=[W,G,M]')
exec(compile(boot,'backup-installed-resources','exec'))
main=Doc(G,name='MatchViewer_12x4');asset_clones=[];new_guids={}
source=(R/'build-highlight-five-column-native-player-lists.py').read_text('utf8');helper=ast.parse(source)
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['register_clone','clone_doc','allptr']],type_ignores=[]),'private-native-template-helpers','exec'))
tool=Doc(G,name='FigmaBaseToolTemplate');titlebar=Doc(G,name='CardTitleBar')
d,guid=clone_doc(tool,'PlayerStatsToolWithPersistentClose',-981025000002200)
clone_audits=[]
helpers=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helpers.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native']],type_ignores=[]),'preserve-close-button-native-overrides','exec'))
oldtool=copy.deepcopy(d.d);tr=refs(oldtool)
def visible(source_id,parent,name):return d.add(tool,source_id,parent,name)
desktop=visible(1025,1012,'PlayerStatsCloseDesktop')
fullscreen=visible(1019,desktop,'PlayerStatsCloseFullscreen')
windowed=visible(1020,desktop,'PlayerStatsCloseWindowed')
missing=visible(1025,windowed,'PlayerStatsCloseMissingHeader')
v=d.data(missing);v['Binding']['m_direct']['Path']['m_path']='game.ShowReportToolSiteHeader'
v.update(InvertDirectBinding=1,InvertDirectBinding_UxmlAttributeFlags=1)
assert d.data(desktop)['Binding']['m_direct']['Path']['m_path']=='config.ShowPhonePanels' and d.data(desktop)['InvertDirectBinding']==1
assert d.data(fullscreen)['Binding']['m_direct']['Path']['m_path']=='isfullscreen' and d.data(fullscreen)['InvertDirectBinding']==0
assert d.data(windowed)['Binding']['m_direct']['Path']['m_path']=='isfullscreen' and d.data(windowed)['InvertDirectBinding']==1
d.st(1012,[(131102,d.enum('relative'))])
d.st(desktop,[(131102,d.enum('absolute')),(131103,d.px(16)),(131104,d.px(8)),(131105,d.px(24)),(131087,d.px(24)),(131097,d.px(24)),(131096,d.px(24)),(131095,d.px(24)),(131094,d.px(24)),(131084,d.num(0)),(131085,d.num(0))])
close_roots=[]
for host in [fullscreen,windowed,missing]:d.size(host,24,24)
for host in [fullscreen,missing]:
 root,mapping=clone_native(titlebar,1041,host);close_roots.append(root)
 assert d.a(root)['m_TemplateAlias']==titlebar.a(1041)['m_TemplateAlias']=='buttons-controls-close-default'
 d.size(root,24,24)
 d.st(root,[(p,d.px(0)) for p in [131090,131091,131092,131093]])
# Keep the header in its own non-shrinking band while the table can shrink/scroll.
d.st(1015,[(131105,d.pct(100)),(131097,d.px(0)),(131085,d.num(0))])
d.st(1016,[(131097,d.px(0)),(131096,d.px(0)),(131085,d.num(1))])
allowed={1012,1015,1016}
for rid,record in tr.items():
 expected=copy.deepcopy(record)
 if rid in allowed:
  expected['data']['m_RuleIndex']=d.a(rid)['m_RuleIndex']
  if rid==1012:expected['data']['m_Children']=d.a(rid)['m_Children']
 assert d.r[rid]==expected,('Existing report behavior changed',rid)
d.save()
card=Doc(W,name='PlayerStatsCard');original_card=copy.deepcopy(card.d)
using=next(u for u in card.d['m_Usings'] if u['alias']=='FigmaBaseToolTemplate');using['path']=guid
expected=copy.deepcopy(original_card);next(u for u in expected['m_Usings'] if u['alias']=='FigmaBaseToolTemplate')['path']=guid
assert card.d==expected
card.save()
comment=Doc(M,name='MatchCommentaryBar');original_comment=copy.deepcopy(comment.d);cr=refs(original_comment)
comment.st(1004,[(131102,comment.enum('relative')),(131089,comment.px(20))])
for rid,record in cr.items():
 expected=copy.deepcopy(record)
 if rid==1004:expected['data']['m_RuleIndex']=comment.a(rid)['m_RuleIndex']
 assert comment.r[rid]==expected
comment.save()
meta_code=source.split('for bundle in NAMES:\n metaobj=',1)[1].split('spec=importlib.util',1)[0]
exec(compile('for bundle in [G]:\n metaobj='+meta_code,'register-private-report-template','exec'))
catalog_code=source.split("spec=importlib.util.spec_from_file_location('five_column_catalog'",1)[1].split('outputs={}\n',1)[0]
exec(compile("spec=importlib.util.spec_from_file_location('five_column_catalog'"+catalog_code,'extend-catalog-preserving-existing-locations','exec'))
outputs={}
for bundle in NAMES:
 data=env[bundle].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 assert set(saved)==set(objs[bundle])
 for pid,h in hashes[bundle].items():
  if pid not in changes[bundle]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',bundle,pid)
 for pid,tree in changes[bundle].items():assert saved[pid].read_typetree()==tree,('Serialization mismatch',bundle,pid)
 for doc in [doc for doc in documents if doc.n==bundle]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 if bundle==G:
  for pid in [main.obj.path_id,main.sid,tool.obj.path_id,tool.sid,titlebar.obj.path_id,titlebar.sid,-981025000002000,-981025000002100]:assert sha(saved[pid].get_raw_data())==hashes[G][pid]
 outputs[bundle]=data
outputs['catalog.bin']=catalog;outputs['catalog.hash']=hashlib.md5(catalog).hexdigest().encode('ascii')
for name,data in outputs.items():(OUT/name).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
visibility=[]
for phone in [False,True]:
 for fs in [False,True]:
  for header in [False,True]:
   fallback=not phone and (fs or not header);existing=not phone and not fs and header
   assert int(fallback)+int(existing)==int(not phone)
   visibility.append({'phone':phone,'fullscreen':fs,'native_tool_header_shown':header,'fallback_close':fallback,'original_close':existing})
report={'commentary_translation_px':20,'commentary_width_75_and_centered_text_unchanged':True,'private_player_stats_tool':d.d['m_Name'],'private_guid':guid,'native_close_template':d.a(close_roots[0])['m_TemplateAlias'],'fallback_size_px':[24,24],'fallback_anchor':{'right_px':16,'top_px':8},'fallback_visibility_truth_table':visibility,'native_close_event_template_preserved':True,'normal_and_phone_headers_preserved':True,'shared_templates_tables_factories_and_grid_cache_unchanged':True,'serialization_roundtrip':True,'unrelated_objects_and_catalog_locations_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):tree.get('m_Name','') for pid,tree in ps.items()} for n,ps in changes.items()},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-match-ui-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('解说可见容器保持75%宽与文字居中，relative left=20px，整体右移20px。球员数据详情原FigmaBaseToolTemplate在isfullscreen分支使用无关闭控件的全屏标题栏；普通标题栏还受game.ShowReportToolSiteHeader限制。本补丁仅让PlayerStatsCard桌面分支引用私有工具模板：在全屏或普通工具标题栏隐藏时提供原生close-button补位控件，固定窗口右上角24x24，原关闭行为不改；普通标题栏已有关闭按钮时不重复显示，手机页保持原样。标题带不随表格收缩，数据区允许收缩。共用模板、表格、工厂、Highlight网格和缓存均不改。序列化回读、关闭按钮显示真值表、无关对象/目录一致性检查通过；未进行游戏内调整大小与点击验证。restore.ps1回退本次修改。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'commentary_right_px':20,'private_report_close_fallback':True,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
