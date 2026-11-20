from pathlib import Path
import sys,json,hashlib,importlib.util
r=Path.cwd();sys.path.insert(0,str(r/'.codex-deps'));import UnityPy
loc=json.loads((r/'current-game-location.json').read_text('utf8'));root=Path(loc['bundle_root']);W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle';L='ui-tileslayouts_assets_all.bundle'
for f in [W,L]:
 e=UnityPy.load(str(root/f));oo={o.path_id:o for o in e.objects}
 print('BUNDLE',f)
 for o in oo.values():
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name()or''
  if f==L and ('Overview' in n and any(x in n for x in ['Third','Left','Composition-Large'])):
   d=o.read_typetree();print(o.path_id,n,json.dumps(d,ensure_ascii=False)[:16000])
  if f==W and ('Overview' in n and any(x in n for x in ['Third','Left','Toggle'])):print(o.path_id,n)
 if f==W:
  ab=next(x.read_typetree()for x in oo.values()if x.type.name=='AssetBundle');print('KEYS',[(k,v['asset'])for k,v in ab['m_Container']if v['asset']['m_PathID']in [-940000000010000,-950000000000162]])
  host=oo[7857044477279960178].read_typetree();(r/'binding-audit-host.json').write_text(json.dumps(host,ensure_ascii=False,indent=2),'utf8')
cache=Path.home()/'AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large'
print('CACHE',str(cache));print(cache.read_text('utf8')if cache.exists()else 'missing')
state=json.loads((r/'current-old-left-fc-hidden-overview.json').read_text('utf8'));tx=json.loads((Path(state['manifest']).parent/'transaction.json').read_text('utf8'));print('HASHES',[(x['target'],hashlib.sha256(Path(x['target']).read_bytes()).hexdigest()==x['after'])for x in tx])
