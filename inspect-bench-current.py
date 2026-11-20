from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
root=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');out=Path('inspect-bench-current');out.mkdir(exist_ok=True)
for bn,names in [('ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',['MatchManySubstitutesSmallCard','MatchManySubstitutesRegularCard']),('ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',['SquadOverviewPlayerBlock','SquadOverviewPlayerBlockSmall']),('ui-visualtreeassets_assets_matchvisualtreeassetpreload.bundle',['SquadOverview'])]:
 e=UnityPy.load(str(root/bn));os={o.path_id:o for o in e.objects}
 for name in names:
  o=next(o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);t=o.read_typetree();st=os[t['inlineSheet']['m_PathID']].read_typetree();r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']};(out/(name+'.json')).write_text(json.dumps({'tree':t,'style':st},ensure_ascii=False),'utf8')
  print(name)
  for i,a in r.items():
   if 'm_Parent' not in a:continue
   s=r.get(a.get('m_SerializedData',{}).get('rid'),{});props=st['m_Rules'][a['m_RuleIndex']]['m_Properties'] if a.get('m_RuleIndex',-1)>=0 else []
   if name=='SquadOverview':
    if not ('RowTemplate' in s or 'Substitut' in s.get('name','') or 'Compact' in s.get('name','')):continue
   print(i,a['m_Parent']['rid'],a.get('m_FullTypeName',a.get('m_TemplateAlias')),s.get('name'),{k:v for k,v in s.items() if k in ['FixedElementSize','RowTemplate','Text','Binding']},'style',props if i in [1001,1028] or 'Compact' in s.get('name','') else '')

