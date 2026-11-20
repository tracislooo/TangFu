from pathlib import Path
import sys,json,re,struct
sys.path.insert(0,'.codex-deps');import UnityPy
root=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64')
for short in ['match','global','gameworld']:
 bn='ui-visualtreeassets_assets_'+short+'visualtreeassetpreload.bundle';e=UnityPy.load(str(root/bn));os={o.path_id:o for o in e.objects};ab=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle');lookup={v['asset']['m_PathID']:k for k,v in ab['m_Container']}
 if short!='match':
  for name in ['MatchManySubstitutesSmallCard','MatchManySubstitutesRegularCard','SquadOverviewPlayerBlockSmall','SquadOverviewPlayerBlock']:
   ob=next((o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name),None)
   if ob:print(name,ob.path_id,lookup.get(ob.path_id))
  continue
 t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='SquadOverview');r={v['rid']:v.get('data',{}) for v in t['references']['RefIds']}
 for i,a in r.items():
  if 'm_Parent' not in a:continue
  s=r.get(a.get('m_SerializedData',{}).get('rid'),{});s2={k:v for k,v in s.items() if k in ['name','Mappings','ValueVariables','ReferenceVariables','Parameters','RowTemplate','FixedElementSize','Binding','BindFunction']}
  # summarize all byte args as ASCII to reveal binding paths
  def shorten(v):
   if isinstance(v,dict):return {k:(b' | '.join(re.findall(rb'[ -~]{3,}',bytes(x))).decode() if k in ['m_argumentBytes','m_bytes'] else shorten(x)) for k,x in v.items()}
   if isinstance(v,list):return [shorten(x) for x in v]
   return v
  print(i,a['m_Parent']['rid'],a.get('m_FullTypeName'),json.dumps(shorten(s2),ensure_ascii=False))

