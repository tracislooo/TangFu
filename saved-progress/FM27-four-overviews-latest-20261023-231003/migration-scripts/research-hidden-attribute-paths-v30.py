import json,sys,re
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
folder='ui-tablefactories_assets_all'
objects={o.path_id:o for o in UnityPy.load(str(AA/(folder+'.bundle'))).objects}
allrows=[]
for name in ['PlayerTableFactory','NonPlayerTableFactory']:
    pid=json.loads((R/'FMskin'/folder/(name+'.json')).read_text(encoding='utf-8'))['path_id']
    t=objects[pid].read_typetree();rows=[]
    def paths(v):
        out=[]
        if isinstance(v,dict):
            for k,x in v.items():
                if k=='m_path' and x:out.append(x)
                else:out.extend(paths(x))
        elif isinstance(v,list):
            for x in v:out.extend(paths(x))
        return out
    def walk(v):
        if isinstance(v,dict):
            ident=v.get('m_id','')
            if isinstance(ident,str) and (ident.startswith('hidden-') or any(x in ident for x in ['ambition','loyalty','professional','sportsmanship','temperament','adaptability','pressure','controvers'])):
                rows.append({'id':ident,'paths':sorted(set(paths(v)))})
            else:
                for x in v.values():walk(x)
        elif isinstance(v,list):
            for x in v:walk(x)
    walk(t)
    print(json.dumps({'name':name,'pid':pid,'rows':rows},ensure_ascii=True))
    allrows.append({'name':name,'pid':pid,'rows':rows})
(R/'隐藏属性原生调用证据-V30.json').write_text(json.dumps(allrows,ensure_ascii=False,indent=2),encoding='utf-8')

world={o.path_id:o for o in UnityPy.load(str(AA/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects}
matches=[]
for o in world.values():
    if o.type.name!='MonoBehaviour':continue
    raw=o.get_raw_data()
    if any(k in raw for k in [b'AttributeProfessionalism',b'InjuryProneness',b'.Consistency',b'.ImportantMatches',b'AttributeAmbition',b'AttributePressure']):
        t=o.read_typetree();p=paths(t);argstrings=[]
        def strings(v,k=''):
            if isinstance(v,dict):
                for kk,x in v.items():strings(x,kk)
            elif isinstance(v,list):
                if k=='m_argumentBytes' and v:
                    argstrings.extend(x.decode('ascii') for x in re.findall(rb'[A-Za-z][A-Za-z0-9_.]{4,}',bytes(v)))
                else:
                    for x in v:strings(x,k)
        strings(t)
        row={'name':t['m_Name'],'pid':o.path_id,'paths':[x for x in p if any(k in x for k in ['Professionalism','Ambition','Pressure','Consistency','ImportantMatches','InjuryProneness'])],
            'args':[x for x in argstrings if any(k in x for k in ['Professionalism','Ambition','Pressure','Consistency','ImportantMatches','InjuryProneness'])]}
        matches.append(row)
        print(json.dumps(row,ensure_ascii=True))
(R/'hidden-attributes-ui-evidence-v30.json').write_text(json.dumps(matches,indent=2),encoding='utf-8')
