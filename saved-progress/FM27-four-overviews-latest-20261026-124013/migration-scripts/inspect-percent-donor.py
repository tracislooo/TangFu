exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
for pid in [-2699943933354802414,-5205389123308821073]:
 d=obs[pid].read_typetree();r={x['rid']:x for x in d['references']['RefIds']};print('\n',d['m_Name'])
 for i,a in r.items():
  v=a.get('data',{})
  if 'm_Parent' in v:print(i,v.get('m_FullTypeName'),v.get('m_Children'),v.get('m_Classes'))
page=obs[-930000000001001].read_typetree();r={x['rid']:x for x in page['references']['RefIds']}
for i,a in r.items():
 v=a.get('data',{})
 if v.get('name','') in ['OverviewFitness_Condition_Above75','OverviewFitness_Condition_Available','OverviewFitness_Condition_Number075'] or 'Condition' in v.get('name','') and a.get('type',{}).get('class')=='BindableSwitchElement/UxmlSerializedData':
  print('PROTO',i,json.dumps(a)[:2700]);break
for f in Path('FMskin/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload').glob('PlayerCondition*.json'):
 d=json.loads(f.read_text());print(f.stem,d['container'])
