from pathlib import Path
import sys,json,hashlib,struct,importlib.util
R=Path(__file__).resolve().parent;sys.path.insert(0,str(R/'.codex-deps'));import UnityPy
O=Path(sys.argv[1]) if len(sys.argv)>1 else R/'tactics-transparent-panels-card-reflow-v7-20261028-103935';report=json.loads((O/'manifest.json').read_text('utf8'))
sha=lambda b:hashlib.sha256(b).hexdigest()
for p,h in report['after_sha256'].items():assert sha(Path(p).read_bytes())==h,p
for p,h in report['protected_files'].items():assert sha(Path(p).read_bytes())==h,p
G=Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64');S=Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages');W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
live={o.path_id:o for o in UnityPy.load(str(G/W)).objects};old={o.path_id:o for o in UnityPy.load(str(O/'backup-game'/W)).objects};changed={int(i) for i in report['changed_world_objects']}
assert set(live)==set(old)|{-970000000012000,-970000000012001}
for i,o in old.items():
    if i not in changed:assert live[i].get_raw_data()==o.get_raw_data(),i
pool={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
def load(pid):
    d=live[pid].read_typetree();r={x['rid']:x.get('data',{}) for x in d['references']['RefIds']};s=live[d['inlineSheet']['m_PathID']].read_typetree();return d,r,s
def sd(r,i):return r[r[i]['m_SerializedData']['rid']]
def named(r,n):return next(i for i,a in r.items() if r.get(a.get('m_SerializedData',{}).get('rid'),{}).get('name')==n)
def pv(r,s,i,k):
    h=next(p for p in s['m_Rules'][r[i]['m_RuleIndex']]['m_Properties'] if p['m_Id']==k)['m_Values'][0]
    return s[pool[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in pool else h
def args(raw):
    b=bytes(raw);p=1;out=[]
    for _ in range(b[0]):n=struct.unpack_from('<I',b,p)[0];p+=4;out.append(b[p:p+n]);p+=n
    return out
pitch_count=0
for pid,i in report['native_pitch_backgrounds_cleared']:
    d,r,s=load(pid);assert pv(r,s,i,458753)=={'m_ValueType':1,'valueIndex':6};assert pv(r,s,i,458752)['a']==0;pitch_count+=1
    before={x['rid']:x.get('data',{}) for x in old[pid].read_typetree()['references']['RefIds']};assert sd(r,i)==sd(before,i)
assert pitch_count==6
checks=[]
for pid,detail in [(3127595210179668386,False),(-8273082868742719783,True)]:
    d,r,s=load(pid);frame=named(r,'TacticsPlayerPortraitFrame');assert pv(r,s,frame,131105)['value']==pv(r,s,frame,131087)['value']==75
    image=named(r,'TacticsPlayerCardBackgroundImage');assert pv(r,s,image,458753)['m_PathID']==-910000000000147
    root=named(r,'PitchFitnessAbove-1')
    for raw in [None,-1]+list(range(111)):
        i=root
        while 'Binding' in sd(r,i):
            a=args(sd(r,i)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);limit=struct.unpack_from('<i',a[1],len(a[1])-4)[0];i=r[i]['m_Children'][int(raw is not None and raw>limit)]['rid']
        v=None if raw is None or raw<0 else min(raw,100);assert sd(r,i)['text']==('--' if v is None else str(v)+'%')
        assert pv(r,s,i,131101)['value']==(36 if detail else 35)
        fill=r[i]['m_Children'][0]['rid'];assert pv(r,s,fill,131105)['value']==(0 if v is None else v*.75)
    for i,y in zip([1024,1028] if detail else [1029,1033],[9,21]):assert pv(r,s,i,131089)['value']==68 and pv(r,s,i,131104)['value']==y
    if not detail:
        assert pv(r,s,1035,131089)['value']==4 and pv(r,s,1035,131104)['value']==8
        assert pv(r,s,1055,131104)['value']==0 and pv(r,s,1057,131104)['value']==13
        assert pv(r,s,1037,131104)['value']==55 and pv(r,s,1037,131087)['value']==16
        assert pv(r,s,1132,131105)['value']==pv(r,s,1132,131087)['value']==16 and pv(r,s,1132,458767)==1
    checks.append(d['m_Name'])
for pid,touch in [(-970000000009000,False),(-970000000010000,True)]:
    d,r,s=load(pid);pos=named(r,'DetailedCurrentPhasePositionContext');assert pv(r,s,pos,131089)['value']==4 and pv(r,s,pos,131104)['value']==8 and pv(r,s,pos,131105)['value']==28
    for field,x in [('LeftFootedness',4),('RightFootedness',16)]:
        gate=named(r,'Detailed'+field+'PlayerVisible');assert pv(r,s,gate,131089)['value']==x and pv(r,s,gate,131104)['value']==23
    name=1061 if touch else 1016;assert pv(r,s,name,131104)['value']==55 and pv(r,s,name,131087)['value']==16
    visible=r[named(r,'DetailedTouchHasPlayerReport')]['m_Children'][0]['rid'] if touch else 1095
    assert pv(r,s,visible,458767)==1
    assert next(u for u in d['m_Usings'] if u['alias']=='PlayerReportPreviewTooltip')['path']==report['white_preview_guid']
d,r,s=load(-970000000012000);assert pv(r,s,1004,196610)=={'r':1.0,'g':1.0,'b':1.0,'a':1.0};assert pv(r,s,1004,131105)['value']==12
assert d['m_Name']=='TacticsWhitePlayerReportPreview' and d['inlineSheet']['m_PathID']==-970000000012001
assert live[-3760232355926433866].get_raw_data()==old[-3760232355926433866].get_raw_data()
shared_style=old[-3760232355926433866].read_typetree()['inlineSheet']['m_PathID'];assert live[shared_style].get_raw_data()==old[shared_style].get_raw_data()

for f in [G,S]:
    for n in ['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle']:
        definitions=0;private_rules=0
        for o in UnityPy.load(str(f/n)).objects:
            if o.type.name!='MonoBehaviour':continue
            data=o.read_typetree()
            for rule in data.get('m_Rules',[]):
                for p in rule['m_Properties']:
                    key=next((k for k in report['palette'] if p.get('m_CustomName')=='--colours-tactics-'+k+'-foreground'),None)
                    if key:
                        actual=data['colors'][p['m_Values'][0]['valueIndex']];h=report['palette'][key].lstrip('#')
                        for k,z in zip(['r','g','b'],[0,2,4]):assert actual[k]==struct.unpack('<f',struct.pack('<f',int(h[z:z+2],16)/255))[0]
                        definitions+=1
                if 'tf-tactics-pitch-black' in str(rule['m_ComplexSelectors']) or 'TFPitchSwitches' in str(rule['m_ComplexSelectors']):private_rules+=1
        assert definitions==6 and private_rules==(6 if 'default' in n else 0)
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'));assert registry['version']==65 and len(registry['textures'])==178
banned={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
for fn in [W,'ui-backgrounds_assets_common.bundle']:
    objects={o.path_id:o for o in UnityPy.load(str(G/fn)).objects};m=next(o.read_typetree() for o in objects.values() if o.type.name=='AssetBundle');assert banned.isdisjoint(objects)
    assert all(p['m_PathID'] not in banned for p in m['m_PreloadTable']);assert all(v['asset']['m_PathID'] not in banned for _,v in m['m_Container'])
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
for f in [G.parent,S]:
    raw=(f/'catalog.bin').read_bytes();assert (f/'catalog.hash').read_bytes()==hashlib.md5(raw).hexdigest().encode();c=cm.Catalog(raw);loc=c.locations(report['white_preview_guid'])[0]
    assert c.location(loc)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset' and c.location(c.location(loc)['dependencies'][0])['internal'].endswith('\\'+W)
    assert loc in {i[0] for i in c.array(dict(c.keys())['GameWorldVisualTreeAssetPreload'],'I')}
report.update(independent_installed_verification=True,fitness_inputs_verified=226,runtime_verified=False)
(O/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed_verified':True,'pitch_renderers':6,'cards':checks,'fitness_inputs':226,'new_icon_white_and_full_size':True,'background_registry_preserved':'V65/178','runtime_verified':False},ensure_ascii=False))
