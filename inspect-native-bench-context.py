from pathlib import Path
import sys,json,re
sys.path.insert(0,'.codex-deps');import UnityPy
root=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for short,name in [('match','SquadOverview'),('gameworld','SquadOverviewPlayerBlock-Compact'),('match','SquadOverviewSidebar')]:
 e=UnityPy.load(str(root/('ui-visualtreeassets_assets_'+short+'visualtreeassetpreload.bundle')));ob=next((o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name),None)
 if not ob:continue
 t=ob.read_typetree();r={v['rid']:v.get('data',{}) for v in t['references']['RefIds']};print(name)
 def short(v):
  if isinstance(v,dict):return {k:(b' | '.join(re.findall(rb'[ -~]{3,}',bytes(x))).decode() if k in ['m_argumentBytes','m_bytes'] else short(x)) for k,x in v.items()}
  if isinstance(v,list):return [short(x) for x in v]
  return v
 for i,a in r.items():
  if name=='SquadOverview':
   if i not in [1011,1012,1013,1004,1005,1006,1028,1029]:continue
   s=r.get(a.get('m_SerializedData',{}).get('rid'),{})
   print(i,json.dumps(short(s),ensure_ascii=False))
  elif name.endswith('-Compact'):
   if 'm_Parent' not in a:continue
   s=r.get(a.get('m_SerializedData',{}).get('rid'),{});print(i,a['m_Parent']['rid'],a.get('m_FullTypeName') or a.get('m_TemplateAlias'),s.get('name'))
