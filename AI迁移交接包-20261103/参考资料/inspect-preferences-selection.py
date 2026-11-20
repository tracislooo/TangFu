import sys,json
from pathlib import Path
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
G=Path(json.loads(Path('current-game-location.json').read_text())['bundle_root'])
for bn in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle']:
 for o in UnityPy.load(str(G/bn)).objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name() or ''
  if not any(k in n.lower() for k in ['preferences','segmented','radio-button']):continue
  d=o.read_typetree()
  if 'inlineSheet' not in d:continue
  rr={r['rid']:r for r in d['references']['RefIds']};nodes=[]
  for r in rr.values():
   a=r.get('data',{});ty=a.get('m_FullTypeName','');cl=a.get('m_Classes',[])
   if any(k in ty for k in ['Button','Gradient']) or any('active' in c or 'segment' in c for c in cl):nodes.append([r['rid'],ty,cl])
  print(n,o.path_id,json.dumps(nodes))
