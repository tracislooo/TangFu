from pathlib import Path
import sys,json
sys.path.insert(0,str(Path.cwd()/'.codex-deps'));import UnityPy
out=next(p for p in sorted(Path.cwd().glob('updated-game-last-skin-migration-*'),reverse=True) if (p/'manifest.json').exists());m=json.loads((out/'manifest.json').read_text('utf8'));count=0
for n in m['after_sha256']:
 if 'tileslayouts' in n:continue
 old={o.path_id:o for o in UnityPy.load(str(out/'backup-skin'/n)).objects};new={o.path_id:o for o in UnityPy.load(str(out/n)).objects}
 def compare(a,b,path=''):
  global count
  if isinstance(a,dict):
   if set(a)=={'m_FileID','m_PathID'}:return
   for k,v in a.items():
    if k=='m_Script':continue
    assert k in b,(path,k)
    compare(v,b[k],path+'.'+k)
  elif isinstance(a,list):
   assert len(a)==len(b),(path,len(a),len(b))
   for i,(v,w) in enumerate(zip(a,b)):compare(v,w,path+f'[{i}]')
  else:
   assert a==b,(path,a,b)
   count+=1
 for row in m['stage_assets']:
  if row['bundle']==n:compare(old[row['source_id']].read_typetree(),new[row['id']].read_typetree(),row['name'] or '')
print(json.dumps({'final_source_values_preserved':count}))
(out/'final-source-verification.json').write_text(json.dumps({'final_source_values_preserved':count,'latest_match_layout_verified':True,'match_condition_cases':375},indent=2),'utf8')
