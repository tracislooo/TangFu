import sys,json,copy,hashlib,ast
from pathlib import Path
R=Path.cwd();sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
from UnityPy.helpers import TypeTreeHelper
oldwrite=TypeTreeHelper.write_value
src=ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'));exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.FunctionDef) and n.name=='write'],type_ignores=[]),'codec','exec'));TypeTreeHelper.write_value=write
out=R/'selection-remnants-lake-20261101-095420';m=json.loads((out/'manifest.json').read_text('utf8'));tx=json.loads((out/'transaction.json').read_text('utf8'))
for target,source in tx['sources'].items():
 if not target.endswith('ui-styles_assets_default.bundle'):continue
 p=Path(source);e=UnityPy.load(p.read_bytes());oo={o.path_id:o for o in e.objects};orig={i:o.get_raw_data() for i,o in oo.items()};ob=next(o for o in oo.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet');s=ob.read_typetree()
 r=next(r for r in reversed(s['m_Rules']) if 'fm27-lake-select-region' in json.dumps(r['m_ComplexSelectors']) and 'unity-slider__dragger' in json.dumps(r['m_ComplexSelectors']));nr=copy.deepcopy(r);nr['m_ComplexSelectors']=nr['m_ComplexSelectors'][:1]
 for c in nr['m_ComplexSelectors']:
  c['ruleIndex']=len(s['m_Rules'])
  for z in c['m_Selectors']:
   for part in z['m_Parts']:
    if part['m_Value']=='unity-base-slider__dragger':part['m_Value']='sislider--dragger'
 s['m_Rules'].append(nr);ob.save_typetree(s);b=e.file.save(packer='lz4')
 for o in UnityPy.load(b).objects:
  if o.path_id==ob.path_id:assert o.read_typetree()==s
  else:assert o.get_raw_data()==orig[o.path_id]
 p.write_bytes(b);m['after_sha256'][target]=hashlib.sha256(b).hexdigest()
(out/'manifest.json').write_text(json.dumps(m,ensure_ascii=False,indent=2),'utf8')
