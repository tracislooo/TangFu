from pathlib import Path
import struct, uuid, importlib.util

source = Path('replace-tactics-shirts-with-portraits.py').read_text('utf-8-sig')
exec(compile(source.split('donor=objs')[0].replace('tactics-overview-player-portraits-', 'team-instruction-image80-controls120-hide-scrollbar-'), 'backup-and-helpers', 'exec'))
src = ast.parse((R/'build-fc-player-hover-layout.py').read_text('utf8'))
exec(compile(ast.Module(body=[n for n in src.body if isinstance(n,ast.ClassDef) and n.name=='Styles'],type_ignores=[]),'styles','exec'))
NATIVE = 6689231267327553076
PID, SID = -970000000006000, -970000000006001
GUID = uuid.uuid5(uuid.NAMESPACE_URL,'tf27-01/TeamInstructionImage80Controls120/v1').hex
MODULE = 1593217430813700770
for p in [GAME.parent/'catalog.bin',GAME.parent/'catalog.hash',SKIN/'catalog.bin']:
    before[p]=p.read_bytes();protected.pop(p,None)
    (OUT/('backup-skin' if p.parent==SKIN else 'backup-game')/p.name).write_bytes(before[p])
assert before[GAME.parent/'catalog.bin']==before[SKIN/'catalog.bin']
def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def named(r,name):
    a=[i for i,v in r.items() if v.get('data',{}).get('m_SerializedData',{}).get('rid',-2)!=-2 and serial(r,i)['data'].get('name')==name]
    assert len(a)==1,(name,a)
    return a[0]
changed={}
def save(pid,d):objs[pid].save_typetree(d);changed[pid]=copy.deepcopy(d)
def clone(source,pid,d):
    assert pid not in objs
    o=copy.copy(source);o.path_id=pid;o.data=None;o._read_until=None
    o.assets_file.objects[pid]=o;objs[pid]=o;save(pid,d)

# Hide both scrollbars; retain all scrolling, viewport sizing and content bindings.
module=objs[MODULE].read_typetree();mr=refs(module);mold=copy.deepcopy(mr)
scroll=named(mr,'TrainingTacticalEffectivenessScroll')
ms=serial(mr,scroll)['data']
oldscroll=copy.deepcopy(ms)
for k in ['horizontalScrollerVisibility','verticalScrollerVisibility']:
    ms[k]=2;ms[k+'_UxmlAttributeFlags']=1
allowed={'horizontalScrollerVisibility','verticalScrollerVisibility','horizontalScrollerVisibility_UxmlAttributeFlags','verticalScrollerVisibility_UxmlAttributeFlags'}
assert {k for k in ms if ms[k]!=oldscroll[k]}<=allowed
assert all(v==mr[i] for i,v in mold.items() if i!=mr[scroll]['data']['m_SerializedData']['rid'])
save(MODULE,module)

# Clone the shared base. Keeping every original element ID preserves the team
# templates' existing event and binding overrides; player templates keep the old base.
doc=objs[NATIVE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr)
old_sid=doc['inlineSheet']['m_PathID'];sheet=objs[old_sid].read_typetree();st=Styles(sheet)
doc['m_Name']='TeamInstructionImage80Controls120'
doc['inlineSheet']['m_PathID']=SID
sheet['m_Name']='TeamInstructionImage80Controls120_Style'
ids={n:named(rr,n) for n in ['Body','IconArea','Icon','ControlsArea','HoverText','NameAndHoverControls','leftarrowbutton','rightarrowbutton','leftbuttonicon','rightbuttonicon','name-style-setter','name','selectedoptionstepper']}
def edit(name,ps):st.edit(rr[ids[name]],ps)
P=st.p
# Scale the native image uniformly. This also preserves the special 72x50
# defensive-line illustrations, instead of forcing them into a 124x72 ratio.
edit('Icon',[P(327681,st.num(.8),st.num(.8))])
edit('IconArea',[P(131105,st.pct(100)),P(131087,st.px(57.6)),P(131094,st.px(57.6)),P(131096,st.px(0)),P(131084,st.num(0)),P(131085,st.num(1)),P(131073,st.en('center')),P(131088,st.en('center'))])
edit('Body',[P(131083,st.en('column')),P(131088,st.en('space-between')),P(131097,st.px(0)),P(131096,st.px(0))])
edit('ControlsArea',[P(131105,st.pct(100)),P(131087,st.px(28.8)),P(131096,st.px(28.8)),P(131084,st.num(0)),P(131085,st.num(0)),P(131073,st.en('center'))])
edit('NameAndHoverControls',[P(131097,st.px(0)),P(131084,st.num(1)),P(131085,st.num(1)),P(131087,st.px(28.8)),P(131083,st.en('column'))])
edit('name',[P(65537,st.px(15.6)),P(131097,st.px(0)),P(131085,st.num(1)),P(131099,st.px(4.8)),P(131100,st.px(4.8))])
edit('HoverText',[P(65537,st.px(15.6))])
edit('name-style-setter',[P(131087,st.px(24)),P(131096,st.px(24)),P(131084,st.num(0)),P(131085,st.num(0))])
for button,icon in [('leftarrowbutton','leftbuttonicon'),('rightarrowbutton','rightbuttonicon')]:
    parent=rr[ids[button]]['data']['m_Parent']['rid']
    st.edit(rr[parent],[P(131105,st.px(19.2)),P(131097,st.px(19.2)),P(131095,st.px(19.2)),P(131087,st.px(28.8)),P(131084,st.num(0)),P(131085,st.num(0))])
    edit(button,[P(131105,st.px(19.2)),P(131097,st.px(19.2)),P(131095,st.px(19.2)),P(131087,st.px(28.8)),P(131096,st.px(28.8)),P(131084,st.num(0)),P(131085,st.num(0)),P(131073,st.en('center')),P(131088,st.en('center'))])
    edit(icon,[P(131105,st.px(19.2)),P(131087,st.px(19.2)),P(131096,st.px(19.2)),P(131097,st.px(19.2)),P(131084,st.num(0)),P(131085,st.num(0))])
step=ids['selectedoptionstepper'];parent=rr[step]['data']['m_Parent']['rid']
st.edit(rr[parent],[P(131087,st.px(4.8)),P(131096,st.px(4.8)),P(131084,st.num(0)),P(131085,st.num(0))])
# Scale the complete stepper including its generated child segments. The parent
# reserves its enlarged height; center alignment leaves horizontal clearance.
edit('selectedoptionstepper',[P(327681,st.num(1.2),st.num(1.2)),P(131105,st.px(68)),P(131087,st.px(4)),P(131084,st.num(0)),P(131085,st.num(0))])
for i,a in old.items():
    if 'UxmlSerializedData' in a.get('type',{}).get('class',''):assert rr[i]==a,('binding/event changed',i)
assert set(rr)==set(old)
for d in sheet['dimensions']:
    d['value']=struct.unpack('<f',struct.pack('<f',d['value']))[0]
validate_ui(doc,sheet)
clone(objs[NATIVE],PID,doc);clone(objs[old_sid],SID,sheet)

wrappers=[]
for pid in [2818111587875485449,-7133918393381693061]:
    d=objs[pid].read_typetree();original=copy.deepcopy(d)
    u=next(u for u in d['m_Usings'] if u['alias']=='InstructionTileBaseTemplate')
    assert u['path']=='5d758db2d2ba75145901a0b9ceaaa57e'
    u['path']=GUID
    assert d['references']==original['references'],'Instruction overrides altered'
    save(pid,d);wrappers.append(d['m_Name'])
compact=refs(changed[-7133918393381693061])
assert 'hide-hideable-children' in compact[1010]['data']['m_Classes']

metaobj=next(o for o in objs.values() if o.type.name=='AssetBundle');meta=metaobj.read_typetree()
entry=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==NATIVE)
span=copy.deepcopy(meta['m_PreloadTable'][entry['preloadIndex']:entry['preloadIndex']+entry['preloadSize']])
span=[p for p in span if not(p['m_FileID']==0 and p['m_PathID'] in [NATIVE,old_sid])]
span.extend([{'m_FileID':0,'m_PathID':PID},{'m_FileID':0,'m_PathID':SID}])
meta['m_Container'].append((GUID,{'preloadIndex':len(meta['m_PreloadTable']),'preloadSize':len(span),'asset':{'m_FileID':0,'m_PathID':PID}}));meta['m_PreloadTable'].extend(span)
for pid in [2818111587875485449,-7133918393381693061]:
    e=next(v for k,v in meta['m_Container'] if v['asset']['m_PathID']==pid)
    sp=copy.deepcopy(meta['m_PreloadTable'][e['preloadIndex']:e['preloadIndex']+e['preloadSize']])
    for p in span:
        if p not in sp:sp.append(p)
    e.update(preloadIndex=len(meta['m_PreloadTable']),preloadSize=len(sp));meta['m_PreloadTable'].extend(sp)
meta['m_Container'].sort(key=lambda x:x[0]);save(metaobj.path_id,meta)
spec=importlib.util.spec_from_file_location('catalog',R/'catalog-binary-v35.py');cm=importlib.util.module_from_spec(spec);spec.loader.exec_module(cm)
oldcat=cm.Catalog(before[GAME.parent/'catalog.bin']);loc=oldcat.locations('5d758db2d2ba75145901a0b9ceaaa57e')[0]
cat=cm.Catalog(oldcat.add_key_location(GUID,loc,loc))
idx=next(i for i,(key,_) in enumerate(cat.keys()) if key=='GameWorldVisualTreeAssetPreload');keyobj,locset=cat.key_records[idx]
locs=[a[0] for a in cat.array(locset,'I')]+cat.locations(GUID);records=list(cat.key_records)
records[idx]=(keyobj,cat.append(b''.join(struct.pack('<I',i) for i in locs),True));struct.pack_into('<I',cat.data,8,cat.append(b''.join(struct.pack('<2I',*r) for r in records),True))
catout=bytes(cat.data);newcat=cm.Catalog(catout);newkeys=dict(newcat.keys())
assert set(newkeys)==set(dict(oldcat.keys()))|{GUID}
for key,locset in oldcat.keys():
    assert [a[0] for a in newcat.array(newkeys[key],'I')]==[a[0] for a in oldcat.array(locset,'I')]+(newcat.locations(GUID) if key=='GameWorldVisualTreeAssetPreload' else [])

def stylevalue(name,key):
    i=ids[name];ps=sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'];h=next(p for p in ps if p['m_Id']==key)['m_Values'][0]
    return sheet[poolmap[h['m_ValueType']]][h['valueIndex']]
assert abs(stylevalue('name',65537)['value']-15.6)<1e-4
for button in ['leftarrowbutton','rightarrowbutton']:
    assert abs(stylevalue(button,131105)['value']-19.2)<1e-4
    assert abs(stylevalue(button,131087)['value']-28.8)<1e-4
assert stylevalue('Icon',327681)==struct.unpack('<f',struct.pack('<f',.8))[0]
# All existing IDs and serialized data overrides must still target the clone.
base_element_ids={a['data']['m_Id'] for a in rr.values() if 'm_Parent' in a.get('data',{})}
base_element_ids.update([130628061,-1311125049,1197638381]) # inherited tile header/auto-scroller elements
for pid in [2818111587875485449,-7133918393381693061]:
    r=refs(changed[pid])
    for a in r[1010]['data']['m_SerializedDataOverride']:
        assert a['m_ElementId'] in base_element_ids,a['m_ElementId']
output=env.file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects};assert check.keys()==objs.keys()
for i,h in hashes.items():
    if i not in changed:assert sha(check[i].get_raw_data())==h,('unrelated object changed',i)
for i,d in changed.items():assert check[i].read_typetree()==d,i
assert sha(check[NATIVE].get_raw_data())==hashes[NATIVE]
(OUT/W).write_bytes(output);(OUT/'catalog.bin').write_bytes(catout)
hashout=hashlib.md5(catout).hexdigest().encode('ascii');(OUT/'catalog.hash').write_bytes(hashout)
(OUT/'team-template.json').write_text(json.dumps(doc,ensure_ascii=False,indent=2),'utf8')
install={GAME/W:output,SKIN/W:output,GAME.parent/'catalog.bin':catout,GAME.parent/'catalog.hash':hashout,SKIN/'catalog.bin':catout}
report={'installed':False,'runtime_verified':False,'scrollbars':'hidden; scrolling and viewport sizing unchanged','image_scale':.8,'controls_scale':1.2,'option_font':15.6,'arrow_size':19.2,'arrow_click_box':[19.2,28.8],'controls_height':28.8,'stepper_visual_size':[81.6,4.8],'private_template_guid':GUID,'team_wrappers':wrappers,'compact_hidden_images_preserved':True,'original_serialized_events_and_bindings_unchanged':True,'player_instruction_templates_and_shared_base_unchanged':True,'avatars_rings_fatigue_and_training_content_unchanged':True,'changed_objects':list(changed),'after_sha256':{str(p):sha(b) for p,b in install.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"',"if (Get-Process -Name fm -ErrorAction SilentlyContinue) { throw 'Exit Football Manager first.' }"];installer=list(restore)
for p,b in before.items():
    tag='backup-skin' if p.parent==SKIN else 'backup-game'
    restore.append("Copy-Item -LiteralPath '"+str(OUT/tag/p.name)+"' -Destination '"+str(p)+"' -Force")
    installer.append("if ((Get-FileHash -LiteralPath '"+str(p)+"' -Algorithm SHA256).Hash.ToLower() -ne '"+sha(b)+"') { throw 'Package changed since preparation.' }")
for p in install:installer.append("Copy-Item -LiteralPath '"+str(OUT/p.name)+"' -Destination '"+str(p)+"' -Force")
(OUT/'restore.ps1').write_text('\n'.join(restore),'utf-8-sig');(OUT/'install.ps1').write_text('\n'.join(installer),'utf-8-sig')
for p,b in before.items():assert p.read_bytes()==b
for p,h in protected.items():assert sha(p.read_bytes())==h
proc=subprocess.run(['powershell','-NoProfile','-Command','Get-Process -Name fm -ErrorAction SilentlyContinue | Select-Object -ExpandProperty Id'],capture_output=True,text=True)
if proc.stdout.strip():print(json.dumps({'prepared':True,'installed':False,'waiting_for_game_exit':True,'output':str(OUT)}));sys.exit(0)
try:
    for p,b in install.items():p.write_bytes(b)
    for p,b in install.items():assert p.read_bytes()==b
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'image_scale':.8,'controls_scale':1.2,'scrollbars_hidden':True,'team_templates':wrappers}))
