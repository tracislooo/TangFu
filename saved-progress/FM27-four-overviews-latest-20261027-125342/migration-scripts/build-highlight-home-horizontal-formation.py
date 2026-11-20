from pathlib import Path
import json,ast
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-home-horizontal-formation-').replace('NAMES=[W,G,M,F]','NAMES=[G,M,T]')
exec(compile(boot,'backup-current-resources','exec'))
main=Doc(G,name='MatchViewer_12x4');asset_clones=[];new_guids={}
source=(R/'build-highlight-five-column-native-player-lists.py').read_text('utf8')
helper=ast.parse(source)
code=ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['register_clone','clone_doc','allptr']],type_ignores=[])
exec(compile(code,'private-native-asset-helpers','exec'))
donor=Doc(G,name='TeamFormationAdaptiveBlock');native=copy.deepcopy(donor.d)
tile,guid=clone_doc(donor,'HighlightHomeHorizontalFormation',-981025000002000)
for i in [1064,1065]:
 assert tile.data(i)['Orientation']==0 and not tile.data(i)['OrientationBindingPath']['m_path']
 tile.data(i).update(Orientation=1,Orientation_UxmlAttributeFlags=1)
before_clone=copy.deepcopy(tile.d)
for i in [1064,1065]:
 sid=tile.a(i)['m_SerializedData']['rid'];expected=copy.deepcopy(donor.r[sid]);expected['data']['Orientation']=1
 assert tile.r[sid]==expected
tile.save()
old_guid='9a03c4e43edfd284fb46d9f17bc197da'
CK='<Configurations>k__BackingField'
desc=find(T,'HomeTeamFormationAdaptiveBlockDescription');dt=desc.read_typetree();old_dt=copy.deepcopy(dt)
for cfg in dt[CK]:assert cfg['AssetRef']['m_AssetGUID']==old_guid;cfg['AssetRef']['m_AssetGUID']=guid
desc.save_typetree(dt);changes[T][desc.path_id]=dt
layouts=[]
for name in ['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']:
 ob=find(T,name);tree=ob.read_typetree();old_tree=copy.deepcopy(tree);count=0
 for block in tree['m_gridComponents']:
  if block['m_elementID']!='HomeTeamFormationAdaptive':continue
  for cfg in block['m_gridElementConfigs']:
   assert cfg['AssetRef']['m_AssetGUID']==old_guid;cfg['AssetRef']['m_AssetGUID']=guid;count+=1
 assert count
 ob.save_typetree(tree);changes[T][ob.path_id]=tree;layouts.append(name)
# Preserve the previous authorized correction that is waiting for game exit.
pending=R/'commentary-bar-left-centered-text-20261025-131528'
pm=json.loads((pending/'manifest.json').read_text('utf8'))
pending_data=(pending/M).read_bytes();assert sha(pending_data)==pm['after_sha256'][M]
assert sha(before[GAME/M]) in [pm['before_sha256'][str(GAME/M)],pm['after_sha256'][M]]

meta_code=source.split('for bundle in NAMES:\n metaobj=',1)[1].split('spec=importlib.util',1)[0]
# Only bundle G gains an asset. T retains its native preload metadata.
exec(compile('for bundle in [G]:\n metaobj='+meta_code,'register-private-native-template','exec'))
catalog_code=source.split("spec=importlib.util.spec_from_file_location('five_column_catalog'",1)[1].split('outputs={}\n',1)[0]
exec(compile("spec=importlib.util.spec_from_file_location('five_column_catalog'"+catalog_code,'register-catalog-and-check-existing-locations','exec'))
outputs={}
for bundle in [G,T]:
 data=env[bundle].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 assert set(saved)==set(objs[bundle])
 for pid,h in hashes[bundle].items():
  if pid not in changes[bundle]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',bundle,pid)
 for pid,tree in changes[bundle].items():assert saved[pid].read_typetree()==tree,('Serialization mismatch',bundle,pid)
 if bundle==G:
  validate_ui(saved[tile.obj.path_id].read_typetree(),saved[tile.sid].read_typetree())
  assert sha(saved[donor.obj.path_id].get_raw_data())==hashes[G][donor.obj.path_id]
  assert sha(saved[main.obj.path_id].get_raw_data())==hashes[G][main.obj.path_id]
 outputs[bundle]=data
outputs[M]=pending_data;outputs['catalog.bin']=catalog;outputs['catalog.hash']=hashlib.md5(catalog).hexdigest().encode('ascii')
for name,data in outputs.items():(OUT/name).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
migration_code='''import copy
OLD=__OLD__;NEW=__NEW__
def migrate_layout(document,forward=True,**kwargs):
 result=copy.deepcopy(document);source,target=(OLD,NEW) if forward else (NEW,OLD)
 for block in result['m_gridComponents']:
  if block['m_elementID']!='HomeTeamFormationAdaptive':continue
  for cfg in block['m_gridElementConfigs']:
   if cfg['AssetRef']['m_AssetGUID']==source:cfg['AssetRef']['m_AssetGUID']=target
 return result
'''.replace('__OLD__',repr(old_guid)).replace('__NEW__',repr(guid))
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
cache_versions={name:{'before':4,'after':4} for name in layouts}
report={'private_template':tile.d['m_Name'],'guid':guid,'native_orientation':1,'pitch_nodes':[1064,1065],'unchanged_player_templates_and_bindings':True,'original_shared_template_and_away_formation_unchanged':True,'layouts':layouts,'pending_commentary_correction_included':True,'tactical_toolbar_minus20_preserved':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):tree.get('m_Name','') for pid,tree in ps.items()} for n,ps in changes.items()},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'cache_root':str(cache_root),'cache_versions':cache_versions},ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-highlight-layout-with-cache.py').read_text('utf8').replace('path=folder/name;assert path.parent.resolve()==folder',"path=(folder.parent/name if folder==game and name.startswith('catalog.') else folder/name);assert path.parent.resolve() in [folder,game.parent]")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((pending/'install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('第一列顶部阵型模块使用 TeamFormationAdaptiveBlock 的私有副本，仅将原生 FMTacticsPanel 的直播及历史分支 Orientation 从 Vertical(0) 改为 Horizontal(1)，不旋转头像、姓名、评分或整个界面。标题、选择器、球员模板及实时位置绑定不变；右侧与共用模板不变。四套大屏布局及主队模块描述引用私有副本；缓存仅替换主队模块的对应资产引用，不改变网格或选择。合并此前等待安装的解说条左移/文字居中修正，保留战术栏左移20px。静态回读及无关对象一致性通过，游戏内显示未验证。restore.ps1回退此合并安装。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'guid':guid,'pending_commentary_included':True,'runtime_verified':False},ensure_ascii=False),flush=True)
