exec(open('inspect-update-migration.py',encoding='utf8').read().split('result={}')[0])
bases={names[0]:R/'header-fix/backup'/names[0],names[1]:R/'header-fix/backup'/names[1],names[2]:R/'概览1080紧凑布局-20261016-021018/backup-game'/names[2]}
for n in names:
 oo={o.path_id:o for o in UnityPy.load(str(SKIN/n)).objects};bo={o.path_id:o for o in UnityPy.load(str(bases[n])).objects}
 diffs=[o for pid,o in oo.items() if pid in bo and o.get_raw_data()!=bo[pid].get_raw_data() and o.type.name=='MonoBehaviour' and o.read_typetree()!=bo[pid].read_typetree()]
 print('MODIFIED OLD NATIVE',n,[(o.path_id,o.peek_name() if o.type.name=='MonoBehaviour' else o.type.name) for o in diffs])
 for o in diffs:
  if o.type.name=='MonoBehaviour' and o.peek_name()=='PlayerReportOverview':
   d=o.read_typetree()
   for r in d['references']['RefIds']:
    a=r.get('data',{})
    if 'Bindings' in a:print('PAGEGRID',r['rid'],json.dumps(a['Bindings'])[:7000])
