from pathlib import Path
R=Path(__file__).parent
source=(R/'refine-card-inner-layout.py').read_text(encoding='utf-8')
exec(compile(source.split('\nportrait = rr[1285]')[0],'<bundle loader>','exec'))
rep=json.loads((R/'gk-no-title-left-stars-horizontal-loans-20261019-011613/manifest.json').read_text(encoding='utf8'))
club={int(k):v for k,v in rep['inline_imports'][2]['mapping'].items()}
star=rep['star_holder'];assert rr[1297]['data']['m_Children'].index({'rid':star})<rr[1297]['data']['m_Children'].index({'rid':1295})
def edit(i,ps):override(rr[i]['data'],ps)
def pct(n):return val(3,{'unit':2,'value':float(n)})
# Remove the reserved percentage width that leaves a large blank between nation and club.
edit(1182,[prop(131082,auto()),prop(131105,auto()),prop(131084,num(0)),prop(131085,num(1)),prop(131099,px(0)),prop(131100,px(0)),prop(131092,px(8))])
edit(1180,[prop(131082,auto()),prop(131105,auto()),prop(131084,num(0)),prop(131085,num(1)),prop(131099,px(0)),prop(131100,px(0)),prop(131091,px(0))])
for i in [1196,1212,1193]:edit(i,[prop(131105,auto()),prop(131084,num(0)),prop(131085,num(1)),prop(131097,px(0))])
# 48px still accommodates native club crests and the nation text, freeing room for the original three-line contract arrangement.
edit(1295,[prop(131096,px(48)),prop(131073,en('center'))])
for i in [1001,1002,1004,1006,1007]:edit(club[i],[prop(131105,auto()),prop(131097,px(0)),prop(131084,num(0)),prop(131085,num(1))])
for i in [1012,1013]:
 edit(club[i],[prop(131105,auto()),prop(131082,auto()),prop(131084,num(0)),prop(131085,num(1)),prop(131097,px(0)),prop(131092,px(6 if i==1012 else 0))])
for i in [1021,1026]:edit(club[i],[prop(131091,px(4)),prop(131092,px(0)),prop(131105,auto()),prop(131084,num(0)),prop(131097,px(0)),prop(131085,num(1))])
# Keep the contract in its existing parent below nation/club; restore native vertical order.
assert rr[1184]['data']['m_Parent']=={'rid':1297}
assert rr[1199]['data']['m_Children']==[{'rid':1214},{'rid':1215}]
edit(1199,[prop(131083,en('column')),prop(131073,en('flex-start')),prop(131087,px(60)),prop(131096,px(60)),prop(131085,num(0))])
edit(1214,[prop(131087,px(24)),prop(131090,px(0)),prop(131092,px(0)),prop(131074,en('flex-start')),prop(131085,num(0))])
edit(1215,[prop(131105,pct(100)),prop(131082,auto()),prop(131084,num(0)),prop(131085,num(0)),prop(131087,px(36)),prop(131096,px(36)),prop(131074,en('stretch'))])
edit(1237,[prop(131083,en('column')),prop(131073,en('stretch')),prop(131087,px(36)),prop(131105,pct(100))])
edit(1260,[prop(131087,px(18)),prop(131090,px(0)),prop(131092,px(0)),prop(131074,en('flex-start')),prop(131085,num(0))])
edit(1261,[prop(131087,px(18)),prop(131090,px(0)),prop(131074,en('stretch')),prop(131085,num(0))])
# Every edit is an inline style change: preserve all node locations/parents, bindings and click events.
changed=[i for i in old_refs if rr[i]!=old_refs[i]]
for i in changed:
 x=copy.deepcopy(rr[i]);x['data']['m_RuleIndex']=old_refs[i]['data']['m_RuleIndex'];assert x==old_refs[i],('Non-style change',i)
assert rr[1297]==old_refs[1297] and rr[1184]==old_refs[1184]
assert rr[star]==old_refs[star]
assert property_value(rr[1199],131083)==property_value(rr[1237],131083)=='column'
assert dimension(rr[1214],131087)+dimension(rr[1215],131087)==dimension(rr[1199],131087)==60
assert dimension(rr[1260],131087)+dimension(rr[1261],131087)==36
assert property_value(rr[club[1007]],131083)=='row'
# The extra contract height is offset by removing the same unused nation/club row height.
assert dimension(rr[1295],131096)+dimension(rr[1199],131087)==64+44
validate_ui(doc,sheet)
objects[FULL].save_typetree(doc);objects[sid].save_typetree(sheet)
output=env.file.save(packer='lz4');saved={o.path_id:o for o in UnityPy.load(output).objects}
assert set(saved)==set(objects)
for i,h in old_hashes.items():
 if i in [FULL,sid]:assert saved[i].read_typetree()=={FULL:doc,sid:sheet}[i]
 else:assert sha(saved[i].get_raw_data())==h,('Unrelated asset changed',i)
validate_ui(saved[FULL].read_typetree(),saved[sid].read_typetree())
for p,data in before.items():assert p.read_bytes()==data
for p,h in protected.items():assert sha(p.read_bytes())==h
stamp=datetime.datetime.now(datetime.timezone(datetime.timedelta(hours=8))).strftime('%Y%m%d-%H%M%S')
out=R/('tight-identity-loans-native-contract-'+stamp);out.mkdir()
for tag,folder in [('game',GAME),('skin',SKIN)]:
 backup=out/('backup-'+tag);backup.mkdir();(backup/WN).write_bytes(before[folder/WN])
(out/WN).write_bytes(output)
report={'installed':False,'runtime_verified':False,'ability_stars_above_country_club':True,'nation_club_gap_px':8,'loan_club_gap_px':6,'loan_icon_text_gap_px':4,'contract_arrangement':['Transfer value','Wage + expiry','Agreed playing time'],'contract_group_parent_and_horizontal_position_preserved':True,'identity_content_total_height_budget_preserved':True,'all_dynamic_bindings_and_events_preserved':True,'changed_nodes':changed,'changed_assets':[FULL,sid],'unchanged_assets_verified':len(old_hashes)-2,'before_sha256':{str(p):sha(data) for p,data in before.items()},'after_sha256':sha(output),'protected_sha256':{str(p):h for p,h in protected.items()}}
manifest=out/'manifest.json';manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
try:
 for folder in [GAME,SKIN]:(folder/WN).write_bytes(output);assert (folder/WN).read_bytes()==output
 for p,h in protected.items():assert sha(p.read_bytes())==h
except Exception:
 for p,data in before.items():p.write_bytes(data)
 raise
report['installed']=True;manifest.write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf8')
print(json.dumps({'output':str(out),'installed':True,'native_contract_order':report['contract_arrangement'],'nation_club_gap_px':8,'loan_gap_px':6,'sha256':sha(output)},ensure_ascii=False,indent=2))
