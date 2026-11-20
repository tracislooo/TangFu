from pathlib import Path
import json,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','portal-overview-left-halves-').replace('NAMES=[W,G,M,F]','NAMES=[T]')
exec(compile(boot,'backup-current-portal-layouts','exec'))
CK='<Configurations>k__BackingField'
tile_set=find(T,'PortalTileSet').read_typetree()
config_audits=[]
for ptr in tile_set['m_gridElementDescriptions']:
 ob=objs[T][ptr['m_PathID']];tree=ob.read_typetree();cfgs=tree[CK]
 if any(c['Size']=={'x':6,'y':5} for c in cfgs):continue
 ident=tree['<ID>k__BackingField']
 sizes=[(6,10),(6,8)] if ident=='Messages' else [(6,4),(4,4),(6,6),(4,6),(8,4)]
 source=next((c for size in sizes for c in cfgs if c['Size']==dict(zip(['x','y'],size))),None)
 if source is None:continue
 old=copy.deepcopy(tree);c=copy.deepcopy(source);c['Size']={'x':6,'y':5};cfgs.append(c)
 assert cfgs[:-1]==old[CK]
 ob.save_typetree(tree);changes[T][ob.path_id]=tree
 config_audits.append({'description':tree['m_Name'],'source_size':source['Size'],'new_size':c['Size'],'asset':c['AssetRef']})

def configs(slot,w,h):
 result=[]
 for ref in slot['m_configDescriptions']:
  pid=ref['m_PathID'];tree=changes[T].get(pid) or objs[T][pid].read_typetree()
  result.extend(copy.deepcopy(c) for c in tree[CK] if c['Size']=={'x':w,'y':h})
 assert result,('Missing configuration',slot['m_elementID'],w,h)
 return result

def resize(slot,x,y,w,h):
 slot['m_location']={'x':x,'y':y,'width':w,'height':h}
 slot['m_minSize']={'x':w,'y':h};slot['m_maxSize']={'x':w,'y':h}
 slot['m_gridElementConfigs']=configs(slot,w,h)

targets={};versions={};audits=[]
for size in ['Large','Medium','Small']:
 for suffix in ['', '-FMC']:
  name='Portal-'+size+suffix;ob=find(T,name);old=ob.read_typetree();tree=copy.deepcopy(old)
  messages=next(c for c in tree['m_gridComponents'] if c['m_elementID']=='Messages')
  report=next(c for c in tree['m_gridComponents'] if c['m_elementID']=='ClubTeamReport')
  w=6 if size=='Large' else 4;h=5 if size=='Large' else 4
  assert messages['m_location']=={'x':0,'y':0,'width':w,'height':h*2}
  resize(messages,0,0,w,h)
  added=copy.deepcopy(report);resize(added,0,h,w,h)
  tree['m_gridComponents'].append(added)
  tree['m_compositionVersion']+=1
  assert tree['m_gridComponents'][:-1]==[messages if c['m_elementID']=='Messages' else c for c in old['m_gridComponents']]
  original_cells=set();new_cells=set()
  for cs,dest in [(old['m_gridComponents'],original_cells),(tree['m_gridComponents'],new_cells)]:
   for a in cs:
    q=a['m_location']
    for x in range(q['x'],q['x']+q['width']):
     for y in range(q['y'],q['y']+q['height']):
      assert (x,y) not in dest,(name,x,y)
      dest.add((x,y))
  assert original_cells==new_cells
  expected=copy.deepcopy(old)
  for k in ['m_gridComponents','m_compositionVersion']:expected[k]=copy.deepcopy(tree[k])
  assert expected==tree
  ob.save_typetree(tree);changes[T][ob.path_id]=tree;targets[name]=tree
  versions[name]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}
  audits.append({'name':name,'left_width':w,'half_height':h,'source_slot':report['m_location'],'new_slot':added['m_location'],'other_slots_preserved':True})

migration_code='import copy\nTARGETS='+repr(targets)+'''
def migrate_layout(document,forward=True,version=None,limits_from=None):
 if not forward:
  assert limits_from is not None,'Original cache backup required'
  return copy.deepcopy(limits_from)
 result=copy.deepcopy(document);target=TARGETS[document['m_Name']]
 left=[c for c in target['m_gridComponents'] if c['m_location']['x']==0]
 assert len(left)==2
 top=copy.deepcopy(next(c for c in left if c['m_location']['y']==0))
 bottom=copy.deepcopy(next(c for c in left if c['m_location']['y']>0))
 width=top['m_location']['width'];half=top['m_location']['height']
 blocks=copy.deepcopy(document['m_gridComponents'])
 outside=[c for c in blocks if c['m_location']['x']>=width]
 existing_bottom=next((c for c in blocks if c['m_location']['x']==0 and c['m_location']['y']==half),None)
 if existing_bottom is not None:
  bottom=copy.deepcopy(existing_bottom)
  for k in ['m_location','m_minSize','m_maxSize']:bottom[k]=copy.deepcopy(left[-1][k])
 for slot in [top,bottom]:
  slot['m_configDescriptions']=[];slot['m_gridElementConfigs']=[]
  slot['m_configDescriptionKeys']=[slot['m_elementID']]
 result['m_gridComponents']=outside+[top,bottom]
 result['m_compositionVersion']=version if version is not None else target['m_compositionVersion']
 return result
'''
migration=types.ModuleType('portal_migration');exec(migration_code,migration.__dict__)
for name,target in targets.items():
 synthetic=copy.deepcopy(target)
 w=6 if 'Large' in name else 4;h=5 if 'Large' in name else 4
 left=[c for c in synthetic['m_gridComponents'] if c['m_location']['x']==0]
 synthetic['m_gridComponents'].remove(left[-1]);top=left[0]
 top['m_location']['height']=h*2;top['m_minSize']['y']=h*2;top['m_maxSize']['y']=h*2
 outside=[c for c in synthetic['m_gridComponents'] if c['m_location']['x']>=w]
 outside[0]['m_elementID']='DataHub';outside[0]['m_configDescriptionKeys']=['DataHub']
 result=migration.migrate_layout(synthetic)
 assert [c for c in result['m_gridComponents'] if c['m_location']['x']>=w]==outside
 assert result['m_optionalSlices']==synthetic['m_optionalSlices']
 bottom=result['m_gridComponents'][-1];bottom['m_elementID']='FixtureSchedule'
 bottom['m_configDescriptionKeys']=['FixtureSchedule']
 repeated=migration.migrate_layout(result)
 assert repeated==result
 assert migration.migrate_layout(result,False,limits_from=synthetic)==synthetic

cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
previews=[]
for name in targets:
 p=cache_root/name
 if p.exists():
  original=json.loads(p.read_text('utf8'));updated=migration.migrate_layout(original)
  (OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8');previews.append(name)

data=env[T].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects}
assert set(saved)==set(objs[T])
for pid,h in hashes[T].items():
 if pid not in changes[T]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',pid)
for pid,tree in changes[T].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',pid)
for name,tree in targets.items():
 for a in tree['m_gridComponents']:
  if a['m_location']['x']!=0:continue
  for c in a['m_gridElementConfigs']:assert c in saved[c['Description']['m_PathID']].read_typetree()[CK],(name,a['m_elementID'],c)
(OUT/T).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
report={'layouts':audits,'new_size_configs':config_audits,'cache_migration_preserves_other_slots':True,'cache_migration_idempotent_and_preserves_lower_selection':True,'all_grid_cells_preserved_without_overlap':True,'phone_and_other_resources_preserved':True,'portrait3x_resource_preserved':True,'serialization_roundtrip':True,'runtime_verified':False,'cache_previews':previews}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{T:{str(pid):tree.get('m_Name','') for pid,tree in changes[T].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{T:sha(data)},'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[T],'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
(OUT/'installer.py').write_bytes((R/'install-highlight-layout-with-cache.py').read_bytes())
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('Portal-overview 六套桌面布局左侧上下各50%，Large为6×5两块，Medium/Small为4×4两块。上方收件箱，下方复制球队报告并保留原生选择器；共享模块按独立坐标放置，与游戏原生重复模块机制一致。补充兼容模块6×5尺寸配置，原尺寸配置不改。中间、右侧、手机、其他页面与三倍头像资源保持原样。已有对应缓存仅迁移左侧；无关槽位及其选择保留。静态网格、回读、无关对象和缓存迁移验证通过；游戏内显示、选择器交互及重新进入后的保存行为未验证。restore.ps1恢复本次资源及有备份的对应缓存。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'layouts':len(targets),'new_size_configs':len(config_audits),'changed_objects':len(changes[T]),'cache_previews':previews,'runtime_verified':False},ensure_ascii=False),flush=True)
