from pathlib import Path
import json

R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-native-stats-only-').replace('NAMES=[W,G,M,F]','NAMES=[G]')
exec(compile(boot,'backup-current-template-and-load-codecs','exec'))

obj=find(G,'MatchViewer_12x4');doc=obj.read_typetree();rr=refs(doc);original=copy.deepcopy(doc);old=refs(original)
setter_rid=rr[1002]['data']['m_SerializedData']['rid']
setter=sd(rr,1002)
assert sd(rr,1016)['name']=='statsOnlyView'
assert rr[1011]['data']['m_Children']==[{'rid':1015},{'rid':1016},{'rid':1017}]
assert sd(rr,1011)['Binding']['m_direct']['Path']['m_path']=='SelectedTab'
selected=next(v for v in setter['ValueVariables'] if v['m_name']=='selectedTab')
assert selected['m_scopeValue']['m_serializedData'].startswith('Int|0|')
selected['m_scopeValue']['m_serializedData']='Int|1|(Session,Implicit,{highlightStatsOnlyDefaultV3},{highlightStatsOnlyDefaultV3})'
fun=next(f for f in setter['BindFunction'] if f['m_target']['m_guid']=='5116d1eea3b6b50438201e93682cd198')
raw=bytes(fun['m_inputs']['m_variable']['m_argumentBytes']);args=[];p=1
for _ in range(raw[0]):
 length=struct.unpack_from('<I',raw,p)[0];p+=4;args.append(raw[p:p+length]);p+=length
assert p==len(raw) and len(args)==5
assert args[0].endswith(bytes([len('const.One')])+b'const.One')
assert args[1].endswith(bytes([len('selectedTab')])+b'selectedTab')
old_path=bytes([len('defaultToStats')])+b'defaultToStats'
new_path=bytes([len('const.True')])+b'const.True'
assert args[3].count(old_path)==1
old_args=copy.deepcopy(args);args[3]=args[3].replace(old_path,new_path)
assert all(args[i]==old_args[i] for i in [0,1,2,4])
fun['m_inputs']['m_variable']['m_argumentBytes']=list(bytes([len(args)])+b''.join(struct.pack('<I',len(a))+a for a in args))

assert rr[1009]==old[1009] and rr[1013]==old[1013]
assert sd(rr,1009)==sd(old,1009) and sd(rr,1013)==sd(old,1013)
assert all(rr[rid]==record for rid,record in old.items() if rid!=setter_rid)
assert sd(rr,1016)==sd(old,1016)
assert any(x.get('data',{}).get('name')=='HighlightPitchUpperHalf' for x in rr.values())
validate_ui(doc,objs[G][doc['inlineSheet']['m_PathID']].read_typetree())
obj.save_typetree(doc);changes[G][obj.path_id]=doc
(OUT/'templates/MatchViewer_12x4.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
output=env[G].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[G])
for pid,h in hashes[G].items():
 if pid not in changes[G]:assert sha(check[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,expected in changes[G].items():assert check[pid].read_typetree()==expected
(OUT/G).write_bytes(output)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
report={'passed':True,'changed_template':'MatchViewer_12x4','changed_record_only':setter_rid,'default_selected_tab':1,'native_page':'statsOnlyView','native_initialize_stats_condition':'const.True','upper_pitch_and_blank_sides_unchanged':True,'dropdown_position_options_events_and_binding_unchanged':True,'all_styles_unchanged':True,'native_stats_only_page_contents_unchanged':True,'unrelated_objects_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{G:{str(pid):v['m_Name'] for pid,v in changes[G].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{G:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[G],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'install-after-game-exits.ps1').write_bytes((R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# 下半区默认启用原生「仅数据」页面

下方的原生模式开关默认从 0（pitchStatsView，两队统计）改为 1（statsOnlyView，完整仅数据页）。
同时启用原生初始化函数的「仅数据」条件，避免调用方 defaultToStats=False 及旧会话选择导致仍打开旧模式。
完整复用 statsOnlyView 现有页面，不将球场两侧的统计作为默认下半区内容。
上半区球场、左右空白、50% 比例及右上角选择器的位置、样式、选项、绑定和操作均保持不变。
全部样式、原生仅数据页内容和其他资源对象通过一致性校验。

游戏运行中请正常退出后安装；install.ps1 安装，restore.ps1 恢复本次修改。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'native_page':'statsOnlyView','only_one_binding_record_changed':True},ensure_ascii=False))
