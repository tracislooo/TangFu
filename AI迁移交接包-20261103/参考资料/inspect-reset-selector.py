from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for tag,path in [('new',G/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'),('approved',Path('saved-progress/FM27-four-overviews-approved-20261022-133405/skin-tf27-01/packages/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'))]:
 o={o.path_id:o for o in UnityPy.load(str(path)).objects};d=o[7857044477279960178].read_typetree();print(tag,'HOST')
 for r in d['references']['RefIds']:
  typ=r.get('type',{}).get('class','');v=r.get('data',{})
  if 'BindingVariables' in typ:print('vars',r['rid'],typ,v)
  if 'Bindings' in v and 'm_gridElementBindingData' in v['Bindings']:print('grid',r['rid'],v.get('name'),list(v['Bindings']),len(v['Bindings']['m_gridElementBindingData']))
 for i in [1002,1006]:
  r=next((r for r in d['references']['RefIds'] if r['rid']==i),None);print('node',i,r)
