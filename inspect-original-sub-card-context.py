from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
bn='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
for tag,p in [('native',Path('match-ui-avatars-layout-20261023-141148/backup-game')/bn),('current',Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')/bn)]:
 e=UnityPy.load(str(p));t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='SquadOverviewPlayerBlock');r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']};print(tag)
 for i in [1001,1004,1005]:print(i,r[i].get('m_Properties'))
