"""Fix only the primary navigation palette; preserve current bundles and bindings."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, subprocess, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
S = 'ui-styles_assets_default.bundle'
BG = 'ui-backgrounds_assets_common.bundle'
ROOT, INK = 'fm27-fixed-primary-nav', 'fm27-fixed-nav-ink'
sha = lambda b: hashlib.sha256(b).hexdigest()
f32 = lambda v: struct.unpack('<f', struct.pack('<f', v))[0]
refs = lambda d: {r['rid']: r for r in d['references']['RefIds']}

# Import definitions only: historical scripts must never run their installers.
oldwrite = TypeTreeHelper.write_value
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
source = ast.parse((R / 'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if
    isinstance(n, ast.FunctionDef) and n.name == 'write' or
    isinstance(n, ast.ClassDef) and n.name == 'Styles'], type_ignores=[]), '<serialization-helpers>', 'exec'))
TypeTreeHelper.write_value = write
source = ast.parse((R / 'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_ui'], type_ignores=[]), '<ui-validator>', 'exec'))

before = {folder / n: (folder / n).read_bytes() for folder in [GAME, SKIN] for n in [W, S]}
assert before[GAME / W] == before[SKIN / W], 'Game/skin navigation bundle mismatch'
protected = {}
for folder in [GAME, SKIN]:
    for n in [G, BG, 'ui-visualfunctions_assets_all.bundle', 'ui-tileslayouts_assets_all.bundle',
              'ui-textures_assets_all.bundle', 'ui-styles_assets_common.bundle',
              'ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle']:
        p = folder / n
        if p.exists(): protected[p] = sha(p.read_bytes())
    for n in ['catalog.bin', 'catalog.hash']:
        p = (GAME.parent if folder == GAME else folder) / n
        if p.exists(): protected[p] = sha(p.read_bytes())
for n in ['AGENTS.md', 'reserved-texture-ids.json', 'current-custom-textures.json',
          '球员弹窗最终版本说明.md', '球员弹窗最终版本资源快照.json']:
    p = R / n
    if p.exists(): protected[p] = sha(p.read_bytes())

reserved = json.loads((R / 'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned = {int(x['path_id']) for x in reserved}
banned_names = {x['name'].lower() for x in reserved}
env = {n: UnityPy.load(before[GAME / n]) for n in [W, S]}
objs = {n: {o.path_id:o for o in en.objects} for n, en in env.items()}
hashes = {n: {i:sha(o.get_raw_data()) for i,o in oo.items()} for n,oo in objs.items()}
expected = {W:{}, S:{}}

def named(oo, name):
    result = [o for o in oo.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name]
    assert len(result) == 1, (name, len(result))
    return result[0]

def color(code):
    return dict(zip(['r','g','b','a'], [f32(int(code[i:i+2],16)/255) for i in [0,2,4]] + [1.]))

grey, black, white = color('E7E7E7'), color('000000'), color('FFFFFF')
lake_left, lake_right = color('35C6E8'), color('078BC4')
navobj = named(objs[W], 'PrimaryNavigationBar')
d = navobj.read_typetree(); original = copy.deepcopy(d); rr = refs(d)
sid = d['inlineSheet']['m_PathID']; s = objs[W][sid].read_typetree(); original_s = copy.deepcopy(s)
st = Styles(s)
assert rr[1002]['data']['m_SerializedData'] and ROOT not in rr[1002]['data']['m_Classes']

def sd(rid): return rr.get(rr[rid]['data'].get('m_SerializedData',{}).get('rid'),{}).get('data',{})

assert sd(1002)['name'] == 'MainNav'
assert sd(1004)['name'] == 'NavThemeStyleSetter'
assert sd(1011)['name'] == 'NavForegroundStyleSetter'
assert sd(1161)['name'] == 'ContinueButton'
rr[1002]['data']['m_Classes'] += [ROOT, 'nav-on-light']
sd(1004)['BindFunction'] = copy.deepcopy(sd(1011)['BindFunction'])
sd(1004)['BindFunction_UxmlAttributeFlags'] = 1
for key in ['PrimaryColorDataLink', 'SecondaryColorDataLink']:
    assert 'Titlebar' in sd(1011)[key]['m_path']
    sd(1011)[key] = {'m_path':''}
    sd(1011)[key + '_UxmlAttributeFlags'] = 1
st.edit(rr[1002], [st.p(458752, st.h(4, grey))])
st.edit(rr[1005], [st.p(131081, st.en('none'))])
# Retain the color-strip footprint but remove its club-colored paint, not the crest.
st.edit(rr[1013], [st.p(458767, st.num(0))])

excluded = {'ClubIcon', 'NationIcon', 'thumbnails-alt-person-picture', 'StandardTextTooltip',
            'PrimaryNavigationBarGradient', 'PrimaryNavigationBarClubColours',
            'dashboard-hud-continue_button-default'}
markers = []
for rid, rec in rr.items():
    a = rec.get('data', {})
    if 'm_FullTypeName' not in a: continue
    data = sd(rid)
    alias = data.get('templateId')
    functional_icon = any(c.startswith(('nd-', 'ui-concepts-', 'game-concepts-transfer_')) for c in a.get('m_Classes', []))
    if alias and alias not in excluded or a['m_FullTypeName'] == 'SI.Bindable.SIText' or functional_icon:
        a['m_Classes'].append(INK)
        markers.append({'rid':rid, 'name':data.get('name'), 'template':alias})
assert any(m['template'] == 'MenuBar' for m in markers)
assert all(INK not in rr[rid]['data']['m_Classes'] for rid in [1161,1163,1165,1228,1232])

# Add literal, scoped USS rules to an already loaded sheet: no new assets or GUIDs.
sheetobj = named(objs[S], 'AlwaysAppliedStyleSheet')
sheet = sheetobj.read_typetree(); original_sheet = copy.deepcopy(sheet); ss = Styles(sheet)
root = '#' + 'MainNav' + '.' + ROOT
rule_records = []

def selector(text, index):
    tokens = text.split(); selectors = []; specificity = 1
    for token in tokens:
        parts = []
        for prefix, value in re.findall(r'([.#:]?)([a-zA-Z_][\w-]*|\*)', token):
            typ = {'.':3, '#':6, ':':4}.get(prefix, 1 if value == '*' else 2)
            parts.append({'m_Value':value, 'm_Type':typ})
            specificity += {1:0, 2:1, 3:10, 4:10, 6:100}[typ]
        assert parts, token
        selectors.append({'m_Parts':parts, 'm_PreviousRelationship':0 if not selectors else 2})
    return {'m_Specificity':specificity, 'm_Selectors':selectors, 'ruleIndex':index}

def rule(selectors, properties):
    index = len(sheet['m_Rules'])
    props = []
    for key, value in properties:
        custom = isinstance(key, str)
        handle = ss.h(4, copy.deepcopy(value)) if isinstance(value, dict) else ss.num(value)
        props.append({'m_Id':-1 if custom else key, 'm_CustomName':key if custom else '',
                      'm_Line':-1, 'm_Values':[handle]})
    sheet['m_Rules'].append({'m_ComplexSelectors':[selector(t,index) for t in selectors], 'm_Properties':props, 'line':-1})
    rule_records.append({'index':index, 'selectors':selectors, 'properties':[k for k,v in properties]})

def ink_targets(target):
    return [root+' .'+INK+' '+target, root+' .'+INK+target if target[0] in '.#:' else root+' '+target+'.'+INK]

text_targets = ['SIText', 'TextElement', 'Label', '.global-text-primary', '.global-text-secondary', '.portal-text', '.nd-flat-black', '.sitext']
rule([t for target in text_targets for t in ink_targets(target)], [(65536,black)])
icon_targets = ['.portal-image', '.nd-flat-black', '.nd-search', '.nd-settings', '.nd-fmpedia', '.nd-edit',
                '.nd-globe', '.nd-microphone', '.nd-bookmark', '.ui-concepts-chevron-left_small',
                '.ui-concepts-chevron-right_small', '.ui-concepts-chevron-down_small',
                '.ui-concepts-edit_small', '.game-concepts-transfer_small', '#leading-icon', '#trailing-icon',
                '#NavTabDropdownIndicator']
rule([t for target in icon_targets for t in ink_targets(target)], [(196610,black)])
# Suppress decorative portal gradients only inside ordinary navigation controls.
rule([root+' .'+INK+' SIGradient', root+' .'+INK+' .sigradient'], [(458767,0.)])
controls = ['.buttons-controls-pc-default--active-true', '.buttons-controls-pc-default--active-false',
            '.navigation-primary-nav-calendar-wiget-calendar', '.calendar-widget-time-container',
            '.si-dropdown__selection-field']
rule([t for target in controls for t in ink_targets(target)], [(458752,grey),(262146,color('B8B8B8'))])
navbuttons = ['.navigation-tab-portal-default-active-true', '.navigation-tab-portal-default-active-false',
              '.nonDiegeticButton', '.nonDiegeticButtonMin-res']
for pseudo, code in [(':hover:enabled','E7E7E7'), (':active:enabled','C7C7C7'), (':checked','D0D0D0')]:
    rule([t for target in controls+navbuttons for t in ink_targets(target+pseudo)], [(458752,color(code))])

# The native gradient binding already selects stylesheet colors (Condition=False).
# Override those two custom properties while retaining its reverse/slide behavior.
button = root+' #ContinueButton'
rule([button+' .continue-button---gradient'], [('--start-colour',lake_left),('--end-colour',lake_right)])
rule([button+' .continue-button'], [(458752,lake_right),(262146,lake_right)])
# This optional native underlay has an inline purple fill that outranks USS.
# Hide only its paint; the button retains its blue surface and animated gradients.
rule([button+' #continue-button-background'], [(458767,0.)])
rule([button+' .continue-button:hover:enabled'], [(458752,color('067BAE'))])
rule([button+' .continue-button--background-image'], [(458767,0.)])
rule([button+' SIText',button+' .white',button+' .sitext'], [(65536,white)])
rule([button+' #primary-icon-image',button+' #primary-icon',button+' .ui-concepts-person_small',
      button+' .ui-concepts-continue_medium'], [(196610,white)])

# The complete preexisting trees, behavior records and styles are immutable except
# for the explicitly enumerated color binding / class / inline rule edits above.
for rid, old in refs(original).items():
    actual = copy.deepcopy(rr[rid]); prior = old.get('data',{})
    if 'm_FullTypeName' in prior:
        actual['data']['m_Classes'] = copy.deepcopy(prior['m_Classes'])
        actual['data']['m_RuleIndex'] = prior['m_RuleIndex']
    if rid == rr[1004]['data']['m_SerializedData']['rid']:
        for k in ['BindFunction','BindFunction_UxmlAttributeFlags']: actual['data'][k] = prior[k]
    if rid == rr[1011]['data']['m_SerializedData']['rid']:
        for k in ['PrimaryColorDataLink','SecondaryColorDataLink','PrimaryColorDataLink_UxmlAttributeFlags','SecondaryColorDataLink_UxmlAttributeFlags']:
            actual['data'][k] = prior[k]
    assert actual == old, ('Unexpected behavioral/layout change',rid)
assert set(rr) == set(refs(original))
for current, old in [(s,original_s), (sheet,original_sheet)]:
    for k,v in old.items():
        if isinstance(v,list): assert current[k][:len(v)] == v, k
        else: assert current[k] == v, k
for rid in [1161,1163,1165,1228,1232]: assert rr[rid] == refs(original)[rid]
validate_ui(d,s)

for n,ob,data in [(W,navobj,d),(W,objs[W][sid],s),(S,sheetobj,sheet)]:
    ob.save_typetree(data); expected[n][ob.path_id] = copy.deepcopy(data)
payloads = {}; saved = {}
for n,en in env.items():
    payloads[n] = en.file.save(packer='lz4')
    saved[n] = {o.path_id:o for o in UnityPy.load(payloads[n]).objects}
    assert set(saved[n]) == set(objs[n]) and banned.isdisjoint(saved[n])
    for pid,ob in saved[n].items():
        if pid in expected[n]: assert ob.read_typetree() == expected[n][pid], ('Roundtrip',n,pid)
        else: assert sha(ob.get_raw_data()) == hashes[n][pid], ('Unrelated object changed',n,pid)
validate_ui(saved[W][navobj.path_id].read_typetree(),saved[W][sid].read_typetree())

# The installed game and Skin Builder have small preexisting style differences.
# Apply the identical new scoped rules independently; do not replace either base.
skin_env = UnityPy.load(before[SKIN/S]); skin_obs = {o.path_id:o for o in skin_env.objects}
skin_hashes = {i:sha(o.get_raw_data()) for i,o in skin_obs.items()}
skin_sheet_obj = named(skin_obs,'AlwaysAppliedStyleSheet')
skin_sheet = skin_sheet_obj.read_typetree(); original_skin_sheet=copy.deepcopy(skin_sheet)
skin_ss = Styles(skin_sheet)
for added in sheet['m_Rules'][len(original_sheet['m_Rules']):]:
    newrule=copy.deepcopy(added);newindex=len(skin_sheet['m_Rules'])
    for sel in newrule['m_ComplexSelectors']:sel['ruleIndex']=newindex
    for prop in newrule['m_Properties']:
        prop['m_Values']=[skin_ss.h(h['m_ValueType'],copy.deepcopy(sheet[poolmap[h['m_ValueType']]][h['valueIndex']])) for h in prop['m_Values']]
    skin_sheet['m_Rules'].append(newrule)
for k,v in original_skin_sheet.items():
    if isinstance(v,list):assert skin_sheet[k][:len(v)]==v,k
    else:assert skin_sheet[k]==v,k
skin_sheet_obj.save_typetree(skin_sheet)
skin_payload=skin_env.file.save(packer='lz4')
skin_saved={o.path_id:o for o in UnityPy.load(skin_payload).objects}
assert set(skin_saved)==set(skin_obs) and banned.isdisjoint(skin_saved)
for pid,ob in skin_saved.items():
    if pid==skin_sheet_obj.path_id:assert ob.read_typetree()==skin_sheet
    else:assert sha(ob.get_raw_data())==skin_hashes[pid],('Unrelated skin style changed',pid)

# Verify the gradient's actual bindings use style colors, not club/competition data.
ge = UnityPy.load(str(GAME/G)); go = {o.path_id:o for o in ge.objects}
cd = named(go,'continue-button').read_typetree(); cr = refs(cd)
for rid in [1028,1029]:
    binding = cr[cr[rid]['data']['m_SerializedData']['rid']]['data']['BindGradientFunc']
    assert binding['m_target']['m_guid'] == '7da12e903fc84624fbf75ebc4c9b7fd7'
    raw = bytes(binding['m_inputs']['m_variable']['m_argumentBytes'])
    assert b'Const.False' in raw or b'const.False' in raw
    assert cr[rid]['data']['m_Classes'][0] == 'continue-button---gradient'

spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
catalog_audits=[]
world_assets={W:saved[W], G:go}
for folder in [GAME, SKIN]:
    catpath=(GAME.parent if folder==GAME else SKIN)/'catalog.bin'
    cat=cm.Catalog(catpath.read_bytes()); audit=[]; native=[]
    for bn,oo in world_assets.items():
        meta=next(ob.read_typetree() for ob in oo.values() if ob.type.name=='AssetBundle')
        for guid,entry in meta['m_Container']:
            if not re.fullmatch('[0-9a-f]{32}',guid) or entry['asset']['m_FileID']!=0:continue
            ob=oo.get(entry['asset']['m_PathID'])
            if ob is None or ob.type.name!='MonoBehaviour':continue
            custom=-1000000000000000<ob.path_id<-900000000000000
            target=ob.path_id==navobj.path_id or ob.peek_name()=='continue-button'
            if not custom and not target:continue
            tree=ob.read_typetree()
            kind='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in tree else 'SI.VisualScripting.VisualFunction' if 'm_nodes' in tree else None
            if kind is None:continue
            locations=[loc for loc in cat.locations(guid) if cat.location(loc)['type'][1]==kind]
            assert locations, ('Missing typed catalog registration',guid,kind)
            for loc in locations:
                v=cat.location(loc)
                assert v['type'][1]==kind and v['internal']==guid and v['dependencies'],(guid,v)
                owner=cat.location(v['dependencies'][0])['internal'].replace('\\','/')
                assert owner.endswith('/'+bn),(guid,owner)
                if custom:
                    assert any(cat.location(x)['internal'].replace('\\','/').endswith('/'+BG) for x in v['dependencies']),(guid,'Missing backgrounds dependency')
            (audit if custom else native).append({'guid':guid,'name':ob.peek_name(),'type':kind,'bundle':bn,'path_id':str(ob.path_id)})
    # Confirm the existing native gradient visual function resolves through Addressables.
    funclocations=cat.locations('7da12e903fc84624fbf75ebc4c9b7fd7');assert funclocations
    for loc in funclocations:
        v=cat.location(loc)
        assert v['type'][1]=='SI.VisualScripting.VisualFunction'
        assert cat.location(v['dependencies'][0])['internal'].replace('\\','/').endswith('/ui-visualfunctions_assets_all.bundle')
    assert len(audit)>=82 and len(native)==2,(len(audit),len(native))
    catalog_audits.append({'catalog':str(catpath),'custom_resources':audit,'native_resources':native,'gradient_function_registered':True})

be=UnityPy.load(str(GAME/BG));bo={o.path_id:o for o in be.objects}
bm=next(ob.read_typetree() for ob in bo.values() if ob.type.name=='AssetBundle')
assert banned.isdisjoint(bo)
assert all(ob.peek_name().lower() not in banned_names for ob in bo.values() if ob.type.name=='Texture2D')
assert all(k.lower() not in banned_names and v['asset']['m_PathID'] not in banned for k,v in bm['m_Container'])
assert all(p['m_PathID'] not in banned for p in bm['m_PreloadTable'])
active=json.loads((R/'current-custom-textures.json').read_text('utf8'))['textures'];assert len(active)==176
for t in active:
    ob=bo[int(t['path_id'])]
    assert ob.type.name=='Texture2D' and ob.peek_name()==t['name'] and sha(ob.get_raw_data())==t['texture_sha256'],t['name']
assert bo[-910000000000145].peek_name()=='kunshan stadium'

for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h,p
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S')
out=R/('primary-navigation-grey-lake-blue-'+stamp);out.mkdir();(out/'templates').mkdir()
for name,data in [('PrimaryNavigationBar',d),('PrimaryNavigationBar-inlineStyle',s),('AlwaysAppliedStyleSheet-game',sheet),('AlwaysAppliedStyleSheet-skin',skin_sheet)]:
    (out/'templates'/ (name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
target_payloads={GAME/W:payloads[W],SKIN/W:payloads[W],GAME/S:payloads[S],SKIN/S:skin_payload}
sources={}
for folder,tag in [(GAME,'game'),(SKIN,'skin')]:
    (out/('backup-'+tag)).mkdir()
    (out/tag).mkdir()
    for n in [W,S]:
        (out/('backup-'+tag)/n).write_bytes(before[folder/n])
        source=out/tag/n;source.write_bytes(target_payloads[folder/n]);sources[str(folder/n)]=str(source)
report={'serialization_roundtrip':True,'unchanged_object_hashes_verified':True,
        'modified_objects':{n:{str(i):t['m_Name'] for i,t in changes.items()} for n,changes in expected.items()},
        'primary_background':'#E7E7E7','primary_content':'#000000','continue_gradient':['#35C6E8','#078BC4'],
        'continue_content':'#FFFFFF','native_continue_gradient_binding_unchanged':True,
        'native_continue_actions_and_state_bindings_unchanged':True,'badge_instances_unchanged':True,
        'second_navigation_and_other_templates_byte_identical':True,'active_176_texture_hashes_verified':True,
        'reserved_70_absent_from_objects_container_preload':True,'catalog_audits':catalog_audits,
        'content_markers':markers,'appended_scoped_rules':rule_records,'runtime_verified':False,
        'distinct_game_skin_style_bases_preserved':True}
manifest={'installed':False,'runtime_verified':False,'output':str(out),
          'before_sha256':{str(p):sha(b) for p,b in before.items()},'after_sha256':{str(p):sha(b) for p,b in target_payloads.items()},
          'protected_sha256':{str(p):h for p,h in protected.items()},'missing_before':[], 'verification':report}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(out/'verification.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps({'game':str(GAME),'skin':str(SKIN),'files':[W,S],'sources':sources,
    'before':{str(p):str(out/('backup-game' if p.parent==GAME else 'backup-skin')/p.name) for p in before},'missing':[]},ensure_ascii=False,indent=2),'utf8')
(out/'installer.py').write_bytes((R/'install-primary-navigation-patch.py').read_bytes())
for action,flag in [('install',''),('restore',' --restore')]:
    (out/(action+'.ps1')).write_text("$ErrorActionPreference='Stop'\n& '"+sys.executable+"' (Join-Path $PSScriptRoot 'installer.py') $PSScriptRoot"+flag+"\nif($LASTEXITCODE -ne 0){throw 'Operation failed.'}\n",'utf-8-sig')
(out/'修改说明.md').write_text('顶部主导航固定背景 #E7E7E7，普通文字与功能图标 #000000；取消俱乐部标题栏颜色与明暗主题切换，隐藏动态背景及装饰色条。\n右上角操作按钮改为湖蓝渐变 #35C6E8 → #078BC4，文字和箭头保留白色；原生渐变反转、滑动、禁用、处理和点击逻辑保留。\n全部新增样式均限于 MainNav.fm27-fixed-primary-nav；队徽、第二行导航、正文、自定义卡面、评分公式和图片包保持原样。没有新增对象、GUID、Path ID 或目录依赖。\n序列化读回、无关对象字节哈希、两份 catalog 自定义模板和评分函数登记、176张有效图片哈希及70个禁用资源缺席校验通过。游戏实际显示与交互尚待重启确认。\ninstall.ps1 安装，restore.ps1 在版本一致时回退；安装/回退前退出游戏。\n','utf8')
print(json.dumps({'prepared':True,'output':str(out),'modified_objects':report['modified_objects'],
    'custom_resources_checked':[len(a['custom_resources']) for a in catalog_audits],
    'scoped_rules':len(rule_records),'runtime_verified':False},ensure_ascii=False),flush=True)
