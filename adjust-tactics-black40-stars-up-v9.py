"""V9: 40% transparent black panels; stars five pixels higher than V8."""
from pathlib import Path
source=Path('trial-tactics-combined-layered-card.py').read_text('utf8')
boot=source.split('# Keep the pitch anchor / footprint')[0]
exec(compile(boot.replace('tactics-combined-layered-card-trial-','tactics-black40-stars-up-v9-').replace('hours=-4','hours=-6'),'boot','exec'))
expected={};outputs={};audits=[];style_audits=[]
extract('reflow-tactics-transparent-panels-v7.py',{'named','value','save_tree','tree','check_sd'})
black={'r':0.,'g':0.,'b':0.,'a':f32(.6)}
for pid,node in [(3127595210179668386,1036),(-970000000009000,1022),(-970000000010000,1027)]:
    t=tree(pid);st=t.st;P=st.p;old=copy.deepcopy(t.r)
    assert value(node,131104)['value']==3 and value(node,327681)==1.5
    t.edit(node,[P(131104,st.px(-2))]);check_sd(old);save_tree(pid)
    audits.append({'template':t.d['m_Name'],'star_node_y':-2,'star_visual_y':-4,'scale':1.5})
t=tree(-966834888143150418);st=t.st;P=st.p;old=copy.deepcopy(t.r)
fn=t.sd(1004)['BindGradientFunc'];args=decode(fn['m_inputs']['m_variable']['m_argumentBytes'])
assert len(args)==2
for a in args:
    assert b'ColorVisualArg' in a
    assert struct.unpack_from('<4f',a,len(a)-16)==(0.,0.,0.,f32(.2))
    struct.pack_into('<4f',a,len(a)-16,0,0,0,.6)
fn['m_inputs']['m_variable']['m_argumentBytes']=encode(args)
check_sd(old,[t.r[1004]['data']['m_SerializedData']['rid']]);save_tree(-966834888143150418)
t=tree(1593217430813700770);st=t.st;P=st.p;old=copy.deepcopy(t.r)
assert value(1002,458752)['a']==f32(.2)
t.edit(1002,[P(458752,st.h(4,black))]);check_sd(old);save_tree(1593217430813700770)
for folder in [GAME,SKIN]:
    path=folder/'ui-styles_assets_default.bundle';before[path]=path.read_bytes();protected.pop(path,None)
    e=UnityPy.load(before[path]);oo={o.path_id:o for o in e.objects};hh={i:sha(o.get_raw_data()) for i,o in oo.items()};changed={};hits=0
    for pid,o in oo.items():
        if o.type.name!='MonoBehaviour':continue
        data=o.read_typetree();ss=Styles(data);count=0
        for rule in data.get('m_Rules',[]):
            if not any(p['m_Value'] in ['tf-tactics-pitch-black','tf-tactics-pitch-black-dark-header'] for sel in rule['m_ComplexSelectors'] for s in sel['m_Selectors'] for p in s['m_Parts']):continue
            prop=next(p for p in rule['m_Properties'] if p['m_Id']==458752)
            h=prop['m_Values'][0];assert data['colors'][h['valueIndex']]['a']==f32(.2)
            prop['m_Values']=[ss.h(4,black)];count+=1
        if count:o.save_typetree(data);changed[pid]=copy.deepcopy(data);hits+=count
    assert hits==4
    raw=e.file.save(packer='lz4');cc={o.path_id:o for o in UnityPy.load(raw).objects};assert cc.keys()==oo.keys()
    for pid,o in cc.items():
        if pid in changed:assert o.read_typetree()==changed[pid]
        else:assert sha(o.get_raw_data())==hh[pid]
    outputs[path]=raw;style_audits.append({'path':str(path),'pitch_surface_rules_updated':hits})
raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert check.keys()==objs.keys()
for pid,h in hashes.items():
    if pid in expected:assert check[pid].read_typetree()==expected[pid]
    else:assert sha(check[pid].get_raw_data())==h,('Unrelated world object changed',pid)
for folder in [GAME,SKIN]:outputs[folder/W]=raw

# Reuse the audited backup, protected-file, process guard and rollback installer.
tail=Path('adjust-tactics-cards-black80-v8.py').read_text('utf8').split("registry=R/'current-custom-textures.json'")[1]
tail="registry=R/'current-custom-textures.json'"+tail
start=tail.index('report={');end=tail.index('\ndef record()',start)
tail=tail[:start]+"report={'version':'V9','installed':False,'runtime_verified':False,'transparency':.4,'black_opacity':.6,'stars_delta_y':-5,'stars_scale':1.5,'stars_visual_y':-4,'all_other_card_layout_and_bindings_unchanged':True,'no_new_objects_or_catalog_changes':True,'cards':audits,'styles':style_audits,'changed_world_objects':list(expected),'after_sha256':{str(p):sha(b) for p,b in outputs.items()},'protected_files':{str(p):h for p,h in protected.items()}}"+tail[end:]
start=tail.index("(OUT/'README.md').write_text(");end=tail.index('\nrecord()',start)
tail=tail[:start]+"(OUT/'README.md').write_text('V9: 上方战术工具栏、下方执行力/复杂度模块、球场面板统一黑色40%透明（alpha0.6）；星级保留150%缩放，相对V8上移5px。其余布局与资源不变。运行中仅准备补丁，退出游戏后运行install.ps1；restore.ps1恢复V8。游戏内视觉/交互待验收。','utf8')"+tail[end:]
tail=tail.replace("V8 installed.","V9 installed.").replace("'black_opacity':.2","'black_opacity':.6")
exec(compile(tail,'verify-backup-install','exec'))
