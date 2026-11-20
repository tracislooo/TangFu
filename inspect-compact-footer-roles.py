from pathlib import Path
import sys,json
sys.path.insert(0,'.codex-deps');import UnityPy
p=Path('F:/Steam/steamapps/common/Football Manager 27/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle');e=UnityPy.load(str(p));os={o.path_id:o for o in e.objects}
for name in ['MatchManySubstitutesSmallCard','MatchManySubstitutesRegularCard']:
 t=next(o.read_typetree() for o in e.objects if o.type.name=='MonoBehaviour' and o.peek_name()==name);r={x['rid']:x.get('data',{}) for x in t['references']['RefIds']};st=os[t['inlineSheet']['m_PathID']].read_typetree();print(name)
 def walk(i,level=0):
  a=r[i];s=r.get(a.get('m_SerializedData',{}).get('rid'),{});ps=st['m_Rules'][a['m_RuleIndex']]['m_Properties'] if a.get('m_RuleIndex',-1)>=0 else [];pm={2:'floats',3:'dimensions',4:'colors',7:'strings'}
  props={p['m_Id']:[st[pm[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in pm else v for v in p['m_Values']] for p in ps};print(' '*level,i,a.get('m_FullTypeName') or a.get('m_TemplateAlias'),s.get('name'),a.get('m_Classes'),props)
  for c in a.get('m_Children',[]):
   cs=r.get(r[c['rid']].get('m_SerializedData',{}).get('rid'),{})
   if level<3 and 'MatchCondition' not in cs.get('name',''):walk(c['rid'],level+1)
 walk(1022)

