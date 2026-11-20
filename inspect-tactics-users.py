exec(open('inspect-tactics-portraits.py',encoding='utf-8-sig').read().split('for o in obs.values():')[0])
for o in obs.values():
 if o.type.name!='MonoBehaviour':continue
 n=o.peek_name()
 if 'Tactic' not in n and 'Pitch' not in n:continue
 d=o.read_typetree();s=json.dumps(d)
 if '80969577b6ef2ef41bfd3185d5fb2dff' in s or 'TacticsPositionDetailed' in s or 'TacticsPositionCombined' in s or 'tactics-overview' in s:print(n,[(u['alias'],u['path']) for u in d.get('m_Usings',[])],s[s.find('TacticsPositionDetailed')-100:s.find('TacticsPositionDetailed')+200])
g=UnityPy.load(str(p.parent/'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
for o in g.objects:
 if o.type.name=='MonoBehaviour' and o.peek_name()=='PersonPicture':
  d=o.read_typetree();Path('person-picture-live.json').write_text(json.dumps(d,indent=2));print('PersonPicture',o.path_id)
  r={x['rid']:x for x in d['references']['RefIds']}
  for i,a in r.items():
   if 'data' in a:print(i,a['type'],str(a['data'])[:1800])
