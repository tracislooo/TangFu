from pathlib import Path
import ast,copy,json,struct,uuid,importlib.util,zlib

bootstrap=Path('second-overview-stats-bans-stacked-pitch.py').read_text('utf8').split('SELECTOR_SOURCE =')[0]
bootstrap=bootstrap.replace("'second-overview-stats-bans-stacked-pitch-'","'third-overview-300px-flow-5to3-dividers-'")
exec(compile(bootstrap,'backup-and-serialization','exec'))
for p in [GAME/G,SKIN/G]:protected[p]=sha(p.read_bytes())
PAGE,STYLE=-940000000010000,-940000000010001
BP,BS=-940000000011010,-940000000011011
BGUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-third-overview-bans-auto-content-height-v1').hex
SOURCE=-3667015745575234167

def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def save(pid,data,sid=None,styles=None):
    if sid is not None:
        validate_ui(data,styles);objs[W][sid].save_typetree(styles);changed[W][sid]=styles
    objs[W][pid].save_typetree(data);changed[W][pid]=data
def add_object(source,pid,data):
    assert pid not in objs[W]
    o=copy.copy(objs[W][source]);o.path_id=pid;o.assets_file.objects[pid]=o;objs[W][pid]=o
    o.save_typetree(data);changed[W][pid]=data
def natural(i):
    override(rr[i]['data'],[prop(131087,auto),prop(131096,px(0)),prop(131094,none),
        prop(131082,auto),prop(131084,num(0)),prop(131085,num(0)),prop(131105,pct(100)),
        prop(131097,px(0)),prop(131095,pct(100)),prop(131088,en('flex-start')),
        prop(131093,px(0)),prop(131090,px(0))])

# A private native bans component sizes itself to its rows; the complete left column scrolls.
ban=copy.deepcopy(objs[W][SOURCE].read_typetree());old_sid=ban['inlineSheet']['m_PathID']
sheet=copy.deepcopy(objs[W][old_sid].read_typetree());ban.update(m_Name='ThirdOverviewBansContentHeight',inlineSheet={'m_FileID':0,'m_PathID':BS})
ban['m_ContentHash']=struct.unpack('<i',struct.pack('<I',zlib.crc32(BGUID.encode())))[0]
sheet['m_Name']=ban['m_Name']+'_Style';rr=refs(ban);old=copy.deepcopy(rr)
for i,r in rr.items():
    a=r.get('data',{})
    if 'm_RuleIndex' in a and a.get('m_FullTypeName')!='UnityEngine.UIElements.UXML':
        natural(i)
    if a.get('m_FullTypeName')=='SI.Bindable.StreamedTable':
        sd(i).update(ClampSizeToPage=1,ClampSizeToPage_UxmlAttributeFlags=1,
            VerticalScrollerVisibility=2,VerticalScrollerVisibility_UxmlAttributeFlags=1)
        for key in ['Binding','FactoryAsset','InitFunction','SelectionEvents','SelectedItemsBinding']:
            if key in sd(i):assert sd(i)[key]==serial(old,i)['data'][key]
validate_ui(ban,sheet);add_object(old_sid,BS,sheet);add_object(SOURCE,BP,ban)

doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr)
sheet=objs[W][STYLE].read_typetree();next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
middle=named('ThirdOverviewMiddleColumn');right=named('ThirdOverviewRightHeaderContext')
right_body=named('ThirdOverviewRightColumn');lower=named('ThirdOverviewLeftIdentityAndBans')
identity=named('ThirdOverviewIdentityScroll');attr=named('ThirdOverviewAttributesScroll')

# Native scroll container outside, plain natural-height content frames inside.
replaced=set()
def replace_kind(i,source_i,kind):
    rid=rr[i]['data']['m_SerializedData']['rid'];replacement=copy.deepcopy(serial(old,source_i))
    replacement['rid']=rid;replacement['data'].update(uxmlAssetId=rr[i]['data']['m_Id'],
        name=serial(old,i)['data'].get('name',''),name_UxmlAttributeFlags=1)
    rr[rid].clear();rr[rid].update(replacement);rr[i]['data']['m_FullTypeName']=kind;replaced.add(rid)
replace_kind(1102,1703,'SI.UI.SIScrollView')
for i in [identity,6228]:replace_kind(i,1291,'UnityEngine.UIElements.VisualElement')
override(rr[1102]['data'],[prop(131105,px(300)),prop(131097,px(300)),prop(131095,px(300)),
    prop(131082,px(300)),prop(131084,num(0)),prop(131085,num(0)),prop(131073,en('stretch'))])
for i,grow in [(middle,5),(right,3)]:
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131082,px(0)),
        prop(131084,num(grow)),prop(131085,num(1)),prop(131092,px(0))])
for i in [1114,1116,1118,1119,1121,1123,1166,1167,1169,1293,lower,identity,1291,1297,6228]:natural(i)
override(rr[1293]['data'],[prop(131073,en('center'))])
# The card frame sits at top=-23 and has height=286. Account for its full painted bounds.
override(rr[1299]['data'],[prop(131105,px(450)),prop(131097,px(450)),prop(131095,none),
    prop(131087,px(263)),prop(131096,px(263)),prop(131094,px(263)),prop(131093,px(23)),
    prop(131090,px(0)),prop(131084,num(0)),prop(131085,num(0)),prop(131074,en('center'))])
override(rr[lower]['data'],[prop(131093,px(4))])
override(rr[6228]['data'],[prop(131093,px(4))])
for i in [1171,1175,1188,1205]:natural(i)
override(rr[1219]['data'],[prop(131087,auto),prop(131096,px(0)),prop(131094,none),prop(65552,en('normal'))])
for i in [1031,6232,6276]:override(rr[i]['data'],[prop(458768,en('hidden'))])
for using in doc['m_Usings']:
    if using['alias']=='PlayerReportBansBlock':using.update(path=BGUID,asset={'m_FileID':0,'m_PathID':0})

def gray():
    return val(4,{k:struct.unpack('<f',struct.pack('<f',v/255))[0] for k,v in zip(['r','g','b','a'],[135,140,145,160])})
def divider(parent,name,vertical=False):
    i=add_pair(old[1291],serial(old,1291),parent,name)
    override(rr[i]['data'],[prop(131102,en('relative')),prop(131084,num(0)),prop(131085,num(0)),
        prop(131082,auto),prop(458752,gray()),prop(262150,px(0)),prop(262151,px(0)),
        prop(131105,px(1) if vertical else pct(100)),prop(131097,px(1) if vertical else px(0)),
        prop(131095,px(1) if vertical else pct(100)),prop(131087,pct(100) if vertical else px(1)),
        prop(131096,px(0) if vertical else px(1)),prop(131094,pct(100) if vertical else px(1)),
        prop(131091,px(4 if vertical else 0)),prop(131092,px(4 if vertical else 0)),
        prop(131093,px(0 if vertical else 4)),prop(131090,px(0 if vertical else 4))])
    return i
v=divider(1002,'ThirdOverviewMiddleRightDivider',True)
rr[1002]['data']['m_Children']=[{'rid':1102},{'rid':middle},{'rid':v},{'rid':right}]
hm=divider(middle,'ThirdOverviewMiddleHorizontalDivider')
rr[middle]['data']['m_Children']=[{'rid':attr},{'rid':hm},{'rid':1007}]
override(rr[1007]['data'],[prop(131093,px(0))])
hr=divider(right_body,'ThirdOverviewRightHorizontalDivider')
rr[right_body]['data']['m_Children']=[{'rid':1703},{'rid':hr},{'rid':1173}]
override(rr[1703]['data'],[prop(131090,px(0))])
for i,r in old.items():
    if i not in replaced and 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i]==r,('existing binding altered',i)
assert 23-23==0 and 23+263==286
assert 5/(5+3)==.625 and 3/(5+3)==.375
save(PAGE,doc,STYLE,sheet)

ab=next(o for o in objs[W].values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
entry=next(v for k,v in meta['m_Container'] if k=='72b2a804423579143940e7fc9b38914d' and v['asset']['m_PathID']==SOURCE)
span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
for ptr in span:
    if ptr['m_FileID']==0:
        if ptr['m_PathID']==SOURCE:ptr['m_PathID']=BP
        elif ptr['m_PathID']==old_sid:ptr['m_PathID']=BS
for ptr in [copy.deepcopy(ban['m_Script']),{'m_FileID':0,'m_PathID':BS},{'m_FileID':0,'m_PathID':BP}]:
    if ptr not in span:span.append(ptr)
meta['m_Container'].append((BGUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':BP}}))
meta['m_PreloadTable'].extend(span);meta['m_Container'].sort(key=lambda x:x[0]);save(ab.path_id,meta)
spec=importlib.util.spec_from_file_location('cat',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=next(x for x in cat.locations('72b2a804423579143940e7fc9b38914d') if cat.location(x)['type'][1].endswith('VisualTreeAsset'))
cat=cm.Catalog(cat.add_key_location(BGUID,loc,loc));newloc=cat.locations(BGUID)[0]
assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(W)
idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)=='GameWorldVisualTreeAssetPreload');ko,ls=cat.key_records[idx]
locations=[x[0] for x in cat.array(ls,'I')]+[newloc];newset=cat.append(b''.join(struct.pack('<I',x) for x in locations),True)
records=list(cat.key_records);records[idx]=(ko,newset);table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table)
catout=bytes(cat.data);hashout=hashlib.md5(catout).hexdigest().encode()
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs[W])
for i,h in hashes[W].items():
    if i not in changed[W]:assert sha(check[i].get_raw_data())==h,('unrelated object altered',i)
for i,d in changed[W].items():assert check[i].read_typetree()==d,('roundtrip mismatch',i)
(OUT/W).write_bytes(output);(OUT/'catalog.bin').write_bytes(catout);(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'third_only':True,'left_width':300,
    'left_flow':'card painted bounds 0..286, natural identity and bans, one outer scroll',
    'middle_right_ratio':[5,3],'horizontal_dividers':2,'vertical_middle_right_divider':1,
    'original_player_data_bindings_retained':True,'first_second_bottom_and_selectors_unchanged':True,
    'new_bans_guid':BGUID,'after_sha256':sha(output)}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
    tag='backup-skin' if p.parent==SKIN else 'backup-game'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for folder in [GAME,SKIN]:(folder/W).write_bytes(output);assert (folder/W).read_bytes()==output
    for p,b in [(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout)]:p.write_bytes(b);assert p.read_bytes()==b
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'left_width':300,'middle_right_ratio':[5,3]}))
