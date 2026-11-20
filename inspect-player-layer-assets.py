import sys,json
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');P=R/'player-page-layer-inspection'
for n in ['OverviewToggle_FullOverview','OverviewToggle_PortraitAttributes','PlayerReportHeader']:
 s=json.loads((P/(n+'-style.json')).read_text('utf8'));print(n,'assets',s.get('assets'));print('externals not dumped')
for b in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(G/b))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name() or ''
  if n in ['OverviewToggle_FullOverview','OverviewToggle_PortraitAttributes','PlayerReportHeader']:
   print('EXTERNALS',n,[(str(x.name),str(x.path)) for x in o.assets_file.externals])
  if any(x in n.lower() for x in ['gameworld','entitybackground','entity-background','screenbackground','pagebackground']):print('CANDIDATE',n,o.path_id)
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name() or ''
  if n not in ['GameWorldLayout','GameWorldRoot','GameWorldScreen','GameWorldTemplate','GameWorldMain']:continue
  (P/(n+'.json')).write_text(json.dumps(o.read_typetree(),indent=2),'utf8')
