"""Detailed-only card clones, independent foot ratings, native report hotspots."""
from pathlib import Path
import uuid

source = Path(__file__).with_name('trial-tactics-combined-layered-card.py').read_text('utf8')
boot = source.split('# Keep the pitch anchor / footprint')[0]
boot = boot.replace('tactics-combined-layered-card-trial-', 'tactics-detailed75-feet-hover-v4-').replace('hours=-4', 'hours=-6')
exec(compile(boot, 'detailed-v4-boot', 'exec'))
DP, CP = -8273082868742719783, 3127595210179668386
DESKTOP, TOUCH, ROLE = 1476694543497088899, 725077918139614894, 1948159345683025545
new_assets = [
    (DESKTOP, -970000000009000, 'TacticsDetailedCardDetailsDesktop'),
    (TOUCH, -970000000010000, 'TacticsDetailedCardDetailsTouch'),
    (ROLE, -970000000011000, 'TacticsDetailedCardPositionButton'),
]
new_guids = {pid: uuid.uuid5(uuid.NAMESPACE_URL, 'tf27-01/'+name+'/v4').hex for _, pid, name in new_assets}
reserved = json.loads((R/'reserved-texture-ids.json').read_text('utf8'))['reserved_textures']
reserved_ids = {int(x['path_id']) for x in reserved}
for _, pid, _ in new_assets:
    assert pid not in objs and pid-1 not in objs
    assert pid not in reserved_ids and pid-1 not in reserved_ids
catalog_before = {f/n: (f/n).read_bytes() for f in [GAME.parent, SKIN] for n in ['catalog.bin', 'catalog.hash'] if (f/n).exists()}
for p, raw in catalog_before.items():
    tag = 'backup-game' if p.parent == GAME.parent else 'backup-skin'
    (OUT/tag/p.name).write_bytes(raw)
    protected.pop(p, None)

expected = {}
audits = []
transparent = {'r':0.0,'g':0.0,'b':0.0,'a':0.0}
cd = objs[CP].read_typetree(); cr = refs(cd); cs = objs[cd['inlineSheet']['m_PathID']].read_typetree()
dd = objs[DP].read_typetree(); dr = refs(dd); ds = objs[dd['inlineSheet']['m_PathID']].read_typetree()
desktop = objs[DESKTOP].read_typetree(); rr_desktop = refs(desktop); ss_desktop = objs[desktop['inlineSheet']['m_PathID']].read_typetree()
role = objs[ROLE].read_typetree(); rr_role = refs(role)
VE = 1165

def named(r, name):
    return next(i for i,a in r.items() if r.get(a.get('data',{}).get('m_SerializedData',{}).get('rid'),{}).get('data',{}).get('name') == name)

def reset(i, ps): st.edit(t.r[i], ps, True)
def hide(i): t.edit(i, [P(131081, st.en('none'))])
def clear_bg(i): t.edit(i, [P(458752,st.h(4,transparent)),P(458768,st.en('visible'))])
def bg(i, color): t.edit(i,[P(458752,st.h(4,color))])
def clone_object(src, pid, data):
    o = copy.copy(objs[src]); o.path_id=pid; o.data=None; o._read_until=None
    o.assets_file.objects[pid]=o; objs[pid]=o; o.save_typetree(data); expected[pid]=copy.deepcopy(data)

def save_tree(pid):
    for dim in t.s['dimensions']: dim['value']=f32(dim['value'])
    validate_ui(t.d,t.s)
    for p,data in [(pid,t.d),(t.d['inlineSheet']['m_PathID'],t.s)]:
        objs[p].save_typetree(data); expected[p]=copy.deepcopy(data)

def copy_tree(pid, target, name):
    data=objs[pid].read_typetree(); oldsid=data['inlineSheet']['m_PathID']; sheet2=objs[oldsid].read_typetree()
    data['m_Name']=name;data['inlineSheet']['m_PathID']=target-1;sheet2['m_Name']=name+'_Style'
    clone_object(pid,target,data);clone_object(oldsid,target-1,sheet2)
    return Tree(data,sheet2)

def add_ve2(parent, name):
    i=t.add(cr,VE,parent,name);t.r[i]['data'].update(m_Classes=[],m_Properties=[]);ignore(i);return i

def full(i, w=75,h=75):
    box(i,0,0,w,h)

def assert_bindings(original, allow=()):
    # Layout picking/tooltip flags may change, but binding and event payloads may not.
    for i,a in original.items():
        if 'UxmlSerializedData' not in a.get('type',{}).get('class',''): continue
        old,new=copy.deepcopy(a),copy.deepcopy(t.r[i])
        for key in ['pickingMode','pickingMode_UxmlAttributeFlags','displayTooltipWhenElided','displayTooltipWhenElided_UxmlAttributeFlags','DisplayTooltipWhenElided','DisplayTooltipWhenElided_UxmlAttributeFlags']:
            old['data'].pop(key,None);new['data'].pop(key,None)
        if i not in allow: assert old==new,('Native binding/event changed',i)

def native_hover(name_node, context_nodes, hasplayer, visible, mapper, instance, text_nodes, switch=None):
    box(name_node,4,43,67,16)
    for i in context_nodes:
        t.edit(i,[P(131105,st.pct(100)),P(131087,st.px(16)),P(131096,st.px(0)),P(131094,st.px(16)),P(262150,st.px(0)),P(262151,st.px(0))])
    for i in [hasplayer,visible,mapper,instance]:
        t.edit(i,[P(131105,st.px(16)),P(131097,st.px(16)),P(131095,st.px(16)),P(131087,st.px(16)),P(131096,st.px(16)),P(131094,st.px(16)),P(262150,st.px(0)),P(262151,st.px(0)),P(327681,st.num(1),st.num(1)),P(458768,st.en('visible'))])
    t.edit(hasplayer,[P(131105,st.px(18)),P(131097,st.px(18)),P(131095,st.px(18)),P(131085,st.num(0))])
    # Cancel former absolute/relative top offsets; the native glyph centers itself.
    box(visible,0,0,16,16);t.edit(visible,[P(131102,st.en('relative'))])
    for i in text_nodes:
        t.edit(i,[P(131097,st.px(0)),P(131096,st.px(0)),P(131087,st.px(16)),P(131094,st.px(16)),P(262150,st.px(0)),P(262151,st.px(0)),P(65537,st.px(10)),P(65546,st.en('middle-center')),P(65552,st.en('nowrap')),P(196609,st.en('ellipsis'))])
        for key in ['DisplayTooltipWhenElided','displayTooltipWhenElided']:
            if key in t.sd(i):t.sd(i).update({key:1,key+'_UxmlAttributeFlags':1})
    if switch:
        t.edit(switch,[P(131105,st.px(0)),P(131082,st.px(0)),P(131084,st.num(1)),P(131097,st.px(0)),P(262150,st.px(0))])

# Combined changes are restricted to the name line and its native report hotspot.
t=Tree(cd,cs);st=t.st;P=st.p;old=copy.deepcopy(t.r)
native_hover(1037,[1061,1082,1098],1114,1132,1148,1158,[1135,1151],1115)
assert_bindings(old);save_tree(CP)
audits.append({'asset':'Combined','changes':'name y43/h16, native report 16px hotspot/12px glyph, transform 1'})

# Private native role template: keep the native position/role event and tooltip.
t=copy_tree(ROLE,-970000000011000,'TacticsDetailedCardPositionButton');st=t.st;P=st.p;old=copy.deepcopy(t.r)
for i in [1001,1002,1004,1006,1008]:
    t.edit(i,[P(131105,st.px(41)),P(131087,st.px(12)),P(131097,st.px(0)),P(131096,st.px(0)),P(131095,st.px(41)),P(131094,st.px(12)),P(262150,st.px(0)),P(262151,st.px(0)),P(131085,st.num(0))])
t.edit(1004,[P(458752,st.h(4,{'r':f32(.025),'g':f32(.055),'b':f32(.07),'a':f32(.92)}))])
t.edit(1011,[P(65537,st.px(9)),P(65536,st.h(4,{'r':1.0,'g':1.0,'b':1.0,'a':1.0})),P(131097,st.px(0)),P(131087,st.px(12)),P(262150,st.px(0)),P(262151,st.px(0)),P(65552,st.en('nowrap')),P(196609,st.en('ellipsis')),P(458768,st.en('hidden'))])
assert_bindings(old);save_tree(-970000000011000)

foot_checks=[]
hexes=['E34B4B','F29538','EBCB42','9CCB45','43BB68']
def rgb(hexcode):return dict(zip(['r','g','b','a'],[f32(int(hexcode[n:n+2],16)/255) for n in [0,2,4]]+[1.0]))

def add_feet():
    # Two independent 1..20 trees retain exact numeric hover descriptions.
    for foot,x,field in [('左',49,'LeftFootedness'),('右',61,'RightFootedness')]:
        gate=t.add(dr,1075,1005,'Detailed'+field+'PlayerVisible');ignore(gate);box(gate,x,60,10,10)
        path='position.Player.Footedness.'+field;leaves={}
        def switch(parent,limit):
            i=t.add(dr,1077,parent,field+'Above'+str(limit));s=t.sd(i)
            args=decode(s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes'])
            struct.pack_into('<i',args[1],len(args[1])-4,limit)
            oldpath=b'position.Player.Condition';newpath=path.encode();assert args[2].endswith(bytes([len(oldpath)])+oldpath)
            args[2][-len(oldpath)-1:]=bytes([len(newpath)])+newpath
            s['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(args);ignore(i)
            t.edit(i,[P(131105,st.pct(100)),P(131087,st.pct(100))]);return i
        def leaf(parent,val):
            i=add_ve2(parent,field+'Value'+str(val));t.sd(i).update(pickingMode=0,pickingMode_UxmlAttributeFlags=1)
            full(i,10,10);rounded(i,1);color=colour(None) if val is None else rgb(hexes[(val-1)//4]);bg(i,color)
            text=t.add(dr,named(dr,'PitchFitnessPercent0'),i,field+'Label'+str(val));s=t.sd(text)
            s.update(text=foot,text_UxmlAttributeFlags=1,pickingMode=1,pickingMode_UxmlAttributeFlags=1);full(text,10,10)
            t.edit(text,[P(65537,st.px(7)),P(65543,st.en('bold')),P(65546,st.en('middle-center')),P(65536,st.h(4,{'r':0.0,'g':0.0,'b':0.0,'a':1.0})),P(262150,st.px(0)),P(262151,st.px(0))])
            tip=t.add(rr_role,1012,i,field+'Tooltip'+str(val))
            body=t.add(dr,named(dr,'PitchFitnessPercent0'),tip,field+'TooltipText'+str(val));s=t.sd(body)
            s.update(text=foot+'脚：'+('数据不可用' if val is None else str(val)+'/20'),text_UxmlAttributeFlags=1)
            reset(body,[P(65537,st.px(12)),P(65536,st.h(4,{'r':1.0,'g':1.0,'b':1.0,'a':1.0})),P(65552,st.en('nowrap'))])
            leaves[i]=val;return i
        def build(parent,lo,hi):
            if lo==hi:return leaf(parent,lo)
            mid=(lo+hi)//2;i=switch(parent,mid);build(i,lo,mid);build(i,mid+1,hi);return i
        upper=switch(gate,20);lower=switch(upper,0);leaf(lower,None);build(lower,1,20);leaf(upper,None)
        for val in [None,-2147483648,-1,0]+list(range(1,23)):
            node=upper
            while node not in leaves:
                args=decode(t.sd(node)['Binding']['m_visualFunction']['m_inputs']['m_variable']['m_argumentBytes']);assert args[2].endswith(path.encode())
                lim=struct.unpack_from('<i',args[1],len(args[1])-4)[0]
                node=t.r[node]['data']['m_Children'][int(val is not None and val>lim)]['rid']
            expectedval=val if val is not None and 1<=val<=20 else None
            assert leaves[node]==expectedval
        foot_checks.append({'asset':t.d['m_Name'],'foot':foot,'path':path,'states':22,'test_inputs':26,'independent_tree':True})

def add_footer_position():
    setter=t.add(rr_desktop,1031,1005,'DetailedCurrentPhasePositionContext')
    box(setter,4,59,41,12)
    inst=t.add(rr_desktop,1044,setter,'DetailedCurrentPhasePositionButton')
    full(inst,41,12)
    u=copy.deepcopy(next(u for u in desktop['m_Usings'] if u['alias']=='PositionIndicatorColouredPosition'))
    u['path']=new_guids[-970000000011000]
    t.d['m_Usings']=[q for q in t.d['m_Usings'] if q['alias']!=u['alias']]+[u]

# Private desktop and touch copies retain their component data and native guards.
for sourceid,target,name in new_assets[:2]:
    t=copy_tree(sourceid,target,name);st=t.st;P=st.p;old=copy.deepcopy(t.r);is_touch=sourceid==TOUCH
    full(1001);full(1005)
    for i in [1001,1005]:ignore(i);clear_bg(i)
    full(1007);ignore(1007)
    if not is_touch:
        hide(1021);hide(1015)  # native position tree is replaced with its current-phase instance below
        full(1014);ignore(1014);box(1022,12.5,-4,50,8)
        for i in [1022,1034,1049,1064]:
            clear_bg(i);t.edit(i,[P(131105,st.px(50)),P(131087,st.px(8)),P(131096,st.px(0)),P(262150,st.px(0)),P(262151,st.px(0)),P(131073,st.en('center'))])
        full(1085,50,10);t.edit(1085,[P(327681,st.num(.8),st.num(.8))])
        native_hover(1016,[1026,1038,1054],1072,1095,1119,1131,[1100,1123],1074)
        bg(1016,{'r':0.0,'g':0.0,'b':0.0,'a':f32(.7)})
        for i in [1026,1038,1054]:bg(i,transparent)
        t.r[1054]['data']['m_Children'].sort(key=lambda c:0 if c['rid']==1073 else 1)
    else:
        # Keep touch native button/event payload. Its old composite rating/flags
        # panels remain serialized, but the new card uses one current-phase role.
        hide(1014);hide(1026);hide(1016);hide(1017)
        full(1015);ignore(1015);box(1027,12.5,-4,50,8)
        for i in [1027,1047,1071,1097]:
            clear_bg(i);t.edit(i,[P(131105,st.px(50)),P(131087,st.px(8)),P(131096,st.px(0)),P(262150,st.px(0)),P(262151,st.px(0)),P(131073,st.en('center'))])
        full(1131,50,10);t.edit(1131,[P(327681,st.num(.8),st.num(.8))])
        # Native touch name has no report hotspot: copy the native desktop chain
        # which maps binding=position.Player and reportcontextteam=team.
        hotspot=t.add(rr_desktop,1072,1061,'DetailedTouchHasPlayerReport',ss_desktop,True)
        chain=[hotspot]
        while t.r[chain[-1]]['data']['m_Children']:chain.append(t.r[chain[-1]]['data']['m_Children'][0]['rid'])
        assert len(chain)==4
        t.d['m_Usings'].append(copy.deepcopy(next(u for u in desktop['m_Usings'] if u['alias']=='PlayerReportPreviewTooltip')))
        t.r[1061]['data']['m_Children']=[{'rid':hotspot}]+[a for a in t.r[1061]['data']['m_Children'] if a['rid']!=hotspot]
        t.edit(1061,[P(131083,st.en('row'))])
        full(1018);full(1037);ignore(1018);ignore(1037)
        native_hover(1061,[],*chain,[1089])
        bg(1061,{'r':0.0,'g':0.0,'b':0.0,'a':f32(.7)})
        t.edit(1089,[P(131105,st.px(0)),P(131082,st.px(0)),P(131084,st.num(1)),P(131085,st.num(1))])
        full(1008)  # native touch role action covers the same centered card
        t.r[1005]['data']['m_Children'].insert(0,t.r[1005]['data']['m_Children'].pop(t.r[1005]['data']['m_Children'].index({'rid':1008})))
    full(1009);ignore(1009)
    # Native selection frame paints before the footer; it never takes the hit.
    for i in ([1019,1029,1042,1008] if not is_touch else [1021,1039,1063]):ignore(i)
    children=t.r[1005]['data']['m_Children'];t.r[1005]['data']['m_Children']=[a for a in children if a['rid']==1009]+[a for a in children if a['rid']!=1009]
    add_footer_position();add_feet()
    assert_bindings(old);save_tree(target)

# Detailed pitch visual retains its native shortcuts, swaps, conditions and drag.
t=Tree(dd,ds);st=t.st;P=st.p;old=copy.deepcopy(t.r)
for node in [1001,1010]:
    full(node,80,70);t.edit(node,[P(131102,st.en('relative')),P(458768,st.en('visible'))])
box(1014,2.5,-2.5,75,75);full(1018);full(1069);rounded(1069,6)
border=t.add(cr,named(cr,'CombinedCardNativePositionBackground'),1069,'DetailedCardNativePositionBackground',cs)
args=decode(t.sd(border)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes'])
oldpath=b'Position.IPPosition';newpath=b'Position.Position';assert args[4].endswith(bytes([len(oldpath)])+oldpath)
args[4][-len(oldpath)-1:]=bytes([len(newpath)])+newpath
t.sd(border)['BindFunction']['m_inputs']['m_variable']['m_argumentBytes']=encode(args);full(border);rounded(border,6,True)
surface=t.add(cr,named(cr,'CombinedCardInnerSurface'),1069,'DetailedCardInnerSurface',cs);box(surface,4,4,67,67);rounded(surface,2,True)
box(1071,4,4,67,67);rounded(1071,2,True)
for node,y in [(1024,20),(1028,31)]:
    move(node,1069);box(node,4,y,10,10)
for node in [1034,1043]:box(node,-3,-3,16,16);t.edit(node,[P(327681,st.num(.625),st.num(.625))])
for node,y in [(1027,9),(1026,24)]:
    move(node,1069);box(node,58,y,16,16);t.edit(node,[P(327681,st.num(.625),st.num(.625))])
move(1017,1069);box(1017,58,-2,16,16);t.edit(1017,[P(327681,st.num(.625),st.num(.625))])
box(1052,0,0,12,14)
gate=1075;root=1077;box(gate,0,0,75,81)
track=t.add(cr,named(cr,'CombinedCardFitnessTrack'),gate,'DetailedCardFitnessTrack',cs);box(track,0,78,75,3)
t.r[gate]['data']['m_Children']=[{'rid':track},{'rid':root}]
for i,a in list(old.items()):
    if a.get('data',{}).get('m_FullTypeName')!='SI.Bindable.SIText':continue
    name=serial(old,i)['data'].get('name','')
    if not name.startswith('PitchFitnessPercent'):continue
    val=None if name.endswith('None') else int(name.removeprefix('PitchFitnessPercent'))
    box(i,0,0,75,81);t.edit(i,[P(65537,st.px(9)),P(65546,st.en('upper-left')),P(131099,st.px(4)),P(131101,st.px(9)),P(458768,st.en('visible'))])
    fill=t.add(cr,named(cr,'CombinedCardFitnessFill'+str(val)),i,'DetailedCardFitnessFill'+str(val),cs);box(fill,0,78,0 if val is None else val*.75,3)
t.r[1069]['data']['m_Children']=[{'rid':i} for i in [border,surface,1025,1071,1036,1037,gate,1024,1028,1027,1026,1017]]
box(1015,2.5,-2.5,75,75);ignore(1015);clear_bg(1015);full(1020)
for i in [1030,1031]:full(i)
for alias,newpid in [('PositionIndicatorDetails',-970000000009000),('PositionIndicatorDetailsTouch',-970000000010000)]:
    next(u for u in dd['m_Usings'] if u['alias']==alias)['path']=new_guids[newpid]
assert_bindings(old);save_tree(DP)

# New GUIDs/objects are registered in the world bundle, with the union of native
# template dependencies. The original shared templates remain byte-identical.
metaobj=next(o for o in objs.values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree();oldmeta=copy.deepcopy(meta)
sourceids=[DP,CP,DESKTOP,TOUCH,ROLE]
common=[]
for pid in sourceids:
    en=next(v for _,v in oldmeta['m_Container'] if v['asset']['m_PathID']==pid)
    for ptr in oldmeta['m_PreloadTable'][en['preloadIndex']:en['preloadIndex']+en['preloadSize']]+[en['asset']]:
        if ptr not in common:common.append(copy.deepcopy(ptr))
for _,pid,_ in new_assets:
    common += [{'m_FileID':0,'m_PathID':pid},{'m_FileID':0,'m_PathID':pid-1}]
for _,pid,_ in new_assets:
    meta['m_Container'].append((new_guids[pid],{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(common),'asset':{'m_FileID':0,'m_PathID':pid}}));meta['m_PreloadTable'].extend(copy.deepcopy(common))
entry=next(v for _,v in meta['m_Container'] if v['asset']['m_PathID']==DP);entry.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(common));meta['m_PreloadTable'].extend(copy.deepcopy(common))
meta['m_Container'].sort(key=lambda x:x[0]);metaobj.save_typetree(meta);expected[metaobj.path_id]=copy.deepcopy(meta)
assert reserved_ids.isdisjoint(objs)
assert not any(p['m_PathID'] in reserved_ids for p in meta['m_PreloadTable'])
assert not any(v['asset']['m_PathID'] in reserved_ids for _,v in meta['m_Container'])

spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
outputs={};catalog_audits=[]
guids={pid:next(k for k,v in oldmeta['m_Container'] if v['asset']['m_PathID']==pid) for pid in sourceids}
for folder in [GAME.parent,SKIN]:
    path=folder/'catalog.bin';oldcat=cm.Catalog(catalog_before[path]);cat=cm.Catalog(catalog_before[path]);oldlocs={loc for _,ptr in oldcat.keys() for (loc,) in oldcat.array(ptr,'I')}
    def vtaloc(c,key):return next(loc for loc in c.locations(key) if c.location(loc)['type'][1]=='UnityEngine.UIElements.VisualTreeAsset')
    deps=[]
    for pid in sourceids:
        for dep in cat.location(vtaloc(cat,guids[pid]))['dependencies']:
            if dep not in deps:deps.append(dep)
    assert cat.location(deps[0])['internal'].endswith('\\'+W)
    for src,pid,name in new_assets:
        loc=vtaloc(cat,guids[src]);cat=cm.Catalog(cat.add_key_location(new_guids[pid],loc,loc))
    modified_locations=[]
    for loc in [vtaloc(cat,new_guids[pid]) for _,pid,_ in new_assets]+cat.locations(guids[DP]):
        raw=list(cat.unpack(loc,'7I'));raw[3]=cat.append(b''.join(struct.pack('<I',dep) for dep in deps),True);struct.pack_into('<7I',cat.data,loc,*raw);modified_locations.append(loc)
    idx=next(i for i,(key,_) in enumerate(cat.keys()) if key=='GameWorldVisualTreeAssetPreload')
    keyobj,ptr=cat.key_records[idx];locs=[x[0] for x in cat.array(ptr,'I')]+[vtaloc(cat,new_guids[pid]) for _,pid,_ in new_assets]
    records=list(cat.key_records);records[idx]=(keyobj,cat.append(b''.join(struct.pack('<I',i) for i in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*v) for v in records),True))
    out=bytes(cat.data);cc=cm.Catalog(out)
    assert set(dict(cc.keys()))==set(dict(oldcat.keys()))|set(new_guids.values())
    for loc in oldlocs:
        if loc not in modified_locations:assert cc.unpack(loc,'7I')==oldcat.unpack(loc,'7I'),('Other catalog location changed',loc)
    for _,pid,_ in new_assets:
        loc=vtaloc(cc,new_guids[pid]);x=cc.location(loc);assert x['dependencies']==deps and loc in locs
    outputs[path]=out;outputs[folder/'catalog.hash']=hashlib.md5(out).hexdigest().encode('ascii')
    catalog_audits.append({'target':str(path),'new_templates':new_guids,'original_locations_preserved_except_detailed_dependencies':True})

output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert set(check)==set(objs)
for pid,h in hashes.items():
    if pid not in expected:assert sha(check[pid].get_raw_data())==h,('Unrelated world object modified',pid)
for pid,data in expected.items():assert check[pid].read_typetree()==data,('Roundtrip differs',pid)
for folder in [GAME,SKIN]:outputs[folder/W]=output
(OUT/W).write_bytes(output)
for path,raw in outputs.items():
    if path.name==W:continue
    tag='output-game' if path.parent==GAME.parent else 'output-skin';(OUT/tag).mkdir(exist_ok=True);(OUT/tag/path.name).write_bytes(raw)
bgobjs={o.path_id:o for o in UnityPy.load(str(GAME/'ui-backgrounds_assets_common.bundle')).objects};assert reserved_ids.isdisjoint(bgobjs)
registry=json.loads((R/'current-custom-textures.json').read_text('utf8'))
for row in registry['textures']:assert bgobjs[int(row['path_id'])].peek_name()==row['name']
report={'installed':False,'runtime_verified':False,'detailed_size':[75,75],'border_width':4,'hotspot_size':[16,16],'native_glyph_size':[12,12],'name_row':[4,43,67,16],'foot_widgets':foot_checks,'foot_colors':hexes,'foot_bins':[[1,4],[5,8],[9,12],[13,16],[17,20]],'new_templates':new_guids,'changed_objects':[str(i) for i in expected],'original_shared_templates_unchanged':True,'native_events_and_bindings_preserved':True,'catalog_audits':catalog_audits,'reserved_70_absent':True,'active_custom_textures_verified':len(registry['textures']),'after_sha256':{str(p):sha(b) for p,b in outputs.items()},'protected_files':{str(p):h for p,h in protected.items()}}
def record():(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
record()
installed_before={**before,**catalog_before}
guard=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"]
restore=list(guard);installer=list(guard)
for path,raw in installed_before.items():
    tag='backup-game' if path.parent in [GAME,GAME.parent] else 'backup-skin'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/path.name)+"' -Destination '"+str(path)+"' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '"+str(path)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(raw)+"') { throw 'File changed since preparation.' }")
for path in outputs:
    src=OUT/W if path.name==W else OUT/('output-game' if path.parent==GAME.parent else 'output-skin')/path.name
    installer.append("Copy-Item -LiteralPath '"+str(src)+"' -Destination '"+str(path)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig')
for p,raw in installed_before.items():assert p.read_bytes()==raw
for p,h in protected.items():assert sha(p.read_bytes())==h
running=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if running.stdout.strip():print(json.dumps({'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for p,raw in outputs.items():p.write_bytes(raw)
    for p,raw in outputs.items():assert p.read_bytes()==raw
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,raw in installed_before.items():p.write_bytes(raw)
    raise
report.update(installed=True,installed_verified=True);record()
print(json.dumps({'installed':True,'output':str(OUT),'new_templates':3,'foot_tests':104,'native_hover_hotspot':16,'changed_objects':len(expected)}))
