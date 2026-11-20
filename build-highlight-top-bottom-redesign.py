from pathlib import Path
import json,copy,ast,struct,uuid,importlib.util,hashlib
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
source=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8')
prefix=source.split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-top-bottom-redesign-').replace("'NAMES=[W,G]'","'NAMES=[G,M,T]'").replace('bases=(W,G)','bases=(G,M,T)')
exec(compile(prefix,'backup-current-highlight','exec'))
# Additional references make the old Highlight independently reviewable.
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for name in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-tablefactories_assets_all.bundle','ui-tableviews_assets_all.bundle','ui-styles_assets_default.bundle']:
  p=folder/name
  if p.exists():(OUT/('backup-'+tag)/name).write_bytes(p.read_bytes())
for name in ['current-game-location.json','current-sidebar-version.json','current-custom-textures.json','reserved-texture-ids.json']:
 if (R/name).exists():(OUT/name).write_bytes((R/name).read_bytes())
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions')
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
cache_before={p:p.read_bytes() for name in layout_names for p in [cache_root/name] if p.exists()}
for p,b in cache_before.items():
 q=OUT/'backup-cache'/p.name;q.parent.mkdir(exist_ok=True);q.write_bytes(b)
(OUT/'backup-inventory.json').write_text(json.dumps({'files':{str(p.relative_to(OUT)):{'sha256':sha(p.read_bytes()),'bytes':p.stat().st_size} for p in OUT.glob('backup-*/*')},'custom_highlight_cache_files':[str(p) for p in cache_before]},ensure_ascii=False,indent=2),'utf8')
print('BACKUP '+str(OUT),flush=True)
# Read-only source plus private clones, never overwrite shared report templates.
helper=ast.parse((R/'build-highlight-five-column-native-player-lists.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['register_clone','clone_doc']],type_ignores=[]),'private-asset-helpers','exec'))
CK='<Configurations>k__BackingField';NONE={'m_ValueType':1,'valueIndex':3};AUTO={'m_ValueType':1,'valueIndex':2}
new_guids={};asset_clones=[];audits=[];cats={};cache_versions={};cache_defaults={};tx=[]
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'));reserved_ids={int(x['path_id']) for x in reserved['reserved_textures']}
spec=importlib.util.spec_from_file_location('redesign_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
def existing_tree(bn,pid):return copy.deepcopy(changes[bn].get(pid,objs[bn][pid].read_typetree()))
def asset_guid(bn,pid):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
 return next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==pid)
def erase(doc,i):
 for c in list(doc.a(i).get('m_Children',[])):erase(doc,c['rid'])
 a=doc.a(i);p=a['m_Parent']['rid'];sr=a.get('m_SerializedData',{}).get('rid');doc.a(p)['m_Children'].remove({'rid':i});ids={i,sr};doc.d['references']['RefIds']=[r for r in doc.d['references']['RefIds'] if r['rid'] not in ids]
 for j in ids:doc.r.pop(j,None)
def clear_edges(doc,i):doc.st(i,[(p,doc.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])
def allptr(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():allptr(x,out)
 elif isinstance(v,list):
  for x in v:allptr(x,out)
def clone_so(bn,pid,newpid,name,tree=None):
 ob=objs[bn][pid];tr=existing_tree(bn,pid) if tree is None else tree
 return register_clone(bn,ob,name,newpid,tr,source_guid=asset_guid(bn,pid))
def cfg_for(tree,w,h,asset=None):
 exact=next((c for c in tree[CK] if c['Size']=={'x':w,'y':h} and (asset is None or c['AssetRef']==asset)),None)
 if exact:return copy.deepcopy(exact)
 choices=tree[CK];best=min(choices,key=lambda c:(0 if asset is not None and c['AssetRef']==asset else 1,abs(c['Size']['x']-w)+abs(c['Size']['y']-h)))
 c=copy.deepcopy(best);c['Size']={'x':w,'y':h}
 if asset is not None:c['AssetRef']=copy.deepcopy(asset)
 return c
def assert_grid(tree):
 cells=set()
 for block in tree['m_gridComponents']:
  q=block['m_location'];assert q['width']>0 and q['height']>0
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):assert 0<=x<24 and 0<=y<10 and (x,y) not in cells;cells.add((x,y))
 assert len(cells)==240
for tag,suffix in [('game',''),('skin','::skin')]:
 G,M,T=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4');source_asset_guids={};vta_assets={}
 for index,side in enumerate(['Home','Away']):
  src=Doc(G,name='HighlightNative'+side+'OOPHorizontal');doc,guid=clone_doc(src,'HighlightRedesign'+side+'OOPVertical',-981104000010000-index*10)
  source_asset_guids[guid]=asset_guid(G,src.obj.path_id)
  for i,r in doc.r.items():
   if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMTacticsPanel':
    doc.data(i).update(Orientation=0,Orientation_UxmlAttributeFlags=1,FlipPositions=0,FlipPositions_UxmlAttributeFlags=1,FillAllAvailableSpace=0,FillAllAvailableSpace_UxmlAttributeFlags=1,UseParentRectForOutline=0,UseParentRectForOutline_UxmlAttributeFlags=1)
  doc.save();vta_assets[side]=guid
 center,guid=clone_doc(main,'HighlightRedesignPitchAndTwoCharts',-981104000010020);vta_assets['Center']=guid;source_asset_guids[guid]=asset_guid(G,main.obj.path_id)
 center.move(1022,1008,0);center.move(3121,1008,1)
 for c in list(center.a(1008)['m_Children']):
  if c['rid'] not in [1022,3121]:erase(center,c['rid'])
 for c in list(center.a(3121)['m_Children']):
  if c['rid'] not in [3123,3261]:erase(center,c['rid'])
 center.st(1008,[(131083,center.enum('column')),(131087,center.pct(100)),(131105,center.pct(100)),(131096,center.px(0)),(131084,center.num(1))]);clear_edges(center,1008)
 for i,grow in [(1022,2),(3121,1)]:
  center.st(i,[(131087,AUTO),(131096,center.px(0)),(131094,NONE),(131105,center.pct(100)),(131097,center.px(0)),(131095,NONE),(131082,center.px(0)),(131084,center.num(grow)),(131085,center.num(1)),(131074,center.enum('stretch')),(131081,center.enum('flex'))]);clear_edges(center,i)
 center.st(3121,[(131083,center.enum('row'))])
 for i in [3123,3261]:
  center.st(i,[(131105,center.pct(50)),(131097,center.px(0)),(131095,NONE),(131087,center.pct(100)),(131096,center.px(0)),(131094,NONE),(131082,center.px(0)),(131084,center.num(1)),(131085,center.num(1))]);clear_edges(center,i)
 center.save();assert [c['rid'] for c in center.a(1008)['m_Children']]==[1022,3121]
 assert [c['rid'] for c in center.a(3121)['m_Children']]==[3123,3261]
 # The original registries, grouped native menus, and all old configurations remain untouched.
 setnames=['MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet'];source_sets=[find(T,n).read_typetree() for n in setnames]
 source_desc_ids=set()
 for tree in source_sets:
  source_desc_ids.update(p['m_PathID'] for p in tree['m_gridElementDescriptions'])
  source_desc_ids.update(p['m_PathID'] for g in tree['m_tileGroups'] for p in g['m_tiles'])
 # Defaults may be selected by compositions but absent from the current grouped menu.
 source_desc_ids.update([find(T,'LiveTableTileDescription').path_id,find(T,'LatestScoresTileDescription').path_id])
 desc_map={};desc_trees={};size_audits=[]
 for index,pid in enumerate(sorted(source_desc_ids)):
  tree=existing_tree(T,pid)
  if CK not in tree or not tree[CK]:continue
  newpid=-981104000021000-index*10;name='HighlightRedesignMenu_'+tree['m_Name']
  obj,tr,guid=clone_so(T,pid,newpid,name)
  for c in tr[CK]:c['Description']={'m_FileID':0,'m_PathID':newpid}
  for w,h in [(4,6),(6,4)]:
   if not any(c['Size']=={'x':w,'y':h} for c in tr[CK]):
    c=cfg_for(tr,w,h);c['Description']={'m_FileID':0,'m_PathID':newpid};tr[CK].append(c)
  obj.save_typetree(tr);changes[T][newpid]=tr;desc_map[pid]=newpid;desc_trees[newpid]=tr
  size_audits.append({'original':pid,'private':newpid,'id':tr['<ID>k__BackingField']})
 # Three new private slots: fixed Home/Away OOP and the reduced centre.
 new_desc={}
 for index,(key,source_pid,ident,size) in enumerate([
  ('Home',find(T,'HomeTeamFormationAdaptiveBlockDescription').path_id,'HighlightRedesignHomeOOP',{'x':4,'y':6}),
  ('Away',find(T,'AwayTeamFormationAdaptiveBlockDescription').path_id,'HighlightRedesignAwayOOP',{'x':4,'y':6}),
  ('Center',find(T,'MatchViewerBlockDescription').path_id if any(o.type.name=='MonoBehaviour' and o.peek_name()=='MatchViewerBlockDescription' for o in objs[T].values()) else 2268119280419395392,'HighlightRedesignCenter',{'x':8,'y':6})]):
  src=existing_tree(T,source_pid);pid=-981104000020000-index*10;obj,tr,cguid=clone_so(T,source_pid,pid,ident+'Description')
  tr['<ID>k__BackingField']=ident;tr['<Name>k__BackingField']=ident;c=cfg_for(src,size['x'],size['y']);c.update(Description={'m_FileID':0,'m_PathID':pid},Size=size,AssetRef={'m_AssetGUID':vta_assets[key],'m_SubObjectName':'','m_SubObjectType':''},Type=1);tr[CK]=[c]
  obj.save_typetree(tr);changes[T][pid]=tr;desc_trees[pid]=tr;new_desc[key]=(pid,ident,c)
 private_sets={}
 def remap_refs(v):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_FileID']==0 and v['m_PathID'] in desc_map:v['m_PathID']=desc_map[v['m_PathID']]
   else:
    for x in v.values():remap_refs(x)
  elif isinstance(v,list):
   for x in v:remap_refs(x)
 for index,(name,original) in enumerate(zip(setnames,source_sets)):
  ob=find(T,name);pid=-981104000030000-index*10;obj,tr,guid=clone_so(T,ob.path_id,pid,'HighlightRedesign'+name)
  remap_refs(tr)
  existing={v['m_PathID'] for v in tr['m_gridElementDescriptions']}
  for q in [desc_map[find(T,'LiveTableTileDescription').path_id],desc_map[find(T,'LatestScoresTileDescription').path_id]]+[v[0] for v in new_desc.values()]:
   if q not in existing:tr['m_gridElementDescriptions'].append({'m_FileID':0,'m_PathID':q});existing.add(q)
  obj.save_typetree(tr);changes[T][pid]=tr;private_sets[name]=pid
 def size_block(block,x,y,w,h):
  b=copy.deepcopy(block);b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h}
  b['m_configDescriptions']=[{'m_FileID':0,'m_PathID':desc_map.get(p['m_PathID'],p['m_PathID'])} for p in b['m_configDescriptions']]
  oldcfg=b['m_gridElementConfigs'][0];dp=b['m_configDescriptions'][0]['m_PathID'];tr=desc_trees[dp];c=cfg_for(tr,w,h,oldcfg['AssetRef']);c['Description']={'m_FileID':0,'m_PathID':dp}
  if not any(q['Size']==c['Size'] and q['AssetRef']==c['AssetRef'] for q in tr[CK]):tr[CK].append(copy.deepcopy(c));objs[T][dp].save_typetree(tr);changes[T][dp]=tr
  b['m_gridElementConfigs']=[c];return b
 def new_block(prototype,key,x,y,w,h):
  pid,ident,c=new_desc[key];b=copy.deepcopy(prototype);b.update(m_elementID=ident,m_configDescriptions=[{'m_FileID':0,'m_PathID':pid}],m_configDescriptionKeys=[],m_gridElementConfigs=[copy.deepcopy(c)],m_location={'x':x,'y':y,'width':w,'height':h},m_minSize={'x':w,'y':h},m_maxSize={'x':w,'y':h});return b
 layout_audits=[]
 for name in layout_names:
  ob=find(T,name);original=ob.read_typetree();blocks=original['m_gridComponents'];byid={b['m_elementID']:b for b in blocks};tr=copy.deepcopy(original)
  b0=new_block(byid['HomeTeamFormationAdaptive'],'Home',0,0,4,6)
  b1=size_block(byid['HomeTeamFormationAdaptive'],4,0,4,6)
  b2=new_block(byid['MatchViewer'],'Center',8,0,8,6)
  b3=size_block(byid['AwayTeamFormationAdaptive'],16,0,4,6)
  b4=new_block(byid['AwayTeamFormationAdaptive'],'Away',20,0,4,6)
  b5=size_block(byid['HighlightLowerHomeSixPages'],0,6,6,4)
  b8=size_block(byid['HighlightLowerAwaySixPages'],18,6,6,4)
  mids=[]
  for idx,(descname,ident,x) in enumerate([('LiveTableTileDescription','LiveTable',6),('LatestScoresTileDescription','LatestScores',12)]):
   srcpid=find(T,descname).path_id;dp=desc_map[srcpid];c=cfg_for(desc_trees[dp],6,4)
   b=copy.deepcopy(b5);b.update(m_elementID=ident,m_configDescriptions=[{'m_FileID':0,'m_PathID':dp}],m_gridElementConfigs=[c],m_location={'x':x,'y':6,'width':6,'height':4});mids.append(b)
  tr['m_gridComponents']=[b0,b1,b2,b3,b4,b5,*mids,b8]
  setname='MatchExperienceHumanGridElementSet' if 'Human' in name else 'MatchExperienceGridElementSet';tr['m_gridElementSet']={'m_FileID':0,'m_PathID':private_sets[setname]};tr['m_compositionVersion']+=1
  tr['m_placementBindings']=[{'m_elementID':b['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]} for b in tr['m_gridComponents']]
  assert_grid(tr);ob.save_typetree(tr);changes[T][ob.path_id]=tr
  if tag=='game':cache_versions[name]={'before':original['m_compositionVersion'],'after':tr['m_compositionVersion']};cache_defaults[name]=copy.deepcopy(tr)
  layout_audits.append({'name':name,'version':tr['m_compositionVersion'],'slots':[{k:b[k] for k in ['m_elementID','m_location']} for b in tr['m_gridComponents']]})
 # Add bindings for the new IDs while preserving every existing menu mapping.
 overview=Doc(M,name='OverviewPrototype');overview_old=copy.deepcopy(overview.d)
 for r in overview.r.values():
  for cfg in r.get('data',{}).get('GridCompositionSets',[]):
   bindings=cfg['m_gridCompositionSetBindings']['m_gridElementBindingData']
   vals={new_desc['Home'][1]:{'match':'match','fixture':'const.NullRef','team':'match.HomeTeam','inpossession':'const.False'},new_desc['Away'][1]:{'match':'match','fixture':'const.NullRef','team':'match.AwayTeam','inpossession':'const.False'},new_desc['Center'][1]:{'match':'match','fixture':'const.NullRef','defaultToStats':'const.False'}}
   for ident,maps in vals.items():
    for key,path in maps.items():bindings.append({'DescriptionAndMapping':{'DescriptionName':ident,'MappingName':key,'MappingReferenceID':0},'BindingPath':{'m_path':path},'IsDynamic':0})
 overview.save()
 # Register private assets and update only the touched preload spans.
 for bn in [G,T]:
  ob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
  for a in [a for a in asset_clones if a['bundle']==bn]:
   assert a['pid'] not in reserved_ids
   meta['m_Container'].append((a['guid'],{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':a['pid']}}))
  for key,entry in meta['m_Container']:
   pid=entry['asset']['m_PathID']
   if pid not in changes[bn]:continue
   span=[{'m_FileID':0,'m_PathID':pid}];allptr(changes[bn][pid],span)
   if bn==G and pid-1 in changes[bn]:allptr(changes[bn][pid-1],span)
   entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
  meta['m_Container'].sort(key=lambda x:x[0]);ob.save_typetree(meta);changes[bn][ob.path_id]=meta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';raw=before[cp];new=[a for a in asset_clones if a['bundle'] in [G,T]]
 for a in new:
  cat=cm.Catalog(raw);loc=cat.locations(a['source_guid'])[0];raw=cat.add_key_location(a['guid'],loc,loc)
 cat=cm.Catalog(raw)
 # Include any extra dependencies used by the copied OOP templates.
 for a in [a for a in new if a['bundle']==G]:
  loc=cat.locations(a['guid'])[0];deps=list(cat.location(loc)['dependencies']);source_guid=source_asset_guids[a['guid']]
  for p in cat.location(cat.locations(source_guid)[0])['dependencies']:
   if p not in deps:deps.append(p)
  offset=cat.append(b''.join(struct.pack('<I',p) for p in deps),True);struct.pack_into('<I',cat.data,loc+12,offset)
 extra=[cat.locations(a['guid'])[0] for a in new if a['bundle']==G];idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];records=list(cat.key_records)
 records[idx]=(ko,cat.append(b''.join(struct.pack('<I',v) for v in [v[0] for v in cat.array(ls,'I')]+extra),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));cats[tag]=bytes(cat.data)
 check=cm.Catalog(cats[tag])
 for a in new:
  loc=check.locations(a['guid'])[0];record=check.location(loc);owner=check.location(record['dependencies'][0])['internal'];assert a['bundle'].split('::')[0] in owner,(a,owner)
 for a in new:
  if a['bundle']==G:assert check.locations(a['guid'])[0] in [v[0] for v in check.array(check.key_records[idx][1],'I')]
 audits.append({'variant':tag,'layouts':layout_audits,'native_menu_descriptors':size_audits,'current_lower_carousels_unchanged':True,'shared_matchviewer_unchanged':True,'report_layouts_unchanged':True,'catalog_registrations_checked':len(new)})
 if tag=='game':game_desc_map=copy.deepcopy(desc_map);game_desc_trees=copy.deepcopy(desc_trees)
 print('PREPARED '+tag,flush=True)
# Final validation, cache migration, packaging, and reversible installer.
outputs={}
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',bn,pid)
  for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr,('Serialization mismatch',bn,pid)
  for ob in saved.values():
   if ob.path_id in changes[bn] and ob.type.name=='MonoBehaviour':
    tr=ob.read_typetree()
    if 'inlineSheet' in tr:validate_ui(tr,saved[tr['inlineSheet']['m_PathID']].read_typetree())
  src=OUT/('skin-'+base if suffix else base);src.write_bytes(raw);outputs[bn]=src
  target=folder/base;assert target.read_bytes()==before[target],('Concurrent target change',target)
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
 for name,data in [('catalog.bin',cats[tag]),('catalog.hash',hashlib.md5(cats[tag]).hexdigest().encode('ascii'))]:
  target=(GAME.parent if tag=='game' else SKIN)/name;assert target.read_bytes()==before[target]
  src=OUT/('skin-'+name if tag=='skin' else name);src.write_bytes(data)
  tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[target]),'after':sha(data)})
 old=cm.Catalog(before[GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin']);new=cm.Catalog(cats[tag]);oldkeys=dict(old.keys());newkeys=dict(new.keys())
 added={a['guid'] for a in asset_clones if a['bundle'].endswith('::skin')==(tag=='skin')}
 assert set(newkeys)==set(oldkeys)|added
 for k,v in oldkeys.items():
  expected=[x[0] for x in old.array(v,'I')];actual=[x[0] for x in new.array(newkeys[k],'I')]
  if k=='GlobalVisualTreeAssetPreload':assert actual[:len(expected)]==expected
  else:assert actual==expected,('Unrelated catalog entry changed',tag,k)
# There were no custom Highlight caches at backup time. If present on another run,
# preserve the four pre-existing user module choices at their new positions.
cache_migrations=[]
for path,data in cache_before.items():
 old=json.loads(data.decode('utf8'));updated=copy.deepcopy(cache_defaults[path.name])
 for ox,oy,target_index in [(0,0,1),(15,0,3),(0,4,5),(15,4,8)]:
  candidates=[b for b in old['m_gridComponents'] if b['m_location']['x']==ox and b['m_location']['y']==oy]
  assert len(candidates)==1,('Unexpected custom slot position',path,ox,oy)
  previous=copy.deepcopy(candidates[0]);slot=updated['m_gridComponents'][target_index];w=slot['m_location']['width'];h=slot['m_location']['height'];previous['m_location']=copy.deepcopy(slot['m_location']);previous['m_minSize']={'x':w,'y':h};previous['m_maxSize']={'x':w,'y':h}
  for ref in previous['m_configDescriptions']:ref['m_PathID']=game_desc_map.get(ref['m_PathID'],ref['m_PathID'])
  dp=previous['m_configDescriptions'][0]['m_PathID'];assert dp in game_desc_trees
  chosen=previous['m_gridElementConfigs'][0]['AssetRef'];cfg=cfg_for(game_desc_trees[dp],w,h,chosen);cfg['Description']={'m_FileID':0,'m_PathID':dp};previous['m_gridElementConfigs']=[cfg];updated['m_gridComponents'][target_index]=previous
 assert_grid(updated);assert path.read_bytes()==data;src=OUT/('cache-'+path.name+'.json');raw=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8');src.write_bytes(raw)
 tx.append({'target':str(path),'source':str(src),'backup':str(OUT/'backup-cache'/path.name),'before':sha(data),'after':sha(raw)});cache_migrations.append(str(path))
# All GUI entrypoints and old report/shared objects are protected by the raw-byte checks.
report={'installed':False,'runtime_verified':False,'output':str(OUT),'grid':[24,10],'upper_lower_ratio':[3,2],'upper_column_ratio':[1,1,2,1,1],'center_upper_lower_ratio':[2,1],'bottom_column_ratio':[1,1,1,1],'checks':audits,'asset_clones':asset_clones,'serialization_roundtrip':True,'unrelated_objects_identical':True,'original_report_and_small_screen_assets_unchanged':True,'original_shared_matchviewer_unchanged':True,'cache_migrations':cache_migrations,'protected_sha256':{}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if cache_migrations:installer=installer.replace("for row in tx:\n", "allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('''# Highlight 上下布局重构

当前资源独立备份见 backup-game、backup-skin、backup-inventory.json。现有游戏与皮肤分别迁移，禁止互相覆盖；restore.ps1 带安装后哈希保护。

整体上下3:2，上方五列1:1:2:1:1，下方四列等宽。24x10逻辑网格，顶部6行、底部4行。上方：主队无球竖向、当前主队模块、球场与两图、当前客队模块、客队无球竖向。下方：当前主队六页模块、完整原生菜单（默认积分榜）、完整原生菜单（默认最新比分）、当前客队六页模块。

仅三份新私有VTA：两份从当前无球模板复制，改原生竖向Orientation=0/FlipPositions=0，保留头像/姓名/评分；中间从当前MatchViewer复制，留下完整实时球场和当前比赛势头/xG子树，保持原生数据绑定，内部2:1、下方左右各半。

大屏专用的私有描述和菜单注册表保留原分组、模块ID和旧尺寸配置，并补4x6/6x4；原始菜单注册表和原模块描述未修改，小屏和报告页继续使用原资源。原有两侧顶部模块与六页轮播模板、原共享MatchViewer逐对象字节保持。四套大屏布局版本提升，OverviewPrototype仅补新模块绑定，不修改顶部记分牌、战术栏、解说、底部卡片或侧栏。

原生选择器、事件和持久化机制保留，不自制菜单。没有自定义Highlight缓存时不创建/清空缓存；存在时仅迁移对应四套布局并保留原有四槽模块选择。原始Grid布局模式和用户分辨率/缩放偏好保持。

新VTA/SO全部登记Addressables目录，校验所属包首项依赖和实际包内对象；三份VTA加入实际GlobalVisualTreeAssetPreload列表。序列化回读、240格无重叠全覆盖、原目录条目与未指定对象一致性检查通过。未启动游戏，1920x1080及用户截图尺寸的实际裁切/交互/数据刷新需游戏内确认，不能将静态检查当作显示验证。
''','utf8')
(OUT/'approved-layout.txt').write_text('TOP 60%: [HOME OOP 1][CURRENT HOME 1][PITCH/CHARTS 2][CURRENT AWAY 1][AWAY OOP 1]\nCENTER: pitch 2 / [momentum 1 | xG 1] 1\nBOTTOM 40%: [CURRENT HOME 1][NATIVE MENU: LiveTable 1][NATIVE MENU: LatestScores 1][CURRENT AWAY 1]\n','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'files':len(tx),'new_vtas':6,'runtime_verified':False},ensure_ascii=False),flush=True)

