from pathlib import Path
import json,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','portal-restore-6-10-4-').replace('NAMES=[W,G,M,F]','NAMES=[T]')
exec(compile(boot,'backup-current-portal-layouts','exec'))
CK='<Configurations>k__BackingField';config_audits=[];descs={}
tile_set=find(T,'PortalTileSet').read_typetree()
for p in tile_set['m_gridElementDescriptions']:
 ob=objs[T][p['m_PathID']];d=ob.read_typetree();ident=d['<ID>k__BackingField'];descs[ident]=(ob,d)
 source=next((c for c in d[CK] if c['Size']=={'x':4,'y':2}),None)
 if source and not any(c['Size']=={'x':6,'y':2} for c in d[CK]):
  c=copy.deepcopy(source);c['Size']={'x':6,'y':2};d[CK].append(c)
  ob.save_typetree(d);changes[T][ob.path_id]=copy.deepcopy(d);config_audits.append(ident)
ob,d=descs['Messages']
if not any(c['Size']=={'x':6,'y':6} for c in d[CK]):
 c=copy.deepcopy(next(c for c in d[CK] if c['Size']=={'x':6,'y':8}));c['Size']={'x':6,'y':6};d[CK].append(c)
 ob.save_typetree(d);changes[T][ob.path_id]=copy.deepcopy(d)
targets={};versions={};audits=[]
for name in ['Portal-Large','Portal-Large-FMC']:
 ob=find(T,name);old=ob.read_typetree();tree=copy.deepcopy(old)
 for slot in tree['m_gridComponents']:
  q=slot['m_location'];ident=slot['m_elementID']
  if q['x']==0:
   assert q['width']==4
   q['width']=6
   for k in ['m_minSize','m_maxSize']:slot[k]['x']=6
   cfg=next(c for c in descs[ident][1][CK] if c['Size']=={'x':6,'y':q['height']})
   slot['m_gridElementConfigs']=[copy.deepcopy(cfg)]
  elif q['x']==4:
   assert q['width']==12;q['x']=6;q['width']=10
 tree['m_compositionVersion']+=1
 for a,b in zip(old['m_gridComponents'],tree['m_gridComponents']):
  assert a['m_elementID']==b['m_elementID']
  assert a['m_location']['y']==b['m_location']['y'] and a['m_location']['height']==b['m_location']['height']
  if a['m_location']['x']>=16:assert a==b
 cells=set()
 for slot in tree['m_gridComponents']:
  q=slot['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<20 and 0<=y<10 and (x,y) not in cells
    cells.add((x,y))
 assert len(cells)==200
 ob.save_typetree(tree);changes[T][ob.path_id]=tree;targets[name]=tree;versions[name]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}
 audits.append({'name':name,'columns':[6,10,4],'left_heights':[6,2,2],'all_module_ids_and_heights_preserved':True,'right_slots_unchanged':True,'complete_grid_no_overlap':True})
migration_code='import copy\nTARGETS='+repr(targets)+'''
def migrate_layout(document,forward=True,version=None,limits_from=None,layout_name=None):
 if not forward:
  assert limits_from is not None,'Original cache backup required'
  return copy.deepcopy(limits_from)
 result=copy.deepcopy(document);name=layout_name or result['m_Name']
 for slot in result['m_gridComponents']:
  q=slot['m_location']
  if q['x']==0:
   q['width']=6
   for k in ['m_minSize','m_maxSize']:slot[k]['x']=6
   slot['m_configDescriptions']=[];slot['m_gridElementConfigs']=[];slot['m_configDescriptionKeys']=[slot['m_elementID']]
  elif q['x'] in [4,6]:q['x']=6;q['width']=10
 result['m_compositionVersion']=version if version is not None else TARGETS[name]['m_compositionVersion']
 return result
'''
migration=types.ModuleType('portal_cache');exec(migration_code,migration.__dict__)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');previews=[]
for name,target in targets.items():
 result=migration.migrate_layout(target,layout_name=name);assert migration.migrate_layout(result,layout_name=name)==result
 p=cache_root/name
 if not p.exists():continue
 original=json.loads(p.read_text('utf8'));updated=migration.migrate_layout(original,layout_name=name)
 assert [c['m_elementID'] for c in original['m_gridComponents']]==[c['m_elementID'] for c in updated['m_gridComponents']]
 for a,b in zip(original['m_gridComponents'],updated['m_gridComponents']):
  if a['m_location']['x']>=16:assert a==b
 assert migration.migrate_layout(updated,layout_name=name)==updated
 assert migration.migrate_layout(updated,False,limits_from=original)==original
 previews.append(name);(OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')
data=env[T].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(objs[T])
for pid,h in hashes[T].items():
 if pid not in changes[T]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',pid)
for pid,tree in changes[T].items():assert saved[pid].read_typetree()==tree
(OUT/T).write_bytes(data)
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
report={'layouts':audits,'six_by_two_selection_configs':config_audits,'compact_phone_and_templates_preserved':True,'cache_previews':previews,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{T:{str(pid):t.get('m_Name','') for pid,t in changes[T].items()}},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{T:sha(data)},'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[T],'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
installer=(R/'install-highlight-layout-with-cache.py').read_text('utf8').replace("version=versions['before' if restore else 'after'],limits_from=old_limits)","version=versions['before' if restore else 'after'],limits_from=old_limits,layout_name=name)")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('Portal Large/FMC三列恢复6:10:4；左侧宽度6，中间10，右侧4。左侧内容与高度保持收件箱6、两块原生模块各2，原模块模板保持，通过6×2适配配置保留选择器候选。已有Portal-Large缓存只调宽度和中间起点，保留选择。中小屏、手机、其他布局与三倍头像不改。资源回读和200格完整覆盖校验通过，游戏内显示未验证。restore.ps1恢复本次修改。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'columns':[6,10,4],'cache_previews':previews,'runtime_verified':False},ensure_ascii=False),flush=True)
