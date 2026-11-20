from pathlib import Path
import json,copy,ast,struct,uuid,hashlib,importlib.util
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-integrated-team-stats-').replace("'NAMES=[W,G]'","'NAMES=[G,T]'").replace('bases=(W,G)','bases=(G,T)')
exec(compile(prefix,'backup-integrated-highlight','exec'))
helper=ast.parse((R/'build-highlight-five-column-native-player-lists.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in helper.body if isinstance(n,ast.FunctionDef) and n.name in ['register_clone','clone_doc']],type_ignores=[]),'clone-private-assets','exec'))
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
CK='<Configurations>k__BackingField';NONE={'m_ValueType':1,'valueIndex':3};asset_clones=[];new_guids={};audits=[];tx=[];cache_outputs={}
names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');cache_before={p:p.read_bytes() for name in names for p in [cache_root/name] if p.exists()}
for p,data in cache_before.items():q=OUT/'backup-cache'/p.name;q.parent.mkdir(exist_ok=True);q.write_bytes(data)
def tree(bn,pid):return copy.deepcopy(changes[bn].get(pid,objs[bn][pid].read_typetree()))
def save(bn,pid,tr):objs[bn][pid].save_typetree(tr);changes[bn][pid]=tr
def asset_guid(bn,pid):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle');return next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==pid)
def ptrs(v,out):
 if isinstance(v,dict):
  if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
  else:
   for x in v.values():ptrs(x,out)
 elif isinstance(v,list):
  for x in v:ptrs(x,out)
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G,T=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4');composites={};source_guids={};dependency_sources={}
 for index,side in enumerate(['Home','Away']):
  source=Doc(G,name='HighlightFiveAnalysis'+side+'OriginalVertical');carousel=Doc(G,name='HighlightLower'+side+'SixPageCarousel');d,guid=clone_doc(source,'HighlightIntegrated'+side+'StatsAndFormation',-981110000010000-index*10);source_guids[guid]=asset_guid(G,source.obj.path_id)
  ve=next(i for i,a in d.r.items() if a.get('data',{}).get('m_FullTypeName')=='UnityEngine.UIElements.VisualElement');row=d.add(d,ve,1001,'IntegratedTeamStatsAndFormationRow')
  d.st(row,[(131083,d.enum('row')),(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
  stats=d.add(d,1006,row,'Fixed'+side+'FirstStatsPageContext');d.data(stats).update(Mappings=[{'m_serialisedType':0,'from':name,'to':{'m_path':path},'type':{'id':typ}} for name,path,typ in [('match','match',1835103331),('team','match.'+side+'Team',1145176088),('ishometeam','const.True' if side=='Home' else 'const.False',0),('fixture','const.NullRef',1718188148),('isonmainscreen','const.False',0)]],Mappings_UxmlAttributeFlags=1)
  instance=d.add(carousel,1013,stats,'Fixed'+side+'StatsFirstPage');alias=carousel.a(1013)['m_TemplateAlias'];d.using(carousel,alias);stats_guid=next(u['path'] for u in carousel.d['m_Usings'] if u['alias']==alias);dependency_sources[guid]=[source_guids[guid],stats_guid]
  d.move(1002,row)
  if side=='Away':d.move(1002,row,0)
  for i in [stats,1002]:d.st(i,[(131105,d.pct(50)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,NONE),(131094,NONE),(131082,d.px(0)),(131084,d.num(1)),(131085,d.num(1))])
  d.st(instance,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131084,d.num(1)),(131085,d.num(1))]);d.save();composites[side]=guid
  assert d.a(row)['m_Children']==([{'rid':stats},{'rid':1002}] if side=='Home' else [{'rid':1002},{'rid':stats}])
 newdesc={};replacements={};first=tree(T,find(T,names[0]).path_id)
 for index,(side,slot) in enumerate([('Home',1),('Away',3)]):
  block=first['m_gridComponents'][slot];oldpid=block['m_configDescriptions'][0]['m_PathID'];original=tree(T,oldpid);pid=-981110000020000-index*10;ob,tr,guid=register_clone(T,objs[T][oldpid],'HighlightIntegrated'+side+'StatsFormationDescription',pid,original,source_guid=asset_guid(T,oldpid))
  c=copy.deepcopy(block['m_gridElementConfigs'][0]);c.update(Description={'m_FileID':0,'m_PathID':pid},Size={'x':8,'y':5},AssetRef={'m_AssetGUID':composites[side],'m_SubObjectName':'','m_SubObjectType':''},Type=1);tr[CK]=[c];save(T,pid,tr);newdesc[side]=(pid,c,tr['<ID>k__BackingField']);replacements[oldpid]=pid
 # Retain the description IDs used by OverviewPrototype and replace their registry references.
 def remap(v):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_FileID']==0 and v['m_PathID'] in replacements:v['m_PathID']=replacements[v['m_PathID']]
   else:
    for x in v.values():remap(x)
  elif isinstance(v,list):
   for x in v:remap(x)
 def config(pid,w,h,asset=None):
  desc=tree(T,pid);found=next((c for c in desc[CK] if c['Size']=={'x':w,'y':h} and (asset is None or c['AssetRef']==asset)),None)
  if found:return copy.deepcopy(found)
  candidates=[c for c in desc[CK] if asset is None or c['AssetRef']==asset];assert candidates,(pid,w,h,asset)
  c=copy.deepcopy(min(candidates,key=lambda c:abs(c['Size']['x']-w)+abs(c['Size']['y']-h)));c['Size']={'x':w,'y':h};c['Description']={'m_FileID':0,'m_PathID':pid};desc[CK].append(copy.deepcopy(c));save(T,pid,desc);return c
 for name in names:
  ob=find(T,name);tr=tree(T,ob.path_id);old=copy.deepcopy(tr['m_gridComponents']);assert len(old)==10 and [b['m_location']['height'] for b in old]==[4]*10
  blocks=[copy.deepcopy(old[1]),copy.deepcopy(old[2]),copy.deepcopy(old[3])]+copy.deepcopy(old[5:])
  for i,side in [(0,'Home'),(2,'Away')]:
   b=blocks[i];pid,c,ident=newdesc[side];assert b['m_elementID']==ident;b['m_configDescriptions']=[{'m_FileID':0,'m_PathID':pid}];b['m_configDescriptionKeys']=[];b['m_gridElementConfigs']=[copy.deepcopy(c)]
  positions=[(0,0,8,5),(8,0,4,5),(12,0,8,5),(0,5,5,3),(5,5,3,3),(8,5,4,3),(12,5,3,3),(15,5,5,3)]
  for b,(x,y,w,h) in zip(blocks,positions):
   b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h};b['m_gridElementConfigs']=[config(c['Description']['m_PathID'],w,h,c['AssetRef']) for c in b['m_gridElementConfigs']]
  regpid=tr['m_gridElementSet']['m_PathID'];reg=tree(T,regpid);remap(reg);save(T,regpid,reg);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  descs={tree(T,r['m_PathID']).get('<ID>k__BackingField'):r['m_PathID'] for r in description_refs}
  for pid in set(descs.values())-set(replacements.values()):
   if tree(T,pid).get(CK):
    for w in [3,4,5]:config(pid,w,3)
  tr['m_gridComponents']=blocks;tr['m_layoutPreset']={'Name':'','Size':{'x':20,'y':8}};tr['m_optionalSlices']['m_instantiationOrder']=list(range(8));tr['m_compositionVersion']+=1;tr['m_placementBindings']=[{'m_elementID':b['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]} for b in blocks]
  cells=[(x,y) for b in blocks for x in range(b['m_location']['x'],b['m_location']['x']+b['m_location']['width']) for y in range(b['m_location']['y'],b['m_location']['y']+b['m_location']['height'])];assert len(cells)==len(set(cells))==160 and all(0<=x<20 and 0<=y<8 for x,y in cells);save(T,ob.path_id,tr)
  p=cache_root/name
  if tag=='game' and p in cache_before:
   cached=json.loads(cache_before[p].decode('utf8'));previous=cached['m_gridComponents'];assert len(previous)==10;updated=copy.deepcopy(cached);cb=[copy.deepcopy(previous[1]),copy.deepcopy(previous[2]),copy.deepcopy(previous[3])]+copy.deepcopy(previous[5:])
   for i,side in [(0,'Home'),(2,'Away')]:
    pid,c,ident=newdesc[side];cb[i]['m_configDescriptions']=[{'instanceID':0}];cb[i]['m_configDescriptionKeys']=[ident];c=copy.deepcopy(c);c['Description']={'instanceID':0};c['Asset']={'instanceID':0};cb[i]['m_gridElementConfigs']=[c]
   for b,(x,y,w,h) in zip(cb,positions):
    b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h}
    for c in b['m_gridElementConfigs']:c['Size']={'x':w,'y':h}
    if y==5:
     key=(b.get('m_configDescriptionKeys') or [b['m_elementID']])[0];assert key in descs
     for c in b['m_gridElementConfigs']:config(descs[key],w,h,c['AssetRef'])
   updated['m_gridComponents']=cb;updated['m_layoutPreset']=copy.deepcopy(tr['m_layoutPreset']);updated['m_optionalSlices']=copy.deepcopy(tr['m_optionalSlices']);updated['m_placementBindings']=copy.deepcopy(tr['m_placementBindings']);updated['m_compositionVersion']=tr['m_compositionVersion'];cache_outputs[p]=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
  audits.append({'variant':tag,'layout':name,'grid':[20,8],'upper_lower':[5,3],'upper_columns':[8,4,8],'lower_columns':[5,3,4,3,5],'fixed_home_stats_left_formation_right':True,'fixed_away_formation_left_stats_right':True,'bottom_choices_and_carousels_preserved':True})
 # Register new private assets and refresh their complete preload references.
 for bn in [G,T]:
  ob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
  for a in [a for a in asset_clones if a['bundle']==bn]:meta['m_Container'].append((a['guid'],{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':a['pid']}}))
  for key,entry in meta['m_Container']:
   pid=entry['asset']['m_PathID']
   if pid not in changes[bn]:continue
   span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span)
   if bn==G and pid-1 in changes[bn]:ptrs(changes[bn][pid-1],span)
   entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
  meta['m_Container'].sort(key=lambda x:x[0]);ob.save_typetree(meta);changes[bn][ob.path_id]=meta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';raw=before[cp];new=[a for a in asset_clones if a['bundle'] in [G,T]]
 for a in new:
  cat=cm.Catalog(raw);sourceguid=source_guids[a['guid']] if a['bundle']==G else a['source_guid'];loc=cat.locations(sourceguid)[0];raw=cat.add_key_location(a['guid'],loc,loc)
 cat=cm.Catalog(raw)
 for guid,sources in dependency_sources.items():
  loc=cat.locations(guid)[0];deps=list(cat.location(loc)['dependencies'])
  for sourceguid in sources:
   for dep in cat.location(cat.locations(sourceguid)[0])['dependencies']:
    if dep not in deps:deps.append(dep)
  struct.pack_into('<I',cat.data,loc+12,cat.append(b''.join(struct.pack('<I',v) for v in deps),True))
 extra=[cat.locations(a['guid'])[0] for a in new if a['bundle']==G];idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GlobalVisualTreeAssetPreload');ko,ls=cat.key_records[idx];records=list(cat.key_records);records[idx]=(ko,cat.append(b''.join(struct.pack('<I',v) for v in [v[0] for v in cat.array(ls,'I')]+extra),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True));catalog=bytes(cat.data)
 verify=cm.Catalog(catalog)
 for a in new:
  loc=verify.locations(a['guid'])[0];assert a['bundle'].split('::')[0] in verify.location(verify.location(loc)['dependencies'][0])['internal']
  if a['bundle']==G:assert loc in [v[0] for v in verify.array(verify.key_records[idx][1],'I')]
 for base in bases:
  bn=base+suffix;raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects}
  for pid,h in hashes[bn].items():
   if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
  for pid,t in changes[bn].items():assert saved[pid].read_typetree()==t
  for doc in [x for x in documents if x.n==bn]:validate_ui(saved[doc.obj.path_id].read_typetree(),saved[doc.sid].read_typetree())
  src=OUT/(('skin-' if suffix else '')+base);src.write_bytes(raw);target=folder/base;tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/base),'before':sha(before[target]),'after':sha(raw)})
 for name,data in [('catalog.bin',catalog),('catalog.hash',hashlib.md5(catalog).hexdigest().encode('ascii'))]:
  target=GAME.parent/name if tag=='game' else SKIN/name;src=OUT/(tag+'-'+name);src.write_bytes(data);tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/name),'before':sha(before[target]),'after':sha(data)})
for p,raw in cache_outputs.items():
 src=OUT/('cache-'+p.name+'.json');src.write_bytes(raw);tx.append({'target':str(p),'source':str(src),'backup':str(OUT/'backup-cache'/p.name),'before':sha(cache_before[p]),'after':sha(raw)})
(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'cache_migrations':[str(p) for p in cache_outputs],'protected_sha256':{}},ensure_ascii=False,indent=2),'utf8');(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if cache_outputs:installer=installer.replace('for row in tx:\n',"allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes());(OUT/'修改说明.md').write_text('Highlight保持20×8，上下改回5:3。删除原上排1/5独立无球阵型槽，原2扩为左8格（主队统计左半、原阵型及选择器右半）；原4扩为右8格（原阵型及选择器左半、客队统计右半）；中间原3仍4格。统计直接实例化原6/10轮播第一页同一原生统计模板，明确match.HomeTeam/false、match.AwayTeam/false及ishometeam真/假绑定，原数据、列、排序、导航与样式复用。下排6—10仍5/3/4/3/5，轮播、选择和中心图表保留。本地自定义缓存同步迁移并保留下排选择。新建2个私有组合VTA及2个描述，描述ID沿用原2/4以复用Overview绑定，替换私有注册表对应引用，目录/Global预加载和跨包依赖校验。序列化及无关对象检查通过，实际显示与交互待游戏验证。分别备份游戏/皮肤，restore.ps1带哈希保护。','utf8');print(OUT)
