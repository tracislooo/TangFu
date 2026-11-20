from pathlib import Path
import json

R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-five-panel-layout-').replace('NAMES=[W,G,M,F]','NAMES=[T]')
exec(compile(boot,'backup-current-layout-and-load-codecs','exec'))

VIEWER=2268119280419395392
STATS=7747877697308398809
config_key='<Configurations>k__BackingField'
viewer=objs[T][VIEWER].read_typetree()
old_viewer=copy.deepcopy(viewer)
large_viewer=next(copy.deepcopy(c) for c in viewer[config_key] if c['Size']=={'x':12,'y':4})
tall_viewer=copy.deepcopy(large_viewer)
tall_viewer['Size']={'x':12,'y':8}
assert not any(c['Size']==tall_viewer['Size'] for c in viewer[config_key])
viewer[config_key].append(tall_viewer)
objs[T][VIEWER].save_typetree(viewer)
changes[T][VIEWER]=viewer
stats=objs[T][STATS].read_typetree()
small_stats=next(copy.deepcopy(c) for c in stats[config_key] if c['Size']=={'x':4,'y':2})

names=[
 'MatchExperienceHumanGridComposition-Large',
 'MatchExperienceHumanGridComposition-Large-NoLeague',
 'MatchExperienceGridComposition-Large',
 'MatchExperienceGridComposition-Large-NoLeague',
]
audits=[]
for name in names:
 obj=find(T,name);doc=obj.read_typetree();original=copy.deepcopy(doc)
 blocks={c['m_elementID']:c for c in doc['m_gridComponents']}
 assert {'MatchEvents','Dugout','LatestScores','xGStory','MatchViewer'}<=blocks.keys()
 original_footprint=max(c['m_location']['x']+c['m_location']['width'] for c in blocks.values()),max(c['m_location']['y']+c['m_location']['height'] for c in blocks.values())
 assert original_footprint==(20,8)
 removed={'MatchEvents','Dugout','LatestScores','xGStory'}
 doc['m_gridComponents']=[c for c in doc['m_gridComponents'] if c['m_elementID'] not in removed]
 middle=next(c for c in doc['m_gridComponents'] if c['m_elementID']=='MatchViewer')
 middle['m_location']={'x':4,'y':0,'width':12,'height':8}
 middle['m_minSize']={'x':12,'y':8};middle['m_maxSize']={'x':12,'y':8}
 middle['m_gridElementConfigs']=[copy.deepcopy(tall_viewer)]
 compact=copy.deepcopy(blocks['xGStory'])
 compact.update(m_elementID='MatchStatsStandAlone',m_configDescriptions=[{'m_FileID':0,'m_PathID':STATS}],m_configDescriptionKeys=[],m_gridElementConfigs=[copy.deepcopy(small_stats)],m_location=copy.deepcopy(blocks['LatestScores']['m_location']),m_minSize={'x':4,'y':2},m_maxSize={'x':4,'y':2},m_features=0)
 doc['m_gridComponents'].append(compact)
 doc['m_placementBindings']=[b for b in doc['m_placementBindings'] if b['m_elementID'] not in removed]
 if not any(b['m_elementID']=='MatchStatsStandAlone' for b in doc['m_placementBindings']):
  doc['m_placementBindings'].append({'m_elementID':'MatchStatsStandAlone','m_optionalConditions':[],'m_optionalConfigConditions':[]})
 for key,value in doc['m_optionalSlices'].items():
  if isinstance(value,list) and key!='m_instantiationOrder':doc['m_optionalSlices'][key]=[]
 doc['m_compositionVersion']+=1
 cells={};ids=set()
 for c in doc['m_gridComponents']:
  assert c['m_elementID'] not in ids;ids.add(c['m_elementID'])
  loc=c['m_location']
  for x in range(loc['x'],loc['x']+loc['width']):
   for y in range(loc['y'],loc['y']+loc['height']):
    assert 0<=x<20 and 0<=y<8
    assert (x,y) not in cells,('overlap',name,c['m_elementID'],cells.get((x,y)))
    cells[x,y]=c['m_elementID']
  for cfg in c['m_gridElementConfigs']:
   available=viewer if cfg['Description']['m_PathID']==VIEWER else objs[T][cfg['Description']['m_PathID']].read_typetree()
   assert cfg in available[config_key],('unsupported configuration',name,c['m_elementID'])
 assert len(cells)==160 and len(ids)==5
 assert all(cells[x,y]=='MatchViewer' for x in range(4,16) for y in range(8))
 assert not ids & removed
 for c in doc['m_gridComponents']:
  if c['m_elementID'] not in ['MatchViewer','MatchStatsStandAlone']:assert c==blocks[c['m_elementID']],('side panel changed',name)
 allowed={'m_gridComponents','m_placementBindings','m_optionalSlices','m_compositionVersion'}
 assert all(v==doc[k] for k,v in original.items() if k not in allowed)
 obj.save_typetree(doc);changes[T][obj.path_id]=doc
 (OUT/'templates'/(name+'.json')).write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
 audits.append({'name':name,'path_id':obj.path_id,'composition_version':doc['m_compositionVersion'],'grid':[20,8],'panels':{c['m_elementID']:c['m_location'] for c in doc['m_gridComponents']},'no_overlaps':True,'no_gaps':True,'side_formations_and_bottom_left_panel_unchanged':True})

assert viewer[config_key][:-1]==old_viewer[config_key]
assert all(v==viewer[k] for k,v in old_viewer.items() if k!=config_key)
output=env[T].file.save(packer='lz4')
check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[T])
for pid,h in hashes[T].items():
 if pid not in changes[T]:assert sha(check[pid].get_raw_data())==h,('unrelated asset changed',pid)
for pid,expected in changes[T].items():assert check[pid].read_typetree()==expected
(OUT/T).write_bytes(output)
(OUT/'templates/MatchViewerTileDescription.json').write_text(json.dumps(viewer,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p in before:
 if p.name.startswith('catalog.'):protected[p]=sha(before[p])
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'scope':'Desktop large highlight grids, human/spectator, league/no-league','layouts':audits,'changes':{T:{str(pid):d['m_Name'] for pid,d in changes[T].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{T:sha(output)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[],'unrelated_objects_unchanged':True}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps({'passed':True,'layouts':audits,'native_compact_stats_configuration':small_stats,'existing_viewer_configs_unchanged':True,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False},ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[T],'before':{str(p):str(OUT/('backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
for name in ['install.ps1','restore.ps1']:(OUT/name).write_bytes((R/'match-ui-avatars-layout-20261023-141148'/name).read_bytes())
(OUT/'修改说明.md').write_text('''# Highlight 布局调整

- 删除 2 替补席意见、3 赛事、8 最新比分。
- 4 比赛数据放到原 8 的右下角，使用原生 4×2 紧凑统计模板。
- 7 球场及两侧统计模块改为占满中间 12×8 网格。
- 1、5 两侧阵型以及 6 左下模块保持原位置、配置。
- 修改大屏布局的主客场/旁观与有无积分榜版本，共四个布局；小屏和其他页面保留。
- 所有头像、记分牌、战术工具条与底部球员卡片资源保持不变。

控制文件：ui-tileslayouts_assets_all.bundle 内的 MatchExperienceHumanGridComposition-Large、MatchExperienceGridComposition-Large 及其 NoLeague 版本。
MatchViewerTileDescription 新增 12×8 配置，复用现有 MatchViewer_12x4 绘制模板；原配置全部保留。
已通过序列化回读、网格无重叠/无空洞及无关对象一致性检查；尚未在游戏内验证显示效果。

安装：运行 install.ps1；恢复本次修改：退出游戏后运行 restore.ps1。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'layouts':len(audits),'changed_objects':len(changes[T])},ensure_ascii=False))
