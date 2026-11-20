"""Read-only installed-resource verification; writes its report only in patch dir."""
from pathlib import Path
import sys, json, hashlib, struct, colorsys, ast, importlib.util
R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
out=R/'tactics-detailed75-feet-hover-v4-20261028-022811'
report=json.loads((out/'manifest.json').read_text('utf8'))
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
GAME=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
sha=lambda b:hashlib.sha256(b).hexdigest()
for p,h in report['after_sha256'].items():assert sha(Path(p).read_bytes())==h,p
for p,h in report['protected_files'].items():assert sha(Path(p).read_bytes())==h,p
live={o.path_id:o for o in UnityPy.load(str(GAME/W)).objects}
old={o.path_id:o for o in UnityPy.load(str(out/'backup-game'/W)).objects}
changed={int(x) for x in report['changed_objects']}
assert set(live)==set(old)|{p for p in changed if p not in old}
for p,o in old.items():
    if p not in changed:assert live[p].get_raw_data()==o.get_raw_data(),p
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def load(pid):
    d=live[pid].read_typetree();r={x['rid']:x.get('data',{}) for x in d['references']['RefIds']};s=live[d['inlineSheet']['m_PathID']].read_typetree();return d,r,s
def sd(r,i):return r[r[i]['m_SerializedData']['rid']]
def named(r,n):return next(i for i,a in r.items() if r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('name')==n)
def val(r,s,i,key):
    rule=s['m_Rules'][r[i]['m_RuleIndex']];v=next(p for p in rule['m_Properties'] if p['m_Id']==key)['m_Values'][0];return s[pool[v['m_ValueType']]][v['valueIndex']]
def args(raw):
    b=bytes(raw);pos=1;out=[]
    for _ in range(b[0]):n=struct.unpack_from('<I',b,pos)[0];pos+=4;out.append(b[pos:pos+n]);pos+=n
    assert pos==len(b);return out
foot_results={}
for pid in [-970000000009000,-970000000010000]:
    d,r,s=load(pid)
    assert val(r,s,1001,131105)['value']==val(r,s,1001,131087)['value']==75
    cache={}
    for word,field in [('左','LeftFootedness'),('右','RightFootedness')]:
        gate=named(r,'Detailed'+field+'PlayerVisible');assert sd(r,gate)['Binding']['m_direct']['Path']['m_path']=='position.Player'
        for v in [None,-1,0]+list(range(1,23)):
            i=r[gate]['m_Children'][0]['rid']
            while 'Binding' in sd(r,i):
                a=args(sd(r,i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack_from('<i',a[1],len(a[1])-4)[0]
                assert a[2].endswith(('position.Player.Footedness.'+field).encode())
                i=r[i]['m_Children'][int(v is not None and v>limit)]['rid']
            valid=v is not None and 1<=v<=20
            expected=None if not valid else v
            assert sd(r,i)['name']==field+'Value'+str(expected)
            label=r[i]['m_Children'][0]['rid'];assert sd(r,label)['text']==word
            tip=r[i]['m_Children'][1]['rid'];body=r[tip]['m_Children'][0]['rid']
            assert sd(r,body)['text']==word+'脚：'+('数据不可用' if not valid else str(v)+'/20')
            if valid:
                h=report['foot_colors'][(v-1)//4];actual=val(r,s,i,458752)
                for key,n in zip(['r','g','b'],[0,2,4]):assert actual[key]==struct.unpack('<f',struct.pack('<f',int(h[n:n+2],16)/255))[0]
            cache[(field,v)]=expected
    for left in range(1,21):
        for right in range(1,21):assert cache[('LeftFootedness',left)]==left and cache[('RightFootedness',right)]==right
    foot_results[d['m_Name']]={'independent_pair_combinations':400,'values_and_tooltips':50}
    if pid==-970000000009000:
        for i in [1072,1095,1119,1131]:assert val(r,s,i,131087)['value']==16
        assert val(r,s,1016,131104)['value']==43 and val(r,s,1016,131087)['value']==16
        assert val(r,s,1021,131081)=='none' and val(r,s,1015,131081)=='none'
    else:
        for i in [1014,1026,1016,1017]:assert val(r,s,i,131081)=='none'
        assert val(r,s,1061,131104)['value']==43 and val(r,s,1061,131087)['value']==16
        i=named(r,'DetailedTouchHasPlayerReport')
        for _ in range(4):
            assert val(r,s,i,131087)['value']==16
            if r[i]['m_Children']:i=r[i]['m_Children'][0]['rid']

d,r,s=load(-8273082868742719783)
frame=named(r,'TacticsPlayerPortraitFrame')
assert val(r,s,frame,131105)['value']==val(r,s,frame,131087)['value']==75
assert val(r,s,1014,131104)['value']==val(r,s,1015,131104)['value']==-2.5
root=named(r,'PitchFitnessAbove-1')
for v in [None,-1]+list(range(111)):
    i=root
    while 'Binding' in sd(r,i):
        a=args(sd(r,i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack_from('<i',a[1],len(a[1])-4)[0]
        i=r[i]['m_Children'][int(v is not None and v>limit)]['rid']
    expected=None if v is None or v<0 else min(v,100)
    assert sd(r,i)['text']==('--' if expected is None else str(expected)+'%')
    fill=r[i]['m_Children'][0]['rid'];assert val(r,s,fill,131105)['value']==(0 if expected is None else expected*.75)
d,r,s=load(3127595210179668386)
for i in [1132,1148,1158]:
    assert val(r,s,i,131105)['value']==val(r,s,i,131087)['value']==16
    rule=s['m_Rules'][r[i]['m_RuleIndex']]
    scale=next(p for p in rule['m_Properties'] if p['m_Id']==327681)['m_Values'];assert [s['floats'][v['valueIndex']] for v in scale]==[1,1]

spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for folder in [GAME.parent,SKIN]:
    raw=(folder/'catalog.bin').read_bytes();assert (folder/'catalog.hash').read_bytes()==hashlib.md5(raw).hexdigest().encode()
    c=cm.Catalog(raw);pre={i[0] for i in c.array(dict(c.keys())['GameWorldVisualTreeAssetPreload'],'I')}
    for pid,guid in report['new_templates'].items():
        loc=next(i for i in c.locations(guid) if c.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
        assert loc in pre and c.location(c.location(loc)['dependencies'][0])['internal'].endswith('\\'+W)
        assert int(pid) in live
report.update(independent_installed_verification=True,foot_pair_combinations_verified=800,
              detailed_condition_inputs_verified=113,runtime_verified=False)
(out/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(out/'verification.json').write_text(json.dumps(foot_results,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed_verified':True,'foot_pair_combinations':800,'detailed_condition_inputs':113,'native_report_hotspot':16,'shared_templates_preserved':True,'output':str(out)},ensure_ascii=False))
