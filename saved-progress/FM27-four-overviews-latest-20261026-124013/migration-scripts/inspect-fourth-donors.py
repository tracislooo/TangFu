from pathlib import Path
import sys
sys.path.insert(0,'.codex-deps');import UnityPy
p=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');e=UnityPy.load(str(p/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'));o={x.path_id:x for x in e.objects}
for pid,root in [(-930000000001003,1293),(-930000000001001,6298)]:
 d=o[pid].read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
 def tree(i,depth=0):
  a=r[i]['data'];s=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(' '*depth,i,s.get('name'),a.get('m_TemplateAlias'),a.get('m_FullTypeName'))
  for c in a.get('m_Children',[]):tree(c['rid'],depth+1)
 tree(root)
 print('types',len(d.get('m_Usings',[])))
