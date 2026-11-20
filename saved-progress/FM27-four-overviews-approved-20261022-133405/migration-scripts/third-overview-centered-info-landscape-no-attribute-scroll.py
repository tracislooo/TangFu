from pathlib import Path
import ast,copy,json,struct

source=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix=source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-','third-overview-centered-info-landscape-no-attribute-scroll-')
exec(compile(prefix,'backup-and-serialization','exec'))
PAGE,STYLE=-940000000010000,-940000000010001
SELECTOR,SELECTOR_STYLE=-940000000010020,-940000000010021

def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def save(n,pid,doc,sid,sheet):
    validate_ui(doc,sheet);objs[n][pid].save_typetree(doc);objs[n][sid].save_typetree(sheet)
    changed[n][pid]=doc;changed[n][sid]=sheet
def width(i,w):override(rr[i]['data'],[prop(131105,w),prop(131097,px(0)),prop(131095,pct(100))])
def fixed_height(i,h):
    override(rr[i]['data'],[prop(131087,px(h)),prop(131096,px(h)),prop(131094,px(h)),
        prop(131084,num(0)),prop(131085,num(0)),prop(131082,auto)])

doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
middle=named('ThirdOverviewMiddleColumn');right=named('ThirdOverviewRightHeaderContext')
for i,grow in [(middle,2),(right,1)]:override(rr[i]['data'],[prop(131084,num(grow))])
# Center name/number as a group and keep the position/age line centered beneath it.
for i in [1188,1205,1206]:
    width(i,pct(100));override(rr[i]['data'],[prop(131073,en('center')),prop(131088,en('center'))])
override(rr[1219]['data'],[prop(65546,en('middle-center')),prop(131092,px(4))])
# Transfer value occupies its own row. The native contract switch contains wages/status on row two.
override(rr[1199]['data'],[prop(131083,en('column')),prop(131073,en('center')),prop(131088,en('flex-start'))])
fixed_height(1199,52)
for i in [1214,1215]:
    width(i,pct(100));fixed_height(i,24)
    override(rr[i]['data'],[prop(131074,en('center')),prop(131073,en('center')),prop(131088,en('center'))])
override(rr[1214]['data'],[prop(131090,px(4))])
override(rr[1234]['data'],[prop(65546,en('middle-center'))])
width(1236,pct(100));override(rr[1236]['data'],[prop(65546,en('middle-center')),prop(131091,px(0)),prop(131092,px(0))])
width(1237,pct(100));override(rr[1237]['data'],[prop(131073,en('center')),prop(131088,en('center'))])
for i in [1260,1261]:
    override(rr[i]['data'],[prop(131105,auto),prop(131097,px(0)),prop(131082,auto),
        prop(131084,num(0)),prop(131085,num(1)),prop(131091,px(4)),prop(131092,px(4)),prop(65546,en('middle-center'))])

# Preserve the original three-column, three-row ordering; each cell becomes title over value.
fixed_height(1184,140)
for i in [1031,6232,6276]:fixed_height(i,140)
rows=[1049,1050,1087,6235,6247,6250,6290,6294]
titles=[1066,1069,1096,6236,6248,6251,6292,6296]
values=[1067,1070,1097,6237,6249,6252,6278,6280]
for i in rows:
    width(i,pct(100));fixed_height(i,44)
    override(rr[i]['data'],[prop(131083,en('column')),prop(131073,en('center')),prop(131088,en('flex-start')),
        prop(131099,px(0)),prop(131100,px(0))])
for i in titles:
    width(i,pct(100));fixed_height(i,16)
    override(rr[i]['data'],[prop(65546,en('middle-center')),prop(131091,px(0)),prop(131092,px(0))])
for i in values:
    width(i,pct(100));fixed_height(i,24)
    override(rr[i]['data'],[prop(65546,en('middle-center')),prop(131091,px(0)),prop(131092,px(0)),prop(65552,en('normal'))])
for i in [6238,6239]:
    width(i,pct(100));fixed_height(i,24);override(rr[i]['data'],[prop(65546,en('middle-center')),prop(65552,en('normal'))])
for i in [1049,1050,1051,1072,6234]:fixed_height(i,44)
for i in [1049,1050,6234,6247,6290]:override(rr[i]['data'],[prop(131090,px(4))])
for i in [1051,1087,6250,6294]:override(rr[i]['data'],[prop(131090,px(0))])
fixed_height(6246,92)
for i,y in [(6268,46),(6270,94)]:override(rr[i]['data'],[prop(131104,px(y))])

# Remove the extra attributes scroll container and allocate the actual full table height first.
attr=named('ThirdOverviewAttributesScroll');attr_sid=rr[attr]['data']['m_SerializedData']['rid']
replacement=copy.deepcopy(serial(old,1291));replacement['rid']=attr_sid
replacement['data'].update(uxmlAssetId=rr[attr]['data']['m_Id'],name='ThirdOverviewAttributesNoScroll',name_UxmlAttributeFlags=1)
rr[attr_sid].clear();rr[attr_sid].update(replacement);rr[attr]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
override(rr[attr]['data'],[prop(131087,auto),prop(131096,px(438)),prop(131094,none),prop(131082,auto),
    prop(131084,num(0)),prop(131085,num(0))])
override(rr[1007]['data'],[prop(131084,num(1)),prop(131082,px(0)),prop(131087,px(0)),prop(131096,px(0))])

# A bounded chart avoids using the entire tall lower row as its drawing rectangle.
override(rr[1026]['data'],[prop(131073,en('stretch')),prop(131088,en('flex-start')),
    prop(131093,px(0)),prop(131092,px(0)),prop(131101,px(0))])
fixed_height(1043,160);width(1043,pct(100))
override(rr[1043]['data'],[prop(131074,en('flex-start')),prop(131093,px(0)),prop(131090,px(0))])
sd(1043).update(SpiderChartRadiusPercentage=28.0,SpiderChartRadiusPercentage_UxmlAttributeFlags=1,
    LabelDistanceFromChart=8.0,LabelDistanceFromChart_UxmlAttributeFlags=1)
assert sd(1043)['BindDataFunction']==serial(old,1043)['data']['BindDataFunction']
hr=named('ThirdOverviewRightHorizontalDivider');override(rr[hr]['data'],[prop(131090,px(0))])
line=add_pair(old[1291],serial(old,1291),1173,'ThirdOverviewRadarRightDivider')
c={k:struct.unpack('<f',struct.pack('<f',v/255))[0] for k,v in zip(['r','g','b','a'],[135,140,145,160])}
override(rr[line]['data'],[prop(131105,px(1)),prop(131097,px(1)),prop(131095,px(1)),
    prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),prop(131084,num(0)),prop(131085,num(0)),
    prop(131091,px(4)),prop(131092,px(4)),prop(458752,val(4,c))])
rr[1173]['data']['m_Children']=[{'rid':1026},{'rid':line},{'rid':2242}]
allowed={attr_sid,old[1043]['data']['m_SerializedData']['rid']}
for i,r in old.items():
    if i not in allowed and 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r,('original binding changed',i)
# No changes to country/club or bans instances, including their layout rules.
for i in [1295,1182,1180,6228,1035]:assert rr[i]==old[i],('country club or bans altered',i)
save(W,PAGE,doc,STYLE,sheet)

doc=objs[G][SELECTOR].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[G][SELECTOR_STYLE].read_typetree()
native=objs[G][-940000000005000].read_typetree();nr=refs(native)
rr[1023]['data']['m_Classes']=copy.deepcopy(nr[1023]['data']['m_Classes'])
override(rr[1022]['data'],[prop(131081,en('flex'))])
sd(1023).update(Orientation=1,Orientation_UxmlAttributeFlags=1)
fit=named('ThirdOverviewPortraitPitchRatio')
sd(fit).update(AspectRatio=struct.unpack('<f',struct.pack('<f',.7))[0],AspectRatio_UxmlAttributeFlags=1)
allowed={rr[1023]['data']['m_SerializedData']['rid'],rr[fit]['data']['m_SerializedData']['rid']}
for i,r in old.items():
    if i not in allowed and 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
save(G,SELECTOR,doc,SELECTOR_STYLE,sheet)

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
    for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
report={'installed':False,'runtime_verified':False,'third_only':True,'middle_right_ratio':[2,1],
    'left_information':'centered name and age, transfer value row, wages/status row; three original rows title over value',
    'profile_row_height':44,'attributes_extra_scroll_container_removed':True,'attributes_min_height':438,
    'pitch':'native landscape 200x140','radar':{'height':160,'radius_percentage':28,'label_distance':8,'top_aligned':True,'right_divider':True},
    'country_club_and_bans_unchanged':True,'first_second_and_bottom_unchanged':True,
    'after_sha256':{n:sha(b) for n,b in outputs.items()}}
(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
restore=['$ErrorActionPreference = "Stop"']
for p in before:
    tag='backup-game' if p.parent==GAME else 'backup-skin'
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
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'middle_right_ratio':[2,1],'attributes_scroll_removed':True,'pitch':'landscape'}))
