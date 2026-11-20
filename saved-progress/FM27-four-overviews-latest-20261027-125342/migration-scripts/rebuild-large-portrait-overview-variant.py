from pathlib import Path
import ast, copy, json, struct, zlib

source = Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix = source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-', 'rebuild-large-portrait-overview-variant-')
exec(compile(prefix, 'backup-and-serialization-helpers', 'exec'))
L = 'ui-tileslayouts_assets_all.bundle'
CACHE = Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
for p in [GAME/L, SKIN/L] + ([CACHE] if CACHE.exists() else []):
    before[p] = p.read_bytes()
    tag = 'backup-cache' if p == CACHE else 'backup-game' if p.parent == GAME else 'backup-skin'
    folder = OUT/tag
    folder.mkdir(exist_ok=True)
    (folder/p.name).write_bytes(before[p])
for p in [GAME/L, SKIN/L]: protected.pop(p)
for p in [GAME/G, SKIN/G]: protected[p] = sha(p.read_bytes())
assert before[GAME/L] == before[SKIN/L]
env[L] = UnityPy.load(before[GAME/L])
objs[L] = {o.path_id:o for o in env[L].objects}
hashes[L] = {i:sha(o.get_raw_data()) for i,o in objs[L].items()}
changed[L] = {}

FULL = -930000000001001
SECOND = -930000000001003
FIRST_DESCRIPTION = -930000000001004
SECOND_DESCRIPTION = -930000000001005
FULL_GUID = '1f6ebbeeaeba50cbbb57ef2d123b47dc'
SECOND_GUID = '76cd79feada45acebc482721c1b688da'
titles = {'OverviewFCVariantTitle':'中间版FC卡+隐藏', 'OverviewPortraitVariantTitle':'中间版大头像+无隐藏'}

def save(n, pid, doc, sid=None, styles=None):
    if sid is not None:
        validate_ui(doc, styles)
        objs[n][sid].save_typetree(styles)
        changed[n][sid] = styles
    objs[n][pid].save_typetree(doc)
    changed[n][pid] = doc

def serial(refs0, i):
    return refs0[refs0[i]['data']['m_SerializedData']['rid']]

# Retain the registered GUID and path IDs so installed/default/saved references stay valid.
full = objs[W][FULL].read_typetree()
old_second = objs[W][SECOND].read_typetree()
doc = copy.deepcopy(full)
doc['m_Name'] = old_second['m_Name']
doc['inlineSheet'] = copy.deepcopy(old_second['inlineSheet'])
sid = doc['inlineSheet']['m_PathID']
sheet = copy.deepcopy(objs[W][full['inlineSheet']['m_PathID']].read_typetree())
sheet['m_Name'] = objs[W][sid].read_typetree()['m_Name']
rr = refs(doc)
removed = set()

def gather(i):
    if i not in rr or i in removed or i == -2: return
    removed.add(i)
    def walk(v):
        if isinstance(v,dict):
            if set(v) == {'rid'}:
                gather(v['rid'])
            else:
                for k,x in v.items():
                    if k != 'm_Parent': walk(x)
        elif isinstance(v,list):
            for x in v: walk(x)
    walk(rr[i].get('data',{}))

def remove_tree(i):
    parent = rr[i]['data']['m_Parent']['rid']
    rr[parent]['data']['m_Children'].remove({'rid':i})
    gather(i)

for i in [1301,1819,1863,named('RightHiddenAttributesPanel')]:
    remove_tree(i)
doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in removed]
rr = refs(doc)
assert rr[1299]['data']['m_Children'] == [{'rid':1285},{'rid':1172},{'rid':1897}]

# A 226px photo and the original foot footer fit the existing 250px banner.
override(rr[1293]['data'], [prop(131087,px(250)),prop(131096,px(250)),prop(131094,px(250)),
    prop(262150,px(0)),prop(262151,px(0)),prop(131099,px(0)),prop(131100,px(0)),
    prop(131101,px(0)),prop(131098,px(0)),prop(131073,en('center'))])
override(rr[1299]['data'], [prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(250)),
    prop(131096,px(250)),prop(131094,px(250)),prop(131083,en('column')),
    prop(131073,en('center')),prop(131088,en('flex-start'))])
override(rr[1285]['data'], [prop(131102,en('relative')),prop(131089,auto),prop(131103,auto),
    prop(131104,auto),prop(131080,auto),prop(131105,px(226)),prop(131087,px(226)),
    prop(131095,pct(100)),prop(131097,px(0)),prop(131074,en('center')),prop(131093,px(2))])
override(rr[1172]['data'], [prop(131102,en('absolute')),prop(131089,auto),prop(131103,px(4)),
    prop(131104,px(4)),prop(131080,auto),prop(131105,px(180)),prop(131095,pct(100)),
    prop(131087,px(20))])
override(rr[1897]['data'], [prop(131102,en('relative')),prop(131089,auto),prop(131103,auto),
    prop(131104,auto),prop(131080,auto),prop(131074,en('center')),prop(131105,px(174)),
    prop(131087,px(14)),prop(131093,px(6))])
override(rr[named('OverviewProsConsTacticsEqualRow')]['data'], [prop(131093,px(0))])
frame = named('FullOverviewFrame')
sd(frame)['name'] = 'LargePortraitNoHiddenOverviewFrame'
doc['m_ContentHash'] = struct.unpack('<i',struct.pack('<I',zlib.crc32(b'large-portrait-no-hidden-v1')))[0]
source_refs = refs(full)
preserved_roots = [1287,1177,1899,1903,1905]
for i in preserved_roots:
    assert serial(rr,i) == serial(source_refs,i), ('native photo/status/foot binding altered',i)
assert 5852 not in rr and 1301 not in rr and 1819 not in rr and 1863 not in rr
assert sd(named('OverviewTopSeasonTwelveStats')) == serial(source_refs,6304)['data']
assert rr[1009] == source_refs[1009]
save(W,SECOND,doc,sid,sheet)

# Give the native grid selector two explicit title strings through its own binding scope.
pid = 7857044477279960178
page = objs[W][pid].read_typetree()
pr = refs(page)
variables = next(r['data'] for r in pr.values() if r.get('type',{}).get('class') == 'BindingVariablesComponent/UxmlSerializedData')
assert not any(v['m_name'] in titles for v in variables['ValueVariables'])
for key,title in titles.items():
    variables['ValueVariables'].append({'m_name':key,'m_scopeValue':{'m_serializedData':'String|'+title+'|'}})
variables['ValueVariables_UxmlAttributeFlags'] = 1
for p in pr[1006]['data']['m_Properties']:
    if p['name'] == 'value-vars':
        p['value'] += ''.join(',{'+key+'}{String|'+title+'|}' for key,title in titles.items())
grid = next(r['data'] for r in pr.values() if r.get('data',{}).get('Bindings',{}).get('m_gridCompositionSet',{}).get('m_PathID') == 1615455816372668659)
for key in titles:
    grid['Bindings']['m_nameBindings'].append({'name':key,'path':{'m_path':key},'method':0})
    for ident in ['PlayerOverviewFull','PlayerOverviewSimple']:
        grid['Bindings']['m_gridElementBindingData'].append({
            'DescriptionAndMapping':{'DescriptionName':ident,'MappingName':key,'MappingReferenceID':0},
            'BindingPath':{'m_path':''},'IsDynamic':0})
validate_ui(page,objs[W][page['inlineSheet']['m_PathID']].read_typetree())
save(W,pid,page)
for pid,key in [(FIRST_DESCRIPTION,'OverviewFCVariantTitle'),(SECOND_DESCRIPTION,'OverviewPortraitVariantTitle')]:
    desc = objs[L][pid].read_typetree()
    desc['m_translationType'] = 2
    desc['m_directTitlePath'] = {'m_path':key}
    save(L,pid,desc)

# Mirror the full page's preload list, replacing only the second page and style pointers.
metaobj = next(o for o in objs[W].values() if o.type.name == 'AssetBundle')
meta = metaobj.read_typetree()
first_entry = next(v for k,v in meta['m_Container'] if k == FULL_GUID and v['asset']['m_PathID'] == FULL)
second_entry = next(v for k,v in meta['m_Container'] if k == SECOND_GUID and v['asset']['m_PathID'] == SECOND)
preload = copy.deepcopy(meta['m_PreloadTable'][first_entry['preloadIndex']:first_entry['preloadIndex']+first_entry['preloadSize']])
for ptr in preload:
    if ptr['m_FileID'] == 0:
        if ptr['m_PathID'] == FULL: ptr['m_PathID'] = SECOND
        elif ptr['m_PathID'] == full['inlineSheet']['m_PathID']: ptr['m_PathID'] = sid
second_entry['preloadIndex'] = len(meta['m_PreloadTable'])
second_entry['preloadSize'] = len(preload)
meta['m_PreloadTable'].extend(preload)
save(W,metaobj.path_id,meta)

# Existing saved selections keep their identity; rebuild only the active overview config.
cacheout = None
if CACHE in before:
    cache = json.loads(before[CACHE])
    top = next(c for c in cache['m_gridComponents'] if c['m_location']['y']==0)
    current = top['m_gridElementConfigs'][0]['AssetRef']['m_AssetGUID']
    assert current in [FULL_GUID,SECOND_GUID], ('unknown saved overview',current)
    is_second = current == SECOND_GUID
    top['m_elementID'] = 'PlayerOverviewSimple' if is_second else 'PlayerOverviewFull'
    top['m_configDescriptionKeys'] = [top['m_elementID']]
    top['m_configDescriptions'] = [{'instanceID':0}]
    assert len(top['m_gridElementConfigs']) == 1
    top['m_gridElementConfigs'][0]['Description'] = {'instanceID':0}
    cacheout = json.dumps(cache,ensure_ascii=False,separators=(',',':')).encode('utf8')
    (OUT/'saved-layout.json').write_bytes(cacheout)

assert sha(objs[W][FULL].get_raw_data()) == hashes[W][FULL]
outputs = {n:env[n].file.save(packer='lz4') for n in [W,L]}
for n,b in outputs.items():
    check = {o.path_id:o for o in UnityPy.load(b).objects}
    assert set(check) == set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]: assert sha(check[i].get_raw_data()) == h, ('unrelated object altered',n,i)
    for i,d in changed[n].items(): assert check[i].read_typetree() == d, ('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
report = {'installed':False,'runtime_verified':False,'variant_titles':list(titles.values()),
    'second_rebuilt_from_current_full':True,'first_page_byte_identical':True,
    'photo_size':226,'banner_height':250,'status':'upper right','feet':'below portrait',
    'hidden_panel_removed':True,'native_bindings_retained':True,'existing_guid_and_path_ids_reused':True,
    'removed_local_reference_count':len(removed),'bottom_layout_unchanged':True,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore = ['$ErrorActionPreference = "Stop"']
for p in before:
    tag = 'backup-cache' if p == CACHE else 'backup-game' if p.parent == GAME else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items(): assert p.read_bytes() == b
for p,h in protected.items(): assert sha(p.read_bytes()) == h
proc = subprocess.run(['powershell','-NoProfile','-Command',
    'Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}))
    sys.exit(0)
try:
    for n,b in outputs.items():
        for folder in [GAME,SKIN]:
            (folder/n).write_bytes(b)
            assert (folder/n).read_bytes() == b
    if cacheout is not None:
        CACHE.write_bytes(cacheout)
        assert CACHE.read_bytes() == cacheout
    for p,h in protected.items(): assert sha(p.read_bytes()) == h
except BaseException:
    for p,b in before.items(): p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'photo_size':226,'removed_refs':len(removed),
    'changed_objects':{n:list(c) for n,c in changed.items()}}))
