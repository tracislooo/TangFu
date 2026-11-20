from pathlib import Path
import ast,copy,json,struct,uuid,zlib,importlib.util

bootstrap=Path('second-overview-stats-bans-stacked-pitch.py').read_text('utf8').split('SELECTOR_SOURCE =')[0]
bootstrap=bootstrap.replace("'second-overview-stats-bans-stacked-pitch-'","'third-left-fc-hidden-overview-'")
exec(compile(bootstrap,'backup-and-native-serialization','exec'))
L='ui-tileslayouts_assets_all.bundle'
CACHE=Path('C:/Users/traci/AppData/LocalLow/Sports Interactive/Football Manager 27/CustomGridCompositions/PlayerReportOverviewComposition-Large')
for p in [GAME/L,SKIN/L]+([CACHE] if CACHE.exists() else []):
    before[p]=p.read_bytes()
    tag='backup-cache' if p==CACHE else 'backup-skin' if p.parent==SKIN else 'backup-game'
    folder=OUT/tag;folder.mkdir(exist_ok=True);(folder/p.name).write_bytes(before[p])
for p in [GAME/L,SKIN/L]:protected.pop(p)
assert before[GAME/L]==before[SKIN/L]
env[L]=UnityPy.load(before[GAME/L]);objs[L]={o.path_id:o for o in env[L].objects}
hashes[L]={i:sha(o.get_raw_data()) for i,o in objs[L].items()};changed[L]={}

PAGE,PS=-940000000010000,-940000000010001
STATS,SS=-940000000010010,-940000000010011
SELECTOR,GS=-940000000010020,-940000000010021
DESCRIPTION=-940000000010030
PAGE_GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-third-left-fc-card-hidden-overview-v1').hex
STATS_GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-third-left-fc-native-season-stats-v1').hex
SELECTOR_GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-third-left-fc-portrait-pitch-roles-comparison-v1').hex
TITLE='左边版FC卡面+隐藏';IDENT='PlayerOverviewLeftFC';TITLE_KEY='OverviewLeftFCVariantTitle'
clones=[]

def serial(refs0,i):return refs0[refs0[i]['data']['m_SerializedData']['rid']]
def add_object(n,source_pid,pid,data):
    assert pid not in objs[n],('existing object',pid)
    o=copy.copy(objs[n][source_pid]);o.path_id=pid;o.assets_file.objects[pid]=o;objs[n][pid]=o
    o.save_typetree(data);changed[n][pid]=data
def save(n,pid,data,sid=None,styles=None):
    if sid is not None:
        validate_ui(data,styles);objs[n][sid].save_typetree(styles);changed[n][sid]=styles
    objs[n][pid].save_typetree(data);changed[n][pid]=data
def clone(n,source,pid,sid,key,label):
    doc=copy.deepcopy(objs[n][source].read_typetree());old_sid=doc['inlineSheet']['m_PathID']
    styles=copy.deepcopy(objs[n][old_sid].read_typetree())
    meta=next(o.read_typetree() for o in objs[n].values() if o.type.name=='AssetBundle')
    source_key=next(k for k,v in meta['m_Container'] if v['asset']['m_PathID']==source)
    doc.update(m_Name=label,inlineSheet={'m_FileID':0,'m_PathID':sid})
    doc['m_ContentHash']=struct.unpack('<i',struct.pack('<I',zlib.crc32(key.encode())))[0]
    styles['m_Name']=label+'_Style'
    clones.append({'bundle':n,'source':source,'source_style':old_sid,'source_key':source_key,
        'pid':pid,'style':sid,'key':key,'doc':doc})
    return doc,styles,old_sid
def commit_clone(n,source,pid,sid,old_sid,doc,styles):
    validate_ui(doc,styles);add_object(n,old_sid,sid,styles);add_object(n,source,pid,doc)
def move(i,parent):
    a=rr[i]['data'];rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i})
    a['m_Parent']={'rid':parent};rr[parent]['data']['m_Children'].append({'rid':i})
def size(i,grow=0,basis=None,height=None,width=None):
    props=[prop(131097,px(0)),prop(131096,px(0)),prop(131094,none),prop(131095,pct(100)),
        prop(131084,num(grow)),prop(131085,num(1)),prop(131073,en('stretch')),prop(131074,en('stretch'))]
    if basis is not None:props.append(prop(131082,px(basis)))
    if height is not None:props.append(prop(131087,height))
    if width is not None:props.append(prop(131105,width))
    override(rr[i]['data'],props)

# Independent three-column selector, using the game's portrait background and position orientation.
doc,sheet,old_sid=clone(G,-940000000005000,SELECTOR,GS,SELECTOR_GUID,'ThirdOverviewPortraitPitchRolesComparison')
rr=refs(doc);original=copy.deepcopy(rr);next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
third=add_pair(rr[2002],serial(rr,2002),1007,'ThirdOverviewComparisonColumn')
move(2006,third)
rr[2000]['data']['m_Children'].remove({'rid':2008});drop={2008,rr[2008]['data']['m_SerializedData']['rid']}
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in drop]
for i in drop:rr.pop(i)
doc['m_ContentContainerId']=0
for i in [2000,2002,third]:
    size(i,1,0,pct(100),px(0));override(rr[i]['data'],[prop(131090,px(0)),prop(131092,px(8 if i!=third else 0))])
size(2010,1,0,px(0),pct(100));override(rr[2010]['data'],[prop(131090,px(0))])
size(2006,1,0,px(0),pct(100))
native=objs[G][-9211596620732837621].read_typetree();nr=refs(native)
fit=add_pair(nr[1145],serial(nr,1145),1010,'ThirdOverviewPortraitPitchRatio')
sd(fit).update(AspectMode=2,AspectMode_UxmlAttributeFlags=1,AspectRatio=1.5,AspectRatio_UxmlAttributeFlags=1)
for i in [1022,1023]:move(i,fit)
override(rr[1010]['data'],[prop(131101,px(0)),prop(131087,px(0)),prop(131082,px(0)),
    prop(131084,num(1)),prop(131085,num(1)),prop(131090,px(2)),prop(131073,en('center')),prop(131088,en('center'))])
size(fit,0,None,pct(100),pct(100));override(rr[fit]['data'],[prop(131102,en('relative')),prop(131085,num(0)),prop(131074,en('center'))])
override(rr[1022]['data'],[prop(131081,en('none'))])
rr[1023]['data']['m_Classes']=['data_display-positions-suitability-medium-small-default-type-thematic-orientation-portrait','playerreport_positional_data_points']
sd(1023).update(Orientation=0,Orientation_UxmlAttributeFlags=1)
override(rr[1011]['data'],[prop(131093,px(2)),prop(131090,px(2))])
for i in [1070,1075]:
    if i in rr:
        sd(i).update(ResizeColumnWidthsToFit=1,ResizeColumnWidthsToFit_UxmlAttributeFlags=1,
            ScrollViewMode=2,ScrollViewMode_UxmlAttributeFlags=1)
for i,r in original.items():
    if i in drop:continue
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        expected=copy.deepcopy(r)
        if i==original[1023]['data']['m_SerializedData']['rid']:expected['data'].update(Orientation=0,Orientation_UxmlAttributeFlags=1)
        for table in [1070,1075]:
            if table in original and i==original[table]['data']['m_SerializedData']['rid']:
                expected['data'].update(ResizeColumnWidthsToFit=1,ResizeColumnWidthsToFit_UxmlAttributeFlags=1,ScrollViewMode=2,ScrollViewMode_UxmlAttributeFlags=1)
        assert rr[i]==expected,('selector bindings altered',i)
commit_clone(G,-940000000005000,SELECTOR,GS,old_sid,doc,sheet)

# Compact first-version statistics, without changing its league-aware component or numeric formatters.
doc,sheet,old_sid=clone(W,-940000000007000,STATS,SS,STATS_GUID,'ThirdOverviewNativeLeagueSeasonStats')
rr=refs(doc);original=copy.deepcopy(rr)
for i in [1041,named('SeasonStatsIsGoalkeeperSwitch'),named('SeasonStatsOutfielderPanel'),named('SeasonStatsGoalkeeperPanel')]:
    size(i,0,None,px(126),pct(100));override(rr[i]['data'],[prop(131096,px(126)),prop(131094,px(126)),prop(131085,num(0))])
for prefix in ['SeasonStatsRow','GoalkeeperStatsRow']:
    for j in range(1,5):
        i=named(prefix+str(j));size(i,0,None,px(30),pct(100))
        override(rr[i]['data'],[prop(131082,auto),prop(131096,px(30)),prop(131094,px(30)),prop(131085,num(0)),prop(131090,px(2 if j<4 else 0))])
for i,r in original.items():
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
commit_clone(W,-940000000007000,STATS,SS,old_sid,doc,sheet)

# Copy the current FC overview and reorganize its existing modules into three equal columns.
doc,sheet,old_sid=clone(W,-930000000001001,PAGE,PS,PAGE_GUID,'OverviewThirdLeftFCCardAndHidden')
rr=refs(doc);original=copy.deepcopy(rr);next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
removed=set()
def gather(i):
    if i not in rr or i in removed or i==-2:return
    removed.add(i)
    def walk(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:gather(v['rid'])
            else:
                for k,a in v.items():
                    if k!='m_Parent':walk(a)
        elif isinstance(v,list):
            for a in v:walk(a)
    walk(rr[i].get('data',{}))
def remove(i):
    a=rr[i]['data'];rr[a['m_Parent']['rid']]['data']['m_Children'].remove({'rid':i});gather(i)
def frame(parent,name):return add_pair(original[1009],serial(original,1009),parent,name)
def scroll(parent,name):
    i=add_pair(original[1703],serial(original,1703),parent,name)
    size(i,1,0,px(0),pct(100));return i
def strip(i):
    override(rr[i]['data'],[prop(262150,px(0)),prop(262151,px(0)),prop(131099,px(0)),prop(131100,px(0)),
        prop(131101,px(0)),prop(131098,px(0)),prop(131093,px(0)),prop(131090,px(0)),prop(131091,px(0)),prop(131092,px(0))])

middle=frame(1002,'ThirdOverviewMiddleColumn')
right_context=add_pair(original[1116],serial(original,1116),1002,'ThirdOverviewRightHeaderContext')
cur=right_context
for source,name in [(1118,'ThirdOverviewRightBindingExpect'),(1119,'ThirdOverviewRightHeaderRemapper'),
        (1166,'ThirdOverviewRightBannerExpect'),(1167,'ThirdOverviewRightTeamSetter')]:
    cur=add_pair(original[source],serial(original,source),cur,name)
    size(cur,1,0,px(0),pct(100));strip(cur)
right=frame(cur,'ThirdOverviewRightColumn');size(right,1,0,px(0),pct(100));strip(right)
move(1102,1002)
move(1009,middle)
move(1007,middle)
move(1703,right)
move(1173,right)
for i in [1008,1010]:remove(i)
rr[1002]['data']['m_Children']=[{'rid':1102},{'rid':middle},{'rid':right_context}]
for i in [1102,middle,right_context]:
    strip(i);size(i,1,0,pct(100),px(0));override(rr[i]['data'],[prop(131083,en('column')),prop(131092,px(8 if i!=right_context else 0))])
strip(1002);size(1002,1,0,px(0),pct(100));override(rr[1002]['data'],[prop(131083,en('row'))])
size(1001,1,0,px(0),pct(100));override(rr[1001]['data'],[prop(131096,px(674))])
sd(1705)['name']='ThirdLeftFCOverviewFrame'

# Keep the original header/team binding chain around the left column; omit unused responsive banners.
move(1166,1123)
remove(1125)
for i in [1114,1116,1118,1119,1121,1123,1166,1167,1169]:
    size(i,1,0,px(0),pct(100));strip(i)
    override(rr[i]['data'],[prop(131083,en('column'))])
left_lower=frame(1169,'ThirdOverviewLeftIdentityAndBans')
identity_scroll=scroll(left_lower,'ThirdOverviewIdentityScroll')
move(1291,identity_scroll)
move(6228,left_lower)
rr[1169]['data']['m_Children']=[{'rid':1293},{'rid':left_lower}]
for i in [1293,left_lower]:
    size(i,1,0,px(0),pct(100));strip(i)
override(rr[left_lower]['data'],[prop(131093,px(8)),prop(131083,en('column'))])
override(rr[1293]['data'],[prop(131073,en('center')),prop(131088,en('center'))])
override(rr[1299]['data'],[prop(131074,en('center')),prop(131095,none)])
size(identity_scroll,7,0,px(0),pct(100))
size(6228,3,0,px(0),pct(100));strip(6228);override(rr[6228]['data'],[prop(131093,px(8))])
size(1291,0,None,auto,pct(100));strip(1291)
strip(1297);size(1297,0,None,auto,pct(100))
override(rr[1219]['data'],[prop(65537,px(24)),prop(65552,en('normal'))])
for i in [1031,6232,6276]:
    override(rr[i]['data'],[prop(131105,px(0)),prop(131082,px(0)),prop(131084,num(1)),
        prop(131085,num(1)),prop(131089,auto),prop(131097,px(0)),prop(131095,pct(100))])
for i in [1150,1152]:
    override(rr[i]['data'],[prop(131105,pct(100)),prop(131087,pct(100))])

# Attributes above three equal native position/phase/comparison columns.
attr_scroll=scroll(middle,'ThirdOverviewAttributesScroll')
move(1009,attr_scroll)
rr[middle]['data']['m_Children']=[{'rid':attr_scroll},{'rid':1007}]
size(attr_scroll,3,0,px(0),pct(100))
size(1007,2,0,px(0),pct(100));strip(1007);override(rr[1007]['data'],[prop(131093,px(8))])
for i in [1009,1025,5850,1040]:
    size(i,0,None,auto,pct(100));override(rr[i]['data'],[prop(131082,auto),prop(131085,num(0))])
override(rr[1009]['data'],[prop(131096,px(438))])

# Hidden/advantages/tactical group above a radar/report/status/statistics row.
size(1703,3,0,px(0),pct(100));strip(1703);override(rr[1703]['data'],[prop(131090,px(8))])
size(1173,2,0,px(0),pct(100));strip(1173);override(rr[1173]['data'],[prop(131083,en('row'))])
move(1186,2242)
move(6286,2242)
remove(1349)
for i in [1179,1181,1183,1185,6288]:remove(i)
rr[1173]['data']['m_Children']=[{'rid':1026},{'rid':2242}]
for i in [1026,2242]:
    strip(i);size(i,1,0,pct(100),px(0))
    override(rr[i]['data'],[prop(131102,en('relative')),prop(131089,auto),prop(131103,auto),prop(131104,auto),prop(131080,auto)])
override(rr[1026]['data'],[prop(131092,px(8))])
override(rr[1043]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
    prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100))])
rr[2242]['data']['m_Children']=[{'rid':1186},{'rid':6286},{'rid':2986},{'rid':6304}]
override(rr[2242]['data'],[prop(131083,en('column')),prop(131088,en('flex-start'))])
size(1186,0,None,auto,pct(100));override(rr[1186]['data'],[prop(131085,num(0))])
override(rr[6286]['data'],[prop(131093,px(2)),prop(131090,px(2))])
override(rr[2986]['data'],[prop(131102,en('relative')),prop(131089,auto),prop(131103,auto),
    prop(131104,auto),prop(131080,auto),prop(131105,pct(100)),prop(131097,px(0)),
    prop(131087,px(42)),prop(131096,px(42)),prop(131094,px(42))])
for i in [2988,3806,4624]:
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131082,px(0)),
        prop(131084,num(1)),prop(131085,num(1))])
override(rr[6304]['data'],[prop(131102,en('relative')),prop(131089,auto),prop(131103,auto),
    prop(131104,auto),prop(131080,auto),prop(131105,pct(100)),prop(131097,px(0)),
    prop(131087,px(126)),prop(131096,px(126)),prop(131094,px(126)),prop(131085,num(0))])
for using in doc['m_Usings']:
    if using['alias']=='role_selector-large':using.update(path=SELECTOR_GUID,asset={'m_FileID':0,'m_PathID':0})
    elif using['alias']==rr[6304]['data']['m_TemplateAlias']:using.update(path=STATS_GUID,asset={'m_FileID':0,'m_PathID':0})
doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in removed]
rr=refs(doc)
for i,r in original.items():
    if i in removed or i==original[1705]['data']['m_SerializedData']['rid']:continue
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('original binding altered',i)
assert rr[1007]['data']['m_Children']==[]
assert rr[1002]['data']['m_Children']==[{'rid':1102},{'rid':middle},{'rid':right_context}]
commit_clone(W,-930000000001001,PAGE,PS,old_sid,doc,sheet)

# Add a third native tile choice while leaving both current descriptions and active selections alone.
desc=copy.deepcopy(objs[L][-930000000001004].read_typetree())
desc.update(m_Name='OverviewThirdLeftFCDescription')
desc['<Name>k__BackingField']=IDENT;desc['<ID>k__BackingField']=IDENT
desc['m_translationType']=2;desc['m_directTitlePath']={'m_path':TITLE_KEY}
for cfg in desc['<Configurations>k__BackingField']:
    cfg['Description']={'m_FileID':0,'m_PathID':DESCRIPTION};cfg['AssetRef']['m_AssetGUID']=PAGE_GUID
add_object(L,-930000000001004,DESCRIPTION,desc)
tiles=objs[L][1332213496068314481].read_typetree()
tiles['m_gridElementDescriptions'].append({'m_FileID':0,'m_PathID':DESCRIPTION});save(L,1332213496068314481,tiles)
layout=objs[L][3901662990989568885].read_typetree()
layout['m_placementBindings'].append({'m_elementID':IDENT,'m_optionalConditions':[],'m_optionalConfigConditions':[]})
save(L,3901662990989568885,layout)
page=objs[W][7857044477279960178].read_typetree();pr=refs(page)
variables=next(r['data'] for r in pr.values() if r.get('type',{}).get('class')=='BindingVariablesComponent/UxmlSerializedData')
variables['ValueVariables'].append({'m_name':TITLE_KEY,'m_scopeValue':{'m_serializedData':'String|'+TITLE+'|'}})
for prop0 in pr[1006]['data']['m_Properties']:
    if prop0['name']=='value-vars':prop0['value']+=',{'+TITLE_KEY+'}{String|'+TITLE+'|}'
grid=next(r['data'] for r in pr.values() if r.get('data',{}).get('Bindings',{}).get('m_gridCompositionSet',{}).get('m_PathID')==1615455816372668659)
bindings=grid['Bindings'];bindings['m_nameBindings'].append({'name':TITLE_KEY,'path':{'m_path':TITLE_KEY},'method':0})
mapping_copies=[]
for mapping in bindings['m_gridElementBindingData']:
    if mapping['DescriptionAndMapping']['DescriptionName']=='PlayerOverviewFull':
        new=copy.deepcopy(mapping);new['DescriptionAndMapping']['DescriptionName']=IDENT;mapping_copies.append(new)
mapping_copies.append({'DescriptionAndMapping':{'DescriptionName':IDENT,'MappingName':TITLE_KEY,'MappingReferenceID':0},'BindingPath':{'m_path':''},'IsDynamic':0})
bindings['m_gridElementBindingData'].extend(mapping_copies)
validate_ui(page,objs[W][page['inlineSheet']['m_PathID']].read_typetree());save(W,7857044477279960178,page)
cacheout=None
if CACHE in before:
    cache=json.loads(before[CACHE]);previous_top=copy.deepcopy(cache['m_gridComponents'][0])
    cache['m_placementBindings'].append({'m_elementID':IDENT,'m_optionalConditions':[],'m_optionalConfigConditions':[]})
    assert cache['m_gridComponents'][0]==previous_top
    cacheout=json.dumps(cache,ensure_ascii=False,separators=(',',':')).encode('utf8');(OUT/'saved-layout.json').write_bytes(cacheout)

# Register local styles and copied preload dependencies for every new component.
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
cat=cm.Catalog(before[GAME.parent/'catalog.bin'])
for bundle in [W,G]:
    ab=next(o for o in objs[bundle].values() if o.type.name=='AssetBundle');meta=ab.read_typetree()
    for c in [x for x in clones if x['bundle']==bundle]:
        entry=next(v for k,v in meta['m_Container'] if k==c['source_key'] and v['asset']['m_PathID']==c['source'])
        span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
        for ptr in span:
            if ptr['m_FileID']==0:
                if ptr['m_PathID']==c['source']:ptr['m_PathID']=c['pid']
                elif ptr['m_PathID']==c['source_style']:ptr['m_PathID']=c['style']
        for ptr in [copy.deepcopy(c['doc']['m_Script']),{'m_FileID':0,'m_PathID':c['style']},{'m_FileID':0,'m_PathID':c['pid']}]:
            if ptr not in span:span.append(ptr)
        meta['m_Container'].append((c['key'],{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':c['pid']}}));meta['m_PreloadTable'].extend(span)
        loc=next(x for x in cat.locations(c['source_key']) if cat.location(x)['type'][1].endswith('VisualTreeAsset'))
        cat=cm.Catalog(cat.add_key_location(c['key'],loc,loc));newloc=cat.locations(c['key'])[0]
        assert cat.location(cat.location(newloc)['dependencies'][0])['internal'].endswith(bundle)
        label='GameWorldVisualTreeAssetPreload' if bundle==W else 'GlobalVisualTreeAssetPreload'
        idx=next(i for i,(k,l) in enumerate(cat.key_records) if cat.object(k)==label);ko,ls=cat.key_records[idx]
        locs=[x[0] for x in cat.array(ls,'I')]+[newloc]
        newset=cat.append(b''.join(struct.pack('<I',x) for x in locs),True);records=list(cat.key_records);records[idx]=(ko,newset)
        table=cat.append(b''.join(struct.pack('<2I',*x) for x in records),True);struct.pack_into('<I',cat.data,8,table);cat=cm.Catalog(bytes(cat.data))
    meta['m_Container'].sort(key=lambda kv:kv[0]);save(bundle,ab.path_id,meta)
catout=bytes(cat.data);hashout=hashlib.md5(catout).hexdigest().encode('ascii')
outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated object altered',n,i)
    for i,data in changed[n].items():assert check[i].read_typetree()==data,('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
(OUT/'catalog.bin').write_bytes(catout);(OUT/'catalog.hash').write_bytes(hashout)
report={'installed':False,'runtime_verified':False,'new_version':TITLE,'guid':PAGE_GUID,
    'first_and_second_page_byte_identical':True,'columns':[1,1,1],'gaps':8,
    'left':{'card_identity_bans':[50,35,15],'background':'original full-column background'},
    'middle':{'attributes_and_selector':[60,40],'pitch_roles_comparison':[1,1,1],'pitch':'native portrait 0; matching portrait background'},
    'right':{'hidden_group_and_lower':[60,40],'radar_and_report_status_stats':[50,50]},
    'original_retained_binding_serializations_unchanged':True,'bottom_grid_components_unchanged':True,
    'new_assets':[{'bundle':c['bundle'],'guid':c['key'],'pid':c['pid']} for c in clones],
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
    tag='backup-cache' if p==CACHE else 'backup-skin' if p.parent==SKIN else 'backup-game'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():
    print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for n,b in outputs.items():
        for folder in [GAME,SKIN]:(folder/n).write_bytes(b);assert (folder/n).read_bytes()==b
    for p,b in [(GAME.parent/'catalog.bin',catout),(SKIN/'catalog.bin',catout),(GAME.parent/'catalog.hash',hashout)]+([(CACHE,cacheout)] if cacheout is not None else []):
        p.write_bytes(b);assert p.read_bytes()==b
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'third_guid':PAGE_GUID,'changed_objects':{n:list(x) for n,x in changed.items()}}))
