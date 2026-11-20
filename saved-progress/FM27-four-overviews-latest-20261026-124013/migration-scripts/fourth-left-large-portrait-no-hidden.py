from pathlib import Path
import ast,copy,json,struct,uuid,zlib,importlib.util

bootstrap=Path('second-overview-stats-bans-stacked-pitch.py').read_text('utf8').split('SELECTOR_SOURCE =')[0]
bootstrap=bootstrap.replace("'second-overview-stats-bans-stacked-pitch-'","'fourth-left-large-portrait-no-hidden-'")
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

PAGE,PS=-940000000012000,-940000000012001
STATS,SS=-940000000010010,-940000000010011
SELECTOR,GS=-940000000010020,-940000000010021
DESCRIPTION=-940000000012030
PAGE_GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-fourth-left-large-portrait-no-hidden-overview-v1').hex
STATS_GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-third-left-fc-native-season-stats-v1').hex
SELECTOR_GUID=uuid.uuid5(uuid.NAMESPACE_URL,'fm27-third-left-fc-portrait-pitch-roles-comparison-v1').hex
TITLE='左边版大头像+非隐藏';IDENT='PlayerOverviewLeftPortrait';TITLE_KEY='OverviewLeftPortraitVariantTitle'
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


# Work only on a private copy of the current third version.
doc,sheet,old_sid=clone(W,-940000000010000,PAGE,PS,PAGE_GUID,'OverviewFourthLeftLargePortraitNoHidden')
rr=refs(doc);original=copy.deepcopy(rr)
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1

def subtree_refs(source,root):
    found=set()
    def visit(i):
        if i not in source or i in found or i==-2:return
        found.add(i)
        def walk(v):
            if isinstance(v,dict):
                if set(v)=={'rid'}:visit(v['rid'])
                else:
                    for k,x in v.items():
                        if k!='m_Parent':walk(x)
            elif isinstance(v,list):
                for x in v:walk(x)
        walk(source[i].get('data',{}))
    visit(root);return found

def remove_tree(i):
    global rr
    parent=rr[i]['data']['m_Parent']['rid']
    rr[parent]['data']['m_Children'].remove({'rid':i})
    gone=subtree_refs(rr,i)
    doc['references']['RefIds']=[r for r in doc['references']['RefIds'] if r['rid'] not in gone]
    rr=refs(doc)
    return gone

def import_subtree(source_pid,root,parent):
    global next_rid,next_id
    donor=objs[W][source_pid].read_typetree();sr=refs(donor)
    ss=objs[W][donor['inlineSheet']['m_PathID']].read_typetree()
    found=subtree_refs(sr,root);mapping={i:next_rid+j for j,i in enumerate(sorted(found))};next_rid+=len(found)
    nodes=[i for i in found if 'm_Id' in sr[i].get('data',{})]
    uidmap={sr[i]['data']['m_Id']:next_id+j for j,i in enumerate(sorted(nodes))};next_id+=len(nodes)
    rulemap={}
    def remap(v):
        if isinstance(v,dict):
            if set(v)=={'rid'}:
                if v['rid'] in mapping:v['rid']=mapping[v['rid']]
            else:
                for k,x in v.items():
                    if k in ['m_Id','m_ParentId','uxmlAssetId'] and isinstance(x,int) and x in uidmap:v[k]=uidmap[x]
                    else:remap(x)
        elif isinstance(v,list):
            for x in v:remap(x)
    for i in sorted(found):
        r=copy.deepcopy(sr[i]);r['rid']=mapping[i];remap(r['data'])
        if i in nodes:
            ix=r['data'].get('m_RuleIndex',-1)
            if ix>=0:
                if ix not in rulemap:
                    ruledata=copy.deepcopy(ss['m_Rules'][ix])
                    for p in ruledata['m_Properties']:
                        for h in p['m_Values']:
                            if h['m_ValueType'] in poolmap:
                                pool=poolmap[h['m_ValueType']];sheet[pool].append(copy.deepcopy(ss[pool][h['valueIndex']]));h['valueIndex']=len(sheet[pool])-1
                    rulemap[ix]=len(sheet['m_Rules']);sheet['m_Rules'].append(ruledata)
                r['data']['m_RuleIndex']=rulemap[ix]
            alias=r['data'].get('m_TemplateAlias')
            if alias:
                use=next(u for u in donor['m_Usings'] if u['alias']==alias)
                current=next((u for u in doc['m_Usings'] if u['alias']==alias),None)
                if current:assert current==use,('template alias conflict',alias)
                else:doc['m_Usings'].append(copy.deepcopy(use))
        if i==root:r['data']['m_Parent']={'rid':parent}
        rr[r['rid']]=r;doc['references']['RefIds'].append(r)
    rr[parent]['data']['m_Children'].append({'rid':mapping[root]})
    return mapping

remove_tree(1293)
portrait=import_subtree(-930000000001003,1293,1169)
rr[1169]['data']['m_Children']=[{'rid':portrait[1293]},{'rid':6324}]
for i in [portrait[1293],portrait[1299]]:
    override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
        prop(131087,px(310)),prop(131096,px(310)),prop(131094,px(310)),
        prop(131084,num(0)),prop(131085,num(0)),prop(262150,px(0)),prop(262151,px(0)),
        prop(131093,px(0)),prop(131073,en('center')),prop(131088,en('flex-start'))])
override(rr[portrait[1285]]['data'],[prop(131105,px(286)),prop(131087,px(286)),
    prop(131096,px(286)),prop(131094,px(286)),prop(131085,num(0)),prop(131093,px(2))])
# The second version's status/foot/footer and all photo bindings stay intact.
remove_tree(5852)
move(2242,1011)
rr[1011]['data']['m_Children']=[{'rid':2242},{'rid':6298}]
override(rr[2242]['data'],[prop(131087,auto),prop(131096,px(0)),prop(131094,none),
    prop(131084,num(0)),prop(131085,num(0)),prop(131082,auto),prop(131090,px(6))])
# Restore the native report mapping, automatic icon wrapping, and content-only tactics.
restored=import_subtree(-930000000001001,6298,1173)
row=restored[6298];pros=restored[6306];tactic=restored[6230]
override(rr[row]['data'],[prop(131105,pct(100)),prop(131087,pct(100)),prop(131096,px(160)),
    prop(131094,none),prop(131084,num(1)),prop(131085,num(1)),prop(131082,px(0)),
    prop(131083,en('row')),prop(131093,px(0)),prop(131090,px(0))])
for i in [pros,tactic]:
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131095,none),
        prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1)),prop(131087,auto),
        prop(131091,px(0)),prop(131092,px(0))])
assert rr[1173]['data']['m_Children']==[{'rid':row}]
assert rr[6298]['data']['m_Children']==[{'rid':6228},{'rid':1026}]
assert 5852 not in rr and 1301 not in rr and 1819 not in rr and 1863 not in rr
assert rr[1007]==original[1007] and rr[1040]==original[1040]
# All retained native serialized fields must remain identical.
for i,r in original.items():
    if i in rr and 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i]==r,('retained binding changed',i)
commit_clone(W,-940000000010000,PAGE,PS,old_sid,doc,sheet)

# Add a third native tile choice while leaving both current descriptions and active selections alone.
desc=copy.deepcopy(objs[L][-940000000010030].read_typetree())
desc.update(m_Name='OverviewFourthLeftPortraitDescription')
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
    'first_three_pages_and_styles_byte_identical':True,'left_width':300,'middle_right_ratio':[2,1],
    'attributes_height':390,'right_upper_height':390,'portrait_size':286,
    'status_and_feet_from_second':True,'hidden_panel_removed':True,
    'right_upper_order':['scout report / fitness 50:50','four rows of native season stats','bans / radar 50:50'],
    'right_lower_order':['pros and cons 50%','tactics 50%'],
    'native_retained_bindings_unchanged':True,'saved_active_selection_unchanged':True,
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
print(json.dumps({'installed':True,'output':str(OUT),'fourth_guid':PAGE_GUID,'changed_objects':{n:list(x) for n,x in changed.items()}}))
