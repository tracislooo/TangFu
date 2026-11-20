exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
d=obs[-4028782843705546248].read_typetree();r={x['rid']:x for x in d['references']['RefIds']};a=r[1007];print(json.dumps(a));print(json.dumps(r[a['data']['m_SerializedData']['rid']]))
for name in ['TacticsPitch','TacticalPlannerCollapsablePitchesSingle','TacticalPlannerCollapsablePitchesDouble']:
 for o in obs.values():
  if o.type.name=='MonoBehaviour' and o.peek_name()==name:
   for r in o.read_typetree()['references']['RefIds']:
    a=r.get('data',{});
    for k in ['PositionTemplateAsset','ProjectedPositionTemplateAsset']:
     if k in a:print(name,k,a[k])
