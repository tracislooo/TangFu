import json
import sys
from pathlib import Path
sys.path.insert(0,'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy
root=Path('G:/Doc/ChatGPT/New project')
rows=json.loads((root/'native-visual-functions-v28.json').read_text(encoding='utf-8'))
d=next(r['tree'] for r in rows if r['tree']['m_Name']=='BindIntComparisonToSwitch')
def compact(v):
    if isinstance(v,dict):
        if set(v)=={'m_idBytes'}: return bytes(v['m_idBytes']).hex()
        return {k:compact(x) for k,x in v.items() if k not in ['m_position','m_parentID']}
    if isinstance(v,list):return [compact(x) for x in v]
    return v
for r in d['references']['RefIds']:
    if r['type']['class'] in ['EntryNode','GeneralVisualFunction_CompareIntInt','GeneralVisualFunction_Branch','BindableSwitchElement_SetVisibleIndex','TypedValueVisualFunctionLibrary_GetInt']:
        print(r['type']['class'],json.dumps(compact(r['data']),ensure_ascii=True))

template=json.loads((root/'native-int-switch-template-v28.json').read_text(encoding='utf-8'))
info=json.loads((root/'native-int-switch-info-v28.json').read_text(encoding='utf-8'))
refs={r['rid']:r for r in template['references']['RefIds']}
sd=refs[info['serialized_rid']]
print('SWITCH_TEMPLATE',json.dumps(compact(sd),ensure_ascii=True))

env=UnityPy.load(str(root/'卡面98总上移10头像70-v27/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
for o in env.objects:
    if o.type.name!='MonoBehaviour':continue
    tree=o.read_typetree()
    if tree.get('m_Name')=='PlayerReportHeaderScoutSection':
        rs={r['rid']:r for r in tree['references']['RefIds']}
        for r in rs.values():
            if r['type']['class']=='BindingRemapper/UxmlSerializedData' and any(m['from']=='player' and m['to']['m_path']=='person' for m in r['data']['Mappings']):
                node=next(n for n in rs.values() if n.get('data',{}).get('m_SerializedData',{}).get('rid')==r['rid'])
                print('REMAPPER_TEMPLATE',json.dumps([node,r],ensure_ascii=True))
                (root/'native-card-remapper-v28.json').write_text(json.dumps([node,r],ensure_ascii=False,indent=2),encoding='utf-8')
        break
