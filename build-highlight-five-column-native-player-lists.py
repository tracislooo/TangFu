from pathlib import Path
import json, ast, types

R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle';V='ui-tableviews_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-five-columns-native-lists-').replace('NAMES=[W,G,M,F]','NAMES=[G,M,T]')
boot=boot.replace("if SKIN/n in before:assert before[SKIN/n]==before[GAME/n]","if SKIN/n in before and n!=V:assert before[SKIN/n]==before[GAME/n]")
exec(compile(boot,'backup-live-resources-and-load-codecs','exec'))
env[W]=UnityPy.load(str(GAME/W));objs[W]={o.path_id:o for o in env[W].objects}
main=Doc(G,name='MatchViewer_12x4');main_before=copy.deepcopy(main.d);main_style_before=copy.deepcopy(main.s)
f32=lambda x:struct.unpack('<f',struct.pack('<f',x))[0]
AUTO={'m_ValueType':1,'valueIndex':2}
new_guids={};asset_clones=[]

def resolve_asset(guid,bundles=None):
 hits=[]
 for bundle in bundles or list(objs):
  for key,ptr in env[bundle].container.items():
   if key!=guid:continue
   obj=objs[bundle].get(ptr.path_id)
   if obj is None or obj.type.name!='MonoBehaviour':continue
   tree=obj.read_typetree()
   if 'm_Rules' in tree:continue
   hits.append((bundle,obj.path_id))
 assert len(set(hits))==1,('Native asset not uniquely resolved',guid,hits)
 bundle,pid=hits[0];return bundle,objs[bundle][pid]

def register_clone(bundle,source,new_name,pid,tree,source_guid=None):
 assert pid not in objs[bundle]
 target=next(o for o in objs[bundle].values() if o.type.name==source.type.name and o.peek_name()==('MatchViewer_12x4' if bundle==G else source.peek_name()))
 obj=copy.copy(target);obj.path_id=pid;obj.data=None;obj._read_until=None;obj.assets_file.objects[pid]=obj;objs[bundle][pid]=obj
 tree=copy.deepcopy(tree);tree['m_Name']=new_name;pointer_remap(tree,source.assets_file,obj.assets_file)
 if 'references' in tree:import_types(source.assets_file,obj.assets_file,tree['references']['RefIds'])
 obj.save_typetree(tree);changes[bundle][pid]=tree
 guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/highlight-five-columns/'+new_name).hex
 if source_guid is None:
  meta=next(o for o in objs[bundle].values() if o.type.name=='AssetBundle').read_typetree()
  source_guid=next(key for key,entry in meta['m_Container'] if entry['asset']['m_PathID']==source.path_id)
 asset_clones.append({'bundle':bundle,'pid':pid,'guid':guid,'name':new_name,'source_guid':source_guid})
 new_guids[new_name]=guid;return obj,tree,guid

def clone_doc(source,new_name,pid):
 tree=copy.deepcopy(source.d);style=copy.deepcopy(source.s);tree['inlineSheet']={'m_FileID':0,'m_PathID':pid-1}
 obj,tree,guid=register_clone(G,source.obj,new_name,pid,tree,source_guid='be643be14ca6c024083f0e6b4c7dea7c')
 proto=objs[G][main.sid];style_obj=copy.copy(proto);style_obj.path_id=pid-1;style_obj.data=None;style_obj._read_until=None;style_obj.assets_file.objects[pid-1]=style_obj;objs[G][pid-1]=style_obj
 style['m_Name']=new_name+'_Style';pointer_remap(style,source.af,style_obj.assets_file);style_obj.save_typetree(style);changes[G][pid-1]=style
 return Doc(G,pid=pid,tree=tree,style=style),guid

helper=ast.parse((R/'build-highlight-lower-five-by-three-with-charts.py').read_text('utf8'))
clone_audits=[]
exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['copy_style','clone_native','unpack_args','pack_args']],type_ignores=[]),'preserve-native-ui-components','exec'))

def walk(doc,i):
 yield i
 for c in doc.a(i).get('m_Children',[]):yield from walk(doc,c['rid'])
def plain(doc,parent,name):return doc.add(main,1015,parent,name)
def clear_space(doc,i):doc.st(i,[(p,doc.px(0)) for p in [131090,131091,131092,131093,131098,131099,131100,131101]])
def stretch(doc,i):doc.st(i,[(131105,doc.pct(100)),(131097,doc.px(0)),(131096,doc.px(0)),(131084,doc.num(1)),(131085,doc.num(1))])

native_stats=Doc(G,name='PlayerStats_4x6')
metric_audits=[]

tile_audits=[];tile_guids={}
for index,(side,home) in enumerate([('Home',True),('Away',False)]):
 tile,guid=clone_doc(native_stats,'Highlight'+side+'NativePlayerStats',-981025000000200-index*10);tile_guids[side]=guid
 before_tile=copy.deepcopy(tile.d);old_r=refs(before_tile)
 scope=tile.add(main,1004,1000,'Explicit'+side+'MatchTeam')
 tile.data(scope).update(Mappings=[{'m_serialisedType':0,'from':'team','to':{'m_path':'match.HomeTeam' if home else 'match.AwayTeam'},'type':{'id':1145176088}},{'m_serialisedType':0,'from':'ishometeam','to':{'m_path':'const.True' if home else 'const.False'},'type':{'id':0}},{'m_serialisedType':0,'from':'isonmainscreen','to':{'m_path':'const.False'},'type':{'id':0}}],Mappings_UxmlAttributeFlags=1)
 tile.move(1001,scope);tile.fill(scope)
 tables=[]
 for i in [1028,1032]:
  value=tile.data(i)
  value.update(ScrollViewMode=2,ScrollViewMode_UxmlAttributeFlags=1,HorizontalScrollerVisibility=0,HorizontalScrollerVisibility_UxmlAttributeFlags=1)
  assert value['FactoryAsset']==sd(old_r,i)['FactoryAsset'] and value['InitFunction']==sd(old_r,i)['InitFunction']
  assert value['FixedElementSize']==sd(old_r,i)['FixedElementSize']
  tile.st(i,[(131105,tile.pct(100)),(131097,tile.px(0)),(131096,tile.px(0)),(131084,tile.num(1)),(131085,tile.num(1))])
  assert value['Binding']==sd(old_r,i)['Binding'];tables.append(i)
 tile.save();tile_audits.append({'side':side,'guid':guid,'root_scope':scope,'team':'match.HomeTeam' if home else 'match.AwayTeam','table_nodes':tables,'native_match_fixture_binding_and_empty_states_preserved':True})

CK='<Configurations>k__BackingField'
descriptor_pids={};private_ids={'Home':'HighlightHomePlayerStatsColumn','Away':'HighlightAwayPlayerStatsColumn'}
for index,side in enumerate(['Home','Away']):
 source=find(T,'PlayerStats'+side+'TeamTileDescription');tree=source.read_typetree();pid=-981025000000300-index
 obj,tree,guid=register_clone(T,source,private_ids[side]+'Description',pid,tree)
 tree['<Name>k__BackingField']=private_ids[side];tree['<ID>k__BackingField']=private_ids[side]
 config=copy.deepcopy(tree[CK][0]);config.update(Description={'m_FileID':0,'m_PathID':pid},Size={'x':1,'y':8},AssetRef={'m_AssetGUID':tile_guids[side],'m_SubObjectName':'','m_SubObjectType':''})
 tree[CK]=[config];tree['<DefaultConfigIndex>k__BackingField']=0
 obj.save_typetree(tree);changes[T][pid]=copy.deepcopy(tree);descriptor_pids[side]=pid
available=set()
for name in ['MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet']:
 obj=find(T,name);tree=obj.read_typetree();original=copy.deepcopy(tree)
 available.update(x['m_PathID'] for x in tree['m_gridElementDescriptions'])
 for pid in descriptor_pids.values():tree['m_gridElementDescriptions'].append({'m_FileID':0,'m_PathID':pid})
 assert tree['m_gridElementDescriptions'][:-2]==original['m_gridElementDescriptions']
 obj.save_typetree(tree);changes[T][obj.path_id]=tree
size_audits=[]
for pid in sorted(available):
 obj=objs[T][pid];tree=obj.read_typetree()
 if CK not in tree:continue
 original=copy.deepcopy(tree);new_sizes=[]
 for config in original[CK]:
  if config['Size']['x'] not in [4,5]:continue
  candidate=copy.deepcopy(config);candidate['Size']['x']=2
  if candidate not in tree[CK]:tree[CK].append(candidate);new_sizes.append(candidate['Size'])
 if new_sizes:
  obj.save_typetree(tree);changes[T][pid]=tree;size_audits.append({'descriptor':tree['m_Name'],'new_sizes':new_sizes,'old_configurations_preserved':tree[CK][:len(original[CK])]==original[CK]})
viewer=objs[T][2268119280419395392];viewer_tree=viewer.read_typetree()
assert any(c['Size']=={'x':8,'y':8} and c['AssetRef']['m_AssetGUID']=='be643be14ca6c024083f0e6b4c7dea7c' for c in viewer_tree[CK])

# Migrate the existing three slots, then add the two independent full-height columns.
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
new_blocks=[]
sample=find(T,layout_names[0]).read_typetree()['m_gridComponents'][0]
for side,x in [('Home',2),('Away',11)]:
 block=copy.deepcopy(sample);pid=descriptor_pids[side];cfg=changes[T][pid][CK][0]
 block.update(m_elementID=private_ids[side],m_configDescriptions=[{'m_FileID':0,'m_PathID':pid}],m_configDescriptionKeys=[],m_gridElementConfigs=[copy.deepcopy(cfg)],m_location={'x':x,'y':0,'width':1,'height':8},m_minSize={'x':1,'y':8},m_maxSize={'x':1,'y':8},m_isLocked=1)
 new_blocks.append(block)
migration_code='''import copy
OLD={(0,5):(0,2),(5,10):(3,8),(15,5):(12,2)}
ADDITIONS=__ADDITIONS__
PRIVATE_IDS={b['m_elementID'] for b in ADDITIONS}
def migrate_layout(document,forward=True,version=None,limits_from=None,cache=False):
 result=copy.deepcopy(document);mapping=OLD if forward else {v:k for k,v in OLD.items()};destinations=set(mapping.values())
 original_blocks=[b for b in result['m_gridComponents'] if b['m_elementID'] not in PRIVATE_IDS]
 result['m_gridComponents']=original_blocks
 for block in original_blocks:
  loc=block['m_location'];key=(loc['x'],loc['width']);assert key in mapping or key in destinations,('Unexpected saved slot',block['m_elementID'],key)
  x,w=mapping.get(key,key);loc['x']=x;loc['width']=w;block['m_minSize']['x']=w;block['m_maxSize']['x']=w
  for cfg in block['m_gridElementConfigs']:cfg['Size']['x']=w
 if forward:
  for addition in ADDITIONS:
   b=copy.deepcopy(addition)
   if cache:
    b['m_configDescriptions']=[];b['m_configDescriptionKeys']=[b['m_elementID']];b['m_gridElementConfigs']=[]
   result['m_gridComponents'].append(b)
 if limits_from is not None:
  old={(b['m_location']['x'],b['m_location']['width'],b['m_location']['y']):b for b in limits_from['m_gridComponents']}
  for b in result['m_gridComponents']:
   key=(b['m_location']['x'],b['m_location']['width'],b['m_location']['y'])
   if key in old:b['m_minSize']=copy.deepcopy(old[key]['m_minSize']);b['m_maxSize']=copy.deepcopy(old[key]['m_maxSize'])
 if version is not None:result['m_compositionVersion']=version
 cells=set();width=14 if forward else 20
 for b in result['m_gridComponents']:
  q=b['m_location']
  for x in range(q['x'],q['x']+q['width']):
   for y in range(q['y'],q['y']+q['height']):
    assert 0<=x<width and 0<=y<8 and (x,y) not in cells,('Invalid grid',b['m_elementID'],x,y)
    cells.add((x,y))
 assert len(cells)==width*8
 return result
'''.replace('__ADDITIONS__',repr(new_blocks))
migration=types.ModuleType('five_column_migration');exec(compile(migration_code,'grid_migration.py','exec'),migration.__dict__)
cache_versions={};layout_audits=[]
for name in layout_names:
 obj=find(T,name);original=obj.read_typetree();version=original['m_compositionVersion']+1
 tree=migration.migrate_layout(original,version=version)
 for block in tree['m_gridComponents']:
  width=block['m_location']['width'];height=block['m_location']['height'];options=[]
  for ref in block['m_configDescriptions']:
   descriptor=changes[T].get(ref['m_PathID'],objs[T][ref['m_PathID']].read_typetree());options.extend(descriptor.get(CK,[]))
  block['m_gridElementConfigs']=[copy.deepcopy(next(c for c in options if c['Size']=={'x':width,'y':height}))]
 for side in ['Home','Away']:
  p=copy.deepcopy(original['m_placementBindings'][-1]);p['m_elementID']=private_ids[side];tree['m_placementBindings'].append(p)
 obj.save_typetree(tree);changes[T][obj.path_id]=tree
 cache_versions[name]={'before':original['m_compositionVersion'],'after':version}
 layout_audits.append({'name':name,'positions':{b['m_elementID']:b['m_location'] for b in tree['m_gridComponents']},'cells':112,'non_overlapping_full_coverage':True})
 (OUT/'templates'/(name+'.json')).write_text(json.dumps(tree,ensure_ascii=False,indent=2),'utf8')

# Feed the same live-match mappings used by native home/away player-table tiles in every overview context.
overview=Doc(M,name='OverviewPrototype');overview_before=copy.deepcopy(overview.d);binding_changes=[]
for rid,r in overview.r.items():
 for cfg in r.get('data',{}).get('GridCompositionSets',[]):
  bindings=cfg['m_gridCompositionSetBindings']['m_gridElementBindingData']
  for side,home in [('Home',True),('Away',False)]:
   values={'match':'match','fixture':'const.NullRef','isonmainscreen':'const.False','ishometeam':'const.True' if home else 'const.False','team':'match.HomeTeam' if home else 'match.AwayTeam'}
   assert not any(b['DescriptionAndMapping']['DescriptionName']==private_ids[side] for b in bindings)
   for key,path in values.items():bindings.append({'DescriptionAndMapping':{'DescriptionName':private_ids[side],'MappingName':key,'MappingReferenceID':0},'BindingPath':{'m_path':path},'IsDynamic':0})
   binding_changes.append({'overview_record':rid,'descriptor':private_ids[side],'mappings':values})
overview.save()
assert main.d==main_before and main.s==main_style_before

# Register private addressable assets and extend only the preload spans that reference new local objects.
def allptr(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'}:
   if v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():allptr(x,out)
 elif isinstance(v,list):
  for x in v:allptr(x,out)
for bundle in NAMES:
 metaobj=next(o for o in objs[bundle].values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();old_meta=copy.deepcopy(meta)
 for clone in [c for c in asset_clones if c['bundle']==bundle]:meta['m_Container'].append((clone['guid'],{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':clone['pid']}}))
 for key,entry in meta['m_Container']:
  pid=entry['asset']['m_PathID']
  if pid not in changes[bundle]:continue
  is_new=pid not in hashes[bundle]
  span=[] if is_new else copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
  allptr(changes[bundle][pid],span)
  pointer={'m_FileID':0,'m_PathID':pid}
  if pointer not in span:span.append(pointer)
  entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable'].extend(span)
 meta['m_Container'].sort(key=lambda kv:kv[0])
 metaobj.save_typetree(meta);changes[bundle][metaobj.path_id]=meta
spec=importlib.util.spec_from_file_location('five_column_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=before[GAME.parent/'catalog.bin']
for clone in asset_clones:
 cat=cm.Catalog(catalog);loc=cat.locations(clone['source_guid'])[0];catalog=cat.add_key_location(clone['guid'],loc,loc)
cat=cm.Catalog(catalog);preload_key='GlobalVisualTreeAssetPreload'
new_locations=[cat.locations(c['guid'])[0] for c in asset_clones if c['bundle']==G]
idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==preload_key);ko,ls=cat.key_records[idx];locs=[v[0] for v in cat.array(ls,'I')]+new_locations
records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog=bytes(cat.data)
oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);newcat=cm.Catalog(catalog);newkeys=dict(newcat.keys())
assert set(newkeys)==set(dict(oldcat.keys()))|{c['guid'] for c in asset_clones}
for key,loc in oldcat.keys():
 expected=[x[0] for x in oldcat.array(loc,'I')]
 if key==preload_key:expected+=new_locations
 assert [x[0] for x in newcat.array(newkeys[key],'I')]==expected,('Unrelated catalog location changed',key)
outputs={}
for bundle in NAMES:
 data=env[bundle].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(objs[bundle])
 for pid,h in hashes[bundle].items():
  if pid not in changes[bundle]:assert sha(saved[pid].get_raw_data())==h,('Unrelated asset changed',bundle,pid)
 for pid,tree in changes[bundle].items():assert saved[pid].read_typetree()==tree,('Serialization mismatch',bundle,pid)
 for doc in [doc for doc in documents if doc.n==bundle]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 if bundle==G:
  assert sha(saved[main.obj.path_id].get_raw_data())==hashes[G][main.obj.path_id] and sha(saved[main.sid].get_raw_data())==hashes[G][main.sid]
 outputs[bundle]=data;(OUT/bundle).write_bytes(data)
(OUT/'catalog.bin').write_bytes(catalog);(OUT/'catalog.hash').write_bytes(hashlib.md5(catalog).hexdigest().encode('ascii'))
outputs['catalog.bin']=catalog;outputs['catalog.hash']=(OUT/'catalog.hash').read_bytes()
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');previews=[]
for name,version in cache_versions.items():
 path=cache_root/name
 if not path.exists():continue
 original=json.loads(path.read_text('utf8'));updated=migration.migrate_layout(original,version=version['after'],cache=True)
 restored=migration.migrate_layout(updated,False,version=version['before'],limits_from=original)
 assert restored['m_gridComponents']==original['m_gridComponents']
 previews.append({'file':name,'original_modules_preserved':[b['m_elementID'] for b in original['m_gridComponents']]})
 (OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')
for path,b in before.items():assert path.read_bytes()==b
for path,h in protected.items():assert sha(path.read_bytes())==h
report={'passed':True,'width_ratios':[2,1,8,1,2],'grid_size':[14,8],'layouts':layout_audits,'native_player_row_height':35,'table_style':'original native; no font, row, cell, factory or view changes','fields':['assists','xg','goals','rating'],'metric_cells':metric_audits,'tiles':tile_audits,'overview_bindings':binding_changes,'new_assets':asset_clones,'existing_native_configs_preserved':size_audits,'custom_layout_previews':previews,'original_selectors_and_player_tables_unchanged':True,'middle_template_and_styles_raw_bytes_unchanged':True,'native_factory_view_formatting_sorting_and_cells_preserved':True,'unrelated_assets_and_catalog_locations_unchanged':True,'serialization_roundtrip':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{n:{str(pid):tree.get('m_Name','AssetBundle') for pid,tree in v.items()} for n,v in changes.items()},'before_sha256':{str(path):sha(b) for path,b in before.items()},'after_sha256':{n:sha(b) for n,b in outputs.items()},'protected_sha256':{str(path):h for path,h in protected.items()},'missing_before':[]}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'cache_root':str(cache_root),'cache_versions':cache_versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
installer=(R/'install-highlight-layout-with-cache.py').read_text('utf8').replace("path=folder/name;assert path.parent.resolve()==folder","path=(folder.parent/name if folder==game and name.startswith('catalog.') else folder/name);assert path.parent.resolve() in [folder,game.parent]")
installer=installer.replace('limits_from=old_limits)','limits_from=old_limits,cache=True)')
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed; see diagnostics above.' }\n",'utf8')
watcher=(R/'scoreboard-three-letter-names-20261023-235308/install-after-game-exits.ps1').read_text('utf8').replace("'G:/Doc/ChatGPT/New project/install-match-ui-patch.py'","(Join-Path $PSScriptRoot 'installer.py')")
(OUT/'install-after-game-exits.ps1').write_text(watcher,'utf8')
(OUT/'修改说明.md').write_text('# Highlight五列：2:1:8:1:2，球员表保留原生样式\n\n桌面大屏执教/旁观、有无积分榜四套布局为14×8逻辑网格。五列起点0/2/3/11/12，宽2/1/8/1/2；第二、第四列显示主队、客队全高球员数据列表。原左右阵型及底部模块纵向位置不变，原选择器和第三页保留。\n根据最新要求，取消紧凑行：完全保留PlayerStats_4x6的原生字体、35px行高、姓名、助攻、预期进球、进球、评分列、原生工厂、视图、单元格、格式、提示、导航和排序。只在新增两列启用横向及纵向滚动，以便在窄列查看全部原生字段。不修改共用表格或表格视图资源。\n两个私有模块明确映射match.HomeTeam/match.AwayTeam和对应ishometeam，保留比赛/历史比赛列表入口与无数据状态。\n中间MatchViewer_12x4及内联样式原始字节不变，内部45%/55%、图表、75%四列数据、50%按钮等均保留。\n若有本地比赛布局，安装时仅迁移原有槽位坐标和尺寸并添加两列；恢复时移除新增列，回迁原槽位，保留原槽位选项，不清空其他布局缓存。\n已检查序列化回读、网格无重叠覆盖、主客队参数、原生数据入口/工厂/视图/样式引用、中间页面和所有无关对象一致性、目录旧条目一致性。尚未在游戏内验证实际显示、滚动、换人和刷新。\n退出游戏后安装；restore.ps1仅恢复本次修改。\n','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'ratios':[2,1,8,1,2],'layouts':4,'private_assets':len(asset_clones),'saved_layouts':len(previews),'roundtrip':True,'runtime_verified':False},ensure_ascii=False))
