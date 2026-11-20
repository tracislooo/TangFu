exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
for o in obs.values():
 if o.type.name!='MonoBehaviour':continue
 n=o.peek_name()
 if not (n.startswith('TacticsPosition') or n=='PlayerPortraitCell' or 'Tactics' in n and 'Overview' in n):continue
 d=o.read_typetree();r={x['rid']:x for x in d['references']['RefIds']};sh=obs[d['inlineSheet']['m_PathID']].read_typetree()
 print('\nASSET',n,o.path_id,'USINGS',[(x['alias'],x['path']) for x in d['m_Usings']])
 def walk(i,dep=0):
  a=r[i].get('data',{});s=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(' '*dep,i,a.get('m_FullTypeName'),a.get('m_TemplateAlias'),s.get('name',''), 'classes',a.get('m_Classes'))
  for k,v in s.items():
   if isinstance(v,dict) and ('Binding' in k or k in ['Mappings','Parameters']):print(' '*dep,k,str(v)[:160])
  if a.get('m_RuleIndex',-1)>=0:
   ps=sh['m_Rules'][a['m_RuleIndex']]['m_Properties'];pools={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
   print(' '*dep,'STYLE',[(p['m_Id'],[sh[pools[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pools else h for h in p['m_Values']]) for p in ps])
  for c in a.get('m_Children',[]):walk(c['rid'],dep+1)
 walk(d['m_VisualTree']['rid'])
