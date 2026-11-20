import sys,json,struct
from pathlib import Path
R=Path('G:/Doc/ChatGPT/New project');sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
AA=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
def string(b,p=0):
    n=shift=0
    while True:
        v=b[p];p+=1;n|=(v&127)<<shift
        if v<128:break
        shift+=7
    return b[p:p+n].decode(),p+n
def args(b):
    p=1;out=[]
    for i in range(b[0]):
        n=struct.unpack_from('<i',b,p)[0];p+=4;payload=b[p:p+n];p+=n;cls,j=string(payload);out.append((cls,payload[j:]))
    return out
for bundle in ['ui-visualtreeassets_assets_globalvisualtreeassetpreload','ui-visualtreeassets_assets_gameworldvisualtreeassetpreload']:
    for o in UnityPy.load(str(AA/(bundle+'.bundle'))).objects:
        if o.type.name!='MonoBehaviour' or b'[%number#1]' not in o.get_raw_data():continue
        t=o.read_typetree();rs=t.get('references',{}).get('RefIds',[])
        for r in rs:
            if r['type']['class']!='SIText/UxmlSerializedData':continue
            binding=r['data'].get('TextBinding',{});vf=binding.get('m_visualFunction',{});raw=bytes(vf.get('m_inputs',{}).get('m_variable',{}).get('m_argumentBytes',[]))
            if not raw:continue
            a=args(raw)
            if len(a)==2 and a[0][0].endswith('SI.Translation.TranslationID]') and len(a[0][1])>5:
                fmt,end=string(a[0][1],5)
                if fmt=='[%number#1]':
                    node=next(n for n in rs if n.get('data',{}).get('m_SerializedData',{}).get('rid')==r['rid'])
                    out={'bundle':bundle,'source_name':t['m_Name'],'node':node,'sd':r,'arg_classes':[c for c,v in a],'arg_payloads':[list(v) for c,v in a]}
                    (R/'native-integer-text-template-v36.json').write_text(json.dumps(out,ensure_ascii=False,indent=2),encoding='utf-8')
                    print(json.dumps({'source':t['m_Name'],'guid':vf['m_target']['m_guid'],'classes':[c for c,v in a],'payloads':[list(v) for c,v in a]}));sys.exit(0)
raise RuntimeError('No exact native integer format found')
