exec(open('inspect-tactics-tab-color.py',encoding='utf-8-sig').read().split('for name in [')[0])
for o in UnityPy.load(str(base/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects:
 if o.type.name=='MonoBehaviour' and o.peek_name() in ['TacticalPlannerTeamShapePitchHeader','TacticalPlannerTeamInstructionsPitchHeader']:
  d=o.read_typetree();r={a['rid']:a for a in d['references']['RefIds']}
  print(o.peek_name(),[(i,a['data']['m_FullTypeName'],a['data']['m_Parent']) for i,a in r.items() if 'm_FullTypeName' in a.get('data',{})])
for o in UnityPy.load(str(base/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects:
 if o.type.name=='MonoBehaviour' and o.peek_name()=='TacticalPlannerTeamShapePitchHeader':
  d=o.read_typetree();r={a['rid']:a for a in d['references']['RefIds']};print(r[r[1061]['data']['m_SerializedData']['rid']]['data'])
