exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
for name in ['PlayerPortraitCell','TacticsPitch','TacticalPlannerCollapsablePitchesSingle']:
 for o in obs.values():
  if o.type.name!='MonoBehaviour' or o.peek_name()!=name:continue
  d=o.read_typetree();r={x['rid']:x for x in d['references']['RefIds']}
  for i,a in r.items():
   if name=='PlayerPortraitCell' and i in [1007,1008,1009]:print(name,i,json.dumps(a))
   if name!='PlayerPortraitCell':
    s=json.dumps(a)
    if '80969577' in s or 'PositionTemplate' in s or 'position-template' in s or 'Combined' in s:print(name,i,s[:4500])
