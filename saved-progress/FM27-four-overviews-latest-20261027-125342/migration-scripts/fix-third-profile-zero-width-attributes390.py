from pathlib import Path
import ast,copy,json

source=Path('photo-up3-titled-pros-cons-tactics-thirds.py').read_text('utf8')
prefix=source.split('ROW=-940000000006000;')[0].replace(
    'photo-up3-titled-pros-cons-tactics-thirds-','fix-third-profile-zero-width-attributes390-')
exec(compile(prefix,'backup-and-serialization','exec'))
for p in [GAME/G,SKIN/G]:protected[p]=sha(p.read_bytes())
PAGE,STYLE=-940000000010000,-940000000010001
doc=objs[W][PAGE].read_typetree();rr=refs(doc);old=copy.deepcopy(rr);sheet=objs[W][STYLE].read_typetree()
def serial(r,i):return r[r[i]['data']['m_SerializedData']['rid']]
def value(i,key):
    p=next(p for p in sheet['m_Rules'][rr[i]['data']['m_RuleIndex']]['m_Properties'] if p['m_Id']==key)
    v=p['m_Values'][0];return sheet[poolmap[v['m_ValueType']]][v['valueIndex']]
for i in [1031,6232,6276]:
    assert value(i,131105)['value']==0 and value(i,131084)==0
    override(rr[i]['data'],[prop(131105,px(0)),prop(131097,px(0)),prop(131082,px(0)),
        prop(131084,num(1)),prop(131085,num(1))])
    assert value(i,131084)==1 and value(i,131087)['value']==140

attr=named('ThirdOverviewAttributesNoScroll')
for i in [attr,1009,1025]:
    override(rr[i]['data'],[prop(131087,px(390)),prop(131096,px(390)),prop(131094,px(390)),
        prop(131082,auto),prop(131084,num(0)),prop(131085,num(0))])
# Remove the older inner scroll as well, retaining the native attributes template and all its bindings.
inner=5850;inner_sid=rr[inner]['data']['m_SerializedData']['rid']
assert rr[inner]['data']['m_FullTypeName']=='SI.UI.SIScrollView'
replacement=copy.deepcopy(serial(old,1291));replacement['rid']=inner_sid
replacement['data'].update(uxmlAssetId=rr[inner]['data']['m_Id'],name='ThirdOverviewAttributesContentNoScroll',name_UxmlAttributeFlags=1)
rr[inner_sid].clear();rr[inner_sid].update(replacement)
rr[inner]['data']['m_FullTypeName']='UnityEngine.UIElements.VisualElement'
override(rr[inner]['data'],[prop(131087,px(0)),prop(131096,px(0)),prop(131094,none),
    prop(131082,px(0)),prop(131084,num(1)),prop(131085,num(1))])
override(rr[1040]['data'],[prop(131087,pct(100)),prop(131096,px(0)),prop(131094,pct(100)),
    prop(131084,num(1)),prop(131085,num(1))])
for i,r in old.items():
    if i!=inner_sid and 'UxmlSerializedData' in r.get('type',{}).get('class',''):
        assert rr[i]==r,('data binding changed',i)
assert all(value(i,131084)==1 for i in [1031,6232,6276])
assert value(attr,131087)['value']==390
validate_ui(doc,sheet)
objs[W][PAGE].save_typetree(doc);objs[W][STYLE].save_typetree(sheet)
output=env[W].file.save(packer='lz4');check={o.path_id:o for o in UnityPy.load(output).objects}
assert set(check)==set(objs[W])
for i,h in hashes[W].items():
    if i not in [PAGE,STYLE]:assert sha(check[i].get_raw_data())==h,('unrelated asset changed',i)
assert check[PAGE].read_typetree()==doc and check[STYLE].read_typetree()==sheet
(OUT/W).write_bytes(output)
report={'installed':False,'runtime_verified':False,'third_only':True,
    'root_cause':'width=0 and flex-grow=0 on the three profile columns; clipped by overflow hidden',
    'profile_column_flex_grow':[1,1,1],'profile_row_order_and_native_bindings_unchanged':True,
    'attributes_height':390,'outer_and_inner_extra_attribute_scrolls_removed':True,
    'first_second_and_bottom_unchanged':True,'after_sha256':sha(output)}
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
    for folder in [GAME,SKIN]:(folder/W).write_bytes(output);assert (folder/W).read_bytes()==output
    for p,h in protected.items():assert sha(p.read_bytes())==h
except BaseException:
    for p,b in before.items():p.write_bytes(b)
    raise
report.update(installed=True,installed_verified=True);(OUT/'manifest.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),'utf8')
print(json.dumps({'installed':True,'output':str(OUT),'profile_columns_restored':True,'attributes_height':390}))
