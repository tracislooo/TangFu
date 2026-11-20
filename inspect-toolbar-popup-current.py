from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
bn='ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle'
for tag,p in [('current',Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')/bn),('native',Path('match-ui-avatars-layout-20261023-141148/backup-game')/bn)]:
 e=UnityPy.load(str(p));o=next(o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='MatchUITacticalOptions');t=o.read_typetree();r={x['rid']:x for x in t['references']['RefIds']}
 print(tag)
 for i in [1018,1048]:
  a=r[i]['data'];s=r[a['m_SerializedData']['rid']]['data'];print(i,{k:s[k] for k in ['ContentTemplate','Anchor','HorizontalAlignment','Anchor_UxmlAttributeFlags','HorizontalAlignment_UxmlAttributeFlags']})
