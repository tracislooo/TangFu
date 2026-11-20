"""V8 presentation-only delta over installed V7; preserve native UI bindings."""
from pathlib import Path
source=Path('trial-tactics-combined-layered-card.py').read_text('utf8')
boot=source.split('# Keep the pitch anchor / footprint')[0]
exec(compile(boot.replace('tactics-combined-layered-card-trial-','tactics-cards-black80-v8-').replace('hours=-4','hours=-6'),'boot','exec'))
CP,DP=3127595210179668386,-8273082868742719783
expected={};outputs={};audits=[]
extract('reflow-tactics-transparent-panels-v7.py',{'named','value','save_tree','tree','check_sd'})
black={'r':0.,'g':0.,'b':0.,'a':f32(.2)}
clear={'r':0.,'g':0.,'b':0.,'a':0.}
rim={'r':1.,'g':1.,'b':1.,'a':f32(.16)}

def visible_ancestors(i):
    while i in t.r and i!=1000:
        t.edit(i,[P(458768,st.en('visible'))])
        i=t.r[i]['data'].get('m_Parent',{}).get('rid',-2)

def name_row(node,contexts,texts):
    box(node,4,60,67,11)
    t.edit(node,[P(131100,st.px(4)),P(458768,st.en('visible')),P(131073,st.en('center'))])
    for i in contexts+texts:
        t.edit(i,[P(131087,st.px(11)),P(131096,st.px(0)),P(131094,st.px(11)),P(458768,st.en('visible')),P(131073,st.en('center'))])
    visible_ancestors(node)

def stars(node):
    # The 50x8 tree keeps its native internal layout. Scaling about its centre
    # produces a 75x12 visual box at (0,1), five px below its old top edge.
    box(node,12.5,3,50,8)
    t.edit(node,[P(327681,st.num(1.5),st.num(1.5))])
    visible_ancestors(node)

for pid in [CP,DP]:
    t=tree(pid);st=t.st;P=st.p;old=copy.deepcopy(t.r);detail=pid==DP
    leaves=0
    for i,a in list(t.r.items()):
        if a.get('data',{}).get('m_FullTypeName')!='SI.Bindable.SIText':continue
        name=t.sd(i).get('name','')
        if not name.startswith('PitchFitnessPercent'):continue
        # Padding cannot be negative. Move only the label box; compensate each
        # existing progress fill child so the external bar stays at x=0.
        t.edit(i,[P(131089,st.px(-12)),P(131105,st.px(87)),P(458768,st.en('visible'))])
        for child in a['data']['m_Children']:
            fill=child['rid'];assert 'FitnessFill' in t.sd(fill).get('name','')
            t.edit(fill,[P(131089,st.px(12))])
        leaves+=1
    assert leaves==102
    roles=[1024,1028] if detail else [1029,1033]
    glyphs=[1034,1043] if detail else [1044,1053]
    for node,glyph,y in zip(roles,glyphs,[6.5,18.5]):
        box(node,65.5,y,15,15)
        box(glyph,-.5,-.5,16,16)
        t.edit(glyph,[P(327681,st.num(.9375),st.num(.9375))])
    for node,y in [((1027 if detail else 1032),30),((1026 if detail else 1031),42)]:
        box(node,65,y,16,16);t.edit(node,[P(327681,st.num(.9375),st.num(.9375))])
    if detail:
        box(1017,65,54,16,16);t.edit(1017,[P(327681,st.num(.9375),st.num(.9375))])
    for i in [roles[0],named(t.r,'PitchFitnessPlayerVisible')]:visible_ancestors(i)
    if not detail:
        box(1035,-8,8,28,25);visible_ancestors(1035)
        name_row(1037,[1061,1082,1098],[1115,1134,1135,1151])
        stars(1036)
    check_sd(old);save_tree(pid)
    audits.append({'template':t.d['m_Name'],'fitness_labels_moved':leaves,'right_icons_visual_size':15})

for pid,touch in [(-970000000009000,False),(-970000000010000,True)]:
    t=tree(pid);st=t.st;P=st.p;old=copy.deepcopy(t.r)
    role=named(t.r,'DetailedCurrentPhasePositionContext');box(role,-8,8,28,12);visible_ancestors(role)
    for field,x in [('LeftFootedness',-8),('RightFootedness',4)]:
        node=named(t.r,'Detailed'+field+'PlayerVisible');box(node,x,23,10,10);visible_ancestors(node)
    if touch:name_row(1061,[],[1089]);stars(1027)
    else:name_row(1016,[1026,1038,1054],[1074,1100,1123]);stars(1022)
    check_sd(old);save_tree(pid)

# The native header renders its own gradient. Replace its two constant RGBA
# arguments, preserving the function, orientation and all control bindings.
t=tree(-966834888143150418);st=t.st;P=st.p;old=copy.deepcopy(t.r)
fn=t.sd(1004)['BindGradientFunc'];args=decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
assert len(args)==2
for a in args:
    assert b'ColorVisualArg' in a;struct.pack_into('<4f',a,len(a)-16,0,0,0,.2)
fn['m_inputs']['m_variable']['m_argumentBytes']=encode(args)
for i in [1004,1007,1009]:t.edit(i,[P(458752,st.h(4,clear)),P(262146,st.h(4,rim))])
check_sd(old,[t.r[1004]['data']['m_SerializedData']['rid']]);save_tree(-966834888143150418)
t=tree(1593217430813700770);st=t.st;P=st.p;old=copy.deepcopy(t.r)
t.edit(1002,[P(458752,st.h(4,black)),P(262146,st.h(4,rim))]);check_sd(old);save_tree(1593217430813700770)

# Six renderers stay transparent over ONE black .2 panel surface. This avoids
# .2-on-.2 compositing (36% opacity) and keeps all native pitch lines unchanged.
style_name='ui-styles_assets_default.bundle';style_audits=[]
for folder in [GAME,SKIN]:
    path=folder/style_name;before[path]=path.read_bytes();protected.pop(path,None)
    e=UnityPy.load(before[path]);oo={o.path_id:o for o in e.objects};hh={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={};hits=0
    for pid,o in oo.items():
        if o.type.name!='MonoBehaviour':continue
        data=o.read_typetree();ss=Styles(data);count=0
        for rule in data.get('m_Rules',[]):
            selectors=rule['m_ComplexSelectors']
            if not any('tf-tactics-pitch-black' in p['m_Value'] or p['m_Value']=='TFPitchSwitches' for sel in selectors for s in sel['m_Selectors'] for p in s['m_Parts']):continue
            header=any(p['m_Value']=='TFPitchSwitches' for sel in selectors for s in sel['m_Selectors'] for p in s['m_Parts'])
            rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id']!=458752]+[ss.p(458752,ss.h(4,clear if header else black))]
            count+=1
        if count:o.save_typetree(data);changed[pid]=copy.deepcopy(data);hits+=count
    assert hits==6
    raw=e.file.save(packer='lz4');cc={o.path_id:o for o in UnityPy.load(raw).objects};assert cc.keys()==oo.keys()
    for pid,o in cc.items():
        if pid in changed:assert o.read_typetree()==changed[pid]
        else:assert sha(o.get_raw_data())==hh[pid]
    outputs[path]=raw;style_audits.append({'path':str(path),'scoped_rules':hits,'objects_changed':list(changed)})

raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert check.keys()==objs.keys()
for pid,h in hashes.items():
    if pid in expected:assert check[pid].read_typetree()==expected[pid]
    else:assert sha(check[pid].get_raw_data())==h,('Unrelated object changed',pid)

# Verify the serialized product, not just the in-memory editing trees.
def read_node(pid,i,k):
    d=check[pid].read_typetree();r=refs(d);s=check[d['inlineSheet']['m_PathID']].read_typetree()
    p=next(p for p in s['m_Rules'][r[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==k)
    return [s[poolmap[h['m_ValueType']]][h['valueIndex']] if h['m_ValueType'] in poolmap else h for h in p['m_Values']]
for pid,node in [(CP,1037),(-970000000009000,1016),(-970000000010000,1061)]:
    assert read_node(pid,node,131104)[0]['value']==60 and read_node(pid,node,131087)[0]['value']==11
for pid,node in [(CP,1036),(-970000000009000,1022),(-970000000010000,1027)]:
    assert read_node(pid,node,327681)==[1.5,1.5] and read_node(pid,node,131104)[0]['value']==3
assert read_node(CP,1035,131089)[0]['value']==-8
assert read_node(-970000000009000,1142,131089)[0]['value']==-8
for folder in [GAME,SKIN]:outputs[folder/W]=raw

registry=R/'current-custom-textures.json';protected[registry]=sha(registry.read_bytes())
banned={int(a['path_id']) for a in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
assert banned.isdisjoint(check)
for o in check.values():
    if o.type.name=='AssetBundle':
        meta=o.read_typetree();assert banned.isdisjoint(p['m_PathID'] for p in meta['m_PreloadTable'])
        assert banned.isdisjoint(v['asset']['m_PathID'] for k,v in meta['m_Container'])
for p,raw in before.items():
    tag='backup-game' if p.parent==GAME else 'backup-skin';(OUT/tag).mkdir(exist_ok=True);(OUT/tag/p.name).write_bytes(raw)
for p,raw in outputs.items():
    tag='output-game' if p.parent==GAME else 'output-skin';(OUT/tag).mkdir(exist_ok=True);(OUT/tag/p.name).write_bytes(raw)
report={'version':'V8','installed':False,'runtime_verified':False,'transparency':.8,'black_opacity':.2,'left_information_delta_x':-12,'name_row':[4,60,67,11],'stars_scale':1.5,'stars_visual_y':1,'stars_visual_size':[75,12],'right_icon_visual_size':15,'pitch_coordinate_and_native_bindings_preserved':True,'white_report_hotspot_preserved':[16,16],'no_new_objects_or_catalog_changes':True,'cards':audits,'styles':style_audits,'changed_world_objects':list(expected),'after_sha256':{str(p):sha(b) for p,b in outputs.items()},'protected_files':{str(p):h for p,h in protected.items()}}
def record():(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
guard=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer=list(guard);restore=list(guard)
for p,b in before.items():
    installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(b)+"') { throw 'File changed since preparation.' }")
    tag='backup-game' if p.parent==GAME else 'backup-skin';restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
for p in outputs:
    tag='output-game' if p.parent==GAME else 'output-skin';installer.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
installer.append("Write-Output 'V8 installed. Restart Football Manager.'")
(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig');(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
(OUT/'README.md').write_text('V8: 左侧信息左移12px；右侧图标及星级150%；星级视觉下移5px；姓名条y60/高11px，报告热区16px保持。上方渐变、下方模块、球场面板均黑色/80%透明（alpha0.2）。场地本体透明覆盖于单一黑色半透明面板上，避免重复叠色。\n\n游戏内视觉、悬停和拖拽待实际验收。运行中仅准备补丁。安装/回退需退出游戏。\n','utf8')
record()
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if running.stdout.strip():
    print(json.dumps({'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for p,b in outputs.items():p.write_bytes(b)
    for p,b in outputs.items():assert p.read_bytes()==b
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True);record()
print(json.dumps({'installed':True,'output':str(OUT),'cards':audits,'black_opacity':.2}))
