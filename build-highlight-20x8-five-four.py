from pathlib import Path
import copy,json
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'
s=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-20x8-five-four-').replace("'NAMES=[W,G]'","'NAMES=[T]'").replace('bases=(W,G)','bases=(T,)')
exec(compile(s,'backup-current-grid','exec'))
CK='<Configurations>k__BackingField';tx=[];audits=[];defaults={};names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague']
positions=[(0,0,3,5),(3,0,4,5),(7,0,6,5),(13,0,4,5),(17,0,3,5),(0,5,5,3),(5,5,5,3),(10,5,5,3),(15,5,5,3)]
def tree(bn,pid):return copy.deepcopy(changes[bn].get(pid,objs[bn][pid].read_typetree()))
def save(bn,pid,tr):objs[bn][pid].save_typetree(tr);changes[bn][pid]=tr
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 bn=bases[0]+suffix
 def config(pid,w,h,chosen=None):
  d=tree(bn,pid);cs=d[CK]
  found=next((c for c in cs if c['Size']=={'x':w,'y':h} and (chosen is None or c['AssetRef']==chosen)),None)
  if found:return copy.deepcopy(found)
  matches=[c for c in cs if chosen is None or c['AssetRef']==chosen];assert matches,(pid,chosen)
  c=copy.deepcopy(min(matches,key=lambda c:abs(c['Size']['x']-w)+abs(c['Size']['y']-h)));c['Size']={'x':w,'y':h};c['Description']={'m_FileID':0,'m_PathID':pid};d[CK].append(c);save(bn,pid,d);return copy.deepcopy(c)
 for name in names:
  ob=find(bn,name);tr=tree(bn,ob.path_id);old=tr['m_gridComponents'];assert len(old)==7,(tag,name,len(old))
  reg=tree(bn,tr['m_gridElementSet']['m_PathID']);refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:refs+=group['m_tiles']
  descs={tree(bn,r['m_PathID']).get('<ID>k__BackingField'):r['m_PathID'] for r in refs}
  mids=[]
  for ident in ['LiveTable','LatestScores']:
   pid=descs[ident];b=copy.deepcopy(old[5]);b.update(m_elementID=ident,m_configDescriptions=[{'m_FileID':0,'m_PathID':pid}],m_configDescriptionKeys=[],m_gridElementConfigs=[config(pid,5,3)]);mids.append(b)
  blocks=copy.deepcopy(old[:6])+mids+[copy.deepcopy(old[6])]
  for b,(x,y,w,h) in zip(blocks,positions):
   b['m_location']={'x':x,'y':y,'width':w,'height':h};b['m_minSize']={'x':w,'y':h};b['m_maxSize']={'x':w,'y':h}
   b['m_gridElementConfigs']=[config(c['Description']['m_PathID'],w,h,c['AssetRef']) for c in b['m_gridElementConfigs']]
  # Every entry of the existing private native menus remains selectable at 5x3.
  for pid in set(descs.values()):
   if tree(bn,pid).get(CK):config(pid,5,3)
  tr['m_gridComponents']=blocks;tr['m_layoutPreset']={'Name':'','Size':{'x':20,'y':8}};tr['m_optionalSlices']['m_instantiationOrder']=list(range(9));tr['m_compositionVersion']+=1
  tr['m_placementBindings']=[{'m_elementID':b['m_elementID'],'m_optionalConditions':[],'m_optionalConfigConditions':[]} for b in blocks]
  cells=[(x,y) for b in blocks for x in range(b['m_location']['x'],b['m_location']['x']+b['m_location']['width']) for y in range(b['m_location']['y'],b['m_location']['y']+b['m_location']['height'])];assert len(cells)==len(set(cells))==160;assert all(0<=x<20 and 0<=y<8 for x,y in cells)
  save(bn,ob.path_id,tr)
  if tag=='game':defaults[name]=copy.deepcopy(tr)
  audits.append({'variant':tag,'layout':name,'slots':[{k:b[k] for k in ['m_elementID','m_location']} for b in blocks],'full_grid_coverage':True})
 metaob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=metaob.read_typetree()
 def ptrs(v,out):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
   else:
    for x in v.values():ptrs(x,out)
  elif isinstance(v,list):
   for x in v:ptrs(x,out)
 for key,entry in meta['m_Container']:
  pid=entry['asset']['m_PathID']
  if pid not in changes[bn]:continue
  span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span);entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
 metaob.save_typetree(meta);changes[bn][metaob.path_id]=meta
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
 for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr
 src=OUT/(('skin-' if suffix else '')+bases[0]);src.write_bytes(raw);target=folder/bases[0];tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/bases[0]),'before':sha(before[target]),'after':sha(raw)})
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');migrations=[]
for name,tr in defaults.items():
 p=cache_root/name
 if not p.exists():continue
 data=p.read_bytes();old=json.loads(data.decode('utf8'));assert len(old['m_gridComponents'])==7
 # Keep each existing slot's selected page and relocate it to the matching new slot.
 for oi,ni in enumerate([0,1,2,3,4,5,8]):
  prev=old['m_gridComponents'][oi];cur=tr['m_gridComponents'][ni]
  assert prev['m_elementID']==cur['m_elementID']
  for key in ['m_configDescriptionKeys']:cur[key]=copy.deepcopy(prev[key])
  chosen=prev['m_gridElementConfigs'][0]['AssetRef'];assert any(c['AssetRef']==chosen for c in cur['m_gridElementConfigs']),'Custom choice requires matching size configuration'
 backup=OUT/'backup-cache'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(data);src=OUT/('cache-'+name+'.json');raw=json.dumps(tr,ensure_ascii=False,indent=2).encode('utf8');src.write_bytes(raw);tx.append({'target':str(p),'source':str(src),'backup':str(backup),'before':sha(data),'after':sha(raw)});migrations.append(name)
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'grid':[20,8],'upper_lower':[5,3],'upper_columns':[3,4,6,4,3],'lower_columns':[5,5,5,5],'checks':audits,'serialization_roundtrip':True,'unrelated_objects_identical':True,'cache_migrations':migrations,'protected_sha256':{}},ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if migrations:installer=installer.replace('for row in tx:\n',"allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
print(OUT)
