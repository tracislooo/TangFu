from pathlib import Path
import sys
sys.path.insert(0,'.codex-deps');import UnityPy
p=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for n,pid,ids in [('gameworld',-940000000010000,[6228,1035,6298,6306,6230,1703,6324]),('global',-940000000010020,[2000,1009,1010,1011])]:
 e=UnityPy.load(str(p/('ui-visualtreeassets_assets_'+n+'visualtreeassetpreload.bundle')))
 d=next(o for o in e.objects if o.path_id==pid).read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
 def tree(i,depth=0):
  x=r[i]['data'];s=r.get(x.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(' '*depth,i,x.get('m_FullTypeName'),s.get('name'), 'parent',x.get('m_Parent'),'template',x.get('m_TemplateAlias'))
  for c in x.get('m_Children',[]):tree(c['rid'],depth+1)
 for i in ids:tree(i)
