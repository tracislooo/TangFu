"""Install only the two Highlight lower six-page native carousels."""
from pathlib import Path
import json, ast, copy, struct, uuid, importlib.util
R=Path(__file__).parent
T='ui-tileslayouts_assets_all.bundle'
boot=(R/'build-match-ui-avatars-layout.py').read_text('utf8').split('portrait=Doc(W,pid=')[0]
boot=boot.replace('match-ui-avatars-layout-','highlight-six-page-carousel-').replace('NAMES=[W,G,M,F]','NAMES=[G,M,T]').replace('datetime.timedelta(hours=-4)','datetime.timedelta(hours=-6)')
exec(compile(boot,'backup-current-resources','exec'))
main=Doc(G,name='MatchViewer_12x4');asset_clones=[];new_guids={}
source=ast.parse((R/'build-highlight-five-column-native-player-lists.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in source.body if isinstance(x,ast.FunctionDef) and x.name in ['register_clone','clone_doc']],type_ignores=[]),'clone-private-assets','exec'))
source=ast.parse((R/'build-highlight-lower-oop-eightstats-footer.py').read_text('utf8'))
exec(compile(ast.Module(body=[x for x in source.body if isinstance(x,ast.FunctionDef) and x.name=='allptr'],type_ignores=[]),'ptr-helper','exec')) if any(isinstance(x,ast.FunctionDef) and x.name=='allptr' for x in source.body) else None
if 'allptr' not in globals():
 def allptr(v,out):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
   else:
    for x in v.values():allptr(x,out)
  elif isinstance(v,list):
   for x in v:allptr(x,out)
reserved=json.loads((R/'reserved-texture-ids.json').read_text('utf8'))
reserved_ids={int(x['path_id']) for x in reserved['reserved_textures']}
reserved_names={x['name'].lower() for x in reserved['reserved_textures']}
CK='<Configurations>k__BackingField'
def guid_for(bn,pid):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle')
 return next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==pid)
donor=Doc(G,name='LatestScoresAndLiveTableCarousel_4x2')
stats=Doc(G,name='HighlightRestoredNativeEightStats')
stats_guid=guid_for(G,stats.obj.path_id)
descriptors={};audits=[]
for idx,side in enumerate(['Home','Away']):
 pid=-981028000007000-idx*10
 assert pid not in reserved_ids and pid-1 not in reserved_ids
 name='HighlightLower'+side+'SixPageCarousel'
 assert name.lower() not in reserved_names
 doc,guid=clone_doc(donor,name,pid)
 # Remove the donor's two pages; native carousel discovers the six new children.
 for child in list(doc.a(1002)['m_Children']):
  node=child['rid'];ser=doc.a(node)['m_SerializedData']['rid']
  doc.d['references']['RefIds']=[r for r in doc.d['references']['RefIds'] if r['rid'] not in [node,ser]]
  del doc.r[node];del doc.r[ser]
 doc.a(1002)['m_Children']=[];doc.d['m_Usings']=[]
 doc.data(1001)['Parameters']=copy.deepcopy(stats.data(1001)['Parameters'])
 doc.a(1001)['m_Classes']=['height-100-percent','flex-grow-class']
 mapper=doc.add(main,1004,1001,'HighlightLower'+side+'CurrentMatchBindings')
 doc.move(1002,mapper)
 mappings=[('team','match.'+side+'Team',1145176088),('ishometeam','const.True' if side=='Home' else 'const.False',0),('inpossession','const.False',0),('isonmainscreen','const.False',0)]
 doc.data(mapper).update(Mappings=[{'m_serialisedType':0,'from':k,'to':{'m_path':v},'type':{'id':typ}} for k,v,typ in mappings],Mappings_UxmlAttributeFlags=1)
 for node in [1001,mapper,1002]:doc.fill(node);doc.st(node,[(131097,doc.px(0)),(131096,doc.px(0))])
 # Base native carousel saves its page in Session scope. The required second
 # stage fix-highlight-six-page-persistence.py replaces this with Persistent tabs.
 persistence='TF27.Highlight.Lower.'+side+'.SixPages.v1'
 doc.data(1002).update(name='Highlight'+side+'SixPages',name_UxmlAttributeFlags=1,SharedPersistenceID=persistence,SharedPersistenceID_UxmlAttributeFlags=1)
 oop=Doc(G,name='HighlightNative'+side+'OOPHorizontal')
 pages=[('Stats',stats_guid),('OutOfPossession',guid_for(G,oop.obj.path_id)),('LiveTable','c38af786a0ce00c40a23511259e88e19'),('LatestScores','8474a8838367004438fa336257d7dfb1'),('MatchdayInfo','c2d724980d7f32b4b9005898db8174ba'),('MatchEvents','dbda07217faf707419c93266465db7b8')]
 for key,pageguid in pages:
  alias='Highlight'+side+key
  doc.d['m_Usings'].append({'alias':alias,'path':pageguid,'asset':{'m_FileID':0,'m_PathID':0}})
  node=doc.add(donor,1004,1002,key)
  doc.a(node)['m_TemplateAlias']=alias;doc.data(node)['templateId']=alias
  doc.a(node)['m_Classes']=['carousel-page']
  doc.fill(node)
 assert len(doc.a(1002)['m_Children'])==6
 assert doc.data(1002)['SharedPersistenceID']==persistence
 doc.save()
 src=find(T,'PlayerStats'+side+'TeamTileDescription');tree=copy.deepcopy(src.read_typetree());dpid=-981028000007100-idx*10
 assert dpid not in reserved_ids
 ident='HighlightLower'+side+'SixPages'
 cfg=copy.deepcopy(next(c for c in tree[CK] if c['Size']=={'x':5,'y':4}))
 cfg.update(Description={'m_FileID':0,'m_PathID':dpid},AssetRef={'m_AssetGUID':guid,'m_SubObjectName':'','m_SubObjectType':''},Type=1)
 tree.update({'<Name>k__BackingField':ident,'<ID>k__BackingField':ident,CK:[cfg],'<DefaultConfigIndex>k__BackingField':0})
 register_clone(T,src,ident+'Description',dpid,tree)
 descriptors[side]=(ident,dpid,cfg)
 audits.append({'side':side,'template_guid':guid,'descriptor':ident,'page_order':[p[0] for p in pages],'page_guids':[p[1] for p in pages],'session_shared_id':persistence,'persistent_fix_required':'fix-highlight-six-page-persistence.py','default_page_index':0,'new_scope_bindings':mappings})

# Register private block descriptions without replacing any existing choices.
for name in ['MatchExperienceHumanGridElementSet','MatchExperienceGridElementSet']:
 ob=find(T,name);tree=ob.read_typetree();old=copy.deepcopy(tree)
 tree['m_gridElementDescriptions'] += [{'m_FileID':0,'m_PathID':dpid} for ident,dpid,cfg in descriptors.values()]
 assert tree['m_tileGroups']==old['m_tileGroups']
 ob.save_typetree(tree);changes[T][ob.path_id]=tree

versions={}
layout_names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
for name in layout_names:
 ob=find(T,name);tree=ob.read_typetree();old=copy.deepcopy(tree)
 for side,(ident,dpid,cfg) in descriptors.items():
  for block in tree['m_gridComponents']:
   if block['m_location']['y']==4 and block['m_location']['x']==(0 if side=='Home' else 15):
    block.update(m_elementID=ident,m_configDescriptions=[{'m_FileID':0,'m_PathID':dpid}],m_configDescriptionKeys=[],m_gridElementConfigs=[copy.deepcopy(cfg)])
  for binding in tree['m_placementBindings']:
   if binding['m_elementID']=='PlayerStats'+side+'Team':binding['m_elementID']=ident
 tree['m_compositionVersion']+=1
 assert [x['m_location'] for x in tree['m_gridComponents']]==[x['m_location'] for x in old['m_gridComponents']]
 versions[name]={'before':old['m_compositionVersion'],'after':tree['m_compositionVersion']}
 ob.save_typetree(tree);changes[T][ob.path_id]=tree

overview=Doc(M,name='OverviewPrototype')
for record in overview.r.values():
 for group in record.get('data',{}).get('GridCompositionSets',[]):
  bindings=group['m_gridCompositionSetBindings']['m_gridElementBindingData']
  for side,(ident,dpid,cfg) in descriptors.items():
   original=[copy.deepcopy(x) for x in bindings if x['DescriptionAndMapping']['DescriptionName']=='PlayerStats'+side+'Team']
   assert original
   for binding in original:
    binding['DescriptionAndMapping']['DescriptionName']=ident
    if binding['DescriptionAndMapping']['MappingName']=='ishometeam':binding['BindingPath']['m_path']='const.True' if side=='Home' else 'const.False'
   bindings.extend(original)
overview.save()

# Extend bundle containers and preload spans for the new assets only.
for bn in NAMES:
 mo=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=mo.read_typetree();old=copy.deepcopy(meta)
 for c in [c for c in asset_clones if c['bundle']==bn]:
  assert c['pid'] not in reserved_ids
  span=[];allptr(changes[bn][c['pid']],span)
  if 'inlineSheet' in changes[bn][c['pid']]:allptr(changes[bn][changes[bn][c['pid']]['inlineSheet']['m_PathID']],span)
  own={'m_FileID':0,'m_PathID':c['pid']}
  if own not in span:span.append(own)
  meta['m_Container'].append((c['guid'],{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':own}));meta['m_PreloadTable']+=span
 if meta!=old:mo.save_typetree(meta);changes[bn][mo.path_id]=meta

spec=importlib.util.spec_from_file_location('carousel_catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog=before[GAME.parent/'catalog.bin']
for c in asset_clones:
 cat=cm.Catalog(catalog);wanted='UnityEngine.UIElements.VisualTreeAsset' if c['bundle']==G else None
 loc=next(x for x in cat.locations(c['source_guid']) if not wanted or cat.location(x)['type'][1]==wanted)
 catalog=cat.add_key_location(c['guid'],loc,loc)
cat=cm.Catalog(catalog);extras=[cat.locations(c['guid'])[0] for c in asset_clones if c['bundle']==G]
idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx]
records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',p) for p in [v[0] for v in cat.array(ls,'I')]+extras),True))
struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog=bytes(cat.data)
oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);cc=cm.Catalog(catalog);keys=dict(cc.keys())
assert set(keys)==set(dict(oldcat.keys()))|{c['guid'] for c in asset_clones}
for key,loc in oldcat.keys():assert cc.array(keys[key],'I')==oldcat.array(loc,'I')+([(x,) for x in extras] if key=='GlobalVisualTreeAssetPreload' else [])

# Validate owner-first catalog dependencies, including native cross-bundle pages.
catalog_audits=[]
for c in asset_clones:
 loc=next(cc.location(p) for p in cc.locations(c['guid']) if c['bundle']!=G or cc.location(p)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
 deps=[cc.location(p)['internal'] for p in loc['dependencies']]
 assert deps and c['bundle'] in deps[0],(c['name'],deps)
 catalog_audits.append({'name':c['name'],'type':loc['type'][1],'owner_first':True,'dependencies':deps})
for audit in audits:
 wrapper=cc.location(cc.locations(audit['template_guid'])[0]);deps=set(wrapper['dependencies'])
 for guid in audit['page_guids']:
  loc=next(cc.location(p) for p in cc.locations(guid) if cc.location(p)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
  assert set(loc['dependencies'])<=deps,('Missing page dependencies',guid,set(loc['dependencies'])-deps)

outputs={};checks=[]
for bn in NAMES:
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
 assert set(saved)==set(objs[bn]);assert reserved_ids.isdisjoint(set(saved)-set(hashes[bn]))
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h,('Unrelated object changed',bn,pid)
 for pid,tree in changes[bn].items():assert saved[pid].read_typetree()==tree,('Roundtrip mismatch',bn,pid)
 for doc in [x for x in documents if x.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
 dest=OUT/bn;dest.write_bytes(raw);outputs[bn]=dest;checks.append({'bundle':bn,'changed_objects':len(changes[bn]),'unrelated_objects_identical':True})
for pid in [main.obj.path_id,-981025000002000,-981025000002100,stats.obj.path_id,-981028000006100,-981028000006110]:assert pid not in changes[G]
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
tx=[]
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
 for bn in NAMES:
  target=folder/bn;tx.append({'target':str(target),'source':str(outputs[bn]),'backup':str(OUT/('backup-'+tag)/bn),'before':sha(before[target]),'after':sha(outputs[bn].read_bytes())})
 for n,data in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode('ascii'))]:
  dest=OUT/n;dest.write_bytes(data);target=(folder.parent if tag=='game' else folder)/n
  tx.append({'target':str(target),'source':str(dest),'backup':str(OUT/('backup-'+tag)/n),'before':sha(before[target]),'after':sha(data)})
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');caches=[]
for name,ver in versions.items():
 p=cache_root/name
 if not p.exists():continue
 raw=p.read_bytes();tree=json.loads(raw)
 for side,(ident,dpid,cfg) in descriptors.items():
  for block in tree['m_gridComponents']:
   if block['m_location']['y']==4 and block['m_location']['x']==(0 if side=='Home' else 15):block.update(m_elementID=ident,m_configDescriptions=[],m_configDescriptionKeys=[ident],m_gridElementConfigs=[])
  for binding in tree.get('m_placementBindings',[]):
   if binding['m_elementID']=='PlayerStats'+side+'Team':binding['m_elementID']=ident
 tree['m_compositionVersion']=ver['after'];dest=OUT/'cache-output'/name;dest.parent.mkdir(exist_ok=True);dest.write_text(json.dumps(tree,ensure_ascii=False,indent=2),'utf8')
 backup=OUT/'backup-custom'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(raw)
 tx.append({'target':str(p),'source':str(dest),'backup':str(backup),'before':sha(raw),'after':sha(dest.read_bytes())});caches.append(name)
for p in cache_root.iterdir() if cache_root.exists() else []:
 if p.is_file() and p.name not in caches:protected[p]=sha(p.read_bytes())
report={'installed':False,'runtime_verified':False,'output':str(OUT),'wrappers':audits,'versions':versions,'new_assets':asset_clones,'catalog_checks':catalog_audits,'native_carousel_persistence_verified_statically':True,'upper_middle_statistics_and_oop_assets_unchanged':True,'serialization_roundtrip':True,'checks':checks,'cache_migrations':caches,'protected_sha256':{str(p):h for p,h in protected.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8').replace("Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve()}","Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages').resolve(),Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve()}")
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(PYTHON).replace('\\','/')+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) { throw 'Operation failed' }\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('仅Highlight左右下方改为原生圆点轮播：球队统计、对应无球阵型、实时积分榜、最新比分、比赛日信息、赛事。使用六个完整原生页面，不恢复旧空表容器。左右SharedPersistenceID独立且固定，原生Core.Persistence的Persistent生命周期保存页面名及索引，恢复使用当前比赛绑定。首次索引0统计。Type=Block避免外层换模块小三角标题，保留轮播内各页标题及原生圆点。四套Large网格只替换下方槽位，不改位置尺寸，上方、中间、统计表及横向阵型资源原始对象逐字节不变。Catalog新增登记保留旧登记，校验跨包依赖、所属包首依赖与预加载。无纹理变更。静态回读检查通过；游戏内显示、滚动和重启记忆须实际运行验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'pages_per_side':6,'serialization_roundtrip':True,'runtime_verified':False},ensure_ascii=False))
