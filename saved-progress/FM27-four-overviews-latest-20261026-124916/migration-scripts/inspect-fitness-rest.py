exec(open('probe-current-action.py',encoding='utf-8-sig').read().split('for i in')[0])
for n in ['MatchSharpnessBlock','MatchLoadBlock','TrainingLoadBlock','FatigueBlock']:
 j=json.loads((R/'FMskin/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload'/ (n+'.json')).read_text(encoding='utf8'));pid=j['path_id'];print(n,pid,'exists',pid in objects)
 if pid in objects:
  d=objects[pid].read_typetree();print('actualname',d.get('m_Name'));rrx={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
 else:d=j['type_tree'];rrx={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
 for r in rrx.values():
  sd=r.get('data',{});
  if any(k in sd for k in ['DebugDisplay','bindingPath','Parameters']):print(r['rid'],r['type']['class'],{k:v for k,v in sd.items() if k in ['name','DebugDisplay','bindingPath','Parameters']})
