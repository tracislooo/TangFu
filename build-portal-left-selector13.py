from pathlib import Path
import json,types
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','portal-left-selector13-').replace('NAMES=[W,G,M,F]','NAMES=[W,T]')
exec(compile(boot,'backup-current-portal-resources','exec'))
CK='<Configurations>k__BackingField'
IDS=['ClubTeamReport','FixtureSchedule','Training','AgentOffers','JobMarket','CompetitionStats','PortalNewsTimedTile','TransferBudget','WageBudget','Calendar','LeagueTableStages','MedicalCentre','DataHub']
LABELS=['球队报告','球队赛程','训练','经纪人推荐','工作中心／职位空缺','赛事统计','新闻','转会预算','工资预算','日历','联赛积分榜／赛事阶段','医疗中心','数据中心']
OUTER_ID='PortalLeftSelector13'
nextpid=-981026000010000
registrations=[]
def newpid():
 global nextpid
 nextpid-=10;return nextpid
def clone(bn,source,name,tree=None,register=False):
 pid=newpid();d=copy.deepcopy(tree if tree is not None else source.read_typetree());d['m_Name']=name
 ob=copy.copy(source);ob.path_id=pid;ob.data=None;ob._read_until=None;ob.assets_file.objects[pid]=ob;objs[bn][pid]=ob;ob.save_typetree(d);changes[bn][pid]=copy.deepcopy(d)
 if register:
  meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
  srcguid=next(g for g,e in meta['m_Container'] if e['asset']['m_PathID']==source.path_id)
  guid=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/portal-left-selector13/'+name).hex
  registrations.append({'bundle':bn,'pid':pid,'guid':guid,'source_guid':srcguid})
 else:guid=None
 return ob,d,guid
def save(bn,ob,d):ob.save_typetree(d);changes[bn][ob.path_id]=copy.deepcopy(d)
def ptr(ob):return {'m_FileID':0,'m_PathID':ob.path_id}

native_set=find(T,'PortalTileSet');old_set=native_set.read_typetree()
descs={}
for p in old_set['m_gridElementDescriptions']:
 ob=objs[T][p['m_PathID']];d=ob.read_typetree();descs[d['<ID>k__BackingField']]=(ob,d)
assert set(IDS)<=set(descs)
private_set_tree=copy.deepcopy(old_set)
private_set_tree['m_gridElementDescriptions']=[ptr(descs[i][0]) for i in IDS];private_set_tree['m_tileGroups']=[]
private_set,private_set_tree,_=clone(T,native_set,'PortalLeftSelector13TileSet',private_set_tree)
assert len(private_set_tree['m_gridElementDescriptions'])==13
assert [objs[T][p['m_PathID']].read_typetree()['<ID>k__BackingField'] for p in private_set_tree['m_gridElementDescriptions']]==IDS

page=Doc(W,name='PortalScreen');page_before=copy.deepcopy(page.d)
outer_groups=page.data(1028)['GridCompositionSets'];outer_binding=outer_groups[0]['m_gridCompositionSetBindings']
wrapper_binding=copy.deepcopy(outer_binding)
wrapper_binding['m_gridElementBindingData']=[b for b in wrapper_binding['m_gridElementBindingData'] if b['DescriptionAndMapping']['DescriptionName'] in IDS]
for key in ['m_gridElementVisiblityFunctions','m_displayNameBindingMethods']:
 wrapper_binding[key]=[b for b in wrapper_binding[key] if (b.get('m_itemA',{}).get('DescriptionName') if isinstance(b.get('m_itemA'),dict) else b.get('m_itemA')) in IDS]
# The outer grid forwards its resolved named mappings into this isolated block.
for n in wrapper_binding['m_nameBindings']:n['path']={'m_path':n['name']}

def config_for(ident,w,h):
 cfgs=descs[ident][1][CK]
 return copy.deepcopy(next(c for c in cfgs if c['Size']=={'x':w,'y':h}))

wrapper_configs=[];private_layouts=[];choice_audits=[]
for variant,w,h in [('Large',6,5),('Compact',4,4)]:
 comp_source=find(T,'Portal-'+('Large' if w==6 else 'Medium'));base=comp_source.read_typetree()
 slot=copy.deepcopy(next(c for c in base['m_gridComponents'] if c['m_location']['x']==0 and c['m_location']['y']>0))
 slot.update(m_elementID='ClubTeamReport',m_location={'x':0,'y':0,'width':w,'height':h},m_minSize={'x':w,'y':h},m_maxSize={'x':w,'y':h},m_isLocked=0,m_isDynamic=0,m_takesFocus=0)
 slot['m_configDescriptions']=[ptr(descs['ClubTeamReport'][0])];slot['m_configDescriptionKeys']=[];slot['m_gridElementConfigs']=[config_for('ClubTeamReport',w,h)]
 base.update(m_gridComponents=[slot],m_compositionVersion=1,m_gridElementSet=ptr(private_set),m_placementBindings=[{'m_elementID':i,'m_optionalConditions':[],'m_optionalConfigConditions':[]} for i in IDS])
 for k,v in base['m_optionalSlices'].items():
  if isinstance(v,list):base['m_optionalSlices'][k]=[0] if k=='m_instantiationOrder' else []
 comps=[]
 for bp in range(6):
  tree=copy.deepcopy(base);tree['m_gridBreakpoint']=bp
  co,tree,_=clone(T,comp_source,'PortalLeftSelector13-'+variant+'-BP'+str(bp),tree)
  comps.append(co);private_layouts.append(tree)
 source_set=find(T,'PortalCompositionSet');st=source_set.read_typetree();st['m_availableGridElements']=ptr(private_set)
 st['m_gridBreakpointCompositionData']={'m_values':[{'m_key':bp,'m_value':[ptr(comps[bp])]} for bp in range(6)],'m_keys':list(range(6))}
 st['m_gridBreakpointCompositionDataOld']={'m_values':[],'m_keys':[],'m_valuesOld':[]}
 comp_set,st,_=clone(T,source_set,'PortalLeftSelector13'+variant+'CompositionSet',st)
 # A private copy of the native scalable grid hosts one independently saved tile.
 donor=Doc(W,name='PortalMessagesContentBlock')
 tree=copy.deepcopy(donor.d);style=copy.deepcopy(donor.s)
 root=copy.deepcopy(donor.r[1000]);frame=copy.deepcopy(page.r[1021]);frame_sd=copy.deepcopy(page.r[page.a(1021)['m_SerializedData']['rid']])
 grid=copy.deepcopy(donor.r[1068]);grid_sd=copy.deepcopy(donor.r[1071])
 frame['rid']=1001;frame_sd['rid']=1002;grid['rid']=1003;grid_sd['rid']=1004
 root['data']['m_Children']=[{'rid':1001}]
 frame['data'].update(m_Parent={'rid':1000},m_Children=[{'rid':1003}],m_SerializedData={'rid':1002},m_RuleIndex=-1,m_Classes=['flex-grow-class','width-100-percent','height-100-percent'])
 grid['data'].update(m_Parent={'rid':1001},m_Children=[],m_SerializedData={'rid':1004},m_RuleIndex=-1,m_Classes=['flex-grow-class','width-100-percent','height-100-percent'])
 frame_sd['data'].update(name='PortalLeftSelectorHost',name_UxmlAttributeFlags=1)
 bindings=copy.deepcopy(wrapper_binding);bindings['m_gridCompositionSet']={'m_FileID':2,'m_PathID':comp_set.path_id}
 grid_sd['data'].update(name='PortalLeftSelector13'+variant,name_UxmlAttributeFlags=1,Bindings=bindings,Bindings_UxmlAttributeFlags=1,IsCustomisable=1,IsCustomisable_UxmlAttributeFlags=1,Flags=0,Flags_UxmlAttributeFlags=1,IgnoreOuterPadding=1,IgnoreOuterPadding_UxmlAttributeFlags=1)
 tree['references']['RefIds']=[root,frame,frame_sd,grid,grid_sd];tree['m_Usings']=[];tree['m_Slots']=[];tree['m_AssetEntries']=[]
 import_types(page.af,donor.af,[frame,frame_sd])
 so,style,_=clone(W,objs[W][donor.sid],'PortalLeftSelector13'+variant+'_Style',style)
 tree['inlineSheet']=ptr(so)
 vo,tree,guid=clone(W,donor.obj,'PortalLeftSelector13'+variant,tree,register=True)
 validate_ui(tree,style)
 cfg=copy.deepcopy(descs['ClubTeamReport'][1][CK][0]);cfg.update(Size={'x':w,'y':h},Type=1);cfg['AssetRef']['m_AssetGUID']=guid;wrapper_configs.append(cfg)
 for ident,label in zip(IDS,LABELS):
  c=config_for(ident,w,h);choice_audits.append({'variant':variant,'id':ident,'name':label,'guid':c['AssetRef']['m_AssetGUID']})

wrapper_tree=copy.deepcopy(descs['ClubTeamReport'][1]);wrapper_tree['<Name>k__BackingField']=OUTER_ID;wrapper_tree['<ID>k__BackingField']=OUTER_ID
wrapper_tree[CK]=wrapper_configs;wrapper_tree['<DefaultConfigIndex>k__BackingField']=0
wrapper,wrapper_tree,_=clone(T,descs['ClubTeamReport'][0],'PortalLeftSelector13Description',wrapper_tree)
for c in wrapper_tree[CK]:c['Description']=ptr(wrapper)
save(T,wrapper,wrapper_tree)
# Cache reconstruction resolves the outer block by this stable description key.
updated_set=copy.deepcopy(old_set);updated_set['m_gridElementDescriptions'].append(ptr(wrapper));save(T,native_set,updated_set)

# Forward precisely the same context as the main portal grid; other bindings are unchanged.
group=outer_groups[0]['m_gridCompositionSetBindings']
for n in group['m_nameBindings']:
 group['m_gridElementBindingData'].append({'DescriptionAndMapping':{'DescriptionName':OUTER_ID,'MappingName':n['name'],'MappingReferenceID':0},'BindingPath':{'m_path':''},'IsDynamic':0})
expected=copy.deepcopy(page_before);refs(expected)[page.a(1028)['m_SerializedData']['rid']]['data']['GridCompositionSets'][0]['m_gridCompositionSetBindings']=copy.deepcopy(group)
assert expected==page.d
page.save()

targets={};versions={}
for variant in ['Large','Medium','Small']:
 for suffix in ['', '-FMC']:
  ob=find(T,'Portal-'+variant+suffix);old=ob.read_typetree();tree=copy.deepcopy(old)
  slot=next(c for c in tree['m_gridComponents'] if c['m_location']['x']==0 and c['m_location']['y']>0)
  w=slot['m_location']['width'];h=slot['m_location']['height']
  slot.update(m_elementID=OUTER_ID,m_configDescriptions=[ptr(wrapper)],m_configDescriptionKeys=[],m_gridElementConfigs=[copy.deepcopy(next(c for c in wrapper_tree[CK] if c['Size']=={'x':w,'y':h}))],m_isLocked=1)
  tree['m_compositionVersion']+=1
  if not any(b['m_elementID']==OUTER_ID for b in tree['m_placementBindings']):tree['m_placementBindings'].append({'m_elementID':OUTER_ID,'m_optionalConditions':[],'m_optionalConfigConditions':[]})
  for a,b in zip(old['m_gridComponents'],tree['m_gridComponents']):
   if a['m_location']['x']!=0 or a['m_location']['y']==0:assert a==b
  save(T,ob,tree);targets[tree['m_Name']]=tree;versions[tree['m_Name']]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}

def allptr(v):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'}:
   if v['m_PathID']:yield v
  else:
   for x in v.values():yield from allptr(x)
 elif isinstance(v,list):
  for x in v:yield from allptr(x)
for bn in [W]:
 mo=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=mo.read_typetree();prior=copy.deepcopy(meta['m_Container'])
 for ent in registrations:
  if ent['bundle']!=bn:continue
  pointers=[{'m_FileID':0,'m_PathID':ent['pid']}]+list(allptr(changes[bn][ent['pid']]))
  idx=len(meta['m_PreloadTable']);meta['m_PreloadTable']+=pointers
  meta['m_Container'].append((ent['guid'],{'preloadIndex':idx,'preloadSize':len(pointers),'asset':pointers[0]}))
 assert meta['m_Container'][:len(prior)]==prior;save(bn,mo,meta)
spec=importlib.util.spec_from_file_location('portal_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=before[GAME.parent/'catalog.bin']
for ent in registrations:
 cat=cm.Catalog(catalog);loc=cat.locations(ent['source_guid'])[0];catalog=cat.add_key_location(ent['guid'],loc,loc)
cat=cm.Catalog(catalog);key='GameWorldVisualTreeAssetPreload';extra=[cat.locations(ent['guid'])[0] for ent in registrations]
idx=next(i for i,(k,_) in enumerate(cat.keys()) if k==key);ko,ls=cat.key_records[idx];locs=[v[0] for v in cat.array(ls,'I')]+extra
records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog=bytes(cat.data)
oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);newcat=cm.Catalog(catalog);nk=dict(newcat.keys())
assert set(nk)==set(dict(oldcat.keys()))|{e['guid'] for e in registrations}
for k,l in oldcat.keys():assert [v[0] for v in newcat.array(nk[k],'I')]==[v[0] for v in oldcat.array(l,'I')]+(extra if k==key else [])

migration_code='import copy\nTARGETS='+repr(targets)+'''
def migrate_layout(document,forward=True,version=None,limits_from=None,layout_name=None):
 if not forward:
  assert limits_from is not None,'Original cache backup required'
  return copy.deepcopy(limits_from)
 result=copy.deepcopy(document);name=layout_name or result['m_Name'];target=TARGETS[name]
 desired=next(c for c in target['m_gridComponents'] if c['m_location']['x']==0 and c['m_location']['y']>0)
 existing=next(c for c in result['m_gridComponents'] if c['m_location']['x']==0 and c['m_location']['y']>0)
 existing.update(m_elementID=desired['m_elementID'],m_configDescriptions=[],m_configDescriptionKeys=[desired['m_elementID']],m_gridElementConfigs=[],m_isLocked=True)
 result['m_compositionVersion']=version if version is not None else target['m_compositionVersion']
 return result
'''
migration=types.ModuleType('portal_cache');exec(migration_code,migration.__dict__)
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');cache_previews=[]
for name in targets:
 p=cache_root/name
 if not p.exists():continue
 original=json.loads(p.read_text('utf8'));updated=migration.migrate_layout(original,layout_name=name)
 assert migration.migrate_layout(updated,layout_name=name)==updated
 for a,b in zip(original['m_gridComponents'],updated['m_gridComponents']):
  if a['m_location']['x']!=0 or a['m_location']['y']==0:assert a==b
 assert updated['m_optionalSlices']==original['m_optionalSlices']
 assert migration.migrate_layout(updated,False,limits_from=original)==original
 cache_previews.append(name);(OUT/('preview-'+name+'.json')).write_text(json.dumps(updated,ensure_ascii=False,indent=2),'utf8')

outputs={}
for bn in [W,T]:
 data=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(data).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',bn,pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',bn,pid)
 (OUT/bn).write_bytes(data);outputs[bn]=data
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
for name,data in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode('ascii'))]:(OUT/name).write_bytes(data);outputs[name]=data
report={'choices':dict(zip(IDS,LABELS)),'private_choice_count':13,'default':'ClubTeamReport','private_grid':True,'native_right_choices_preserved':True,'wide_and_compact_templates':choice_audits,'cache_previews':cache_previews,'serialization_roundtrip':True,'unrelated_objects_unchanged':True,'runtime_verified':False}
manifest={'installed':False,'runtime_verified':False,'output':str(OUT),'layout':report,'changes':{bn:{str(pid):t.get('m_Name','AssetBundle') for pid,t in changes[bn].items()} for bn in [W,T]},'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{bn:sha(data) for bn,data in outputs.items()},'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8');(OUT/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':list(outputs),'cache_root':str(cache_root),'cache_versions':versions},ensure_ascii=False,indent=2),'utf8')
(OUT/'grid_migration.py').write_text(migration_code,'utf8')
installer=(R/'install-highlight-layout-with-cache.py').read_text('utf8')
installer=installer.replace('path=folder/name;assert path.parent.resolve()==folder',"path=(folder.parent if tag=='game' and name.startswith('catalog.') else folder)/name;assert path.parent.resolve() in [folder,folder.parent]")
installer=installer.replace("version=versions['before' if restore else 'after'],limits_from=old_limits)","version=versions['before' if restore else 'after'],limits_from=old_limits,layout_name=name)")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'修改说明.md').write_text('左下新增模块改为独立原生网格选择器，候选目录仅13项：'+ '、'.join(LABELS)+'。默认球队报告，既有Portal缓存只重置左下槽位；右侧、中间及收件箱保留。两种尺寸分别使用对应原生模板；独立网格保存切换状态。外层只用于承载嵌套网格，不显示外层切换菜单。新增私有模板、布局与描述，保留原Portal候选并登记承载描述用于缓存重建。通过序列化回读、原资源哈希和缓存迁移检查；游戏内显示、选择器交互及保存尚未验证。restore.ps1恢复本次资源和有备份的Portal缓存。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'choices':13,'default':'球队报告','cache_previews':cache_previews,'runtime_verified':False},ensure_ascii=False),flush=True)
