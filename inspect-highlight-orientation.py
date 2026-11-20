from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
e=UnityPy.load('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')
for name in ['TeamFormationAdaptiveBlock','HighlightHomeHorizontalFormation','HighlightAwayHorizontalFormation']:
 t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']};print(name)
 for i in [1001,1002,1003,1004,1064,1065]:
  a=r[i];s=r.get(a.get('m_SerializedData',{}).get('rid'),{});print(i,a.get('m_FullTypeName'),{k:v for k,v in s.items() if (k in ['Parameters','Mappings','ReferenceVariables','ValueVariables'] or any(q in k for q in ['Orientation','Flip','BindingPath'])) and not k.endswith('UxmlAttributeFlags')})
 print('setters',[(i,a.get('m_FullTypeName')) for i,a in r.items() if 'Setter' in a.get('m_FullTypeName','')])
