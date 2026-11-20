from pathlib import Path
import sys,json,re
sys.path.insert(0,'.codex-deps');import UnityPy
root=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64');out=Path('inspect-highlight-redesign');out.mkdir(exist_ok=True)
for short,names in [('global',['HighlightNativeHomeOOPHorizontal','HighlightNativeAwayOOPHorizontal','HighlightLowerHomeSixPages','HighlightLowerAwaySixPages','MatchViewer_12x4']),('match',['OverviewPrototype'])]:
 bn='ui-visualtreeassets_assets_'+short+'visualtreeassetpreload.bundle';e=UnityPy.load(str(root/bn));os={o.path_id:o for o in e.objects};meta=next(o.read_typetree() for o in e.objects if o.type.name=='AssetBundle');guids={v['asset']['m_PathID']:k for k,v in meta['m_Container']}
 if short=='global':
  for name in names[:]:
   if not any(o.type.name=='MonoBehaviour' and o.peek_name()==name for o in e.objects):names.remove(name)
  names+= [o.peek_name() for o in e.objects if o.type.name=='MonoBehaviour' and 'SixPages' in (o.peek_name() or '') and o.peek_name() not in names]
 for name in names:
  ob=next(o for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);t=ob.read_typetree();r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']};st=os[t['inlineSheet']['m_PathID']].read_typetree();(out/(name+'.json')).write_text(json.dumps({'tree':t,'style':st},ensure_ascii=False,indent=1),'utf8');print(name,ob.path_id,guids.get(ob.path_id),'nodes',len(r))
  if name=='OverviewPrototype':
   for i,a in r.items():
    if 'GridCompositionSets' in a:
     print('GRID',i,json.dumps(a['GridCompositionSets'],ensure_ascii=False)[:1600])
  elif 'OOP' in name:
   for i,a in r.items():
    if 'm_Parent' not in a:continue
    s=r.get(a.get('m_SerializedData',{}).get('rid'),{});print(i,a['m_Parent']['rid'],a.get('m_FullTypeName') or a.get('m_TemplateAlias'),s.get('name'),{k:v for k,v in s.items() if k in ['Mappings','Parameters','Orientation','FlipPositions','OrientationBindingPath']})
  elif 'SixPages' in name:print('usings',t['m_Usings'])
