from pathlib import Path
import json,copy,ast,struct,uuid,hashlib,importlib.util
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0]
prefix=prefix.replace('bench-cards-centered-no-face-number-','summary-horizontal-formations-').replace("'NAMES=[W,G]'","'NAMES=[G,T]'").replace('bases=(W,G)','bases=(G,T)').replace('datetime.timedelta(hours=-6)','datetime.timedelta(hours=-7)')
exec(compile(prefix,'backup-latest-game-and-skin-separately','exec'))
spec=importlib.util.spec_from_file_location('summary_catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
CK='<Configurations>k__BackingField'
REPORT_PREFIXES=('HalfTimeTeamReport','FullTimeTeamReport','PastMatchTeamReport')
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))
reserved_ids={int(a['path_id']) for a in reserved['reserved_textures']}
reserved_names={a['name'] for a in reserved['reserved_textures']}
tx=[];audits=[];asset_clones=[];cache_maps={}
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
cache_before={p:p.read_bytes() for p in cache_root.iterdir() if p.is_file()} if cache_root.exists() else {}

def tree(bn,pid):return copy.deepcopy(changes[bn].get(pid,objs[bn][pid].read_typetree()))

def save(bn,pid,tr):
 objs[bn][pid].save_typetree(tr);changes[bn][pid]=copy.deepcopy(tr)

def asset_guid(bn,pid):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
 return next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==pid)

def clone_asset(bn,source,pid,name,tr):
 assert pid not in objs[bn] and pid not in reserved_ids and name not in reserved_names
 ob=copy.copy(source);ob.path_id=pid;ob.data=None;ob._read_until=None
 ob.assets_file.objects[pid]=ob;objs[bn][pid]=ob
 tr=copy.deepcopy(tr);tr['m_Name']=name;save(bn,pid,tr)
 return ob,tr

def ptrs(value,out):
 if isinstance(value,dict):
  if set(value)=={'m_FileID','m_PathID'} and value['m_PathID'] and value not in out:out.append(copy.deepcopy(value))
  else:
   for x in value.values():ptrs(x,out)
 elif isinstance(value,list):
  for x in value:ptrs(x,out)

def replace_report_refs(value,pidmap,guidmap):
 if isinstance(value,dict):
  if set(value)=={'m_FileID','m_PathID'} and value['m_FileID']==0 and value['m_PathID'] in pidmap:
   value['m_PathID']=pidmap[value['m_PathID']]
  elif 'm_AssetGUID' in value and value['m_AssetGUID'] in guidmap:value['m_AssetGUID']=guidmap[value['m_AssetGUID']]
  else:
   for x in value.values():replace_report_refs(x,pidmap,guidmap)
 elif isinstance(value,list):
  for x in value:replace_report_refs(x,pidmap,guidmap)

for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G,T=[base+suffix for base in bases]
 pidmap={};guidmap={};private=[];panel_audits=[]
 for index,side in enumerate(['Home','Away']):
  source=Doc(G,name='Highlight'+side+'HorizontalFormation')
  name='Summary'+side+'HorizontalFormation';pid=-981111000030000-index*10
  original=copy.deepcopy(source.d);d=copy.deepcopy(original);s=copy.deepcopy(source.s)
  d['inlineSheet']={'m_FileID':0,'m_PathID':pid-1}
  ob,d=clone_asset(G,source.obj,pid,name,d)
  _,s=clone_asset(G,objs[G][source.sid],pid-1,name+'_Style',s)
  doc=Doc(G,pid=pid,tree=d,style=s);panels=[]
  for i,r in doc.r.items():
   if r.get('data',{}).get('m_FullTypeName')!='FM.UI.FMTacticsPanel':continue
   doc.data(i).update(Orientation=1,Orientation_UxmlAttributeFlags=1,FlipPositions=1 if side=='Home' else 0,FlipPositions_UxmlAttributeFlags=1)
   panels.append(i)
  assert len(panels)==4,(tag,side,panels)
  expected=copy.deepcopy(original);expected['m_Name']=name;expected['inlineSheet']={'m_FileID':0,'m_PathID':pid-1}
  er=refs(expected)
  for i in panels:sd(er,i).update(Orientation=1,Orientation_UxmlAttributeFlags=1,FlipPositions=1 if side=='Home' else 0,FlipPositions_UxmlAttributeFlags=1)
  assert doc.d==expected,'Only formation direction may change in the private copy'
  assert doc.s==dict(source.s,m_Name=name+'_Style')
  doc.save()
  guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/summary-horizontal/'+name).hex
  oldguid=asset_guid(G,source.obj.path_id);guidmap[oldguid]=guid
  private.append({'bundle':G,'pid':pid,'style':pid-1,'guid':guid,'source_guid':oldguid,'name':name,'kind':'VisualTreeAsset'})
  desc=find(T,side+'TeamFormationAdaptiveBlockDescription');dt=tree(T,desc.path_id)
  descpid=-981111000030020-index;descname=name+'Description'
  for c in dt[CK]:
   assert c['Description']=={'m_FileID':0,'m_PathID':desc.path_id}
   assert c['AssetRef']['m_AssetGUID']==oldguid
   c['Description']['m_PathID']=descpid;c['AssetRef']['m_AssetGUID']=guid
  _,dt=clone_asset(T,desc,descpid,descname,dt)
  descguid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27/summary-horizontal/'+descname).hex
  private.append({'bundle':T,'pid':descpid,'guid':descguid,'source_guid':asset_guid(T,desc.path_id),'name':descname,'kind':'GridElementDescription'})
  pidmap[desc.path_id]=descpid
  panel_audits.append({'side':side,'source':source.d['m_Name'],'private_template':name,'guid':guid,'panels':panels,'orientation':1,'flip':1 if side=='Home' else 0,'all_bindings_events_and_styles_preserved':True})
 report_assets=[];layouts=[]
 for ob in list(objs[T].values()):
  if ob.type.name!='MonoBehaviour':continue
  name=ob.peek_name()
  if not name.startswith(REPORT_PREFIXES):continue
  original=tree(T,ob.path_id);updated=copy.deepcopy(original)
  replace_report_refs(updated,pidmap,guidmap)
  if updated==original:continue
  assert 'm_gridComponents' in original or 'm_gridElementDescriptions' in original,(name,'Unexpected report asset')
  if 'm_gridComponents' in original:
   assert updated.keys()==original.keys()
   for before_block,after_block in zip(original['m_gridComponents'],updated['m_gridComponents']):
    assert before_block['m_location']==after_block['m_location']
    assert before_block['m_elementID']==after_block['m_elementID']
   layouts.append(name)
  save(T,ob.path_id,updated);report_assets.append(name)
 assert len(layouts)==6,(tag,layouts)
 assert len(report_assets)==11,(tag,report_assets)
 for name in layouts:
  layout=tree(T,find(T,name).path_id)
  reg=tree(T,layout['m_gridElementSet']['m_PathID'])
  available={p['m_PathID'] for p in reg['m_gridElementDescriptions']}
  assert set(pidmap.values())<=available
  for b in layout['m_gridComponents']:
   for cfg in b['m_gridElementConfigs']:
    descpid=cfg['Description']['m_PathID']
    if descpid in pidmap.values():assert cfg in tree(T,descpid)[CK]
 if tag=='game':cache_maps={name:(pidmap.copy(),guidmap.copy()) for name in layouts}
 for bn in [G,T]:
  mo=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=mo.read_typetree()
  for a in private:
   if a['bundle']==bn:meta['m_Container'].append((a['guid'],{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':a['pid']}}))
  for key,entry in meta['m_Container']:
   pid=entry['asset']['m_PathID']
   if pid not in changes[bn]:continue
   span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span)
   if bn==G and pid-1 in changes[bn]:ptrs(changes[bn][pid-1],span)
   entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
  meta['m_Container'].sort(key=lambda x:x[0]);save(bn,mo.path_id,meta)
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';raw=before[cp]
 original_cat=cm.Catalog(raw);original_locations={p[0]:original_cat.location(p[0]) for _,ls in original_cat.key_records for p in original_cat.array(ls,'I')}
 for a in private:
  cat=cm.Catalog(raw);loc=cat.locations(a['source_guid'])[0]
  raw=cat.add_key_location(a['guid'],loc,loc)
 cat=cm.Catalog(raw);idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload')
 ko,ls=cat.key_records[idx];existing=[v[0] for v in cat.array(ls,'I')]
 extra=[cat.locations(a['guid'])[0] for a in private if a['bundle']==G]
 records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',v) for v in existing+extra),True))
 struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True))
 catalog=bytes(cat.data);verify=cm.Catalog(catalog)
 for p,loc in original_locations.items():assert verify.location(p)==loc,('Existing catalog location changed',p)
 for a in private:
  loc=verify.location(verify.locations(a['guid'])[0]);assert a['bundle'].split('::')[0] in verify.location(loc['dependencies'][0])['internal']
  assert loc['type']==original_cat.location(original_cat.locations(a['source_guid'])[0])['type']
  assert loc['dependencies']==original_cat.location(original_cat.locations(a['source_guid'])[0])['dependencies']
  if a['bundle']==G:
   assert loc['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'
   assert loc['offset'] in [v[0] for v in verify.array(verify.key_records[idx][1],'I')]
 asset_clones.extend(private)
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
  assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',bn,pid)
  for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr,('Serialization mismatch',bn,pid)
  for doc in [d for d in documents if d.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
  src=OUT/(('skin-' if suffix else '')+base);src.write_bytes(raw);target=folder/base
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
 for name,data in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode('ascii'))]:
  target=GAME.parent/name if tag=='game' else SKIN/name;src=OUT/(tag+'-'+name);src.write_bytes(data)
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[target]),'after':sha(data)})
 audits.append({'variant':tag,'formations':panel_audits,'report_assets_changed':report_assets,'summary_layouts':layouts,'original_match_templates_descriptors_and_layouts_byte_identical':True,'grid_geometry_and_bindings_unchanged':True,'catalog_types_owner_first_dependencies_and_actual_global_preload_verified':True})
for p,b in before.items():assert p.read_bytes()==b,('Concurrent resource modification',p)
for p,h in protected.items():assert sha(p.read_bytes())==h,('Protected resource modified',p)
cache_changed=[]
for p,original in cache_before.items():
 if p.name not in cache_maps:continue
 d=json.loads(original);updated=copy.deepcopy(d);pidmap,guidmap=cache_maps[p.name]
 replace_report_refs(updated,pidmap,guidmap)
 if d==updated:continue
 data=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
 backup=OUT/'backup-cache'/p.name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(original)
 src=OUT/('cache-'+p.name);src.write_bytes(data)
 tx.append({'target':str(p),'source':str(src),'backup':str(backup),'before':sha(original),'after':sha(data)})
 cache_changed.append(str(p))
for p,b in cache_before.items():assert p.read_bytes()==b
manifest={'installed':False,'runtime_verified':False,'source_script':str(Path(__file__)),'checks':audits,'new_assets':asset_clones,'serialization_roundtrip':True,'unrelated_objects_identical':True,'cache_migrations':cache_changed,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if cache_changed:installer=installer.replace('for row in tx:\n',"allowed.add(Path("+repr(str(cache_root))+").resolve())\nfor row in tx:\n",1)
installer+="\nstate=json.loads((out/'summary-state.json').read_text('utf8'))\nstate.update(status='restored' if restore else 'installed',installed_files=len(tx),runtime_verified=False)\n(out.parent/'current-summary-formations.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')\n"
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'修改说明.md').write_text('中场、赛后及赛后回看总结左右阵型使用专用横向模板，直播/历史和有球/无球四个分支均使用Orientation=1，主队门将在左、客队门将在右。复制当前模板和描述，保留描述逻辑ID、全部数据绑定/事件/样式和网格尺寸，仅在总结页的五份资源集合和六份布局中替换引用。比赛Highlight的模板、描述、集合、布局及缓存保持。游戏与独立皮肤分别以最新资源生成，目录类型、所属包首项依赖和Global实际预加载校验通过，所有无关对象字节一致。restore.ps1带哈希保护；未启动游戏，实际显示待确认。','utf8')
state={'status':'prepared','date':'2026-11-11','patch':str(OUT),'source_script':str(Path(__file__)),'restore':str(OUT/'restore.ps1'),'game_root':str(GAME.parents[3]),'summary_orientation':1,'match_formation_resources_unchanged':True,'runtime_verified':False}
(OUT/'summary-state.json').write_text(json.dumps(state,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'resource_files':len(tx),'summary_layouts_each_variant':6,'runtime_verified':False},ensure_ascii=False),flush=True)
