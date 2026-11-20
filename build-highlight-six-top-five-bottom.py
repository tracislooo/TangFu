from pathlib import Path
import json,copy,ast,struct,uuid,hashlib,importlib.util
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-six-top-five-bottom-').replace("'NAMES=[W,G]'","'NAMES=[G,T]'").replace('bases=(W,G)','bases=(G,T)')
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

def config(pid,w,h,asset=None):
 desc=tree(T,pid);found=next((c for c in desc[CK] if c['Size']=={'x':w,'y':h} and (asset is None or c['AssetRef']==asset)),None)
 if found:return copy.deepcopy(found)
 candidates=[c for c in desc[CK] if asset is None or c['AssetRef']==asset];assert candidates,(pid,w,h,asset)
 c=copy.deepcopy(min(candidates,key=lambda c:abs(c['Size']['x']-w)+abs(c['Size']['y']-h)));c['Size']={'x':w,'y':h};c['Description']={'m_FileID':0,'m_PathID':pid};desc[CK].append(copy.deepcopy(c));save(T,pid,desc);return c

for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G,T=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4');source_guids={};dependency_sources={}
 for index,side in enumerate(['Home','Away']):
  source=Doc(G,name='HighlightFiveAnalysis'+side+'Vertical');oop,guid=clone_doc(source,'HighlightSixColumns'+side+'OutOfPossession',-981111000010000-index*10);source_guids[guid]=asset_guid(G,source.obj.path_id)
  selected=[]
  for r in oop.r.values():
   s=r.get('data',{})
   for v in s.get('ValueVariables',[]):
    if v['m_name'].startswith('SelectedFormation'):
     val=v['m_scopeValue']['m_serializedData'];val=val.replace('Int|0|','Int|1|')
     if v['m_name']!='SelectedFormation':
      import re
      val=re.sub(r'\{[^{}]*SelectedFormation(?:Human|AI|Default)\}', '{HighlightSixColumns'+side+v['m_name']+'}',val)
     v['m_scopeValue']['m_serializedData']=val;selected.append(v['m_name']);assert val.startswith('Int|1|')
   for p in s.get('m_Properties',[]):
    if p.get('name')=='value-vars':
     import re
     p['value']=re.sub(r'(\{SelectedFormation(?:Human|AI|Default)?\}\{)Int\|0\|',r'\1Int|1|',p['value'])
     p['value']=p['value'].replace('Highlight18x10'+side,'HighlightSixColumns'+side)
  assert len(selected)==4
  panels=[oop.data(i) for i,r in oop.r.items() if r.get('data',{}).get('m_FullTypeName')=='FM.UI.FMTacticsPanel']
  assert panels and all(s['Orientation']==0 and s['FlipPositions']==0 for s in panels)
  assert any(s['PositionTemplateAsset']['m_AssetGUID']==asset_guid(G,find(G,'HighlightPhaseSpecificFeetAndCondition').path_id) for s in panels if 'PositionTemplateAsset' in s)
  oop.save()
  d=Doc(G,name='HighlightIntegrated'+side+'StatsAndFormation');original=copy.deepcopy(d.d);row=d.named('IntegratedTeamStatsAndFormationRow');stats=d.named('Fixed'+side+'FirstStatsPageContext');carousel=Doc(G,name='HighlightLower'+side+'SixPageCarousel')
  instance=d.add(carousel,1013,row,side+'OutOfPossessionSelector');alias='HighlightSixColumns'+side+'OOP';d.a(instance)['m_TemplateAlias']=alias;d.data(instance)['templateId']=alias
  d.d['m_Usings'].append({'alias':alias,'path':guid,'asset':{'m_FileID':0,'m_PathID':0}})
  order=[stats,instance,1002] if side=='Home' else [1002,instance,stats]
  for i in order:d.move(i,row)
  for i in order:
   weight=3 if i==stats else 3.5
   d.st(i,[(131105,{'m_ValueType':1,'valueIndex':2}),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,NONE),(131094,NONE),(131082,d.px(0)),(131084,d.num(weight)),(131085,d.num(1))])
  assert d.a(row)['m_Children']==[{'rid':i} for i in order]
  # Every old binding/event remains identical; only new sibling and flex sizing added.
  for i,r in refs(original).items():
   if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,(side,i,'Existing binding changed')
  d.save();dependency_sources[asset_guid(G,d.obj.path_id)]=[guid]
 for name in names:
  ob=find(T,name);tr=tree(T,ob.path_id);old=copy.deepcopy(tr['m_gridComponents']);assert len(old)==8
  regpid=tr['m_gridElementSet']['m_PathID'];reg=tree(T,regpid);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  descs={tree(T,r['m_PathID']).get('<ID>k__BackingField'):r['m_PathID'] for r in description_refs}
  assert 'LiveTable' in descs
  # Full native grid menu, exactly like the existing xG slot, not the custom six-page carousel.
  native=copy.deepcopy(old[6]);native['m_elementID']='LiveTable';native['m_configDescriptions']=[{'m_FileID':0,'m_PathID':descs['LiveTable']}];native['m_configDescriptionKeys']=[];native['m_gridElementConfigs']=[config(descs['LiveTable'],4,3)]
  blocks=[copy.deepcopy(old[i]) for i in [0,2,4,5,1,6]]+[native]
  positions=[(0,0,10,5),(10,0,10,5),(0,5,4,3),(4,5,4,3),(8,5,4,3),(12,5,4,3),(16,5,4,3)]
  for b,(x,y,w,h) in zip(blocks,positions):
   b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h};b['m_gridElementConfigs']=[config(c['Description']['m_PathID'],w,h,c['AssetRef']) for c in b['m_gridElementConfigs']]
  # All native menu choices need the new bottom 4x3 dimensions.
  for pid in set(descs.values()):
   if tree(T,pid).get(CK):config(pid,4,3)
  tr['m_gridComponents']=blocks;tr['m_layoutPreset']={'Name':'','Size':{'x':20,'y':8}};tr['m_optionalSlices']['m_instantiationOrder']=list(range(7));tr['m_compositionVersion']+=1;tr['m_placementBindings']=[{'m_elementID':b['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]} for b in blocks]
  cells=[(x,y) for b in blocks for x in range(b['m_location']['x'],b['m_location']['x']+b['m_location']['width']) for y in range(b['m_location']['y'],b['m_location']['y']+b['m_location']['height'])];assert len(cells)==len(set(cells))==160 and all(0<=x<20 and 0<=y<8 for x,y in cells);save(T,ob.path_id,tr)
  p=cache_root/name
  if tag=='game' and p in cache_before:
   cached=json.loads(cache_before[p].decode('utf8'));previous=cached['m_gridComponents'];assert len(previous)==8;updated=copy.deepcopy(cached);cb=[copy.deepcopy(previous[i]) for i in [0,2,4,5,1,6]]+[copy.deepcopy(native)]
   # Replace instance IDs only on the new native slot; retain all other selections.
   cb[-1]['m_configDescriptions']=[{'instanceID':0}];cb[-1]['m_configDescriptionKeys']=['LiveTable']
   for c in cb[-1]['m_gridElementConfigs']:c['Description']={'instanceID':0};c['Asset']={'instanceID':0}
   for b,(x,y,w,h) in zip(cb,positions):
    b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h}
    for c in b['m_gridElementConfigs']:c['Size']={'x':w,'y':h}
    key=(b.get('m_configDescriptionKeys') or [b['m_elementID']])[0];assert key in descs
    for c in b['m_gridElementConfigs']:config(descs[key],w,h,c['AssetRef'])
   updated['m_gridComponents']=cb;updated['m_layoutPreset']=copy.deepcopy(tr['m_layoutPreset']);updated['m_optionalSlices']=copy.deepcopy(tr['m_optionalSlices']);updated['m_placementBindings']=copy.deepcopy(tr['m_placementBindings']);updated['m_compositionVersion']=tr['m_compositionVersion'];cache_outputs[p]=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
  audits.append({'variant':tag,'layout':name,'grid':[20,8],'upper_lower':[5,3],'upper_columns':[3,3.5,3.5,3.5,3.5,3],'logical_top_slots':[10,10],'bottom_columns':[4]*5,'bottom_order':['MatchMomentum','MatchStatsStandAlone','live pitch and four maps','xGStory','LiveTable native picker'],'native_menu_choices_sized':True,'existing_formation_bindings_preserved':True,'out_of_possession_default':1})
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

(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('20×8网格、上5下3。上方两个10格原生容器，内部各按3/3.5/3.5和3.5/3.5/3布局，总六列为主队统计/无球/有球/客队有球/无球/统计；无球副本默认第二页，保留原生左右脚及选择器、竖向阵型。下方五等宽依次比赛势头/比赛统计/原球场与四图/xG/原生可选区默认实时积分榜。复用当前样式和数据绑定，保留其他原生选择，缓存同步。分别备份游戏与皮肤，restore.ps1哈希保护。文件检查通过，实际游戏内显示尚未验证。','utf8')
print(OUT)

