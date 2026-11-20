import sys
import json
import struct
import re
from pathlib import Path
sys.path.insert(0,'G:/Doc/ChatGPT/New project/.codex-deps')
import UnityPy
root=Path('G:/Doc/ChatGPT/New project')
env=UnityPy.load(str(root/'卡面98总上移10头像70-v27/ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'))

def readstr(b,off):
    length=0;shift=0
    while True:
        n=b[off];off+=1;length|=(n&127)<<shift;shift+=7
        if not n&128:break
    return b[off:off+length].decode(),off+length

def args(b):
    if not b:return []
    off=1;items=[]
    for i in range(b[0]):
        n=struct.unpack_from('<i',b,off)[0];off+=4
        p=b[off:off+n];off+=n
        cls,pos=readstr(p,0)
        items.append({'class':cls,'value_hex':p[pos:].hex(),'value_text':p[pos:].decode('latin1')})
    assert off==len(b)
    return items

hits=0; mapping_hits=0; classes={}
for o in env.objects:
    if o.type.name!='MonoBehaviour':continue
    raw=o.get_raw_data()
    if not any(t in raw for t in [b'BindableSwitchElement',b'Mappings']):continue
    d=o.read_typetree();refs={r['rid']:r for r in d.get('references',{}).get('RefIds',[])}
    for r in refs.values():
        data=r.get('data',{})
        if r['type']['class']=='BindingRemapper/UxmlSerializedData' and mapping_hits<12:
            mappings=[m for m in data['Mappings'] if m['from'].lower()=='player']
            if mappings:
                print('PLAYER_MAP',d['m_Name'],json.dumps(mappings));mapping_hits+=1
        if 'Switch' not in r['type']['class'] or 'UxmlSerializedData' not in r['type']['class']:continue
        classes[r['type']['class']]=list(data)
        f=data.get('Binding',{}).get('m_visualFunction',data.get('BindTextFunction',{}))
        if not f.get('m_target',{}).get('m_guid'):continue
        parsed=args(bytes(f['m_inputs']['m_variable']['m_argumentBytes']))
        if any('ComparisonOperator' in arg['class'] for arg in parsed):
            print('SWITCH',json.dumps({'name':d['m_Name'],'pid':o.path_id,'rid':r['rid'],'guid':f['m_target']['m_guid'],'args':parsed},ensure_ascii=True))
            if hits==0:
                (root/'native-int-switch-template-v28.json').write_text(json.dumps(d,ensure_ascii=False,indent=2),encoding='utf-8')
                (root/'native-int-switch-info-v28.json').write_text(json.dumps({'pid':o.path_id,'serialized_rid':r['rid'],'guid':f['m_target']['m_guid']},indent=2),encoding='utf-8')
            hits+=1
            if hits>=12:break
    if hits>=12 and mapping_hits>=1:break
print('COUNTS',hits,mapping_hits,classes)
