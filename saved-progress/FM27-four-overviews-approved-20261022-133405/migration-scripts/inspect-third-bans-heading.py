from pathlib import Path
import sys
sys.path.insert(0,'.codex-deps');import UnityPy
p=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')
e=UnityPy.load(str(p));o=next(o for o in e.objects if o.path_id==-940000000011010);d=o.read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
for i,x in r.items():
 v=x.get('data',{})
 if 'm_SerializedData' in v:
  s=r.get(v['m_SerializedData']['rid'],{}).get('data',{});print(i,v.get('m_FullTypeName'),s.get('name'),v.get('m_Parent'),v.get('m_Children'),v.get('m_Classes'), 'style',v.get('m_RuleIndex'))
print('sheet',d['inlineSheet'])

