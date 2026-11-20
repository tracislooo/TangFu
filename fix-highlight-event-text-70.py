from pathlib import Path
import json,copy,ast,struct,uuid,hashlib,importlib.util
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle';V='ui-tableviews_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-event-text-70-').replace("'NAMES=[W,G]'","'NAMES=[G,T]'").replace('bases=(W,G)','bases=(G,T)')
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
 G,T=[n+suffix for n in bases];main=Doc(G,name='MatchViewer_12x4');source_guids={};dependency_sources={}
 source=Doc(G,name='MatchEventsRow');row,rowguid=clone_doc(source,'HighlightMatchEventsRow70Percent',-981113000010000);source_guids[rowguid]=asset_guid(G,source.obj.path_id)
 changed=[]
 for i,a in list(row.r.items()):
  if a.get('data',{}).get('m_FullTypeName')!='SI.Bindable.SIText':continue
  binding=row.data(i).get('TextBinding',{}).get('m_direct',{}).get('Path',{}).get('m_path','')
  if binding in ['row.Player.InitialSurname','row.Player2.InitialSurname']:
   row.st(i,[(65537,row.px(struct.unpack('<f',struct.pack('<f',9.8))[0]))]);changed.append(i)
 assert len(changed)==12
 for i,a in refs(source.d).items():
  if 'm_Parent' not in a.get('data',{}):assert row.r[i]==a
 row.save()
 source=Doc(G,name='MatchEventsTile_4x4');d,compactguid=clone_doc(source,'HighlightMatchEvents70Percent',-981113000010010);source_guids[compactguid]=asset_guid(G,source.obj.path_id)
 for i in [1058,1062]:
  assert d.data(i)['RowTemplate']['m_AssetGUID']==source_guids[rowguid]
  d.data(i)['RowTemplate']['m_AssetGUID']=rowguid
  for prop in d.a(i).get('m_Properties',[]):
   if isinstance(prop.get('value'),str):prop['value']=prop['value'].replace(source_guids[rowguid],rowguid)
 d.save()
 for name in names:
  ob=find(T,name);layout=tree(T,ob.path_id);reg=tree(T,layout['m_gridElementSet']['m_PathID']);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  descpid=next(r['m_PathID'] for r in description_refs if tree(T,r['m_PathID']).get('<ID>k__BackingField')=='MatchEvents');desc=tree(T,descpid)
  assert descpid<0,descpid
  for c in desc[CK]:
   if c['AssetRef']['m_AssetGUID']==source_guids[compactguid]:c['AssetRef']['m_AssetGUID']=compactguid
  save(T,descpid,desc)
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
   if updated!=cached:cache_outputs[p]=json.dumps(updated,ensure_ascii=False,indent=2).encode('utf8')
 audits.append({'variant':tag,'name_labels':changed,'font_before':14,'font_after':9.8,'ratio':0.7,'original_templates_unchanged':True})
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
print(OUT)

