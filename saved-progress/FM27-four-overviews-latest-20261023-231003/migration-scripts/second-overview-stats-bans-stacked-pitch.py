from pathlib import Path
import ast, copy, json, struct, uuid, zlib, importlib.util

source = Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix = source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-', 'second-overview-stats-bans-stacked-pitch-')
exec(compile(prefix, 'backup-and-serialization-helpers', 'exec'))
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:
    before[p] = p.read_bytes()
    folder = OUT/('backup-skin' if p.parent == SKIN else 'backup-game')
    (folder/p.name).write_bytes(before[p])
    protected.pop(p)
assert before[GAME.parent/'catalog.bin'] == before[SKIN/'catalog.bin']

SELECTOR_SOURCE = -940000000005000
SELECTOR_SOURCE_GUID = '1d1704ae44cb5b7ba38367bc28362460'
SELECTOR_PID, SELECTOR_SID = -940000000008000, -940000000008001
SELECTOR_GUID = uuid.uuid5(uuid.NAMESPACE_URL,'fm27-large-portrait-only-stacked-landscape-pitch-roles-comparison-2to3').hex
STATS_SOURCE = -940000000007000
STATS_PID, STATS_SID = -940000000008100, -940000000008101
STATS_GUID = uuid.uuid5(uuid.NAMESPACE_URL,'fm27-large-portrait-only-right-middle-twelve-stats-174px').hex
SECOND = -930000000001003
new_assets = []

def serial(rr0,i): return rr0[rr0[i]['data']['m_SerializedData']['rid']]

def save(n,pid,doc,sid=None,styles=None):
    if sid is not None:
        validate_ui(doc,styles)
        objs[n][sid].save_typetree(styles)
        changed[n][sid] = styles
    objs[n][pid].save_typetree(doc)
    changed[n][pid] = doc

def add_object(n,source_pid,pid,data):
    assert pid not in objs[n]
    obj = copy.copy(objs[n][source_pid])
    obj.path_id = pid
    obj.assets_file.objects[pid] = obj
    objs[n][pid] = obj
    obj.save_typetree(data)
    changed[n][pid] = data

def clone_asset(n,source_pid,pid,sid,guid,label):
    doc = copy.deepcopy(objs[n][source_pid].read_typetree())
    old_sid = doc['inlineSheet']['m_PathID']
    styles = copy.deepcopy(objs[n][old_sid].read_typetree())
    doc['inlineSheet'] = {'m_FileID':0,'m_PathID':sid}
    doc['m_Name'] = label
    styles['m_Name'] = label+'_Style'
    doc['m_ContentHash'] = struct.unpack('<i',struct.pack('<I',zlib.crc32(guid.encode())))[0]
    new_assets.append((n,source_pid,old_sid,pid,sid,guid,doc))
    return doc,styles,old_sid

def move(i,parent):
    a = rr[i]['data']
    rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i})
    a['m_Parent'] = {'rid':parent}
    rr[parent]['data']['m_Children'].append({'rid':i})

# The first overview continues using its original selector. Only the second gets this copy.
doc,sheet,original_sid = clone_asset(G,SELECTOR_SOURCE,SELECTOR_PID,SELECTOR_SID,SELECTOR_GUID,
    'LargePortraitOverviewPitchAboveRolesAndComparison')
rr = refs(doc)
original = copy.deepcopy(rr)
next_rid = max(rr)+1
next_id = max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
assert rr[1007]['data']['m_Children'] == [{'rid':2000},{'rid':2002}]
assert rr[2002]['data']['m_Children'] == [{'rid':2010},{'rid':2006}]
rr[2000]['data']['m_Children'].remove({'rid':2008})
remove_rids = {2008,rr[2008]['data']['m_SerializedData']['rid']}
doc['references']['RefIds'] = [r for r in doc['references']['RefIds'] if r['rid'] not in remove_rids]
for i in remove_rids: rr.pop(i)
doc['m_ContentContainerId'] = 0
override(rr[1007]['data'],[prop(131083,en('column')),prop(131073,en('stretch'))])
for i,grow in [(2000,2),(2002,3)]:
    override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
        prop(131087,px(0)),prop(131096,px(0)),prop(131094,none),prop(131082,px(0)),
        prop(131084,num(grow)),prop(131085,num(1)),prop(131092,px(0)),
        prop(131090,px(8 if i==2000 else 0)),prop(131073,en('stretch'))])
override(rr[2002]['data'],[prop(131083,en('row'))])
for i in [2010,2006]:
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),
        prop(131087,pct(100)),prop(131096,px(0)),prop(131094,none),prop(131082,px(0)),
        prop(131084,num(1)),prop(131085,num(1)),prop(131090,px(0)),prop(131093,px(0)),
        prop(131092,px(8 if i==2010 else 0))])
# FitInParent is the shipped SIAspectRatioFitterCore.Mode value 2 (verified in metadata).
# Both background and interactive panel live inside that same fitted rectangle.
native = objs[G][-9211596620732837621].read_typetree()
nr = refs(native)
fitter = add_pair(nr[1145],serial(nr,1145),1010,'LargePortraitLandscapePitchAspectRatio')
sd(fitter).update(AspectMode=2,AspectMode_UxmlAttributeFlags=1,
    AspectRatio=struct.unpack('<f',struct.pack('<f',200/140))[0],AspectRatio_UxmlAttributeFlags=1)
for i in [1022,1023]: move(i,fitter)
override(rr[1010]['data'],[prop(131101,px(0)),prop(131087,px(0)),prop(131096,px(0)),
    prop(131094,none),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),
    prop(131090,px(4)),prop(131073,en('center')),prop(131088,en('center'))])
override(rr[fitter]['data'],[prop(131102,en('relative')),prop(131105,pct(100)),
    prop(131087,pct(100)),prop(131097,px(0)),prop(131096,px(0)),prop(131084,num(0)),
    prop(131085,num(0)),prop(131074,en('center')),prop(262150,px(0)),prop(262151,px(0))])
changed_scroll_ids = set()
for i,r in list(rr.items()):
    a = r.get('data',{})
    if a.get('m_FullTypeName') in ['SI.Bindable.StreamedTable','SI.Bindable.StreamedObjectList']:
        for key,value in [('ScrollViewMode',0),('HorizontalScrollerVisibility',2),('VerticalScrollerVisibility',0)]:
            sd(i)[key] = value
            sd(i)[key+'_UxmlAttributeFlags'] = 1
        changed_scroll_ids.add(a['m_SerializedData']['rid'])
for i,r in original.items():
    if i in remove_rids or i in changed_scroll_ids: continue
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i] == r, ('selector binding changed',i)
assert rr[2000]['data']['m_Children'] == [{'rid':1009},{'rid':1010},{'rid':1011}]
assert rr[2002]['data']['m_Children'] == [{'rid':2010},{'rid':2006}]
validate_ui(doc,sheet)
add_object(G,original_sid,SELECTOR_SID,sheet)
add_object(G,SELECTOR_SOURCE,SELECTOR_PID,doc)

# Private copy of the working league-aware statistics component; formatters and bindings stay intact.
doc,sheet,original_sid = clone_asset(W,STATS_SOURCE,STATS_PID,STATS_SID,STATS_GUID,
    'LargePortraitOverviewRightMiddleTwelveSeasonStats')
rr = refs(doc)
original = copy.deepcopy(rr)
for i in [1041,named('SeasonStatsIsGoalkeeperSwitch'),named('SeasonStatsOutfielderPanel'),named('SeasonStatsGoalkeeperPanel')]:
    override(rr[i]['data'],[prop(131105,pct(100)),prop(131087,px(174)),prop(131096,px(174)),
        prop(131094,px(174)),prop(131084,num(0)),prop(131085,num(0))])
for prefix in ['SeasonStatsRow','GoalkeeperStatsRow']:
    for j in range(1,5):
        i = named(prefix+str(j))
        override(rr[i]['data'],[prop(131087,px(42)),prop(131096,px(42)),prop(131094,px(42)),
            prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131090,px(2 if j<4 else 0))])
for i,r in rr.items():
    if 'm_Parent' not in r.get('data',{}): continue
    name = sd(i).get('name','')
    if name.startswith(('SeasonStatTitle_','GoalkeeperStatTitle_')):
        override(rr[i]['data'],[prop(65537,px(10)),prop(131087,px(18)),prop(131096,px(18)),
            prop(131094,px(18)),prop(65552,en('normal'))])
    elif name.startswith(('SeasonStatValue_','GoalkeeperStatValue_')):
        override(rr[i]['data'],[prop(65537,px(14)),prop(131087,px(20)),prop(131096,px(20)),prop(131094,px(20))])
for i,r in original.items():
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i] == r, ('native statistics binding changed',i)
assert 4*42+3*2 == 174
validate_ui(doc,sheet)
add_object(W,original_sid,STATS_SID,sheet)
add_object(W,STATS_SOURCE,STATS_PID,doc)

# Relocate the existing instances without rebuilding their player/team data scopes.
doc = objs[W][SECOND].read_typetree()
rr = refs(doc)
original = copy.deepcopy(rr)
sid = doc['inlineSheet']['m_PathID']
sheet = objs[W][sid].read_typetree()
stats = named('OverviewTopSeasonTwelveStats')
bans = named('OverviewPitchLowerBansScroll')
lower = named('OverviewProsConsTacticsEqualRow')
status = named('OverviewTopRightStatusPanel')
assert rr[bans]['data']['m_Parent']['rid'] == 1007
move(stats,1011)
rr[1011]['data']['m_Children'] = [{'rid':stats},{'rid':lower}]
move(bans,status)
override(rr[stats]['data'],[prop(131102,en('relative')),prop(131089,auto),prop(131103,auto),
    prop(131104,auto),prop(131080,auto),prop(131105,pct(100)),prop(131097,px(0)),
    prop(131095,pct(100)),prop(131087,px(174)),prop(131096,px(174)),prop(131094,px(174)),
    prop(131084,num(0)),prop(131085,num(0)),prop(131074,en('stretch'))])
override(rr[lower]['data'],[prop(131093,px(8))])
override(rr[bans]['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131103,px(0)),
    prop(131104,px(48)),prop(131080,px(0)),prop(131105,auto),prop(131087,auto),
    prop(131096,px(0)),prop(131094,none),prop(131084,num(0)),prop(131085,num(1)),prop(131082,auto)])
for using in doc['m_Usings']:
    if using['alias'] == 'role_selector-large':
        assert using['path'] == SELECTOR_SOURCE_GUID
        using['path'] = SELECTOR_GUID
        using['asset'] = {'m_FileID':0,'m_PathID':0}
    elif using['alias'] == rr[stats]['data']['m_TemplateAlias']:
        STATS_SOURCE_GUID = using['path']
        using['path'] = STATS_GUID
        using['asset'] = {'m_FileID':0,'m_PathID':0}
for i,r in original.items():
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i] == r, ('second overview binding changed',i)
assert rr[1007]['data']['m_Children'] == []
assert serial(rr,1285) == serial(original,1285)
assert serial(rr,1897) == serial(original,1897)
save(W,SECOND,doc,sid,sheet)

# Register each isolated asset under the same owner bundle as its source, preserving preload order.
for n,source_pid,source_sid,pid,new_sid,key,asset_doc in new_assets:
    ab = next(o for o in objs[n].values() if o.type.name == 'AssetBundle')
    meta = ab.read_typetree()
    # There is one new asset per bundle, so the source metadata is still untouched here.
    source_entry = next(v for k,v in meta['m_Container'] if v['asset']['m_PathID'] == source_pid)
    span = copy.deepcopy(meta['m_PreloadTable'][source_entry['preloadIndex']:source_entry['preloadIndex']+source_entry['preloadSize']])
    for ptr in span:
        if ptr['m_FileID'] == 0:
            if ptr['m_PathID'] == source_pid: ptr['m_PathID'] = pid
            elif ptr['m_PathID'] == source_sid: ptr['m_PathID'] = new_sid
    for ptr in [copy.deepcopy(asset_doc['m_Script']),{'m_FileID':0,'m_PathID':new_sid},{'m_FileID':0,'m_PathID':pid}]:
        if ptr not in span: span.append(ptr)
    assert not any(k == key for k,v in meta['m_Container'])
    meta['m_Container'].append((key,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':pid}}))
    meta['m_PreloadTable'].extend(span)
    meta['m_Container'].sort(key=lambda kv:kv[0])
    save(n,ab.path_id,meta)

spec = importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py')
cm = importlib.util.module_from_spec(spec)
spec.loader.exec_module(cm)
cat = cm.Catalog(before[GAME.parent/'catalog.bin'])
for key,source_key,label,bundle in [(SELECTOR_GUID,SELECTOR_SOURCE_GUID,'GlobalVisualTreeAssetPreload',G),
        (STATS_GUID,STATS_SOURCE_GUID,'GameWorldVisualTreeAssetPreload',W)]:
    loc = next(x for x in cat.locations(source_key) if cat.location(x)['type'][1].endswith('VisualTreeAsset'))
    cat = cm.Catalog(cat.add_key_location(key,loc,loc))
    newloc = cat.locations(key)[0]
    assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(bundle)
    idx = next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k) == label)
    ko,ls = cat.key_records[idx]
    locations = [x[0] for x in cat.array(ls,'I')]+[newloc]
    newset = cat.append(b''.join(struct.pack('<I',x) for x in locations),True)
    records = list(cat.key_records)
    records[idx] = (ko,newset)
    table = cat.append(b''.join(struct.pack('<2I',*x) for x in records),True)
    struct.pack_into('<I',cat.data,8,table)
    cat = cm.Catalog(bytes(cat.data))
catout = bytes(cat.data)
hashout = hashlib.md5(catout).hexdigest().encode('ascii')

outputs = {n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check = {o.path_id:o for o in UnityPy.load(b).objects}
    assert set(check) == set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]: assert sha(check[i].get_raw_data()) == h, ('unrelated asset altered',n,i)
    for i,d in changed[n].items(): assert check[i].read_typetree() == d, ('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout)
(OUT/'catalog.hash').write_bytes(hashout)
report = {'installed':False,'runtime_verified':False,'second_only':True,'first_page_and_shared_components_unchanged':True,
    'stats':{'position':'right-middle above pros cons tactics','title_size':10,'value_size':14,'row_height':42,'row_gap':2,'height':174,'bottom_gap':8,'native_bindings_unchanged':True},
    'bans':'under top fitness circles, original scrolling content',
    'selector':{'top_bottom_ratio':[2,3],'bottom_left_right_ratio':[1,1],'gaps':8,'pitch_aspect_ratio':[200,140],'aspect_mode':'native FitInParent 2','native_events_unchanged':True},
    'new_selector_guid':SELECTOR_GUID,'new_stats_guid':STATS_GUID,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore = ['$ErrorActionPreference = "Stop"']
for p in before:
    tag = 'backup-skin' if p.parent == SKIN else 'backup-game'
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
    for p,b in [(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout)]:
        p.write_bytes(b)
        assert p.read_bytes() == b
    for p,h in protected.items(): assert sha(p.read_bytes()) == h
except BaseException:
    for p,b in before.items(): p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'selector_guid':SELECTOR_GUID,'stats_guid':STATS_GUID,
    'changed_objects':{n:list(x) for n,x in changed.items()}}))
