import json
import sys
import uuid
import struct
import re
from pathlib import Path
sys.path.insert(0, 'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy
root = Path('G:/Doc/ChatGPT/New project')
env = UnityPy.load('F:/Steam/steamapps/common/Football Manager 26/fm_Data/StreamingAssets/aa/StandaloneWindows64/ui-visualfunctions_assets_all.bundle')
objs = {o.path_id:o for o in env.objects}
metadata = next(o for o in env.objects if o.type.name=='AssetBundle').read_typetree()
guidmap = {o.path_id: uuid.UUID(bytes_le=bytes(o.read_typetree()['m_id']['m_idBytes'])).hex for o in env.objects if o.type.name=='MonoBehaviour'}
selected = ['BindIntComparisonToSwitch','BindIndexOrLessToSwitch','BindListHasGreaterThanBindingCountToSwitch','BindIntPropertyComparisonToAOrBStyle','BindIntComparisonToAOrBUssClass']
for o in env.objects:
    if o.type.name != 'MonoBehaviour':
        continue
    d = o.read_typetree()
    if d.get('m_Name') in selected:
        rows=[]
        for r in d['references']['RefIds']:
            if 'CompareIntInt' in r['type']['class'] or r['type']['class']=='BindableSwitchElement_SetVisibleIndex':
                rows.append({'class':r['type']['class'],'defaults':{k:v.get('m_defaultSocketValue') for k,v in r['data'].items() if isinstance(v,dict) and 'm_defaultSocketValue' in v}})
        print(json.dumps({'name':d['m_Name'],'guid':guidmap.get(o.path_id),'inputs':[(v['m_name'],v['m_type']['m_typeString']) for v in d['m_inputs']],'nodes':rows},ensure_ascii=True))

def readstr(b, off):
    length=0; shift=0
    while True:
        n=b[off];off+=1;length|=(n&127)<<shift;shift+=7
        if not n&128:break
    return b[off:off+length].decode(),off+length

def arguments(b):
    if not b:return []
    count=b[0];off=1;items=[]
    for i in range(count):
        n=struct.unpack_from('<i',b,off)[0];off+=4
        payload=b[off:off+n];off+=n
        cls,p=readstr(payload,0)
        items.append((cls,payload[p:].hex(),payload[p:].decode('latin1')))
    assert off==len(b),(off,len(b))
    return items

globalenv = UnityPy.load(str(root/'卡面98总上移10头像70-v27/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))
matched=0
targetguid = guidmap[468212822105936887]
for o in globalenv.objects:
    if o.type.name!='MonoBehaviour':continue
    if targetguid.encode() not in o.get_raw_data():continue
    d=o.read_typetree();refs={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
    for r in refs.values():
        for k,f in r.get('data',{}).items():
            if isinstance(f,dict) and f.get('m_target',{}).get('m_guid')==targetguid:
                row={'asset':d['m_Name'],'pid':o.path_id,'rid':r['rid'],'class':r['type']['class'],'field':k,'args':arguments(bytes(f['m_inputs']['m_variable']['m_argumentBytes']))}
                print('EXAMPLE',json.dumps(row,ensure_ascii=True))
                if matched==0:
                    (root/'switch-example-v28.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
                matched+=1
                if matched>=8:break
        if matched>=8:break
    if matched>=8:break
