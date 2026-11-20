exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
def printtree(d,root=None):
 sr={r['rid']:r for r in d['references']['RefIds']}
 def walk(i,dep=0):
  a=sr[i].get('data',{});sd=sr.get(a.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
  print(' '*dep,i,a.get('m_FullTypeName'),a.get('m_TemplateAlias',''),sd.get('name',''),sd.get('DebugDisplay',''))
  for c in a.get('m_Children',[]):walk(c['rid'],dep+1)
 walk(root or d['m_VisualTree']['rid'])
d=objects[FULL].read_typetree();print('USINGS',[(u['alias'],u['path'],u['asset']) for u in d['m_Usings'] if any(s in u['alias'] for s in ['Scout','TeamSection','AttributesTable'])]);printtree(d,1349);printtree(d,1297)
ge=UnityPy.load(str(GAME/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
for e in [env,ge]:
 for o in e.objects:
  if o.type.name=='MonoBehaviour' and o.peek_name() in ['PlayerReportHeaderScoutSection','PlayerReportHeaderMaxTeamSection']:
   td=o.read_typetree();print('ASSET',o.path_id,td['m_Name']);printtree(td)
