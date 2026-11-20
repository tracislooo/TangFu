"""Replace the failed background event while retaining the user's current navigation."""
from pathlib import Path
import ast,copy,datetime,hashlib,json,struct,sys

R=Path(__file__).resolve().parent
sys.path.insert(0,str(R/'.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

def extract(file,names):
    t=ast.parse((R/file).read_text('utf8'))
    exec(compile(ast.Module(body=[n for n in t.body if isinstance(n,(ast.FunctionDef,ast.ClassDef)) and n.name in names],type_ignores=[]),file,'exec'),globals())

oldwrite=TypeTreeHelper.write_value
extract('build-fc-player-hover-layout.py',{'write'})
TypeTreeHelper.write_value=write
poolmap={2:'floats',3:'dimensions',4:'colors',5:'strings',6:'assets',7:'strings',8:'strings'}
extract('add-card-six-ratings.py',{'validate_ui'})
extract('build-match-ui-avatars-layout.py',{'refs','sd','find','pointer_remap','import_types','Doc'})
loc=json.loads((R/'current-game-location.json').read_text('utf8'))
GAME,SKIN=Path(loc['bundle_root']),Path(loc['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W='ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G='ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
STATE='TFBackgroundShowStadium'
OUT=R/('background-switch-local-assignment-'+datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir();(OUT/'templates').mkdir()
sha=lambda b:hashlib.sha256(b).hexdigest()
protected={str(p):sha(p.read_bytes()) for folder in [GAME,SKIN] for p in folder.glob('*.bundle') if p.name!=W}
for folder in [GAME.parent,SKIN]:
    for name in ['catalog.bin','catalog.hash']:protected[str(folder/name)]=sha((folder/name).read_bytes())
transactions,reports,documents=[],[],[]

def text(value):
    b=value.encode('utf8');assert len(b)<128
    return bytes([len(b)])+b

def event_parts(event):
    b=bytes(event['m_bytes']);assert b[:3]==b'\x01\x01\x01'
    p,parts=4,[]
    for _ in range(b[3]):
        assert b[p]==1
        size=struct.unpack_from('<I',b,p+1)[0];p+=5
        parts.append(b[p:p+size]);p+=size
    assert p==len(b)
    return parts

def set_payload(path,value):
    source=b'\x01\x01'+text('const.True' if value else 'const.False')
    return struct.pack('<I',624065536)+b'\x01\x01'+text(path)+struct.pack('<I',len(source))+source

def set_event(path,value):
    payload=set_payload(path,value)
    return {'m_bytes':list(b'\x01\x01\x01\x01\x01'+struct.pack('<I',len(payload))+payload)}

for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
    before=(folder/W).read_bytes()
    env={W:UnityPy.load(before),G:UnityPy.load(str(folder/G))}
    objs={n:{o.path_id:o for o in e.objects} for n,e in env.items()}
    hashes={i:sha(o.get_raw_data()) for i,o in objs[W].items()}
    changes={W:{},G:{}}
    native=Doc(G,name='TouchStore')
    assert event_parts(native.a(1024)['Events'])[0]==set_payload('goToStore',False)
    nav=Doc(W,name='PrimaryNavigationBar')
    original=copy.deepcopy(nav.d);original_style=copy.deepcopy(nav.s)
    old_refs=refs(original)
    button=nav.named('TFBackgroundSwitchButton')
    label=nav.named('TFBackgroundSwitchLabel')
    wrapper=nav.named('TFBackgroundButtonSharedSelection')
    assert nav.a(button)['m_Parent']=={'rid':wrapper}
    assert nav.a(wrapper)['m_Children']==[{'rid':button}]
    assert struct.unpack_from('<I',event_parts(nav.data(button)['Events'])[0])[0]==1564320233
    assert nav.data(wrapper)['ValueVariables'][0]['m_name']==STATE

    # The native boolean selector swaps two identical-looking buttons. Each click
    # assigns one explicit value, and never calls the manager-summary event.
    background=Doc(W,name='GameWorldBackground')
    selector=nav.add(background,1002,wrapper,'TFBackgroundButtonState')
    nav.move(selector,wrapper,0)
    nav.move(button,selector)
    nav.data(selector).update(AlwaysInstantiate=0,AlwaysInstantiate_UxmlAttributeFlags=1,
        Binding=copy.deepcopy(background.data(1002)['Binding']),Binding_UxmlAttributeFlags=1,
        BindDirectAsMask=0,BindDirectAsMask_UxmlAttributeFlags=1,
        InvertDirectBinding=0,InvertDirectBinding_UxmlAttributeFlags=1,
        Preview={'Mask':1},Preview_UxmlAttributeFlags=1)
    assert nav.data(selector)['Binding']['m_direct']['Path']['m_path']==STATE
    nav.size(selector,76,28)
    nav.st(selector,[(131073,nav.enum('center')),(131088,nav.enum('center'))])
    back=nav.add(nav,button,selector,'TFBackgroundSwitchBackButton')
    nav.a(back)['m_RuleIndex']=nav.a(button)['m_RuleIndex']
    nav.a(back)['m_Classes']=copy.deepcopy(nav.a(button)['m_Classes'])
    back_label=nav.add(nav,label,back,'TFBackgroundSwitchBackLabel')
    nav.a(back_label)['m_RuleIndex']=nav.a(label)['m_RuleIndex']
    nav.a(back_label)['m_Classes']=copy.deepcopy(nav.a(label)['m_Classes'])
    for i,value,tooltip in [(button,True,'切换为昆山球场背景'),(back,False,'切换为 TF skin V1 背景')]:
        nav.data(i).update(Events=set_event(STATE,value),Events_UxmlAttributeFlags=1,
            RightClickEvents={'m_bytes':[]},RightClickEvents_UxmlAttributeFlags=1,
            MigrateEventTemplate='',MigrateEventTemplate_UxmlAttributeFlags=1,
            tooltip=tooltip,tooltip_UxmlAttributeFlags=1)
    touched={i for i,r in old_refs.items() if nav.r[i]!=r}
    assert touched=={wrapper,button,nav.a(button)['m_SerializedData']['rid']},touched
    for field,value in original_style.items():
        if isinstance(value,list):assert nav.s[field][:len(value)]==value,field
        else:assert nav.s[field]==value,field
    assert nav.a(selector)['m_Children']==[{'rid':button},{'rid':back}]
    for i in [button,back]:
        assert len(event_parts(nav.data(i)['Events']))==1
        assert struct.unpack_from('<I',event_parts(nav.data(i)['Events'])[0])[0]==624065536
    nav.save()
    payload=env[W].file.save(packer='lz4')
    saved={o.path_id:o for o in UnityPy.load(payload).objects}
    assert set(saved)==set(hashes)
    for pid,h in hashes.items():
        if pid not in changes[W]:assert sha(saved[pid].get_raw_data())==h,(tag,pid)
    for pid,data in changes[W].items():assert saved[pid].read_typetree()==data,(tag,pid)
    source,backup=OUT/tag/W,OUT/('backup-'+tag)/W
    source.parent.mkdir();backup.parent.mkdir()
    source.write_bytes(payload);backup.write_bytes(before)
    transactions.append({'target':str(folder/W),'source':str(source),'backup':str(backup),'before':sha(before),'after':sha(payload)})
    reports.append({'target':tag,'changed_objects':list(changes[W]),'unrelated_objects_unchanged':len(hashes)-len(changes[W]),
        'old_navigation_records_changed':sorted(touched),'selector':selector,'buttons':[button,back],
        'labels':[label,back_label],'removed_event_type':1564320233,'assignment_event_type':624065536,
        'native_assignment_source':'TouchStore/1024 first event','background_objects_unchanged':True,
        'existing_navigation_and_sidebar_state_preserved':True,'style_arrays_preserved':True})

for tx in transactions:assert sha(Path(tx['target']).read_bytes())==tx['before']
for p,h in protected.items():assert sha(Path(p).read_bytes())==h
manifest={'installed':False,'runtime_verified':False,'protected_sha256':protected,'reports':reports,
    'reason':'User reports navigation disappears on background click; remove manager-edit event, use explicit local state assignments.'}
(OUT/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT/'transaction.json').write_text(json.dumps(transactions,ensure_ascii=False,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (OUT/name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif($LASTEXITCODE -ne 0){throw 'Resource transaction failed.'}\n",'utf-8-sig')
(OUT/'说明.md').write_text('修正点击切换背景后导航消失的问题：移除旧经理资料编辑页事件1564320233。改为原生TouchStore所用赋值事件624065536，仅将自定义局部状态TFBackgroundShowStadium设为const.True/const.False。布尔选择器每次只显示一个同外观的“切换背景”按钮，两个按钮分别负责切至球场和切回TF。不改公共背景、图片、目录或其他页面；保留用户最新顶部导航布局及独立皮肤各自状态。回退restore.ps1仅撤销本次事件修正，会回到有问题的旧按钮，请勿作为正常恢复方式。尚未启动游戏，事件修正及跨模板共享状态仍须游戏内验证。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'reports':reports},ensure_ascii=False))
