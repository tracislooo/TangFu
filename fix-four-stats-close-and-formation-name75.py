from pathlib import Path
import json,ast
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','four-stats-close-formation-name75-').replace('NAMES=[W,G,M,F]','NAMES=[W,G]')
exec(compile(boot,'backup-current-resources','exec'))
main=Doc(G,name='MatchViewer_12x4');asset_clones=[];new_guids={}
source=(R/'build-highlight-five-column-native-player-lists.py').read_text('utf8');helper=ast.parse(source)
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['register_clone','clone_doc','allptr']],type_ignores=[]),'private-marker-helpers','exec'))
card=Doc(W,name='PlayerStatsCard');original_card=copy.deepcopy(card.d);oldcr=refs(original_card)
target=next(x for x in card.a(1005)['m_SerializedDataOverride'] if x['m_ElementId']==-2034783885)
close_override=target['m_SerializedData']['rid'];v=card.a(close_override)
assert v['Binding']['m_direct']['Path']['m_path']=='InMatch'
v['Binding']['m_direct']['Path']['m_path']='const.True'
for rid,record in oldcr.items():
 expected=copy.deepcopy(record)
 if rid==close_override:expected['data']['Binding']['m_direct']['Path']['m_path']='const.True'
 assert card.r[rid]==expected,('Unexpected report/event change',rid)
card.save()
# Verify the exact four lower-selector choices use the same native stats tile.
T='ui-tileslayouts_assets_all.bundle';te=UnityPy.load(str(GAME/T));to={o.path_id:o for o in te.objects};route_audits=[]
for name in ['PlayerStatsHumanTeamTileDescription','PlayerStatsOppositionTeamTileDescription','PlayerStatsHomeTeamTileDescription','PlayerStatsAwayTeamTileDescription']:
 ob=next(o for o in to.values() if o.type.name=='MonoBehaviour' and o.peek_name()==name);tree=ob.read_typetree()
 assert all(c['AssetRef']['m_AssetGUID']=='6a4b032b28fee7b47941ca946d06eafb' for c in tree['<Configurations>k__BackingField'])
 route_audits.append(name)
stats=Doc(G,name='PlayerStats_4x6');event=bytes(stats.a(1009)['Events']['m_bytes'])
assert b'dc085ed5dab4a7c478fc45e7db3e93d0' in event and b'InMatch' not in event

font_audits=[];marker_guids={}
resolver=(R/'reflow-highlight-comparison-four-by-four.py').read_text('utf8').split('# Resolve the existing desktop style metrics.')[1].split('\n',1)[1].split('f32=lambda value:')[0]
for index,(kind,name) in enumerate([('Live','TacticsMatchPositionFilled'),('Past','TacticsPastMatchPositionFilled')]):
 donor=Doc(G,name=name);old_refs=refs(copy.deepcopy(donor.d));old_style=copy.deepcopy(donor.s)
 def data_before(i):return sd(old_refs,i)
 exec(compile(resolver,'resolve-current-desktop-name-font','exec'))
 assert donor.data(1022)['name']=='Name'
 assert 65537 in computed(1022),('Name font missing from desktop styles',name)
 original=font_metric(1022)
 assert len(original)==1 and original[0][0]==3 and original[0][1]['unit']==1
 original_px=original[0][1]['value'];new_px=original_px*.75
 tile,guid=clone_doc(donor,'HighlightFormation'+kind+'NameAt75',-981025000002300-index*10)
 before_tile=copy.deepcopy(tile.d);br=refs(before_tile)
 tile.st(1022,[(65537,tile.px(new_px))])
 for rid,record in br.items():
  expected=copy.deepcopy(record)
  if rid==1022:expected['data']['m_RuleIndex']=tile.a(rid)['m_RuleIndex']
  assert tile.r[rid]==expected,('Other marker style/binding changed',name,rid)
 tile.save();marker_guids[kind]=guid;font_audits.append({'source':name,'private':tile.d['m_Name'],'name_node':1022,'font_before_px':original_px,'font_after_px':new_px,'scale':.75})

for pid in [-981025000002000,-981025000002100]:
 d=Doc(G,pid=pid);before_tile=copy.deepcopy(d.d);br=refs(before_tile);allowed=set()
 for node,kind,old_guid in [(1064,'Past','27f358854bccd54408d274f5c58c3091'),(1065,'Live','ea29b0e9d55be0845aaf4d9afefd7721')]:
  v=d.data(node);assert v['PositionTemplateAsset']['m_AssetGUID']==old_guid
  v['PositionTemplateAsset']['m_AssetGUID']=marker_guids[kind];allowed.add(d.a(node)['m_SerializedData']['rid'])
 for rid,record in br.items():
  expected=copy.deepcopy(record)
  if rid in allowed:
   kind='Past' if rid==d.a(1064)['m_SerializedData']['rid'] else 'Live'
   expected['data']['PositionTemplateAsset']['m_AssetGUID']=marker_guids[kind]
  assert d.r[rid]==expected,('Formation layout/direction/selector changed',rid)
 d.save()
meta_code=source.split('for bundle in NAMES:\n metaobj=',1)[1].split('spec=importlib.util',1)[0]
exec(compile('for bundle in [G]:\n metaobj='+meta_code,'register-private-name-markers','exec'))
catalog_code=source.split("spec=importlib.util.spec_from_file_location('five_column_catalog'",1)[1].split('outputs={}\n',1)[0]
exec(compile("spec=importlib.util.spec_from_file_location('five_column_catalog'"+catalog_code,'extend-catalog-preserving-originals','exec'))
outputs={}
for bundle in NAMES:
 data=env[bundle].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 assert set(saved)==set(objs[bundle])
 for pid,h in hashes[bundle].items():
  if pid not in changes[bundle]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',bundle,pid)
 for pid,tree in changes[bundle].items():assert saved[pid].read_typetree()==tree,('Serialization mismatch',bundle,pid)
 for doc in [doc for doc in documents if doc.n==bundle]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 if bundle==G:
  for doc in [main,stats,Doc(G,name='TacticsMatchPositionFilled'),Doc(G,name='TacticsPastMatchPositionFilled')]:
   for pid in [doc.obj.path_id,doc.sid]:assert sha(saved[pid].get_raw_data())==hashes[G][pid]
 outputs[bundle]=data
outputs['catalog.bin']=catalog;outputs['catalog.hash']=hashlib.md5(catalog).hexdigest().encode('ascii')
for name,data in outputs.items():(OUT/name).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'four_stats_routes':route_audits,'all_open_panel_guid':'dc085ed5dab4a7c478fc45e7db3e93d0','tile_entry_missing_InMatch_confirmed':True,'normal_close_override':{'node':close_override,'old_path':'InMatch','new_path':'const.True'},'fullscreen_fallback_preserved':True,'native_close_events_unchanged':True,'private_name_fonts':font_audits,'only_two_private_side_formations_use_new_markers':True,'all_other_marker_text_portraits_and_events_unchanged':True,'formation_layout_directions_IP_OOP_and_stats_pages_unchanged':True,'commentary_and_toolbar_unchanged':True,'serialization_roundtrip':True,'unrelated_objects_and_catalog_locations_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):tree.get('m_Name','') for pid,tree in ps.items()} for n,ps in changes.items()},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
(OUT/'installer.py').write_bytes((R/'install-match-ui-patch.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('四个球员统计入口共用PlayerStats_4x6，其标题点击打开PlayerStatsReport时只传入match/team/ishometeam/fixture，未传入InMatch；PlayerStatsCard却将正常标题栏ShouldShowCloseButton可见性绑定到InMatch。将这个页面专属覆盖改为const.True，保留原关闭事件及上一版全屏/隐藏标题栏补位关闭按钮。两侧上方阵型仅改姓名：当前直播/历史姓名标记各建立私有副本，Name节点fontsize=当前桌面实际字号*0.75；左右两个私有阵型的两个绘图分支引用对应私有标记。头像、体能、评分、角色、绑定和其他样式不改；共用标记不改，方向、有球/无球切换、球员统计页和外层布局不改。解说及战术栏本轮不改。已完成精确字段比对、序列化回读、四入口共用路径核对及无关对象/目录一致性检查。当前游戏窗口已退出，未进行游戏内点击或渲染验证。restore.ps1回退本次修改。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'four_routes_verified':4,'name_fonts':font_audits,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
