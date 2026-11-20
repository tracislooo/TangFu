from pathlib import Path
import json,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','portal-4-12-4-left-two-tiles-').replace('NAMES=[W,G,M,F]','NAMES=[W,T]')
exec(compile(boot,'backup-current-portal-resources','exec'))
CK='<Configurations>k__BackingField';REMOVED='PortalLeftSelector13'
ts=find(T,'PortalTileSet');oldset=ts.read_typetree();newset=copy.deepcopy(oldset)
newset['m_gridElementDescriptions']=[p for p in newset['m_gridElementDescriptions'] if objs[T][p['m_PathID']].read_typetree()['<ID>k__BackingField']!=REMOVED]
assert len(newset['m_gridElementDescriptions'])==len(oldset['m_gridElementDescriptions'])-1
ts.save_typetree(newset);changes[T][ts.path_id]=newset
descs={}
for p in newset['m_gridElementDescriptions']:
 ob=objs[T][p['m_PathID']];tree=ob.read_typetree();descs[tree['<ID>k__BackingField']]=(ob,tree)
messages,md=descs['Messages'];oldmd=copy.deepcopy(md)
if not any(c['Size']=={'x':4,'y':6} for c in md[CK]):
 c=copy.deepcopy(next(c for c in md[CK] if c['Size']=={'x':4,'y':4}));c['Size']={'x':4,'y':6};md[CK].append(c)
 assert md[CK][:-1]==oldmd[CK]
 messages.save_typetree(md);changes[T][messages.path_id]=md
def config(ident,w,h):return copy.deepcopy(next(c for c in descs[ident][1][CK] if c['Size']=={'x':w,'y':h}))
def set_content(slot,ident,w,h):
 slot.update(m_elementID=ident,m_configDescriptions=[{'m_FileID':0,'m_PathID':descs[ident][0].path_id}],m_configDescriptionKeys=[],m_gridElementConfigs=[config(ident,w,h)],m_isLocked=0,m_isDynamic=0,m_takesFocus=0)
 slot['m_minSize']={'x':w,'y':h};slot['m_maxSize']={'x':w,'y':h}

page=Doc(W,name='PortalScreen');page_before=copy.deepcopy(page.d)
for group in page.data(1028)['GridCompositionSets']:
 b=group['m_gridCompositionSetBindings'];b['m_gridElementBindingData']=[v for v in b['m_gridElementBindingData'] if v['DescriptionAndMapping']['DescriptionName']!=REMOVED]
assert page.d!=page_before
page.save()

targets={};versions={};audits=[]
for size in ['Large','Medium','Small']:
 for suffix in ['', '-FMC']:
  name='Portal-'+size+suffix;ob=find(T,name);old=ob.read_typetree();tree=copy.deepcopy(old)
  original_left=next(c for c in old['m_gridComponents'] if c['m_location']['x']==0 and c['m_location']['y']>0)
  assert original_left['m_elementID']==REMOVED
  tree['m_gridComponents']=[c for c in tree['m_gridComponents'] if c['m_elementID']!=REMOVED]
  inbox=next(c for c in tree['m_gridComponents'] if c['m_elementID']=='Messages')
  old_inbox=next(c for c in old['m_gridComponents'] if c['m_elementID']=='Messages')
  total_height=10 if size=='Large' else 8;inbox_height=total_height-4
  set_content(inbox,'Messages',4,inbox_height);inbox['m_location']={'x':0,'y':0,'width':4,'height':inbox_height}
  if size=='Large':
   center=next(c for c in tree['m_gridComponents'] if c['m_elementID']=='PortalAdaptiveContent')
   assert center['m_location']=={'x':6,'y':0,'width':10,'height':10}
   center['m_location']={'x':4,'y':0,'width':12,'height':10}
  donor=next(c for c in old['m_gridComponents'] if c['m_elementID']=='ClubTeamReport' and c['m_location']['x']>0)
  for ident,y in [('ClubTeamReport',inbox_height),('DataHub',inbox_height+2)]:
   slot=copy.deepcopy(donor);set_content(slot,ident,4,2);slot['m_location']={'x':0,'y':y,'width':4,'height':2};tree['m_gridComponents'].append(slot)
  tree['m_placementBindings']=[v for v in tree['m_placementBindings'] if v['m_elementID']!=REMOVED]
  for ident in ['ClubTeamReport','DataHub']:
   if not any(v['m_elementID']==ident for v in tree['m_placementBindings']):tree['m_placementBindings'].append({'m_elementID':ident,'m_optionalConditions':[],'m_optionalConfigConditions':[]})
  tree['m_compositionVersion']+=1
  old_right=[c for c in old['m_gridComponents'] if c['m_location']['x']>=(16 if size=='Large' else 12 if size=='Medium' else 8)]
  for c in old_right:assert c in tree['m_gridComponents']
  if size!='Large':
   for c in old['m_gridComponents']:
    if c['m_location']['x']>0:assert c in tree['m_gridComponents']
  cells=set()
  width=20 if size=='Large' else 16 if size=='Medium' else 12
  for slot in tree['m_gridComponents']:
   q=slot['m_location']
   for x in range(q['x'],q['x']+q['width']):
    for y in range(q['y'],q['y']+q['height']):
     assert 0<=x<width and 0<=y<total_height and (x,y) not in cells,(name,x,y)
     cells.add((x,y))
  assert len(cells)==width*total_height
  ob.save_typetree(tree);changes[T][ob.path_id]=tree;targets[name]=tree;versions[name]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}
  audits.append({'name':name,'columns':[4,12,4] if size=='Large' else [4,8,4] if size=='Medium' else [4,4,4],'left_heights':[inbox_height,2,2],'left_defaults':['Messages','ClubTeamReport','DataHub'],'right_slots_preserved':True,'complete_grid_without_overlap':True})

migration_code='import copy\nTARGETS='+repr(targets)+'''
def migrate_layout(document,forward=True,version=None,limits_from=None,layout_name=None):
 if not forward:
  assert limits_from is not None,'Original cache backup required'
  return copy.deepcopy(limits_from)
 result=copy.deepcopy(document);name=layout_name or document['m_Name'];target=TARGETS[name]
 large='Large' in name;old_width=6 if large else 4
 prior=document['m_gridComponents'];blocks=[]
 for original in prior:
  q=original['m_location']
  if q['x']==0:continue
  slot=copy.deepcopy(original)
  if large and q['x'] in [4,6]:slot['m_location']={'x':4,'y':0,'width':12,'height':10}
  blocks.append(slot)
 for native in target['m_gridComponents']:
  q=native['m_location']
  if q['x']!=0:continue
  slot=copy.deepcopy(native)
  slot['m_configDescriptions']=[];slot['m_gridElementConfigs']=[];slot['m_configDescriptionKeys']=[slot['m_elementID']]
  blocks.append(slot)
 result['m_gridComponents']=blocks
 result['m_compositionVersion']=version if version is not None else target['m_compositionVersion']
 result['m_placementBindings']=copy.deepcopy(target['m_placementBindings'])
 return result
'''
migration=types.ModuleType('portal_cache');exec(migration_code,migration.__dict__)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');previews=[]
for name,target in targets.items():
 synthetic=copy.deepcopy(target);result=migration.migrate_layout(synthetic,layout_name=name)
 assert migration.migrate_layout(result,layout_name=name)==result
 p=cache_root/name
 if not p.exists():continue
 original=json.loads(p.read_text('utf8'));updated=migration.migrate_layout(original,layout_name=name)
 for a in original['m_gridComponents']:
  if a['m_location']['x']>=(16 if 'Large' in name else 12 if 'Medium' in name else 8):assert a in updated['m_gridComponents']
 assert updated['m_optionalSlices']==original['m_optionalSlices']
 assert migration.migrate_layout(updated,False,limits_from=original)==original
 assert migration.migrate_layout(updated,layout_name=name)==updated
 previews.append(name);(OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')

outputs={}
for bn in [W,T]:
 data=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',bn,pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',bn,pid)
 for doc in documents:
  if doc.n==bn:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 (OUT/bn).write_bytes(data);outputs[bn]=data
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for p,b in before.items():
 if p.name.startswith('catalog.'):protected[p]=sha(b)
report={'layouts':audits,'nested_selector_removed_from_page_and_menu':True,'portrait3x_preserved':True,'cache_previews':previews,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{bn:{str(pid):t.get('m_Name','') for pid,t in changes[bn].items()} for bn in [W,T]},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{bn:sha(data) for bn,data in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
installer=(R/'install-highlight-layout-with-cache.py').read_text('utf8').replace("version=versions['before' if restore else 'after'],limits_from=old_limits)","version=versions['before' if restore else 'after'],limits_from=old_limits,layout_name=name)")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('Portal-overview Large/FMC列宽改为4:12:4，左列收件箱4×6，下方球队报告4×2、数据中心4×2。Medium/Small/FMC维持响应式列宽，左列4×4收件箱下添加相同两块4×2模块。移除页面左下13项独立选择器及其外层菜单登记，改回原生模块选择器。右侧槽位及已有选择保留；缓存仅调整左侧和Large中间列几何位置。三倍消息头像、手机、目录与其他资源保持。资源回读、网格全覆盖及无关对象一致性通过，游戏内显示及选择器交互未验证。restore.ps1恢复本次资源和已有备份的Portal缓存。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'large_columns':[4,12,4],'large_left_heights':[6,2,2],'compact_left_heights':[4,2,2],'cache_previews':previews,'runtime_verified':False},ensure_ascii=False),flush=True)
