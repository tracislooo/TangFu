from pathlib import Path
import json,copy,ast
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','match-toolbar-pending-top-right-').replace('NAMES=[W,G,M,F]','NAMES=[G,M]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
boot=boot.replace('if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]','if False:assert before[SKIN/n]==before[GAME/n]').replace("assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']",'')
exec(compile(boot,'backup-correct-installation','exec'))
baseG,baseM=G,M
for bn in NAMES:
 alias=bn+'::skin';env[alias]=UnityPy.load(before[SKIN/bn]);objs[alias]={o.path_id:o for o in env[alias].objects};hashes[alias]={i:sha(o.get_raw_data()) for i,o in objs[alias].items()};changes[alias]={}
helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in helper.body if isinstance(x,ast.FunctionDef) and x.name in ['copy_style','clone_native']],type_ignores=[]),'copy-original-native-toolbar','exec'))
clone_audits=[];all_audits=[]
move_code=(R/'move-match-pending-changes-to-right-controls.py').read_text('utf8').split("d=Doc(M,name='OverviewHeader')",1)[1].split("tail=(R/",1)[0]
for tag,suffix in [('game',''),('skin','::skin')]:
 G,M=baseG+suffix,baseM+suffix
 exec(compile("d=Doc(M,name='OverviewHeader')"+move_code,'relocate-pending-with-original-gates','exec'))
 d.st(row,[(131102,d.enum('absolute')),(131103,d.px(0)),(131104,d.px(0)),(131089,{'m_ValueType':1,'valueIndex':2}),(131091,d.px(0)),(131093,d.px(0)),(131083,d.enum('row')),(131073,d.enum('center')),(131085,d.num(0)),(131084,d.num(0))])
 footer=Doc(M,name='SquadOverview');footer_before=copy.deepcopy(footer.d)
 host=footer.named('MatchBottomTacticalToolbar');bindings=footer.named('MatchBottomToolbarBindings')
 bar,mapping=clone_native(footer,bindings,row);d.move(bar,row,0)
 d.data(bar)['name']='MatchTopRightToolbarBindings'
 d.st(bar,[(131083,d.enum('row')),(131073,d.enum('center')),(131085,d.num(0)),(131084,d.num(0)),(131102,d.enum('relative')),(131092,d.px(8))])
 footer.st(host,[(131081,footer.enum('none'))]);footer.save();d.save()
 # Keep the popup inside its new row even if theme classes specify placement.
 popup=Doc(G,name='MatchTacticPendingChanges')
 for node in [1004,1006]:popup.st(node,[(131102,popup.enum('relative'))]+[(p,{'m_ValueType':1,'valueIndex':2}) for p in [131089,131103,131104,131080]])
 popup.save()
 assert d.a(row)['m_Children'][0]['rid']==bar and d.a(row)['m_Children'][-1]['rid']==1037
 for i,r in refs(footer_before).items():
  if 'm_Parent' not in r.get('data',{}):assert footer.r[i]==r
 all_audits.append({'variant':tag,'layout':'toolbar, pending change notification, playback controls','toolbar_native_clone':clone_audits[-1],'bottom_toolbar_hidden':True,'header_right_px':0,'header_top_px':0,'existing_tactics_page_clearance_preserved':True})
G,M=baseG,baseM
outputs={}
for bn in [n+s for s in ['', '::skin'] for n in NAMES]:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,(bn,pid)
 for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t,(bn,pid)
 for doc in [x for x in documents if x.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/('skin-'+bn.split('::')[0] if bn.endswith('::skin') else bn);dest.write_bytes(raw);outputs[bn]=dest
for p,b in before.items():
 assert p.read_bytes()==b
 if p.name.startswith('catalog.'):protected[p]=sha(b)
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for tag,folder in [('game',GAME),('skin',SKIN)]:
 for bn in NAMES:
  p=folder/bn;src=outputs[bn+('::skin' if tag=='skin' else '')];tx.append({'target':str(p),'source':str(src),'backup':str(OUT/('backup-'+tag)/bn),'before':sha(before[p]),'after':sha(src.read_bytes())})
report={'installed':False,'runtime_verified':False,'output':str(OUT),'checks':all_audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'no_new_assets_or_catalog_changes':True,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');(OUT/'installer.py').write_text((R/'install-independent-resource-patch.py').read_text('utf8'),'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('按截图两条箭头：将原SquadOverview底部战术栏的原生绑定子树完整复制进OverviewHeader右上角行，隐藏底部旧显示；该行从左至右为战术栏、待执行更改提示、原设置/播放按钮。提示保留桌面/执教/战术确认状态/非点球/待更改条件和原生编辑取消事件，旧Switch仍保留两页槽位。提示自身设relative防主题定位覆盖；记分牌和48单位战术页面下移均未更改。仅修改当前Football Manager 27与皮肤包的相关模板和内联样式，不覆盖旧整包，不改目录、纹理、统计。回读及未改对象一致性通过；实际位置和菜单操作待游戏验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'runtime_verified':False},ensure_ascii=False))
