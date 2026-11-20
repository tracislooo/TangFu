from pathlib import Path
import sys, copy, ast, json, hashlib, datetime, subprocess, importlib.util, uuid, struct, zlib
R = Path.cwd()
sys.path.insert(0, str(R / '.codex-deps'))
import UnityPy
from UnityPy.helpers import TypeTreeHelper
GAME = Path('F:/Steam/steamapps/common/Project Taco/fm_Data/StreamingAssets/aa/StandaloneWindows64')
SKIN = Path('G:/Doc/FM Skin Builder/skins/tf27-01/packages')
W = 'ui-visualtreeassets_assets_gameworldvisualtreeassetpreload.bundle'
G = 'ui-visualtreeassets_assets_globalvisualtreeassetpreload.bundle'
OUT = R / ('overview-role-selector-three-columns-' + datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=-4))).strftime('%Y%m%d-%H%M%S'))
OUT.mkdir()
sha = lambda b: hashlib.sha256(b).hexdigest()
paths = [p / n for p in [GAME, SKIN] for n in [W, G]] + [GAME.parent / 'catalog.bin', GAME.parent / 'catalog.hash', SKIN / 'catalog.bin']
before = {p: p.read_bytes() for p in paths}
for p, b in before.items():
    folder = OUT / ('backup-skin' if p.parent == SKIN else 'backup-game')
    folder.mkdir(exist_ok=True)
    (folder / p.name).write_bytes(b)
for n in [W, G]:
    assert before[GAME / n] == before[SKIN / n]
protected = {p: sha(p.read_bytes()) for folder in [GAME, SKIN] for p in [folder / 'ui-backgrounds_assets_common.bundle', folder / 'ui-tileslayouts_assets_all.bundle']}
env = {n: UnityPy.load(before[GAME / n]) for n in [W, G]}
objs = {n: {o.path_id: o for o in e.objects} for n, e in env.items()}
hashes = {n: {i: sha(o.get_raw_data()) for i, o in oo.items()} for n, oo in objs.items()}
changed = {W: {}, G: {}}
oldwrite = TypeTreeHelper.write_value
source = ast.parse((R / 'redesign-card-top-info-foot.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name in {'write', 'val', 'px', 'pct', 'en', 'num', 'prop', 'rule', 'override'}], type_ignores=[]), 'helpers', 'exec'))
TypeTreeHelper.write_value = write
poolmap = {2: 'floats', 3: 'dimensions', 4: 'colors', 5: 'strings', 6: 'assets', 7: 'strings', 8: 'strings'}
source = ast.parse((R / 'add-card-six-ratings.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in source.body if isinstance(n, ast.FunctionDef) and n.name == 'validate_ui'], type_ignores=[]), 'validator', 'exec'))
auto = {'m_ValueType': 1, 'valueIndex': 2}
none = {'m_ValueType': 1, 'valueIndex': 3}
SOURCE_PID = -4928795461599700197
SOURCE_GUID = '71ce851e086e1f440b63ed3dbda009d9'
PID, SID = -940000000005000, -940000000005001
KEY = uuid.uuid5(uuid.NAMESPACE_URL, 'fm27-overview-private-portrait-pitch-role-comparison-three-columns').hex
assert PID not in objs[G] and SID not in objs[G]
doc = copy.deepcopy(objs[G][SOURCE_PID].read_typetree())
original_doc = copy.deepcopy(doc)
original_sid = doc['inlineSheet']['m_PathID']
sheet = copy.deepcopy(objs[G][original_sid].read_typetree())
doc['m_Name'] = 'OverviewPortraitPitchRolesComparisonThreeColumns'
sheet['m_Name'] = doc['m_Name'] + '_Style'
doc['inlineSheet'] = {'m_FileID': 0, 'm_PathID': SID}
doc['m_ContentHash'] = struct.unpack('<i', struct.pack('<I', zlib.crc32(KEY.encode())))[0]
rr = {r['rid']: r for r in doc['references']['RefIds']}
original_rr = copy.deepcopy(rr)
def sd(i):
    return rr[rr[i]['data']['m_SerializedData']['rid']]['data']
def move(i, parent):
    node = rr[i]['data']
    rr[node['m_Parent']['rid']]['data']['m_Children'].remove({'rid': i})
    node['m_Parent'] = {'rid': parent}
    rr[parent]['data']['m_Children'].append({'rid': i})
def new_frame(i, name, parent, visible=False):
    sample = 1020 if visible else 1009
    node = copy.deepcopy(rr[sample])
    serial = copy.deepcopy(rr[node['data']['m_SerializedData']['rid']])
    node['rid'] = i
    node['data'].update(m_Id=2138000000+i, m_Parent={'rid': parent}, m_Children=[], m_RuleIndex=-1, m_Classes=[], m_SerializedData={'rid': i+1})
    serial['rid'] = i+1
    serial['data'].update(uxmlAssetId=2138000000+i, name=name, name_UxmlAttributeFlags=1)
    if visible:
        serial['data'].update(InvertDirectBinding=0, InvertDirectBinding_UxmlAttributeFlags=1)
        serial['data']['Binding'] = copy.deepcopy(sd(1055)['Binding'])
    rr[i] = node
    rr[i+1] = serial
    doc['references']['RefIds'].extend([node, serial])
    rr[parent]['data']['m_Children'].append({'rid': i})
def fill(i, grow=0):
    override(rr[i]['data'], [prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),prop(131096,px(0)),prop(131074,en('stretch')),prop(131073,en('stretch')),prop(131084,num(grow)),prop(131085,num(1))])
new_frame(2000, 'OverviewVerticalPitchColumn', 1007)
new_frame(2002, 'OverviewPhaseRolesColumn', 1007)
new_frame(2004, 'OverviewComparisonColumn', 1007)
new_frame(2006, 'OverviewComparisonContentVisible', 2004, visible=True)
for i in [1009,1010,1011]:
    move(i, 2000)
move(1074,2002)
move(1012,2002)
move(1020,2004)
move(1064,2006)
rr[2004]['data']['m_Children'] = [{'rid':1020},{'rid':2006}]
# The old switch no longer owns the comparison branch, so it becomes a normal frame.
switch_id = rr[1055]['data']['m_SerializedData']['rid']
replacement = copy.deepcopy(rr[rr[1009]['data']['m_SerializedData']['rid']])
replacement['rid'] = switch_id
replacement['data'].update(uxmlAssetId=rr[1055]['data']['m_Id'],name='OverviewPersistentRolesFrame',name_UxmlAttributeFlags=1)
rr[switch_id].clear()
rr[switch_id].update(replacement)
rr[1055]['data']['m_FullTypeName'] = 'UnityEngine.UIElements.VisualElement'
assert rr[1055]['data']['m_Children'] == [{'rid':1063}]
for v in rr[1018]['data']['ValueVariables']:
    if v['m_name'] == 'showTeamCompareTable':
        v['m_scopeValue']['m_serializedData'] = 'Bool|1|'
for p in rr[1006]['data']['m_Properties']:
    if p['name'] == 'value-vars':
        p['value'] = p['value'].replace('{showTeamCompareTable}{Bool|0|}', '{showTeamCompareTable}{Bool|1|}')
fill(1007,1)
rr[1007]['data']['m_Classes'] = ['flex-grow-class']
override(rr[1007]['data'], [prop(131083,en('row')),prop(131087,pct(100)),prop(131094,pct(100)),prop(262150,px(0)),prop(262151,px(0))])
for i, weight in [(2000,26),(2002,37),(2004,37)]:
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(weight)),prop(131085,num(1)),prop(131083,en('column')),prop(131073,en('stretch')),prop(131074,en('stretch')),prop(131096,px(0)),prop(131092,px(8 if i!=2004 else 0))])
for i in [1009,1019,1031,1011,1025,1026]:
    fill(i)
override(rr[1009]['data'],[prop(131087,px(38)),prop(131096,px(38)),prop(131094,px(38)),prop(131090,px(0))])
override(rr[1019]['data'],[prop(131083,en('column'))])
for i in [1030,1057,1038,1040]:
    override(rr[i]['data'],[prop(131097,px(0)),prop(65537,px(11)),prop(65546,en('middle-left'))])
# Match the native portrait pitch background to the actual portrait tactics panel.
rr[1010]['data']['m_Classes'] = []
override(rr[1010]['data'],[prop(131102,en('relative')),prop(131105,pct(100)),prop(131097,px(0)),prop(131087,px(0)),prop(131096,px(0)),prop(131094,none),prop(131084,num(0)),prop(131085,num(0)),prop(131099,px(0)),prop(131100,px(0)),prop(131101,pct(150)),prop(131098,px(0)),prop(131090,px(8))])
override(rr[1022]['data'],[prop(131081,en('none'))])
rr[1023]['data']['m_Classes'] = ['data_display-positions-suitability-medium-small-default-type-thematic-orientation-portrait','playerreport_positional_data_points']
override(rr[1023]['data'],[prop(131102,en('absolute')),prop(131089,px(0)),prop(131103,px(0)),prop(131104,px(0)),prop(131080,px(0)),prop(131105,auto),prop(131087,auto),prop(131097,px(0)),prop(131095,none),prop(131096,px(0)),prop(131094,none),prop(262150,px(0)),prop(262151,px(0))])
sd(1023).update(Orientation=0,Orientation_UxmlAttributeFlags=1)
for i in [1012,1028,1042,1055,1063,1068,2006,1064]:
    fill(i,1)
    override(rr[i]['data'],[prop(131083,en('column')),prop(131082,px(0))])
fill(1074)
override(rr[1074]['data'],[prop(131087,px(38)),prop(131096,px(38)),prop(131094,px(38)),prop(131083,en('row')),prop(131090,px(0)),prop(131093,px(0))])
for i in [1079,1080,1083,1085]:
    override(rr[i]['data'],[prop(131097,px(0)),prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131099,px(3)),prop(131100,px(3)),prop(131087,px(30)),prop(131096,px(30)),prop(131094,px(30))])
for i in [1089,1093]:
    override(rr[i]['data'],[prop(65537,px(10)),prop(131097,px(0))])
fill(1020)
override(rr[1020]['data'],[prop(131087,px(38)),prop(131096,px(38)),prop(131094,px(38)),prop(131073,en('flex-start'))])
override(rr[1033]['data'],[prop(131097,px(0)),prop(131087,px(30)),prop(131096,px(30)),prop(131094,px(30)),prop(131099,px(5)),prop(131100,px(5))])
override(rr[1048]['data'],[prop(65537,px(12))])
for i in [1070,1075]:
    fill(i,1)
    override(rr[i]['data'],[prop(131082,px(0)),prop(131094,none)])
    sd(i).update(ResizeColumnWidthsToFit=1,ResizeColumnWidthsToFit_UxmlAttributeFlags=1,ScrollViewMode=2,ScrollViewMode_UxmlAttributeFlags=1,HorizontalScrollerVisibility=0,HorizontalScrollerVisibility_UxmlAttributeFlags=1,VerticalScrollerVisibility=0,VerticalScrollerVisibility_UxmlAttributeFlags=1)
# Native input events, position selection, role table data, and comparison data remain byte-identical.
for i in [1002,1003,1004,1005,1033,1042,1063,1064,1083,1085]:
    sid=original_rr[i]['data'].get('m_SerializedData',{}).get('rid')
    if sid is not None:assert rr[sid]==original_rr[sid],('native behavior changed',i)
for i in [1070,1075]:
    oldsd=original_rr[original_rr[i]['data']['m_SerializedData']['rid']]['data']
    for key in ['Binding','InitFunction','FactoryAsset','SelectedItemsBinding','SelectionEvents','SelectionCellID']:
        assert sd(i)[key]==oldsd[key],(i,key)
validate_ui(doc,sheet)
for newpid,sourcepid,data in [(SID,original_sid,sheet),(PID,SOURCE_PID,doc)]:
    obj=copy.copy(objs[G][sourcepid]);obj.path_id=newpid
    obj.assets_file.objects[newpid]=obj;objs[G][newpid]=obj
    obj.save_typetree(data);changed[G][newpid]=data
# Only the two overview instances reference the new private selector.
for pagepid in [-930000000001001,-930000000001003]:
    page=objs[W][pagepid].read_typetree();oldpage=copy.deepcopy(page)
    matches=[u for u in page['m_Usings'] if u['alias']=='role_selector-large']
    assert len(matches)==1 and matches[0]['path']==SOURCE_GUID
    matches[0]['path']=KEY;matches[0]['asset']={'m_FileID':0,'m_PathID':0}
    assert page['references']==oldpage['references']
    validate_ui(page,objs[W][page['inlineSheet']['m_PathID']].read_typetree())
    objs[W][pagepid].save_typetree(page);changed[W][pagepid]=page
ab=next(o for o in objs[G].values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
entry=next(v for k,v in meta['m_Container'] if k==SOURCE_GUID and v['asset']['m_PathID']==SOURCE_PID)
span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for ptr in span:
    if ptr['m_FileID']==0 and ptr['m_PathID'] in [SOURCE_PID,original_sid]:ptr['m_PathID']={SOURCE_PID:PID,original_sid:SID}[ptr['m_PathID']]
for ptr in [copy.deepcopy(doc['m_Script']),{'m_FileID':0,'m_PathID':SID},{'m_FileID':0,'m_PathID':PID}]:
    if ptr not in span:span.append(ptr)
meta['m_Container'].append((KEY,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':PID}}))
meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda kv:kv[0]);ab.save_typetree(meta);changed[G][ab.path_id]=meta
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cat=cm.Catalog(before[GAME.parent/'catalog.bin'])
loc=next(x for x in cat.locations(SOURCE_GUID) if cat.location(x)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
cat=cm.Catalog(cat.add_key_location(KEY,loc,loc));newloc=cat.locations(KEY)[0]
assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(G)
idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)=='GlobalVisualTreeAssetPreload')
ko,ls=cat.key_records[idx];locs=[x[0] for x in cat.array(ls,'I')]+[newloc]
newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[idx]=(ko,newset)
table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table)
catout=bytes(cat.data);outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check={o.path_id:o for o in UnityPy.load(b).objects}
    assert set(check)==set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated object changed',n,i)
    for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout)
hashout=hashlib.md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'private_guid':KEY,'private_pid':PID,'column_ratio':[26,37,37],'gap_px':8,'pitch_orientation':'native portrait 0 with native thematic portrait background','comparison_default_visible':True,'native_position_role_and_comparison_events_preserved':True,'unrelated_objects_verified_unchanged':True,'overview_outer_layout_unchanged':True,'after_sha256':{**{n:sha(b) for n,b in outputs.items()},'catalog.bin':sha(catout),'catalog.hash':sha(hashout)}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
assert not proc.stdout.strip(),'Prepared files ready; exit the running game before install'
try:
    for n,b in outputs.items():
        for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
    for p,b in [(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout)]:p.write_bytes(b);assert p.read_bytes()==b
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report['installed']=True;(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
    tag='backup-skin' if p.parent==SKIN else 'backup-game'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
print(json.dumps({'installed':True,'output':str(OUT),'private_guid':KEY,'column_ratio':[26,37,37]},ensure_ascii=True))
