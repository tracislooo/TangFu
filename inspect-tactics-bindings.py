exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
for o in obs.values():
 if o.type.name!='MonoBehaviour':continue
 n=o.peek_name()
 if n in ['TacticsPositionDetailed','TacticsPositionCombined','PersonPicture']:
  d=o.read_typetree();print(n,o.path_id);r={x['rid']:x for x in d['references']['RefIds']}
  if n=='PersonPicture':print(json.dumps(d,indent=2))
  else:
   for i in [1006,1007,1008,1009]:
    if i in r:print(i,json.dumps(r[i])[:2500])
 for us in o.read_typetree().get('m_Usings',[]) if ('Tactic' in n or 'Pitch' in n) else []:
  if us['alias'] in ['TacticsPositionDetailed','TacticsPositionCombined']:print('USER',n,us)
