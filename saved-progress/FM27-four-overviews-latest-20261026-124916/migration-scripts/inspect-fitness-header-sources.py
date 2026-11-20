exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
names=['MatchSharpnessBlock','MatchLoadBlock','InjurySusceptibilityBlock','EnergyBlock','TrainingLoadBlock','InjuryRiskBlock']
for o in objects.values():
 if o.type.name=='MonoBehaviour' and o.peek_name() in names:
  d=o.read_typetree();r={x['rid']:x for x in d['references']['RefIds']};print('\nASSET',o.path_id,d['m_Name']);print('USINGS',d['m_Usings'])
  def walk(i,dep=0):
   a=r[i].get('data',{});s=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   print(' '*dep,i,a.get('m_FullTypeName'),a.get('m_TemplateAlias'),{k:v for k,v in s.items() if k in ['name','bindingPath','Binding','DebugDisplay','Mappings','Parameters','Text','StaticText','BindTextFunction','m_components','SwitchBinding']})
   for c in a.get('m_Children',[]):walk(c['rid'],dep+1)
  walk(d['m_VisualTree']['rid'])
