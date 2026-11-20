from pathlib import Path
import ast, copy, json, struct

source = Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix = source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-', 'align-statistics-conditional-pros-balanced-bottom-')
exec(compile(prefix, 'backup-and-serialization-helpers', 'exec'))
L = 'ui-tileslayouts_assets_all.bundle'
CACHE = Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
extra = [GAME/L, SKIN/L] + ([CACHE] if CACHE.exists() else [])
for p in extra:
    before[p] = p.read_bytes()
    tag = 'backup-cache' if p == CACHE else 'backup-game' if p.parent == GAME else 'backup-skin'
    folder = OUT/tag
    folder.mkdir(exist_ok=True)
    (folder/p.name).write_bytes(before[p])
for p in [GAME/L, SKIN/L]:
    protected.pop(p)
assert before[GAME/L] == before[SKIN/L]
env[L] = UnityPy.load(before[GAME/L])
objs[L] = {o.path_id:o for o in env[L].objects}
hashes[L] = {i:sha(o.get_raw_data()) for i,o in objs[L].items()}
changed[L] = {}

def save(n, pid, doc, sid, sheet):
    validate_ui(doc, sheet)
    objs[n][pid].save_typetree(doc)
    objs[n][sid].save_typetree(sheet)
    changed[n][pid] = doc
    changed[n][sid] = sheet

def serial(rr0, i):
    return rr0[rr0[i]['data']['m_SerializedData']['rid']]

# Reuse SIVisible's shipped null-safe list predicate, separately for pros and cons.
native = objs[W][-9220808338929290082].read_typetree()
nr = refs(native)
visible_sd = next(r for r in nr.values() if r.get('data', {}).get('name') == 'has-items-state')
assert visible_sd['data']['Binding']['m_visualFunction']['m_target']['m_guid'] == 'fb85a893388896b458c4be0009043d13'
old_path = b'comp.SquadRewards.SquadRewardsList'

def list_binding(path):
    binding = copy.deepcopy(visible_sd['data']['Binding'])
    raw = bytes(binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
    assert raw[0] == 3
    chunks = []
    pos = 1
    for _ in range(3):
        size = struct.unpack_from('<I', raw, pos)[0]
        pos += 4
        chunks.append(raw[pos:pos+size])
        pos += size
    assert pos == len(raw)
    assert chunks[-1].endswith(bytes([len(old_path)]) + old_path)
    new_path = path.encode('utf8')
    chunks[-1] = chunks[-1][:-len(old_path)-1] + bytes([len(new_path)]) + new_path
    result = bytes([3]) + b''.join(struct.pack('<I', len(c)) + c for c in chunks)
    binding['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'] = list(result)
    assert new_path in result and old_path not in result
    return binding

pid = -940000000006002
doc = objs[G][pid].read_typetree()
rr = refs(doc)
old = copy.deepcopy(rr)
sid = doc['inlineSheet']['m_PathID']
sheet = objs[G][sid].read_typetree()
for i, key in [(1004, 'ProsList'), (1005, 'ConsList')]:
    srid = rr[i]['data']['m_SerializedData']['rid']
    replacement = copy.deepcopy(visible_sd)
    replacement['rid'] = srid
    replacement['data'].update(uxmlAssetId=rr[i]['data']['m_Id'], name='OverviewConditional'+key,
        name_UxmlAttributeFlags=1, Binding=list_binding('report.ScoutedProConsList.'+key),
        PreviewVisibilityToggle=0, PreviewVisibilityToggle_UxmlAttributeFlags=1,
        VisibilityType=0, VisibilityType_UxmlAttributeFlags=1)
    rr[srid].clear()
    rr[srid].update(replacement)
    rr[i]['data']['m_FullTypeName'] = 'SI.Bindable.SIVisible'
for i in [1008, 1011]:
    assert rr[i] == old[i] and serial(rr,i) == serial(old,i)
save(G, pid, doc, sid, sheet)

# The normal header uses the remaining column height; its bottom is the radar divider bottom.
page_audits = []
for pid in [-930000000001001, -930000000001003]:
    doc = objs[W][pid].read_typetree()
    rr = refs(doc)
    old = copy.deepcopy(rr)
    sid = doc['inlineSheet']['m_PathID']
    sheet = objs[W][sid].read_typetree()
    stats = named('OverviewTopSeasonTwelveStats')
    status = named('OverviewTopRightStatusPanel')
    if pid == -930000000001001:
        override(rr[status]['data'], [prop(131087, auto), prop(131096, px(0)),
            prop(131094, none), prop(131082, px(0)), prop(131084, num(1)),
            prop(131085, num(1)), prop(131090, px(2))])
        # Frame content ends at 248px (250 minus 2px padding); the 2px margin aligns at 246px.
        divider = named('OverviewStatusRadarDivider')
        props = sheet['m_Rules'][rr[divider]['data']['m_RuleIndex']]['m_Properties']
        dims = {p['m_Id']: sheet['dimensions'][p['m_Values'][0]['valueIndex']]['value']
            for p in props if p['m_Id'] in [131104,131087]}
        assert dims[131104] + dims[131087] == 246
    override(rr[stats]['data'], [prop(131087, auto), prop(131096, px(0)),
        prop(131094, none), prop(131080, px(0))])
    for i,r in old.items():
        if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
            assert rr[i] == r
    save(W, pid, doc, sid, sheet)
    page_audits.append({'page':pid,'stats_top':48,'stats_bottom':'status bottom',
        'divider_bottom':246 if pid == -930000000001001 else 140})

# Stretch each existing branch and distribute its four rows equally. Preserve text and data.
for pid in [-940000000007000, -940000000007002]:
    doc = objs[W][pid].read_typetree()
    rr = refs(doc)
    old = copy.deepcopy(rr)
    sid = doc['inlineSheet']['m_PathID']
    sheet = objs[W][sid].read_typetree()
    for i in [1041, named('SeasonStatsIsGoalkeeperSwitch'), named('SeasonStatsOutfielderPanel'), named('SeasonStatsGoalkeeperPanel')]:
        override(rr[i]['data'], [prop(131087, pct(100)), prop(131096, px(0)), prop(131094, none)])
    for prefix in ['SeasonStatsRow', 'GoalkeeperStatsRow']:
        for j in range(1,5):
            i = named(prefix+str(j))
            override(rr[i]['data'], [prop(131087, px(0)), prop(131096, px(0)),
                prop(131094, none), prop(131082, px(0)), prop(131084, num(1)), prop(131085, num(1))])
            for child in rr[i]['data']['m_Children']:
                c = child['rid']
                if 'StatCell_' in sd(c).get('name',''):
                    override(rr[c]['data'], [prop(131088, en('center'))])
    for i,r in old.items():
        if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
            assert rr[i] == r, ('stat binding changed',pid,i)
    save(W, pid, doc, sid, sheet)

def rebalance(layout):
    cards = sorted([c for c in layout['m_gridComponents'] if c['m_location']['y'] == 8], key=lambda c:c['m_location']['x'])
    assert len(cards) == 6
    assert cards[3]['m_elementID'] == 'PlayerTrainingOverview'
    assert cards[4]['m_elementID'] == 'PlayerSeasonStats' and cards[4]['m_location']['width'] == 8
    cards[3], cards[4] = cards[4], cards[3]
    cursor = 0
    for card,width in zip(cards,[2,2,2,8,2,4]):
        card['m_location'].update(x=cursor,width=width)
        cursor += width
    assert cursor == 20 and cards[3]['m_location']['x'] == 6
    assert 6 + 8/2 == 20/2
    return [{'id':c['m_elementID'],'x':c['m_location']['x'],'width':c['m_location']['width']} for c in cards]

layoutpid = 3901662990989568885
layout = objs[L][layoutpid].read_typetree()
default_order = rebalance(layout)
objs[L][layoutpid].save_typetree(layout)
changed[L][layoutpid] = layout
cacheout = None
if CACHE in before:
    cache = json.loads(before[CACHE])
    saved_order = rebalance(cache)
    cacheout = json.dumps(cache,ensure_ascii=False,separators=(',',':')).encode('utf8')
    (OUT/'saved-layout.json').write_bytes(cacheout)

outputs = {n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check = {o.path_id:o for o in UnityPy.load(b).objects}
    assert set(check) == set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]:
            assert sha(check[i].get_raw_data()) == h, ('unrelated object altered',n,i)
    for i,d in changed[n].items():
        assert check[i].read_typetree() == d, ('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
report = {'installed':False,'runtime_verified':False,'stats_rows_equal':True,
    'native_stats_bindings_preserved':True,'pros_cons_visibility':'native list has items independently',
    'bottom_order':default_order,'saved_layout_updated':cacheout is not None,'pages':page_audits,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore = ['$ErrorActionPreference = "Stop"']
for p in before:
    tag = 'backup-cache' if p == CACHE else 'backup-game' if p.parent == GAME else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items():
    assert p.read_bytes() == b
for p,h in protected.items():
    assert sha(p.read_bytes()) == h
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
    for p,h in protected.items():
        assert sha(p.read_bytes()) == h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True)
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'bottom':default_order,'changed_objects':{n:list(c) for n,c in changed.items()}}))
