"""Transparent pitch, scoped dark panels, left controls and white report icons."""
from pathlib import Path
import uuid

source=Path(__file__).with_name('trial-tactics-combined-layered-card.py').read_text('utf8')
boot=source.split('# Keep the pitch anchor / footprint')[0]
boot=boot.replace('tactics-combined-layered-card-trial-','tactics-transparent-panels-card-reflow-v7-').replace('hours=-4','hours=-6')
exec(compile(boot,'v7-boot','exec'))
CP,DP=3127595210179668386,-8273082868742719783
WHITE=-970000000012000; WHITE_STYLE=WHITE-1
WHITE_GUID=uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/TacticsWhitePlayerReportPreview/v7').hex
PREVIEW=-3760232355926433866
STYLE_NAMES=['ui-styles_assets_default.bundle','ui-styles_assets_common.bundle']
for f in [GAME,SKIN]:
    for n in STYLE_NAMES:before[f/n]=(f/n).read_bytes();protected.pop(f/n,None)
for f in [GAME.parent,SKIN]:
    for n in ['catalog.bin','catalog.hash']:
        p=f/n
        if p.exists():before[p]=p.read_bytes();protected.pop(p,None)
for p,raw in before.items():
    tag='backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin'
    (OUT/tag).mkdir(exist_ok=True);(OUT/tag/p.name).write_bytes(raw)
assert WHITE not in objs and WHITE_STYLE not in objs
palette={'striker':'E53935','attacking-midfield':'D97800','midfield':'C7A600','defensive-midfield':'2196F3','defender':'2E7D32','goalkeeper':'C77DDF'}
transparent={'r':0.0,'g':0.0,'b':0.0,'a':0.0};white={'r':1.0,'g':1.0,'b':1.0,'a':1.0}
def rgba(h):return dict(zip(['r','g','b','a'],[f32(int(h[i:i+2],16)/255) for i in [0,2,4]]+[1.0]))
def named(r,n):return next(i for i,a in r.items() if r.get(a.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name')==n)
def value(i,key):
    rule=t.s['m_Rules'][t.r[i]['data']['m_RuleIndex']];h=next(p for p in rule['m_Properties'] if p['m_Id']==key)['m_Values'][0];return t.s[poolmap[h['m_ValueType']]][h['valueIndex']]
expected={};outputs={};audits=[]
def save_tree(pid):
    for x in t.s['dimensions']:x['value']=f32(x['value'])
    validate_ui(t.d,t.s)
    for p,data in [(pid,t.d),(t.d['inlineSheet']['m_PathID'],t.s)]:objs[p].save_typetree(data);expected[p]=copy.deepcopy(data)
def tree(pid):
    # ObjectReader reads its original stream until the final bundle is rebuilt.
    # Reuse the edited trees when a component has more than one layout pass.
    data=copy.deepcopy(expected[pid]) if pid in expected else objs[pid].read_typetree()
    sid=data['inlineSheet']['m_PathID']
    sheet=copy.deepcopy(expected[sid]) if sid in expected else objs[sid].read_typetree()
    return Tree(data,sheet)
def clone(src,pid,data):
    o=copy.copy(objs[src]);o.path_id=pid;o.data=None;o._read_until=None;o.assets_file.objects[pid]=o;objs[pid]=o;o.save_typetree(data);expected[pid]=copy.deepcopy(data)
def check_sd(old,allowed=()):
    for i,a in old.items():
        if 'UxmlSerializedData' in a.get('type',{}).get('class','') and i not in allowed:assert t.r[i]==a,('Native data changed',i)
def redirect_report():
    next(u for u in t.d['m_Usings'] if u['alias']=='PlayerReportPreviewTooltip')['path']=WHITE_GUID
def name_line(node,visible,contexts,texts):
    box(node,4,55,67,16);t.edit(node,[P(131100,st.px(4))])
    for i in contexts:t.edit(i,[P(131105,st.pct(100)),P(131087,st.px(16))])
    for i in visible:t.edit(i,[P(458767,st.num(1))])
    for i in texts:t.edit(i,[P(131100,st.px(1)),P(65537,st.px(10)),P(131097,st.px(0)),P(131085,st.num(1))])

# White report icon is a scoped clone. Its popup contents and report bindings
# remain the original serialized data; the shared report template is untouched.
data=objs[PREVIEW].read_typetree();old_style=data['inlineSheet']['m_PathID'];sheet2=objs[old_style].read_typetree()
data['m_Name']='TacticsWhitePlayerReportPreview';data['inlineSheet']['m_PathID']=WHITE_STYLE;sheet2['m_Name']='TacticsWhitePlayerReportPreview_Style'
clone(PREVIEW,WHITE,data);clone(old_style,WHITE_STYLE,sheet2)
t=tree(WHITE);st=t.st;P=st.p;old=copy.deepcopy(t.r)
for i in [1001,1002,1004]:t.edit(i,[P(458767,st.num(1))])
t.edit(1004,[P(196610,st.h(4,white))])
assert value(1004,131105)['value']==value(1004,131087)['value']==12
check_sd(old);save_tree(WHITE)

# Combined: existing IP/OOP buttons stay in their native data scopes.
t=tree(CP);st=t.st;P=st.p;old=copy.deepcopy(t.r)
box(1035,4,8,28,25);t.edit(1035,[P(131083,st.en('column'))])
for i,y in [(1055,0),(1057,13)]:box(i,0,y,28,12)
t.edit(1056,[P(131081,st.en('none'))])
for i in [1075,1078,1092,1094,1105,1107]:
    t.edit(i,[P(131105,st.pct(100)),P(131095,st.px(28)),P(131097,st.px(0)),P(131087,st.px(12)),P(131094,st.px(12)),P(262150,st.px(0)),P(262151,st.px(0))])
for i in [1119,1122]:t.edit(i,[P(65537,st.px(9)),P(131097,st.px(0)),P(131087,st.px(12))])
name_line(1037,[1132,1148,1158],[1061,1082,1098],[1135,1151])
redirect_report();check_sd(old);save_tree(CP)

for pid,touch in [(-970000000009000,False),(-970000000010000,True)]:
    t=tree(pid);st=t.st;P=st.p;old=copy.deepcopy(t.r)
    setter=named(t.r,'DetailedCurrentPhasePositionContext');button=named(t.r,'DetailedCurrentPhasePositionButton')
    box(setter,4,8,28,12);box(button,0,0,28,12)
    for field,x in [('LeftFootedness',4),('RightFootedness',16)]:box(named(t.r,'Detailed'+field+'PlayerVisible'),x,23,10,10)
    if touch:
        chain=[named(t.r,'DetailedTouchHasPlayerReport')]
        while t.r[chain[-1]]['data']['m_Children']:chain.append(t.r[chain[-1]]['data']['m_Children'][0]['rid'])
        name_line(1061,chain,[],[1089])
    else:name_line(1016,[1095,1119,1131],[1026,1038,1054],[1100,1123])
    redirect_report();check_sd(old);save_tree(pid)

t=tree(-970000000011000);st=t.st;P=st.p;old=copy.deepcopy(t.r)
for i in [1001,1002,1004,1006,1008]:
    t.edit(i,[P(131105,st.px(28)),P(131095,st.px(28)),P(131097,st.px(0)),P(131087,st.px(12))])
check_sd(old);save_tree(-970000000011000)

# Fitness labels move within the same switch tree; progress remains at y78.
# Role/status icons straddle the right 4px rim, with only their native guards.
for pid in [CP,DP]:
    t=tree(pid);st=t.st;P=st.p;old=copy.deepcopy(t.r);is_detail=pid==DP
    for i,a in list(t.r.items()):
        if a.get('data',{}).get('m_FullTypeName')!='SI.Bindable.SIText':continue
        if not t.sd(i).get('name','').startswith('PitchFitnessPercent'):continue
        t.edit(i,[P(131099,st.px(4)),P(131101,st.px(36 if is_detail else 35)),P(65537,st.px(9))])
    role_nodes=[1024,1028] if is_detail else [1029,1033]
    for i,y in zip(role_nodes,[9,21]):box(i,68,y,10,10)
    status,yellow=(1027,1026) if is_detail else (1032,1031)
    for i,y in [(status,30),(yellow,42)]:
        box(i,65,y,16,16);t.edit(i,[P(327681,st.num(.625),st.num(.625))])
    box(1052 if is_detail else 1069,2,1,12,14)
    if is_detail:
        box(1017,65,54,16,16);t.edit(1017,[P(327681,st.num(.625),st.num(.625))])
    t.edit(named(t.r,'TacticsPlayerPortraitFrame'),[P(458768,st.en('visible'))])
    check_sd(old);save_tree(pid)
    audits.append({'template':t.d['m_Name'],'fitness_y':36 if is_detail else 35,'native_icons_on_right_rim':True,'geometry_unchanged':[75,75]})

pitch_ids=[-4411574370150944845,3412805035020634299]
pitch_nodes=[]
for pid in pitch_ids:
    t=tree(pid);st=t.st;P=st.p;old=copy.deepcopy(t.r);allowed=[]
    for i,a in list(t.r.items()):
        typ=a.get('data',{}).get('m_FullTypeName','')
        if any(x in typ for x in ['FMTacticsPanel','FMTacticsWithAnalysis','FMTacticsWithPhases']):
            t.edit(i,[P(458753,{'m_ValueType':1,'valueIndex':6}),P(458752,st.h(4,transparent))]);pitch_nodes.append([pid,i])
    if pid==pitch_ids[0]:
        # Native parent-class setter remains native. Change only its two class
        # names to private copies with the same geometry and table background.
        args=decode(t.sd(1005)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes'])
        for k,oldname,newname in [(1,'tactics-collapsable-pitch-container-with-darker-header','tf-tactics-pitch-black-dark-header'),(2,'tactics-collapsable-pitch-container','tf-tactics-pitch-black')]:
            b=oldname.encode();n=newname.encode();assert args[k].endswith(bytes([len(b)])+b);args[k][-len(b)-1:]=bytes([len(n)])+n
        t.sd(1005)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(args)
        t.sd(1019).update(name='TFPitchSwitches',name_UxmlAttributeFlags=1)
        allowed=[t.r[i]['data']['m_SerializedData']['rid'] for i in [1005,1019]]
    check_sd(old,allowed);save_tree(pid)
assert len(pitch_nodes)==6

# Native palette edits preserve old colour pool values. Scoped panel CSS is
# appended to the same default sheets; no generic tile background is changed.
style_audits=[]
for folder in [GAME,SKIN]:
    for n in STYLE_NAMES:
        path=folder/n;se=UnityPy.load(before[path]);so={o.path_id:o for o in se.objects};sh={i:sha(o.get_raw_data()) for i,o in so.items()};changed={};palette_hits=0;scope_hits=0
        for pid,o in so.items():
            if o.type.name!='MonoBehaviour':continue
            data=o.read_typetree()
            if 'm_Rules' not in data:continue
            count=0
            for rule in data['m_Rules']:
                for p in rule['m_Properties']:
                    key=next((k for k in palette if p.get('m_CustomName')=='--colours-tactics-'+k+'-foreground'),None)
                    if key is None:continue
                    data['colors'].append(rgba(palette[key]));p['m_Values']=[{'m_ValueType':4,'valueIndex':len(data['colors'])-1}];count+=1
            if count:assert count==6;palette_hits+=count
            # Find the concrete native pitch container rules in each loaded
            # default stylesheet (AlwaysApplied and generated fallback).
            originals={}
            table_bg=None
            for rule in data['m_Rules']:
                for selector in rule['m_ComplexSelectors']:
                    seq=selector['m_Selectors']
                    if len(seq)==1 and {p['m_Value'] for p in seq[0]['m_Parts']}=={'layout-tile-base-container','startscreenVar'}:
                        table_bg=next((copy.deepcopy(p) for p in rule['m_Properties'] if p['m_Id']==458752),table_bg)
                    if len(seq)!=1 or len(seq[0]['m_Parts'])!=1:continue
                    cls=seq[0]['m_Parts'][0]['m_Value']
                    if cls in ['tactics-collapsable-pitch-container','tactics-collapsable-pitch-container-with-darker-header']:originals[cls]=copy.deepcopy(rule)
                    if cls=='layout-tile-base-container':
                        table_bg=next((copy.deepcopy(p) for p in rule['m_Properties'] if p['m_Id']==458752),table_bg)
            if originals:
                assert len(originals)==2 and table_bg is not None
                ss=Styles(data);ps=ss.p
                for cls,newcls in [('tactics-collapsable-pitch-container','tf-tactics-pitch-black'),('tactics-collapsable-pitch-container-with-darker-header','tf-tactics-pitch-black-dark-header')]:
                    rule=originals[cls];rule['m_ComplexSelectors']=[{'m_Specificity':11,'m_Selectors':[{'m_Parts':[{'m_Value':newcls,'m_Type':3}],'m_PreviousRelationship':0}],'ruleIndex':len(data['m_Rules'])}]
                    rule['m_Properties']=[p for p in rule['m_Properties'] if p['m_Id'] not in [458752,262146]]+[copy.deepcopy(table_bg),ps(262146,ss.h(4,{'r':1.0,'g':1.0,'b':1.0,'a':f32(.16)}))]
                    data['m_Rules'].append(rule);scope_hits+=1
                selector={'m_Specificity':102,'m_Selectors':[{'m_Parts':[{'m_Value':'TFPitchSwitches','m_Type':6}],'m_PreviousRelationship':0},{'m_Parts':[{'m_Value':'SIButton','m_Type':2}],'m_PreviousRelationship':2}],'ruleIndex':len(data['m_Rules'])}
                data['m_Rules'].append({'m_ComplexSelectors':[selector],'m_Properties':[copy.deepcopy(table_bg)],'line':-1});scope_hits+=1
            if count or originals:o.save_typetree(data);changed[pid]=data
        assert palette_hits==6 and scope_hits==(6 if n==STYLE_NAMES[0] else 0)
        raw=se.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert check.keys()==so.keys()
        for pid,o in check.items():
            if pid in changed:assert o.read_typetree()==changed[pid]
            else:assert sha(o.get_raw_data())==sh[pid]
        outputs[path]=raw;style_audits.append({'path':str(path),'palette_variables':palette_hits,'scoped_rules':scope_hits,'changed_objects':[str(i) for i in changed]})

# Register the private report VTA and its original dependency/preload span.
metaobj=next(o for o in objs.values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();oldmeta=copy.deepcopy(meta)
src_entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==PREVIEW)
span=copy.deepcopy(meta['m_PreloadTable'][src_entry['preloadIndex']:src_entry['preloadIndex']+src_entry['preloadSize']])
for p in [{'m_FileID':0,'m_PathID':WHITE},{'m_FileID':0,'m_PathID':WHITE_STYLE}]:
    if p not in span:span.append(p)
meta['m_Container'].append((WHITE_GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':WHITE}}));meta['m_PreloadTable'].extend(copy.deepcopy(span))
parents=[CP,-970000000009000,-970000000010000]
for pid in parents:
    for k,v in meta['m_Container']:
        if v['asset']['m_PathID']!=pid:continue
        own=copy.deepcopy(meta['m_PreloadTable'][v['preloadIndex']:v['preloadIndex']+v['preloadSize']])
        for p in span:
            if p not in own:own.append(copy.deepcopy(p))
        v.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(own));meta['m_PreloadTable'].extend(own)
meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta);expected[metaobj.path_id]=copy.deepcopy(meta)
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
preview_guid=next(k for k,v in oldmeta['m_Container'] if v['asset']['m_PathID']==PREVIEW)
cat_audits=[]
for folder in [GAME.parent,SKIN]:
    path=folder/'catalog.bin';oldcat=cm.Catalog(before[path]);cat=cm.Catalog(before[path]);oldlocs={i for _,ptr in oldcat.keys() for (i,) in oldcat.array(ptr,'I')}
    loc=next(i for i in cat.locations(preview_guid) if cat.location(i)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
    cat=cm.Catalog(cat.add_key_location(WHITE_GUID,loc,loc));newloc=cat.locations(WHITE_GUID)[0]
    idx=next(i for i,(k,_) in enumerate(cat.keys()) if k=='GameWorldVisualTreeAssetPreload');key,ptr=cat.key_records[idx]
    locs=[a[0] for a in cat.array(ptr,'I')]+[newloc];records=list(cat.key_records);records[idx]=(key,cat.append(b''.join(struct.pack('<I',i) for i in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*v) for v in records),True))
    raw=bytes(cat.data);check=cm.Catalog(raw)
    assert set(dict(check.keys()))==set(dict(oldcat.keys()))|{WHITE_GUID}
    for i in oldlocs:assert check.unpack(i,'7I')==oldcat.unpack(i,'7I')
    assert check.location(newloc)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset'
    assert check.location(check.location(newloc)['dependencies'][0])['internal'].endswith('\\'+W)
    outputs[path]=raw;outputs[folder/'catalog.hash']=hashlib.md5(raw).hexdigest().encode('ascii')
    cat_audits.append({'target':str(path),'guid':WHITE_GUID,'preload_registered':True,'all_existing_catalog_locations_unchanged':True})

raw=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(raw).objects};assert set(check)==set(hashes)|{WHITE,WHITE_STYLE}
assert old_style not in expected, 'The original shared report stylesheet must not change.'
assert check[WHITE].read_typetree()['inlineSheet']['m_PathID']==WHITE_STYLE
combined=check[CP].read_typetree();rr=refs(combined);ss=check[combined['inlineSheet']['m_PathID']].read_typetree()
for node,key,wanted in [(1035,131104,8),(1037,131104,55)]:
    rule=ss['m_Rules'][rr[node]['data']['m_RuleIndex']];h=next(p for p in rule['m_Properties'] if p['m_Id']==key)['m_Values'][0];assert ss['dimensions'][h['valueIndex']]['value']==wanted
assert next(u for u in combined['m_Usings'] if u['alias']=='PlayerReportPreviewTooltip')['path']==WHITE_GUID
for pid,h in hashes.items():
    if pid not in expected:assert sha(check[pid].get_raw_data())==h,('Unrelated world object changed',pid)
for pid,data in expected.items():assert check[pid].read_typetree()==data,('Roundtrip differs',pid)
for folder in [GAME,SKIN]:outputs[folder/W]=raw
registry_path=R/'current-custom-textures.json';registry=json.loads(registry_path.read_text('utf8'));assert len(registry['textures'])==registry['active_custom_texture_count']
protected[registry_path]=sha(registry_path.read_bytes())
BN='ui-backgrounds_assets_common.bundle';bgobjs={o.path_id:o for o in UnityPy.load(str(GAME/BN)).objects}
banned={int(x['path_id']) for x in json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']}
assert banned.isdisjoint(bgobjs) and banned.isdisjoint(check)
for row in registry['textures']:assert bgobjs[int(row['path_id'])].peek_name()==row['name']
for p,data in outputs.items():
    tag='output-game' if p.parent in [GAME,GAME.parent] else 'output-skin';(OUT/tag).mkdir(exist_ok=True);(OUT/tag/p.name).write_bytes(data)
report={'installed':False,'runtime_verified':False,'card_size':[75,75],'name_row':[4,55,67,16],'combined_roles':[[4,8,28,12],[4,21,28,12]],'detailed_role':[4,8,28,12],'detailed_feet':[[4,23,10,10],[16,23,10,10]],'fitness_y':{'Combined':35,'Detailed':36},'icons_on_right_border_y':[9,21,33,45,57],'native_pitch_backgrounds_cleared':pitch_nodes,'palette':{k:'#'+v for k,v in palette.items()},'panel_scope':'native single pitch parent private classes only; original table background declaration copied','styles':style_audits,'white_preview_guid':WHITE_GUID,'white_preview_pid':str(WHITE),'white_icon_hotspot':[16,16],'native_icon_glyph':[12,12],'native_bindings_preserved_except_presentation_class_names':True,'original_shared_preview_unchanged':True,'card_background_patchplayerbg_preserved':True,'background_textures_and_registry_unchanged':True,'active_custom_textures':registry['active_custom_texture_count'],'registry_version':registry['version'],'other_world_objects_unchanged':len(hashes)-len([i for i in expected if i in hashes]),'changed_world_objects':[str(i) for i in expected],'catalog':cat_audits,'after_sha256':{str(p):sha(b) for p,b in outputs.items()},'protected_files':{str(p):h for p,h in protected.items()}}
def record():(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
record()
guard=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
installer=list(guard);restore=list(guard)
for p,old in before.items():
    tag='backup-game' if p.parent in [GAME,GAME.parent] else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(old)+"') { throw 'File changed since preparation.' }")
for p in outputs:
    tag='output-game' if p.parent in [GAME,GAME.parent] else 'output-skin';installer.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig');(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig')
for p,old in before.items():assert p.read_bytes()==old
for p,h in protected.items():assert sha(p.read_bytes())==h
running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if running.stdout.strip():print(json.dumps({'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for p,data in outputs.items():p.write_bytes(data)
    for p,data in outputs.items():assert p.read_bytes()==data
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,old in before.items():p.write_bytes(old)
    raise
report.update(installed=True,installed_verified=True);record()
print(json.dumps({'installed':True,'output':str(OUT),'cleared_pitch_renderers':6,'cards_reflowed':2,'white_report_hotspot':16,'active_textures_unchanged':registry['active_custom_texture_count']}))
