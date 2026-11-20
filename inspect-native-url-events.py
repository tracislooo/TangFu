import sys,json
from pathlib import Path
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
L=json.loads((R/'current-game-location.json').read_text('utf8'));G=Path(L['bundle_root'])
for name in ['ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(G/name))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  raw=o.get_raw_data()
  if b'https' not in raw and o.peek_name() not in ['MainMenu','MarketingBannerTile_8x2']:continue
  try:d=o.read_typetree()
  except Exception:continue
  for r in d.get('references',{}).get('RefIds',[]):
   sd=r.get('data',{});ev=sd.get('Events',{}).get('m_bytes',[])
   if b'http' in bytes(ev):print(d.get('m_Name'),sd.get('name'),bytes(ev).hex(),repr(bytes(ev)))
   if 'BindingSetter' in r.get('type',{}).get('class',''):print('SETTER',r)
   if 'BindingVariables' in r.get('type',{}).get('class',''):print('VARS',r)
