from pathlib import Path
import copy,json
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-20x8-equal-rows-').replace("'NAMES=[W,G]'","'NAMES=[T]'").replace('bases=(W,G)','bases=(T,)')
exec(compile(prefix,'backup-current-grid-height','exec'))
names=['MatchExperienceHumanGridComposition-Large','MatchExperienceHumanGridComposition-Large-NoLeague','MatchExperienceGridComposition-Large','MatchExperienceGridComposition-Large-NoLeague'];CK='<Configurations>k__BackingField';tx=[];audits=[];versions={}
def tree(bn,pid):return copy.deepcopy(changes[bn].get(pid,objs[bn][pid].read_typetree()))
def save(bn,pid,tr):objs[bn][pid].save_typetree(tr);changes[bn][pid]=tr
for tag,suffix,folder in [('game','',GAME),('skin','::skin',SKIN)]:
 bn=bases[0]+suffix
 def config(pid,w,h,asset=None):
  tr=tree(bn,pid);found=next((c for c in tr[CK] if c['Size']=={'x':w,'y':h} and (asset is None or c['AssetRef']==asset)),None)
  if found:return copy.deepcopy(found)
  candidates=[c for c in tr[CK] if asset is None or c['AssetRef']==asset];assert candidates
  c=copy.deepcopy(min(candidates,key=lambda c:abs(c['Size']['x']-w)+abs(c['Size']['y']-h)));c['Size']={'x':w,'y':h};c['Description']={'m_FileID':0,'m_PathID':pid};tr[CK].append(copy.deepcopy(c));save(bn,pid,tr);return c
 for name in names:
  ob=find(bn,name);tr=tree(bn,ob.path_id);beforetree=copy.deepcopy(tr);bs=tr['m_gridComponents'];assert len(bs)==10
  for b in bs:
   loc=b['m_location']
   if loc['y']==0:assert loc['height']==5;loc['height']=4
   else:assert loc['y']==5 and loc['height']==4;loc['y']=4
   b['m_minSize']['y']=4;b['m_maxSize']['y']=4
   b['m_gridElementConfigs']=[config(c['Description']['m_PathID'],loc['width'],4,c['AssetRef']) for c in b['m_gridElementConfigs']]
  assert [b['m_elementID'] for b in bs]==[b['m_elementID'] for b in beforetree['m_gridComponents']]
  assert [[c['AssetRef'] for c in b['m_gridElementConfigs']] for b in bs]==[[c['AssetRef'] for c in b['m_gridElementConfigs']] for b in beforetree['m_gridComponents']]
  reg=tree(bn,tr['m_gridElementSet']['m_PathID']);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  for pid in {r['m_PathID'] for r in description_refs}:
   if not tree(bn,pid).get(CK):continue
   for w in [3,4,5]:config(pid,w,4)
  tr['m_layoutPreset']={'Name':'','Size':{'x':20,'y':8}};tr['m_compositionVersion']+=1
  cells=[(x,y) for b in bs for x in range(b['m_location']['x'],b['m_location']['x']+b['m_location']['width']) for y in range(b['m_location']['y'],b['m_location']['y']+b['m_location']['height'])];assert len(cells)==len(set(cells))==160 and all(0<=x<20 and 0<=y<8 for x,y in cells)
  save(bn,ob.path_id,tr)
  if tag=='game':versions[name]=tr['m_compositionVersion']
  audits.append({'variant':tag,'layout':name,'grid':[20,8],'upper_lower':[4,4],'all_module_assets_and_order_preserved':True,'all_module_ids_and_asset_choices_preserved':True,'grid_full_coverage':True})
 def ptrs(v,out):
  if isinstance(v,dict):
   if set(v)=={'m_FileID','m_PathID'} and v['m_PathID'] and v not in out:out.append(copy.deepcopy(v))
   else:
    for x in v.values():ptrs(x,out)
  elif isinstance(v,list):
   for x in v:ptrs(x,out)
 ob=next(o for o in objs[bn].values() if o.type.name=='AssetBundle');meta=ob.read_typetree()
 for key,entry in meta['m_Container']:
  pid=entry['asset']['m_PathID']
  if pid not in changes[bn]:continue
  span=[{'m_FileID':0,'m_PathID':pid}];ptrs(changes[bn][pid],span);entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(span));meta['m_PreloadTable']+=span
 ob.save_typetree(meta);changes[bn][ob.path_id]=meta
 raw=env[bn].file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(raw).objects};assert set(saved)==set(objs[bn])
 for pid,h in hashes[bn].items():
  if pid not in changes[bn]:assert sha(saved[pid].get_raw_data())==h
 for pid,tr in changes[bn].items():assert saved[pid].read_typetree()==tr
 src=OUT/(('skin-' if suffix else '')+bases[0]);src.write_bytes(raw);target=folder/bases[0];tx.append({'target':str(target),'source':str(src),'backup':str(OUT/('backup-'+tag)/bases[0]),'before':sha(before[target]),'after':sha(raw)})
cache_root=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions');migrations=[]
for name,version in versions.items():
 p=cache_root/name
 if not p.exists():continue
 data=p.read_bytes();tr=json.loads(data.decode('utf8'));assert len(tr['m_gridComponents'])==10
 for b in tr['m_gridComponents']:
  loc=b['m_location']
  if loc['y']==0:assert loc['height']==5;loc['height']=4
  else:assert loc['y']==5 and loc['height']==4;loc['y']=4
  b['m_minSize']['y']=4;b['m_maxSize']['y']=4
  for c in b['m_gridElementConfigs']:c['Size']={'x':loc['width'],'y':4}
 tr['m_layoutPreset']={'Name':'','Size':{'x':20,'y':8}};tr['m_compositionVersion']=version;backup=OUT/'backup-cache'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(data);src=OUT/('cache-'+name+'.json');raw=json.dumps(tr,ensure_ascii=False,indent=2).encode('utf8');src.write_bytes(raw);tx.append({'target':str(p),'source':str(src),'backup':str(backup),'before':sha(data),'after':sha(raw)});migrations.append(name)
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'grid':[20,8],'upper_lower':[4,4],'upper_columns':[4,4,4,4,4],'lower_columns':[5,3,4,3,5],'checks':audits,'cache_migrations':migrations,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{}},ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if migrations:installer=installer.replace('for row in tx:\n',"allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('Highlight由20×9改为20×8，上排5→4格，下排维持4格并从y5移到y4。上下各占一半。保持上排五等宽4/4/4/4/4及下排5/3/4/3/5、模块顺序、现有模板和原生可选模块选择。分别备份并增量修改游戏与皮肤TilesLayouts及对应自定义缓存。八套布局160格覆盖、资产和模块顺序保留、序列化回读及无关对象检查通过；游戏内显示待验证。restore.ps1带哈希保护。','utf8');print(OUT)
