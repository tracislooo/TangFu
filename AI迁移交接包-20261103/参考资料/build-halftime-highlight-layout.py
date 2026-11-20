from pathlib import Path
import json,types
R=Path(__file__).parent
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','halftime-highlight-layout-').replace('NAMES=[W,G,M,F]','NAMES=[M,T]')
T='ui-tileslayouts_assets_all.bundle'
exec(compile(boot,'backup-current-installed-resources','exec'))
CK='<Configurations>k__BackingField'
names=['HalfTimeTeamReportHumanGridComposition-Large','HalfTimeTeamReportGridComposition-Large']
donor=find(T,'MatchExperienceHumanGridComposition-Large').read_typetree()
donor_slots=copy.deepcopy(donor['m_gridComponents'])
assert {a['m_elementID'] for a in donor_slots}=={'HomeTeamFormationAdaptive','AwayTeamFormationAdaptive','PlayerStatsHomeTeam','PlayerStatsAwayTeam','MatchViewer'}
stats_pids=[1730867061287688386,-2842495133054264931]
elementset_audits=[];available=set()
for name in ['HalfTimeTeamReportHumanGridElementSet','HalfTimeTeamReportGridElementSet']:
 ob=find(T,name);tree=ob.read_typetree();original=copy.deepcopy(tree)
 for pid in stats_pids:
  ref={'m_FileID':0,'m_PathID':pid}
  if ref not in tree['m_gridElementDescriptions']:tree['m_gridElementDescriptions'].append(ref)
  prior=-2396292803891594087 if pid==stats_pids[0] else -4364492723797385922
  group=next((g for g in tree['m_tileGroups'] if g['m_name']=={'GameID':45621}),None)
  if group is None:
   group={'m_name':{'GameID':45621},'m_tiles':[{'m_FileID':0,'m_PathID':p} for p in [-2396292803891594087,-4364492723797385922]]}
   tree['m_tileGroups'].insert(0,group)
  if ref not in group['m_tiles']:group['m_tiles'].append(ref)
 available.update(r['m_PathID'] for r in tree['m_gridElementDescriptions'])
 ob.save_typetree(tree);changes[T][ob.path_id]=tree
 elementset_audits.append({'name':name,'added_descriptors':stats_pids,'existing_choices_preserved':True})
config_audits=[]
for pid in sorted(available):
 ob=objs[T][pid];tree=ob.read_typetree();cfgs=tree.get(CK,[])
 if not cfgs or any(c['Size']=={'x':5,'y':4} for c in cfgs):continue
 choices=[c for c in cfgs if c['Size'] in [{'x':4,'y':6},{'x':4,'y':4},{'x':4,'y':2},{'x':5,'y':6},{'x':4,'y':8}]]
 if not choices:continue
 c=copy.deepcopy(choices[0]);c['Size']={'x':5,'y':4};cfgs.append(c)
 ob.save_typetree(tree);changes[T][pid]=tree
 config_audits.append({'name':tree['m_Name'],'new_size':[5,4],'asset_unchanged':c['AssetRef']['m_AssetGUID']})
versions={};layout_audits=[];target_layouts={}
def check_grid(tree):
 cells=set()
 for a in tree['m_gridComponents']:
  q=a['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<20 and 0<=y<10 and (x,y) not in cells,(tree['m_Name'],x,y)
    cells.add((x,y))
 assert len(cells)==200
for name in names:
 ob=find(T,name);old=ob.read_typetree();tree=copy.deepcopy(old)
 header=copy.deepcopy(next(a for a in old['m_gridComponents'] if a['m_elementID']=='MatchResult'))
 assert header['m_location']=={'x':0,'y':0,'width':20,'height':2}
 slots=copy.deepcopy(donor_slots)
 for a in slots:a['m_location']['y']+=2
 tree['m_gridComponents']=[header]+slots
 # Optional slices are additional instantiated cards, not the selector's available choices.
 for k,v in tree['m_optionalSlices'].items():
  if isinstance(v,list) and k!='m_instantiationOrder':tree['m_optionalSlices'][k]=[]
 for a in slots:
  if not any(p['m_elementID']==a['m_elementID'] for p in tree['m_placementBindings']):
   tree['m_placementBindings'].append({'m_elementID':a['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]})
 tree['m_compositionVersion']=old['m_compositionVersion']+1
 check_grid(tree);assert tree['m_gridComponents'][0]==header
 for a in slots:
  for cfg in a['m_gridElementConfigs']:
   desc=changes[T].get(cfg['Description']['m_PathID'],objs[T][cfg['Description']['m_PathID']].read_typetree())
   assert cfg in desc[CK],('Missing size config',a['m_elementID'])
 ob.save_typetree(tree);changes[T][ob.path_id]=tree;target_layouts[name]=tree
 versions[name]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}
 layout_audits.append({'name':name,'slots':[{k:a[k] for k in ['m_elementID','m_location']} for a in tree['m_gridComponents']],'score_header_exactly_preserved':True})

report_doc=Doc(M,name='HalfTimeTeamReport');old=copy.deepcopy(report_doc.d);rr=refs(old)
overview=Doc(M,name='OverviewPrototype')
source_groups=[x['data']['GridCompositionSets'] for x in overview.r.values() if 'GridCompositionSets' in x.get('data',{})][0]
source_bindings=source_groups[0]['m_gridCompositionSetBindings']['m_gridElementBindingData']
stats_bindings=[copy.deepcopy(x) for x in source_bindings if x['DescriptionAndMapping']['DescriptionName'] in ['PlayerStatsHomeTeam','PlayerStatsAwayTeam']]
assert len(stats_bindings)==10
for x in stats_bindings:
 if x['DescriptionAndMapping']['MappingName']=='ishometeam':
  x['BindingPath']['m_path']='const.True' if x['DescriptionAndMapping']['DescriptionName']=='PlayerStatsHomeTeam' else 'const.False'
groups=report_doc.r[1008]['data']['GridCompositionSets']
for group in groups:
 bindings=group['m_gridCompositionSetBindings']['m_gridElementBindingData']
 assert not any(x['DescriptionAndMapping']['DescriptionName'] in ['PlayerStatsHomeTeam','PlayerStatsAwayTeam'] for x in bindings)
 bindings.extend(copy.deepcopy(stats_bindings))
for rid,record in rr.items():
 expected=copy.deepcopy(record)
 if rid==1008:
  for group in expected['data']['GridCompositionSets']:group['m_gridCompositionSetBindings']['m_gridElementBindingData'].extend(copy.deepcopy(stats_bindings))
 assert report_doc.r[rid]==expected,('Unrelated report change',rid)
report_doc.save()

migration_code='import copy\nTARGETS='+repr(target_layouts)+'''
def migrate_layout(document,forward=True,version=None,limits_from=None):
 if not forward:
  assert limits_from is not None,'Original cache backup required'
  return copy.deepcopy(limits_from)
 name=document['m_Name'];assert name in TARGETS
 target=TARGETS[name];result=copy.deepcopy(document)
 result['m_gridComponents']=copy.deepcopy(target['m_gridComponents'])
 for a in result['m_gridComponents']:
  a['m_configDescriptionKeys']=[a['m_elementID']]
  a['m_configDescriptions']=[];a['m_gridElementConfigs']=[]
 result['m_optionalSlices']=copy.deepcopy(target['m_optionalSlices'])
 result['m_placementBindings']=copy.deepcopy(target['m_placementBindings'])
 result['m_compositionVersion']=version if version is not None else target['m_compositionVersion']
 return result
'''
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
migration=types.ModuleType('halftime_migration');exec(migration_code,migration.__dict__)
previews=[]
for name,ver in versions.items():
 p=cache_root/name
 if not p.exists():continue
 document=json.loads(p.read_text('utf8'));updated=migration.migrate_layout(document,version=ver['after'])
 check_grid(updated);assert migration.migrate_layout(updated,False,limits_from=document)==document
 previews.append(name)
 (OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')
outputs={}
for n in NAMES:
 data=env[n].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
 assert set(saved)==set(objs[n])
 for pid,h in hashes[n].items():
  if pid not in changes[n]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',n,pid)
 for pid,tree in changes[n].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',n,pid)
 for doc in [d for d in documents if d.n==n]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 outputs[n]=data;(OUT/n).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
report={'columns':[5,10,5],'sides_upper_lower':[4,4],'header':[20,2],'body':[20,8],'layouts':layout_audits,'added_size_configs':config_audits,'element_sets':elementset_audits,'halftime_stats_bindings':stats_bindings,'all_current_global_templates_unchanged':True,'highlight_layouts_and_cache_unchanged':True,'original_selector_choices_retained':True,'cache_previews':previews,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):tree.get('m_Name','') for pid,tree in ps.items()} for n,ps in changes.items()},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
(OUT/'installer.py').write_bytes((R/'install-highlight-layout-with-cache.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('中场报告两套桌面大屏布局：顶部20x2比分槽完全保留；下方改为20x8、5:10:5，侧栏上下4:4，中间10x8。复用当前Highlight私有横向主客队阵型、21px行高/70%字号球员统计及当前MatchViewer全部图表。移除原额外常驻卡片和可选扩展切片，保留选择器模块目录并补齐5x4尺寸；添加主客队统计条目和明确主客队绑定。现有Highlight、全局私有模板、手机、小屏及赛后布局不变。若存在对应中场自定义缓存，仅重排这两份并备份，恢复脚本还原备份。序列化回读、完整200格覆盖、顶部比分槽/其他对象/绑定检查通过；游戏内显示和操作未验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'changed_object_counts':{n:len(ps) for n,ps in changes.items()},'added_size_configs':len(config_audits),'cache_previews':previews,'roundtrip':True,'runtime_verified':False},ensure_ascii=False),flush=True)
