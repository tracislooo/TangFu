from pathlib import Path
import ast,copy,datetime,hashlib,importlib.util,json,struct,subprocess,sys
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'<codec>','exec'));TypeTreeHelper.write_value=write
sha=lambda b:hashlib.sha256(b).hexdigest()
GAME=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');L='ui-tileslayouts_assets_all.bundle'
guids=['f4db6cab508a54f5923ce1285e687dd1','7f5394f1ac14510e832ba7ba73485c96']
sp=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
out=R/('preferences-grid-preload-repair-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));out.mkdir();before={};outputs={};audits=[]
for folder in [GAME,SKIN]:
 p=folder/L;before[p]=p.read_bytes();e=UnityPy.load(before[p]);a=e.assets[0];expected={}
 for ob in a.objects.values():
  if ob.type.name!='MonoBehaviour':continue
  name=ob.peek_name()
  if name in ['OnlineGamePreferencesTileDescription','AccessibilityPreferencesTileDescription']:
   d=ob.read_typetree()
   for c in d['<Configurations>k__BackingField']:c['Size']['y']=1
   ob.save_typetree(d);expected[ob.path_id]=d
  elif name in ['PreferenceTFWXPicturesDescription','PreferenceBBDYPicturesDescription']:
   d=ob.read_typetree();variant=copy.deepcopy(d['<Configurations>k__BackingField'][0]);variant['Size']['y']=1
   if not any(x['Size']['y']==1 for x in d['<Configurations>k__BackingField']):d['<Configurations>k__BackingField'].append(variant)
   ob.save_typetree(d);expected[ob.path_id]=d
  elif name in ['OverviewPreferencesFMMenuCardGridComposition','OverviewPreferencesFMMenuCardGridComposition-FMC']:
   d=ob.read_typetree()
   for c in d['m_gridComponents']:
    if c['m_elementID'] in ['OnlineGamePreferences','AccessibilityPreferencesTile','PreferenceTFWXPictures','PreferenceBBDYPictures']:
     isheader=c['m_elementID'] in ['OnlineGamePreferences','AccessibilityPreferencesTile']
     height=1 if isheader or name.endswith('-FMC') else 2
     c['m_location']['height']=height
     if not isheader:c['m_location']['y']=6 if name.endswith('-FMC') else 5
     c['m_minSize']={'x':4,'y':height}
     for config in c['m_gridElementConfigs']:config['Size']={'x':4,'y':height}
   # Check every mandatory rectangle and minimum/configuration size, plus pairwise overlap.
   cells=set()
   for c in d['m_gridComponents']:
    loc=c['m_location'];assert loc['width']>=c['m_minSize']['x'] and loc['height']>=c['m_minSize']['y']
    for config in c['m_gridElementConfigs']:assert config['Size']['x']<=loc['width'] and config['Size']['y']<=loc['height']
    for y in range(loc['y'],loc['y']+loc['height']):
     for x in range(loc['x'],loc['x']+loc['width']):
      assert 0<=x<12 and 0<=y<7 and (x,y) not in cells,(name,c['m_elementID'],x,y)
      cells.add((x,y))
   assert len(cells)==84
   ob.save_typetree(d);expected[ob.path_id]=d
 payload=e.file.save(packer='lz4');check=UnityPy.load(payload).assets[0];original=UnityPy.load(before[p]).assets[0]
 assert set(check.objects)==set(original.objects)
 for pid,obj in check.objects.items():
  if pid in expected:assert obj.read_typetree()==expected[pid]
  else:assert obj.get_raw_data()==original.objects[pid].get_raw_data()
 assert len(expected)==6;outputs[p]=payload
 cp=(GAME.parent if folder==GAME else folder)/'catalog.bin';before[cp]=cp.read_bytes();c=cm.Catalog(before[cp]);label='GlobalVisualTreeAssetPreload';idx=next(i for i,(key,_) in enumerate(c.keys()) if key==label);keyobj,ptr=c.key_records[idx]
 oldlocs=[x[0] for x in c.array(ptr,'I')];extra=[c.locations(g)[0] for g in guids];assert all(c.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' for x in extra)
 locs=oldlocs+[x for x in extra if x not in oldlocs];records=list(c.key_records);records[idx]=(keyobj,c.append(b''.join(struct.pack('<I',x) for x in locs),True));struct.pack_into('<I',c.data,8,c.append(b''.join(struct.pack('<2I',*r) for r in records),True))
 cb=bytes(c.data);cc=cm.Catalog(cb);oc=cm.Catalog(before[cp]);assert all(x in cc.locations(label) for x in extra)
 keymap=dict(cc.keys())
 for key,ptr in oc.keys():
  actual=[x[0] for x in cc.array(keymap[key],'I')]
  if key==label:assert actual==locs
  else:assert actual==[x[0] for x in oc.array(ptr,'I')]
 outputs[cp]=cb;hp=cp.with_name('catalog.hash');before[hp]=hp.read_bytes();outputs[hp]=hashlib.md5(cb).hexdigest().encode('ascii')
 audits.append({'catalog':str(cp),'preload_label':label,'added_template_locations':extra,'existing_keys_and_locations_preserved':True,'mandatory_grid_cells':84,'minimum_and_configuration_sizes_consistent':True})
items=[]
for p,b in outputs.items():
 tag='game' if p.parent in [GAME,GAME.parent] else 'skin';source=Path(tag)/p.name;backup=Path('backup-'+tag)/p.name
 for rel,data in [(source,b),(backup,before[p])]:
  (out/rel).parent.mkdir(exist_ok=True);(out/rel).write_bytes(data)
 items.append({'target':str(p),'source':source.as_posix(),'backup':backup.as_posix(),'before_sha256':sha(before[p]),'after_sha256':sha(b)})
protected={str(p):sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p not in outputs}
m={'installed':False,'runtime_verified':False,'install_files':items,'protected_sha256':protected,'audits':audits,'fixes':['GlobalVisualTreeAssetPreload label membership','Native header configuration height1','Grid minSize1 for headers and2 for pictures']}
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
for action,flag in [('install',''),('restore',' --restore')]:
 (out/(action+'.ps1')).write_text("& '"+sys.executable+"' '"+str(R/'fix-preferences-picture-grid-install.py')+"' '"+str(out)+"'"+flag+'\n','utf8')
assert all(p.read_bytes()==before[p] for p in outputs)
print(out,flush=True);subprocess.run([sys.executable,str(R/'fix-preferences-picture-grid-install.py'),str(out)],check=True)
