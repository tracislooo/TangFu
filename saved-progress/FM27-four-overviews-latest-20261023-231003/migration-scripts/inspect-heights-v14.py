import sys
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy

ROOT = Path('G:/Doc/ChatGPT/New project')
BASES = [Path('G:/Doc/FM Skin Builder/skins/tf27-01/original'),
         Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages'),
         ROOT / '蓝光200标志间距80-v13']
def summarize(o, style, rid):
    doc = o.read_typetree()
    refs = {r['rid']:r for r in doc['references']['RefIds']}
    r = refs[rid]
    name = refs.get(r['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')
    rule = r['data'].get('m_RuleIndex',-1)
    sd = style.read_typetree()
    values = []
    if rule >= 0:
        for p in sd['m_Rules'][rule]['m_Properties']:
            if p['m_Id'] in [131087,131094,131096,458767,131084,131085,131101,131098]:
                values.append((p['m_Id'], [sd[{2:'floats',3:'dimensions',7:'strings'}[v['m_ValueType']]][v['valueIndex']] if v['m_ValueType'] in [2,3,7] else v for v in p['m_Values']]))
    print('NODE',rid,name,'classes',r['data'].get('m_Classes'), 'height props',values)

for base in BASES:
    print('\nBASE',str(base))
    for bundle,hid,sid in [('ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle',5775949770471550939,-1940069326759809061),('ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle',-4194025542157271532,8045407476604796436)]:
        env = UnityPy.load(str(base/bundle))
        objects = {o.path_id:o for o in env.objects}
        for rid in ([1002,1004,1006,1008,1011,1027] if 'gameworld' in bundle else [1004,1140,1146]):
            try:
                summarize(objects[hid],objects[sid],rid)
            except KeyError:
                pass
        if 'gameworld' in bundle:
            doc = objects[hid].read_typetree()
            print('HEADER GRADIENT CHILDREN',next(r for r in doc['references']['RefIds'] if r['rid']==1004)['data']['m_Children'])
            for pid in [-910000000000201,-910000000000202]:
                if pid in objects:
                    print('UNDERLAY',pid,objects[pid].peek_name())
            if -910000000000201 in objects:
                for rid in [1004,1140,1146,1148]:
                    summarize(objects[-910000000000201],objects[-910000000000202],rid)
            original_objects = [o for o in env.objects if o.type.name=='MonoBehaviour' and o.peek_name()=='inlineStyle']
            matches = []
            for o in original_objects:
                d = o.read_typetree()
                for rule in d['m_Rules']:
                    for sel in rule['m_ComplexSelectors']:
                        if 'report-player-full-header-max' in str(sel):
                            matches.append((o.path_id,sel,rule['m_Properties']))
            print('matching selectors',matches[:10])
