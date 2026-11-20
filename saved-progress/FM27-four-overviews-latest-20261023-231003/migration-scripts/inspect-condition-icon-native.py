exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
for o in ge.objects:
 if o.type.name=='MonoBehaviour' and o.peek_name()=='scaling-icons-condition-large':
  d=o.read_typetree();sr={r['rid']:r for r in d['references']['RefIds']};print(o.path_id,d['m_Usings'])
  for r in sr.values():
   a=r.get('data',{});sd=sr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
   if 'm_Parent' in a:print(r['rid'],a.get('m_FullTypeName'),sd.get('Parameters'),sd.get('Binding'))
