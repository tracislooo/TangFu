from pathlib import Path
import json,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','fulltime-highlight-layout-').replace('NAMES=[W,G,M,F]','NAMES=[T]')
exec(compile(boot,'backup-current-installed-resources','exec'))
CK='<Configurations>k__BackingField'
names=['FullTimeTeamReportHumanGridComposition-Large','FullTimeTeamReportGridComposition-Large']
versions={};targets={};audits=[]
for name in names:
 ob=find(T,name);old=ob.read_typetree();tree=copy.deepcopy(old)
 human='Human' in name
 donor=find(T,'HalfTimeTeamReport'+('Human' if human else '')+'GridComposition-Large').read_typetree()
 oldslots={a['m_elementID']:a for a in old['m_gridComponents']}
 newslots={a['m_elementID']:a for a in donor['m_gridComponents']}
 slots=[copy.deepcopy(oldslots['MatchResult'])]
 for ident in ['HomeTeamFormationAdaptive','LiveTable','MatchViewer','AwayTeamFormationAdaptive','LatestScores']:
  if ident in ['LiveTable','LatestScores']:
   a=copy.deepcopy(oldslots[ident]);a['m_location']={'x':0 if ident=='LiveTable' else 15,'y':6,'width':5,'height':4}
   for key in ['m_minSize','m_maxSize']:a[key]={'x':5,'y':4}
   configs=[]
   for ref in a['m_configDescriptions']:
    desc=objs[T][ref['m_PathID']].read_typetree()
    configs.extend(copy.deepcopy(c) for c in desc[CK] if c['Size']=={'x':5,'y':4})
   assert len(configs)==1
   assert configs[0]['AssetRef']==a['m_gridElementConfigs'][0]['AssetRef']
   a['m_gridElementConfigs']=configs
   # Preserve the native card and all non-size behavior.
   expected=copy.deepcopy(oldslots[ident])
   for k in ['m_location','m_minSize','m_maxSize','m_gridElementConfigs']:expected[k]=copy.deepcopy(a[k])
   assert a==expected
  else:
   a=copy.deepcopy(oldslots[ident]);source=newslots[ident]
   for k in ['m_location','m_minSize','m_maxSize','m_gridElementConfigs']:a[k]=copy.deepcopy(source[k])
   assert a['m_configDescriptions']==source['m_configDescriptions']
  slots.append(a)
 tree['m_gridComponents']=slots
 for k,v in tree['m_optionalSlices'].items():
  if isinstance(v,list) and k!='m_instantiationOrder':tree['m_optionalSlices'][k]=[]
 tree['m_compositionVersion']=old['m_compositionVersion']+1
 assert slots[0]==oldslots['MatchResult']
 assert {a['m_elementID'] for a in slots}=={'MatchResult','HomeTeamFormationAdaptive','AwayTeamFormationAdaptive','MatchViewer','LiveTable','LatestScores'}
 cells=set()
 for a in slots:
  q=a['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<20 and 0<=y<10 and (x,y) not in cells
    cells.add((x,y))
  for c in a['m_gridElementConfigs']:assert c in objs[T][c['Description']['m_PathID']].read_typetree()[CK]
 assert len(cells)==200
 # No binding, selector directory, condition, or header changes.
 expected=copy.deepcopy(old)
 for k in ['m_gridComponents','m_optionalSlices','m_compositionVersion']:expected[k]=copy.deepcopy(tree[k])
 assert tree==expected
 ob.save_typetree(tree);changes[T][ob.path_id]=tree;targets[name]=tree
 versions[name]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}
 audits.append({'name':name,'slots':[{k:a[k] for k in ['m_elementID','m_location']} for a in slots],'header_and_all_bindings_preserved':True,'native_live_table_and_latest_scores_preserved':True})

migration_code='import copy\nTARGETS='+repr(targets)+'''
def migrate_layout(document,forward=True,version=None,limits_from=None):
 if not forward:
  assert limits_from is not None,'Original cache backup required'
  return copy.deepcopy(limits_from)
 result=copy.deepcopy(document);target=TARGETS[result['m_Name']]
 prior=document['m_gridComponents'];blocks=[]
 for slot in target['m_gridComponents']:
  ident=slot['m_elementID'];q=slot['m_location']
  origin={'MatchResult':(0,0),'HomeTeamFormationAdaptive':(0,2),'LiveTable':(0,8),'MatchViewer':(4,2),'AwayTeamFormationAdaptive':(16,2),'LatestScores':(16,8)}[ident]
  candidates=[b for b in prior if (b['m_location']['x'],b['m_location']['y']) in [origin,(q['x'],q['y'])]]
  chosen=next((b for b in candidates if b['m_elementID']==ident),None)
  if chosen is None:chosen=next(iter(candidates),None)
  b=copy.deepcopy(chosen if chosen is not None else slot)
  for k in ['m_location','m_minSize','m_maxSize']:b[k]=copy.deepcopy(slot[k])
  b['m_configDescriptions']=[];b['m_gridElementConfigs']=[];b['m_configDescriptionKeys']=[b['m_elementID']]
  blocks.append(b)
 result['m_gridComponents']=blocks
 result['m_optionalSlices']=copy.deepcopy(target['m_optionalSlices'])
 result['m_compositionVersion']=version if version is not None else target['m_compositionVersion']
 return result
'''
migration=types.ModuleType('fulltime_migration');exec(migration_code,migration.__dict__)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');previews=[]
for name,ver in versions.items():
 p=cache_root/name
 if not p.exists():continue
 document=json.loads(p.read_text('utf8'));updated=migration.migrate_layout(document,version=ver['after'])
 assert migration.migrate_layout(updated,False,limits_from=document)==document
 previews.append(name)
 (OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')
data=env[T].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
assert set(saved)==set(objs[T])
for pid,h in hashes[T].items():
 if pid not in changes[T]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,tree in changes[T].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',pid)
assert len(changes[T])==2
(OUT/T).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
report={'layouts':audits,'columns':[5,10,5],'side_heights':[4,4],'middle_size':[10,8],'selected_defaults':['LiveTable','LatestScores'],'only_two_fulltime_large_compositions_changed':True,'all_templates_descriptors_bindings_and_selector_choices_unchanged':True,'halftime_highlight_small_phone_unchanged':True,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False,'cache_previews':previews}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{T:{str(pid):tree['m_Name'] for pid,tree in changes[T].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{T:sha(data)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[T],'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
(OUT/'installer.py').write_bytes((R/'install-highlight-layout-with-cache.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('仅修改赛后报告执教/旁观两套Large布局：顶部20x2比分槽原样保留；下方5:10:5、两侧4:4、中间10x8。引用当前中场报告的私有横向主客队阵型和完整MatchViewer，左下保留LiveTable，右下保留LatestScores，使用已有5x4配置。移除中间额外三卡及可选扩展切片；选择器目录、所有绑定/条件不变。中场、Highlight、全局模板、小屏、手机资源不变；当前无对应赛后缓存，安装时若出现，仅迁移对应两份并保留槽位选择。已通过200格覆盖、序列化回读和无关对象一致性检查；游戏内渲染/点击未验证。restore.ps1恢复本次资源及对应缓存。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'changed_objects':2,'cache_previews':previews,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
