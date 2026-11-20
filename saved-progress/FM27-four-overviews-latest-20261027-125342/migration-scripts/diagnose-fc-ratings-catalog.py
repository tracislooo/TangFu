import sys,json,re,importlib.util
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
sp=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(sp);sp.loader.exec_module(cm)
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa');SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
cats={t:cm.Catalog(p.read_bytes()) for t,p in [('game',GAME/'catalog.bin'),('skin',SKIN/'catalog.bin')]};keys={t:{k for k,_ in c.keys() if isinstance(k,str)} for t,c in cats.items()}
GN='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle';WN='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
known={}
for n in [GN,WN]:
 e=UnityPy.load(str(GAME/'StandaloneWindows64'/n));obs={o.path_id:o for o in e.objects};meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle')
 for k,v in meta['m_Container']:
  if not re.fullmatch('[a-f0-9]{32}',k) or v['asset']['m_FileID']!=0:continue
  o=obs.get(v['asset']['m_PathID'])
  if not o or o.type.name!='MonoBehaviour':continue
  d=o.read_typetree()
  if 'm_nodes' in d:
   known[k]=(n,str(o.path_id),d.get('m_Name',''));print('FUNCTION',k,known[k],{t:k in kk for t,kk in keys.items()})
log=Path.home()/'AppData/LocalLow/Sports Interactive/Football Manager 27/Player.log'
errs={}
for line in log.read_text('utf8',errors='replace').splitlines():
 if not line.startswith('{'):continue
 try:d=json.loads(line)
 except:continue
 m=d.get('Message','')
 if 'Failed to load Visual Function' in m:
  match=re.search(r'Visual Function ([a-f0-9]{32})',m)
  if match:errs.setdefault(match[1],m)
print('LOG_FAILURES',json.dumps(errs,ensure_ascii=False,indent=2))
print('SIZES',[(t,len(k)) for t,k in keys.items()])
