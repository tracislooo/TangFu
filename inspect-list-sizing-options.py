from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
e=UnityPy.load('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle');t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='SquadOverview');r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']}
for i in [1087,1088,1038,1041]:
 s=r[r[i]['m_SerializedData']['rid']];print(i,json.dumps({k:v for k,v in s.items() if not k.endswith('UxmlAttributeFlags') and k not in ['bindings','Binding']},ensure_ascii=False))
