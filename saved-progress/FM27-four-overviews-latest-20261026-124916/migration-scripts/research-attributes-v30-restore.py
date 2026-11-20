import json,re,sys
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
folders=['ui-visualtreeassets_assets_gameworldvisualtreeassetpreload','ui-tablefactories_assets_all','ui-settings_assets_all','ui-datacollections_assets_all']
names={'PlayerAttributesLargeBlock','PlayerAttributesStandardBlock','PlayerAttributesSmallBlock','PlayerViewableAttributeNameFromIndexCell',
    'PlayerAttributesTooltipBlock','AttributeHolderTableFactory','TechnicalAttributesDataTableFactory','MentalAttributesDataTableFactory',
    'PhysicalAttributesDataTableFactory','PlayerAttributesTechnicalTable','PlayerAttributesPhysicalTable','PlayerAttributesMentalTable'}
out=[]
for folder in folders:
    selected=[]
    for p in (R/'FMskin'/folder).glob('*.json'):
        if p.stem in names or (folder=='ui-tablefactories_assets_all' and 'Attribute' in p.stem and any(w in p.stem for w in ['Technical','Physical','Mental','Player'])):
            d=json.loads(p.read_text(encoding='utf-8'));selected.append((p.stem,d['path_id']))
    if not selected:continue
    objects={o.path_id:o for o in UnityPy.load(str(AA/(folder+'.bundle'))).objects}
    for name,pid in selected:
        if pid not in objects:print('missing',name,pid);continue
        t=objects[pid].read_typetree();strings=set();paths=set();raw=[]
        def walk(v,k=''):
            if isinstance(v,dict):
                for kk,x in v.items():walk(x,kk)
            elif isinstance(v,list):
                if k=='m_argumentBytes' and v:
                    b=bytes(v);raw.extend(x.decode('ascii') for x in re.findall(rb'[A-Za-z][A-Za-z0-9_./%# +\-]{3,}',b))
                else:
                    for x in v:walk(x,k)
            elif isinstance(v,str) and v:
                if k=='m_path':paths.add(v)
                if any(x.lower() in v.lower() for x in ['Player','Attribute','Passing','Average','Sum','Acceleration']):strings.add(v)
        walk(t)
        print(json.dumps({'name':name,'pid':pid,'paths':sorted(paths),'strings':sorted(strings),'args':sorted(set(raw))},ensure_ascii=True))
        out.append({'folder':folder,'name':name,'pid':pid,'tree':t})
(R/'attribute-bindings-research-v30.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
