import sys,json
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
out=R/'player-page-layer-inspection';out.mkdir(exist_ok=True)
for b in ['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle','ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle']:
 e=UnityPy.load(str(G/b))
 for o in e.objects:
  if o.type.name!='MonoBehaviour':continue
  n=o.peek_name() or ''
  if n in ['PlayerReport','PlayerReportOverview','GameWorldBackground','GameWorld','PlayerReportHeader','OverviewToggle_FullOverview','OverviewToggle_PortraitAttributes'] or ('background' in n.lower() and ('player' in n.lower() or 'gameworld' in n.lower())):
   t=o.read_typetree();(out/(n+'.json')).write_text(json.dumps(t,ensure_ascii=False,indent=2),'utf8');print(b,n,o.path_id)
   if 'inlineSheet' in t and not t['inlineSheet']['m_FileID'] and t['inlineSheet']['m_PathID']:
    s=o.assets_file.objects[t['inlineSheet']['m_PathID']].read_typetree();(out/(n+'-style.json')).write_text(json.dumps(s,ensure_ascii=False,indent=2),'utf8')
