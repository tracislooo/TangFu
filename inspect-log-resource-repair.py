from pathlib import Path
import sys,json,collections,importlib.util
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
root=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa')
guid='c0b4248e39d6df84d978dd6f8a209dcf'
for label,folder,catpath in [('game',root/'StandaloneWindows64',root/'catalog.bin'),('skin',Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages'),Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages/catalog.bin'))]:
 c=cm.Catalog(catpath.read_bytes());keys={k for k,_ in c.keys() if isinstance(k,str)}
 print(label,'function catalog', [c.location(l) for l in c.locations(guid)] if guid in keys else 'MISSING',flush=True)
 for path in sorted(folder.glob('*.bundle')):
  if not any(s in path.name for s in ['ui-visualtreeassets','ui-styles','gamemodules_assets_gameworld']):continue
  e=UnityPy.load(str(path));counts=collections.Counter();samples=[]
  for o in e.objects:
   if o.type.name=='AssetBundle':
    for k,v in o.read_typetree()['m_Container']:
     if k==guid:print(label,'function object',path.name,v,flush=True)
   if o.type.name!='MonoBehaviour':continue
   d=o.read_typetree()
   if 'm_Rules' not in d:continue
   for ri,rule in enumerate(d['m_Rules']):
    for p in rule['m_Properties']:
     if p['m_Id']!=458753:continue
     for h in p['m_Values']:
      typ=h['m_ValueType'];value=d.get('strings',[])[h['valueIndex']] if typ in [5,7,8] else h['valueIndex']
      counts[str((typ,value))]+=1
      if typ==7 and len(samples)<5:samples.append([o.path_id,d.get('m_Name'),ri,p])
  print(label,path.name,dict(counts),samples,flush=True)
