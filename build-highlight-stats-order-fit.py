from pathlib import Path
import json,copy,ast,struct,uuid,hashlib,importlib.util
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle';V='ui-tableviews_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-stats-order-fit-').replace("'NAMES=[W,G]'","'NAMES=[G,T,V]'").replace('bases=(W,G)','bases=(G,T,V)')
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

def resolve_guid(bn,guid):
 meta=next(o.read_typetree() for o in objs[bn].values() if o.type.name=='AssetBundle');return objs[bn][next(v['asset']['m_PathID'] for k,v in meta['m_Container'] if k==guid)]

for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 G,T,V=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4');source_guids={};dependency_sources={}
 source=Doc(G,name='HighlightRestoredNativeEightStats');stats,statsguid=clone_doc(source,'HighlightUpperGoalsAssistsTallerRows',-981112000010000);source_guids[statsguid]=asset_guid(G,source.obj.path_id)
 raw=bytes(stats.data(1028)['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);import re
 oldviewguid=re.findall(rb'[0-9a-f]{32}',raw)[0].decode();sourceview=resolve_guid(V,oldviewguid);oldview=sourceview.read_typetree();pid=-981112000020000;ob,tr,viewguid=register_clone(V,sourceview,'HighlightUpperGoalsAssistsView',pid,oldview,source_guid=oldviewguid)
 order=['picked-position','player','rating','goals','assists','run','pass%','keyPasses','keyTackles'];cols={c['m_columnID']:c for c in tr['m_tableView']['m_tableConfig']};assert set(cols)==set(order);tr['m_tableView']['m_tableConfig']=[cols[k] for k in order];save(V,pid,tr)
 for node in [1028,1032]:
  s=stats.data(node);assert s['FixedElementSize']==22
  s.update(FixedElementSize=28.,FixedElementSizeControllerOrTouch=28.,FixedElementSize_UxmlAttributeFlags=1,FixedElementSizeControllerOrTouch_UxmlAttributeFlags=1)
  data=bytes(s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert oldviewguid.encode() in data;s['InitFunction']['m_inputs']['m_variable']['m_argumentBytes']=list(data.replace(oldviewguid.encode(),viewguid.encode()))
 for r in stats.r.values():
  for prop in r.get('data',{}).get('m_Properties',[]):
   if isinstance(prop.get('value'),str):prop['value']=prop['value'].replace(oldviewguid,viewguid)
 stats.save()
 for side in ['Home','Away']:
  d=Doc(G,name='HighlightIntegrated'+side+'StatsAndFormation');alias='Highlight'+side+'Stats';u=next(u for u in d.d['m_Usings'] if u['alias']==alias);assert u['path']==source_guids[statsguid];u['path']=statsguid;d.save()
 source=Doc(G,name='MatchStats_4x4');d,compactguid=clone_doc(source,'HighlightCompactMatchStatsThreeByThree',-981112000010010);source_guids[compactguid]=asset_guid(G,source.obj.path_id);unchanged=copy.deepcopy(d.d)
 NONE={'m_ValueType':1,'valueIndex':3};AUTO={'m_ValueType':1,'valueIndex':2}
 # Let the five native comparison rows share the available height; override old minimums.
 for i in [1001,1002,1004,1006,1008,1010]:d.st(i,[(131105,d.pct(100)),(131087,d.pct(100)),(131097,d.px(0)),(131096,d.px(0)),(131095,NONE),(131094,NONE),(131084,d.num(1)),(131085,d.num(1))])
 d.st(1015,[(131096,d.px(0)),(131087,d.px(20)),(131084,d.num(0)),(131085,d.num(0)),(131090,d.px(2)),(131093,d.px(0))])
 d.st(1016,[(131096,d.px(0)),(131087,AUTO),(131082,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131093,d.px(0)),(131090,d.px(0))])
 for i in [1021,1022,1023,1024,1025]:
  d.st(i,[(131096,d.px(0)),(131094,NONE),(131087,AUTO),(131082,d.px(0)),(131084,d.num(1)),(131085,d.num(1)),(131093,d.px(0)),(131090,d.px(0)),(131101,d.px(0)),(131098,d.px(0))])
 for i,r in list(d.r.items()):
  if r.get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':d.st(i,[(65537,d.px(10)),(131096,d.px(0))])
 for i in [1031,1034,1037,1040,1043]:d.st(i,[(65537,d.px(9)),(131087,d.px(12)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131093,d.px(0)),(131090,d.px(0))])
 for i in [1032,1035,1038,1041,1044]:d.st(i,[(131087,d.px(12)),(131096,d.px(0)),(131084,d.num(0)),(131085,d.num(0)),(131093,d.px(0)),(131090,d.px(0))])
 for i,r in refs(unchanged).items():
  if 'm_Parent' not in r.get('data',{}):assert d.r[i]==r,('Comparison binding changed',i)
 d.save()
 changed_descriptions=0
 for name in names:
  ob=find(T,name);layout=tree(T,ob.path_id);reg=tree(T,layout['m_gridElementSet']['m_PathID']);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  descpid=next(r['m_PathID'] for r in description_refs if tree(T,r['m_PathID']).get('<ID>k__BackingField')=='MatchStatsStandAlone');desc=tree(T,descpid)
  for c in desc[CK]:
   if c['AssetRef']['m_AssetGUID']==source_guids[compactguid]:c['AssetRef']['m_AssetGUID']=compactguid
  save(T,descpid,desc);changed_descriptions+=1
  for b in layout['m_gridComponents']:
   for c in b['m_gridElementConfigs']:
    if c['AssetRef']['m_AssetGUID']==source_guids[compactguid]:c['AssetRef']['m_AssetGUID']=compactguid
  save(T,ob.path_id,layout)
  p=cache_root/name
  if tag=='game' and p in cache_before:
   cached=json.loads(cache_before[p].decode('utf8'));updated=copy.deepcopy(cached)
   for b in updated['m_gridComponents']:
    for c in b['m_gridElementConfigs']:
     if c['AssetRef']['m_AssetGUID']==source_guids[compactguid]:c['AssetRef']['m_AssetGUID']=compactguid
   cache_outputs[p]=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
 audits.append({'variant':tag,'column_order':order,'upper_row_height_before':22,'upper_row_height_after':28,'upper_stats_private_template':statsguid,'private_table_view':viewguid,'compact_comparisons_private_template':compactguid,'all_comparison_bindings_preserved':True,'grid_locations_unchanged':True,'shared_stats_and_original_view_unchanged':True})
 # Register new private assets and refresh their complete preload references.
 for bn in [G,T,V]:
  ob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
  for a in [a for a in asset_clones if a['bundle']==bn]:meta['m_Container'].append((a['guid'],{'preloadIndex':0,'preloadSize':0,'asset':{'m_FileID':0,'m_PathID':a['pid']}}))
  for key,entry in meta['m_Container']:
   pid=entry['asset']['m_PathID']
   if pid not in changes[bn]:continue
   span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span)
   if bn==G and pid-1 in changes[bn]:ptrs(changes[bn][pid-1],span)
   entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
  meta['m_Container'].sort(key=lambda x:x[0]);ob.save_typetree(meta);changes[bn][ob.path_id]=meta
 cp=GAME.parent/'catalog.bin' if tag=='game' else SKIN/'catalog.bin';raw=before[cp];new=[a for a in asset_clones if a['bundle'] in [G,T,V]]
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
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes());(OUT/'修改说明.md').write_text('仅上方两端统计使用专用模板和专用表格视图，列序位置/姓名/评分/进球/助攻/跑动/传球成功率/关键传球/关键抢断；行高22→28。原共用统计、轮播与其他视图不变。下方比赛数据使用私有紧凑模板，字体9/10px，五行均分可用高度并取消旧最小高度和垂直空隙。保持20×8及所有位置比例和原绑定，备份/哈希回退齐全。文件检查通过，实际行高与显示待游戏确认。','utf8')
print(OUT)
