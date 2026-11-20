import sys,json,importlib.util
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');m=importlib.util.module_from_spec(spec);spec.loader.exec_module(m)
c=m.Catalog(Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/catalog.bin').read_bytes())
f={o.path_id:o for o in UnityPy.load(str(R/'修复函数版本报错-v34/ui-visualfunctions_assets_all.bundle')).objects}
g={o.path_id:o for o in UnityPy.load(str(R/'原生卡面写法检测75-v33/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')).objects}
t=f[468212822105936887].read_typetree()
(R/'private-function-template-v35.json').write_text(json.dumps(t,ensure_ascii=False,indent=2),encoding='utf-8')
print('int nodes',[(r['type']['class'],list(r['data'])) for r in t['references']['RefIds']])
print('function script',t['m_Script'],'fexternals',[(i+1,e.path) for i,e in enumerate(f[468212822105936887].assets_file.externals)])
print('gexternals',[(i+1,e.path) for i,e in enumerate(g[-4194025542157271532].assets_file.externals)])
bundle=next(o for o in g.values() if o.type.name=='AssetBundle').read_typetree()
key=next(k for k,v in bundle['m_Container'] if v['asset']['m_PathID']==-4194025542157271532)
print('banner key',key)
for l in c.locations(key):
    loc=c.location(l);print('bannerloc',json.dumps(loc));print('deps',json.dumps([c.location(d) for d in loc['dependencies']]))
for o in f.values():
    if o.type.name!='MonoBehaviour':continue
    ft=o.read_typetree()
    for r in ft.get('references',{}).get('RefIds',[]):
        if r['type']['class'] in ['TypedValueVisualFunctionLibrary_TryCastToFloat','GeneralVisualFunction_CompareFloatFloat']:
            p=R/(r['type']['class']+'-v35.json')
            if not p.exists():p.write_text(json.dumps(r,indent=2),encoding='utf-8');print('float template',r['type'],list(r['data']))
