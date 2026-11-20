from pathlib import Path
import json

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-blank-data-halves-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-current-template-and-load-codecs','exec'))

d=Doc(G,name='MatchViewer_12x4')
old=copy.deepcopy(d.d);old_style=copy.deepcopy(d.s);old_refs=refs(old)
assert d.a(1006)['m_Children']==[{'rid':1008},{'rid':1009}]
assert d.data(1013)['SelectionValueBinding']['m_path']=='SelectedTab'
assert d.data(1011)['Binding']['m_direct']['Path']['m_path']=='SelectedTab'

upper=d.add(d,1015,1006,'HighlightUpperBlankHalf')
lower=d.add(d,1015,1006,'HighlightLowerDataHalf')
d.a(upper)['m_Classes']=copy.deepcopy(d.a(1008)['m_Classes'])
d.a(lower)['m_Classes']=[]
for i,top in [(upper,0),(lower,50)]:
 d.st(i,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.pct(top)),(131105,d.pct(100)),(131087,d.pct(50)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0))])

d.move(1008,lower)
d.move(1009,lower)
for i in [1001,1002,1004,1006]:
 d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
d.st(1006,[(131102,d.enum('relative'))])
d.st(1008,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131101,d.px(36))])
d.st(1009,[(131102,d.enum('absolute')),(131104,d.px(4)),(131103,d.px(4))])
d.st(1011,[(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
for i in [1015,1016,1017,1026]:
 d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
for i in [1022,1030]:
 assert d.data(i)['name']=='PitchContainer'
 d.st(i,[(131081,d.enum('none'))])
for i in [1021,1023,1029,1031]:
 d.st(i,[(131105,d.pct(50)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])

selected=next(v for v in d.data(1002)['ValueVariables'] if v['m_name']=='selectedTab')
assert selected['m_scopeValue']['m_serializedData']=='Int|0|(Session,Implicit,{selectedTab},{selectedTab})'
selected['m_scopeValue']['m_serializedData']='Int|1|(Session,Implicit,{highlightLowerSelectedTab},{highlightLowerSelectedTab})'

assert d.data(1013)==sd(old_refs,1013), 'Native dropdown choices or events changed'
assert d.data(1011)==sd(old_refs,1011), 'Native selector switch changed'
assert d.a(upper)['m_Children']==[]
assert d.a(lower)['m_Children']==[{'rid':1008},{'rid':1009}]
assert all(d.a(i)['m_Parent']['rid']==lower for i in [1008,1009])
allowed_nodes={1001,1002,1004,1006,1008,1009,1011,1015,1016,1017,1021,1022,1023,1026,1029,1030,1031}
allowed_records=allowed_nodes|{d.a(1002)['m_SerializedData']['rid']}
for rid,record in old_refs.items():
 if rid not in allowed_records:assert d.r[rid]==record,('Unrelated UI record changed',rid)
for key,value in old_style.items():
 if isinstance(value,list):assert d.s[key][:len(value)]==value,('Original stylesheet data modified',key)
 else:assert d.s[key]==value
d.save()

output=env[G].file.save(packer='lz4')
check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[G])
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(check[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,expected in changes[G].items():assert check[pid].read_typetree()==expected
validate_ui(check[d.obj.path_id].read_typetree(),check[d.sid].read_typetree())
(OUT/G).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
report={'passed':True,'template':d.d['m_Name'],'upper_half':{'name':d.data(upper)['name'],'top_percent':0,'height_percent':50,'empty':True},'lower_half':{'name':d.data(lower)['name'],'top_percent':50,'height_percent':50,'native_dropdown_preserved':True,'default_mode':'statsOnlyView','pitch_hidden_in_all_modes':True},'parent_grid_unchanged':True,'unrelated_ui_records_unchanged':True,'unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v['m_Name'] for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# Highlight 中间区域上下布局

上方 50% 为空白占位；下方 50% 保留原生数据选择器和数据视图，默认显示比赛统计。
球场绘制在全部选择模式中隐藏；原来球场两侧的统计/事件内容仅在下半区对应数据模式中显示。
沿用三项原生选择器的绑定、选项和交互，下半区的详细统计、两队统计和赛事数据仍可切换。
不修改外层网格，左右阵型、左右下方数据卡、底部球员和工具条保持现有布局。

控制文件：ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle 的 MatchViewer_12x4 及其内联样式。
新增 HighlightUpperBlankHalf / HighlightLowerDataHalf 两个内部容器。
本地 CustomGridCompositions 当前的 MatchViewer 仍占中间 12×8，因而无需清除或重置该布局。

退出游戏后运行 install.ps1 安装。restore.ps1 用于只恢复本次修改。
已通过序列化回读、UI 层级和样式引用、无关对象一致性检查，尚未进行游戏内显示验证。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'upper_percent':50,'lower_percent':50,'native_dropdown_preserved':True},ensure_ascii=False))
