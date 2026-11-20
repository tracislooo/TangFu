from pathlib import Path
import ast,copy,json

source=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix=source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-','third-milestones-pitch-inset-right390-')
exec(compile(prefix,'backup-and-serialization','exec'))
PAGE,STYLE=-940000000010000,-940000000010001
SELECTOR,SELECTOR_STYLE=-940000000010020,-940000000010021
def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def save(n,pid,doc,sid,styles):
    validate_ui(doc,styles);objs[n][pid].save_typetree(doc);objs[n][sid].save_typetree(styles)
    changed[n][pid]=doc;changed[n][sid]=styles

doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
for i in [1051,1072,1087]:
    override(rr[i]['data'],[prop(131105,pct(100)),prop(131097,px(0)),prop(131095,pct(100)),
        prop(131083,en('column')),prop(131073,en('center')),prop(131088,en('flex-start')),
        prop(131074,en('stretch')),prop(131099,px(0)),prop(131100,px(0)),
        prop(131091,px(0)),prop(131092,px(0))])
for i in [1096,1097]:override(rr[i]['data'],[prop(65546,en('middle-center'))])
override(rr[1703]['data'],[prop(131087,px(390)),prop(131096,px(390)),prop(131094,px(390)),
    prop(131082,auto),prop(131084,num(0)),prop(131085,num(0))])
override(rr[1173]['data'],[prop(131087,px(0)),prop(131096,px(0)),prop(131094,none),
    prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
for i,r in old.items():
    if 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
save(W,PAGE,doc,STYLE,sheet)

doc=objs[G][SELECTOR].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[G][SELECTOR_STYLE].read_typetree()
next_rid=max(rr)+1;next_id=max(r.get('data',{}).get('m_Id',0) for r in rr.values())+1
fitter=named('ThirdOverviewPortraitPitchRatio')
inset=add_pair(old[2000],serial(old,2000),1010,'ThirdOverviewPitchSafeInset')
rr[1010]['data']['m_Children'].remove({'rid':fitter})
rr[fitter]['data']['m_Parent']={'rid':inset};rr[inset]['data']['m_Children']=[{'rid':fitter}]
override(rr[inset]['data'],[prop(131102,en('absolute')),prop(131089,px(8)),prop(131103,px(8)),
    prop(131104,px(8)),prop(131080,px(8)),prop(131105,auto),prop(131087,auto),
    prop(131097,px(0)),prop(131096,px(0)),prop(131095,none),prop(131094,none),
    prop(131084,num(0)),prop(131085,num(0)),prop(131073,en('center')),prop(131088,en('center')),
    prop(262150,px(0)),prop(262151,px(0))])
sd(1023).update(ClampIncludesTileExtents=1,ClampIncludesTileExtents_UxmlAttributeFlags=1)
assert sd(1023)['Orientation']==1
assert abs(sd(fitter)['AspectRatio']-.7)<.00001
allow=rr[1023]['data']['m_SerializedData']['rid']
for i,r in old.items():
    if i==allow:
        expected=copy.deepcopy(r);expected['data'].update(ClampIncludesTileExtents=1,ClampIncludesTileExtents_UxmlAttributeFlags=1)
        assert rr[i]==expected
    elif 'UxmlSerializedData' in r.get('type',{}).get('class',''):assert rr[i]==r
save(G,SELECTOR,doc,SELECTOR_STYLE,sheet)

outputs={n:e.file.save(packer='lz4') for n,e in env.items()}
for n,b in outputs.items():
    check={o.path_id:o for o in UnityPy.load(b).objects};assert set(check)==set(objs[n])
    for i,h in hashes[n].items():
        if i not in changed[n]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',n,i)
    for i,d in changed[n].items():assert check[i].read_typetree()==d,('roundtrip mismatch',n,i)
    (OUT/n).write_bytes(b)
report={'installed':False,'runtime_verified':False,'third_only':True,
    'milestones_alignment':'same full-width centered column as reputation',
    'right_hidden_pros_cons_tactics_height':390,'attributes_height_390_preserved':True,
    'pitch_inset':8,'landscape_aspect_parameter':.7,'native_position_tiles_kept_inside_bounds':True,
    'native_data_and_input_bindings_unchanged':True,'after_sha256':{n:sha(b) for n,b in outputs.items()}}
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
print(json.dumps({'installed':True,'output':str(OUT),'right_height':390,'pitch_safe_inset':8}))
