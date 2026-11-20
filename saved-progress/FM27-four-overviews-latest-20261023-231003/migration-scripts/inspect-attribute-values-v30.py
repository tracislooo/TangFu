import json,sys,re
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
o={o.path_id:o for o in UnityPy.load(str(AA/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects}
out=[]
for n in ['ColouredAttributeCell','ColouredAttributeValueWithBackgroundCell','PlayerAttributeNumberTableCell','OnThePitchComparisonAttributesTab']:
    p=R/'FMskin/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload'/f'{n}.json'
    if not p.exists():continue
    pid=json.loads(p.read_text(encoding='utf-8'))['path_id'];t=o[pid].read_typetree()
    out.append({'name':n,'tree':t});print(n)
    for r in t['references']['RefIds']:
        d=r.get('data',{})
        if any(x in str(d) for x in ['PropertyValue','propertyvalue','DisplayValue','displayvalue']) or 'BindingExpect' in r['type']['class']:
            print(json.dumps(r,ensure_ascii=True)[:2800])
t=o[-224993782040584907].read_typetree()
for r in t['references']['RefIds']:
    if 'person.AttributePassing' in str(r.get('data',{})):
        print('passing mapping',json.dumps(r,ensure_ascii=True))
(R/'attribute-value-wrapper-evidence-v30.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
