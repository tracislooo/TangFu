from pathlib import Path
import json,ast,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-equal-sides-away-horizontal-commentary75-').replace('NAMES=[W,G,M,F]','NAMES=[G,M,T]')
exec(compile(boot,'backup-current-resources','exec'))
main=Doc(G,name='MatchViewer_12x4');asset_clones=[];new_guids={}
source=(R/'build-highlight-five-column-native-player-lists.py').read_text('utf8')
helper=ast.parse(source)
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['register_clone','clone_doc','allptr']],type_ignores=[]),'private-asset-helpers','exec'))
home=Doc(G,pid=-981025000002000)
away,away_guid=clone_doc(home,'HighlightAwayHorizontalFormation',-981025000002100)
for i in [1064,1065]:
 assert home.data(i)['Orientation']==1 and home.data(i)['FlipPositions']==1
 away.data(i).update(FlipPositions=0,FlipPositions_UxmlAttributeFlags=1)
 sid=away.a(i)['m_SerializedData']['rid'];expected=copy.deepcopy(home.r[sid]);expected['data'].update(FlipPositions=0,FlipPositions_UxmlAttributeFlags=1)
 assert away.r[sid]==expected
for rid,record in home.r.items():
 if rid in {away.a(i)['m_SerializedData']['rid'] for i in [1064,1065]}:continue
 assert away.r[rid]==record,('Native selector/OOP binding changed',rid)
away.save()
comment=Doc(M,name='MatchCommentaryBar');original_comment=copy.deepcopy(comment.d);cr=refs(original_comment)
# Keep the existing outer measurement/max-width and shorten only the visible bar.
comment.st(1004,[(131105,comment.pct(75)),(131095,comment.pct(75)),(131074,comment.enum('flex-start'))])
for rid,record in cr.items():
 expected=copy.deepcopy(record)
 if rid==1004:expected['data']['m_RuleIndex']=comment.a(rid)['m_RuleIndex']
 assert comment.r[rid]==expected,('Commentary text/style/structure changed',rid)
comment.save()

CK='<Configurations>k__BackingField';native_guid='9a03c4e43edfd284fb46d9f17bc197da'
away_desc=find(T,'AwayTeamFormationAdaptiveBlockDescription');ad=away_desc.read_typetree()
for cfg in ad[CK]:
 assert cfg['AssetRef']['m_AssetGUID']==native_guid;cfg['AssetRef']['m_AssetGUID']=away_guid
changes[T][away_desc.path_id]=ad
available=set()
for name in ['MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet']:
 available.update(x['m_PathID'] for x in find(T,name).read_typetree()['m_gridElementDescriptions'])
config_audits=[]
for pid in sorted(available):
 ob=objs[T][pid];tree=copy.deepcopy(changes[T].get(pid,ob.read_typetree()));cfgs=tree.get(CK,[])
 # Existing top/bottom choices must remain loadable in the new 5x4 slots.
 if any(c['Size']=={'x':5,'y':4} for c in cfgs):continue
 options=[c for c in cfgs if c['Size']['x']==5 and c['Size']['y'] in [6,2]]
 if not options:continue
 candidate=copy.deepcopy(options[0]);candidate['Size']={'x':5,'y':4};cfgs.append(candidate)
 changes[T][pid]=tree;config_audits.append({'descriptor':tree['m_Name'],'added_size':[5,4],'asset_reused':candidate['AssetRef']['m_AssetGUID']})
for pid,tree in changes[T].items():objs[T][pid].save_typetree(tree)
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
migration_code='''import copy
NATIVE=__NATIVE__;AWAY=__AWAY__
def migrate_layout(document,forward=True,version=None,limits_from=None):
 result=copy.deepcopy(document)
 for block in result['m_gridComponents']:
  q=block['m_location']
  if q['x'] not in [0,15]:continue
  assert q['width']==5
  top=q['y']==0
  if forward:
   assert (q['y'],q['height']) in [(0,6),(6,2),(0,4),(4,4)]
   q['y']=0 if top else 4;q['height']=4
  else:
   assert (q['y'],q['height']) in [(0,4),(4,4)]
   q['y']=0 if top else 6;q['height']=6 if top else 2
  for key in ['m_minSize','m_maxSize']:block[key]['y']=q['height']
  for cfg in block['m_gridElementConfigs']:
   cfg['Size']['y']=q['height']
   if block['m_elementID']=='AwayTeamFormationAdaptive':
    old,new=(NATIVE,AWAY) if forward else (AWAY,NATIVE)
    if cfg['AssetRef']['m_AssetGUID']==old:cfg['AssetRef']['m_AssetGUID']=new
 if limits_from is not None:
  for block in result['m_gridComponents']:
   q=block['m_location']
   prior=[b for b in limits_from['m_gridComponents'] if b['m_location']==q and b['m_elementID']==block['m_elementID']]
   if len(prior)==1:
    for key in ['m_minSize','m_maxSize']:block[key]=copy.deepcopy(prior[0][key])
 if version is not None:result['m_compositionVersion']=version
 cells=set()
 for block in result['m_gridComponents']:
  q=block['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<20 and 0<=y<8 and (x,y) not in cells
    cells.add((x,y))
 assert len(cells)==160
 return result
'''.replace('__NATIVE__',repr(native_guid)).replace('__AWAY__',repr(away_guid))
migration=types.ModuleType('equal_sides_migration');exec(compile(migration_code,'grid_migration.py','exec'),migration.__dict__)
versions={};layout_audits=[]
for name in layout_names:
 ob=find(T,name);original=ob.read_typetree();version=original['m_compositionVersion']+1
 tree=migration.migrate_layout(original,version=version)
 assert [b['m_elementID'] for b in tree['m_gridComponents']]==[b['m_elementID'] for b in original['m_gridComponents']]
 for block in tree['m_gridComponents']:
  if block['m_location']['x'] not in [0,15]:continue
  choices=[]
  for ref in block['m_configDescriptions']:
   descriptor=changes[T].get(ref['m_PathID'],objs[T][ref['m_PathID']].read_typetree());choices.extend(descriptor.get(CK,[]))
  block['m_gridElementConfigs']=[copy.deepcopy(next(c for c in choices if c['Size']=={'x':5,'y':4}))]
 center=next(b for b in tree['m_gridComponents'] if b['m_elementID']=='MatchViewer')
 assert center==next(b for b in original['m_gridComponents'] if b['m_elementID']=='MatchViewer')
 ob.save_typetree(tree);changes[T][ob.path_id]=tree;versions[name]={'before':original['m_compositionVersion'],'after':version}
 layout_audits.append({'name':name,'slots':[{k:b[k] for k in ['m_elementID','m_location']} for b in tree['m_gridComponents']]})

meta_code=source.split('for bundle in NAMES:\n metaobj=',1)[1].split('spec=importlib.util',1)[0]
exec(compile('for bundle in [G]:\n metaobj='+meta_code,'register-private-template','exec'))
catalog_code=source.split("spec=importlib.util.spec_from_file_location('five_column_catalog'",1)[1].split('outputs={}\n',1)[0]
exec(compile("spec=importlib.util.spec_from_file_location('five_column_catalog'"+catalog_code,'extend-catalog-and-check-originals','exec'))
outputs={}
for bundle in NAMES:
 data=env[bundle].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 assert set(saved)==set(objs[bundle])
 for pid,h in hashes[bundle].items():
  if pid not in changes[bundle]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',bundle,pid)
 for pid,tree in changes[bundle].items():assert saved[pid].read_typetree()==tree,('Serialization mismatch',bundle,pid)
 for doc in [doc for doc in documents if doc.n==bundle]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 if bundle==G:
  for pid in [main.obj.path_id,main.sid,home.obj.path_id,home.sid,-4147311404635738106]:assert sha(saved[pid].get_raw_data())==hashes[G][pid]
 outputs[bundle]=data
outputs['catalog.bin']=catalog;outputs['catalog.hash']=hashlib.md5(catalog).hexdigest().encode('ascii')
for name,data in outputs.items():(OUT/name).write_bytes(data)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');previews=[]
for name,version in versions.items():
 path=cache_root/name
 if not path.exists():continue
 original=json.loads(path.read_text('utf8'));updated=migration.migrate_layout(original,version=version['after'])
 assert [b['m_elementID'] for b in updated['m_gridComponents']]==[b['m_elementID'] for b in original['m_gridComponents']]
 restored=migration.migrate_layout(updated,False,version=version['before'],limits_from=original)
 assert restored==original,('Cache restore mismatch',name)
 previews.append({'name':name,'selected_modules':[b['m_elementID'] for b in updated['m_gridComponents']]})
 (OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
report={'columns':[5,10,5],'side_upper_lower':[4,4],'layouts':layout_audits,'added_configs':config_audits,'home_formation_unchanged':True,'away_private_template':away.d['m_Name'],'away_guid':away_guid,'away_direction':'forwards left, goalkeeper right; native horizontal orientation, flip false','native_IP_OOP_selection_bindings_and_player_stats_page_preserved':True,'commentary_visible_width_relative_to_previous':.75,'commentary_outer_width_maximum_text_font_alignment_and_height_unchanged':True,'toolbar_minus20_and_middle_area_unchanged':True,'cache_previews':previews,'serialization_roundtrip':True,'unrelated_objects_and_catalog_locations_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):tree.get('m_Name','') for pid,tree in ps.items()} for n,ps in changes.items()},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
installer=(R/'install-highlight-layout-with-cache.py').read_text('utf8').replace('path=folder/name;assert path.parent.resolve()==folder',"path=(folder.parent/name if folder==game and name.startswith('catalog.') else folder/name);assert path.parent.resolve() in [folder,game.parent]")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('两侧上/下槽由6+2改为4+4，保持5:10:5与20x8总网格；四套大屏与对应缓存同步，仅变更侧栏y/height和尺寸配置，不清空缓存，不改所选模块。补齐5x4配置以继续加载原模块。左侧阵型原样保留；右侧复制当前左侧私有阵型，原生横向Orientation=1、FlipPositions=0，前锋在左门将在右。沿用满宽设置，保留有球/无球原生切换与全部绑定、第三个球员数据页、头像文字正立。解说可见容器1004宽度/最大宽度75%，外层原始宽度与最大宽度算法不变，左端位置不变，文字继续居中，文字/高度/颜色不改。战术栏左移20px与中间页面保持不变。序列化回读、160格覆盖无重叠、缓存迁移往返及无关对象/目录一致性通过；未进行游戏内显示验证。restore.ps1恢复本次资源与对应缓存改动。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'side_heights':[4,4],'away_guid':away_guid,'commentary_width':.75,'added_size_configs':len(config_audits),'cache_previews':len(previews),'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
