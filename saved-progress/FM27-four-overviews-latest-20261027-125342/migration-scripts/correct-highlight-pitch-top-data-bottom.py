from pathlib import Path
import json

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-pitch-top-data-bottom-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-current-template-and-load-codecs','exec'))

previous=R/'highlight-blank-data-halves-20261024-052900'
backup=UnityPy.load(str(previous/'backup-game'/G))
base_objects={o.path_id:o for o in backup.objects}
pid=-7710242645031577538
base=base_objects[pid].read_typetree();sid=base['inlineSheet']['m_PathID']
base_style=base_objects[sid].read_typetree()
d=Doc(G,pid=pid,tree=base,style=base_style)
original=copy.deepcopy(d.d);old_refs=refs(original)
assert d.a(1006)['m_Children']==[{'rid':1008},{'rid':1009}]
assert d.a(1008)['m_Children']==[{'rid':1011}]
assert d.a(1022)['m_Parent']['rid']==1015

upper=d.add(d,1015,1008,'HighlightPitchUpperHalf')
lower=d.add(d,1015,1008,'HighlightDataLowerHalf')
left=d.add(d,1015,upper,'HighlightPitchLeftBlank')
right=d.add(d,1015,upper,'HighlightPitchRightBlank')
for i in [upper,lower,left,right]:d.a(i)['m_Classes']=[]
for i,top in [(upper,0),(lower,50)]:
 d.st(i,[(131102,d.enum('absolute')),(131089,d.px(0)),(131104,d.pct(top)),(131105,d.pct(100)),(131087,d.pct(50)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131099,d.px(12)),(131100,d.px(12)),(131101,d.px(12)),(131098,d.px(12))])
d.st(upper,[(131083,d.enum('row')),(131073,d.enum('stretch')),(131101,d.px(24))])
for i in [left,right]:
 d.st(i,[(131105,d.px(200)),(131097,d.px(200)),(131084,d.num(0)),(131085,d.num(0))])
d.move(1011,lower)
d.move(1022,upper,1)
for i in [1001,1002,1004,1006]:
 d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
d.st(1008,[(131102,d.enum('relative')),(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131099,d.px(0)),(131100,d.px(0)),(131101,d.px(0)),(131098,d.px(0))])
d.st(1022,[(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
d.st(1030,[(131081,d.enum('none'))])
for i in [1011,1015,1016,1017,1026]:
 d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
for i in [1021,1023,1029,1031]:
 d.st(i,[(131105,d.pct(50)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])

assert d.a(1006)['m_Children']==[{'rid':1008},{'rid':1009}]
assert d.r[1009]==old_refs[1009] and d.r[1013]==old_refs[1013]
assert d.data(1009)==sd(old_refs,1009) and d.data(1013)==sd(old_refs,1013)
selector_rule=old_refs[1009]['data']['m_RuleIndex']
assert d.s['m_Rules'][selector_rule]==base_style['m_Rules'][selector_rule]
assert d.data(1002)==sd(old_refs,1002),'Original selection and session settings changed'
assert d.data(1011)==sd(old_refs,1011),'Native data switch binding changed'
assert d.a(upper)['m_Children']==[{'rid':left},{'rid':1022},{'rid':right}]
assert d.a(left)['m_Children']==[] and d.a(right)['m_Children']==[]
assert d.a(lower)['m_Children']==[{'rid':1011}]
allowed={1001,1002,1004,1006,1008,1011,1015,1016,1017,1021,1022,1023,1026,1029,1030,1031}
for rid,record in old_refs.items():
 if rid not in allowed:assert d.r[rid]==record,('Unrelated original record changed',rid)
d.save()
assert not any('HighlightUpperBlankHalf'==x.get('data',{}).get('name') for x in d.r.values())

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
report={'passed':True,'incorrect_previous_template_reverted_before_edit':True,'baseline':str(previous/'backup-game'/G),'template':d.d['m_Name'],'upper_half':{'height_percent':50,'native_pitch_retained':True,'left_and_right_blank':True,'pitch_independent_of_data_selection':True},'lower_half':{'height_percent':50,'original_data_modes_and_bindings_preserved':True},'selector_original_parent_position_style_options_and_selection_unchanged':True,'parent_grid_unchanged':True,'unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v['m_Name'] for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# Highlight 球场在上、数据在下

先从上一次修改前的备份恢复 MatchViewer_12x4 模板与样式，再实施以下更正：

- 中间区域上半区保留原生实时球场；两侧原来的数据位置改为空白占位。
- 下半区使用原生选择器控制的数据模式；切换数据不隐藏上半区球场。
- 选择器完全保留原来的右上角位置、父容器、样式、选项、绑定与初始选择。
- 不改外层网格、左右阵型、底部球员条或战术指令。

控制文件：ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle 内的 MatchViewer_12x4 及其内联样式。
新内部容器：HighlightPitchUpperHalf、HighlightDataLowerHalf。
已通过层级/样式检查、选择器原样一致性检查和序列化回读；尚未在游戏内验证视觉效果。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'pitch_top':True,'data_bottom':True,'selector_unchanged':True},ensure_ascii=False))
