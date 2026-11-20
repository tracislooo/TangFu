import json,re,sys,struct
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
def paths(v):
    found=[]
    if isinstance(v,dict):
        for k,x in v.items():
            if k=='m_path' and x:found.append(x)
            else:found.extend(paths(x))
    elif isinstance(v,list):
        for x in v:found.extend(paths(x))
    return found
folder='ui-tablefactories_assets_all'
pid=json.loads((R/'FMskin'/folder/'PlayerTableFactory.json').read_text(encoding='utf-8'))['path_id']
t=next(o for o in UnityPy.load(str(AA/(folder+'.bundle'))).objects if o.path_id==pid).read_typetree()
need=['aerialreach','commandofarea','communication','eccentricity','handling','kicking','oneonones','reflexes','rushingout','tendencytopunch','throwing']
gk=[]
def walk(v):
    if isinstance(v,dict):
        if isinstance(v.get('m_id'),str) and any('attribute'+k in x.lower() for x in paths(v) for k in need):
            gk.append({'id':v['m_id'],'paths':sorted(set(paths(v)))})
        else:
            for x in v.values():walk(x)
    elif isinstance(v,list):
        for x in v:walk(x)
walk(t);print(json.dumps(gk,ensure_ascii=True))
world={o.path_id:o for o in UnityPy.load(str(AA/'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle')).objects}
foot_objects={}
for o in world.values():
    if o.type.name=='MonoBehaviour' and b'Footedness' in o.get_raw_data():
        tt=o.read_typetree()
        if tt['m_Name'].startswith('Footedness'):
            foot_objects[tt['m_Name']]=(o.path_id,tt)
print('available foot UI',list(foot_objects))
feet=[]
for name in ['FootednessBlock','FootednessBlock_6x4','FootednessCard','FootednessCell','FootednessTile_4x2']:
    f=R/'FMskin/ui-visualtreeassets_assets_gameworldvisualtreeassetpreload'/(name+'.json')
    if name not in foot_objects:continue
    pid,tt=foot_objects[name];args=[];mappings=[]
    def get(v,k=''):
        if isinstance(v,dict):
            if 'Mappings' in v:mappings.extend(v['Mappings'])
            for kk,x in v.items():get(x,kk)
        elif isinstance(v,list):
            if k=='m_argumentBytes' and v:
                args.extend(x.decode('ascii') for x in re.findall(rb'[A-Za-z][A-Za-z0-9_.]{4,}',bytes(v)))
            else:
                for x in v:get(x,k)
    get(tt)
    row={'name':name,'pid':pid,'paths':sorted(set(paths(tt))),'argument_strings':sorted(set(x for x in args if 'oot' in x)), 'mappings':mappings}
    feet.append(row);print(json.dumps(row,ensure_ascii=True))
meta=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/il2cpp_data/Metadata/global-metadata.dat').read_bytes();s=[struct.unpack_from('<III',meta,8+i*12) for i in range(31)];keys=[]
for i in range(s[0][2]-1):
    a,z=struct.unpack_from('<II',meta,s[0][0]+i*4);txt=meta[s[1][0]+a:s[1][0]+z].decode('utf-8',errors='replace')
    if len(txt)<65 and ('Footedness' in txt or 'FootString' in txt):keys.append(txt)
print('foot keys',json.dumps(keys))
(R/'门将及左右脚原生调用证据-V30.json').write_text(json.dumps({'goalkeeper_columns':gk,'foot_ui':feet,'foot_registered_keys':keys},ensure_ascii=False,indent=2),encoding='utf-8')
