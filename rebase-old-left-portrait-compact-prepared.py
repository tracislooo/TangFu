from pathlib import Path
import sys,ast,copy,json,hashlib,subprocess
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
t=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,ast.FunctionDef)and n.name=='write'],type_ignores=[]),'serializer','exec'));TypeTreeHelper.write_value=write
out=Path(json.loads((R/'old-left-portrait-compact-details-prepared.json').read_text('utf8'))['output']);tx=json.loads((out/'transaction.json').read_text('utf8'));sha=lambda b:hashlib.sha256(b).hexdigest();PAGE=-941100000001010;FC=-950000000000162;KEY='4874947676d35ad2bcc95789754f22e0'
for attempt in range(5):
 for row in tx:
  if not row['target'].endswith('.bundle'):continue
  target=Path(row['target']);before=target.read_bytes()
  if sha(before)==row['before']:continue
  print('Rebasing latest '+str(target)+' attempt '+str(attempt+1),flush=True)
  old={o.path_id:o for o in UnityPy.load(row['backup']).objects};patch={o.path_id:o for o in UnityPy.load(row['source']).objects};env=UnityPy.load(before);oo={o.path_id:o for o in env.objects}
  assert oo[PAGE].get_raw_data()==old[PAGE].get_raw_data(),'Target portrait was concurrently edited'
  assert oo[FC].get_raw_data()==old[FC].get_raw_data(),'Source FC was concurrently edited'
  pd=patch[PAGE].read_typetree();sid=pd['inlineSheet']['m_PathID'];baseline={i:sha(o.get_raw_data())for i,o in oo.items()}
  for i in [PAGE,sid]:oo[i].save_typetree(patch[i].read_typetree())
  output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
  assert check.keys()==oo.keys()
  for i,h in baseline.items():
   if i not in [PAGE,sid]:assert sha(check[i].get_raw_data())==h,('Unrelated object changed',i)
  assert check[PAGE].read_typetree()==pd
  Path(row['backup']).write_bytes(before);Path(row['source']).write_bytes(output);row.update(before=sha(before),after=sha(output))
 (out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
 result=subprocess.run([sys.executable,str(out/'installer.py'),str(out)],capture_output=True,text=True)
 print(result.stdout,flush=True)
 if result.returncode==0:break
 print(result.stderr[-1100:],flush=True)
else:raise RuntimeError('Concurrent resource updates prevented installation')
