exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
def show(d):
 r={a['rid']:a for a in d['references']['RefIds']}
 def v(i,dep=0):
  a=r[i].get('data',{});s=r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(' '*dep,i,a.get('m_FullTypeName',r[i]['type']['class']),s.get('name',''),a.get('m_TemplateAlias',''),a.get('m_RuleIndex'))
  for c in a.get('m_Children',[]):v(c['rid'],dep+1)
 print(d['m_Name'],d['inlineSheet']);v(d['m_VisualTree']['rid'])
show(objects[5775949770471550939].read_typetree())
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'));go={o.path_id:o for o in ge.objects}
show(go[-4194025542157271532].read_typetree())
