import json
import sys
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy
env = UnityPy.load('G:/Doc/ChatGPT/New project/卡面110同步新图片-v23/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle')
objs = {o.path_id: o for o in env.objects}
for doc_id, style_id in [(-4194025542157271532,8045407476604796436),(-910000000000101,-910000000000102)]:
    doc, sheet = objs[doc_id].read_typetree(), objs[style_id].read_typetree()
    refs = {r['rid']:r for r in doc['references']['RefIds']}
    for rid, ref in refs.items():
        d = ref.get('data', {})
        sd = refs.get(d.get('m_SerializedData',{}).get('rid'),{}).get('data',{})
        if (doc_id == -4194025542157271532 and rid in [1132,1162]) or d.get('m_FullTypeName') == 'SI.Bindable.SIImage':
            ix = d.get('m_RuleIndex',-1)
            props = []
            if ix >= 0:
                for p in sheet['m_Rules'][ix]['m_Properties']:
                    if p['m_Id'] in [131087,131105,131089,131104,327681,262153,458768]:
                        props.append([p['m_Id'],[sheet[{2:'floats',3:'dimensions',7:'strings'}[v['m_ValueType']]][v['valueIndex']] for v in p['m_Values']]])
            print(json.dumps({'doc':doc_id,'rid':rid,'name':sd.get('name'),'rule':ix,'props':props},ensure_ascii=True))
