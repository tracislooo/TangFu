"""Prepare a reversible holiday shortcut from the currently installed native UI."""
from pathlib import Path
import ast, copy, datetime, hashlib, importlib.util, json, re, struct, sys

R = Path(__file__).resolve().parent
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper

GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
S = 'ui-styles_assets_default.bundle'
F = 'ui-visualfunctions_assets_all.bundle'
ROOT = 'fm27-header-holiday-shortcut'
sha = lambda b: hashlib.sha256(b).hexdigest()
refs = lambda d: {r['rid']: r for r in d['references']['RefIds']}
poolmap = {2:'floats', 3:'dimensions', 4:'colors', 5:'strings', 6:'assets', 7:'strings', 8:'strings'}
oldwrite = TypeTreeHelper.write_value
for filename, names in [('build-fc-player-hover-layout.py', {'write', 'Styles'}),
                        ('add-card-six-ratings.py', {'validate_ui'}),
                        ('fix-primary-navigation-grey-lake-blue.py', {'selector'})]:
    tree = ast.parse((R / filename).read_text('utf8'))
    definitions = [n for n in tree.body if isinstance(n, (ast.FunctionDef, ast.ClassDef)) and n.name in names]
    exec(compile(ast.Module(body=definitions, type_ignores=[]), filename + ':definitions-only', 'exec'))
TypeTreeHelper.write_value = write

before = {folder/n: (folder/n).read_bytes() for folder in [GAME, SKIN] for n in [W, S]}
assert before[GAME/W] == before[SKIN/W], 'Game and skin world bundles differ; investigate before patching.'
protected = {}
for folder in [GAME, SKIN]:
    for n in [G, F, 'ui-backgrounds_assets_.bundle', 'ui-backgrounds_assets_common.bundle',
              'ui-styles_assets_common.bundle', 'ui-tileslayouts_assets_all.bundle',
              'ui-visualtreeassets_assets_introvisualtreeassetpreload.bundle']:
        p = folder/n
        if p.exists(): protected[p] = sha(p.read_bytes())
for n in ['AGENTS.md', 'reserved-texture-ids.json', 'current-custom-textures.json']:
    protected[R/n] = sha((R/n).read_bytes())
for folder in [GAME.parent, SKIN]:
    for n in ['catalog.bin', 'catalog.hash']:
        if (folder/n).exists(): protected[folder/n] = sha((folder/n).read_bytes())
reserved = json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
banned = {int(t['path_id']) for t in reserved}
banned_names = {t['name'].lower() for t in reserved}

env = UnityPy.load(before[GAME/W]); oo = {o.path_id:o for o in env.objects}
old_hashes = {i:sha(o.get_raw_data()) for i,o in oo.items()}
named = lambda name: next(o for o in oo.values() if o.type.name == 'MonoBehaviour' and o.peek_name() == name)
nav = named('PrimaryNavigationBar'); doc = nav.read_typetree(); original = copy.deepcopy(doc)
rr = refs(doc); sheet_id = doc['inlineSheet']['m_PathID']; sheet = oo[sheet_id].read_typetree(); st = Styles(sheet)
widget = named('GoOnHolidayWidget').read_typetree()
choose = named('HolidayReturnDateTypeChooseRadioButtonOption').read_typetree()
wr, cr = refs(widget), refs(choose)
serial = lambda records, i: records[records[i]['data']['m_SerializedData']['rid']]['data']
assert serial(rr,1161)['name'] == 'ContinueButton'
assert all(ROOT not in r.get('data',{}).get('m_Classes',[]) for r in rr.values()), 'Shortcut already installed.'
assert wr[1022]['data']['m_FullTypeName'] == 'SI.Bindable.SIEnabled'
assert serial(wr,1022)['Binding']['m_direct']['Path']['m_path'] == 'holiday.CanConfirm'

next_rid = max(rr) + 1
next_element_id = 1902700000
created = []
usings_before = copy.deepcopy(doc['m_Usings'])

def copy_subtree(source, root, parent, shallow=False):
    """Copy the element and its serialized/override/component closure, excluding ancestors."""
    global next_rid, next_element_id
    sr = refs(source); records = {}; visiting = set()
    def collect(i, is_root=False):
        if i == -2 or i in visiting: return
        visiting.add(i); r = copy.deepcopy(sr[i]); records[i] = r
        a = r.get('data', {})
        if is_root and shallow: a['m_Children'] = []
        def visit(v, key=''):
            if key == 'm_Parent': return
            if isinstance(v, dict):
                if set(v) == {'rid'}: collect(v['rid'])
                else:
                    for k,x in v.items(): visit(x,k)
            elif isinstance(v,list):
                for x in v: visit(x)
        visit(a)
    collect(root, True)
    mapping = {i:next_rid+n for n,i in enumerate(records)}; next_rid += len(mapping)
    ids = {}
    for rec in records.values():
        if 'm_Id' in rec.get('data',{}):
            ids[rec['data']['m_Id']] = next_element_id; next_element_id += 1
    def fix(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:
                if v['rid'] != -2: v['rid'] = mapping[v['rid']]
            else:
                for k,x in v.items():
                    if k in ['m_Id','uxmlAssetId','m_ParentId'] and isinstance(x,int) and x in ids: v[k]=ids[x]
                    else: fix(x)
        elif isinstance(v,list):
            for x in v: fix(x)
    source_sheet = oo[source['inlineSheet']['m_PathID']].read_typetree()
    def import_handle(h):
        h=copy.deepcopy(h); pool=poolmap.get(h['m_ValueType'])
        if pool:
            sheet[pool].append(copy.deepcopy(source_sheet[pool][h['valueIndex']]))
            h['valueIndex']=len(sheet[pool])-1
        return h
    for old,r in records.items():
        r['rid']=mapping[old]
        a=r.get('data',{})
        if old==root: a['m_Parent']={'rid':-2}
        fix(a)
        if a.get('m_RuleIndex',-1)>=0:
            rule=copy.deepcopy(source_sheet['m_Rules'][a['m_RuleIndex']]); rule['m_ComplexSelectors']=[]
            for prop in rule['m_Properties']: prop['m_Values']=[import_handle(h) for h in prop['m_Values']]
            a['m_RuleIndex']=len(sheet['m_Rules']); sheet['m_Rules'].append(rule)
        rr[r['rid']]=r; doc['references']['RefIds'].append(r); created.append(r['rid'])
    new=mapping[root]; rr[new]['data']['m_Parent']={'rid':parent}
    rr[parent]['data']['m_Children'].append({'rid':new})
    for r in records.values():
        alias=r.get('data',{}).get('m_TemplateAlias')
        if alias:
            using=next(u for u in source['m_Usings'] if u['alias']==alias)
            existing=next((u for u in doc['m_Usings'] if u['alias']==alias),None)
            assert existing is None or existing==using, ('Template alias collision',alias)
            if existing is None: doc['m_Usings'].append(copy.deepcopy(using))
    return new,mapping

def sd(i): return serial(rr,i)
def rename(i,name): sd(i).update(name=name,name_UxmlAttributeFlags=1)
def edit(i,props): st.edit(rr[i],props)
P=st.p
def dimensions(width=None,height=None):
    props=[P(131084,st.num(0)),P(131085,st.num(0)),P(262150,st.px(0)),P(262151,st.px(0)),
           P(131097,st.px(0)),P(131096,st.px(0)),P(131094,{'m_ValueType':1,'valueIndex':3}),
           P(131095,{'m_ValueType':1,'valueIndex':3})]
    if width is not None: props.append(P(131105,st.px(width)))
    if height is not None: props.append(P(131087,st.pct(height)))
    return props

# Same visibility condition as Continue, inserted between the clock and Continue.
visible,_=copy_subtree(original,1114,1042,True); rename(visible,'HeaderHolidayShortcutVisible')
rr[1042]['data']['m_Children'].remove({'rid':visible})
insert_at=next(i for i,c in enumerate(rr[1042]['data']['m_Children']) if c['rid']==1114)
rr[1042]['data']['m_Children'].insert(insert_at,{'rid':visible})
root,_=copy_subtree(widget,1001,visible,True); rename(root,'HeaderHolidayShortcut')
rr[root]['data']['m_Classes']=[ROOT,'flex-no-shrink-class']
defaults,_=copy_subtree(widget,1025,root,True); rename(defaults,'HeaderHolidayDefaults')
assert len(sd(defaults)['ValueVariables'])==1
sd(defaults)['ValueVariables'][0]['m_name']='headerHolidayFallbackIndex'
sd(defaults)['ValueVariables'][0]['m_scopeValue']['m_serializedData']='Int|2|'
body,_=copy_subtree(widget,1002,defaults,True); rename(body,'HeaderHolidayShortcutRows')
rr[body]['data']['m_Classes']=['fm27-holiday-rows']
drop,dropmap=copy_subtree(choose,1007,body); rename(drop,'HeaderHolidayDate')
rr[drop]['data']['m_Classes']=['fm27-holiday-date']
enabled,buttonmap=copy_subtree(widget,1022,body); rename(enabled,'HeaderHolidayCanConfirm')
button=buttonmap[1037]; rename(button,'HeaderConfirmHoliday')
rr[enabled]['data']['m_Classes']=['fm27-holiday-confirm-enabled']
rr[button]['data']['m_Classes'].append('fm27-holiday-confirm')
date,date_map=copy_subtree(choose,1008,body); rename(date,'HeaderHolidayCustomDate')
rr[date]['data']['m_Classes']=['fm27-holiday-custom-date']

def string(text):
    raw=text.encode('utf8'); assert len(raw)<128
    return bytes([len(raw)])+raw
def set_event(source,destination):
    # Native SetBinding event encoding, also used by overview-position-rectangle-zones.py.
    a=b'\x01\x01'+string(source); b=b'\x01\x01'+string(destination)
    payload=struct.pack('<I',0x57e10fd9)+b'\x01'+struct.pack('<I',len(a))+a+struct.pack('<I',len(b))+b+b'\x00\x00'
    return {'m_bytes':list(b'\x01\x01\x01\x01\x01'+struct.pack('<I',len(payload))+payload)}
def event_payloads(event):
    b=bytes(event['m_bytes']); assert b[:3]==b'\x01\x01\x01'
    count=b[3]; p=4; parts=[]
    for _ in range(count):
        assert b[p]==1; length=struct.unpack_from('<I',b,p+1)[0]
        parts.append(b[p:p+5+length]); p+=5+length
    assert p==len(b); return parts
def combine_events(*events):
    parts=[part for event in events for part in event_payloads(event)]
    return {'m_bytes':list(b'\x01\x01\x01'+bytes([len(parts)])+b''.join(parts))}
# Validate composition against an existing two-action native button before using it.
card=refs(named('GoOnHolidayCard').read_typetree())
assert combine_events(card[1012]['data']['Events'],card[1020]['data']['Events'])==card[1021]['data']['Events']
date_type_event=set_event('holiday.ReturnDateDropdownSelectedOption.PropertyValue','holiday.ReturnDateType')
native_event=copy.deepcopy(serial(wr,1037)['Events'])
sd(button).update(Events=combine_events(date_type_event,native_event),Events_UxmlAttributeFlags=1,
                  OnlyAcceptsClickEvents=1,OnlyAcceptsClickEvents_UxmlAttributeFlags=1,
                  StopsEventPropagation=1,StopsEventPropagation_UxmlAttributeFlags=1)
dropdown_data=rr[dropmap[1014]]['data']
dropdown_data.update(SelectionEvents=date_type_event,SelectionEvents_UxmlAttributeFlags=1,
                     TriggerSelectionEventOnInit=0,TriggerSelectionEventOnInit_UxmlAttributeFlags=1,
                     HideOnSelectionChange=1,HideOnSelectionChange_UxmlAttributeFlags=1)

def decode(raw):
    b=bytes(raw); p=1; result=[]
    for _ in range(b[0]):
        n=struct.unpack_from('<I',b,p)[0]; p+=4; result.append(b[p:p+n]); p+=n
    assert p==len(b); return result
def encode(parts): return list(bytes([len(parts)])+b''.join(struct.pack('<I',len(p))+p for p in parts))
def path_arg(path): return string('SI.VisualScripting.GenericVisualArg`1[SI.Bindable.BindingPath]')+b'\x01'+string(path)
# Verified in the live native dropdown: Next week, Next month, Next match, Choose.
# Native initialization must select index 2 rather than preserving its built-in Next week default.
old_arguments=decode(dropdown_data['BindChoicesFunction']['m_inputs']['m_variable']['m_argumentBytes'])
assert len(old_arguments)==3 and struct.unpack('<i',old_arguments[-1][-4:])[0]==0
assert dropdown_data['BindChoicesFunction']['m_target']['m_guid']=='50902af85e1d1534cabaecf7660bda36'
old_arguments[-1]=old_arguments[-1][:-4]+struct.pack('<i',2)
dropdown_data['BindChoicesFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(old_arguments)

edit(visible,dimensions()+[P(131091,st.px(0)),P(131092,st.px(8))])
edit(root,dimensions(210)+[P(131083,st.en('column')),P(458768,st.en('visible'))])
edit(defaults,dimensions(height=100)+[P(131083,st.en('column')),P(458768,st.en('visible'))])
edit(body,dimensions(height=100)+[P(131083,st.en('column')),P(131102,st.en('relative')),P(458768,st.en('visible'))])
for node in [drop,enabled]:
    edit(node,dimensions()+[P(131105,st.pct(100)),P(131087,st.px(0)),P(131084,st.num(1)),P(131085,st.num(1))])
edit(drop,[P(131092,st.px(0)),P(131090,st.px(2))])
edit(button,dimensions(height=100)+[P(131105,st.pct(100)),P(262147,st.px(4)),P(262148,st.px(1)),
                                 P(131099,st.px(6)),P(131100,st.px(6)),P(65537,st.px(12))])
# The optional native date-picker control appears under the shortcut without changing header height.
edit(date,dimensions(210)+[P(131102,st.en('absolute')),P(131089,st.px(0)),P(131104,st.pct(100)),
                         P(131087,st.px(36)),P(458752,st.h(4,dict(zip(['r','g','b','a'],[struct.unpack('<f',struct.pack('<f',v))[0] for v in [0.91,0.91,0.91,1.0]])))),
                         P(262148,st.px(1)),P(262147,st.px(4))])
for old,new in date_map.items():
    if 'm_FullTypeName' in rr[new].get('data',{}):
        rr[new]['data']['m_Classes']=[x for x in rr[new]['data'].get('m_Classes',[]) if not x.startswith('margin-')]
for old,new in buttonmap.items():
    if rr[new].get('data',{}).get('m_FullTypeName')=='SI.Bindable.SIText':
        edit(new,[P(65537,st.px(12)),P(131096,st.px(0)),P(131094,{'m_ValueType':1,'valueIndex':3}),P(131087,st.pct(100)),P(65546,st.en('middle-center'))])

# Locate the native clock height. Variables must remain in a regular stylesheet:
# this game's InlineStyleAccess reaches ResolveVariable with a null variable context.
style_env=UnityPy.load(before[GAME/S]); source_style=None; clock_height=None
for ob in style_env.objects:
    if ob.type.name!='MonoBehaviour': continue
    sh=ob.read_typetree()
    for rule in sh.get('m_Rules',[]):
        if any(len(s['m_Selectors'])==1 and s['m_Selectors'][0]['m_Parts']==[{'m_Value':'navigation-primary-nav-calendar-wiget-calendar','m_Type':3}] for s in rule.get('m_ComplexSelectors',[])):
            for prop in rule['m_Properties']:
                if prop['m_Id']==131087: source_style=sh; clock_height=copy.deepcopy(prop)
assert clock_height is not None
for i in created:
    a=rr[i].get('data',{})
    if a.get('m_RuleIndex',-1)>=0:
        assert all(h['m_ValueType'] not in [8,10] for p in sheet['m_Rules'][a['m_RuleIndex']]['m_Properties'] for h in p['m_Values']), ('Variable in shortcut inline style',i)

# Native root/continue nodes and the entire original holiday dialog remain byte-for-byte equivalent.
for i,r in refs(original).items():
    if i==1042:
        expected=copy.deepcopy(r); expected['data']['m_Children'].insert(insert_at,{'rid':visible}); assert rr[i]==expected
    else: assert rr[i]==r, ('Existing navigation record modified',i)
validate_ui(doc,sheet)
nav.save_typetree(doc); oo[sheet_id].save_typetree(sheet)
world_output=env.file.save(packer='lz4')
saved={o.path_id:o for o in UnityPy.load(world_output).objects}
assert set(saved)==set(oo) and banned.isdisjoint(saved)
for i,h in old_hashes.items():
    if i in [nav.path_id,sheet_id]: assert saved[i].read_typetree()=={nav.path_id:doc,sheet_id:sheet}[i]
    else: assert sha(saved[i].get_raw_data())==h, ('Unrelated world asset changed',i)
validate_ui(saved[nav.path_id].read_typetree(),saved[sheet_id].read_typetree())

payloads={GAME/W:world_output,SKIN/W:world_output}
style_reports=[]
for folder in [GAME,SKIN]:
    en=UnityPy.load(before[folder/S]); objects={o.path_id:o for o in en.objects}
    hashes={i:sha(o.get_raw_data()) for i,o in objects.items()}; changes={}
    # AlwaysAppliedStyleSheet is the active default stylesheet, not an unrelated imported sheet.
    active=next(o for o in objects.values() if o.type.name=='MonoBehaviour' and o.peek_name()=='AlwaysAppliedStyleSheet')
    sh=active.read_typetree(); ss=Styles(sh)
    col=lambda s: dict(zip(['r','g','b','a'],[struct.unpack('<f',struct.pack('<f',int(s[i:i+2],16)/255))[0] for i in [0,2,4]]+[1.]))
    def add_rule(selectors,properties):
        idx=len(sh['m_Rules']);sh['m_Rules'].append({'m_ComplexSelectors':[selector(s,idx) for s in selectors], 'm_Properties':properties,'line':-1})
    base='.'+ROOT+' .fm27-holiday-date'
    height_props=[p for rule in sh['m_Rules'] for p in rule['m_Properties'] if p['m_Id']==131087 and any(
        len(s['m_Selectors'])==1 and s['m_Selectors'][0]['m_Parts']==[{'m_Value':'navigation-primary-nav-calendar-wiget-calendar','m_Type':3}]
        for s in rule.get('m_ComplexSelectors',[]))]
    assert height_props
    add_rule(['.'+ROOT],[copy.deepcopy(height_props[-1])])
    # Scope every new selector to the shortcut; keep row popup typography native.
    add_rule([base+' .buttons-dropdown-base-regular'],[
        ss.p(131105,ss.pct(100)),ss.p(131087,ss.pct(100)),ss.p(131096,ss.px(0)),
        ss.p(131094,{'m_ValueType':1,'valueIndex':3}),ss.p(262150,ss.px(0)),ss.p(262151,ss.px(0))])
    add_rule([base+' .si-dropdown__selection-field'],[
        ss.p(131087,ss.pct(100)),ss.p(131096,ss.px(0)),ss.p(131094,{'m_ValueType':1,'valueIndex':3}),
        ss.p(262150,ss.px(0)),ss.p(262151,ss.px(0)),ss.p(262147,ss.px(4)),ss.p(262148,ss.px(1)),
        ss.p(262146,ss.h(4,col('35C6E8'))),ss.p(458752,ss.h(4,col('E7E7E7'))),
        ss.p(131099,ss.px(6)),ss.p(131100,ss.px(6)),ss.p(65537,ss.px(12)),ss.p(65536,ss.h(4,col('000000')))])
    add_rule([base,base+' .sitext',base+' SIText',base+' TextElement'],[
        ss.p(65537,ss.px(12)),ss.p(65536,ss.h(4,col('000000'))),ss.p(65552,ss.en('nowrap')),
        ss.p(131096,ss.px(0)),ss.p(262150,ss.px(0))])
    add_rule([base+' .si-dropdown__selection-field:hover'],[ss.p(458752,ss.h(4,col('D8F3FA')))])
    add_rule([base+' .ui-concepts-chevron-down_small',base+' SIImage'],[ss.p(196610,ss.h(4,col('000000')))])
    add_rule(['.'+ROOT+' .fm27-holiday-confirm'],[ss.p(262146,ss.h(4,col('35C6E8'))),ss.p(65536,ss.h(4,col('FFFFFF')))])
    active.save_typetree(sh); changes[active.path_id]=sh
    raw=en.file.save(packer='lz4'); check={o.path_id:o for o in UnityPy.load(raw).objects}
    assert set(check)==set(objects)
    for i,o in check.items():
        if i in changes: assert o.read_typetree()==changes[i]
        else: assert sha(o.get_raw_data())==hashes[i]
    payloads[folder/S]=raw
    style_reports.append({'target':str(folder/S),'stylesheet':active.path_id,'added_scoped_rules':7})

# Validate the actual catalog type, owning bundle, container object, and dependency closure.
spec=importlib.util.spec_from_file_location('holiday_catalog',R/'catalog-binary-v35.py')
cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cache={W:oo}
def bundle(name):
    if name not in cache:
        e=UnityPy.load(str(GAME/name));cache[name]={o.path_id:o for o in e.objects}
    return cache[name]
def asset_guids(value):
    result=set()
    if isinstance(value,dict):
        for k,x in value.items():
            if k in ['m_guid','m_AssetGUID'] and isinstance(x,str) and re.fullmatch('[0-9a-f]{32}',x):result.add(x)
            else:result.update(asset_guids(x))
    elif isinstance(value,list):
        for x in value:result.update(asset_guids(x))
    return result
added_usings=[u for u in doc['m_Usings'] if u not in usings_before]
required=set(u['path'] for u in added_usings)
for i in created:required.update(asset_guids(rr[i]))
nav_meta=next(o.read_typetree() for o in oo.values() if o.type.name=='AssetBundle')
nav_guid=next(k for k,v in nav_meta['m_Container'] if v['asset']['m_PathID']==nav.path_id)
audits=[]
for folder in [GAME.parent,SKIN]:
    cp=folder/'catalog.bin'; raw=cp.read_bytes(); cat=cm.Catalog(raw)
    navloc=next(l for l in cat.locations(nav_guid) if cat.location(l)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
    navdeps=cat.location(navloc)['dependencies']; extra=[]; queue=list(required); seen=set(); audit=[]
    while queue:
        key=queue.pop()
        if key in seen:continue
        seen.add(key); locations=cat.locations(key);assert locations,('Missing catalog entry',key)
        loc=next(l for l in locations if cat.location(l)['provider'].endswith('.BundledAssetProvider'))
        v=cat.location(loc);assert v['internal']==key and v['dependencies'],(key,v)
        owner=cat.location(v['dependencies'][0])['internal'].replace('\\','/').split('/')[-1]
        objects=bundle(owner);meta=next(o.read_typetree() for o in objects.values() if o.type.name=='AssetBundle')
        entries=[x for k,x in meta['m_Container'] if k==key]
        matches=[]
        for entry in entries:
            assert entry['asset']['m_FileID']==0
            candidate=objects[entry['asset']['m_PathID']];candidate_tree=candidate.read_typetree()
            kind=('UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in candidate_tree else
                  'SI.VisualScripting.VisualFunction' if 'm_nodes' in candidate_tree else
                  'UnityEngine.UIElements.StyleSheet' if 'm_Rules' in candidate_tree else None)
            if kind==v['type'][1] or kind is None and len(entries)==1:matches.append((candidate,candidate_tree))
        assert len(matches)==1,(key,owner,v['type'],len(matches))
        ob,tree=matches[0]
        expected_type='UnityEngine.UIElements.VisualTreeAsset' if 'inlineSheet' in tree else 'SI.VisualScripting.VisualFunction' if 'm_nodes' in tree else None
        if expected_type:assert v['type'][1]==expected_type,(key,v['type'],expected_type)
        assert ob.path_id not in banned
        audit.append({'guid':key,'name':ob.peek_name(),'type':v['type'][1],'bundle':owner,'path_id':str(ob.path_id)})
        extra.extend(v['dependencies'])
        if 'inlineSheet' in tree:
            queue.extend(u['path'] for u in tree.get('m_Usings',[]) if u.get('path'))
            queue.extend(asset_guids(tree))
    deps=list(dict.fromkeys(navdeps+extra));assert cat.location(deps[0])['internal'].replace('\\','/').endswith('/'+W)
    if deps!=navdeps:
        dep_ptr=cat.append(b''.join(struct.pack('<I',x) for x in deps),True)
        struct.pack_into('<I',cat.data,navloc+12,dep_ptr)
        # Addressables uses this hash as a cache key for the dependency list.
        from zlib import crc32
        dep_hash=crc32(b''.join(struct.pack('<I',x) for x in deps)) & 0xffffffff
        struct.pack_into('<I',cat.data,navloc+16,dep_hash)
        payloads[cp]=bytes(cat.data);payloads[folder/'catalog.hash']=hashlib.md5(bytes(cat.data)).hexdigest().encode('ascii')
        for n in ['catalog.bin','catalog.hash']:
            p=folder/n;before[p]=p.read_bytes();protected.pop(p,None)
    audited=cm.Catalog(payloads.get(cp,raw));assert audited.location(navloc)['dependencies']==deps
    prior=cm.Catalog(raw);assert audited.keys()==prior.keys()
    all_locations={l for _,ptr in prior.keys() for (l,) in prior.array(ptr,'I')}
    for location in all_locations:
        old_fields=prior.unpack(location,'7I');new_fields=audited.unpack(location,'7I')
        if location==navloc:
            assert all(old_fields[i]==new_fields[i] for i in [0,1,2,5,6])
        else:assert new_fields==old_fields,('Unrelated catalog registration changed',location)
    audits.append({'catalog':str(cp),'navigation_guid':nav_guid,'added_dependency_count':len(deps)-len(navdeps),'resources':audit})

# No images are imported or repacked; verify the permanent exclusions in the current background files.
for n in ['ui-backgrounds_assets_.bundle','ui-backgrounds_assets_common.bundle']:
    for folder in [GAME,SKIN]:
        objects={o.path_id:o for o in UnityPy.load(str(folder/n)).objects};assert banned.isdisjoint(objects)
        meta=next(o.read_typetree() for o in objects.values() if o.type.name=='AssetBundle')
        assert all(o.peek_name().lower() not in banned_names for o in objects.values() if o.type.name=='Texture2D')
        assert all(k.lower() not in banned_names and v['asset']['m_PathID'] not in banned for k,v in meta['m_Container'])
        assert all(p['m_PathID'] not in banned for p in meta['m_PreloadTable'])
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-6))).strftime('%Y%m%d-%H%M%S')
out=R/('header-holiday-shortcut-'+stamp);out.mkdir();(out/'templates').mkdir()
for name,data in [('PrimaryNavigationBar',doc),('PrimaryNavigationBar-inlineStyle',sheet)]:
    (out/'templates'/(name+'.json')).write_text(json.dumps(data,ensure_ascii=False,indent=2),'utf8')
tx=[]
for p,data in payloads.items():
    tag='game' if p.parent in [GAME,GAME.parent] else 'skin'
    source=out/tag/p.name; backup=out/('backup-'+tag)/p.name
    source.parent.mkdir(exist_ok=True);backup.parent.mkdir(exist_ok=True)
    source.write_bytes(data);backup.write_bytes(before[p])
    tx.append({'target':str(p),'source':str(source),'backup':str(backup),'before':sha(before[p]),'after':sha(data)})
manifest={'installed':False,'runtime_verified':False,'protected_sha256':{str(p):h for p,h in protected.items()},
          'layout':{'width':210,'height':'--interaction-global-height-lg','rows':['return date','confirm holiday']},
          'default_selection':'native index 2: Next match (verified native option order)',
          'selection_initialization':'Next match when native choices initialize; manual selection remains available',
          'initialization_triggers_holiday':False,
          'crash_fix':'Keep the clock height variable in the regular stylesheet; no variable/function handles in added inline styles.',
          'no_shortcut_inline_style_variables':True,
          'confirmation_event_order':['set ReturnDateType from selected dropdown property','native holiday confirmation'],
          'original_continue_and_holiday_dialog_preserved':True,'no_texture_or_function_objects_added':True,
          'reserved_ids_absent':True,'created_navigation_records':created,'style_changes':style_reports,'catalog_audits':audits,
          'runtime_checks_pending':['next match default and live date','custom date picker','page/manager switching',
                                    'disabled states','direct holiday and return','resolution and UI scaling']}
(out/'manifest.json').write_text(json.dumps(manifest,ensure_ascii=False,indent=2),'utf8')
(out/'transaction.json').write_text(json.dumps(tx,ensure_ascii=False,indent=2),'utf8')
python=Path(sys.executable)
for name,flag in [('install',''),('restore',' --restore')]:
    (out/(name+'.ps1')).write_text("$ErrorActionPreference = 'Stop'\n& '"+str(python)+"' '"+str(R/'install-independent-resource-patch.py')+"' '"+str(out)+"'"+flag+"\nif ($LASTEXITCODE -ne 0) { throw 'Patch operation failed.' }\n",'utf-8-sig')
(out/'使用说明.md').write_text('右上角度假快捷区\n\n在时间与继续按钮之间添加日期下拉框和确认度假按钮。原度假弹窗保留。默认选择经游戏内确认的第三项“下一场比赛”（索引2），允许手动修改。点击确认先应用当前日期类型，再执行原生度假事件。\n\n安装或回退前正常退出游戏。执行 install.ps1 安装，restore.ps1 回退。\n\n静态校验完成，实际游戏操作和分辨率适配仍需游戏内验证。\n','utf8')
print(json.dumps({'prepared':True,'output':str(out),'changed_files':len(tx),'added_navigation_records':len(created),
                  'catalog_resources_verified':[len(a['resources']) for a in audits],
                  'catalog_dependencies_added':[a['added_dependency_count'] for a in audits],'runtime_verified':False},ensure_ascii=False))
