"""Add a reversible, native two-image background switch to current FM27 assets."""
raise SystemExit('Deprecated: this experiment made navigation disappear on click. Use the documented current-background-switch.json repair; do not regenerate the manager-edit event.')
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, struct, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.classes import PPtr
from UnityPy.helpers import TypeTreeHelper

def extract(file, names):
    tree = ast.parse((R / file).read_text('utf8'))
    nodes = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    exec(compile(ast.Module(body=nodes, type_ignores=[]), file, 'exec'), globals())

oldwrite = TypeTreeHelper.write_value
extract('build-fc-player-hover-layout.py', {'write'})
TypeTreeHelper.write_value = write
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
extract('add-card-six-ratings.py', {'validate_ui'})
extract('build-match-ui-avatars-layout.py', {'refs', 'sd', 'find', 'pointer_remap', 'import_types', 'Doc'})
spec = importlib.util.spec_from_file_location('background_catalog', R / 'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
loc = json.loads((R / 'current-game-location.json').read_text('utf8'))
GAME, SKIN = Path(loc['bundle_root']), Path(loc['skin_packages'])
assert 'Football Manager 27' in str(GAME) and 'Project Taco' not in str(GAME)
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
B = 'ui-backgrounds_assets_common.bundle'
TF, STADIUM = -910000000000149, -910000000000145
STATE = 'TFBackgroundShowStadium'
SCOPE = 'Bool|0|(Session,Explicit,{},{TF27.Background.ShowStadium.v1})'
OUT = R / ('background-switch-button-' + datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-7))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
(OUT / 'templates').mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
f32 = lambda v: struct.unpack('<f',struct.pack('<f',v))[0]
reserved = {int(t['path_id']) for t in json.loads((R / 'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
assert reserved.isdisjoint([TF, STADIUM])
protected = {str(p):sha(p.read_bytes()) for folder in [GAME, SKIN] for p in folder.glob('*.bundle') if p.name != W}
transactions, reports, documents = [], [], []

def direct(path):
    return {'m_kind':1, 'm_direct':{'Path':{'m_path':path}, 'Nullable':0},
            'm_visualFunction':{'m_target':{'m_guid':''}, 'm_inputs':{'m_variable':{'m_argumentBytes':[]}}, 'm_outputs':{'m_variable':{'m_argumentBytes':[]}}}}

def string(value):
    b = value.encode('utf8')
    assert len(b) < 128
    return bytes([len(b)]) + b

def toggle_event(path):
    binding = b'\x01\x01' + string(path)
    payload = struct.pack('<I', 1564320233) + b'\x01' + struct.pack('<I', len(binding)) + binding
    return {'m_bytes':list(b'\x01\x01\x01\x01\x01' + struct.pack('<I', len(payload)) + payload)}

def variables(d, donor, parent, name):
    i = d.add(donor, 1043, parent, name)
    d.data(i).update(ValueVariables=[{'m_name':STATE, 'm_scopeValue':{'m_serializedData':SCOPE}}],
        ReferenceVariables=[], ValueVariables_UxmlAttributeFlags=1, ReferenceVariables_UxmlAttributeFlags=1)
    return i

def record(target, old, new, tag):
    if old == new:
        protected[str(target)] = sha(old)
        return
    backup, source = OUT / ('backup-' + tag) / target.name, OUT / tag / target.name
    backup.parent.mkdir(exist_ok=True)
    source.parent.mkdir(exist_ok=True)
    backup.write_bytes(old)
    source.write_bytes(new)
    transactions.append({'target':str(target), 'backup':str(backup), 'source':str(source), 'before':sha(old), 'after':sha(new)})

for folder, tag in [(GAME, 'game'), (SKIN, 'skin')]:
    before = (folder / W).read_bytes()
    env = {W:UnityPy.load(before), G:UnityPy.load(str(folder / G))}
    objs = {n:{o.path_id:o for o in e.objects} for n,e in env.items()}
    hashes = {i:sha(o.get_raw_data()) for i,o in objs[W].items()}
    changes = {W:{}, G:{}}
    assert reserved.isdisjoint(objs[W])
    bg_env = UnityPy.load(str(folder / B))
    bg_af = bg_env.assets[0]
    assert reserved.isdisjoint(bg_af.objects)
    for pid, name in [(TF, 'TF skin V1'), (STADIUM, 'kunshan stadium')]:
        assert bg_af.objects[pid].type.name == 'Texture2D'
        assert bg_af.objects[pid].peek_name() == name

    donor = Doc(G, name='PersonSearchConditionFiltersMainBlock')
    native_toggle = Doc(G, name='ManagerPersonaBiographicalDetailsEditTile_4x2')
    native_bytes = bytes(native_toggle.a(1009)['Events']['m_bytes'])
    p, native_parts = 4, []
    for _ in range(native_bytes[3]):
        assert native_bytes[p] == 1
        size = struct.unpack_from('<I',native_bytes,p+1)[0]
        p += 5
        native_parts.append(native_bytes[p:p+size])
        p += size
    assert p == len(native_bytes)
    assert native_parts[-1] == bytes(toggle_event('isSummaryActive')['m_bytes'])[9:]
    background = Doc(W, name='GameWorldBackground')
    old_background = copy.deepcopy(background.d)
    assert background.data(1002)['Binding']['m_direct']['Path']['m_path'] == 'game.BackgroundImage.Use3DBackground'
    bg_vars = variables(background, donor, 1001, 'TFBackgroundSharedSelection')
    background.move(bg_vars, 1001, 0)
    background.move(1002, bg_vars)
    background.fill(bg_vars)
    background.st(bg_vars, [(131085, background.num(0))])
    background.data(1002).update(Binding=direct(STATE), Binding_UxmlAttributeFlags=1,
        BindDirectAsMask=0, BindDirectAsMask_UxmlAttributeFlags=1,
        InvertDirectBinding=0, InvertDirectBinding_UxmlAttributeFlags=1,
        Preview={'Mask':1}, Preview_UxmlAttributeFlags=1)
    background.fill(1002)
    # Both branches become non-interactive native visual elements with texture styles.
    source_data = copy.deepcopy(background.r[1008])
    old_image = background.a(1004)
    old_image['m_FullTypeName'] = 'UnityEngine.UIElements.VisualElement'
    background.r[1007]['type'] = copy.deepcopy(source_data['type'])
    background.r[1007]['data'] = copy.deepcopy(source_data['data'])
    background.r[1007]['data']['uxmlAssetId'] = old_image['m_Id']
    background.a(1004)['m_Classes'] = []
    bg_fileid = next(i+1 for i,x in enumerate(background.af.externals) if x.path.lower() == f'archive:/{bg_af.name}/{bg_af.name}'.lower())
    image_pointers = []
    for i, pid, name in [(1004, TF, 'TFBackgroundSkinV1'), (1005, STADIUM, 'TFBackgroundKunshanStadium')]:
        background.data(i).update(name=name, name_UxmlAttributeFlags=1, pickingMode=1, pickingMode_UxmlAttributeFlags=1)
        ptr = {'m_FileID':bg_fileid, 'm_PathID':pid}
        image_pointers.append(ptr)
        background.fill(i)
        background.st(i, [(131085,background.num(0)), (458753,background.val(6,ptr)),
            (262153,background.enum('scale-and-crop')), (458767,background.num(1)),
            (196610,background.val(4,{'r':1.,'g':1.,'b':1.,'a':1.}))])
    background.save()

    nav = Doc(W, name='PrimaryNavigationBar')
    old_nav = copy.deepcopy(nav.d)
    menu = Doc(W, name='MenuBar')
    parent = nav.named('NonDiageticMenu')
    wrapper = variables(nav, donor, parent, 'TFBackgroundButtonSharedSelection')
    nav.move(wrapper, parent, 0)
    nav.st(wrapper, [(131083,nav.enum('row')), (131073,nav.enum('center')), (131074,nav.enum('center')),
        (131084,nav.num(0)), (131085,nav.num(0)), (131092,nav.px(6))])
    button = nav.add(menu, menu.named('PrimaryNavMessagesButton'), wrapper, 'TFBackgroundSwitchButton')
    nav.a(button)['m_Classes'] = ['sibutton', 'buttons-button-secondary-default']
    nav.data(button).update(text='', text_UxmlAttributeFlags=1, StaticText='', StaticText_UxmlAttributeFlags=1,
        Events=toggle_event(STATE), Events_UxmlAttributeFlags=1,
        RightClickEvents={'m_bytes':[]}, RightClickEvents_UxmlAttributeFlags=1,
        BindTextFunction=direct('')['m_visualFunction'], BindTextFunction_UxmlAttributeFlags=1,
        InputActionRef={'m_inputActionAsset':{'m_AssetGUID':'','m_SubObjectName':'','m_SubObjectType':''},'m_actionID':''}, InputActionRef_UxmlAttributeFlags=1,
        HoverBinding={'m_path':''}, HoverBinding_UxmlAttributeFlags=1,
        AuditComponentBinding={'m_path':''}, AuditComponentBinding_UxmlAttributeFlags=1,
        pickingMode=0, pickingMode_UxmlAttributeFlags=1, enabledSelf=1, enabledSelf_UxmlAttributeFlags=1,
        focusable=1, focusable_UxmlAttributeFlags=1, tooltip='TF skin V1 / kunshan stadium', tooltip_UxmlAttributeFlags=1,
        OnlyAcceptsClickEvents=1, OnlyAcceptsClickEvents_UxmlAttributeFlags=1,
        OnlyAcceptsSubmitEvents=0, OnlyAcceptsSubmitEvents_UxmlAttributeFlags=1,
        StopsEventPropagation=1, StopsEventPropagation_UxmlAttributeFlags=1)
    nav.size(button, 76, 28)
    nav.st(button, [(131081,nav.enum('flex')), (131102,nav.enum('relative')), (131073,nav.enum('center')),
        (131088,nav.enum('center')), (262150,nav.px(0)), (262151,nav.px(4)),
        (458752,nav.val(4,{'r':f32(38/255),'g':f32(52/255),'b':f32(69/255),'a':1.})),
        (458753,nav.enum('none')), (458767,nav.num(1))])
    label = nav.add(menu, menu.named('PrimaryNavMessagesLabel'), button, 'TFBackgroundSwitchLabel')
    nav.a(label)['m_Classes'] = ['content-no-wrap', 'sitext-hover-cursor']
    nav.data(label).update(text='切换背景', text_UxmlAttributeFlags=1, TextBinding=direct(''), TextBinding_UxmlAttributeFlags=1,
        pickingMode=1, pickingMode_UxmlAttributeFlags=1)
    # m_kind=0 makes the explicit Chinese text authoritative.
    nav.data(label)['TextBinding']['m_kind'] = 0
    nav.st(label, [(65537,nav.px(11)), (65536,nav.val(4,{'r':1.,'g':1.,'b':1.,'a':1.})),
        (458767,nav.num(1)), (262150,nav.px(0)), (262151,nav.px(0))])
    nav.save()
    original_refs = refs(old_nav)
    assert {i for i in original_refs if original_refs[i] != nav.r[i]} == {parent}
    assert nav.a(parent)['m_Children'][0] == {'rid':wrapper}
    assert background.data(bg_vars)['ValueVariables'] == nav.data(wrapper)['ValueVariables']
    assert background.a(1002)['m_Children'] == [{'rid':1004}, {'rid':1005}]

    meta_obj = next(o for o in objs[W].values() if o.type.name == 'AssetBundle')
    meta = meta_obj.read_typetree()
    original_meta = copy.deepcopy(meta)
    preloads = copy.deepcopy(meta['m_PreloadTable'])
    bg_guids, nav_guids = [], []
    for key, entry in meta['m_Container']:
        pid = entry['asset']['m_PathID']
        if entry['asset']['m_FileID'] != 0:continue
        if pid in [background.obj.path_id, background.sid]:
            bg_guids.append(key)
            span = copy.deepcopy(preloads[entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
            for ptr in image_pointers:
                if ptr not in span:span.append(copy.deepcopy(ptr))
            if span != preloads[entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']]:
                entry['preloadIndex'] = len(meta['m_PreloadTable'])
                entry['preloadSize'] = len(span)
                meta['m_PreloadTable'].extend(span)
        if pid == nav.obj.path_id:nav_guids.append(key)
    assert bg_guids and nav_guids
    if bg_af.name.lower() not in meta['m_Dependencies']:meta['m_Dependencies'].append(bg_af.name.lower())
    if meta != original_meta:
        meta_obj.save_typetree(meta)
        changes[W][meta_obj.path_id] = meta

    catroot = GAME.parent if tag == 'game' else SKIN
    catbefore = (catroot / 'catalog.bin').read_bytes()
    cat = cm.Catalog(catbefore)
    all_locations = {q for _, p in cat.keys() for (q,) in cat.array(p,'I')}
    bgloc = next(q for q in all_locations if cat.location(q)['provider'].endswith('.AssetBundleProvider') and cat.location(q)['internal'].replace('\\','/').endswith('/'+B))
    catalog_audit = []
    for key in dict.fromkeys(bg_guids):
        assert cat.locations(key), ('Missing background catalog key',key)
        for q in cat.locations(key):
            info = cat.location(q)
            assert info['type'][1] in ['UnityEngine.UIElements.VisualTreeAsset','UnityEngine.UIElements.StyleSheet']
            assert cat.location(info['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)
            if bgloc not in info['dependencies']:
                deps = info['dependencies'] + [bgloc]
                payload = b''.join(struct.pack('<I',i) for i in deps)
                import zlib
                struct.pack_into('<II',cat.data,q+12,cat.append(payload,True),zlib.crc32(payload))
            catalog_audit.append({'key':key,'location':q,'background_dependency':True})
    # Check existing actual preload membership; no new template GUID is introduced.
    preload_locations = {q for label in ['GameWorldVisualTreeAssetPreload', 'GlobalVisualTreeAssetPreload'] for q in cat.locations(label)}
    tree_keys = []
    for key, entry in meta['m_Container']:
        if entry['asset']['m_FileID']==0 and entry['asset']['m_PathID'] in [background.obj.path_id,nav.obj.path_id]:tree_keys.append(key)
    for key in dict.fromkeys(tree_keys):
        assert cat.locations(key)
        tree_locations = [q for q in cat.locations(key) if cat.location(q)['type'][1] == 'UnityEngine.UIElements.VisualTreeAsset']
        assert tree_locations and any(q in preload_locations for q in tree_locations), ('Missing actual preload',key)
        for q in cat.locations(key):
            assert cat.location(q)['type'][1] in ['UnityEngine.UIElements.VisualTreeAsset','UnityEngine.UIElements.StyleSheet']
            assert cat.location(cat.location(q)['dependencies'][0])['internal'].replace('\\','/').endswith('/'+W)
    output = env[W].file.save(packer='lz4')
    check_env = UnityPy.load(output, (folder / B).read_bytes())
    check_af = next(a for a in check_env.assets if a.name == background.af.name)
    saved = check_af.objects
    assert set(saved) == set(hashes)
    for pid,h in hashes.items():
        if pid not in changes[W]:assert sha(saved[pid].get_raw_data()) == h, ('Unrelated object changed',tag,pid)
    for pid,d in changes[W].items():assert saved[pid].read_typetree() == d, (tag,pid)
    for ptr in image_pointers:
        assert PPtr(**ptr,assetsfile=check_af).deref().get_raw_data() == bg_af.objects[ptr['m_PathID']].get_raw_data()
    record(folder / W, before, output, tag)
    catraw = bytes(cat.data)
    record(catroot / 'catalog.bin', catbefore, catraw, tag)
    hash_before = (catroot / 'catalog.hash').read_bytes()
    record(catroot / 'catalog.hash', hash_before, hashlib.md5(catraw).hexdigest().encode() if catraw != catbefore else hash_before, tag)
    reports.append({'target':tag, 'background_path_id':background.obj.path_id, 'navigation_path_id':nav.obj.path_id,
        'button_node':button, 'label_node':label, 'state':STATE, 'scope':SCOPE,
        'default':'TF skin V1', 'alternative':'kunshan stadium', 'texture_path_ids':[TF,STADIUM],
        'native_event_source':'ManagerPersonaBiographicalDetailsEditTile_4x2/1009',
        'changed_objects':list(changes[W]), 'unchanged_objects':len(hashes)-len(changes[W]),
        'catalog':catalog_audit, 'existing_navigation_records_preserved':True})

for tx in transactions:assert sha(Path(tx['target']).read_bytes()) == tx['before']
for p,h in protected.items():assert sha(Path(p).read_bytes()) == h
manifest = {'installed':False,'runtime_verified':False,'protected_sha256':protected,'reports':reports}
(OUT / 'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(OUT / 'transaction.json').write_text(json.dumps(transactions,ensure_ascii=False,indent=2),'utf8')
for name,arg in [('install.ps1',''),('restore.ps1',' --restore')]:
    (OUT / name).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' '"+str(R/'install-independent-resource-patch.py')+"' $PSScriptRoot"+arg+"\nif($LASTEXITCODE -ne 0){throw 'Resource transaction failed.'}\n",'utf-8-sig')
(OUT / '说明.md').write_text('右上角搜索等工具按钮旁新增“切换背景”。默认TF skin V1，点击后与kunshan stadium来回切换；复用现有两张纹理，不修改图片包。公共背景两分支以等比裁切铺满。原生布尔切换事件驱动独立Session/Explicit共享键，本次游戏会话内共享选择，退出后默认TF。游戏及独立主皮肤各自基于当前资源增量修改，保留各自侧栏、导航、悬浮和页面修改。页面内既有不透明卡片底色仍会遮挡其下方背景。安装后需要用户在游戏内验证按钮显示、点击切换及跨页面保持，文件校验不代表运行成功。未启动游戏或操作桌面/浏览器。restore.ps1校验当前资源哈希后回退本次修改；后续资源变化不能用旧整包覆盖。','utf8')
print(json.dumps({'prepared':True,'output':str(OUT),'files':len(transactions),'reports':reports},ensure_ascii=False),flush=True)
