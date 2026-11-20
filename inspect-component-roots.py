from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
e=UnityPy.load('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle');t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='SquadOverview');r={x['rid']:x for x in t['references']['RefIds']}
for i in [1004,1005,1006]:print(i,json.dumps(r[i],ensure_ascii=False))
