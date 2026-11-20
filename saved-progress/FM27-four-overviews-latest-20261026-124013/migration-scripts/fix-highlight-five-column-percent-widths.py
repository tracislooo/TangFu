from pathlib import Path
import json,types

R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-widths-20-10-40-10-20-').replace('NAMES=[W,G,M,F]','NAMES=[T]')
exec(compile(boot,'backup-current-grid-and-load-codecs','exec'))
CK='<Configurations>k__BackingField'
names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
mapping={(0,2):(0,4),(2,1):(4,2),(3,8):(6,8),(11,1):(14,2),(12,2):(16,4)}
migration_code='''import copy
MAPPING=__MAPPING__
def migrate_layout(document,forward=True,version=None,limits_from=None):
 result=copy.deepcopy(document);mapping=MAPPING if forward else {v:k for k,v in MAPPING.items()}
 destination=set(mapping.values())
 for b in result['m_gridComponents']:
  q=b['m_location'];key=(q['x'],q['width']);assert key in mapping or key in destination,('Unexpected slot',b['m_elementID'],key)
  x,w=mapping.get(key,key);q['x']=x;q['width']=w;b['m_minSize']['x']=w;b['m_maxSize']['x']=w
  for cfg in b['m_gridElementConfigs']:cfg['Size']['x']=w
 result['m_layoutMode']=0 if forward else 4
 if limits_from is not None:
  old={(b['m_location']['x'],b['m_location']['width'],b['m_location']['y']):b for b in limits_from['m_gridComponents']}
  for b in result['m_gridComponents']:
   q=b['m_location'];key=(q['x'],q['width'],q['y'])
   if key in old:b['m_minSize']=copy.deepcopy(old[key]['m_minSize']);b['m_maxSize']=copy.deepcopy(old[key]['m_maxSize'])
  result['m_layoutMode']=limits_from['m_layoutMode']
 if version is not None:result['m_compositionVersion']=version
 cells=set();width=20 if forward else 14
 for b in result['m_gridComponents']:
  q=b['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<width and 0<=y<8 and (x,y) not in cells
    cells.add((x,y))
 assert len(cells)==width*8
 return result
'''.replace('__MAPPING__',repr(mapping))
migration=types.ModuleType('percent_grid_migration');exec(compile(migration_code,'grid_migration.py','exec'),migration.__dict__)
size_audits=[]
for pid in [-981025000000300,-981025000000301]:
 obj=objs[T][pid];tree=obj.read_typetree();old=copy.deepcopy(tree)
 candidate=copy.deepcopy(tree[CK][0]);candidate['Size']['x']=2
 if candidate not in tree[CK]:tree[CK].append(candidate)
 assert tree[CK][:len(old[CK])]==old[CK]
 obj.save_typetree(tree);changes[T][pid]=tree;size_audits.append({'name':tree['m_Name'],'added_size':candidate['Size']})
versions={};audits=[]
for name in names:
 obj=find(T,name);original=obj.read_typetree();version=original['m_compositionVersion']+1
 tree=migration.migrate_layout(original,version=version)
 for b in tree['m_gridComponents']:
  q=b['m_location'];choices=[]
  for ref in b['m_configDescriptions']:
   descriptor=changes[T].get(ref['m_PathID'],objs[T][ref['m_PathID']].read_typetree());choices.extend(descriptor.get(CK,[]))
  b['m_gridElementConfigs']=[copy.deepcopy(next(c for c in choices if c['Size']=={'x':q['width'],'y':q['height']}))]
 assert [b['m_elementID'] for b in tree['m_gridComponents']]==[b['m_elementID'] for b in original['m_gridComponents']]
 obj.save_typetree(tree);changes[T][obj.path_id]=tree
 versions[name]={'before':original['m_compositionVersion'],'after':version}
 audits.append({'name':name,'layout_mode_before':original['m_layoutMode'],'layout_mode_after':tree['m_layoutMode'],'positions':{b['m_elementID']:b['m_location'] for b in tree['m_gridComponents']}})
 (OUT/'templates'/(name+'.json')).write_text(json.dumps(tree,ensure_ascii=False,indent=2),'utf8')
data=env[T].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
assert set(saved)==set(objs[T])
for pid,h in hashes[T].items():
 if pid not in changes[T]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',pid)
for pid,tree in changes[T].items():assert saved[pid].read_typetree()==tree,('Roundtrip failed',pid)
(OUT/T).write_bytes(data)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');previews=[]
for name,version in versions.items():
 path=cache_root/name
 if not path.exists():continue
 original=json.loads(path.read_text('utf8'));updated=migration.migrate_layout(original,version=version['after'])
 restored=migration.migrate_layout(updated,False,version=version['before'],limits_from=original)
 assert restored['m_gridComponents']==original['m_gridComponents'] and restored['m_layoutMode']==original['m_layoutMode']
 previews.append({'file':name,'selected_modules':[b['m_elementID'] for b in updated['m_gridComponents']]})
 (OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')
for path,b in before.items():assert path.read_bytes()==b
for path,h in protected.items():assert sha(path.read_bytes())==h
for path in before:
 if path.name.startswith('catalog.'):protected[path]=sha(before[path])
report={'passed':True,'requested_percentages':[20,10,40,10,20],'logical_columns':[4,2,8,2,4],'column_boundaries_percent':[0,20,30,70,80,100],'grid_extent':[20,8],'layout_mode':0,'layouts':audits,'added_native_size_configs':size_audits,'custom_layout_previews':previews,'visual_templates_table_styles_and_mid_content_untouched':True,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{T:{str(pid):tree.get('m_Name','AssetBundle') for pid,tree in changes[T].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{T:sha(data)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[T],'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8');(OUT/'installer.py').write_bytes((R/'install-highlight-layout-with-cache.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed; see diagnostics above.' }\n",'utf8')
watcher=(R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_text('utf8').replace("'G:/Doc/ChatGPT/New project/install-match-ui-patch.py'","(Join-Path $PSScriptRoot 'installer.py')")
(OUT/'install-after-game-exits.ps1').write_text(watcher,'utf8')
(OUT/'修改说明.md').write_text('''# 修正五列宽度为20%/10%/40%/10%/20%

仅调整四套大屏执教/旁观、有无积分榜的外层网格：总跨度由14改为20，五列改为4/2/8/2/4，起点0/4/6/14/16；布局模式由原4改为原生自适应模式0。补充两个私有球员列表2×8尺寸配置，继续引用原有原生列表资产。
不修改球员表字体、行高、工厂、视图、列表内容、两侧选择器或中间页面的任何视觉资产。
存在本地比赛布局时，安装迁移坐标和布局模式，保留所有模块选择；不清空缓存。恢复脚本回退本次宽度调整。
已完成160格覆盖/无重叠、五列数学占比、序列化回读、无关对象一致性检查。尚未在游戏中实际验证铺满效果。
''','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'percentages':[20,10,40,10,20],'layout_mode':0,'saved_layouts':len(previews),'roundtrip':True},ensure_ascii=False))
