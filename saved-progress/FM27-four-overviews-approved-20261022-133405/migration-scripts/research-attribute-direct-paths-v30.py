import json,re,sys,struct
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
names=['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload','ui-visualtreeassets_assets_globalvisualtreeassetpreload','ui-settings_assets_all','ui-visualfunctions_assets_all']
hits=[];funcs=[]
for name in names:
    for o in UnityPy.load(str(AA/(name+'.bundle'))).objects:
        if o.type.name!='MonoBehaviour':continue
        raw=o.get_raw_data()
        if b'AttributePassing' in raw or b'AttributeAcceleration' in raw or b'SumIntArgs' in raw or b'AttributesTechnicalSummary' in raw or b'AttributeCategoryAverage' in raw or b'AttributesPhysicalSummary' in raw:
            t=o.read_typetree();texts=set();args=[]
            def walk(v,k=''):
                if isinstance(v,dict):
                    for kk,x in v.items():walk(x,kk)
                elif isinstance(v,list):
                    if k=='m_argumentBytes' and v:
                        args.extend(x.decode('ascii') for x in re.findall(rb'[A-Za-z][A-Za-z0-9_./%# +\-]{3,}',bytes(v)))
                    else:
                        for x in v:walk(x,k)
                elif isinstance(v,str) and (any(x in v for x in ['Attribute','Sum','Args']) or k=='m_path'):texts.add(v)
            walk(t)
            row={'bundle':name,'pid':o.path_id,'name':t['m_Name'],'strings':sorted(texts),'args':sorted(set(args))}
            hits.append(row);print(json.dumps(row,ensure_ascii=True))
        if name=='ui-visualfunctions_assets_all':
            t=o.read_typetree();n=t['m_Name'];classes=[r['type']['class'] for r in t.get('references',{}).get('RefIds',[])]
            if any(x in n.lower() for x in ['sum','average','arithm','math']) or any(any(w in c.lower() for w in ['sumint','average','addint','divide','multiply']) for c in classes):
                row={'pid':o.path_id,'name':n,'inputs':[(x['m_name'],x['m_type']['m_typeString'].split(',')[0]) for x in t.get('m_inputs',[])],'nodes':classes}
                funcs.append({'info':row,'tree':t});print(json.dumps(row,ensure_ascii=True))
(R/'attribute-direct-path-evidence-v30.json').write_text(json.dumps(hits,ensure_ascii=False,indent=2),encoding='utf-8')
(R/'attribute-arithmetic-functions-v30.json').write_text(json.dumps(funcs,ensure_ascii=False,indent=2),encoding='utf-8')
meta=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes()
sections=[struct.unpack_from('<III',meta,8+i*12) for i in range(31)]
keys=[]
for i in range(sections[0][2]-1):
    a,b=struct.unpack_from('<II',meta,sections[0][0]+i*4)
    txt=meta[sections[1][0]+a:sections[1][0]+b].decode('utf-8',errors='replace')
    if txt.startswith('Attribute') and len(txt)<50:keys.append(txt)
print('attribute keys',json.dumps(keys))
(R/'attribute-key-names-v30.json').write_text(json.dumps(keys,indent=2),encoding='utf-8')
