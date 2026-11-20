import json
import sys
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
p=R/'修复函数版本报错-v34/ui-visualfunctions_assets_all.bundle'
objects=list(UnityPy.load(str(p)).objects)
bundle=next(o for o in objects if o.type.name=='AssetBundle').read_typetree()
keys={info['asset']['m_PathID']:k for k,info in bundle['m_Container']}
for o in objects:
    if o.type.name!='MonoBehaviour':continue
    t=o.read_typetree();n=t.get('m_Name','')
    if any(x in n.lower() for x in ['visible','comparison','float','double','multiply','scale','map']):
        print(json.dumps({'pid':o.path_id,'guid':keys.get(o.path_id),'name':n,
            'inputs':[(x['m_name'],x['m_type']['m_typeString'].split(',')[0]) for x in t.get('m_inputs',[])],
            'nodes':[r['type']['class'] for r in t.get('references',{}).get('RefIds',[])]}))
    if n=='BindDoubleToVisible':
        (R/'decimal-visible-function-v35.json').write_text(json.dumps(t,indent=2),encoding='utf-8')
