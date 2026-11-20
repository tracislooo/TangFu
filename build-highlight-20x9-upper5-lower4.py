from pathlib import Path
import copy,json
R=Path(__file__).parent;T='ui-tileslayouts_assets_all.bundle'
prefix=(R/'fix-bench-card-centering-and-face-number.py').read_text('utf8').split('audits=[];tx=[]')[0].replace('bench-cards-centered-no-face-number-','highlight-20x9-upper5-lower4-').replace("'NAMES=[W,G]'","'NAMES=[T]'").replace('bases=(W,G)','bases=(T,)')
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
   if loc['y']==5:
    assert loc['height']==3;loc['height']=4;b['m_minSize']['y']=4;b['m_maxSize']['y']=4
    b['m_gridElementConfigs']=[config(c['Description']['m_PathID'],loc['width'],4,c['AssetRef']) for c in b['m_gridElementConfigs']]
   else:assert loc['y']==0 and loc['height']==5
  assert bs[:5]==beforetree['m_gridComponents'][:5]
  reg=tree(bn,tr['m_gridElementSet']['m_PathID']);description_refs=list(reg['m_gridElementDescriptions'])
  for group in reg['m_tileGroups']:description_refs+=group['m_tiles']
  for pid in {r['m_PathID'] for r in description_refs}:
   if not tree(bn,pid).get(CK):continue
   for w in [3,4,5]:config(pid,w,4)
  tr['m_layoutPreset']={'Name':'','Size':{'x':20,'y':9}};tr['m_compositionVersion']+=1
  cells=[(x,y) for b in bs for x in range(b['m_location']['x'],b['m_location']['x']+b['m_location']['width']) for y in range(b['m_location']['y'],b['m_location']['y']+b['m_location']['height'])];assert len(cells)==len(set(cells))==180 and all(0<=x<20 and 0<=y<9 for x,y in cells)
  save(bn,ob.path_id,tr)
  if tag=='game':versions[name]=tr['m_compositionVersion']
  audits.append({'variant':tag,'layout':name,'grid':[20,9],'upper_lower':[5,4],'top_five_components_identical':True,'all_module_ids_and_asset_choices_preserved':True,'grid_full_coverage':True})
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
  if loc['y']==5:
   assert loc['height']==3;loc['height']=4;b['m_minSize']['y']=4;b['m_maxSize']['y']=4
   for c in b['m_gridElementConfigs']:c['Size']={'x':loc['width'],'y':4}
  else:assert loc['y']==0 and loc['height']==5
 tr['m_layoutPreset']={'Name':'','Size':{'x':20,'y':9}};tr['m_compositionVersion']=version;backup=OUT/'backup-cache'/name;backup.parent.mkdir(exist_ok=True);backup.write_bytes(data);src=OUT/('cache-'+name+'.json');raw=json.dumps(tr,ensure_ascii=False,indent=2).encode('utf8');src.write_bytes(raw);tx.append({'target':str(p),'source':str(src),'backup':str(backup),'before':sha(data),'after':sha(raw)});migrations.append(name)
(OUT/'transaction.json').write_text(json.dumps(tx,indent=2),'utf8');(OUT/'manifest.json').write_text(json.dumps({'installed':False,'runtime_verified':False,'grid':[20,9],'upper_lower':[5,4],'upper_columns':[4,4,4,4,4],'lower_columns':[5,3,4,3,5],'checks':audits,'cache_migrations':migrations,'serialization_roundtrip':True,'unrelated_objects_identical':True,'protected_sha256':{}},ensure_ascii=False,indent=2),'utf8')
installer=(R/'install-independent-resource-patch.py').read_text('utf8')
if migrations:installer=installer.replace('for row in tx:\n',"allowed.add(Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions').resolve())\nfor row in tx:\n",1)
(OUT/'installer.py').write_text(installer,'utf8')
for mode,name in [('', 'install.ps1'),(' --restore','restore.ps1')]:
 (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+str(PYTHON)+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+mode+"\nif ($LASTEXITCODE -ne 0) {throw 'Failed'}\n",'utf8')
(OUT/'install-after-game-exits.ps1').write_bytes((R/'commentary-bar-left-centered-text-20261025-131528/install-after-game-exits.ps1').read_bytes())
(OUT/'修改说明.md').write_text('Highlight网格由20×8改20×9，上排高5格、下排高4格。上排五列各4格，下排5/3/4/3/5，所有模块顺序/资产引用/选择记忆保留。四套大屏布局及对应本地缓存同步增加下排高度，补全当前私有菜单3×4/4×4/5×4配置。分别备份并增量修改游戏和独立皮肤TilesLayouts，其他模板、图表、头像、替补卡不修改。8套布局180格覆盖/回读/无关对象检查通过，实际显示待游戏验证。restore.ps1带哈希保护。','utf8');print(OUT)
