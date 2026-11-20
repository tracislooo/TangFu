import sys,json
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
out=[]
for bundle in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload']:
    objects=list(UnityPy.load(str(AA/(bundle+'.bundle'))).objects)
    count=0
    for o in objects:
        if o.type.name!='MonoBehaviour':continue
        raw=o.get_raw_data()
        match=b'a82e4cf3a34b1ae41b85cacd4f63208c' in raw
        if not match and (count>=3 or b'BindingSetter' not in raw):continue
        t=o.read_typetree();setters=[r for r in t.get('references',{}).get('RefIds',[]) if 'BindingSetter' in r['type']['class']]
        if match or setters:
            out.append({'bundle':bundle,'name':t['m_Name'],'tree':t,'match':match})
            print(json.dumps({'name':t['m_Name'],'sum_function_match':match,'setters':setters},ensure_ascii=True)[:6000])
            if not match:count+=1
(R/'sum-ui-template-v36.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
