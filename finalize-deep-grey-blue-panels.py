from pathlib import Path
import sys,json,copy,shutil,ast,hashlib,datetime
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'));TypeTreeHelper.write_value=write
old=R/'panel-background-alpha60-20261102-103548';out=R/('panel-deep-grey-blue60-'+datetime.datetime.now().strftime('%Y%m%d-%H%M%S'));shutil.copytree(old,out)
m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'));tx['sources']={k:v.replace(str(old),str(out)) for k,v in tx['sources'].items()};tx['before']={k:v.replace(str(old),str(out)) for k,v in tx['before'].items()}
for target,source in tx['sources'].items():
 e=UnityPy.load(Path(source).read_bytes());oo={o.path_id:o for o in e.objects};orig={i:o.get_raw_data() for i,o in oo.items()};expected={};roles={c['role'] for c in m['changes'] if c['target']==target}
 for o in oo.values():
  if o.type.name!='MonoBehaviour':continue
  s=o.read_typetree();changed=False
  for r in s.get('m_Rules',[]):
   for p in r['m_Properties']:
    if p.get('m_CustomName') in roles:
     hs=p['m_Values']
     if len(hs)==1 and hs[0]['m_ValueType']==4:
      c=copy.deepcopy(s['colors'][hs[0]['valueIndex']]);c.update(r=38/255,g=52/255,b=69/255);s['colors'].append(c);hs[0]['valueIndex']=len(s['colors'])-1;changed=True
  if changed:o.save_typetree(s);expected[o.path_id]=s
 b=e.file.save(packer='lz4')
 for o in UnityPy.load(b).objects:
  if o.path_id not in expected:assert o.get_raw_data()==orig[o.path_id]
  else:
   now=o.read_typetree()
   for r in now['m_Rules']:
    for p in r['m_Properties']:
     if p.get('m_CustomName') in roles:
      c=now['colors'][p['m_Values'][0]['valueIndex']];assert abs(c['r']-38/255)<1e-6 and abs(c['g']-52/255)<1e-6 and abs(c['b']-69/255)<1e-6 and abs(c['a']-.6)<1e-6
 Path(source).write_bytes(b);m['after_sha256'][target]=hashlib.sha256(b).hexdigest()
for c in m['changes']:c['after'].update(r=38/255,g=52/255,b=69/255)
m['background_color']='#263445';m['background_alpha']=.6
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8');(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8');p=out/'restore.ps1';p.write_text(p.read_text('utf8').replace(str(old),str(out)),'utf8');print(out)
